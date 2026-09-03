import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SDK_NOTEBOOK = ROOT / "NB_Run_SDK_Evaluation.ipynb"
REVIEW_NOTEBOOK = ROOT / "NB_Review_And_Score_Data_Agent.ipynb"


class SdkEvaluationNotebookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.notebook = json.loads(SDK_NOTEBOOK.read_text(encoding="utf-8"))
        cls.code = [
            "".join(cell["source"])
            for cell in cls.notebook["cells"]
            if cell["cell_type"] == "code"
        ]
        cls.markdown = "\n".join(
            "".join(cell["source"])
            for cell in cls.notebook["cells"]
            if cell["cell_type"] == "markdown"
        )
        cls.source = "\n".join(cls.code)

    def test_notebook_structure_and_compilation(self):
        self.assertEqual(4, self.notebook["nbformat"])
        self.assertEqual(12, len(self.notebook["cells"]))
        self.assertEqual(6, len(self.code))
        identifiers = [cell["id"] for cell in self.notebook["cells"]]
        self.assertEqual(len(identifiers), len(set(identifiers)))
        for number, cell in enumerate(self.notebook["cells"], start=1):
            expected_language = "python" if cell["cell_type"] == "code" else "markdown"
            self.assertEqual(expected_language, cell["metadata"]["language"])
            if cell["cell_type"] == "code":
                compile("".join(cell["source"]), f"cell-{number}", "exec")

    def test_single_notebook_participant_workflow(self):
        self.assertFalse(REVIEW_NOTEBOOK.exists())
        self.assertIn("participant evaluation notebook", self.markdown)
        self.assertIn("Change only `SNAPSHOT_NAME`", self.markdown)
        self.assertIn("16 prompts", self.markdown)
        self.assertIn('SNAPSHOT_NAME = "step1_baseline"', self.source)
        for snapshot in (
            "step1_baseline",
            "step2_prep_ai",
            "step3_lakehouse_added",
            "step4_lakehouse_tuned",
            "step5_final",
            "step5_routing",
        ):
            self.assertIn(f'"{snapshot}"', self.source)
        self.assertIn('DATASET_NAME = SNAPSHOT_PLAN[SNAPSHOT_NAME]', self.source)
        self.assertIn('"step3_lakehouse_added": "lakehouse-tuning"', self.source)
        self.assertIn('"step4_lakehouse_tuned": "lakehouse-tuning"', self.source)
        self.assertIn('INCLUDE_PARAPHRASES = DATASET_NAME != "routing"', self.source)
        self.assertIn('if dataset_name != "routing":', self.source)

    def test_sdk_contract_and_complete_expected_answers(self):
        self.assertIn("fabric-data-agent-sdk==0.1.30a0", self.code[0])
        self.assertIn('import_module("fabric.dataagent.evaluation")', self.code[1])
        self.assertIn('import_module("fabric.dataagent.evaluation._storage")', self.code[1])
        self.assertIn('item.get("sdk_expected_answer", item["ground_truth_answer"])', self.code[2])
        self.assertIn('"expected_answer": [item["sdk_expected_answer"]', self.code[3])
        self.assertIn("fabric_evaluation.evaluate_data_agent", self.code[3])
        self.assertIn("fabric_evaluation.get_evaluation_details", self.code[3])

    def test_query_evidence_and_comparison_contract(self):
        evidence_code = self.code[4]
        comparison_code = self.code[5]
        self.assertIn('evaluation_storage._get_data(f"{TABLE_NAME}_steps")', evidence_code)
        self.assertIn('details.merge(steps[STEP_COLUMNS], on="id", how="left")', evidence_code)
        for column in (
            '"sql_steps"',
            '"dax_steps"',
            '"kql_steps"',
            '"query_type"',
            '"generated_query"',
            '"source_trace"',
        ):
            self.assertIn(column, evidence_code)
        self.assertIn("SNAPSHOT_PLAN.items()", comparison_code)
        self.assertIn("latest_evaluation_rows", comparison_code)
        self.assertIn("snapshot_summary_df", comparison_code)
        self.assertIn("judgement_matrix_df", comparison_code)
        self.assertIn("comparison_evidence_df[EVIDENCE_COLUMNS]", comparison_code)


if __name__ == "__main__":
    unittest.main()
