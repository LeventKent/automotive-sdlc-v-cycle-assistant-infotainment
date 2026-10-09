#!/usr/bin/env python3
"""
On-demand evaluation of the automotive technical design generator with
Amazon Bedrock AgentCore Evaluations built-in evaluators.

Every run reads ``default_agent`` from ``backend/design-agent/.bedrock_agentcore.yaml``
and evaluates that deployed runtime, so a redeploy or a switch of the default agent
is picked up without editing this script.

For each scenario in ``dataset.json`` the SDK's OnDemandEvaluationDatasetRunner:
  1. invokes the agent runtime (one session per scenario),
  2. waits for the OpenTelemetry spans to land in CloudWatch,
  3. collects the spans for that session from ``aws/spans`` and the runtime log group,
  4. calls the Evaluate API once per evaluator, targeting traces or tool-call spans
     according to the evaluator level, and maps ``expected_response`` to
     Builtin.Correctness as ground truth.

Prerequisites
  - AWS credentials for the account in .bedrock_agentcore.yaml with permission for
    bedrock-agentcore:Evaluate, bedrock-agentcore:GetEvaluator, logs:StartQuery and
    logs:GetQueryResults.
  - CloudWatch Transaction Search enabled, and the runtime deployed with observability
    (the generated Dockerfile runs the agent under ``opentelemetry-instrument``).
  - The runtime uses inbound JWT auth. The Cognito client ID is taken from
    ``authorizer_configuration.customJWTAuthorizer.allowedClients[0]``. The user is
    read from COGNITO_USERNAME / COGNITO_PASSWORD, falling back to the notebook test
    user defined in ../utils.py. COGNITO_CLIENT_ID overrides the client ID.

Usage (from the repository root, with the workspace .venv active)
  pip install -r backend/design-agent/evals/requirements.txt
  python backend/design-agent/evals/run_evals.py --dry-run
  python backend/design-agent/evals/run_evals.py
  python backend/design-agent/evals/run_evals.py --scenario notebook-sample --verbose
  python backend/design-agent/evals/run_evals.py --fail-under 0.7

Results are written to evals/results/<UTC timestamp>/:
  results.json   raw Evaluate API results per scenario and evaluator
  summary.json   aggregated scores, labels and explanations
  designs/       the generated design document of each scenario, for manual review
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import statistics
import sys
import threading
import time
import urllib.parse
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import boto3
import requests
import yaml
from bedrock_agentcore.evaluation import (
    AgentInvokerInput,
    AgentInvokerOutput,
    CloudWatchAgentSpanCollector,
    Dataset,
    EvaluationResult,
    EvaluationRunConfig,
    EvaluatorConfig,
    OnDemandEvaluationDatasetRunner,
    PredefinedScenario,
    Turn,
)

EVALS_DIR = Path(__file__).resolve().parent
AGENT_DIR = EVALS_DIR.parent
DEFAULT_AGENT_CONFIG = AGENT_DIR / ".bedrock_agentcore.yaml"
DEFAULT_DATASET = EVALS_DIR / "dataset.json"
DEFAULT_RESULTS_DIR = EVALS_DIR / "results"

DEFAULT_EVALUATORS = [
    "Builtin.Coherence",
    "Builtin.Correctness",
    "Builtin.Faithfulness",
    "Builtin.InstructionFollowing",
    "Builtin.ToolParameterAccuracy",
    "Builtin.ToolSelectionAccuracy",
]

# Tool-level evaluators produce no result when the trace contains no tool call.
TOOL_LEVEL_EVALUATORS = {"Builtin.ToolParameterAccuracy", "Builtin.ToolSelectionAccuracy"}

# Suffix that marks a payload field whose value is a file path to inline.
FILE_SUFFIX = "_file"

logger = logging.getLogger("design_agent_evals")


# --------------------------------------------------------------------------- config


@dataclass(frozen=True)
class AgentTarget:
    """The deployed runtime selected by ``default_agent`` in .bedrock_agentcore.yaml."""

    name: str
    agent_id: str
    agent_arn: str
    region: str
    cognito_client_id: Optional[str]
    endpoint: str = "DEFAULT"

    @property
    def log_group(self) -> str:
        return f"/aws/bedrock-agentcore/runtimes/{self.agent_id}-{self.endpoint}"

    @property
    def invocation_url(self) -> str:
        escaped_arn = urllib.parse.quote(self.agent_arn, safe="")
        return (
            f"https://bedrock-agentcore.{self.region}.amazonaws.com/runtimes/"
            f"{escaped_arn}/invocations?qualifier={self.endpoint}"
        )


def load_default_agent(config_path: Path) -> AgentTarget:
    """Resolve ``default_agent`` from the AgentCore starter toolkit config."""
    if not config_path.is_file():
        raise SystemExit(f"Agent config not found: {config_path}")

    with config_path.open(encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}

    name = config.get("default_agent")
    if not name:
        raise SystemExit(f"No 'default_agent' set in {config_path}")

    agent = (config.get("agents") or {}).get(name)
    if not agent:
        raise SystemExit(f"default_agent '{name}' is not defined under 'agents' in {config_path}")

    runtime = agent.get("bedrock_agentcore") or {}
    agent_id = runtime.get("agent_id")
    agent_arn = runtime.get("agent_arn")
    if not agent_id or not agent_arn:
        raise SystemExit(f"Agent '{name}' has no agent_id/agent_arn. Deploy it before running evaluations.")

    region = (agent.get("aws") or {}).get("region") or agent_arn.split(":")[3]

    allowed_clients = (
        ((agent.get("authorizer_configuration") or {}).get("customJWTAuthorizer") or {}).get("allowedClients")
        or []
    )
    client_id = os.getenv("COGNITO_CLIENT_ID") or (allowed_clients[0] if allowed_clients else None)

    return AgentTarget(
        name=name,
        agent_id=agent_id,
        agent_arn=agent_arn,
        region=region,
        cognito_client_id=client_id,
    )


# --------------------------------------------------------------------------- dataset


def _resolve_payload(payload: Dict[str, Any], base_dir: Path, scenario_id: str) -> Dict[str, Any]:
    """Inline ``<field>_file`` entries as ``<field>`` with the file's text."""
    resolved: Dict[str, Any] = {}
    for key, value in payload.items():
        if key.endswith(FILE_SUFFIX):
            field = key[: -len(FILE_SUFFIX)]
            if field in payload:
                raise SystemExit(f"Scenario '{scenario_id}': both '{field}' and '{key}' are set.")
            path = (base_dir / value).resolve()
            if not path.is_file():
                raise SystemExit(f"Scenario '{scenario_id}': file for '{key}' not found: {path}")
            resolved[field] = path.read_text(encoding="utf-8")
        else:
            resolved[key] = value
    return resolved


def load_dataset(dataset_path: Path, scenario_ids: Optional[List[str]]) -> Dataset:
    """Load dataset.json (AgentCore predefined-scenario schema) and inline document files."""
    with dataset_path.open(encoding="utf-8") as f:
        raw = json.load(f)

    available = [s["scenario_id"] for s in raw.get("scenarios", [])]
    if scenario_ids:
        unknown = sorted(set(scenario_ids) - set(available))
        if unknown:
            raise SystemExit(f"Unknown scenario(s): {', '.join(unknown)}. Available: {', '.join(available)}")

    scenarios = []
    for entry in raw.get("scenarios", []):
        scenario_id = entry["scenario_id"]
        if scenario_ids and scenario_id not in scenario_ids:
            continue

        turns = []
        for turn in entry["turns"]:
            turn_input = turn["input"]
            if isinstance(turn_input, dict):
                turn_input = _resolve_payload(turn_input, dataset_path.parent, scenario_id)
            turns.append(Turn(input=turn_input, expected_response=turn.get("expected_response")))

        scenarios.append(
            PredefinedScenario(
                scenario_id=scenario_id,
                turns=turns,
                assertions=entry.get("assertions"),
                expected_trajectory=entry.get("expected_trajectory"),
                metadata=entry.get("metadata"),
            )
        )

    if not scenarios:
        raise SystemExit(f"No scenarios selected from {dataset_path}")
    return Dataset(scenarios=scenarios)


# --------------------------------------------------------------------------- auth


def _cognito_user() -> Tuple[str, str, str]:
    """Return (username, password, source). Never log the password."""
    username = os.getenv("COGNITO_USERNAME")
    password = os.getenv("COGNITO_PASSWORD")
    if username and password:
        return username, password, "COGNITO_USERNAME/COGNITO_PASSWORD"

    # Fall back to the test user the deployment notebook creates (../utils.py).
    sys.path.insert(0, str(AGENT_DIR))
    try:
        import utils  # noqa: PLC0415  (local module next to mcp_agent.py)
    finally:
        sys.path.pop(0)
    return utils.USER_NAME, utils.PASSWORD, "notebook test user in utils.py"


class CognitoTokenProvider:
    """Thread-safe bearer token cache for the runtime's inbound JWT authorizer."""

    REFRESH_MARGIN_SECONDS = 300

    def __init__(self, region: str, client_id: str):
        self._client = boto3.client("cognito-idp", region_name=region)
        self._client_id = client_id
        self._username, self._password, source = _cognito_user()
        logger.info("Authenticating to the runtime as Cognito user '%s' (%s)", self._username, source)
        self._token: Optional[str] = None
        self._expires_at = 0.0
        self._lock = threading.Lock()

    def token(self) -> str:
        with self._lock:
            if self._token and time.time() < self._expires_at - self.REFRESH_MARGIN_SECONDS:
                return self._token
            result = self._client.initiate_auth(
                ClientId=self._client_id,
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={"USERNAME": self._username, "PASSWORD": self._password},
            )["AuthenticationResult"]
            self._token = result["AccessToken"]
            self._expires_at = time.time() + int(result.get("ExpiresIn", 3600))
            return self._token


# --------------------------------------------------------------------------- invoker


class RuntimeInvoker:
    """Agent invoker for the dataset runner.

    Uses HTTPS with a bearer token because the runtime is configured with a custom JWT
    authorizer, which boto3's SigV4-signed invoke_agent_runtime cannot satisfy. The
    runtime session header carries the runner's session ID, which AgentCore Runtime
    stamps on the spans as ``attributes.session.id``; the span collector filters on it.
    """

    def __init__(self, target: AgentTarget, tokens: CognitoTokenProvider, timeout_seconds: int):
        self._target = target
        self._tokens = tokens
        self._timeout = (10, timeout_seconds)
        self._outputs: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def __call__(self, invoker_input: AgentInvokerInput) -> AgentInvokerOutput:
        session_id = invoker_input.session_id
        payload = invoker_input.payload
        if isinstance(payload, str):
            payload = {"prompt": payload}

        logger.info("[%s] invoking %s", session_id, self._target.name)
        started = time.monotonic()
        response = requests.post(
            self._target.invocation_url,
            headers={
                "Authorization": f"Bearer {self._tokens.token()}",
                "Content-Type": "application/json",
                "X-Amzn-Bedrock-AgentCore-Runtime-Session-Id": session_id,
            },
            data=json.dumps(payload),
            timeout=self._timeout,
        )
        elapsed = time.monotonic() - started

        if response.status_code != 200:
            raise RuntimeError(f"Runtime returned HTTP {response.status_code}: {response.text[:500]}")
        try:
            body = response.json()
        except ValueError as err:
            raise RuntimeError(f"Runtime returned non-JSON response: {response.text[:500]}") from err

        # The entrypoint reports its own failures as a 200 with an 'error' key.
        if isinstance(body, dict) and body.get("error"):
            raise RuntimeError(f"Agent error: {body['error']}: {body.get('message', '')}")

        logger.info("[%s] response received in %.1fs", session_id, elapsed)
        with self._lock:
            self._outputs[session_id] = body
        return AgentInvokerOutput(agent_output=body)

    def output_for(self, session_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self._outputs.get(session_id)


# --------------------------------------------------------------------------- reporting


def summarize(result: EvaluationResult, evaluator_ids: List[str]) -> Dict[str, Any]:
    """Aggregate raw Evaluate API results into per-scenario and per-evaluator scores."""
    scenarios = []
    per_evaluator_values: Dict[str, List[float]] = {eid: [] for eid in evaluator_ids}

    for scenario in result.scenario_results:
        entry: Dict[str, Any] = {
            "scenario_id": scenario.scenario_id,
            "session_id": scenario.session_id,
            "status": scenario.status,
            "error": scenario.error,
            "evaluators": {},
        }
        by_id = {er.evaluator_id: er.results for er in scenario.evaluator_results}

        for evaluator_id in evaluator_ids:
            raw = by_id.get(evaluator_id)
            if scenario.status != "COMPLETED":
                entry["evaluators"][evaluator_id] = {"status": "NOT_RUN"}
                continue
            if raw is None:
                reason = (
                    "no tool calls in the trace"
                    if evaluator_id in TOOL_LEVEL_EVALUATORS
                    else "no matching traces in the collected spans"
                )
                entry["evaluators"][evaluator_id] = {"status": "SKIPPED", "reason": reason}
                continue

            ok = [r for r in raw if "value" in r and not r.get("errorCode")]
            failed = [r for r in raw if r.get("errorCode")]
            values = [float(r["value"]) for r in ok]
            per_evaluator_values[evaluator_id].extend(values)
            entry["evaluators"][evaluator_id] = {
                "status": "SCORED" if values else "ERROR",
                "score": round(statistics.mean(values), 3) if values else None,
                "results": len(raw),
                "labels": [r.get("label") for r in ok],
                "explanations": [r.get("explanation") for r in ok],
                "ignored_reference_fields": sorted(
                    {f for r in ok for f in r.get("ignoredReferenceInputFields", []) or []}
                ),
                "errors": [f"{r.get('errorCode')}: {r.get('errorMessage')}" for r in failed],
            }
        scenarios.append(entry)

    overall = {
        eid: {
            "mean": round(statistics.mean(vals), 3) if vals else None,
            "results": len(vals),
        }
        for eid, vals in per_evaluator_values.items()
    }
    return {"scenarios": scenarios, "overall": overall}


def _short(evaluator_id: str) -> str:
    return evaluator_id.removeprefix("Builtin.")


def print_report(summary: Dict[str, Any], evaluator_ids: List[str], verbose: bool) -> None:
    columns = [_short(e) for e in evaluator_ids]
    width_id = max([len("scenario")] + [len(s["scenario_id"]) for s in summary["scenarios"]])
    widths = [max(len(c), 7) for c in columns]

    def cell(ev: Dict[str, Any]) -> str:
        status = ev.get("status")
        if status == "SCORED":
            return f"{ev['score']:.2f}"
        return {"SKIPPED": "skip", "NOT_RUN": "-", "ERROR": "error"}.get(status, "?")

    header = "scenario".ljust(width_id) + "  " + "  ".join(c.rjust(w) for c, w in zip(columns, widths))
    print("\n" + header)
    print("-" * len(header))
    for s in summary["scenarios"]:
        cells = [cell(s["evaluators"][e]).rjust(w) for e, w in zip(evaluator_ids, widths)]
        print(s["scenario_id"].ljust(width_id) + "  " + "  ".join(cells))
    print("-" * len(header))
    means = [
        (f"{summary['overall'][e]['mean']:.2f}" if summary["overall"][e]["mean"] is not None else "-").rjust(w)
        for e, w in zip(evaluator_ids, widths)
    ]
    print("mean".ljust(width_id) + "  " + "  ".join(means))
    print("\nskip = evaluator not applicable (tool evaluators: the agent made no tool call); - = scenario failed\n")

    for s in summary["scenarios"]:
        if s["status"] != "COMPLETED":
            print(f"[{s['scenario_id']}] FAILED: {s['error']}")
        for eid in evaluator_ids:
            ev = s["evaluators"][eid]
            if ev.get("errors"):
                print(f"[{s['scenario_id']}] {_short(eid)} errors: {'; '.join(ev['errors'])}")
            if ev.get("status") == "SKIPPED":
                print(f"[{s['scenario_id']}] {_short(eid)} skipped: {ev['reason']}")
            if verbose and ev.get("status") == "SCORED":
                for label, explanation in zip(ev["labels"], ev["explanations"]):
                    print(f"\n[{s['scenario_id']}] {_short(eid)} = {label}\n  {explanation}")


def write_results(
    out_dir: Path,
    target: AgentTarget,
    evaluator_ids: List[str],
    result: EvaluationResult,
    summary: Dict[str, Any],
    invoker: RuntimeInvoker,
) -> None:
    designs_dir = out_dir / "designs"
    designs_dir.mkdir(parents=True, exist_ok=True)

    run_info = {
        "agent": target.name,
        "agent_arn": target.agent_arn,
        "region": target.region,
        "log_group": target.log_group,
        "evaluators": evaluator_ids,
    }
    (out_dir / "results.json").write_text(
        json.dumps({**run_info, **json.loads(result.model_dump_json())}, indent=2), encoding="utf-8"
    )
    (out_dir / "summary.json").write_text(json.dumps({**run_info, **summary}, indent=2), encoding="utf-8")

    for scenario in result.scenario_results:
        output = invoker.output_for(scenario.session_id) or {}
        design = (output.get("step1_design_generation") or {}).get("design")
        if design:
            (designs_dir / f"{scenario.scenario_id}.md").write_text(design, encoding="utf-8")


# --------------------------------------------------------------------------- main


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--agent-config", type=Path, default=DEFAULT_AGENT_CONFIG,
                        help="Path to .bedrock_agentcore.yaml (default_agent is used).")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET, help="Path to the dataset JSON.")
    parser.add_argument("--scenario", action="append", dest="scenarios",
                        help="Run only this scenario_id. Repeat to select several.")
    parser.add_argument("--evaluator", action="append", dest="evaluators",
                        help="Override the evaluator list. Repeat to select several.")
    parser.add_argument("--delay", type=int, default=180,
                        help="Seconds to wait for CloudWatch span ingestion after invocation (default 180).")
    parser.add_argument("--concurrency", type=int, default=2,
                        help="Scenarios invoked and evaluated in parallel (default 2).")
    parser.add_argument("--invoke-timeout", type=int, default=900,
                        help="Read timeout in seconds for a single agent invocation (default 900).")
    parser.add_argument("--results-dir", type=Path, default=DEFAULT_RESULTS_DIR,
                        help="Parent directory for run output.")
    parser.add_argument("--fail-under", type=float, default=None,
                        help="Exit with status 1 if any evaluator's mean score is below this value.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Resolve the agent and dataset and print the plan without calling AWS.")
    parser.add_argument("--verbose", action="store_true", help="Print evaluator explanations.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")
    for noisy in ("botocore", "boto3", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    target = load_default_agent(args.agent_config.resolve())
    dataset = load_dataset(args.dataset.resolve(), args.scenarios)
    evaluator_ids = args.evaluators or DEFAULT_EVALUATORS

    print(f"Agent      : {target.name} ({target.agent_arn})")
    print(f"Region     : {target.region}")
    print(f"Log group  : {target.log_group}")
    print(f"Evaluators : {', '.join(evaluator_ids)}")
    print("Scenarios  :")
    for scenario in dataset.scenarios:
        payload = scenario.turns[0].input
        sizes = (
            ", ".join(f"{k}={len(v)} chars" for k, v in payload.items() if isinstance(v, str))
            if isinstance(payload, dict) else f"{len(str(payload))} chars"
        )
        ground_truth = "expected_response" if scenario.turns[0].expected_response else "no ground truth"
        print(f"  - {scenario.scenario_id}: {sizes}; {ground_truth}")

    if args.dry_run:
        return 0

    if not target.cognito_client_id:
        raise SystemExit("No Cognito client ID: set COGNITO_CLIENT_ID or allowedClients in the agent config.")

    tokens = CognitoTokenProvider(target.region, target.cognito_client_id)
    tokens.token()  # fail fast on bad credentials before any scenario starts
    invoker = RuntimeInvoker(target, tokens, args.invoke_timeout)

    config = EvaluationRunConfig(
        evaluator_config=EvaluatorConfig(evaluator_ids=evaluator_ids),
        evaluation_delay_seconds=args.delay,
        max_concurrent_scenarios=args.concurrency,
    )
    span_collector = CloudWatchAgentSpanCollector(log_group_name=target.log_group, region=target.region)
    runner = OnDemandEvaluationDatasetRunner(region=target.region)

    result = runner.run(config=config, dataset=dataset, agent_invoker=invoker, span_collector=span_collector)

    summary = summarize(result, evaluator_ids)
    out_dir = args.results_dir.resolve() / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    write_results(out_dir, target, evaluator_ids, result, summary, invoker)

    print_report(summary, evaluator_ids, args.verbose)
    print(f"Results written to {out_dir}")

    exit_code = 0
    if any(s["status"] != "COMPLETED" for s in summary["scenarios"]):
        exit_code = 1
    if args.fail_under is not None:
        below = [
            e for e, o in summary["overall"].items() if o["mean"] is not None and o["mean"] < args.fail_under
        ]
        if below:
            print(f"Below --fail-under {args.fail_under}: {', '.join(_short(e) for e in below)}")
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
