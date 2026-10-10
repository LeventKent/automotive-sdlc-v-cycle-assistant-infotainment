#!/usr/bin/env python3
"""
Deploy, list and validate the custom AgentCore evaluators in evals/evaluators/.

Commands
  deploy     Create each evaluator that does not exist yet, or update it if its
             definition changed. Creates (or updates) a resource in the AWS account;
             an evaluator costs nothing until it is used in an evaluation.
  list       Show the custom evaluators deployed in the account.
  validate-judge
             Re-score the sessions of an earlier run_evals.py run with the custom
             evaluator(s) and compare the verdicts with hand labels. Spans are read from
             CloudWatch, so this works only while the run's spans are retained
             (aws/spans keeps them for 30 days in this account). No agent invocation.

The region is taken from default_agent in ../.bedrock_agentcore.yaml.

Examples (from the repository root)
  python backend/design-agent/evals/manage_evaluators.py deploy
  python backend/design-agent/evals/manage_evaluators.py list
  python backend/design-agent/evals/manage_evaluators.py validate-judge \\
      --results backend/design-agent/evals/results/20261009T143634Z \\
      --expect weather-app=fail --expect ev-charging-planner=pass --repeat 2
"""

from __future__ import annotations

import argparse
import json
import logging
import statistics
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List

import boto3
from botocore.config import Config
from bedrock_agentcore.evaluation import CloudWatchAgentSpanCollector, trace_ids

from custom_evaluators import (
    build_request,
    control_client,
    display_name,
    list_custom_evaluators,
    load_local_configs,
    wait_until_active,
)
from run_evals import DEFAULT_AGENT_CONFIG, load_default_agent

logger = logging.getLogger("design_agent_evals.manage")

# Fields compared to decide whether a deployed evaluator needs an update.
_COMPARED_FIELDS = ("level", "description", "evaluatorConfig")


# --------------------------------------------------------------------------- deploy / list


def _needs_update(client, evaluator_id: str, request: Dict[str, Any]) -> bool:
    current = client.get_evaluator(evaluatorId=evaluator_id)
    # Structural comparison: the service returns numbers as floats (temperature 0 -> 0.0),
    # which Python equality treats as equal but a JSON string comparison would not.
    return any(field in request and current.get(field) != request[field] for field in _COMPARED_FIELDS)


def cmd_deploy(region: str) -> int:
    client = control_client(region)
    deployed = list_custom_evaluators(client)
    exit_code = 0

    for config in load_local_configs():
        request = build_request(config)
        name = request["evaluatorName"]
        existing = deployed.get(name)

        if existing is None:
            response = client.create_evaluator(**request)
            evaluator_id = response["evaluatorId"]
            action = "created"
        elif _needs_update(client, existing["evaluatorId"], request):
            evaluator_id = existing["evaluatorId"]
            update = {k: v for k, v in request.items() if k != "evaluatorName"}
            client.update_evaluator(evaluatorId=evaluator_id, **update)
            action = "updated"
        else:
            print(f"{name}: unchanged ({existing['evaluatorId']}, {existing['status']})")
            continue

        status = wait_until_active(client, evaluator_id)
        print(f"{name}: {action} ({evaluator_id}), status {status}")
        if status != "ACTIVE":
            exit_code = 1
    return exit_code


def cmd_list(region: str) -> int:
    deployed = list_custom_evaluators(control_client(region))
    local = {c["evaluatorName"] for c in load_local_configs()}
    if not deployed and not local:
        print("No custom evaluators.")
        return 0
    for name in sorted(set(deployed) | local):
        summary = deployed.get(name)
        if summary is None:
            print(f"{name:<36} not deployed (local definition only)")
        else:
            origin = "local" if name in local else "account only"
            print(
                f"{name:<36} {summary['evaluatorId']:<50} {summary['status']:<8} "
                f"{summary.get('level', ''):<9} {origin}"
            )
    return 0


# --------------------------------------------------------------------------- validate-judge


def _parse_expectations(values: List[str]) -> Dict[str, str]:
    expectations = {}
    for value in values or []:
        scenario, _, verdict = value.partition("=")
        if verdict not in ("pass", "fail"):
            raise SystemExit(f"--expect must be <scenario_id>=pass|fail, got '{value}'")
        expectations[scenario] = verdict
    return expectations


def _run_time_window(results_dir: Path) -> tuple[datetime, datetime]:
    """The results directory name is the run's UTC end time. Allow for a long run."""
    end = datetime.strptime(results_dir.name, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    return end - timedelta(hours=2), end + timedelta(minutes=5)


def cmd_validate_judge(args: argparse.Namespace, region: str) -> int:
    results_dir = args.results.resolve()
    with (results_dir / "results.json").open(encoding="utf-8") as f:
        run = json.load(f)

    deployed = list_custom_evaluators(control_client(region))
    names = args.evaluators or [c["evaluatorName"] for c in load_local_configs()]
    evaluator_ids = []
    for name in names:
        summary = deployed.get(name)
        if summary is None or summary["status"] != "ACTIVE":
            raise SystemExit(f"{name} is not deployed and ACTIVE. Run 'manage_evaluators.py deploy' first.")
        evaluator_ids.append(summary["evaluatorId"])

    expectations = _parse_expectations(args.expect)
    start, end = _run_time_window(results_dir)
    collector = CloudWatchAgentSpanCollector(
        log_group_name=run["log_group"], region=region, max_wait_seconds=30, poll_interval_seconds=10
    )
    data_plane = boto3.client(
        "bedrock-agentcore",
        region_name=region,
        config=Config(retries={"max_attempts": 3, "mode": "adaptive"}, read_timeout=300),
    )

    rows: List[Dict[str, Any]] = []
    for scenario in run["scenario_results"]:
        if scenario["status"] != "COMPLETED":
            continue
        scenario_id = scenario["scenario_id"]
        if args.scenarios and scenario_id not in args.scenarios:
            continue

        spans = collector.collect(session_id=scenario["session_id"], start_time=start, end_time=end)
        targets = trace_ids(spans)
        if not targets:
            rows.append({"scenario_id": scenario_id, "error": "no spans found (expired or wrong time window)"})
            continue

        for evaluator_id in evaluator_ids:
            scores, labels, explanations, errors = [], [], [], []
            for _ in range(args.repeat):
                response = data_plane.evaluate(
                    evaluatorId=evaluator_id,
                    evaluationInput={"sessionSpans": spans},
                    evaluationTarget={"traceIds": targets[:10]},
                )
                for result in response.get("evaluationResults", []):
                    if result.get("errorCode"):
                        errors.append(f"{result['errorCode']}: {result.get('errorMessage')}")
                        continue
                    scores.append(float(result["value"]))
                    labels.append(result.get("label"))
                    explanations.append(result.get("explanation"))

            mean = statistics.mean(scores) if scores else None
            expected = expectations.get(scenario_id)
            verdict = None if mean is None else ("pass" if mean >= args.pass_threshold else "fail")
            rows.append({
                "scenario_id": scenario_id,
                "evaluator": display_name(evaluator_id),
                "evaluator_id": evaluator_id,
                "scores": scores,
                "labels": labels,
                "mean": mean,
                "verdict": verdict,
                "expected": expected,
                "match": None if expected is None or verdict is None else expected == verdict,
                "errors": errors,
                "explanations": explanations,
            })

    out_path = results_dir / f"judge-validation-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    out_path.write_text(json.dumps({"results_dir": str(results_dir), "rows": rows}, indent=2), encoding="utf-8")

    print(f"\nJudge validation of {results_dir.name} (pass = mean >= {args.pass_threshold}, {args.repeat} run(s) each)\n")
    print(f"{'scenario':<22}{'evaluator':<30}{'scores':<18}{'verdict':<9}{'expected':<10}match")
    print("-" * 95)
    mismatches = 0
    for row in rows:
        if "error" in row:
            print(f"{row['scenario_id']:<22}ERROR: {row['error']}")
            mismatches += 1
            continue
        scores = ", ".join(f"{s:.2f}" for s in row["scores"]) or "-"
        match = {True: "yes", False: "NO", None: "-"}[row["match"]]
        mismatches += row["match"] is False
        print(f"{row['scenario_id']:<22}{row['evaluator']:<30}{scores:<18}{row['verdict'] or '-':<9}"
              f"{row['expected'] or '-':<10}{match}")
        for error in row["errors"]:
            print(f"    error: {error}")
        if args.verbose:
            for label, explanation in zip(row["labels"], row["explanations"]):
                print(f"\n    [{label}] {explanation}\n")
    print(f"\nWritten to {out_path}")
    return 1 if mismatches else 0


# --------------------------------------------------------------------------- main


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--agent-config", type=Path, default=DEFAULT_AGENT_CONFIG,
                        help="Path to .bedrock_agentcore.yaml (its region is used).")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("deploy", help="Create or update the evaluators in evals/evaluators/.")
    sub.add_parser("list", help="List custom evaluators in the account.")
    judge = sub.add_parser("validate-judge", help="Re-score an earlier run and compare with hand labels.")
    judge.add_argument("--results", type=Path, required=True, help="A results/<timestamp> directory.")
    judge.add_argument("--evaluator", action="append", dest="evaluators",
                       help="Evaluator name to validate (default: all local definitions).")
    judge.add_argument("--scenario", action="append", dest="scenarios", help="Only this scenario_id.")
    judge.add_argument("--expect", action="append", help="Hand label as <scenario_id>=pass|fail. Repeatable.")
    judge.add_argument("--pass-threshold", type=float, default=0.67, help="Mean score counted as pass.")
    judge.add_argument("--repeat", type=int, default=1, help="Judge runs per scenario, to check stability.")
    judge.add_argument("--verbose", action="store_true", help="Print judge explanations.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")
    region = load_default_agent(args.agent_config.resolve()).region

    if args.command == "deploy":
        return cmd_deploy(region)
    if args.command == "list":
        return cmd_list(region)
    if args.command == "validate-judge":
        return cmd_validate_judge(args, region)
    parser.error(f"unknown command: {args.command}")  # unreachable unless a subparser is added without a handler


if __name__ == "__main__":
    sys.exit(main())
