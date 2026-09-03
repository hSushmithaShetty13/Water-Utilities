# Water Utilities Operations Facilitator Guide

Keep this guide private until teams have captured their baseline and diagnoses.

## How To Use This Guide

1. Give participants [USER_GUIDE.md](USER_GUIDE.md) and ask them to change one control at a time.
2. Use [NB_Deploy_Data_Agent_Hackathon.ipynb](../../NB_Deploy_Data_Agent_Hackathon.ipynb) to create or reset local workshop artifacts with `DOMAIN_PROFILE="water-utilities"`.
3. Use [NB_Run_SDK_Evaluation.ipynb](../../NB_Run_SDK_Evaluation.ipynb) for baseline and final live-agent runs.
4. Use [NB_Review_And_Score_Data_Agent.ipynb](../../NB_Review_And_Score_Data_Agent.ipynb) to review source/query evidence and score results.
5. Remind participants that every record is synthetic and no output directs field operations or establishes compliance.

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
- Capture all eight questions and paraphrases with `SNAPSHOT_NAME="baseline"`.
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

### Steps 3-4: Add And Tune The Lakehouse

- Add `WaterUtilitiesDemo` to the existing agent and initially expose only five `base_*` tables.
- Expect source ambiguity before tuning.
- Use selected objects, source descriptions, Data Agent instructions, and validated SQL examples for Lakehouse sources.
- Do not tell participants to add synonyms to Lakehouse tables; that control belongs to Prep for AI on Power BI semantic models.
- Teach exact `INC0001`, `WO0001`, and `INSP0001` lookups from the participant guide.
- Keep standard KPI questions on `WaterUtilitiesSemanticModel`.

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