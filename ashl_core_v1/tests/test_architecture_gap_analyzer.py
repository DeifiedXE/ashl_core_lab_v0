import unittest
from types import SimpleNamespace
from pathlib import Path

from ashl_core_v1.tools.architecture_gap_analyzer import analyze_architecture_gaps
from ashl_core_v1.tools.architecture_repo_scanner import scan_repo_baseline


class ArchitectureGapAnalyzerTests(unittest.TestCase):
    def test_gap_analyzer_reports_mandatory_bottlenecks_and_go_no_go_false_when_runtime_missing(self):
        root = Path(__file__).resolve().parents[2]
        baseline = scan_repo_baseline(root)
        interfaces = (
            SimpleNamespace(connection_id="perception_to_host_body", connection_status="verified_runtime_connection"),
            SimpleNamespace(connection_id="learning_evidence_to_teacher_gate", connection_status="verified_runtime_connection"),
        )
        modules = (
            SimpleNamespace(module_path="ashl_core_v1.runtime.bounded_multimodal_perception_session_runtime", downstream_consumers=(), implementation_status="actual_runtime"),
            SimpleNamespace(module_path="ashl_core_v1.runtime.no_codex_two_cycle_fixture_growth_run", downstream_consumers=(), implementation_status="actual_runtime"),
        )
        roadmap = {
            "roadmap_conflicts": [{"resolution_status": "resolved"}],
            "revised_route": [{"package_id": "123"}],
        }
        analysis = analyze_architecture_gaps(
            repo_root=root,
            baseline=baseline,
            module_records=modules,
            interface_records=interfaces,
            store_records=(SimpleNamespace(),),
            surface_records=(SimpleNamespace(),),
            test_records=(SimpleNamespace(),),
            roadmap_records=roadmap,
        )

        bottleneck_names = {record["interface_name"] for record in analysis["bottlenecks"]}
        self.assertIn("PerceptionReadableData -> HostBodyEvent", bottleneck_names)
        self.assertFalse(analysis["package_123_go_no_go"]["package_123_go"])
        self.assertIn("Thought Engine is design/schema only", {record["gap_name"] for record in analysis["capability_gaps"]})


if __name__ == "__main__":
    unittest.main()
