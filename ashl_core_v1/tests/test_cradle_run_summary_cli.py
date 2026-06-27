import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.runtime.cradle_cases import list_cradle_case_ids
from ashl_core_v1.runtime.cradle_runner import run_all_cradle_cases
from ashl_core_v1.runtime.cradle_summary import (
    summarize_all_cradle_cases,
    summarize_cradle_case,
    summarize_last_run,
)


ROOT = Path(__file__).resolve().parents[2]
CLI_MODULE = "ashl_core_v1.runtime.cradle_summary_cli"


class CradleRunSummaryCliTests(unittest.TestCase):
    def run_cli(
        self,
        data_dir: Path,
        *args: str,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", CLI_MODULE, "--data-dir", str(data_dir), *args],
            cwd=ROOT,
            check=check,
            capture_output=True,
            text=True,
        )

    def test_summarize_case_works_for_every_case(self):
        for case_id in list_cradle_case_ids():
            with self.subTest(case_id=case_id):
                summary = summarize_cradle_case(case_id)
                self.assertEqual(case_id, summary["case_id"])
                self.assertTrue(summary["human_readable_summary"])

    def test_summarize_all_cases_includes_all_cases(self):
        summary = summarize_all_cradle_cases()

        self.assertEqual(len(list_cradle_case_ids()), summary["case_count"])
        self.assertEqual(set(list_cradle_case_ids()), {item["case_id"] for item in summary["case_summaries"]})

    def test_approved_count_is_correct(self):
        self.assertEqual(4, summarize_all_cradle_cases()["approved_count"])

    def test_blocked_by_review_count_is_correct(self):
        self.assertEqual(4, summarize_all_cradle_cases()["blocked_by_review_count"])

    def test_routed_count_is_correct(self):
        self.assertEqual(2, summarize_all_cradle_cases()["routed_count"])

    def test_influence_visible_count_is_correct(self):
        self.assertEqual(2, summarize_all_cradle_cases()["influence_visible_count"])

    def test_summarize_last_run_works_after_run_all_cases(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            run_all_cradle_cases(data_dir)

            summary = summarize_last_run(data_dir)

            self.assertIsNotNone(summary)
            self.assertEqual("cradle_all_cases_run_001", summary["source_run_id"])
            self.assertEqual(len(list_cradle_case_ids()), summary["case_count"])

    def test_human_readable_summary_is_non_empty(self):
        for item in summarize_all_cradle_cases()["case_summaries"]:
            with self.subTest(case_id=item["case_id"]):
                self.assertTrue(item["human_readable_summary"])

    def test_missing_case_id_returns_readable_not_found_result(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_cli(
                Path(temp_dir),
                "summarize-case",
                "--case-id",
                "missing_case",
                check=False,
            )

            self.assertEqual(1, result.returncode)
            self.assertIn("not_found case_id=missing_case", result.stdout)

    def test_cli_summarize_all_cases_outputs_counts(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_cli(Path(temp_dir), "summarize-all-cases")
            summary = json.loads(result.stdout)

            self.assertEqual(8, summary["case_count"])
            self.assertEqual(4, summary["approved_count"])
            self.assertEqual(2, summary["routed_count"])

    def test_cli_summarize_last_run_after_run_all_cases(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            run_all_cradle_cases(data_dir)

            result = self.run_cli(data_dir, "summarize-last-run")
            summary = json.loads(result.stdout)

            self.assertEqual("cradle_all_cases_run_001", summary["source_run_id"])
            self.assertEqual(8, summary["case_count"])
            self.assertEqual("working", summary["case_summaries"][0]["memory_layer_target"])


if __name__ == "__main__":
    unittest.main()
