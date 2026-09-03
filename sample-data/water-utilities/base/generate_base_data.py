"""Generate deterministic synthetic Water Utilities hackathon data."""

from __future__ import annotations

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent
SEED = 20260902
AS_OF = datetime(2026, 8, 31, 12, 0)


def write_csv(name: str, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with (OUTPUT_DIR / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def timestamp(value: datetime | None) -> str:
    return value.strftime("%Y-%m-%d %H:%M:%S") if value else ""


def generate() -> dict[str, list[dict[str, object]]]:
    random.seed(SEED)
    regions = ["North West", "North East", "Midlands", "South West", "South East"]
    postcode_areas = ["B", "BS", "CA", "EX", "GL", "LS", "M", "NE", "OX", "RG"]

    customers = []
    for number in range(1, 41):
        customers.append(
            {
                "customer_id": f"CUS{number:04d}",
                "account_holder_name": f"Synthetic Account {number:03d}",
                "customer_type": "Business" if number % 5 == 0 else "Household",
                "region": regions[(number - 1) % len(regions)],
                "postcode_area": postcode_areas[(number - 1) % len(postcode_areas)],
                "service_status": "Active" if number % 11 else "Closed",
                "joined_date": (datetime(2018, 1, 1) + timedelta(days=number * 47)).date().isoformat(),
            }
        )

    asset_types = ["Water Main", "Pumping Station", "Service Reservoir", "Valve", "Metering Point"]
    assets = []
    for number in range(1, 31):
        assets.append(
            {
                "asset_id": f"AST{number:04d}",
                "asset_type": asset_types[(number - 1) % len(asset_types)],
                "region": regions[(number + 1) % len(regions)],
                "commissioned_date": (datetime(1985, 1, 1) + timedelta(days=number * 311)).date().isoformat(),
                "asset_status": "Inactive" if number in {14, 29} else "Active",
                "criticality": ["Low", "Medium", "High"][number % 3],
            }
        )

    incidents = []
    previous_by_asset: dict[str, datetime] = {}
    incident_statuses = ["Open", "Investigating", "Resolved", "Closed"]
    severities = ["Low", "Medium", "High", "Critical"]
    incident_types = ["Leakage", "Burst Main", "Pressure Loss", "Service Interruption"]
    for number in range(1, 61):
        asset_index = ((number - 4) * 7) % len(assets) if number % 8 == 0 else (number * 7) % len(assets)
        asset = assets[asset_index]
        opened_at = datetime(2026, 1, 3, 7, 30) + timedelta(days=number * 3, hours=number % 9)
        status = incident_statuses[number % len(incident_statuses)]
        resolved_at = None if status in {"Open", "Investigating"} else opened_at + timedelta(hours=18 + number % 70)
        previous = previous_by_asset.get(str(asset["asset_id"]))
        repeat_flag = bool(previous and timedelta(0) < opened_at - previous <= timedelta(days=30))
        previous_by_asset[str(asset["asset_id"])] = opened_at
        incidents.append(
            {
                "incident_id": f"INC{number:04d}",
                "asset_id": asset["asset_id"],
                "customer_id": "" if number % 4 == 0 else customers[(number * 3) % len(customers)]["customer_id"],
                "incident_type": incident_types[number % len(incident_types)],
                "severity": severities[(number * 3) % len(severities)],
                "status": status,
                "opened_at": timestamp(opened_at),
                "resolved_at": timestamp(resolved_at),
                "estimated_leakage_m3": round(8.5 + number * 2.75, 2),
                "service_interruption_hours": round(0 if number % 3 else 1.25 + number / 20, 2),
                "repeat_incident_flag": str(repeat_flag).lower(),
            }
        )

    work_orders = []
    for number in range(1, 56):
        incident = incidents[(number * 5) % len(incidents)]
        raised_at = datetime.strptime(str(incident["opened_at"]), "%Y-%m-%d %H:%M:%S") + timedelta(hours=2)
        status = ["Planned", "In Progress", "Completed", "Completed"][number % 4]
        started_at = raised_at + timedelta(hours=4 + number % 12) if status != "Planned" else None
        promised_at = raised_at + timedelta(hours=30 + number % 36)
        completed_at = None
        if status == "Completed" and started_at:
            completed_at = started_at + timedelta(hours=8 + (number * 7) % 60)
        work_orders.append(
            {
                "work_order_id": f"WO{number:04d}",
                "incident_id": incident["incident_id"],
                "work_type": ["Leak Repair", "Valve Replacement", "Pressure Investigation", "Network Flush"][number % 4],
                "priority": ["Routine", "Urgent", "Emergency"][number % 3],
                "status": status,
                "raised_at": timestamp(raised_at),
                "work_started_at": timestamp(started_at),
                "promised_completion_at": timestamp(promised_at),
                "work_completed_at": timestamp(completed_at),
                "crew_region": regions[number % len(regions)],
            }
        )

    inspections = []
    results = ["Passed", "Passed", "Advisory", "Failed"]
    for number in range(1, 91):
        asset = assets[(number * 11) % len(assets)]
        inspected_at = datetime(2025, 9, 1, 9, 0) + timedelta(days=number * 4, hours=number % 6)
        inspections.append(
            {
                "inspection_id": f"INSP{number:04d}",
                "asset_id": asset["asset_id"],
                "inspection_type": ["Routine Condition", "Leak Detection", "Mechanical", "Water Quality Support"][number % 4],
                "inspected_at": timestamp(inspected_at),
                "result": results[(number * 5) % len(results)],
                "condition_score": 1 + (number * 3) % 5,
                "follow_up_required": str(number % 4 == 0 or number % 7 == 0).lower(),
            }
        )

    return {
        "customers": customers,
        "assets": assets,
        "incidents": incidents,
        "work_orders": work_orders,
        "inspections": inspections,
    }


def validate(data: dict[str, list[dict[str, object]]]) -> None:
    customer_ids = {row["customer_id"] for row in data["customers"]}
    asset_ids = {row["asset_id"] for row in data["assets"]}
    incident_ids = {row["incident_id"] for row in data["incidents"]}
    assert all(row["asset_id"] in asset_ids for row in data["incidents"])
    assert all(not row["customer_id"] or row["customer_id"] in customer_ids for row in data["incidents"])
    assert all(row["incident_id"] in incident_ids for row in data["work_orders"])
    assert all(row["asset_id"] in asset_ids for row in data["inspections"])


def main() -> int:
    data = generate()
    validate(data)
    fields = {
        "customers": ["customer_id", "account_holder_name", "customer_type", "region", "postcode_area", "service_status", "joined_date"],
        "assets": ["asset_id", "asset_type", "region", "commissioned_date", "asset_status", "criticality"],
        "incidents": ["incident_id", "asset_id", "customer_id", "incident_type", "severity", "status", "opened_at", "resolved_at", "estimated_leakage_m3", "service_interruption_hours", "repeat_incident_flag"],
        "work_orders": ["work_order_id", "incident_id", "work_type", "priority", "status", "raised_at", "work_started_at", "promised_completion_at", "work_completed_at", "crew_region"],
        "inspections": ["inspection_id", "asset_id", "inspection_type", "inspected_at", "result", "condition_score", "follow_up_required"],
    }
    for name, rows in data.items():
        write_csv(f"{name}.csv", fields[name], rows)
        print(f"Generated {name}.csv ({len(rows)} rows)")
    print(f"Synthetic dataset as-of timestamp: {AS_OF:%Y-%m-%d %H:%M:%S}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())