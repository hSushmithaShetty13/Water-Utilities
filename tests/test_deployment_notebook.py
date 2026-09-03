import ast
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = ROOT / "NB_Deploy_Data_Agent_Hackathon.ipynb"


class DeploymentNotebookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.notebook = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))
        cls.cells = cls.notebook["cells"]
        cls.source = "\n".join("".join(cell["source"]) for cell in cls.cells)

    def test_notebook_structure_and_metadata(self):
        self.assertEqual(4, self.notebook["nbformat"])
        self.assertEqual(18, len(self.cells))
        identifiers = [cell["id"] for cell in self.cells]
        self.assertEqual(len(identifiers), len(set(identifiers)))
        for cell in self.cells:
            expected_language = "python" if cell["cell_type"] == "code" else "markdown"
            self.assertEqual(expected_language, cell["metadata"]["language"])
        self.assertIn("parameters", self.cells[1]["metadata"]["tags"])

    def test_all_code_cells_compile(self):
        for number, cell in enumerate(self.cells, start=1):
            if cell["cell_type"] == "code":
                compile("".join(cell["source"]), f"cell-{number}", "exec")

    def test_parameter_defaults(self):
        tree = ast.parse("".join(self.cells[1]["source"]))
        values = {}
        for statement in tree.body:
            if isinstance(statement, ast.Assign) and isinstance(statement.targets[0], ast.Name):
                values[statement.targets[0].id] = ast.literal_eval(statement.value)
        self.assertEqual("", values["WORKSPACE_ID"])
        self.assertEqual("water-utilities", values["DOMAIN_PROFILE"])
        self.assertEqual("hSushmithaShetty13", values["REPOSITORY_OWNER"])
        self.assertEqual("Water-Utilities", values["REPOSITORY_NAME"])
        self.assertEqual("main", values["REPOSITORY_REF"])
        self.assertNotIn("DEPLOY_BASIC_MODEL", values)
        self.assertTrue(values["DEPLOY_OPTIMIZED_MODEL"])
        self.assertFalse(values["ENABLE_PREP_FOR_AI"])
        self.assertTrue(values["REFRESH_SEMANTIC_MODELS"])
        self.assertFalse(values["ENABLE_ONTOLOGY"])
        self.assertFalse(values["CONFIRM_PREVIEW_DEPLOYMENTS"])
        self.assertFalse(values["ENABLE_DATA_AGENT"])
        self.assertFalse(values["PUBLISH_DATA_AGENT"])
        self.assertEqual(1800, values["LRO_TIMEOUT_SECONDS"])
        self.assertEqual(180, values["ITEM_DISCOVERY_TIMEOUT_SECONDS"])
        self.assertEqual(900, values["SEMANTIC_REFRESH_TIMEOUT_SECONDS"])
        self.assertEqual(300, values["LAKEHOUSE_SYNC_TIMEOUT_SECONDS"])

    def test_required_deployment_patterns(self):
        for section in range(1, 9):
            self.assertIn(f"## {section}.", self.source)
        self.assertIn('context.get("currentWorkspaceId")', self.source)
        self.assertIn('notebookutils.conf.get("trident.onelake.endpoint")', self.source)
        self.assertIn("abfss://{target_workspace_id}@{onelake_endpoint}", self.source)
        self.assertIn('f"{FABRIC_API}/operations/{operation_id}"', self.source)
        self.assertIn("updateDefinition", self.source)
        self.assertIn("deployer.definition_payload", self.source)
        self.assertNotIn("Waiting for semantic-model lineage tags", self.source)
        self.assertIn("https://api.powerbi.com/v1.0/myorg", self.source)
        self.assertIn('status == "Completed"', self.source)
        self.assertIn("refresh_semantic_model(model_id, model_name)", self.source)
        self.assertIn("CONFIRM_PREVIEW_DEPLOYMENTS", self.source)
        self.assertIn("fabric-data-agent-sdk==0.1.28a0", self.source)
        self.assertIn("wait_for_lakehouse_table_sync", self.source)
        self.assertIn("lakehouses/{lakehouse_id}/tables", self.source)

    def test_csv_temporal_values_use_iso_source_formats(self):
        self.assertIn('source_format = "yyyy-MM-dd" if data_type == "date" else "yyyy-MM-dd HH:mm:ss"', self.source)
        self.assertIn("Could not parse {data_type} value", self.source)
        self.assertNotIn('F.to_date(F.col(name), "dd/MM/yyyy")', self.source)
        self.assertNotIn('F.to_timestamp(F.col(name), "dd/MM/yyyy HH:mm:ss")', self.source)

    def test_no_binary_model_dependency(self):
        lowered = self.source.lower()
        self.assertNotIn(".pbip", lowered)
        self.assertNotIn(".pbix", lowered)
        self.assertNotIn("model.bim", lowered)
        self.assertNotIn("definition.pbism", lowered)


if __name__ == "__main__":
    unittest.main()
