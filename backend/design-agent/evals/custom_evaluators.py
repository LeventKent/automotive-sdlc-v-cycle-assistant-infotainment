"""
Shared helpers for the custom AgentCore evaluators defined in evals/evaluators/.

Each evaluator is described by a JSON file that mirrors the CreateEvaluator request
(evaluatorName, description, level, evaluatorConfig). The judge instructions live in a
separate markdown file referenced by ``instructionsFile`` so the rubric stays readable;
it is inlined as ``evaluatorConfig.llmAsAJudge.instructions`` when the request is built.

Evaluator IDs are account specific and are not stored in the repository. They are
resolved by name through ListEvaluators whenever they are needed.
"""

from __future__ import annotations

import json
import logging
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import boto3
from botocore.config import Config

EVALUATORS_DIR = Path(__file__).resolve().parent / "evaluators"

# Custom evaluator IDs are "<name>-<10 char suffix>".
_ID_SUFFIX = re.compile(r"-[A-Za-z0-9]{10}$")

logger = logging.getLogger("design_agent_evals.custom")


def control_client(region: str):
    return boto3.client(
        "bedrock-agentcore-control",
        region_name=region,
        config=Config(retries={"max_attempts": 5, "mode": "adaptive"}, read_timeout=30),
    )


def display_name(evaluator_id: str) -> str:
    """Short column name: drop the Builtin. prefix or the custom ID suffix."""
    return _ID_SUFFIX.sub("", evaluator_id.removeprefix("Builtin."))


def load_local_configs(evaluators_dir: Path = EVALUATORS_DIR) -> List[Dict[str, Any]]:
    """Load every evaluator definition in evals/evaluators/*.json."""
    configs = []
    for path in sorted(evaluators_dir.glob("*.json")):
        with path.open(encoding="utf-8") as f:
            config = json.load(f)
        if "evaluatorName" not in config or "evaluatorConfig" not in config or "level" not in config:
            raise SystemExit(f"{path}: evaluatorName, level and evaluatorConfig are required")
        config["_path"] = path
        configs.append(config)
    return configs


def build_request(config: Dict[str, Any]) -> Dict[str, Any]:
    """Turn a local definition into CreateEvaluator/UpdateEvaluator parameters."""
    evaluator_config = json.loads(json.dumps(config["evaluatorConfig"]))  # deep copy
    instructions_file = config.get("instructionsFile")
    if instructions_file:
        judge = evaluator_config.get("llmAsAJudge")
        if judge is None:
            raise SystemExit(f"{config['_path']}: instructionsFile requires an llmAsAJudge config")
        path = config["_path"].parent / instructions_file
        judge["instructions"] = path.read_text(encoding="utf-8")

    request = {
        "evaluatorName": config["evaluatorName"],
        "level": config["level"],
        "evaluatorConfig": evaluator_config,
    }
    if config.get("description"):
        request["description"] = config["description"]
    return request


def list_custom_evaluators(client) -> Dict[str, Dict[str, Any]]:
    """Return the account's custom evaluators keyed by evaluatorName."""
    found: Dict[str, Dict[str, Any]] = {}
    token: Optional[str] = None
    while True:
        response = client.list_evaluators(**({"nextToken": token} if token else {}))
        for summary in response.get("evaluators", []):
            if summary.get("evaluatorType") in ("Builtin", "ThirdParty"):
                continue
            found[summary["evaluatorName"]] = summary
        token = response.get("nextToken")
        if not token:
            return found


def wait_until_active(client, evaluator_id: str, timeout_seconds: int = 180) -> str:
    deadline = time.monotonic() + timeout_seconds
    while True:
        status = client.get_evaluator(evaluatorId=evaluator_id)["status"]
        if status == "ACTIVE" or status.endswith("FAILED"):
            return status
        if time.monotonic() > deadline:
            return status
        time.sleep(5)


def resolve_custom_evaluator_ids(region: str) -> Tuple[List[str], List[str]]:
    """Map the local definitions to deployed, ACTIVE evaluator IDs.

    Returns (evaluator_ids, problems) where problems describes definitions that are
    not deployed or not ACTIVE, so callers can warn instead of failing the run.
    """
    configs = load_local_configs()
    if not configs:
        return [], []

    deployed = list_custom_evaluators(control_client(region))
    ids, problems = [], []
    for config in configs:
        name = config["evaluatorName"]
        summary = deployed.get(name)
        if summary is None:
            problems.append(f"{name} is not deployed (run manage_evaluators.py deploy)")
        elif summary["status"] != "ACTIVE":
            problems.append(f"{name} is {summary['status']}")
        else:
            ids.append(summary["evaluatorId"])
    return ids, problems
