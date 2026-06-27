import copy
import unittest

from ashl_core_v1.runtime.cradle_cases import build_cradle_case_sample, list_cradle_case_ids
from ashl_core_v1.runtime.review_routing_matrix import (
    check_all_cradle_cases_against_matrix,
    check_cradle_case_against_matrix,
    get_review_routing_expectation_matrix,
)


class ReviewRoutingExpectationMatrixTests(unittest.TestCase):
    def test_matrix_contains_all_cradle_cases(self):
        matrix = get_review_routing_expectation_matrix()

        self.assertEqual(set(list_cradle_case_ids()), set(matrix))

    def test_each_case_passes_matrix_check(self):
        for case_id in list_cradle_case_ids():
            with self.subTest(case_id=case_id):
                result = check_cradle_case_against_matrix(case_id, build_cradle_case_sample(case_id))
                self.assertTrue(result["passed"])
                self.assertEqual({}, result["mismatches"])

    def test_wrong_review_status_fails(self):
        sample = copy.deepcopy(build_cradle_case_sample("blocked_front_obstacle"))
        sample["cycle_summary"]["review_status"] = "rejected"

        result = check_cradle_case_against_matrix("blocked_front_obstacle", sample)

        self.assertFalse(result["passed"])
        self.assertIn("review_status", result["mismatches"])

    def test_wrong_routing_status_fails(self):
        sample = copy.deepcopy(build_cradle_case_sample("blocked_front_obstacle"))
        sample["cycle_summary"]["routing_status"] = "deferred"

        result = check_cradle_case_against_matrix("blocked_front_obstacle", sample)

        self.assertFalse(result["passed"])
        self.assertIn("routing_status", result["mismatches"])

    def test_wrong_memory_entry_allowed_fails(self):
        sample = copy.deepcopy(build_cradle_case_sample("teacher_rejected"))
        sample["cycle_summary"]["memory_entry_allowed"] = True

        result = check_cradle_case_against_matrix("teacher_rejected", sample)

        self.assertFalse(result["passed"])
        self.assertIn("memory_entry_allowed", result["mismatches"])

    def test_stale_and_superseded_approve_but_do_not_route_to_active_memory_layer(self):
        for case_id in ("stale_learning", "superseded_learning"):
            result = check_cradle_case_against_matrix(case_id, build_cradle_case_sample(case_id))
            actual = result["actual"]
            with self.subTest(case_id=case_id):
                self.assertEqual("approved", actual["review_status"])
                self.assertTrue(actual["memory_entry_allowed"])
                self.assertEqual("none", actual["memory_layer_target"])

    def test_unknown_rejected_deferred_conflict_never_allow_memory_entry(self):
        for case_id in (
            "unknown_feedback",
            "teacher_rejected",
            "teacher_deferred",
            "conflict_detected",
        ):
            actual = check_cradle_case_against_matrix(case_id, build_cradle_case_sample(case_id))["actual"]
            with self.subTest(case_id=case_id):
                self.assertFalse(actual["memory_entry_allowed"])

    def test_check_all_cradle_cases_against_matrix_returns_all_passed_true(self):
        result = check_all_cradle_cases_against_matrix()

        self.assertEqual(len(list_cradle_case_ids()), result["case_count"])
        self.assertEqual(result["case_count"], result["passed_count"])
        self.assertEqual(0, result["failed_count"])
        self.assertTrue(result["all_passed"])


if __name__ == "__main__":
    unittest.main()
