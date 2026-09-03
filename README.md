# Water Utilities Data Agent Hackathon

A standalone Microsoft Fabric hackathon for building and evaluating a Water Utilities Operations Data Agent. The package uses deterministic synthetic UK data and must not be used for operational decisions, field direction, infrastructure security assessment, or regulatory reporting.

## Start Here

### Facilitators

1. Review the [facilitator guide](guides/water-utilities/FACILITATOR_GUIDE.md).
2. Import [NB_Deploy_Data_Agent_Hackathon.ipynb](NB_Deploy_Data_Agent_Hackathon.ipynb) into a capacity-backed Fabric workspace.
3. Leave `DOMAIN_PROFILE="water-utilities"` and `WORKSPACE_ID=""` for the default deployment.
4. Keep Prep for AI, Data Agent automation, and preview stages disabled for the participant baseline.
5. Run all cells and confirm that `WaterUtilitiesDemo` and `WaterUtilitiesSemanticModel` are created.

### Participants

Follow the [participant guide](guides/water-utilities/USER_GUIDE.md). The three-hour exercise improves one Data Agent through semantic-model tuning, Lakehouse source configuration, prepared routing marts, and an optional ontology.

## Evaluation

The challenge contains eight scored questions and their paraphrases. Two additional hard questions require regional ranking and a filtered cross-entity performance calculation.

1. Run [NB_Run_SDK_Evaluation.ipynb](NB_Run_SDK_Evaluation.ipynb) before tuning with `SNAPSHOT_NAME="baseline"`.
2. Run it again after tuning with `SNAPSHOT_NAME="final"`.
3. Complete [NB_Review_And_Score_Data_Agent.ipynb](NB_Review_And_Score_Data_Agent.ipynb) using the captured evidence.
4. Use the [evaluation guide](evaluation/EVALUATION_GUIDE.md) for scoring and troubleshooting.

The reviewed scorecard is worth 32 points for the baseline and 32 points for the final snapshot. The optional three-question routing dataset is evaluated separately.

## Repository Structure

| Path | Purpose |
| --- | --- |
| `config/domains/water-utilities.json` | Deployable domain profile and semantic-model source of truth |
| `sample-data/water-utilities/` | Deterministic base and prepared routing data |
| `agent-configuration/routing/water-utilities/` | Reference Data Agent routing configuration |
| `evaluation/` | Challenge, routing dataset, and evaluation instructions |
| `ontology/water-utilities/` | Optional Fabric IQ Ontology definition |
| `semantic-model/optimized/water-utilities/` | Human-readable model reference |
| `deployment/` | Reusable deployment implementation and notes |
| `guides/water-utilities/` | Participant and facilitator instructions |
| `tests/` | Data, definition, notebook, and documentation contracts |

## Local Validation

Python 3.10 or later is recommended.

```powershell
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

The Fabric notebooks install their own runtime dependencies inside Fabric. Local tests do not deploy or modify Fabric items.

## Synthetic Data

All customers, assets, incidents, inspections, and work orders are fictional. Locations are broad synthetic reporting regions, not precise infrastructure locations.
