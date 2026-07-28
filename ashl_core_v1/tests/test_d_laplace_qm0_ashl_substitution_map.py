from __future__ import annotations

import unittest

from ashl_core_v1.migration_audit.d_laplace_ashl_substitution_map import (
    build_ashl_substitution_map,
)


class DLaplaceQM0ASHLSubstitutionMapTests(unittest.TestCase):
    def setUp(self) -> None:
        self.records = build_ashl_substitution_map(())

    def test_resource_budgeting_is_full_future_candidate(self) -> None:
        record = next(
            item
            for item in self.records
            if item.ashl_module_or_future_role == "fixed_resource_budget_accounting"
        )
        self.assertEqual(record.substitution_status, "full_substitution_candidate")
        self.assertEqual(record.earliest_allowed_stage, "DLM-1-after-Package-132")

    def test_thought_routing_is_partial_only(self) -> None:
        record = next(
            item
            for item in self.records
            if item.ashl_module_or_future_role == "fixed_Thought_layer_router"
        )
        self.assertEqual(record.substitution_status, "partial_substitution_candidate")
        self.assertIn("hypothesis_generation", record.preserved_ashl_responsibilities)

    def test_self_audit_framework_is_supporting_only(self) -> None:
        record = next(
            item
            for item in self.records
            if item.ashl_module_or_future_role
            == "general_research_trust_audit_support"
        )
        self.assertEqual(record.substitution_status, "supporting_mechanism_only")
        self.assertIn(
            "Package_125_capture_session_identity_audit",
            record.preserved_ashl_responsibilities,
        )

    def test_sensor_memory_history_teacher_and_output_are_never_substituted(self) -> None:
        never = {
            item.ashl_module_or_future_role
            for item in self.records
            if item.substitution_status == "never_substitute"
        }
        for role in (
            "Package_120_sensor_ingress",
            "raw_append_only_history",
            "teacher_review",
            "memory_admission",
            "Core_Memory",
            "Package_125_capture_session_identity_audit",
            "output_provenance",
        ):
            self.assertIn(role, never)

    def test_package_124_temporal_and_archive_foundations_remain_authoritative(self) -> None:
        never = {
            item.ashl_module_or_future_role
            for item in self.records
            if item.substitution_status == "never_substitute"
        }
        self.assertIn("Package_124_archive", never)
        self.assertIn("Package_124A_temporal_foundation", never)


if __name__ == "__main__":
    unittest.main()
