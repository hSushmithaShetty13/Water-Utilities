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
4. Rerun WU001, WU003, and WU006 to expose overlap with `WaterUtilitiesSemanticModel`.
5. Capture `SNAPSHOT_NAME="step3_lakehouse_added"` before tuning the source.

Expected: exact-row questions can use the Lakehouse, but governed KPI questions may route inconsistently while both sources expose similar entities.

### Step 4: Tune The Lakehouse Source

Apply each control in the location named below. Lakehouse tables do not have the semantic-model synonym editor; do not attempt to add Prep for AI synonyms here.

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

Validation checks:

| Example | Expected check |
|---|---|
| Incident lookup | Exactly one row: `INC0001`, `AST0008`, `CUS0004`, `Burst Main`, `Critical`, `Investigating`, 11.25 m3. |
| Work-order lookup | Exactly one row: `WO0001`, linked to `INC0006`, status `In Progress`, crew region `North East`. |
| Inspection and asset lookup | Exactly one row: `INSP0001`, linked to `AST0012`, with inspection result `Passed`. |
| Incident relationship lookup | Exactly one row linking `INC0001` to `CUS0004` and `AST0008`. |

#### Step 4 Checkpoint

1. Clear or start a new agent conversation so earlier source choices do not affect the test.
2. Run the four example questions and confirm `WaterUtilitiesDemo` is selected and the generated SQL uses the intended base table and key predicate.
3. Rerun WU001-WU008 and their paraphrases. Confirm they still route to `WaterUtilitiesSemanticModel` and use the governed measures in the answer key.
4. Capture `SNAPSHOT_NAME="step4_lakehouse_tuned"` and inspect `source_trace`, `query_type`, and `generated_query` in the SDK evidence table.
5. Diagnose any standard KPI that generates Lakehouse SQL as a routing failure, even when its numeric answer happens to be correct.

Do not reuse the challenge `ground_truth_sql` as Lakehouse examples for aggregate questions. Those queries verify deterministic answers, while the workshop routing contract deliberately keeps governed KPIs on the semantic model.

### Step 5: Prepared Tables And Multi-Source Routing

Deselect the five base tables and select only:

- `routing_customer_service_impact` for service-impact segments.
- `routing_asset_attention_scorecard` for latest-inspection and incident attention bands.
- `routing_repair_performance_mart` for repair performance bands.

Use this routing rule:

```text
Prefer WaterUtilitiesSemanticModel for standard governed metrics. Use WaterUtilitiesDemo only for service-impact segments, asset attention bands, and repair performance bands. Prefer one source and do not combine sources when one selected source answers the question.
```

| Test | Expected source | Expected object |
|---|---|---|
| How many open incidents do we have? | `WaterUtilitiesSemanticModel` | `[Open Incidents]` |
| What percentage of completed work was on time? | `WaterUtilitiesSemanticModel` | `[Work Completed On Time]` |
| Which customers are in the high impact segment? | `WaterUtilitiesDemo` | `routing_customer_service_impact` |
| Which assets need immediate review? | `WaterUtilitiesDemo` | `routing_asset_attention_scorecard` |
| Which completed repairs were late? | `WaterUtilitiesDemo` | `routing_repair_performance_mart` |

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