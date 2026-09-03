import ast
import copy
import json
import re
import unittest
from pathlib import Path

from deployment.hackathon_deployer import (
    decode_definition_parts,
    definition_payload,
    load_json,
    render_copilot_parts,
    render_copilot_schema,
    render_ontology_parts,
    render_semantic_model_parts,
    validate_profile,
)

ROOT = Path(__file__).resolve().parents[1]
PROFILE = load_json(ROOT / "config" / "domains" / "water-utilities.json")
WORKSPACE_ID = "11111111-1111-1111-1111-111111111111"
LAKEHOUSE_ID = "22222222-2222-2222-2222-222222222222"


class ProfileTests(unittest.TestCase):
    def test_profile_cross_references_and_csv_headers(self):
        validate_profile(PROFILE, ROOT)

    def test_measure_expressions_are_present(self):
        expressions = [
            measure["expression"]
            for model in PROFILE["semanticModels"].values()
            for measure in model["measures"]
        ]
        self.assertTrue(expressions)
        self.assertTrue(all(expression.strip() for expression in expressions))

    def test_deployer_uses_fabric_compatible_python_syntax(self):
        source = (ROOT / "deployment" / "hackathon_deployer.py").read_text(encoding="utf-8")
        ast.parse(source, filename="hackathon_deployer.py", feature_version=(3, 10))


class SemanticModelTests(unittest.TestCase):
    def test_model_parts_and_base64_round_trip(self):
        # No profile ships a "basic" model anymore; use a synthetic flat-model
        # variant to keep coverage of the useRelationships=False code path.
        flat_profile = copy.deepcopy(PROFILE)
        flat_profile["semanticModels"]["flat"] = copy.deepcopy(PROFILE["semanticModels"]["optimized"])
        flat_profile["semanticModels"]["flat"]["useRelationships"] = False

        flat = render_semantic_model_parts(flat_profile, "flat", WORKSPACE_ID, LAKEHOUSE_ID)
        optimized = render_semantic_model_parts(PROFILE, "optimized", WORKSPACE_ID, LAKEHOUSE_ID)

        self.assertEqual(6, sum(path.startswith("definition/tables/") for path in flat))
        self.assertEqual(6, sum(path.startswith("definition/tables/") for path in optimized))
        self.assertNotIn("definition/relationships.tmdl", flat)
        self.assertIn("definition/relationships.tmdl", optimized)
        self.assertEqual(flat, decode_definition_parts(definition_payload(flat, "TMDL")))
        self.assertEqual(optimized, decode_definition_parts(definition_payload(optimized, "TMDL")))

        for model_key, parts, source_profile in (("flat", flat, flat_profile), ("optimized", optimized, PROFILE)):
            declarations = "\n".join(parts.values())
            for measure in source_profile["semanticModels"][model_key]["measures"]:
                escaped_name = re.escape(measure["name"])
                pattern = rf"^\s*measure\s+(?:'{escaped_name}'|{escaped_name})\s*="
                self.assertEqual(1, len(re.findall(pattern, declarations, re.MULTILINE)), measure["name"])

    def test_copilot_parts_and_lineage_schema(self):
        parts = render_copilot_parts(PROFILE)
        self.assertIn("Copilot/Instructions/instructions.md", parts)
        self.assertIn("Copilot/settings.json", parts)
        self.assertIn("Copilot/examplePrompts.json", parts)
        json.loads(parts["Copilot/settings.json"])
        json.loads(parts["Copilot/examplePrompts.json"])

        optimized = render_semantic_model_parts(PROFILE, "optimized", WORKSPACE_ID, LAKEHOUSE_ID)
        schema = json.loads(render_copilot_schema(PROFILE, optimized))
        self.assertEqual(6, len(schema["tables"]))
        self.assertTrue(all(table["id"] for table in schema["tables"]))

        measures_table_tmdl = optimized["definition/tables/_Measures.tmdl"]
        for measure in PROFILE["semanticModels"]["optimized"]["measures"]:
            escaped_name = re.escape(measure["name"])
            pattern = rf"^\s*measure\s+(?:'{escaped_name}'|{escaped_name})\s*="
            self.assertRegex(measures_table_tmdl, re.compile(pattern, re.MULTILINE))

        declarations = "\n".join(
            content
            for path, content in optimized.items()
            if path.startswith("definition/tables/")
        )
        declaration_count = len(re.findall(r"^\s*(?:table|column|measure)\s+", declarations, re.MULTILINE))
        lineage_tags = re.findall(
            r"^\s*lineageTag:\s*([0-9a-fA-F-]+)\s*$", declarations, re.MULTILINE
        )
        self.assertEqual(declaration_count, len(lineage_tags))
        self.assertEqual(len(lineage_tags), len(set(lineage_tags)))
        self.assertEqual(
            optimized,
            render_semantic_model_parts(PROFILE, "optimized", WORKSPACE_ID, LAKEHOUSE_ID),
        )


class OntologyTests(unittest.TestCase):
    def test_ontology_parts_are_deterministic_and_valid(self):
        first = render_ontology_parts(PROFILE, WORKSPACE_ID, LAKEHOUSE_ID)
        second = render_ontology_parts(PROFILE, WORKSPACE_ID, LAKEHOUSE_ID)
        self.assertEqual(first, second)
        self.assertEqual(5, sum(bool(re.fullmatch(r"EntityTypes/[^/]+/definition.json", path)) for path in first))
        self.assertEqual(5, sum("/DataBindings/" in path for path in first))
        self.assertEqual(3, sum(bool(re.fullmatch(r"RelationshipTypes/[^/]+/definition.json", path)) for path in first))
        self.assertEqual(3, sum("/Contextualizations/" in path for path in first))
        self.assertFalse(any("\\" in path for path in first))
        for path, content in first.items():
            if path == ".platform" or path.endswith(".json"):
                json.loads(content)


if __name__ == "__main__":
    unittest.main()
