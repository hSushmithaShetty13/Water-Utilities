"""Generate Water Utilities routing marts from the deterministic base CSVs."""

from __future__ import annotations

import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent
BASE_DIR = OUTPUT_DIR.parent / "base"
ACTIVE_INCIDENT_STATUSES = {"Open", "Investigating"}
HIGH_SEVERITIES = {"Critical", "High"}


def load_csv(name: str) -> list[dict[str, str]]:
    with (BASE_DIR / name).open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(name: str, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with (OUTPUT_DIR / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def parse_timestamp(value: str) -> datetime | None:
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S") if value else None


def customer_service_impact(customers: list[dict[str, str]], incidents: list[dict[str, str]]) -> list[dict[str, object]]:
    by_customer: dict[str, list[dict[str, str]]] = defaultdict(list)
    for incident in incidents:
        if incident["customer_id"]:
            by_customer[incident["customer_id"]].append(incident)
    rows = []
    for customer in customers:
        related = by_customer[customer["customer_id"]]
        active = [row for row in related if row["status"] in ACTIVE_INCIDENT_STATUSES]
        interruption = sum(float(row["service_interruption_hours"]) for row in related)
        if active or interruption >= 10:
            segment = "High Impact"
        elif related:
            segment = "Moderate Impact"
        else:
            segment = "No Recorded Impact"
        rows.append(
            {
                "customer_id": customer["customer_id"],
                "account_holder_name": customer["account_holder_name"],
                "region": customer["region"],
                "total_incidents": len(related),
                "active_incidents": len(active),
                "service_interruption_hours": round(interruption, 2),
                "service_impact_segment": segment,
            }
        )
    return rows


def asset_attention_scorecard(assets: list[dict[str, str]], incidents: list[dict[str, str]], inspections: list[dict[str, str]]) -> list[dict[str, object]]:
    incidents_by_asset: dict[str, list[dict[str, str]]] = defaultdict(list)
    inspections_by_asset: dict[str, list[dict[str, str]]] = defaultdict(list)
    for incident in incidents:
        incidents_by_asset[incident["asset_id"]].append(incident)
    for inspection in inspections:
        inspections_by_asset[inspection["asset_id"]].append(inspection)
    rows = []
    for asset in assets:
        asset_id = asset["asset_id"]
        asset_incidents = incidents_by_asset[asset_id]
        high_active = sum(1 for row in asset_incidents if row["status"] in ACTIVE_INCIDENT_STATUSES and row["severity"] in HIGH_SEVERITIES)
        latest = max(inspections_by_asset[asset_id], key=lambda row: row["inspected_at"], default=None)
        latest_result = latest["result"] if latest else "Not Inspected"
        requires_attention = asset["asset_status"] == "Active" and (high_active > 0 or latest_result == "Failed")
        if requires_attention and high_active > 0:
            band = "Immediate Review"
        elif requires_attention:
            band = "Inspection Follow-up"
        else:
            band = "Routine Monitoring"
        rows.append(
            {
                "asset_id": asset_id,
                "asset_type": asset["asset_type"],
                "region": asset["region"],
                "asset_status": asset["asset_status"],
                "active_high_severity_incidents": high_active,
                "latest_inspection_at": latest["inspected_at"] if latest else "",
                "latest_inspection_result": latest_result,
                "requires_attention": str(requires_attention).lower(),
                "attention_band": band,
            }
        )
    return rows


def repair_performance(work_orders: list[dict[str, str]], incidents: list[dict[str, str]]) -> list[dict[str, object]]:
    incident_by_id = {row["incident_id"]: row for row in incidents}
    rows = []
    for work_order in work_orders:
        started = parse_timestamp(work_order["work_started_at"])
        completed = parse_timestamp(work_order["work_completed_at"])
        promised = parse_timestamp(work_order["promised_completion_at"])
        duration = round((completed - started).total_seconds() / 3600, 2) if started and completed else ""
        on_time = completed is not None and promised is not None and completed <= promised
        incident = incident_by_id[work_order["incident_id"]]
        if work_order["status"] == "Completed" and not on_time:
            band = "Completed Late"
        elif work_order["status"] == "Completed":
            band = "Completed On Time"
        elif incident["severity"] in HIGH_SEVERITIES:
            band = "Open Priority Repair"
        else:
            band = "Open Routine Repair"
        rows.append(
            {
                "work_order_id": work_order["work_order_id"],
                "incident_id": work_order["incident_id"],
                "asset_id": incident["asset_id"],
                "incident_severity": incident["severity"],
                "work_order_status": work_order["status"],
                "repair_duration_hours": duration,
                "completed_on_time": str(on_time).lower(),
                "performance_band": band,
            }
        )
    return rows


def main() -> int:
    customers = load_csv("customers.csv")
    assets = load_csv("assets.csv")
    incidents = load_csv("incidents.csv")
    work_orders = load_csv("work_orders.csv")
    inspections = load_csv("inspections.csv")
    outputs = {
        "customer_service_impact.csv": (
            ["customer_id", "account_holder_name", "region", "total_incidents", "active_incidents", "service_interruption_hours", "service_impact_segment"],
            customer_service_impact(customers, incidents),
        ),
        "asset_attention_scorecard.csv": (
            ["asset_id", "asset_type", "region", "asset_status", "active_high_severity_incidents", "latest_inspection_at", "latest_inspection_result", "requires_attention", "attention_band"],
            asset_attention_scorecard(assets, incidents, inspections),
        ),
        "repair_performance_mart.csv": (
            ["work_order_id", "incident_id", "asset_id", "incident_severity", "work_order_status", "repair_duration_hours", "completed_on_time", "performance_band"],
            repair_performance(work_orders, incidents),
        ),
    }
    for name, (fieldnames, rows) in outputs.items():
        write_csv(name, fieldnames, rows)
        print(f"Generated {name} ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())