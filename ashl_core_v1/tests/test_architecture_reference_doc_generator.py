import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.tools.architecture_reference_doc_generator import REFERENCE_DOC_NAMES, generate_reference_docs


class ArchitectureReferenceDocGeneratorTests(unittest.TestCase):
    def test_reference_doc_generator_writes_deterministic_docs_from_records(self):
        scan = {
            "scan_sha256": "abc",
            "baseline": {"scan_id": "scan:123", "scanned_commit": None},
            "modules": [],
            "interfaces": [
                {
                    "connection_id": "perception_to_host_body",
                    "source_module": "a",
                    "target_module": "b",
                    "connection_kind": "session_injection",
                    "actual_import_exists": True,
                    "actual_runtime_call_exists": True,
                    "integration_test_exists": True,
                    "connection_status": "verified_runtime_connection",
                    "risk_codes": [],
                }
            ],
            "roadmap": {
                "roadmap_conflicts": [
                    {
                        "conflict_id": "package_125_129_active_perception_audio_collision",
                        "conflict_kind": "package_number_collision",
                        "conflicting_package_ids": ("125",),
                        "resolution_status": "resolved",
                        "chosen_resolution": "Use unique ids.",
                        "superseded_route_refs": ("old",),
                    }
                ],
                "package_number_registry": {"registry_valid": True},
                "revised_route": [
                    {
                        "package_id": "123",
                        "package_name": "No-Codex Real Perception Two-Cycle Growth Run",
                        "path_classification": "critical_path",
                        "milestone_dependency": "Package 124",
                        "route_note": "Proceed when live data exists.",
                    }
                ],
            },
            "analysis": {
                "current_module_map": [],
                "ideal_organs": [],
                "capability_gaps": [],
                "bottlenecks": [],
                "duplicates_or_orphans": [],
                "audit": {"audit_status": "passed_architecture_module_and_roadmap_gap_reconciliation"},
                "package_123_go_no_go": {"package_123_go": True},
            },
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            docs = generate_reference_docs(scan, temp_dir)
            names = {path.name for path in docs}
            self.assertEqual(names, set(REFERENCE_DOC_NAMES))
            route_doc = Path(temp_dir) / "package_123_to_daily_runtime_revised_route_v0.md"
            self.assertIn("scan:123", route_doc.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
