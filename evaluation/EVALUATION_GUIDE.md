# SDK Evaluation Guide

The hackathon uses one participant evaluation notebook: `NB_Run_SDK_Evaluation.ipynb`. It runs the official Fabric Data Agent SDK, stores each workshop snapshot in the default Lakehouse, captures run-step query evidence, and compares all completed stages.

There is no simulation mode or manual scorecard. The checked-in challenge, Lakehouse-tuning, and routing JSON files are the sources of truth for questions, complete SDK expected answers, intended sources, and intended measures or objects.

## 1. Configure Fabric

1. Import `NB_Run_SDK_Evaluation.ipynb` into the Fabric workspace.
2. Attach `WaterUtilitiesDemo` and make it the notebook's default Lakehouse.
3. Set `WORKSPACE_NAME` and `DATA_AGENT_STAGE`.
4. Keep the same Data Agent throughout the workshop.

## 2. Run Workshop Snapshots

Change only `SNAPSHOT_NAME`, then run all cells:

| Stage | Snapshot | Dataset selected automatically |
| --- | --- | --- |
| Initial semantic-model agent | `step1_baseline` | Challenge |
| Prep for AI configured | `step2_prep_ai` | Challenge |
| Lakehouse attached | `step3_lakehouse_added` | Lakehouse tuning |
| Lakehouse tuned | `step4_lakehouse_tuned` | Lakehouse tuning |
| Final standard evaluation | `step5_final` | Challenge |
| Prepared routing marts | `step5_routing` | Routing |

Challenge runs contain 16 prompts: eight original questions and eight paraphrases. Lakehouse-tuning runs contain five held-out questions and five paraphrases. The validated examples use different IDs, so Step 4 measures whether the instructions and examples generalize rather than whether the agent memorized an answer. The routing run contains three prompts. Step 6 ontology questions remain a qualitative extension unless a separate ontology dataset is added.

The SDK creates `${TABLE_NAME}` and `${TABLE_NAME}_steps` in the `eval_result` schema when schemas are supported, or under the Lakehouse root tables otherwise.

## 3. Read The Evidence

The notebook joins result and step records using the SDK row `id` and displays:

- Actual and expected answers plus the official SDK judgement.
- Expected source and expected measure or object from the evaluation JSON.
- Extracted SQL, DAX, or KQL in `generated_query`.
- Tool function names and queries in `source_trace`.
- Fabric thread links when supplied by the SDK.

`source_trace` can support routing review, but the SDK does not guarantee a dedicated selected-source field. Do not claim an actual source unless the trace or thread evidence identifies it.

The final section reads the latest evaluation ID from each available snapshot table and produces a pass-rate trend, a question-by-step judgement matrix, and a detailed all-step evidence table.

Use only like-for-like comparisons:

- Compare `step1_baseline`, `step2_prep_ai`, and `step5_final` because all three use the challenge dataset.
- Compare `step3_lakehouse_added` with `step4_lakehouse_tuned` because both use the held-out Lakehouse-tuning dataset.
- Review `step5_routing` separately because it uses three prepared-mart questions.

Do not subtract pass rates from snapshots that use different datasets.

## Evidence Rules

- Keep the Data Agent name, stage, workspace, and challenge questions comparable across standard snapshots.
- A correct answer alone does not prove correct routing or query logic; inspect `generated_query`, `source_trace`, or the thread.
- For Step 3/4, require `WaterUtilitiesDemo` evidence and SQL over the expected `base_*` objects in addition to a correct answer.
- Empty `generated_query` means the SDK did not extract SQL, DAX, or KQL from that run. It must not be treated as proof that no query was executed.
- Re-running the same snapshot is allowed. The comparison uses the latest evaluation ID in that snapshot table.

## Troubleshooting

### No default Lakehouse

Attach `WaterUtilitiesDemo` in the notebook Explorer and set it as the default Lakehouse before running the SDK evaluation.

### SDK import error

Run the dependency installation cell and allow the Fabric Python session to restart. Then continue from the configuration cell.

### Missing SDK detail rows

Check the Data Agent name, workspace, stage, output table, and default Lakehouse. Rerun the same snapshot after correcting the configuration.

### Query evidence is empty

Open the supplied thread URL and inspect the run. The SDK preview may return tool metadata without an extracted command for some response paths.

For expected answers, hints, and debrief guidance, see the [Water Utilities facilitator guide](../guides/water-utilities/FACILITATOR_GUIDE.md).