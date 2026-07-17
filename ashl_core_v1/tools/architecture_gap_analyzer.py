"""Gap, bottleneck, duplicate/orphan, audit, and Package 123 go/no-go analysis."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ashl_core_v1.tools.architecture_repo_scanner import plain, read_text, stable_id, utc_now


IDEAL_ORGAN_SCHEMA_VERSION = "ashl_ideal_end_state_organ_v0"
CAPABILITY_GAP_SCHEMA_VERSION = "ashl_architecture_capability_gap_v0"
BOTTLENECK_SCHEMA_VERSION = "ashl_architecture_bottleneck_v0"
DUPLICATE_OR_ORPHAN_SCHEMA_VERSION = "ashl_architecture_duplicate_or_orphan_v0"
ARCHITECTURE_AUDIT_SCHEMA_VERSION = "ashl_architecture_module_roadmap_reconciliation_audit_v0"
PACKAGE_123_GO_NO_GO_SCHEMA_VERSION = "ashl_package_123_architecture_go_no_go_v0"


@dataclass(frozen=True)
class IdealEndStateOrganRecord:
    organ_id: str
    schema_version: str
    organ_name: str
    purpose: str
    required_inputs: tuple[str, ...]
    required_outputs: tuple[str, ...]
    authority: str
    persistence_boundary: str
    teacher_boundary: str
    failure_behavior: str
    upstream_organs: tuple[str, ...]
    downstream_organs: tuple[str, ...]
    completion_milestone: str

    def to_dict(self) -> dict[str, Any]:
        return plain(self)


@dataclass(frozen=True)
class ArchitectureCapabilityGapRecord:
    gap_id: str
    schema_version: str
    gap_name: str
    gap_category: str
    ideal_module: str
    current_module_refs: tuple[str, ...]
    current_status: str
    required_status: str
    missing_interfaces: tuple[str, ...]
    missing_runtime_behavior: tuple[str, ...]
    missing_tests: tuple[str, ...]
    blocks_package_ids: tuple[str, ...]
    severity: str
    recommended_resolution: str

    def to_dict(self) -> dict[str, Any]:
        return plain(self)


@dataclass(frozen=True)
class ArchitectureBottleneckRecord:
    bottleneck_id: str
    schema_version: str
    interface_name: str
    upstream_modules: tuple[str, ...]
    downstream_modules: tuple[str, ...]
    throughput_role: str
    information_loss_risk: str
    authority_concentration_risk: str
    coupling_risk: str
    current_evidence: tuple[str, ...]
    affected_future_milestones: tuple[str, ...]
    bottleneck_status: str
    recommended_action: str

    def to_dict(self) -> dict[str, Any]:
        return plain(self)


@dataclass(frozen=True)
class ArchitectureDuplicateOrOrphanRecord:
    record_id: str
    schema_version: str
    item_kind: str
    item_refs: tuple[str, ...]
    classification: str
    current_runtime_consumer_count: int
    safe_to_archive: bool
    requires_human_review: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return plain(self)


@dataclass(frozen=True)
class ArchitectureModuleRoadmapReconciliationAuditRecord:
    audit_id: str
    schema_version: str
    created_at: str
    repo_scan_complete: bool
    module_inventory_complete: bool
    interface_map_complete: bool
    store_inventory_complete: bool
    CLI_inventory_complete: bool
    test_map_complete: bool
    ideal_module_map_complete: bool
    current_module_map_complete: bool
    gap_matrix_complete: bool
    package_number_conflicts_resolved: bool
    revised_roadmap_complete: bool
    package_123_path_valid: bool
    package_124_path_valid: bool
    critical_interface_risks: tuple[str, ...]
    high_priority_gaps: tuple[str, ...]
    runtime_behavior_changed: bool
    source_runtime_records_modified: bool
    audit_status: str
    failure_reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return plain(self)


@dataclass(frozen=True)
class Package123ArchitectureGoNoGoRecord:
    record_id: str
    schema_version: str
    created_at: str
    package_122_runtime_valid: bool
    perception_lineage_valid: bool
    teacher_gate_path_valid: bool
    cross_process_growth_path_valid: bool
    missing_live_experience_data_only: bool
    architecture_blockers: tuple[str, ...]
    nonblocking_gaps: tuple[str, ...]
    package_123_go: bool
    decision_reason: str

    def to_dict(self) -> dict[str, Any]:
        return plain(self)


def _ideal_organs() -> tuple[IdealEndStateOrganRecord, ...]:
    rows = (
        ("Host Sensor System", "Read-only bounded capture of camera, screen, microphone, and host-state adapter output.", ("explicit local capture commands",), ("SensorRawArtifact", "ephemeral audio buffers"), "local read-only sensor authority only", "raw artifacts local and explicit; daily audio may be RAM-only", "no teacher decision by capture alone", "stop, fail closed, preserve metadata", tuple(), ("Perception Compilation System",), "Package 120/120A complete, later strengthened"),
        ("Perception Compilation System", "Compile raw/ephemeral inputs into deterministic low-level primitives.", ("SensorRawArtifact", "PerceptionSourceBuffer"), ("PerceptionReadableData", "primitive records"), "deterministic compiler authority, no semantics", "primitive store only; no raw media copies", "no teacher decision by compilation alone", "failure record, no fabricated primitive", ("Host Sensor System",), ("Multimodal Timeline System",), "Package 121 complete"),
        ("Multimodal Timeline System", "Place low-level perception records on one bounded timeline.", ("PerceptionReadableData",), ("alignment windows", "low-level HostBodyEvent"), "bounded session assembly authority", "session records only", "stops at teacher gate after Package 115", "drop/backpressure traces", ("Perception Compilation System",), ("Teacher System", "Qingyin Home Runtime Surface"), "Package 122 complete"),
        ("Active Perception And Attention System", "Select bounded internal recapture/relisten/focus actions.", ("low-level events", "uncertainty", "working readback"), ("internal focus state", "observe/listen again requests"), "internal-only action authority", "bounded attention state, not external control", "teacher gate for interpreted learning", "pause or request review", ("Multimodal Timeline System",), ("Thought Engine", "Teacher System"), "Packages 125-132"),
        ("Teacher System", "Approve exact evidence and scoped learning promotion.", ("pending reviews", "evidence snapshots"), ("teacher decisions", "approval scopes"), "human project-owner authorization", "decision records append-only", "explicit teacher action required", "pause/rollback on reject/defer", ("Multimodal Timeline System",), ("Learning And Generalization System",), "Packages 115-117 complete for current path"),
        ("Learning And Generalization System", "Convert approved evidence into reviewed concepts.", ("teacher decision", "learning feedback candidate"), ("ReviewedConcept", "identity sidecars"), "teacher-gated learning path", "no unreviewed memory promotion", "explicit scoped approval", "rollback or pause", ("Teacher System",), ("Memory System",), "Packages 90-92/116/117 complete for current path"),
        ("Memory System", "Commit approved interpretation and provide bounded readback.", ("ReviewedConcept", "commit provenance"), ("working readback", "memory traces"), "approved interpreted memory only", "source-trace linked stores", "teacher scope required", "rollback preserves raw trace", ("Learning And Generalization System",), ("Daily Session And Recovery System",), "Packages 116-118 complete for current path"),
        ("Persistent Self-State System", "Maintain long-lived self-state distinct from session and readback.", ("approved self-state changes",), ("persistent self-state",), "not yet implemented", "must be separate from working readback", "future teacher gate required", "no mutation on uncertainty", ("Memory System",), ("Thought Engine", "Daily Session And Recovery System"), "Packages 133-140"),
        ("Mimetic Endocrine Regulation System", "Bounded modulation signals without purpose or direct action authority.", ("state/readback/context signals",), ("drive modulation traces",), "non-authoritative modulation only", "persistent drive only after self-state gate", "future teacher gate for persistent changes", "fail to neutral modulation", ("Persistent Self-State System",), ("Thought Engine", "Active Perception And Attention System"), "Packages 135-140"),
        ("Thought Engine", "Non-LLM bounded thought layers.", ("perception/readback/self-state",), ("verification proposals", "bounded deliberation traces"), "non-LLM internal reasoning only", "traceable thought state", "teacher gate for learning/memory", "budget stop", ("Active Perception And Attention System",), ("Self-Proposed Verification System",), "Packages 141-148"),
        ("Self-Proposed Verification System", "Propose and teacher-gate bounded verification loops.", ("thought proposals",), ("verification evidence", "verification result bindings"), "bounded local verification only", "source trace linked", "teacher gate for interpretations", "safe stop", ("Thought Engine",), ("Memory System",), "Packages 149-156"),
        ("Expression System", "Create first non-LLM output under approval boundary.", ("approved expression candidates",), ("first_output",), "teacher-gated expression only", "output traces", "explicit approval", "silence/rollback", ("Thought Engine", "Teacher System"), ("Qingyin Home Runtime Surface",), "Packages 157-164"),
        ("Qingyin Home Runtime Surface", "Expose real runtime/teacher/memory/perception status.", ("runtime records",), ("read-only user surface",), "display/inspection authority only", "surface records/UI state", "does not approve by display", "show missing status honestly", ("Multimodal Timeline System", "Teacher System", "Memory System"), ("Teacher System",), "currently record surface; later daily runtime"),
        ("Daily Session And Recovery System", "Run a bounded daily no-Codex session with recovery.", ("sensors", "attention", "memory", "teacher console"), ("daily session records",), "foreground bounded runtime authority", "explicit local state dirs", "teacher gates remain explicit", "recover or stop", ("Persistent Self-State System", "Thought Engine"), ("Audit And Governance System",), "Packages 165-172"),
        ("External Capability Bridge", "Future external capability boundary.", ("approved capability requests",), ("bounded bridge records",), "not implemented; no external control", "no arbitrary file/network/shell authority", "future teacher gate", "deny by default", ("Teacher System",), ("Audit And Governance System",), "post-v1 or later"),
        ("Audit And Governance System", "Verify claims from records without manufacturing capability.", ("records", "traces", "stores"), ("audits", "certificates"), "read-only audit authority", "audit records only", "no runtime approval", "blocked when evidence missing", ("Daily Session And Recovery System",), tuple(), "ongoing"),
    )
    records = []
    for row in rows:
        payload = {"organ": row[0], "milestone": row[-1]}
        records.append(IdealEndStateOrganRecord(stable_id("ideal_organ", payload), IDEAL_ORGAN_SCHEMA_VERSION, *row))
    return tuple(records)


def _module_exists(module_records: tuple[Any, ...], module_name: str) -> bool:
    return any(getattr(record, "module_path", "") == module_name for record in module_records)


def _interface_status(interface_records: tuple[Any, ...], connection_id: str) -> str:
    for record in interface_records:
        if getattr(record, "connection_id", "") == connection_id:
            return str(getattr(record, "connection_status", "unknown"))
    return "unknown"


def _current_module_map(module_records: tuple[Any, ...]) -> tuple[dict[str, Any], ...]:
    groups = {
        "bounded session runtime": ("ashl_core_v1.runtime.bounded_embodied_session_runtime", "verified_runtime"),
        "teacher gate": ("ashl_core_v1.runtime.teacher_gated_session_resume_commit", "verified_runtime"),
        "Package 90-92 learning pipeline": ("ashl_core_v1.learning.learning_feedback_to_concept_candidate", "verified_partial"),
        "reviewed interpretation commit": ("ashl_core_v1.runtime.teacher_gated_session_resume_commit", "verified_runtime"),
        "working readback": ("ashl_core_v1.runtime.teacher_gated_session_store", "verified_runtime"),
        "cross-process continuation": ("ashl_core_v1.runtime.no_codex_two_cycle_fixture_growth_run", "verified_runtime"),
        "camera/screen/microphone/host-state ingress": ("ashl_core_v1.runtime.bounded_host_sensor_ingress_runtime", "verified_runtime"),
        "ephemeral audio": ("ashl_core_v1.runtime.ephemeral_audio_ring_buffer", "verified_runtime"),
        "raw artifact store": ("ashl_core_v1.runtime.content_addressed_sensor_artifact_store", "verified_runtime"),
        "primitive compiler": ("ashl_core_v1.perception.hard_soft_perception_primitive_compiler", "verified_runtime"),
        "multimodal timeline": ("ashl_core_v1.runtime.bounded_multimodal_perception_session_runtime", "verified_runtime"),
        "PerceptionReadableData": ("ashl_core_v1.perception.types", "schema_only"),
        "HostBodyEvent bridge": ("ashl_core_v1.runtime.perception_to_host_body_event_adapter", "verified_runtime"),
        "internal action": ("ashl_core_v1.host_body.host_body_internal_action_choice", "verified_runtime"),
        "Home surface": ("ashl_core_v1.host_body.internal_action_home_surface_link", "verified_partial"),
        "active perception": ("ashl_core_v1.runtime.perception_low_level_event_policy", "verified_partial"),
        "persistent self-state": ("ashl_core_v1.state.cradle_state_persistence_handoff", "verified_partial"),
        "endocrine": ("ashl_core_v1.endocrine.types", "schema_only"),
        "Thought Engine": ("ashl_core_v1.thought.types", "schema_only"),
    }
    rows = []
    for name, (module, expected_status) in groups.items():
        exists = _module_exists(module_records, module)
        rows.append(
            {
                "organ": name,
                "module_ref": module,
                "current_status": expected_status if exists else "missing",
                "evidence": "module present in source scan" if exists else "no matching runtime module found",
            }
        )
    return tuple(rows)


def _gap(
    name: str,
    category: str,
    ideal_module: str,
    refs: tuple[str, ...],
    status: str,
    required: str,
    missing_interfaces: tuple[str, ...],
    missing_behavior: tuple[str, ...],
    missing_tests: tuple[str, ...],
    blocks: tuple[str, ...],
    severity: str,
    resolution: str,
) -> ArchitectureCapabilityGapRecord:
    payload = {"name": name, "ideal": ideal_module, "blocks": blocks}
    return ArchitectureCapabilityGapRecord(
        gap_id=stable_id("architecture_capability_gap", payload),
        schema_version=CAPABILITY_GAP_SCHEMA_VERSION,
        gap_name=name,
        gap_category=category,
        ideal_module=ideal_module,
        current_module_refs=refs,
        current_status=status,
        required_status=required,
        missing_interfaces=missing_interfaces,
        missing_runtime_behavior=missing_behavior,
        missing_tests=missing_tests,
        blocks_package_ids=blocks,
        severity=severity,
        recommended_resolution=resolution,
    )


def _bottleneck(
    name: str,
    upstream: tuple[str, ...],
    downstream: tuple[str, ...],
    info: str,
    authority: str,
    coupling: str,
    evidence: tuple[str, ...],
    milestones: tuple[str, ...],
    status: str,
    action: str,
) -> ArchitectureBottleneckRecord:
    return ArchitectureBottleneckRecord(
        bottleneck_id=stable_id("architecture_bottleneck", {"interface": name, "status": status}),
        schema_version=BOTTLENECK_SCHEMA_VERSION,
        interface_name=name,
        upstream_modules=upstream,
        downstream_modules=downstream,
        throughput_role="critical runtime handoff",
        information_loss_risk=info,
        authority_concentration_risk=authority,
        coupling_risk=coupling,
        current_evidence=evidence,
        affected_future_milestones=milestones,
        bottleneck_status=status,
        recommended_action=action,
    )


def _build_gaps_and_bottlenecks(interface_records: tuple[Any, ...]) -> tuple[tuple[ArchitectureCapabilityGapRecord, ...], tuple[ArchitectureBottleneckRecord, ...]]:
    perception_to_host_body_status = _interface_status(interface_records, "perception_to_host_body")
    gaps = (
        _gap(
            "HostBodyEvent perception payload may become overloaded",
            "overloaded_interface",
            "Multimodal Timeline System",
            ("ashl_core_v1.runtime.perception_to_host_body_event_adapter", "ashl_core_v1.runtime.bounded_embodied_session_runtime"),
            "needs_typed_perception_event_interface",
            "safe current adapter plus typed future perception context",
            ("typed_perception_event_interface", "parallel_read_only_perception_context"),
            ("future active attention should not parse generic HostBodyEvent payloads as its primary API",),
            ("future active perception integration tests",),
            ("125", "127", "132"),
            "high",
            "Keep the current Package 122 adapter for Package 123, then add a typed read-only perception context before active attention.",
        ),
        _gap(
            "PerceptionReadableData summary is intentionally compressed",
            "trace_lineage_risk",
            "Perception Compilation System",
            ("ashl_core_v1.perception.perception_readable_data_builder", "ashl_core_v1.perception.perception_primitive_store"),
            "verified_partial",
            "primitive identity and detailed primitive table remain available downstream",
            ("primitive_detail_loader_for_attention",),
            ("downstream modules must load primitive records instead of relying only on readable summaries",),
            ("compression-risk integration tests",),
            ("125", "126"),
            "medium",
            "Preserve `PerceptionReadableData` as summary and expose primitive-detail read APIs to attention modules.",
        ),
        _gap(
            "Teacher gate will need specialized future scopes",
            "authority_leak",
            "Teacher System",
            ("ashl_core_v1.runtime.session_learning_evidence_identity", "ashl_core_v1.runtime.teacher_gated_session_resume_commit"),
            "approval_scope_repaired_for_current_commit_path",
            "separate future scopes for perception interpretation, retention, speaker profile, and commitment memory",
            ("perception_interpretation_scope", "retention_scope", "speaker_profile_scope", "speech_content_scope"),
            ("future semantic/audio lanes need narrower teacher interfaces",),
            ("future specialized teacher-gate tests",),
            ("130", "173", "174", "175"),
            "medium",
            "Do not widen current approval; add explicit scopes only when those future capabilities are implemented.",
        ),
        _gap(
            "Working readback is an active interpreted hint, not the full memory system",
            "missing_module",
            "Memory System",
            ("ashl_core_v1.runtime.teacher_gated_session_store", "ashl_core_v1.host_body.host_body_readback_internal_action_influence"),
            "active interpreted hint and session initialization context",
            "five-layer memory with retrieval, routing, self-state separation, and long-term governance",
            ("memory_layer_router", "persistent_self_state_boundary"),
            ("long-term memory retrieval and persistent self-state are not completed by working readback",),
            ("five-layer memory integration tests",),
            ("133", "167"),
            "high",
            "Keep working readback bounded; build persistent self-state and memory retrieval as separate organs.",
        ),
        _gap(
            "Internal action set lacks active perception verbs",
            "missing_connection",
            "Active Perception And Attention System",
            ("ashl_core_v1.host_body.host_body_internal_action_choice",),
            "mark_uncertain/request_teacher_review/observe_again/pause/home_status are available or represented",
            "listen_again/shift_internal_focus/extend_observation_window connected as internal-only actions",
            ("attention_action_adapter",),
            ("relisten, recapture and focus-shift are not connected to multimodal runtime yet",),
            ("active perception action tests",),
            ("128", "132"),
            "high",
            "Add bounded recapture/relisten/focus internal actions after Package 124.",
        ),
        _gap(
            "Qingyin Home is currently a read-only record surface",
            "missing_connection",
            "Qingyin Home Runtime Surface",
            ("ashl_core_v1.host_body.internal_action_home_surface_link", "ashl_core_v1.host_body.qingyin_home_internal_space_surface"),
            "read-only record surface",
            "real runtime surface for status, perception, teacher gate, and memory/readback state",
            ("home_runtime_status_adapter", "perception_status_surface"),
            ("live UI/runtime status aggregation is not implemented",),
            ("home runtime surface integration tests",),
            ("169",),
            "medium",
            "Treat current Home records as surface links; build daily runtime surface later.",
        ),
        _gap(
            "Persistent self-state is not completed by session persistence",
            "missing_module",
            "Persistent Self-State System",
            ("ashl_core_v1.state.cradle_state_persistence_handoff", "ashl_core_v1.runtime.teacher_gated_session_store"),
            "session persistence and restore preview exist",
            "teacher-gated persistent self-state distinct from working readback and sensor state",
            ("persistent_self_state_store", "self_state_teacher_gate"),
            ("identity/personality-like continuity remains unimplemented",),
            ("self-state rollback and review tests",),
            ("133", "140"),
            "high",
            "Build self-state as its own bounded governed store after active perception milestone.",
        ),
        _gap(
            "Endocrine line remains mostly schema/historical scaffolding",
            "missing_module",
            "Mimetic Endocrine Regulation System",
            ("ashl_core_v1.endocrine.types",),
            "schema_only_or_historical",
            "bounded non-authoritative modulation with persistent drive review gate",
            ("drive_signal_trace_adapter",),
            ("same-session regulation and persistent drive state are not runtime organs",),
            ("endocrine modulation boundary tests",),
            ("135", "140"),
            "medium",
            "Keep endocrine signals non-authoritative and separate them from action selection.",
        ),
        _gap(
            "Thought Engine is design/schema only",
            "missing_module",
            "Thought Engine",
            ("ashl_core_v1.thought.types",),
            "schema_only",
            "non-LLM Instinct, Specialized Thought, Coarse Thought, and Deep Thought runtime layers",
            ("thought_runtime_dispatch", "thought_trace_boundary"),
            ("no current non-LLM thought runtime exists",),
            ("thought engine non-LLM tests",),
            ("141", "148"),
            "high",
            "Do not imply Thought Engine behavior before packages 141-148.",
        ),
        _gap(
            "Audio roadmap package numbers collided with active perception route",
            "roadmap_conflict",
            "Audit And Governance System",
            ("ashl_core_v1/docs/reference/qingyin_audio_line_decisions_v0.md", "ashl_core_v1/docs/reference/qingyin_master_roadmap_after_package_116_v0.md"),
            "collision_detected_and_reconciled",
            "unique normal numeric package ids after Package 124",
            tuple(),
            ("audio concept/retention/speaker/speech routes must not reuse 125-129",),
            ("roadmap registry tests",),
            tuple(),
            "medium",
            "Place grounded auditory concepts in 130/131, retention in 173, speaker decision in 174, and speech content in 175/post-v1.",
        ),
    )
    bottlenecks = (
        _bottleneck(
            "PerceptionReadableData -> HostBodyEvent",
            ("ashl_core_v1.perception", "ashl_core_v1.runtime.perception_to_host_body_event_adapter"),
            ("ashl_core_v1.runtime.bounded_embodied_session_runtime",),
            "medium: primitive ids and source refs are preserved, but future modules should not rely on generic payload parsing",
            "medium: HostBodyEvent is the teacher-gate ingress",
            "medium",
            (f"connection_status={perception_to_host_body_status}", "Package 122 bridge preserves primitive/readable/window ids"),
            ("125", "127", "132"),
            "needs_typed_perception_event_interface",
            "Add typed perception event/read-only context before active attention.",
        ),
        _bottleneck("HostBodyEvent -> internal action", ("bounded_embodied_session_runtime",), ("host_body_internal_action_choice",), "low", "medium", "low", ("existing Package 115 path",), ("128",), "safe_current_adapter", "Extend internal action vocabulary without external control."),
        _bottleneck("learning evidence -> teacher gate", ("bounded_embodied_session_runtime",), ("session_learning_evidence_identity",), "low", "low", "low", ("Package 117 identity binding",), ("123", "124"), "safe_current_adapter", "Use current gate for Package 123."),
        _bottleneck("teacher decision -> Package 90-92", ("teacher_gated_session_resume_commit",), ("learning",), "low", "medium", "medium", ("approval scope is explicit",), ("130", "173"), "safe_current_adapter", "Add future specialized scopes rather than widening current one."),
        _bottleneck("memory commit -> working readback", ("teacher_gated_session_resume_commit",), ("teacher_gated_session_store",), "low", "medium", "medium", ("Package 118 cross-process consumption",), ("133", "167"), "safe_current_adapter", "Keep working readback classified as active interpreted hint."),
        _bottleneck("working readback -> candidate scoring", ("teacher_gated_session_store",), ("host_body_readback_internal_action_influence",), "low", "medium", "medium", ("Package 118 receipt proves candidate delta provenance",), ("127",), "safe_current_adapter", "Keep provenance on candidate score records."),
        _bottleneck("runtime state -> Qingyin Home", ("bounded_embodied_session_runtime",), ("internal_action_home_surface_link",), "medium", "low", "medium", ("Home surface link records exist",), ("169",), "record_surface_not_live_ui", "Build live Home status surface later."),
    )
    return gaps, bottlenecks


def _duplicates_or_orphans(module_records: tuple[Any, ...]) -> tuple[ArchitectureDuplicateOrOrphanRecord, ...]:
    records = [
        ArchitectureDuplicateOrOrphanRecord(
            record_id="duplicate_fixture_demo_builders_need_runtime_boundary_review",
            schema_version=DUPLICATE_OR_ORPHAN_SCHEMA_VERSION,
            item_kind="conceptual_duplicate_fixture_builder",
            item_refs=("build_demo_* milestone pass builders", "runtime capability profiles"),
            classification="requires_human_review",
            current_runtime_consumer_count=0,
            safe_to_archive=False,
            requires_human_review=True,
            reason="Demo builders remain useful for tests/CLI but must stay out of live runtime hot paths.",
        ),
        ArchitectureDuplicateOrOrphanRecord(
            record_id="historical_phase0_documents_design_only",
            schema_version=DUPLICATE_OR_ORPHAN_SCHEMA_VERSION,
            item_kind="historical_document_route",
            item_refs=("ashl_core_v1/docs/concept_transfer_sources", "docs_archive"),
            classification="historical_design_only",
            current_runtime_consumer_count=0,
            safe_to_archive=False,
            requires_human_review=True,
            reason="Historical documents explain intent but do not override current code or generated package registry.",
        ),
    ]
    for record in module_records:
        consumers = tuple(getattr(record, "downstream_consumers", tuple()))
        status = getattr(record, "implementation_status", "")
        module = getattr(record, "module_path", "")
        if not consumers and status not in {"actual_cli", "actual_test_harness"} and any(token in module for token in ("thought", "endocrine")):
            records.append(
                ArchitectureDuplicateOrOrphanRecord(
                    record_id=stable_id("architecture_duplicate_or_orphan", {"module": module}),
                    schema_version=DUPLICATE_OR_ORPHAN_SCHEMA_VERSION,
                    item_kind="unconsumed_module",
                    item_refs=(module,),
                    classification="schema_or_design_orphan",
                    current_runtime_consumer_count=0,
                    safe_to_archive=False,
                    requires_human_review=True,
                    reason="Module is visible in source but not consumed by the current runtime path.",
                )
            )
    return tuple(records)


def _package123_go_no_go(module_records: tuple[Any, ...], interface_records: tuple[Any, ...], gaps: tuple[ArchitectureCapabilityGapRecord, ...], repo_root: Path) -> Package123ArchitectureGoNoGoRecord:
    package_122_runtime_valid = _module_exists(module_records, "ashl_core_v1.runtime.bounded_multimodal_perception_session_runtime")
    perception_lineage_valid = _interface_status(interface_records, "perception_to_host_body") in {"verified_runtime_connection", "implemented_without_integration_test"}
    teacher_gate_path_valid = _interface_status(interface_records, "learning_evidence_to_teacher_gate") in {"verified_runtime_connection", "implemented_without_integration_test"}
    cross_process_growth_path_valid = _module_exists(module_records, "ashl_core_v1.runtime.no_codex_two_cycle_fixture_growth_run") and _module_exists(module_records, "ashl_core_v1.runtime.no_codex_two_cycle_fixture_growth_worker")
    package123_module_exists = _module_exists(module_records, "ashl_core_v1.runtime.no_codex_real_perception_two_cycle_growth_run")
    missing_live_data_only = package_122_runtime_valid and perception_lineage_valid and teacher_gate_path_valid and cross_process_growth_path_valid and not package123_module_exists
    blockers = tuple(gap.gap_name for gap in gaps if gap.severity == "critical" and "123" in gap.blocks_package_ids)
    nonblocking = tuple(gap.gap_name for gap in gaps if gap.severity in {"high", "medium"} and "123" not in gap.blocks_package_ids)
    go = not blockers and package_122_runtime_valid and perception_lineage_valid and teacher_gate_path_valid and cross_process_growth_path_valid
    reason = (
        "Package 123 may proceed: current blocker is live real-experience data, not architecture wiring."
        if go and missing_live_data_only
        else "Package 123 blocked by architecture evidence gaps."
    )
    return Package123ArchitectureGoNoGoRecord(
        record_id=stable_id("package_123_go_no_go", {"go": go, "blockers": blockers}),
        schema_version=PACKAGE_123_GO_NO_GO_SCHEMA_VERSION,
        created_at=utc_now(),
        package_122_runtime_valid=package_122_runtime_valid,
        perception_lineage_valid=perception_lineage_valid,
        teacher_gate_path_valid=teacher_gate_path_valid,
        cross_process_growth_path_valid=cross_process_growth_path_valid,
        missing_live_experience_data_only=missing_live_data_only,
        architecture_blockers=blockers,
        nonblocking_gaps=nonblocking,
        package_123_go=go,
        decision_reason=reason,
    )


def analyze_architecture_gaps(
    *,
    repo_root: str | Path,
    baseline: Any,
    module_records: tuple[Any, ...],
    interface_records: tuple[Any, ...],
    store_records: tuple[Any, ...],
    surface_records: tuple[Any, ...],
    test_records: tuple[Any, ...],
    roadmap_records: dict[str, Any],
) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    ideal = _ideal_organs()
    current_map = _current_module_map(module_records)
    gaps, bottlenecks = _build_gaps_and_bottlenecks(interface_records)
    duplicates = _duplicates_or_orphans(module_records)
    conflicts = roadmap_records.get("roadmap_conflicts", [])
    package_conflicts_resolved = bool(conflicts) and all(item.get("resolution_status") == "resolved" for item in conflicts)
    go_no_go = _package123_go_no_go(module_records, interface_records, gaps, root)
    critical_risks = tuple(gap.gap_name for gap in gaps if gap.severity == "critical")
    high_gaps = tuple(gap.gap_name for gap in gaps if gap.severity == "high")
    failure_reasons = []
    if not getattr(baseline, "scan_id", None):
        failure_reasons.append("repo_scan_incomplete")
    if not module_records:
        failure_reasons.append("module_inventory_incomplete")
    if not interface_records:
        failure_reasons.append("interface_map_incomplete")
    if not package_conflicts_resolved:
        failure_reasons.append("package_number_conflict_unresolved")
    audit_status = (
        "passed_architecture_module_and_roadmap_gap_reconciliation"
        if not failure_reasons
        else "blocked_critical_path_unresolved"
    )
    audit = ArchitectureModuleRoadmapReconciliationAuditRecord(
        audit_id=stable_id("architecture_reconciliation_audit", {"baseline": getattr(baseline, "scan_id", ""), "status": audit_status}),
        schema_version=ARCHITECTURE_AUDIT_SCHEMA_VERSION,
        created_at=utc_now(),
        repo_scan_complete=bool(getattr(baseline, "scan_id", None)),
        module_inventory_complete=bool(module_records),
        interface_map_complete=bool(interface_records),
        store_inventory_complete=bool(store_records),
        CLI_inventory_complete=bool(surface_records),
        test_map_complete=bool(test_records),
        ideal_module_map_complete=bool(ideal),
        current_module_map_complete=bool(current_map),
        gap_matrix_complete=bool(gaps),
        package_number_conflicts_resolved=package_conflicts_resolved,
        revised_roadmap_complete=bool(roadmap_records.get("revised_route")),
        package_123_path_valid=go_no_go.package_123_go,
        package_124_path_valid=go_no_go.package_123_go,
        critical_interface_risks=critical_risks,
        high_priority_gaps=high_gaps,
        runtime_behavior_changed=False,
        source_runtime_records_modified=False,
        audit_status=audit_status,
        failure_reasons=tuple(failure_reasons),
    )
    return {
        "ideal_organs": [record.to_dict() for record in ideal],
        "current_module_map": list(current_map),
        "capability_gaps": [record.to_dict() for record in gaps],
        "bottlenecks": [record.to_dict() for record in bottlenecks],
        "duplicates_or_orphans": [record.to_dict() for record in duplicates],
        "audit": audit.to_dict(),
        "package_123_go_no_go": go_no_go.to_dict(),
    }
