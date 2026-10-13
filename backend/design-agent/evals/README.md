# Design Agent Evaluations

On-demand evaluation of the technical design generator (`../mcp_agent.py`) with [Amazon Bedrock AgentCore Evaluations](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/evaluations-types.html). Each run invokes the deployed agent with a set of sample requirements, then scores the generated designs with built-in evaluators and one custom LLM-as-a-judge evaluator.

## How it works

```
dataset.json ──▶ run_evals.py ──invoke──▶ AgentCore Runtime 
                     │                          │ OpenTelemetry spans
                     │                          ▼
                     │                    CloudWatch (aws/spans + runtime log group)
                     │                          │
                     └──── Evaluate API ◀───────┘
                              │
                              ▼
                     results/<UTC timestamp>/
```

1. `run_evals.py` reads `default_agent` from `../.bedrock_agentcore.yaml` on every run, so a redeployed or switched runtime is picked up automatically.
2. Each scenario is sent to the runtime as one session. The runtime uses a Cognito JWT authorizer, so the script calls it over HTTPS with a bearer token.
3. After a 180 s wait for CloudWatch ingestion, the SDK's `OnDemandEvaluationDatasetRunner` collects the session's spans and calls the Evaluate API once per evaluator.

The agent needs no code changes for this. Strands emits the spans, and the runtime container runs under `opentelemetry-instrument`. CloudWatch Transaction Search must be enabled in the account.

## Files

| Path | Purpose |
|---|---|
| `run_evals.py` | Runs the dataset against the deployed agent and writes the results |
| `dataset.json` | Scenarios in the AgentCore predefined-scenario schema, with an `expected_response` per scenario as ground truth for Correctness |
| `data/` | Sample BRD/SRS documents referenced by `dataset.json` |
| `evaluators/` | Custom evaluator definitions: the request body (`.json`) and the judge instructions (`.md`) |
| `custom_evaluators.py` | Shared helpers for custom evaluators (load definitions, resolve IDs by name) |
| `manage_evaluators.py` | Deploys, lists and validates the custom evaluators |
| `requirements.txt` | Pinned dependencies |
| `results/` | Run output; gitignored |

## Scenarios

| Scenario | What it tests |
|---|---|
| `weather-app` | The full repository demo (`weather-app/` BRD and SRS). Checks that constraints such as "6 months prior to SOP" are carried over unchanged and that no ASIL is invented. |
| `infotainment-simple` | The small weather example from the deployment notebook, including `other_documents` as plain text. Its SRS rates weather alerts ASIL-B. |
| `ev-charging-planner` | Requirements that state QM explicitly. The design must not upgrade the app to an ASIL. |
| `tpms-display` | Mixed ASIL A / QM parts, with an interface control document passed as `other_documents`. Checks the allocation, freedom from interference and exact timing values. |
| `driver-profile-sync` | A draft full of TBD items. The design must list them as open issues instead of inventing values. |

In `dataset.json`, keys ending in `_file` hold a path relative to `dataset.json`. The script inlines the file's text and sends it under the key without the suffix, e.g. `srs_documents_file` becomes `srs_documents`.

## Evaluators

| Evaluator | Level | Measures |
|---|---|---|
| `Builtin.Coherence` | Trace | Internal consistency of the design |
| `Builtin.Correctness` | Trace | Agreement with the scenario's `expected_response` |
| `Builtin.Faithfulness` | Trace | Grounding in the prompt and tool output |
| `Builtin.InstructionFollowing` | Trace | Compliance with explicit instructions, e.g. "NEVER include code" |
| `Builtin.ToolParameterAccuracy` | Tool call | Parameters of each guideline tool call. Always 1.0 here, because both gateway tools take no parameters. |
| `Builtin.ToolSelectionAccuracy` | Tool call | Whether each guideline tool call was appropriate |
| `SafetyClassificationFidelity` (custom) | Trace | Whether ASIL/QM levels, hazards and safety goals trace to the requirements and are not invented, raised or lowered |

### SafetyClassificationFidelity

None of the built-ins checks whether a safety classification is grounded in the requirements, so this custom evaluator covers it.
- Judge: `us.anthropic.claude-sonnet-4-6` at temperature 0.
- Rubric: `evaluators/safety_classification_fidelity.md`. Only the requirements documents count as a source. The system prompt, the retrieved guideline and the judge's own judgement don't.
- Scale:
  - 1.0 fully traceable
  - 0.67 minor gaps
  - 0.33 unsupported additions
  - 0.0 invented or contradicting
- Online evaluation: it uses no ground-truth placeholders, so it can also be added to an online evaluation configuration later.

## Prerequisites

- AWS credentials for the account in `.bedrock_agentcore.yaml`. They need `bedrock-agentcore:Evaluate`, `GetEvaluator`, `ListEvaluators` (plus `CreateEvaluator` / `UpdateEvaluator` for deploying), `logs:StartQuery` / `GetQueryResults`, and Bedrock model access for the judge.
- The design agent deployed with observability enabled.
- A Cognito user for the runtime's JWT authorizer, set as `COGNITO_USERNAME` / `COGNITO_PASSWORD`. Without these variables the script falls back to the test user that the deployment notebook creates (`../utils.py`). `COGNITO_CLIENT_ID` overrides the client ID from the agent config.

```bash
pip install -r backend/design-agent/evals/requirements.txt
```

## Usage

Run from the repository root with the workspace virtual environment active.

```bash
# One-time, and after every change in evaluators/: create or update the custom evaluator
python backend/design-agent/evals/manage_evaluators.py deploy

# Show the plan without calling AWS
python backend/design-agent/evals/run_evals.py --dry-run

# Run all scenarios with all evaluators (about 5-6 minutes)
python backend/design-agent/evals/run_evals.py

# One scenario, with the judges' explanations
python backend/design-agent/evals/run_evals.py --scenario tpms-display --verbose

# Only the built-ins, or only selected evaluators
python backend/design-agent/evals/run_evals.py --no-custom
python backend/design-agent/evals/run_evals.py --evaluator SafetyClassificationFidelity

# CI gate: exit 1 if any evaluator's mean is below 0.7
python backend/design-agent/evals/run_evals.py --fail-under 0.7
```

Each run writes `results/<UTC timestamp>/`:
- `results.json`: the raw Evaluate API results
- `summary.json`: scores, labels and judge explanations
- `designs/<scenario>.md`: the generated designs, for manual review

## Validating the judge

Run this after every rubric change. `validate-judge` re-scores the sessions of an earlier run with the custom evaluator and compares the verdicts with hand labels you provide:

```bash
python backend/design-agent/evals/manage_evaluators.py validate-judge \
    --results backend/design-agent/evals/results/<timestamp> \
    --expect weather-app=pass --expect tpms-display=fail --repeat 2
```

- No agent call: it reuses the spans already stored in CloudWatch, so the designs stay fixed and only the judge varies.
- `--repeat` runs the judge several times on the same input to check that its scores are stable.
- A verdict is "pass" when the mean score is at least `--pass-threshold` (default 0.67).

Limitations:
- **Labels are not stored in the repo.** They are passed on the command line and copied into `results/<run>/judge-validation-*.json`, which is gitignored.
- **Spans expire.** Validation only works while the run's spans are still in CloudWatch: `aws/spans` keeps them for 30 days in this account.
- **The evidence is limited.** The rubric was tuned on the same cases it was validated on, and the labels were not set by a functional safety engineer. Treat a full match as evidence, not proof. Independent labels and seeded-defect cases that were not used for tuning would make it stronger.

## Interpreting results

- **One run is a baseline, not a measurement.** The agent and the judges are both nondeterministic, and scores move in coarse steps. Run 2-3 times before comparing a prompt or guideline change.
- **Correctness grades content, not format.** A design containing forbidden code can still score 1.0; InstructionFollowing is where format violations show up.
- **`skip`** for a tool evaluator means the agent made no tool call. Treat that as an instruction failure, because the agent is told to retrieve the guidelines first.
- **`NO_SPANS`** means the agent answered, but no spans were found for the session, so nothing was evaluated. Re-run that scenario with `--scenario`.
- **The console's Evaluations tab stays empty.** On-demand evaluation is stateless and creates no AWS resource; the tab lists online evaluation configurations only. The eval sessions do appear in CloudWatch GenAI Observability, with session IDs prefixed by the scenario ID.

## Cost

Each full run costs:
- one agent invocation per scenario (Amazon Nova 2 Lite)
- one judge call per evaluator and per trace or tool call
- the CloudWatch Logs Insights queries for span collection

Judge validation skips the agent invocations.
