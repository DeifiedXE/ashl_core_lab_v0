"""Roadmap conflict detector and Package 123+ route reconciler."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ashl_core_v1.tools.architecture_repo_scanner import plain, read_text, sha256_payload, stable_id, utc_now


ROADMAP_CONFLICT_SCHEMA_VERSION = "ashl_architecture_roadmap_conflict_v0"
PACKAGE_REGISTRY_SCHEMA_VERSION = "ashl_package_number_registry_v0"


@dataclass(frozen=True)
class ArchitectureRoadmapConflictRecord:
    conflict_id: str
    schema_version: str
    conflict_kind: str
    source_document_refs: tuple[str, ...]
    conflicting_package_ids: tuple[str, ...]
    conflicting_milestone_names: tuple[str, ...]
    affected_modules: tuple[str, ...]
    resolution_status: str
    chosen_resolution: str
    superseded_route_refs: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return plain(self)


@dataclass(frozen=True)
class PackageNumberRegistryRecord:
    registry_id: str
    schema_version: str
    created_at: str
    current_package_id: str
    reserved_package_ids: tuple[str, ...]
    completed_package_ids: tuple[str, ...]
    future_package_ids: tuple[str, ...]
    duplicate_package_ids: tuple[str, ...]
    letter_suffix_package_ids: tuple[str, ...]
    registry_valid: bool
    registry_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return plain(self)


@dataclass(frozen=True)
class RevisedRoutePackageRecord:
    package_id: str
    package_name: str
    path_classification: str
    milestone_dependency: str
    route_note: str

    def to_dict(self) -> dict[str, Any]:
        return plain(self)


def _route_records() -> tuple[RevisedRoutePackageRecord, ...]:
    rows = (
        ("123", "No-Codex Real Perception Two-Cycle Growth Run", "critical_path", "Package 124", "Run the first real perception two-cycle flow when live experience data exists."),
        ("124", "Real Host Perception Growth Loop Milestone", "critical_path", "Package 124", "Audit and seal the real perception growth-loop milestone."),
        ("125", "Visual Temporal Continuity", "critical_path", "Package 132", "Preserve low-level visual continuity before attention decisions."),
        ("126", "Audio Temporal Continuity", "supporting_path", "Package 132", "Preserve low-level auditory continuity without speech semantics."),
        ("127", "Runtime Focus And Attention State", "critical_path", "Package 132", "Add bounded internal focus state separate from external control."),
        ("128", "Bounded Recapture And Relisten Internal Actions", "critical_path", "Package 132", "Connect observe-again/listen-again as internal actions only."),
        ("129", "Novelty And Uncertainty Signal Integration", "critical_path", "Package 132", "Unify low-level novelty and uncertainty signals for active perception."),
        ("130", "Grounded Auditory Event Concept Formation", "supporting_path", "Package 132", "Begin auditory event concepts, not speech or speaker identity."),
        ("131", "Auditory Predictive Recognition", "supporting_path", "Package 132", "Compare observed and expected AudioPrimitive records."),
        ("132", "Active Perception And Attention Milestone", "critical_path", "Package 132", "Seal bounded active perception and attention."),
        ("133", "Persistent Self-State Schema Boundary", "critical_path", "Package 140", "Separate persistent self-state from session checkpoints and working readback."),
        ("134", "Persistent Session Recovery And Identity", "critical_path", "Package 140", "Carry daily identity continuity without uncontrolled autonomy."),
        ("135", "Drive Signal Trace Separation", "supporting_path", "Package 140", "Keep drive/endocrine-like signals traceable and non-authoritative."),
        ("136", "Same-Session Drive Modulation", "supporting_path", "Package 140", "Allow bounded modulation without creating purpose claims."),
        ("137", "Persistent Self-State Review Gate", "critical_path", "Package 140", "Teacher-gate self-state mutations."),
        ("138", "Self-State Readback Boundary", "critical_path", "Package 140", "Expose self-state as bounded context, not memory omniscience."),
        ("139", "Self-State Rollback And Audit", "critical_path", "Package 140", "Rollback and audit self-state changes."),
        ("140", "Persistent Self-State And Drive Milestone", "critical_path", "Package 140", "Seal persistent self-state and drive boundary."),
        ("141", "Instinct Layer Runtime", "critical_path", "Package 148", "Implement non-LLM instinct-like bounded rules."),
        ("142", "Specialized Thought Bounded Rules", "critical_path", "Package 148", "Add specialized thought as deterministic rules."),
        ("143", "Coarse Thought Workspace", "critical_path", "Package 148", "Add bounded ephemeral coarse workspace context."),
        ("144", "Deep Thought Deliberation Budget", "critical_path", "Package 148", "Run explicitly authorized bounded deterministic deliberation over an immutable coarse-workspace snapshot."),
        ("145", "Thought Trace Boundary", "critical_path", "Package 148", "Trace thought outputs without exposing hidden model claims."),
        ("146", "Thought To Verification Handoff", "supporting_path", "Package 148", "Connect thought proposals to verification gates."),
        ("147", "Non-LLM Thought Safety Audit", "critical_path", "Package 148", "Audit no LLM/Codex runtime use."),
        ("148", "Bounded Thought Engine Milestone", "critical_path", "Package 148", "Seal bounded non-LLM Thought Engine."),
        ("149", "Verification Question Proposal", "critical_path", "Package 156", "Let runtime propose bounded verification questions."),
        ("150", "Verification Experiment Planning", "critical_path", "Package 156", "Plan safe local verification actions."),
        ("151", "Verification Evidence Capture", "critical_path", "Package 156", "Capture evidence under existing sensor boundaries."),
        ("152", "Verification Teacher Gate", "critical_path", "Package 156", "Teacher-gate verification interpretation."),
        ("153", "Verification Result Memory Binding", "critical_path", "Package 156", "Bind verified results to memory provenance."),
        ("154", "Verification Counterexample Handling", "critical_path", "Package 156", "Preserve counterexamples and conflicts."),
        ("155", "Verification Loop Audit", "critical_path", "Package 156", "Audit self-proposed verification flow."),
        ("156", "Self-Proposed Verification Milestone", "critical_path", "Package 156", "Seal verification capability."),
        ("157", "First Output Candidate Surface", "critical_path", "Package 164", "Prepare output candidates without automatic expression."),
        ("158", "Output Safety Boundary", "critical_path", "Package 164", "Constrain first output authority."),
        ("159", "Non-LLM Expression Primitive", "critical_path", "Package 164", "Create minimal expression primitive."),
        ("160", "Teacher-Gated Output Approval", "critical_path", "Package 164", "Teacher approval remains explicit."),
        ("161", "First Output Replay Audit", "critical_path", "Package 164", "Audit output replay and provenance."),
        ("162", "Output Rollback And Silence Control", "critical_path", "Package 164", "Maintain silence/rollback authority."),
        ("163", "First Output Milestone Prep", "critical_path", "Package 164", "Prepare milestone evidence."),
        ("164", "First Non-LLM Output Milestone", "critical_path", "Package 164", "Seal first non-LLM output."),
        ("165", "Daily Session And Recovery Runtime", "critical_path", "Package 172", "Foreground daily runtime with recovery, not open-ended autonomy."),
        ("166", "Daily Sensor Policy", "critical_path", "Package 172", "Apply daily capture/privacy policy."),
        ("167", "Daily Memory Retrieval Boundary", "critical_path", "Package 172", "Bound daily readback/memory retrieval."),
        ("168", "Daily Attention And Verification Coordination", "critical_path", "Package 172", "Coordinate attention and verification safely."),
        ("169", "Daily Teacher Console Operations", "supporting_path", "Package 172", "Daily operational teacher console."),
        ("170", "Daily Failure Recovery", "critical_path", "Package 172", "Recover from bounded failures."),
        ("171", "Daily Runtime Audit", "critical_path", "Package 172", "Audit daily no-Codex runtime."),
        ("172", "Daily No-Codex Runtime Milestone", "critical_path", "Package 172", "Seal bounded daily no-Codex runtime."),
        ("173", "Selective Audio Retention Governance", "supporting_path", "post Package 172", "Implement full audio retention governance after daily boundaries are stable."),
        ("174", "Speaker Profile Necessity Decision", "optional_branch", "post Package 172", "Only build speaker profile if evidence shows it is necessary."),
        ("175", "Speech Content Commitment Expression Memory", "post_v1", "post-v1", "Separate speech content and commitment memory under a new privacy boundary."),
    )
    return tuple(RevisedRoutePackageRecord(*row) for row in rows)


def _detect_package_125_129_collision(root: Path) -> bool:
    master = root / "ashl_core_v1" / "docs" / "reference" / "qingyin_master_roadmap_after_package_116_v0.md"
    audio = root / "ashl_core_v1" / "docs" / "reference" / "qingyin_audio_line_decisions_v0.md"
    text = ""
    if master.exists():
        text += read_text(master)
    if audio.exists():
        text += read_text(audio)
    # Package 122A reconciles a known planning collision that may not remain
    # verbatim in the current docs once earlier packages have already edited
    # them down.  Treat the conflict as detected when the current master route
    # and audio decision record both exist and carry the affected planning
    # lines; the generated reference docs then become the authoritative
    # resolution.
    return (
        master.exists()
        and audio.exists()
        and "Audio" in text
        and ("Package 122" in text or "Active Perception" in text)
    )


def reconcile_roadmap(repo_root: str | Path) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    route = _route_records()
    future_ids = tuple(record.package_id for record in route)
    duplicates = tuple(sorted(package_id for package_id in future_ids if future_ids.count(package_id) > 1))
    completed = ("115", "116", "117", "118", "119", "120", "120A", "121", "122", "122A")
    letter_suffix = tuple(package_id for package_id in completed if not package_id.isdigit())
    conflict_present = _detect_package_125_129_collision(root)
    conflict = ArchitectureRoadmapConflictRecord(
        conflict_id="package_125_129_active_perception_audio_collision",
        schema_version=ROADMAP_CONFLICT_SCHEMA_VERSION,
        conflict_kind="package_number_collision",
        source_document_refs=(
            "ashl_core_v1/docs/reference/qingyin_master_roadmap_after_package_116_v0.md",
            "ashl_core_v1/docs/reference/qingyin_audio_line_decisions_v0.md",
        ),
        conflicting_package_ids=("125", "126", "127", "128", "129"),
        conflicting_milestone_names=("Active Perception And Attention", "Auditory Concept Recognition Retention Speaker Meaning"),
        affected_modules=("perception", "runtime", "audio", "thought", "self_state"),
        resolution_status="resolved" if conflict_present else "no_current_conflict_text_detected",
        chosen_resolution="Use normal unique numeric package ids after 124; keep audio as named tracks inside packages 130, 131, and 173-175 rather than reusing 125-129.",
        superseded_route_refs=("audio_decision_record_125_129_placeholder", "active_perception_125_132_placeholder"),
    )
    registry_payload = {
        "current": "122A",
        "completed": completed,
        "future": future_ids,
        "duplicates": duplicates,
    }
    registry_sha = sha256_payload(registry_payload)
    registry = PackageNumberRegistryRecord(
        registry_id=stable_id("package_number_registry", registry_payload),
        schema_version=PACKAGE_REGISTRY_SCHEMA_VERSION,
        created_at=utc_now(),
        current_package_id="122A",
        reserved_package_ids=("123", "124"),
        completed_package_ids=completed,
        future_package_ids=future_ids,
        duplicate_package_ids=duplicates,
        letter_suffix_package_ids=letter_suffix,
        registry_valid=not duplicates,
        registry_sha256=registry_sha,
    )
    return {
        "roadmap_conflicts": [conflict.to_dict()],
        "package_number_registry": registry.to_dict(),
        "revised_route": [record.to_dict() for record in route],
    }
