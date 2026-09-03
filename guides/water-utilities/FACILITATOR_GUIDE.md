# Water Utilities Operations Facilitator Guide

Keep this guide private until teams have captured their baseline and diagnoses.

## How To Use This Guide

1. Give participants [USER_GUIDE.md](USER_GUIDE.md) and ask them to change one control at a time.
2. Use [NB_Deploy_Data_Agent_Hackathon.ipynb](../../NB_Deploy_Data_Agent_Hackathon.ipynb) to create or reset local workshop artifacts with `DOMAIN_PROFILE="water-utilities"`.
3. Use [NB_Run_SDK_Evaluation.ipynb](../../NB_Run_SDK_Evaluation.ipynb) after Steps 1-5. Participants change only `SNAPSHOT_NAME`.
4. Review the notebook's all-step evidence table for actual answers, SDK judgements, generated SQL/DAX/KQL, source traces, and thread links.
5. Treat Step 6 ontology questions as a qualitative extension rather than mixing them into the standard challenge score.
6. Remind participants that every record is synthetic and no output directs field operations or establishes compliance.

## Setup Checklist

- Run the deployment notebook with preview flags disabled.
- Confirm five base tables have 40 Customers, 30 Assets, 60 Incidents, 55 Work Orders, and 90 Inspections.
- Confirm `WaterUtilitiesSemanticModel` contains all four relationships and governed measures.
- Keep the Data Agent absent or untuned before participants begin.
- Retain [evaluation/challenge/water-utilities.json](../../evaluation/challenge/water-utilities.json) as the machine-readable answer source.

## Facilitator Solution Checkpoints

### Step 1: Untuned Baseline

- Source: `WaterUtilitiesSemanticModel` only.
- Prep for AI, synonyms, Verified Answers, and Data Agent instructions are empty.
- Capture all eight questions and paraphrases with `SNAPSHOT_NAME="step1_baseline"`.
- Do not reveal answers before teams record their own evidence.

### Step 2: Prep For AI And Agent Instructions

Recommended semantic-model rules:

```text
This is a synthetic UK Water Utilities Operations demonstration. Customers and account holders are synonyms. Incident, event, and issue are synonyms. Repair describes work performed through a work order, but repair and work order are not synonyms.

Active incidents have status Open or Investigating. High severity means Critical or High. Repeat incidents have another earlier incident on the same asset in the prior 30 days. Completed on time means work_completed_at is on or before promised_completion_at for completed work orders only.

Use explicit governed measures. Leakage is in cubic metres and repair duration is in hours. Dates use UK conventions. Do not imply live status, direct field operations, disclose sensitive infrastructure details, or claim regulatory compliance.
```

Recommended Data Agent instruction:

```text
Use WaterUtilitiesSemanticModel for standard governed customer, asset, incident, repair, inspection, leakage, interruption, and performance questions. Prefer explicit measures and state important filters and units. Ask a concise clarifying question only when different interpretations materially change the result. All records are synthetic; never present answers as live operational, safety, security, or compliance advice.
```

Checkpoint: WU001 returns `30` using `[Open Incidents]`; WU005 returns `46.43%` using `[Work Completed On Time]`.

### Optional Verified Answers

Create saved report Card visuals bound to `[Open Incidents]`, `[Total Estimated Leakage]`, `[Work Completed On Time]`, and `[Assets Requiring Attention]`. Use each visual's **Add to Q&A** action and enable **Verified answer**. Do not paste raw DAX as the verified response.

### Step 3: Add The Untuned Lakehouse

1. Add `WaterUtilitiesDemo` to the existing agent.
2. Select only `base_customers`, `base_assets`, `base_incidents`, `base_work_orders`, and `base_inspections`.
3. Leave the Lakehouse source description, data-source instructions, and example queries empty.
4. Capture `SNAPSHOT_NAME="step3_lakehouse_added"` before tuning the source. The notebook selects five held-out Lakehouse questions plus paraphrases.
5. Separately rerun WU001, WU003, and WU006 to expose overlap with `WaterUtilitiesSemanticModel`; treat these as routing guardrails rather than part of the Step 3/4 accuracy score.

Expected: simple exact-row questions may already pass. Multi-table joins, raw fields, latest-record selection, one-to-many completeness, or paraphrases should provide room for improvement. Governed KPI questions may route inconsistently while both sources expose similar entities.

### Step 4: Tune The Lakehouse Source

Apply each control in the location named below. Lakehouse tables do not have the semantic-model synonym editor; do not attempt to add Prep for AI synonyms here.

Before adding instructions, confirm all five tables remain selected and that the identifier and relationship columns are available: `customer_id`, `asset_id`, `incident_id`, `work_order_id`, and `inspection_id`. A description cannot compensate for an excluded join key.

#### Data Agent Instructions

Add this to the agent-level instructions. Preserve the Step 2 business definitions and safety rules.

```text
Route standard counts, totals, percentages, averages, rankings, and business-rule questions to WaterUtilitiesSemanticModel and use its explicit governed measures. This includes active incidents, leakage, repair duration, repeat incidents, on-time completion, assets requiring attention, and region-level KPI analysis.

Use WaterUtilitiesDemo base tables only for detailed record retrieval by an exact customer, asset, incident, work-order, or inspection identifier, or when the requested raw field is not exposed by WaterUtilitiesSemanticModel. Prefer one source when it can answer the complete question. Do not recompute a governed KPI in SQL merely because similar base columns are available.

When SQL is required, select only relevant columns, use exact key joins, qualify ambiguous column names, and apply an ORDER BY for multi-row results. State units for leakage and durations. All records are synthetic; do not imply live operational status, disclose precise infrastructure locations, direct field work, or claim regulatory compliance.
```

#### Lakehouse Source Description

Set the description for `WaterUtilitiesDemo` to:

```text
Detailed synthetic Water Utilities records for exact customer, asset, incident, work-order, and inspection lookup. The five base tables contain row-level attributes and relationship keys. Use this source for identifier-led detail questions and raw fields not exposed by WaterUtilitiesSemanticModel. It is not the authoritative source for governed KPI calculations.
```

#### Lakehouse Data-Source Instructions

Set the instructions on the `WaterUtilitiesDemo` source to:

```text
Use base_customers for customer/account-holder details and join it to base_incidents on customer_id. Use base_assets for asset attributes and join it to base_incidents or base_inspections on asset_id. Use base_incidents for incident details; active means status is Open or Investigating. Use base_work_orders for work-order details and join it to base_incidents on incident_id. Use base_inspections for inspection details and join it to base_assets on asset_id.

Use exact equality for identifiers such as CUS0001, AST0001, INC0001, WO0001, and INSP0001. Return only requested fields and preserve the stored values. Do not infer a missing relationship, use customer region as asset region, or treat priority as field direction. Route aggregate business metrics back to WaterUtilitiesSemanticModel.
```

#### Selected-Table Descriptions

Use these descriptions to make table grain and relationship keys explicit:

| Table | Description |
|---|---|
| `base_customers` | One row per fictional water service account holder, keyed by `customer_id`; contains account label, customer type, broad customer region, postcode area, service status, and joined date. |
| `base_assets` | One row per fictional maintainable water asset, keyed by `asset_id`; contains asset type, broad asset region, commissioned date, status, and analytical criticality. |
| `base_incidents` | One row per fictional incident, keyed by `incident_id`; links to one asset through `asset_id` and optionally one customer through `customer_id`; contains type, severity, status, timestamps, leakage, interruption hours, and repeat flag. |
| `base_work_orders` | One row per fictional work order, keyed by `work_order_id`; links to its incident through `incident_id`; contains work type, priority, status, lifecycle timestamps, and broad crew region. |
| `base_inspections` | One row per fictional inspection, keyed by `inspection_id`; links to its asset through `asset_id`; contains inspection type, timestamp, result, condition score, and follow-up flag. |

#### Validated SQL Example Queries

Add each question/query pair to the Lakehouse source and use the UI's **Validate** action before saving. These examples use Fabric SQL endpoint table and column names.

**Question:** Find incident INC0001 and show its available details.

```sql
SELECT incident_id, asset_id, customer_id, incident_type, severity, status,
	   opened_at, resolved_at, estimated_leakage_m3,
	   service_interruption_hours, repeat_incident_flag
FROM base_incidents
WHERE incident_id = 'INC0001';
```

**Question:** Show the detailed work order record for WO0001.

```sql
SELECT work_order_id, incident_id, work_type, priority, status, raised_at,
	   work_started_at, promised_completion_at, work_completed_at, crew_region
FROM base_work_orders
WHERE work_order_id = 'WO0001';
```

**Question:** Find inspection INSP0001 and include the inspected asset type and region.

```sql
SELECT i.inspection_id, i.asset_id, a.asset_type, a.region AS asset_region,
	   i.inspection_type, i.inspected_at, i.result, i.condition_score,
	   i.follow_up_required
FROM base_inspections AS i
INNER JOIN base_assets AS a ON a.asset_id = i.asset_id
WHERE i.inspection_id = 'INSP0001';
```

**Question:** Show the customer and asset linked to incident INC0001.

```sql
SELECT i.incident_id, i.incident_type, i.status,
	   c.customer_id, c.account_holder_name,
	   a.asset_id, a.asset_type, a.region AS asset_region
FROM base_incidents AS i
LEFT JOIN base_customers AS c ON c.customer_id = i.customer_id
INNER JOIN base_assets AS a ON a.asset_id = i.asset_id
WHERE i.incident_id = 'INC0001';
```

Add these advanced pairs to teach reusable query shapes. They deliberately use different identifiers from the held-out evaluation.

**Question:** What is the latest inspection for asset AST0012?

```sql
SELECT TOP 1 inspection_id, inspected_at, result,
	   condition_score, follow_up_required
FROM base_inspections
WHERE asset_id = 'AST0012'
ORDER BY inspected_at DESC, inspection_id DESC;
```

**Question:** Show work order WO0001 with its linked incident and affected asset.

```sql
SELECT w.work_order_id, w.work_type, w.status AS work_order_status,
	   i.incident_id, i.incident_type, i.severity,
	   a.asset_id, a.asset_type, a.region AS asset_region
FROM base_work_orders AS w
INNER JOIN base_incidents AS i ON i.incident_id = w.incident_id
INNER JOIN base_assets AS a ON a.asset_id = i.asset_id
WHERE w.work_order_id = 'WO0001';
```

**Question:** List all incidents for asset AST0008 in incident ID order.

```sql
SELECT incident_id, incident_type, status, estimated_leakage_m3
FROM base_incidents
WHERE asset_id = 'AST0008'
ORDER BY incident_id;
```

Validation checks:

| Example | Expected check |
|---|---|
| Incident lookup | Exactly one row: `INC0001`, `AST0008`, `CUS0004`, `Burst Main`, `Critical`, `Investigating`, 11.25 m3. |
| Work-order lookup | Exactly one row: `WO0001`, linked to `INC0006`, status `In Progress`, crew region `North East`. |
| Inspection and asset lookup | Exactly one row: `INSP0001`, linked to `AST0012`, with inspection result `Passed`. |
| Incident relationship lookup | Exactly one row linking `INC0001` to `CUS0004` and `AST0008`. |
| Latest-inspection pattern | Exactly one row: `INSP0061`, 3 May 2026 10:00, `Passed`, score 4, follow-up false. |
| Work-order relationship pattern | Exactly one row linking `WO0001` to `INC0006` and `AST0013`, a Service Reservoir in South East. |
| One-to-many incident pattern | Two ordered rows: `INC0001` Investigating at 11.25 m3, then `INC0031` Closed at 93.75 m3. |

Save the source description, source instructions, table descriptions, and validated examples. Wait for the agent configuration to finish updating, then start a new conversation. Do not test in the conversation used before the changes, because prior tool and source choices can mask the effect of tuning.

#### Step 4 Checkpoint

1. Clear or start a new agent conversation so earlier source choices do not affect the test.
2. Run the four example questions and confirm `WaterUtilitiesDemo` is selected and the generated SQL uses the intended base table and key predicate.
3. Capture `SNAPSHOT_NAME="step4_lakehouse_tuned"`. The notebook reruns the same 10 held-out prompts used at Step 3, not the four examples shown above.
4. Compare only Step 3 with Step 4. Inspect `source_trace`, `query_type`, and `generated_query`; a Step 4 answer passes the routing review only when it uses `WaterUtilitiesDemo` and the expected `base_*` tables.
5. Separately rerun WU001-WU008 and their paraphrases. Confirm they still route to `WaterUtilitiesSemanticModel` and use the governed measures in the answer key.
6. Diagnose any standard KPI that generates Lakehouse SQL as a routing failure, even when its numeric answer happens to be correct.

#### Why Step 3 And Step 4 Previously Matched

The earlier notebook ran the same eight semantic-model KPI questions at both stages. Step 4 is designed to improve Lakehouse record retrieval and SQL generation, so equal answer accuracy on those KPI questions did not mean the source tuning had no effect. It meant the evaluation did not exercise the capability being tuned.

The dedicated `lakehouse-tuning` dataset fixes that mismatch. It uses different IDs from the visible SQL examples and tests five behaviors: a three-table incident lookup, a three-table work-order lookup, deterministic latest-inspection selection, a raw customer-field lookup, and a complete one-to-many asset history. Each has a paraphrase.

#### Held-Out Step 3/4 Answer Key

Keep these answers private until both snapshots are complete.

| ID | Expected answer summary | Expected SQL objects |
|---|---|---|
| WULH001 | INC0017 is an Investigating Burst Main with 55.25 m3 leakage, affecting Synthetic Account 012 and a Metering Point in North East. | `base_incidents`, `base_customers`, `base_assets` |
| WULH002 | WO0017 is an In Progress Valve Replacement promised for 24 March 2026 16:30, crew region Midlands; linked to a High Pressure Loss incident and AST0003, a Pumping Station. | `base_work_orders`, `base_incidents`, `base_assets` |
| WULH003 | AST0004 latest inspection is INSP0063 at 11 May 2026 12:00; Failed, score 5, follow-up true. | `base_inspections` |
| WULH004 | CUS0011 is Synthetic Account 011, Household, postcode area B, Closed, joined 2 June 2019. | `base_customers` |
| WULH005 | AST0017 is an Active High-criticality Pumping Station in South West, commissioned 24 June 1999; incidents INC0028 Open, INC0032 Open, INC0058 Resolved. | `base_assets`, `base_incidents` |

Score interpretation:

- SDK answer pass: the expected facts are present and correct.
- Routing pass: `source_trace` or the thread identifies `WaterUtilitiesDemo`.
- SQL pass: `generated_query` uses the expected objects, exact key predicate, correct joins or ordering, and returns the complete result.
- Treat improved answer accuracy with incorrect routing as partial improvement, not a fully tuned Step 4 result.

Do not reuse the challenge `ground_truth_sql` as Lakehouse examples for aggregate questions. Those queries verify deterministic answers, while the workshop routing contract deliberately keeps governed KPIs on the semantic model.

### Step 5: Prepared Tables And Multi-Source Routing

Step 5 changes the Lakehouse from detailed base records to three prepared classification marts. Complete the object selection first; leaving a `base_*` table selected creates unnecessary overlap and can reduce routing accuracy.

#### Selected Objects

Deselect all five `base_*` tables and select only:

- `routing_customer_service_impact` for service-impact segments.
- `routing_asset_attention_scorecard` for latest-inspection and incident attention bands.
- `routing_repair_performance_mart` for repair performance bands.

Confirm that no other Lakehouse table is selected before saving.

#### Step 5 Data Agent Instructions

Replace the Step 4 base-table routing text with the following agent-level instructions. Retain the semantic-model business definitions and safety rules from Step 2.

```text
The agent has two complementary sources. Route by intent and use exactly one source whenever it can answer the complete question.

Use WaterUtilitiesSemanticModel for standard governed counts, totals, averages, percentages, rankings, and business-rule metrics. This includes open or active incidents, active estimated leakage, average repair duration, repeat incidents, completed-on-time percentage, assets requiring attention, affected customers, service interruption hours, and region-level KPI analysis. Prefer its explicit measures and do not recreate these metrics in SQL.

Use WaterUtilitiesDemo only when the question asks for one of these prepared row-level classifications:
1. Customer service-impact segment, including High Impact, Moderate Impact, or No Recorded Impact: use routing_customer_service_impact.
2. Asset attention band, including Immediate Review, Inspection Follow-up, or Routine Monitoring: use routing_asset_attention_scorecard.
3. Repair performance band, including Completed Late, Completed On Time, Open Priority Repair, or Open Routine Repair: use routing_repair_performance_mart.

Map "high impact customers" and "customers in the high impact segment" to service_impact_segment = 'High Impact'. Map "assets needing immediate review" to attention_band = 'Immediate Review'. Map "late completed repairs" and "completed repairs that were late" to performance_band = 'Completed Late'. Do not substitute a similar boolean or recompute the classification from another source.

For list questions, return every matching identifier exactly once in ascending identifier order. Do not return only a sample, top rows, or a count unless the user asks for one. Include concise supporting fields only when requested. State that the data is synthetic when confusion with live operations is possible. Never direct field operations, reveal precise infrastructure locations, or claim regulatory compliance.
```

#### Step 5 Lakehouse Source Description

Set the `WaterUtilitiesDemo` source description to:

```text
Prepared synthetic Water Utilities classification marts for customer service impact, asset attention, and repair performance. Each table contains one precomputed business classification column and supporting fields. Use this source only for questions that explicitly ask for a segment, attention band, or performance band. Standard governed KPIs remain authoritative in WaterUtilitiesSemanticModel.
```

#### Step 5 Lakehouse Data-Source Instructions

Set the instructions on `WaterUtilitiesDemo` to:

```text
Use routing_customer_service_impact only for customer service-impact classifications. One row represents one customer. Filter service_impact_segment using the exact stored values 'High Impact', 'Moderate Impact', or 'No Recorded Impact'. High Impact means the prepared row has at least one active incident or at least 10 total service-interruption hours.

Use routing_asset_attention_scorecard only for asset attention classifications. One row represents one asset. Filter attention_band using the exact stored values 'Immediate Review', 'Inspection Follow-up', or 'Routine Monitoring'. Immediate Review means an active asset has at least one active Critical or High incident. Inspection Follow-up means the active asset requires attention because its latest inspection failed but it has no active high-severity incident.

Use routing_repair_performance_mart only for work-order performance classifications. One row represents one work order. Filter performance_band using the exact stored values 'Completed Late', 'Completed On Time', 'Open Priority Repair', or 'Open Routine Repair'. Completed Late means the work order is Completed and its completion timestamp is later than its promised timestamp.

Select identifiers and only the supporting columns needed by the question. For complete lists, do not use TOP, LIMIT, sampling, or aggregation. Always ORDER BY the entity identifier. Do not join the three marts to answer the three standard classification questions. Do not use this source to calculate standard semantic-model KPIs.
```

#### Step 5 Table Descriptions

| Table | Description |
|---|---|
| `routing_customer_service_impact` | One row per customer, keyed by `customer_id`. Contains account-holder label, region, incident counts, total interruption hours, and the prepared `service_impact_segment`. Use only for customer impact-segment questions. |
| `routing_asset_attention_scorecard` | One row per asset, keyed by `asset_id`. Contains asset attributes, active high-severity incident count, latest inspection details, `requires_attention`, and the prepared `attention_band`. Use the band, not the boolean, when a question names a classification such as Immediate Review. |
| `routing_repair_performance_mart` | One row per work order, keyed by `work_order_id`. Contains incident and asset keys, incident severity, work-order status, repair duration, on-time flag, and the prepared `performance_band`. Use only for repair performance-band questions. |

#### Step 5 Validated SQL Examples

Add all three question/query pairs to the Lakehouse source and use the UI's **Validate** action. Keep the question wording aligned with the intended classification phrase.

**Question:** Which customers are in the high impact segment?

```sql
SELECT customer_id, account_holder_name, active_incidents,
	   service_interruption_hours
FROM routing_customer_service_impact
WHERE service_impact_segment = 'High Impact'
ORDER BY customer_id;
```

**Question:** Which assets need immediate review?

```sql
SELECT asset_id, asset_type, active_high_severity_incidents,
	   latest_inspection_result
FROM routing_asset_attention_scorecard
WHERE attention_band = 'Immediate Review'
ORDER BY asset_id;
```

**Question:** Which completed repairs were late?

```sql
SELECT work_order_id, incident_id, repair_duration_hours
FROM routing_repair_performance_mart
WHERE performance_band = 'Completed Late'
ORDER BY work_order_id;
```

Validation checks:

| Example | Expected validation result |
|---|---|
| High Impact customers | 10 ordered rows, from `CUS0004` through `CUS0040`; all rows have `service_impact_segment = 'High Impact'` in the source table. |
| Immediate Review assets | 14 ordered rows, from `AST0002` through `AST0030`; every row uses `attention_band = 'Immediate Review'`. |
| Completed Late repairs | 15 ordered rows, from `WO0003` through `WO0051`; every row uses `performance_band = 'Completed Late'`. |

#### Step 5 Save And Test Sequence

1. Verify only the three `routing_*` tables are selected.
2. Save the source description, data-source instructions, table descriptions, and all three validated examples.
3. Save the agent-level instructions and wait for the Data Agent configuration update to complete.
4. Start a new conversation. Do not reuse the Step 4 conversation because earlier base-table tool choices can affect routing.
5. Ask the three routing questions once in the agent UI. Confirm the source, table, exact filter literal, complete row count, and ascending order.
6. Fix configuration errors before running the SDK snapshot. Do not repeatedly prompt the same conversation until it happens to answer correctly.
7. Run `SNAPSHOT_NAME="step5_routing"` and inspect `source_trace` and `generated_query` in addition to the SDK answer judgement.
8. Run `SNAPSHOT_NAME="step5_final"` separately for the 16 standard challenge prompts. Confirm standard KPIs still use `WaterUtilitiesSemanticModel`.

The three exact routing questions are intentionally stored as validated examples because Step 5 demonstrates deterministic multi-source routing rather than held-out generalization. This configuration should make the expected route highly reliable, but Data Agent generation is nondeterministic; no instruction set can promise 100% on every run.

#### Step 5 Routing Checkpoint

| Test | Expected source | Expected object |
|---|---|---|
| How many open incidents do we have? | `WaterUtilitiesSemanticModel` | `[Open Incidents]` |
| What percentage of completed work was on time? | `WaterUtilitiesSemanticModel` | `[Work Completed On Time]` |
| Which customers are in the high impact segment? | `WaterUtilitiesDemo` | `routing_customer_service_impact` |
| Which assets need immediate review? | `WaterUtilitiesDemo` | `routing_asset_attention_scorecard` |
| Which completed repairs were late? | `WaterUtilitiesDemo` | `routing_repair_performance_mart` |

For each routing question, require all three conditions:

- Answer pass: every expected ID is present once, with no extra IDs.
- Routing pass: the trace or thread identifies `WaterUtilitiesDemo` and the expected mart.
- SQL pass: the query uses the exact classification value and orders by the correct identifier without row limiting.

#### Step 5 Final Accuracy Refinement

`step5_routing` and `step5_final` test different sources. A 3/3 routing result confirms the prepared marts are configured correctly; it does not improve the 16 semantic-model prompts automatically. If `step5_final` remains near 60%, refine `WaterUtilitiesSemanticModel`, Prep for AI, Verified Answers, and the agent instructions below. Do not add the challenge SQL as Lakehouse examples, because that would route governed KPI questions to the wrong source.

First use the all-step evidence table to identify whether each failure is the original question, its paraphrase, or both. Inspect `source_trace`, `query_type`, `generated_query`, and `actual_answer` before changing a control.

##### Final Semantic-Model Prep For AI Instructions

Replace or extend the semantic model's AI instructions with this copy-ready block:

```text
This model is the authoritative source for all standard Water Utilities KPIs. Always use the named explicit measure instead of recreating its logic from columns.

Question-to-measure rules:
- Open incidents, active incidents, open events, and events being investigated use [Open Incidents]. Active means Incident Status is Open or Investigating.
- Estimated leakage for active, open, or investigating incidents uses [Total Estimated Leakage]. Return cubic metres and do not sum all incident statuses.
- Average repair duration for completed work orders or completed repairs uses [Average Repair Duration]. Return hours and do not include Planned or In Progress work orders.
- Repeat incidents and incidents following another incident on the same asset within 30 days use [Repeat Incidents].
- Percentage or share of completed work orders completed on time uses [Work Completed On Time]. The denominator is completed work orders only; on time means Work Completed At is on or before Promised Completion At.
- Assets requiring attention use [Assets Requiring Attention]. Do not approximate this with asset criticality. The measure counts active assets having an Open or Investigating Critical/High incident or a Failed latest inspection.
- For the region with the highest active estimated leakage, group [Total Estimated Leakage] by Assets[Asset Region], sort the measure descending, and return the first region and its value.
- For on-time completion of work orders linked to service interruption incidents, filter Incidents[Incident Type] to Service Interruption and then evaluate [Work Completed On Time]. Keep the completed-work-order denominator inside that incident filter.

Terminology rules:
- Customer and account holder are equivalent terms.
- Incident, event, and issue are equivalent terms.
- Repair can refer to a work order in performance questions, but repair and work order are related concepts rather than global synonyms.
- Finished means Work Order Status is Completed. Promised timestamp means Promised Completion At.
- Leakage volume is measured in m3. Repair duration and service interruption are measured in hours.

Answer rules:
- Return the requested number, percentage, region, and unit directly.
- For percentages, include the percentage and numerator/denominator when available.
- Do not substitute a raw column aggregation when an explicit measure exists.
- Do not use WaterUtilitiesDemo for these governed KPI questions.
```

##### Final Data Agent Instructions

Add this after the Step 5 routing rules in the agent-level instructions:

```text
For the standard evaluation questions and their paraphrases, always route to WaterUtilitiesSemanticModel.

Use these exact measure mappings: open or active incident count -> [Open Incidents]; active estimated leakage -> [Total Estimated Leakage]; completed repair duration -> [Average Repair Duration]; repeat incident count -> [Repeat Incidents]; completed-on-time percentage -> [Work Completed On Time]; asset attention count -> [Assets Requiring Attention].

When a question adds a dimension or filter, keep the governed measure and apply model context rather than rebuilding the measure. For highest-leakage region, evaluate [Total Estimated Leakage] by Assets[Asset Region] and return the top region and value. For service-interruption repair performance, filter Incidents[Incident Type] to Service Interruption and evaluate [Work Completed On Time].

Treat the following paraphrases identically to their original concepts: events open or being investigated = active incidents; finished repairs = completed work orders; met the promised timestamp = completed on time; issues = incidents; most leakage = highest [Total Estimated Leakage]. State the unit and important filter in the answer.
```

##### Measure Descriptions To Verify

Confirm these descriptions are present and exposed in the AI Data Schema. Tight descriptions help measure selection more reliably than repeating the full DAX in agent instructions.

| Measure | Recommended description |
|---|---|
| `[Open Incidents]` | Count of incidents whose status is Open or Investigating; use for open events, active incidents, and issues being investigated. |
| `[Total Estimated Leakage]` | Sum of estimated leakage volume in m3 for Open or Investigating incidents; supports filtering and grouping by related asset attributes such as Asset Region. |
| `[Average Repair Duration]` | Average elapsed hours from Work Started At to Work Completed At for Completed work orders only. |
| `[Repeat Incidents]` | Count of incidents marked as having an earlier incident on the same asset within the prior 30 days. |
| `[Work Completed On Time]` | Percentage of Completed work orders finished on or before Promised Completion At; respects filters from related Incidents, including Incident Type. |
| `[Assets Requiring Attention]` | Count of Active assets with an Open/Investigating Critical/High incident or a Failed latest inspection; do not substitute asset criticality. |

##### Expected DAX Shapes For Hard Questions

Power BI semantic-model sources do not accept validated SQL question/query pairs. Use the generated DAX evidence to verify that the model preserved the governed measure. Equivalent DAX can vary, but these are the expected logical shapes.

Highest active leakage region:

```dax
EVALUATE
TOPN(
	1,
	SUMMARIZECOLUMNS(
		Assets[Asset Region],
		"Total Estimated Leakage", [Total Estimated Leakage]
	),
	[Total Estimated Leakage], DESC,
	Assets[Asset Region], ASC
)
```

On-time percentage for service-interruption work orders:

```dax
EVALUATE
ROW(
	"Work Completed On Time",
	CALCULATE(
		[Work Completed On Time],
		Incidents[Incident Type] = "Service Interruption"
	)
)
```

Reject generated logic that sums leakage without the measure's active-status filter, averages all work orders, divides by all work orders, counts asset criticality, or evaluates service interruption without filtering the related Incidents table.

##### Verified Answer Coverage

For the most reliable workshop result, create and verify saved report visuals for the governed questions. Verified Answers must be grounded in visuals; do not paste static text or raw DAX as an answer.

| Questions | Saved visual recipe |
|---|---|
| WU001 and paraphrase | Card using `[Open Incidents]`. |
| WU002 and paraphrase | Card using `[Total Estimated Leakage]`. |
| WU003 and paraphrase | Card using `[Average Repair Duration]`. |
| WU004 and paraphrase | Card using `[Repeat Incidents]`. |
| WU005 and paraphrase | Card using `[Work Completed On Time]`; show percentage formatting. |
| WU006 and paraphrase | Card using `[Assets Requiring Attention]`. |
| WU007 and paraphrase | Table or bar chart with `Assets[Asset Region]` and `[Total Estimated Leakage]`, sorted descending; apply a visual Top N 1 filter by `[Total Estimated Leakage]`. |
| WU008 and paraphrase | Card using `[Work Completed On Time]` with visual filter `Incidents[Incident Type] = Service Interruption`. |

For each saved visual, use **Add to Q&A**, enable **Verified answer**, and add both the original wording and its paraphrase if the interface supports alternate phrasings. Refresh the semantic model and wait for the Data Agent configuration to update before retesting in a new conversation.

##### Final Retest Sequence

1. Confirm the six governed measures and all relationship columns are included in the AI Data Schema.
2. Apply the semantic-model and Data Agent instruction blocks above.
3. Add Verified Answers, prioritizing the exact failed question IDs from the evidence table. For a 10/16 result, check paraphrase failures before creating unnecessary new measures.
4. Save and refresh the semantic model, then wait for the Data Agent update to complete.
5. Start a new conversation and test each previously failed original/paraphrase pair once.
6. Verify that standard questions use `WaterUtilitiesSemanticModel`; correct numbers produced by routing-mart SQL are still routing failures.
7. Rerun `SNAPSHOT_NAME="step5_final"`. The notebook uses the latest evaluation ID, so rerunning replaces the displayed Step 5 final comparison without deleting earlier Delta rows.

##### Blank Temporal Measures After Deployment

If `[Completed Work Orders]` returns 28 but `[Average Repair Duration]`, `[Completed On Time Work Orders]`, or `[Work Completed On Time]` displays blank, stop tuning instructions. This combination indicates a data-typing problem rather than measure selection.

The repository CSV files store dates as `yyyy-MM-dd` and timestamps as `yyyy-MM-dd HH:mm:ss`. An earlier deployment notebook parsed them as `dd/MM/yyyy` and `dd/MM/yyyy HH:mm:ss`, which silently wrote null temporal values into the Delta tables. The corrected deployment notebook uses the ISO source formats and raises an error instead of accepting an unparseable non-empty value.

Repair an existing workspace as follows:

1. Update or reimport the latest `NB_Deploy_Data_Agent_Hackathon.ipynb` from the repository.
2. Keep `DOMAIN_PROFILE="water-utilities"`, set `OVERWRITE_TABLES=True`, and retain the same target workspace and artifact names.
3. Run the setup cells, then rerun notebook section **3. Load profile data into managed Delta tables**. This overwrites the affected tables with correctly typed `date` and `timestamp` columns.
4. Run section **8. Refresh and verify deployment** so `WaterUtilitiesSemanticModel` sees the replaced Delta schema and values. If the existing imported notebook requires earlier variables, run the notebook from the start with semantic-model deployment enabled; the update is idempotent for the named artifacts.
5. In the Lakehouse, verify `base_work_orders` has non-null values for `work_started_at`, `promised_completion_at`, and completed rows of `work_completed_at`.
6. Refresh the report page. The cards should show 36.07 hours for `[Average Repair Duration]`, 13 for `[Completed On Time Work Orders]`, 28 for `[Completed Work Orders]`, and 46.43% for `[Work Completed On Time]`.
7. Refresh or reopen the semantic model and Data Agent, start a new conversation, and retest the six failed prompts before rerunning `step5_final`.

Do not replace blanks with zero in DAX. That would hide the failed timestamp ingestion and produce misleading results.

If a hard filtered question still fails after these controls, add a dedicated governed measure rather than instructing the agent to reconstruct business logic. For WU008, the optional measure is:

```dax
Service Interruption Work Completed On Time =
CALCULATE(
	[Work Completed On Time],
	Incidents[Incident Type] = "Service Interruption"
)
```

Describe it as: "Percentage of Completed work orders linked to Service Interruption incidents that finished on or before Promised Completion At." Add it to the AI Data Schema and bind the WU008 Verified Answer card to it. This is a targeted fallback; do not add duplicate measures unless evidence shows the existing filtered measure is not selected correctly.

## Complete Answer Key

Every value below was calculated from the checked-in generated CSVs.

| ID | Question | Expected answer | Expected source | Expected measure |
|---|---|---:|---|---|
| WU001 | How many open incidents do we have? | 30 | `WaterUtilitiesSemanticModel` | `[Open Incidents]` |
| WU002 | What is total estimated leakage for active incidents? | 2,771.25 m3 | `WaterUtilitiesSemanticModel` | `[Total Estimated Leakage]` |
| WU003 | What is average repair duration for completed work orders? | 36.07 hours | `WaterUtilitiesSemanticModel` | `[Average Repair Duration]` |
| WU004 | How many repeat incidents occurred? | 7 | `WaterUtilitiesSemanticModel` | `[Repeat Incidents]` |
| WU005 | What percentage of completed work orders were completed on time? | 46.43% (13 of 28) | `WaterUtilitiesSemanticModel` | `[Work Completed On Time]` |
| WU006 | How many assets require attention? | 14 | `WaterUtilitiesSemanticModel` | `[Assets Requiring Attention]` |
| WU007 | Which asset region has the highest total estimated leakage from active incidents, and what is that total? | North East, 738.75 m3 | `WaterUtilitiesSemanticModel` | `[Total Estimated Leakage]` |
| WU008 | What percentage of completed work orders linked to service interruption incidents were completed on time? | 42.86% (6 of 14) | `WaterUtilitiesSemanticModel` | `[Work Completed On Time]` |

Routing answers:

| ID | Expected answer | Expected source/object |
|---|---|---|
| WURT001 | CUS0004, CUS0008, CUS0012, CUS0016, CUS0020, CUS0024, CUS0028, CUS0032, CUS0036, CUS0040 | `WaterUtilitiesDemo` / `routing_customer_service_impact` |
| WURT002 | AST0002, AST0004, AST0006, AST0008, AST0010, AST0012, AST0016, AST0018, AST0020, AST0022, AST0024, AST0026, AST0028, AST0030 | `WaterUtilitiesDemo` / `routing_asset_attention_scorecard` |
| WURT003 | WO0003, WO0006, WO0007, WO0014, WO0015, WO0022, WO0023, WO0034, WO0038, WO0039, WO0042, WO0046, WO0047, WO0050, WO0051 | `WaterUtilitiesDemo` / `routing_repair_performance_mart` |

## Escalating Hints

Give one hint at a time.

### Level 1: Observe

- Which source and object did the agent select?
- Is the value wrong, the source wrong, or only the wording weak?
- Does the paraphrase fail in the same way?

### Level 2: Classify

- Is this terminology, governed business logic, schema scope, source routing, or response style?
- Does an explicit measure already represent the question?
- Is the requested classification available only in a routing mart?

### Level 3: Choose A Control

- Use semantic-model synonyms for alternate names; use instructions for definitions.
- Use Lakehouse descriptions and SQL examples for detailed rows and routing-only classifications.
- Narrow selected objects when overlapping sources cause ambiguity.
- Use a Verified Answer only for stable, high-value questions grounded in saved visuals.

Never give the exact answer, diagnosis, and control in one hint.

## Controls By Source Type

| Source | Controls |
|---|---|
| Power BI semantic model | Relationships, measures, names/descriptions, AI Data Schema, synonyms, AI instructions, Verified Answers, Data Agent instructions |
| Lakehouse | Selected tables/columns, descriptions, Data Agent instructions, validated SQL example queries |

Example question/query pairs are for Lakehouse SQL sources, not Power BI semantic-model sources.

## Safety Boundary

Refuse or redirect requests to dispatch crews, isolate assets, set repair priority, provide precise locations, expose credentials or vulnerabilities, certify water quality, or claim regulatory compliance. The acceptable response is an analytical summary of synthetic records plus a reminder to use approved systems and competent personnel for operational decisions.

## Debrief Prompts

- Which failure was initially misclassified, and what evidence changed the diagnosis?
- Which single configuration change improved both a question and its paraphrase?
- Where did a model measure outperform an agent-only instruction?
- How did source descriptions affect routing after the Lakehouse was attached?
- Why should routing classifications remain separate from governed standard metrics?
- How did the safety and privacy boundary change the phrasing of an otherwise correct answer?