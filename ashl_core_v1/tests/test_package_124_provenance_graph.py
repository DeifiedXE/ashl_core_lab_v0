import unittest

from ashl_core_v1.runtime.package_124_provenance_graph import build_milestone_provenance_graph


class Package124ProvenanceGraphTests(unittest.TestCase):
    def test_graph_contains_verified_required_edges(self):
        evidence = {
            "cycle_1_record": {
                "experiment_run_id": "run1",
                "process_instance_id": "proc1",
                "perception_session_id": "p1",
                "bounded_runtime_session_id": "s1",
                "pending_teacher_review_id": "review1",
                "screen_artifact_refs": ("screen1",),
                "audio_artifact_refs": ("audio1",),
                "host_state_artifact_refs": ("host1",),
                "perception_readable_data_refs": ("prd1",),
            },
            "cycle_2_record": {
                "experiment_run_id": "run2",
                "process_instance_id": "proc2",
                "perception_session_id": "p2",
                "bounded_runtime_session_id": "s2",
                "pending_teacher_review_id": "review2",
                "screen_artifact_refs": ("screen2",),
                "audio_artifact_refs": ("audio2",),
                "host_state_artifact_refs": ("host2",),
            },
            "cycle_1_transport_summary": {"integrity_summary_id": "transport"},
            "teacher_decision": {
                "teacher_decision_id": "decision",
                "target_evidence_snapshot_id": "snapshot",
                "target_evidence_identity_sha256": "hash",
            },
            "reviewed_interpretation_commit": {
                "interpretation_commit_id": "interpretation",
                "reviewed_concept_ref": "concept",
                "memory_learning_trace_ref": "learning",
                "memory_routing_trace_ref": "routing",
                "memory_application_data_ref": "application",
                "evidence_identity_sha256": "hash",
            },
            "working_readback_commit": {
                "working_readback_commit_id": "readback",
                "evidence_identity_sha256": "hash",
            },
            "readback_influence": {
                "influence_record_id": "influence",
                "cycle_2_candidate_id": "candidate",
            },
            "two_cycle_comparison": {"comparison_id": "comparison"},
            "package_123_growth_audit": {"audit_id": "growth-audit"},
            "package_123_transport_audit": {"audit_id": "transport-audit"},
            "readback_timing_id": "timing",
            "cycle_1_primitive_ids": ("primitive1",),
            "cycle_2_primitive_ids": ("primitive2",),
        }
        graph = build_milestone_provenance_graph(evidence)
        self.assertTrue(graph.required_edges_verified)
        self.assertGreaterEqual(len(graph.nodes), 20)
        self.assertGreaterEqual(len(graph.edges), 20)


if __name__ == "__main__":
    unittest.main()
