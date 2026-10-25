import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "build_cross_stage_summary.py"
SPEC = importlib.util.spec_from_file_location("cross_stage", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class CrossStageSummaryTests(unittest.TestCase):
    def write(self, root: Path, name: str, payload) -> None:
        path = root / "validation" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")

    def write_stage_result(self, root: Path, stage_folder: str, payload) -> None:
        path = root / stage_folder / "automated_validation.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")

    def write_stage_review(self, root: Path, stage_folder: str, payload) -> None:
        path = root / stage_folder / "human_review.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")
        manifest = {"human_review": {"status": "completed", "artifact_path": f"{stage_folder}/human_review.json"}}
        (path.parent / "stage_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    def test_missing_stages_are_incomplete_not_failed(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp) / "test_run"
            self.write(run, "source_acquisition_validation.json", {"error_count": 0, "warning_count": 0})
            summary = MODULE.build_summary(run)
            self.assertEqual(summary["overall_status"], "incomplete")
            self.assertEqual(summary["stages"]["source_acquisition"]["status"], "pass")
            self.assertEqual(summary["totals"]["stages_not_run"], 5)

    def test_errors_fail_and_warnings_do_not(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp) / "test_run"
            self.write(run, "source_acquisition_validation.json", {"warnings": ["short text"]})
            self.write(run, "evidence_extraction_validation.json", {"errors": ["unknown source"]})
            summary = MODULE.build_summary(run)
            self.assertEqual(summary["overall_status"], "fail")
            self.assertEqual(summary["stages"]["source_acquisition"]["status"], "warning")
            self.assertEqual(summary["stages"]["evidence_extraction"]["status"], "fail")

    def test_explicit_false_status_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp) / "test_run"
            self.write(run, "indexing_validation.json", {"passed": False})
            summary = MODULE.build_summary(run)
            self.assertEqual(summary["stages"]["indexing"]["status"], "fail")

    def test_stage_local_result_is_preferred(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp) / "test_run"
            self.write(run, "evidence_extraction_validation.json", {"errors": ["legacy failure"]})
            self.write_stage_result(run, "02_evidence_extraction", {"error_count": 0, "warning_count": 0})
            summary = MODULE.build_summary(run)
            self.assertEqual(summary["stages"]["evidence_extraction"]["status"], "pass")
            self.assertEqual(summary["stages"]["evidence_extraction"]["artifact"], "02_evidence_extraction/automated_validation.json")

    def test_human_json_scores_are_aggregated(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp) / "test_run"
            self.write_stage_result(run, "02_evidence_extraction", {"error_count": 0, "warning_count": 0})
            self.write_stage_review(
                run,
                "02_evidence_extraction",
                {
                    "review_status": "completed",
                    "items": [{"row_type": "review_item", "eu_id": "EU-1", "faithfulness_score": 2, "relevance_score": 1, "value_score": 0}],
                },
            )
            summary = MODULE.build_summary(run)
            metrics = summary["stages"]["evidence_extraction"]["human_review"]["metrics"]
            self.assertEqual(metrics["faithfulness"]["mean_score"], 2)
            self.assertEqual(metrics["relevance"]["mean_score"], 1)
            self.assertEqual(metrics["value"]["mean_score"], 0)


if __name__ == "__main__":
    unittest.main()
