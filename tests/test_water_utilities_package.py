import csv
import hashlib
import json
import re
import subprocess
import sys
import unittest
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "sample-data" / "water-utilities" / "base"
ROUTING = ROOT / "sample-data" / "water-utilities" / "derived-routing"

EXPECTED_HEADERS = {
    "customers.csv": ["customer_id", "account_holder_name", "customer_type", "region", "postcode_area", "service_status", "joined_date"],
    "assets.csv": ["asset_id", "asset_type", "region", "commissioned_date", "asset_status", "criticality"],
    "incidents.csv": ["incident_id", "asset_id", "customer_id", "incident_type", "severity", "status", "opened_at", "resolved_at", "estimated_leakage_m3", "service_interruption_hours", "repeat_incident_flag"],
    "work_orders.csv": ["work_order_id", "incident_id", "work_type", "priority", "status", "raised_at", "work_started_at", "promised_completion_at", "work_completed_at", "crew_region"],
    "inspections.csv": ["inspection_id", "asset_id", "inspection_type", "inspected_at", "result", "condition_score", "follow_up_required"],
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_timestamp(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")


class WaterUtilitiesPackageTests(unittest.TestCase):
    def test_profile_schema_csv_headers_and_sources(self):
        profile = json.loads((ROOT / "config" / "domains" / "water-utilities.json").read_text(encoding="utf-8"))
        schema = json.loads((ROOT / "config" / "domain-profile.schema.json").read_text(encoding="utf-8"))
        validate(profile, schema)
        self.assertEqual("water-utilities", profile["domain"]["id"])
        for table in profile["tables"]:
            source_path = ROOT / table["sourcePath"]
            self.assertTrue(source_path.is_file(), table["sourcePath"])
            with source_path.open(encoding="utf-8", newline="") as handle:
                actual_header = next(csv.reader(handle))
            declared_header = [column["source"] for column in table["columns"]]
            self.assertEqual(declared_header, actual_header, table["sourcePath"])
        for filename, expected_header in EXPECTED_HEADERS.items():
            with (BASE / filename).open(encoding="utf-8", newline="") as handle:
                self.assertEqual(expected_header, next(csv.reader(handle)))

    def test_foreign_keys_and_stable_keys(self):
        customers = read_csv(BASE / "customers.csv")
        assets = read_csv(BASE / "assets.csv")
        incidents = read_csv(BASE / "incidents.csv")
        work_orders = read_csv(BASE / "work_orders.csv")
        inspections = read_csv(BASE / "inspections.csv")
        for rows, key in ((customers, "customer_id"), (assets, "asset_id"), (incidents, "incident_id"), (work_orders, "work_order_id"), (inspections, "inspection_id")):
            values = [row[key] for row in rows]
            self.assertEqual(len(values), len(set(values)), key)
            self.assertTrue(all(values))
        customer_ids = {row["customer_id"] for row in customers}
        asset_ids = {row["asset_id"] for row in assets}
        incident_ids = {row["incident_id"] for row in incidents}
        self.assertTrue(all(row["asset_id"] in asset_ids for row in incidents))
        self.assertTrue(all(not row["customer_id"] or row["customer_id"] in customer_ids for row in incidents))
        self.assertTrue(all(row["incident_id"] in incident_ids for row in work_orders))
        self.assertTrue(all(row["asset_id"] in asset_ids for row in inspections))

    def test_generators_are_deterministic(self):
        tracked = list(BASE.glob("*.csv")) + list(ROUTING.glob("*.csv"))
        before = {path: sha256(path) for path in tracked}
        subprocess.run([sys.executable, str(BASE / "generate_base_data.py")], check=True, capture_output=True, text=True)
        subprocess.run([sys.executable, str(ROUTING / "generate_derived_routing_data.py")], check=True, capture_output=True, text=True)
        after = {path: sha256(path) for path in tracked}
        self.assertEqual(before, after)

    def test_challenge_answers_are_calculated_from_base_data(self):
        incidents = read_csv(BASE / "incidents.csv")
        work_orders = read_csv(BASE / "work_orders.csv")
        assets = read_csv(BASE / "assets.csv")
        inspections = read_csv(BASE / "inspections.csv")
        active = [row for row in incidents if row["status"] in {"Open", "Investigating"}]
        completed = [row for row in work_orders if row["status"] == "Completed"]
        durations = [(parse_timestamp(row["work_completed_at"]) - parse_timestamp(row["work_started_at"])).total_seconds() / 3600 for row in completed]
        on_time = sum(parse_timestamp(row["work_completed_at"]) <= parse_timestamp(row["promised_completion_at"]) for row in completed)
        active_high_assets = {row["asset_id"] for row in active if row["severity"] in {"Critical", "High"}}
        assets_by_id = {row["asset_id"]: row for row in assets}
        active_leakage_by_region = defaultdict(float)
        for row in active:
            active_leakage_by_region[assets_by_id[row["asset_id"]]["region"]] += float(row["estimated_leakage_m3"])
        top_region, top_region_leakage = max(active_leakage_by_region.items(), key=lambda item: item[1])
        incidents_by_id = {row["incident_id"]: row for row in incidents}
        service_interruption_completed = [
            row for row in completed
            if incidents_by_id[row["incident_id"]]["incident_type"] == "Service Interruption"
        ]
        service_interruption_on_time = sum(
            parse_timestamp(row["work_completed_at"]) <= parse_timestamp(row["promised_completion_at"])
            for row in service_interruption_completed
        )
        latest_inspections = {}
        for row in inspections:
            if row["asset_id"] not in latest_inspections or row["inspected_at"] > latest_inspections[row["asset_id"]]["inspected_at"]:
                latest_inspections[row["asset_id"]] = row
        attention_assets = sorted(row["asset_id"] for row in assets if row["asset_status"] == "Active" and (row["asset_id"] in active_high_assets or latest_inspections[row["asset_id"]]["result"] == "Failed"))
        calculated = {
            "WU001": len(active),
            "WU002": round(sum(float(row["estimated_leakage_m3"]) for row in active), 2),
            "WU003": round(sum(durations) / len(durations), 2),
            "WU004": sum(row["repeat_incident_flag"] == "true" for row in incidents),
            "WU005": round(100 * on_time / len(completed), 2),
            "WU006": len(attention_assets),
            "WU007": round(top_region_leakage, 2),
            "WU008": round(100 * service_interruption_on_time / len(service_interruption_completed), 2),
        }
        challenge = json.loads((ROOT / "evaluation" / "challenge" / "water-utilities.json").read_text(encoding="utf-8"))
        self.assertEqual(8, challenge["metadata"]["total_queries"])
        self.assertTrue(all(row.get("sdk_expected_answer") for row in challenge["evaluation_queries"]))
        self.assertEqual(calculated, {row["id"]: row["ground_truth_answer"] for row in challenge["evaluation_queries"]})
        self.assertEqual(attention_assets, challenge["evaluation_queries"][5]["ground_truth_detail"])
        self.assertEqual("North East", top_region)
        self.assertEqual(top_region, challenge["evaluation_queries"][6]["ground_truth_detail"])
        self.assertEqual((13, 28), (on_time, len(completed)))
        self.assertEqual((6, 14), (service_interruption_on_time, len(service_interruption_completed)))

    def test_routing_answers_and_configuration_match(self):
        routing = json.loads((ROOT / "evaluation" / "routing" / "water-utilities.json").read_text(encoding="utf-8"))
        calculated = {
            "WURT001": [row["customer_id"] for row in read_csv(ROUTING / "customer_service_impact.csv") if row["service_impact_segment"] == "High Impact"],
            "WURT002": [row["asset_id"] for row in read_csv(ROUTING / "asset_attention_scorecard.csv") if row["attention_band"] == "Immediate Review"],
            "WURT003": [row["work_order_id"] for row in read_csv(ROUTING / "repair_performance_mart.csv") if row["performance_band"] == "Completed Late"],
        }
        self.assertEqual(3, routing["metadata"]["total_queries"])
        self.assertTrue(all(row.get("sdk_expected_answer") for row in routing["evaluation_queries"]))
        self.assertEqual(calculated, {row["id"]: row["ground_truth_answer"] for row in routing["evaluation_queries"]})
        config = json.loads((ROOT / "agent-configuration" / "routing" / "water-utilities" / "data-agent-configuration.json").read_text(encoding="utf-8"))["dataAgentConfiguration"]
        selected = config["dataSources"][1]["selectedTables"]
        self.assertEqual(selected, [row["expected_object"] for row in routing["evaluation_queries"]])

    def test_guides_have_valid_links_and_required_content(self):
        guide_dir = ROOT / "guides" / "water-utilities"
        user_guide = (guide_dir / "USER_GUIDE.md").read_text(encoding="utf-8")
        facilitator_guide = (guide_dir / "FACILITATOR_GUIDE.md").read_text(encoding="utf-8")
        for step in range(1, 7):
            self.assertIn(f"## Step {step}", user_guide)
        for required in ("## Complete Answer Key", "## Escalating Hints", "## Controls By Source Type", "## Debrief Prompts"):
            self.assertIn(required, facilitator_guide)
        for identifier in ("INC0001", "WO0001", "INSP0001"):
            self.assertIn(identifier, user_guide)
        for guide_path in guide_dir.glob("*.md"):
            text = guide_path.read_text(encoding="utf-8")
            for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", text):
                if "://" in target or target.startswith("#"):
                    continue
                local_target = target.split("#", 1)[0]
                self.assertTrue((guide_path.parent / local_target).resolve().is_file(), f"Broken link in {guide_path.name}: {target}")

    def test_package_is_complete(self):
        required = [
            "config/domain-briefs/water-utilities.json", "config/domains/water-utilities.json",
            "sample-data/water-utilities/base/generate_base_data.py", "sample-data/water-utilities/derived-routing/generate_derived_routing_data.py",
            "semantic-model/optimized/water-utilities/README.md", "ontology/water-utilities/ontology-definition.json",
            "agent-configuration/routing/water-utilities/data-agent-configuration.json", "evaluation/challenge/water-utilities.json",
            "evaluation/routing/water-utilities.json", "guides/water-utilities/USER_GUIDE.md", "guides/water-utilities/FACILITATOR_GUIDE.md",
        ]
        required.extend(f"sample-data/water-utilities/base/{name}" for name in EXPECTED_HEADERS)
        required.extend(f"sample-data/water-utilities/derived-routing/{name}" for name in ("customer_service_impact.csv", "asset_attention_scorecard.csv", "repair_performance_mart.csv"))
        self.assertEqual([], [path for path in required if not (ROOT / path).is_file()])


if __name__ == "__main__":
    unittest.main()