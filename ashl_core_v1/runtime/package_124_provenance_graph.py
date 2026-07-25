"""Provenance graph builder for Package 124 milestone evidence."""

from __future__ import annotations

from typing import Any

from ashl_core_v1.runtime.host_sensor_types import sha256_payload, stable_id, utc_now
from ashl_core_v1.runtime.package_124_types import (
    PACKAGE_124_MILESTONE_ID,
    MilestoneProvenanceEdge,
    MilestoneProvenanceGraphRecord,
    MilestoneProvenanceNode,
)


GRAPH_SCHEMA_VERSION = "ashl_package_124_milestone_provenance_graph_v0"


def build_milestone_provenance_graph(evidence: dict[str, Any]) -> MilestoneProvenanceGraphRecord:
    nodes: list[MilestoneProvenanceNode] = []
    edges: list[MilestoneProvenanceEdge] = []
    node_ids: dict[str, str] = {}

    def add_node(
        kind: str,
        store: str,
        record_id: str | None,
        *,
        content_identity: str | None = None,
        created_at: str | None = None,
        source_trace_refs: tuple[str, ...] = tuple(),
        immutable: bool = True,
    ) -> str:
        if not record_id:
            record_id = f"missing:{kind}:{len(nodes)}"
        key = f"{kind}:{record_id}"
        if key in node_ids:
            return node_ids[key]
        node_id = stable_id(f"package_124_node:{kind}")
        node_ids[key] = node_id
        nodes.append(
            MilestoneProvenanceNode(
                node_id=node_id,
                node_kind=kind,
                source_store=store,
                record_id=str(record_id),
                content_identity=content_identity,
                created_at=created_at,
                immutable=immutable,
                source_trace_refs=source_trace_refs,
            )
        )
        return node_id

    def add_edge(kind: str, source: str | None, target: str | None, method: str, verified: bool = True) -> None:
        if not source or not target:
            verified = False
        edges.append(
            MilestoneProvenanceEdge(
                edge_id=stable_id(f"package_124_edge:{kind}"),
                relation_kind=kind,
                from_node_id=str(source or "missing_source"),
                to_node_id=str(target or "missing_target"),
                verified=verified,
                verification_method=method,
            )
        )

    cycle_one = dict(evidence.get("cycle_1_record") or {})
    cycle_two = dict(evidence.get("cycle_2_record") or {})
    transport = dict(evidence.get("cycle_1_transport_summary") or {})
    teacher = dict(evidence.get("teacher_decision") or {})
    interpretation = dict(evidence.get("reviewed_interpretation_commit") or {})
    readback = dict(evidence.get("working_readback_commit") or {})
    influence = dict(evidence.get("readback_influence") or {})
    comparison = dict(evidence.get("two_cycle_comparison") or {})
    package_123_audit = dict(evidence.get("package_123_growth_audit") or {})
    transport_audit = dict(evidence.get("package_123_transport_audit") or {})

    c1_run = add_node("cycle_1_experiment_run", "package_123_cycle_store", cycle_one.get("experiment_run_id"), created_at=cycle_one.get("created_at"))
    c1_process = add_node("cycle_1_process_instance", "package_123_cycle_store", cycle_one.get("process_instance_id"), created_at=cycle_one.get("created_at"))
    c1_perception_session = add_node("cycle_1_perception_session", "multimodal_session_store", cycle_one.get("perception_session_id"))
    c1_bounded_session = add_node("cycle_1_bounded_session", "teacher_gated_session_store", cycle_one.get("bounded_runtime_session_id"))
    c1_review = add_node("cycle_1_pending_teacher_review", "teacher_gated_session_store", cycle_one.get("pending_teacher_review_id"))
    c1_snapshot = add_node("cycle_1_evidence_snapshot", "teacher_gated_session_store", teacher.get("target_evidence_snapshot_id"), content_identity=teacher.get("target_evidence_identity_sha256"))
    c1_decision = add_node("cycle_1_teacher_decision", "teacher_gated_session_store", teacher.get("teacher_decision_id"), created_at=teacher.get("created_at"))
    c1_interpretation = add_node("cycle_1_reviewed_interpretation_commit", "teacher_gated_session_store", interpretation.get("interpretation_commit_id"), content_identity=interpretation.get("evidence_identity_sha256"), created_at=interpretation.get("created_at"))
    c1_reviewed_concept = add_node("cycle_1_reviewed_concept", "learning_pipeline_identity_bindings", interpretation.get("reviewed_concept_ref"))
    c1_memory_learning = add_node("cycle_1_memory_learning_trace", "learning_pipeline_identity_bindings", interpretation.get("memory_learning_trace_ref"))
    c1_memory_routing = add_node("cycle_1_memory_routing_trace", "learning_pipeline_identity_bindings", interpretation.get("memory_routing_trace_ref"))
    c1_memory_application = add_node("cycle_1_memory_application_data", "learning_pipeline_identity_bindings", interpretation.get("memory_application_data_ref"))
    c1_readback = add_node("cycle_1_working_readback", "teacher_gated_session_store", readback.get("working_readback_commit_id"), content_identity=readback.get("evidence_identity_sha256"), created_at=readback.get("created_at"))
    transport_node = add_node("package_123_transport_integrity_summary", "package_123_cycle_store", transport.get("integrity_summary_id"))

    c2_run = add_node("cycle_2_experiment_run", "package_123_cycle_store", cycle_two.get("experiment_run_id"), created_at=cycle_two.get("created_at"))
    c2_process = add_node("cycle_2_process_instance", "package_123_cycle_store", cycle_two.get("process_instance_id"), created_at=cycle_two.get("created_at"))
    c2_perception_session = add_node("cycle_2_perception_session", "multimodal_session_store", cycle_two.get("perception_session_id"))
    c2_bounded_session = add_node("cycle_2_bounded_session", "package_123_cycle_store", cycle_two.get("bounded_runtime_session_id"))
    c2_readback_timing = add_node("cycle_2_readback_load_timing", "package_123_cycle_store", evidence.get("readback_timing_id"))
    c2_candidate = add_node("cycle_2_package_112_candidate", "host_body_internal_action", influence.get("cycle_2_candidate_id"))
    c2_influence = add_node("cycle_2_package_112_scoring_contribution", "package_123_cycle_store", influence.get("influence_record_id"))
    c2_review = add_node("cycle_2_pending_teacher_review", "package_123_cycle_store", cycle_two.get("pending_teacher_review_id"))
    comparison_node = add_node("package_123_two_cycle_comparison", "package_123_cycle_store", comparison.get("comparison_id"))
    final_audit_node = add_node("package_123_growth_audit", "package_123_cycle_store", package_123_audit.get("audit_id"))
    transport_audit_node = add_node("package_123_transport_repair_audit", "package_123_cycle_store", transport_audit.get("audit_id"))

    for artifact_id in tuple(cycle_one.get("screen_artifact_refs") or ()):
        artifact_node = add_node("cycle_1_raw_screen_artifact", "sensor_artifact_store", artifact_id, content_identity=(evidence.get("artifact_hashes") or {}).get(artifact_id))
        add_edge("derived_from", c1_run, artifact_node, "cycle_1_artifact_ref")
        add_edge("compiled_from", artifact_node, c1_perception_session, "source_primitive_link")
    for artifact_id in tuple(cycle_one.get("audio_artifact_refs") or ()):
        artifact_node = add_node("cycle_1_raw_loopback_audio_artifact", "sensor_artifact_store", artifact_id, content_identity=(evidence.get("artifact_hashes") or {}).get(artifact_id))
        add_edge("derived_from", c1_run, artifact_node, "cycle_1_artifact_ref")
        add_edge("compiled_from", artifact_node, c1_perception_session, "source_primitive_link")
    for artifact_id in tuple(cycle_one.get("host_state_artifact_refs") or ()):
        artifact_node = add_node("cycle_1_host_state_artifact", "sensor_artifact_store", artifact_id, content_identity=(evidence.get("artifact_hashes") or {}).get(artifact_id))
        add_edge("derived_from", c1_run, artifact_node, "cycle_1_artifact_ref")
        add_edge("compiled_from", artifact_node, c1_perception_session, "source_primitive_link")
    for primitive_id in tuple(evidence.get("cycle_1_primitive_ids") or ()):
        primitive_node = add_node("cycle_1_perception_primitive", "perception_primitive_store", primitive_id)
        add_edge("compiled_from", c1_perception_session, primitive_node, "perception_lane_item")
    for readable_id in tuple(cycle_one.get("perception_readable_data_refs") or ()):
        readable_node = add_node("cycle_1_perception_readable_data", "perception_primitive_store", readable_id)
        add_edge("aligned_into", c1_perception_session, readable_node, "perception_readable_data_ref")

    for artifact_id in tuple(cycle_two.get("screen_artifact_refs") or ()) + tuple(cycle_two.get("audio_artifact_refs") or ()) + tuple(cycle_two.get("host_state_artifact_refs") or ()):
        artifact_node = add_node("cycle_2_raw_artifact", "sensor_artifact_store", artifact_id, content_identity=(evidence.get("artifact_hashes") or {}).get(artifact_id))
        add_edge("derived_from", c2_run, artifact_node, "cycle_2_artifact_ref")
        add_edge("compiled_from", artifact_node, c2_perception_session, "source_primitive_link")
    for primitive_id in tuple(evidence.get("cycle_2_primitive_ids") or ()):
        primitive_node = add_node("cycle_2_perception_primitive", "perception_primitive_store", primitive_id)
        add_edge("compiled_from", c2_perception_session, primitive_node, "perception_lane_item")

    add_edge("derived_from", c1_process, c1_run, "cycle_record_process_instance")
    add_edge("aligned_into", c1_perception_session, c1_bounded_session, "perception_host_body_event_bridge")
    add_edge("stopped_at", c1_bounded_session, c1_review, "pending_teacher_review_id")
    add_edge("review_target_of", c1_snapshot, c1_review, "teacher_decision_target_binding")
    add_edge("approved_by", c1_review, c1_decision, "teacher_decision_exact_target")
    add_edge("committed_as", c1_decision, c1_interpretation, "reviewed_interpretation_commit")
    add_edge("committed_as", c1_interpretation, c1_reviewed_concept, "reviewed_concept_ref")
    add_edge("routed_as", c1_reviewed_concept, c1_memory_learning, "learning_pipeline_identity_binding")
    add_edge("routed_as", c1_memory_learning, c1_memory_routing, "learning_pipeline_identity_binding")
    add_edge("applied_as", c1_memory_routing, c1_memory_application, "learning_pipeline_identity_binding")
    add_edge("committed_as", c1_memory_application, c1_readback, "working_readback_commit")
    add_edge("audited_by", c1_bounded_session, transport_node, "transport_integrity_summary")

    add_edge("derived_from", c2_process, c2_run, "cycle_record_process_instance")
    add_edge("loaded_by", c1_readback, c2_readback_timing, "readback_load_timing_record")
    add_edge("loaded_by", c2_readback_timing, c2_bounded_session, "readback_loaded_before_event")
    add_edge("aligned_into", c2_perception_session, c2_bounded_session, "perception_host_body_event_bridge")
    add_edge("influenced", c1_readback, c2_influence, "readback_influence_record")
    add_edge("influenced", c2_influence, c2_candidate, "candidate_score_component")
    add_edge("stopped_at", c2_bounded_session, c2_review, "cycle_2_pending_review")
    add_edge("audited_by", c2_influence, comparison_node, "two_cycle_comparison")
    add_edge("audited_by", comparison_node, final_audit_node, "package_123_growth_audit")
    add_edge("audited_by", transport_node, transport_audit_node, "package_123_transport_repair_audit")

    required_edges_verified = all(edge.verified for edge in edges)
    graph_payload = {
        "milestone_id": PACKAGE_124_MILESTONE_ID,
        "nodes": [node.to_dict() for node in nodes],
        "edges": [edge.to_dict() for edge in edges],
        "required_edges_verified": required_edges_verified,
    }
    graph_hash = sha256_payload(graph_payload)
    return MilestoneProvenanceGraphRecord(
        graph_id=stable_id("package_124_provenance_graph"),
        schema_version=GRAPH_SCHEMA_VERSION,
        created_at=utc_now(),
        milestone_id=PACKAGE_124_MILESTONE_ID,
        nodes=tuple(nodes),
        edges=tuple(edges),
        required_edges_verified=required_edges_verified,
        graph_sha256=graph_hash,
    )
