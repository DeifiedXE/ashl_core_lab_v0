import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.runtime.cradle_cases import list_cradle_case_ids
from ashl_core_v1.runtime.cradle_runner import (
    CRADLE_RUN_HISTORY_FILE,
    LAST_CRADLE_RUN_FILE,
    load_last_cradle_run,
    run_all_cradle_cases,
    run_cradle_case,
)


ROOT = Path(__file__).resolve().parents[2]
CLI_MODULE = "ashl_core_v1.runtime.cradle_runner_cli"


class MultiCaseCradleRunnerTests(unittest.TestCase):
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

    def test_list_cases_returns_all_package_6_cases(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_cli(Path(temp_dir), "list-cases")

            self.assertEqual(list(list_cradle_case_ids()), result.stdout.strip().splitlines())

    def test_run_case_works_for_each_case(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            for case_id in list_cradle_case_ids():
                with self.subTest(case_id=case_id):
                    result = run_cradle_case(case_id, data_dir)
                    self.assertEqual(case_id, result["case_id"])
                    self.assertEqual(case_id, result["cycle_summary"]["case_id"])

    def test_run_case_rejects_unknown_case_id_with_readable_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_cli(
                Path(temp_dir),
                "run-case",
                "--case-id",
                "missing_case",
                check=False,
            )

            self.assertEqual(1, result.returncode)
            self.assertIn("not_found case_id=missing_case", result.stdout)

    def test_run_all_cases_runs_all_cases(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_all_cradle_cases(Path(temp_dir))

            self.assertTrue(result["all_cases_completed"])
            self.assertEqual(list(list_cradle_case_ids()), result["case_ids"])

    def test_run_all_cases_case_count_matches_list(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_all_cradle_cases(Path(temp_dir))

            self.assertEqual(len(list_cradle_case_ids()), result["case_count"])
            self.assertEqual(result["case_count"], len(result["case_summaries"]))

    def test_show_last_run_returns_latest_run(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            result = run_all_cradle_cases(data_dir)

            self.assertEqual(result, load_last_cradle_run(data_dir))

    def test_last_cradle_run_json_is_written(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            run_all_cradle_cases(data_dir)

            self.assertTrue((data_dir / LAST_CRADLE_RUN_FILE).is_file())

    def test_cradle_run_history_jsonl_appends_entries(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            run_cradle_case("blocked_front_obstacle", data_dir)
            run_all_cradle_cases(data_dir)

            lines = (data_dir / CRADLE_RUN_HISTORY_FILE).read_text(encoding="utf-8").splitlines()
            self.assertEqual(2, len(lines))

    def test_runner_output_is_repeatable_for_fixed_cases(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            first = run_all_cradle_cases(data_dir)
            second = run_all_cradle_cases(data_dir)

            self.assertEqual(first, second)

    def test_cli_run_all_cases_outputs_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_cli(Path(temp_dir), "run-all-cases")
            payload = json.loads(result.stdout)

            self.assertEqual(len(list_cradle_case_ids()), payload["case_count"])
            self.assertTrue(payload["all_cases_completed"])
            self.assertIn("memory_layer_target", payload["case_summaries"][0])

    def test_cli_show_last_run_returns_latest_run(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.run_cli(data_dir, "run-all-cases")

            result = self.run_cli(data_dir, "show-last-run")
            payload = json.loads(result.stdout)

            self.assertEqual("cradle_all_cases_run_001", payload["run_id"])

    def test_repo_data_directory_is_not_polluted_during_tests(self):
        self.assertFalse((ROOT / "ashl_core_v1" / "data").exists())


if __name__ == "__main__":
    unittest.main()
