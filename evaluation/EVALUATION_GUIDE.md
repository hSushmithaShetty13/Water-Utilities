# Evaluation Guide

The hackathon uses two notebooks with separate responsibilities:

| Notebook | Responsibility |
| --- | --- |
| `NB_Run_SDK_Evaluation.ipynb` | Run prompts against the live Fabric Data Agent and capture raw SDK evidence |
| `NB_Review_And_Score_Data_Agent.ipynb` | Review answers, sources, paraphrases, and generated query logic; calculate the deterministic 32-point score |

There is no simulation mode or separate CLI evaluator. The checked-in challenge JSON is the source of truth for questions and expected answers.

## 1. Capture The Baseline

1. Import `NB_Run_SDK_Evaluation.ipynb` into the Fabric workspace.
2. Attach `WaterUtilitiesDemo` and make it the notebook's default Lakehouse.
3. Set `AGENT_NAME` and `WORKSPACE_NAME`.
4. Set `DATA_AGENT_STAGE` to `sandbox` or `draft` for an unpublished agent, or `production` for a published agent.
5. Set `DATASET_NAME = "challenge"`, `SNAPSHOT_NAME = "baseline"`, and `INCLUDE_PARAPHRASES = True`.
6. Run all cells and retain the JSON and official-details CSV.

The SDK creates the configured evaluation table and companion steps table. Do not create them manually.

## 2. Capture The Final Snapshot

After tuning the same Data Agent:

1. Change `SNAPSHOT_NAME` to `final`.
2. Keep the agent, dataset, stage, and paraphrase setting unchanged.
3. Run all cells again and retain the final JSON and official-details CSV.

For the optional Step 5 routing extension, run the notebook separately with `DATASET_NAME = "routing"`. Do not merge those results into the eight-question score.

## 3. Review And Score

1. Import `NB_Review_And_Score_Data_Agent.ipynb`.
2. Use the baseline and final SDK artifacts to complete each observation.
3. Record the original answer, paraphrase answer, selected Fabric item, and copied SQL/DAX or run-step evidence.
4. Set `logic_correct` only after verifying the measure or table, filters, and aggregation.
5. Run all cells and resolve every actionable validation issue.
6. Submit the scorecard CSV and report JSON with the supporting SDK evidence.

Each question is worth four points in each phase:

- Correct original answer.
- Correct source.
- Correct paraphrase answer.
- Correct reviewed query or measure logic with evidence.

The maximum is 32 points for the baseline and 32 points for the final snapshot.

## Evidence Rules

- A correct answer alone does not prove correct routing or query logic.
- Do not award the logic point without copied SQL, DAX, or run-step evidence.
- Keep baseline and final settings comparable.
- Treat the official SDK result as captured evidence; the reviewed scorecard remains the event's deterministic scoring contract.

## Troubleshooting

### No default Lakehouse

Attach `WaterUtilitiesDemo` in the notebook Explorer and set it as the default Lakehouse before running the SDK evaluation.

### SDK import error

Run the dependency installation cell and allow the Fabric Python session to restart. Then continue from the configuration cell.

### Missing SDK detail rows

Check the Data Agent name, workspace, stage, output table, and default Lakehouse. Rerun the same snapshot after correcting the configuration.

### Scorecard validation issues

Complete every required answer and source, paste query evidence, and finish the human logic review for both baseline and final phases.

For expected answers, hints, and debrief guidance, see the [Water Utilities facilitator guide](../guides/water-utilities/FACILITATOR_GUIDE.md).