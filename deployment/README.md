# Reusable Notebook Deployment

[`NB_Deploy_Data_Agent_Hackathon.ipynb`](../NB_Deploy_Data_Agent_Hackathon.ipynb) deploys the hackathon assets from a domain profile. It runs inside Microsoft Fabric and defaults to its current workspace.

## Stable Core

The default run creates or reuses:

- A workspace folder and Lakehouse.
- All managed Delta tables declared by the profile.
- An Optimized Direct Lake semantic model with relationships, explicit measures, and descriptions.

The default participant-ready deployment intentionally leaves synonyms, Prep for AI, Verified Answers, and Data Agent configuration empty. Set `ENABLE_PREP_FOR_AI=True` only for an organizer demonstration that needs preconfigured AI instructions, example prompts, and a scoped AI Data Schema.

After all definition updates, the notebook refreshes each deployed semantic model and waits for completion. This initializes every Direct Lake partition so the model does not remain in a `NoData` state after deployment.

Semantic models are generated as TMDL and sent through the Fabric Semantic Model definition API. The workflow does not use PBIP, PBIX, BIM, or report-template files.

## Preview Stages

These stages are disabled by default:

- Organizer Prep for AI automation: set `ENABLE_PREP_FOR_AI=True` only when participants are not expected to author the AI configuration.
- Fabric IQ Ontology: set `ENABLE_ONTOLOGY=True` and `CONFIRM_PREVIEW_DEPLOYMENTS=True` after reviewing the proposed entities and relationships.
- Fabric Data Agent SDK: set `ENABLE_DATA_AGENT=True`; set `PUBLISH_DATA_AGENT=True` only when staging is ready to publish.

Verified Answers are not generated automatically. They require saved report visuals and live testing in Power BI/Fabric.

## Run

1. Download [../NB_Deploy_Data_Agent_Hackathon.ipynb](../NB_Deploy_Data_Agent_Hackathon.ipynb) from this repo, then use **Import → Notebook** in the target Fabric workspace to upload it. First time importing a notebook into Fabric? See the [participant guide](../guides/water-utilities/USER_GUIDE.md#automated-deployment) for the deployment steps.
2. Leave `WORKSPACE_ID=""` to deploy to the notebook's current workspace.
3. Keep AI, Data Agent, and preview automation flags disabled for participant-ready deployment.
4. Run all cells with `DOMAIN_PROFILE="water-utilities"` for the default scenario.
5. Review the deployment summary and begin the participant exercises.

Use a release tag or commit SHA for `REPOSITORY_REF` during an event so the notebook and its profile remain immutable.

## Custom Domain

A domain package consists of:

- A JSON profile conforming to [`domain-profile.schema.json`](../config/domain-profile.schema.json).
- Source CSV files whose paths and exact columns match the profile.
- Domain-specific relationships, measures, AI instructions, source routing, and evaluation prompts.

Either commit the profile under `config/domains/<domain>.json` and set `DOMAIN_PROFILE`, or set:

- `CUSTOM_PROFILE_URL` to an absolute raw JSON URL.
- `ASSET_BASE_URL` to the base URL for its relative source paths.

A new domain must model its real entities and metrics. Renaming legal entities alone is not sufficient for domains with different grains, relationships, or business rules.

## Profile Sections

| Section | Purpose |
| --- | --- |
| `domain` | Domain identity, culture, and currency |
| `artifacts` | Fabric item names |
| `tables` | Source paths, physical names, business names, columns, and types |
| `relationships` | Optimized semantic-model relationships |
| `semanticModels` | Optimized tables and measures |
| `ai` | AI instructions, schema scope, and Verified Answer candidates |
| `ontology` | Optional entities, bindings, and relationships |
| `agent` | Optional Data Agent sources, scope, instructions, and examples |

## Idempotency

The notebook reuses Fabric items by exact display name and updates complete semantic-model definitions in place. Semantic-model item IDs are assigned by Fabric when first created; their generated definitions remain reproducible on later runs. Ontology entity/property/relationship IDs are deterministic from the profile. The notebook overwrites only profile-owned Delta table paths when `OVERWRITE_TABLES=True` and does not delete unrelated workspace items.

## Local Validation

Run before publishing changes:

```powershell
python -m unittest discover -s tests -v
```

These tests validate the Water Utilities profile against the CSV headers, generated semantic-model and Ontology definitions, notebook metadata, parameter defaults, and Python syntax.
