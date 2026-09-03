# Water Utilities Optimized Semantic Model

## Artifact Reference

This folder documents the notebook-generated Direct Lake model for the Water Utilities Operations hackathon. The machine-readable source of truth is [config/domains/water-utilities.json](../../../config/domains/water-utilities.json).

Participant instructions are in [USER_GUIDE.md](../../../guides/water-utilities/USER_GUIDE.md), with checkpoints and the answer key in [FACILITATOR_GUIDE.md](../../../guides/water-utilities/FACILITATOR_GUIDE.md).

## Deployed Model

- Lakehouse: `WaterUtilitiesDemo`
- Semantic model: `WaterUtilitiesSemanticModel`
- Storage mode: Direct Lake
- Data classification: deterministic synthetic demonstration data

## Tables

| Lakehouse table | Model table | Grain |
|---|---|---|
| `base_customers` | Customers | One fictional account holder |
| `base_assets` | Assets | One fictional water asset |
| `base_incidents` | Incidents | One fictional incident affecting one primary asset |
| `base_work_orders` | Work Orders | One fictional work order belonging to one incident |
| `base_inspections` | Inspections | One fictional inspection of one asset |

## Relationships

| From | To | Cardinality | Cross filter |
|---|---|---|---|
| Incidents[Customer ID] | Customers[Customer ID] | Many to one | One direction |
| Incidents[Asset ID] | Assets[Asset ID] | Many to one | One direction |
| Work Orders[Incident ID] | Incidents[Incident ID] | Many to one | One direction |
| Inspections[Asset ID] | Assets[Asset ID] | Many to one | One direction |

## Governed Measures

- `Open Incidents`: Open or Investigating incidents.
- `Total Estimated Leakage`: estimated cubic metres for active incidents.
- `Average Repair Duration`: elapsed hours for completed work orders only.
- `Repeat Incidents`: incidents with another incident on the asset in the prior 30 days.
- `Work Completed On Time`: completed on or before the promised timestamp, divided by completed work orders.
- `Assets Requiring Attention`: active assets with an open Critical/High incident or a failed latest inspection.
- `Customers Affected` and `Service Interruption Hours`: supporting operational-performance measures.

All records are synthetic. The model must not be used to direct field operations or to claim regulatory compliance.