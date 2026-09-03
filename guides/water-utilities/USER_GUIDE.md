# Water Utilities Operations Hackathon

Use one continuous learning loop: ask a question, observe the result, form a hypothesis, change one durable control, and retest. All records are deterministic synthetic UK demonstration data. Nothing in this exercise directs field operations or demonstrates regulatory compliance.

You will extend one Data Agent through six steps:

1. Build the agent on the optimized semantic model.
2. Configure Prep for AI and agent instructions.
3. Attach the Lakehouse to the same agent.
4. Tune the Lakehouse source with descriptions and SQL examples.
5. Replace base tables with prepared routing marts.
6. Optionally add the ontology and retest relationship questions.

## Prerequisites

- A Microsoft Fabric workspace with capacity and permission to create Lakehouse, Semantic Model, Data Agent, and optional Ontology items.
- The files in this repository.
- Report authoring access only when testing optional Verified Answers.

## Automated Deployment

1. Import [NB_Deploy_Data_Agent_Hackathon.ipynb](../../NB_Deploy_Data_Agent_Hackathon.ipynb) into the target Fabric workspace.
2. Set `DOMAIN_PROFILE="water-utilities"` and leave `WORKSPACE_ID=""` to use the current workspace.
3. Keep `ENABLE_PREP_FOR_AI=False`, `ENABLE_DATA_AGENT=False`, and preview stages disabled for the participant baseline.
4. Run all cells and confirm `WaterUtilitiesDemo` and `WaterUtilitiesSemanticModel` are created.
5. Do not deploy against operational water-company systems or substitute real data.

## Suggested Three-Hour Schedule

| Time | Activity |
|---|---|
| 0:00-0:25 | Create the Data Agent and capture the semantic-model baseline |
| 0:25-1:05 | Configure Prep for AI and retest eight scored questions |
| 1:05-1:35 | Attach the Lakehouse and capture the two-source baseline |
| 1:35-2:05 | Tune Lakehouse descriptions, instructions, and SQL examples |
| 2:05-2:35 | Add derived marts and test routing |
| 2:35-2:50 | Optional ontology |
| 2:50-3:00 | Debrief |

## Quick File Map

- [Domain profile](../../config/domains/water-utilities.json)
- [Base generator](../../sample-data/water-utilities/base/generate_base_data.py)
- [Derived generator](../../sample-data/water-utilities/derived-routing/generate_derived_routing_data.py)
- [Semantic-model reference](../../semantic-model/optimized/water-utilities/README.md)
- [Ontology definition](../../ontology/water-utilities/ontology-definition.json)
- [Routing configuration](../../agent-configuration/routing/water-utilities/data-agent-configuration.json)
- [Eight scored questions](../../evaluation/challenge/water-utilities.json)
- [Five held-out Lakehouse tuning questions](../../evaluation/lakehouse-tuning/water-utilities.json)
- [Three routing questions](../../evaluation/routing/water-utilities.json)
- [Facilitator guide](FACILITATOR_GUIDE.md)

Use [NB_Run_SDK_Evaluation.ipynb](../../NB_Run_SDK_Evaluation.ipynb) for all measured runs. Change only `SNAPSHOT_NAME` after each stage; the notebook chooses the correct dataset and retains answer, judgement, generated SQL/DAX/KQL, tool trace, and thread evidence.

| After stage | `SNAPSHOT_NAME` | Prompts |
| --- | --- | ---: |
| Step 1 initial agent | `step1_baseline` | 16 challenge prompts |
| Step 2 Prep for AI | `step2_prep_ai` | 16 challenge prompts |
| Step 3 Lakehouse attached | `step3_lakehouse_added` | 10 held-out Lakehouse prompts |
| Step 4 Lakehouse tuned | `step4_lakehouse_tuned` | Same 10 held-out Lakehouse prompts |
| Step 5 final standard test | `step5_final` | 16 challenge prompts |
| Step 5 prepared routing marts | `step5_routing` | 3 routing prompts |

Run all notebook cells for each snapshot. Compare Step 3 directly with Step 4; both use the same unseen identifier, join, raw-field, latest-record, and one-to-many questions. Compare challenge snapshots only with other challenge snapshots. The final section reads every available snapshot table, skips stages not yet run, and shows the pass rates, question-by-step judgement, and formula evidence. Step 6 ontology remains a qualitative extension because it uses different relationship questions.

## Step 1: Build The Semantic-Model Agent

### Goal

Create the one agent you will improve throughout the workshop and capture an untuned baseline.

### Actions

1. Create a Fabric Data Agent named `WaterUtilitiesOperationsAgent`.
2. Add `WaterUtilitiesSemanticModel` and expose `Customers`, `Assets`, `Incidents`, `Work Orders`, and `Inspections`.
3. Leave Prep for AI, synonyms, Verified Answers, and Data Agent instructions empty.
4. Ask all eight questions below and their paraphrases. Record the answer, selected source, measure or query, and confidence.

| ID | Question | Paraphrase |
|---|---|---|
| WU001 | How many open incidents do we have? | How many events are open or being investigated? |
| WU002 | What is total estimated leakage for active incidents? | How many cubic metres are associated with open or investigating issues? |
| WU003 | What is the average repair duration for completed work orders? | How many hours do completed repairs take on average? |
| WU004 | How many repeat incidents occurred? | How many incidents followed another on the asset within 30 days? |
| WU005 | What percentage of completed work orders were completed on time? | What share of finished repairs met the promised timestamp? |
| WU006 | How many assets require attention? | Count active assets with an open high-severity incident or failed latest inspection. |
| WU007 | Which asset region has the highest total estimated leakage from active incidents, and what is that total? | Find the region with the most leakage across open or investigating incidents and give its volume. |
| WU008 | What percentage of completed work orders linked to service interruption incidents were completed on time? | Of finished repairs for service interruption events, what share met the promised completion timestamp? |

Expected at this stage: model relationships and measures help, but alternate terminology and multi-condition rules may be inconsistent. Capture this baseline before tuning.

## Step 2: Configure Prep For AI

### Goal

Make the semantic model reliable for governed Water Utilities questions without changing the source data.

### Actions

1. In `WaterUtilitiesSemanticModel` Prep for AI, scope the AI Data Schema to business-facing fields and all governed measures.
2. Add `account holder` as a synonym for customer. Add `event` and `issue` as synonyms for incident.
3. Do not make repair a synonym for work order; they are related concepts, not equivalent labels.
4. Add the business rules: active incidents are Open or Investigating; high severity is Critical or High; repeat means an earlier same-asset incident in the prior 30 days.
5. Add Data Agent instructions to prefer explicit measures and state filters and units.
6. Change one control at a time, rerun the question and paraphrase, and record evidence.

Lakehouse tables do not have the semantic-model synonym editor. Synonyms in this step belong to the Power BI semantic-model source. Data agent instructions are a separate control for source preference and response behaviour.

Optional Verified Answers should be created from saved report visuals bound to stable measures such as `[Open Incidents]`, `[Total Estimated Leakage]`, and `[Work Completed On Time]`.

Expected: all eight standard questions route to `WaterUtilitiesSemanticModel` and select the governed measure named in the facilitator answer key.

## Step 3: Attach The Lakehouse

### Goal

Observe source ambiguity before applying Lakehouse-specific tuning.

### Actions

1. Add `WaterUtilitiesDemo` to the same agent.
2. Select only `base_customers`, `base_assets`, `base_incidents`, `base_work_orders`, and `base_inspections`.
3. Leave the new source description and SQL examples empty.
4. Rerun WU001, WU003, and WU006 and record source selection.

Expected: overlapping sources may cause hesitation or unnecessary SQL even though the semantic model already owns governed metrics.

## Step 4: Tune The Lakehouse Source

### Goal

Teach detailed row lookup without displacing the semantic model for governed measures.

### Actions

1. Describe `WaterUtilitiesDemo` as a detailed synthetic record source.
2. Add a Data Agent instruction: prefer `WaterUtilitiesSemanticModel` for governed metrics; use base Lakehouse tables for exact identifier lookups or fields not exposed by the model.
3. Add and validate these Lakehouse SQL example pairs:

```sql
SELECT * FROM base_incidents WHERE incident_id = 'INC0001'
```

```sql
SELECT * FROM base_work_orders WHERE work_order_id = 'WO0001'
```

```sql
SELECT * FROM base_inspections WHERE inspection_id = 'INSP0001'
```

Ask:

- Find incident INC0001 and show its available details.
- Show the detailed work order record for WO0001.
- Find inspection INSP0001 and show its available details.

Example question/query pairs belong on the Lakehouse SQL source, not on the `WaterUtilitiesSemanticModel` Power BI semantic-model source.

Expected: identifier lookups use `WaterUtilitiesDemo`; all eight scored KPI questions continue to use the semantic model.

## Step 5: Add Prepared Routing Marts

### Goal

Demonstrate clean source routing for classifications that do not exist in the optimized model.

### Actions

1. Deselect the five `base_*` tables.
2. Select only `routing_customer_service_impact`, `routing_asset_attention_scorecard`, and `routing_repair_performance_mart`.
3. Apply the descriptions and SQL examples in the [routing configuration](../../agent-configuration/routing/water-utilities/data-agent-configuration.json).
4. Clear chat history and ask the three routing questions:
   - Which customers are in the high impact segment?
   - Which assets need immediate review?
   - Which completed repairs were late?
5. Inspect selected source and generated SQL. A correct-looking answer alone does not prove correct routing.

Expected: routing questions use `WaterUtilitiesDemo` and the named routing table. Standard KPIs continue to use `WaterUtilitiesSemanticModel`.

## Step 6: Optional Ontology

### Goal

Explore cross-entity relationships without treating analytics as operational direction.

### Actions

1. Review [ontology-definition.json](../../ontology/water-utilities/ontology-definition.json).
2. Deploy the ontology only if the workspace supports the preview and the facilitator has enabled it.
3. Ask relationship questions such as "Which incidents and work orders relate to AST0002?" and "What is the latest inspection for assets with open incidents?"
4. Confirm that the answer identifies synthetic data and does not recommend field action.

Expected: the ontology improves entity traversal. It does not authorize repairs, assess live risk, or prove compliance.

## Reading The Evaluation Tables

- `expected_source` and `expected_measure_or_object` describe the intended route from the checked-in dataset.
- `actual_answer` and `evaluation_judgement` come from the official SDK evaluation result.
- `query_type` and `generated_query` normalize SQL, DAX, or KQL extracted by the SDK from the run steps.
- `source_trace` retains function names and function queries. It is evidence, not a guaranteed selected-source field.
- `thread_url` opens the supporting Fabric conversation when the SDK provides one.

Use the all-step evidence CSV for detailed review and the judgement-matrix CSV for a compact progression view.

Do not use this synthetic package for operational decisions, customer contact, infrastructure security assessment, safety-critical work, or regulatory reporting.