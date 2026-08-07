"""Actual validator and isolated-authority controls for Package 137."""

from __future__ import annotations

import shutil
from contextlib import contextmanager
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Callable, Iterator

from ashl_core_v1.runtime.host_sensor_types import sha256_payload, utc_now
from ashl_core_v1.state.package_134_package_133_source import (
    load_package_133_source_read_only,
)
from ashl_core_v1.state.package_137_self_state_review_store import (
    Package137SelfStateReviewStore,
)
from ashl_core_v1.state.persistent_self_state_review_runtime import (
    _hashed_record,
    _require_proposal_current,
    commit_approved_self_state_successor,
    create_self_state_successor_proposal,
    review_self_state_successor_proposal,
)
from ashl_core_v1.state.persistent_self_state_review_types import (
    CONTROL_NAMES,
    CONTROL_SCHEMA_VERSION,
    SelfStateSuccessorProposalRecord,
    Package137ControlResult,
)
from ashl_core_v1.state.persistent_self_state_store import (
    PACKAGE_DIR as PACKAGE_133_DIR,
    PersistentSelfStateStore,
)
from ashl_core_v1.state.persistent_session_recovery_store import (
    PACKAGE_DIR as PACKAGE_134_DIR,
    PersistentSessionRecoveryStore,
)


def run_package_137_self_state_review_controls(
    *,
    ashl_root: str | Path,
    package_133_state_dir: str | Path,
    package_134_state_dir: str | Path,
    state_dir: str | Path,
    append: bool = True,
) -> Package137ControlResult:
    store = Package137SelfStateReviewStore(state_dir)
    existing = store.latest_payload("package_137_control_results")
    if existing is not None:
        return Package137ControlResult(
            **{
                **existing,
                "control_names": tuple(existing["control_names"]),
                "passed_control_names": tuple(existing["passed_control_names"]),
                "evidence_refs": tuple(existing["evidence_refs"]),
            }
        )

    outcomes: dict[str, bool] = {}
    evidence: list[str] = []

    with _authority_copy(package_133_state_dir, package_134_state_dir) as roots:
        p133, p134, p137 = roots
        seeded = _proposal(
            ashl_root, p133, p134, p137, "package_137_control_delta_session"
        )
        delta = seeded["delta"]
        proposal = seeded["proposal"]
        outcomes["non_allowlisted_delta_rejected"] = _rejects(
            lambda: replace(
                delta,
                changed_persistent_fields=(
                    "self_state_version",
                    "lineage_generation",
                    "memory_content",
                ),
            ),
            "allowlist",
        )
        outcomes["semantic_content_delta_rejected"] = _rejects(
            lambda: replace(delta, semantic_content_added=True), "forbidden"
        )
        outcomes["drive_or_modulation_delta_rejected"] = _rejects(
            lambda: replace(delta, drive_or_modulation_content_added=True), "forbidden"
        )
        outcomes["runtime_behavior_influence_rejected"] = _rejects(
            lambda: replace(delta, runtime_behavior_authority_added=True), "forbidden"
        )
        outcomes["package_135_drive_persistence_rejected"] = _rejects(
            lambda: replace(
                delta,
                complete_persistent_field_allowlist=(
                    *delta.complete_persistent_field_allowlist,
                    "drive_signal_trace",
                ),
            ),
            "allowlist",
        )
        outcomes["package_136_modulation_persistence_rejected"] = _rejects(
            lambda: replace(
                delta,
                complete_persistent_field_allowlist=(
                    *delta.complete_persistent_field_allowlist,
                    "drive_modulation",
                ),
            ),
            "allowlist",
        )
        outcomes["proposal_tampering_rejected"] = _rejects(
            lambda: replace(proposal, delta_sha256="0" * 64), "mismatch"
        )
        evidence.extend(f"validator:{name}" for name, passed in outcomes.items() if passed)

    outcomes["missing_explicit_teacher_action_rejected"], ref = _teacher_rejection_control(
        ashl_root,
        package_133_state_dir,
        package_134_state_dir,
        explicit_teacher_action=False,
        teacher_actor="project_owner",
        teacher_role="project_owner",
        expected="explicit_teacher_action_missing",
    )
    evidence.append(ref)
    outcomes["invalid_teacher_actor_or_role_rejected"], ref = _teacher_rejection_control(
        ashl_root,
        package_133_state_dir,
        package_134_state_dir,
        explicit_teacher_action=True,
        teacher_actor="runtime",
        teacher_role="runtime",
        expected="invalid_existing_teacher_identity",
    )
    evidence.append(ref)
    outcomes["review_target_tampering_rejected"], ref = _review_tamper_control(
        ashl_root, package_133_state_dir, package_134_state_dir
    )
    evidence.append(ref)
    outcomes["wrong_parent_or_head_rejected"], ref = _wrong_head_control(
        ashl_root, package_133_state_dir, package_134_state_dir
    )
    evidence.append(ref)
    stale, ref = _stale_review_control(
        ashl_root, package_133_state_dir, package_134_state_dir
    )
    outcomes["stale_review_blocked_before_history_append"] = stale
    evidence.append(ref)
    conflict, ref = _partial_control(
        ashl_root,
        package_133_state_dir,
        package_134_state_dir,
        fault="cas_conflict_after_package_133_append",
        required_reason="active_head_cas_conflict",
    )
    outcomes["cas_conflict_blocked_without_rebase"] = conflict
    evidence.append(ref)
    partial, ref = _partial_control(
        ashl_root,
        package_133_state_dir,
        package_134_state_dir,
        fault="after_package_133_append_before_package_134_cas",
        required_reason="partial_after_package_133_append",
    )
    outcomes["cross_authority_partial_failure_visible_and_blocked"] = partial
    evidence.append(ref)
    reuse, ref = _approval_reuse_control(
        ashl_root, package_133_state_dir, package_134_state_dir
    )
    outcomes["approval_reuse_rejected"] = reuse
    evidence.append(ref)
    rejected, rejected_ref = _invariance_control(
        ashl_root, package_133_state_dir, package_134_state_dir, "rejected"
    )
    deferred, deferred_ref = _invariance_control(
        ashl_root, package_133_state_dir, package_134_state_dir, "deferred"
    )
    outcomes["rejected_review_preserves_authorities"] = rejected
    outcomes["deferred_review_preserves_authorities"] = deferred
    evidence.extend((rejected_ref, deferred_ref))
    corrupt_133, ref_133 = _corrupt_store_control(
        ashl_root, package_133_state_dir, package_134_state_dir, "package_133"
    )
    corrupt_134, ref_134 = _corrupt_store_control(
        ashl_root, package_133_state_dir, package_134_state_dir, "package_134"
    )
    outcomes["corrupt_package_133_store_blocked"] = corrupt_133
    outcomes["corrupt_package_134_store_blocked"] = corrupt_134
    evidence.extend((ref_133, ref_134))
    outcomes["package_137_store_append_only"], ref = _append_only_control()
    evidence.append(ref)

    passed = tuple(name for name in CONTROL_NAMES if outcomes.get(name, False))
    result = Package137ControlResult(
        control_result_id=f"package_137_controls:{sha256_payload({'controls': outcomes})[:16]}",
        schema_version=CONTROL_SCHEMA_VERSION,
        created_at=utc_now(),
        control_names=CONTROL_NAMES,
        passed_control_names=passed,
        passed_count=len(passed),
        expected_count=len(CONTROL_NAMES),
        controls_passed=len(passed) == len(CONTROL_NAMES),
        evidence_refs=tuple(dict.fromkeys(evidence)),
    )
    if append:
        store.append_once("package_137_control_results", result)
    return result


def _teacher_rejection_control(
    ashl_root: str | Path,
    source_133: str | Path,
    source_134: str | Path,
    *,
    explicit_teacher_action: bool,
    teacher_actor: str,
    teacher_role: str,
    expected: str,
) -> tuple[bool, str]:
    with _authority_copy(source_133, source_134) as (p133, p134, p137):
        proposal = _proposal(ashl_root, p133, p134, p137, f"teacher_{expected}")["proposal"]
        passed = _rejects(
            lambda: _review(
                ashl_root,
                p133,
                p134,
                p137,
                proposal.proposal_id,
                "approved",
                explicit_teacher_action=explicit_teacher_action,
                teacher_actor=teacher_actor,
                teacher_role=teacher_role,
            ),
            expected,
        )
        return passed, f"validator:{expected}"


def _review_tamper_control(
    ashl_root: str | Path, source_133: str | Path, source_134: str | Path
) -> tuple[bool, str]:
    with _authority_copy(source_133, source_134) as (p133, p134, p137):
        proposal = _proposal(ashl_root, p133, p134, p137, "review_tamper")["proposal"]
        review = _review(ashl_root, p133, p134, p137, proposal.proposal_id, "approved")["review"]
        return (
            _rejects(lambda: replace(review, delta_sha256="0" * 64), "mismatch"),
            f"review:{review.review_id}",
        )


def _wrong_head_control(
    ashl_root: str | Path, source_133: str | Path, source_134: str | Path
) -> tuple[bool, str]:
    with _authority_copy(source_133, source_134) as (p133, p134, p137):
        seeded = _proposal(ashl_root, p133, p134, p137, "wrong_head")
        proposal = seeded["proposal"]
        payload = proposal.to_dict()
        payload["proposal_id"] = ""
        payload["proposal_sha256"] = ""
        payload["expected_head_revision"] += 1
        wrong = _hashed_record(
            SelfStateSuccessorProposalRecord,
            payload,
            id_field="proposal_id",
            hash_field="proposal_sha256",
            prefix="self_state_successor_proposal",
        )
        head = PersistentSessionRecoveryStore(p134).get_active_head()
        source = load_package_133_source_read_only(p133)
        passed = _rejects(
            lambda: _require_proposal_current(wrong, seeded["delta"], head, source.leaf),
            "head",
        )
        return passed, f"proposal:{wrong.proposal_id}"


def _stale_review_control(
    ashl_root: str | Path, source_133: str | Path, source_134: str | Path
) -> tuple[bool, str]:
    with _authority_copy(source_133, source_134) as (p133, p134, p137):
        stale = _proposal(ashl_root, p133, p134, p137, "stale_review")
        stale_review = _review(
            ashl_root, p133, p134, p137, stale["proposal"].proposal_id, "approved"
        )["review"]
        winner = _proposal(ashl_root, p133, p134, p137, "stale_winner")
        winner_review = _review(
            ashl_root, p133, p134, p137, winner["proposal"].proposal_id, "approved"
        )["review"]
        won = commit_approved_self_state_successor(
            ashl_root=ashl_root,
            package_133_state_dir=p133,
            package_134_state_dir=p134,
            state_dir=p137,
            review_id=winner_review.review_id,
            process_instance_id="package_137_stale_winner_process",
            allow_self_state_mutation=True,
        )
        before = PersistentSelfStateStore(p133).count("persistent_self_state_records")
        blocked = commit_approved_self_state_successor(
            ashl_root=ashl_root,
            package_133_state_dir=p133,
            package_134_state_dir=p134,
            state_dir=p137,
            review_id=stale_review.review_id,
            process_instance_id="package_137_stale_review_process",
            allow_self_state_mutation=True,
        )
        after = PersistentSelfStateStore(p133).count("persistent_self_state_records")
        attempt = blocked.get("blocked_attempt")
        passed = bool(
            won["status"] == "committed_reviewed_self_state_successor"
            and blocked["status"] == "blocked"
            and before == after
            and attempt
            and "stale" in attempt.failure_reason
            and not attempt.automatic_rebase_performed
        )
        return passed, attempt.blocked_attempt_id if attempt else "stale_review:no_record"


def _partial_control(
    ashl_root: str | Path,
    source_133: str | Path,
    source_134: str | Path,
    *,
    fault: str,
    required_reason: str,
) -> tuple[bool, str]:
    with _authority_copy(source_133, source_134) as (p133, p134, p137):
        seeded = _proposal(ashl_root, p133, p134, p137, f"partial_{fault}")
        review = _review(
            ashl_root, p133, p134, p137, seeded["proposal"].proposal_id, "approved"
        )["review"]
        head_before = PersistentSessionRecoveryStore(p134).get_active_head()
        result = commit_approved_self_state_successor(
            ashl_root=ashl_root,
            package_133_state_dir=p133,
            package_134_state_dir=p134,
            state_dir=p137,
            review_id=review.review_id,
            process_instance_id=f"package_137_{fault}_process",
            allow_self_state_mutation=True,
            fault_injection=fault,
        )
        head_after = PersistentSessionRecoveryStore(p134).get_active_head()
        attempt = result.get("blocked_attempt")
        passed = bool(
            result["status"] == "blocked"
            and attempt
            and required_reason in attempt.failure_reason
            and attempt.package_133_successor_appended
            and not attempt.package_134_active_head_advanced
            and attempt.partial_failure_detected
            and not attempt.automatic_rebase_performed
            and head_before.active_head_sha256 == head_after.active_head_sha256
        )
        return passed, attempt.blocked_attempt_id if attempt else f"partial:{fault}:no_record"


def _approval_reuse_control(
    ashl_root: str | Path, source_133: str | Path, source_134: str | Path
) -> tuple[bool, str]:
    with _authority_copy(source_133, source_134) as (p133, p134, p137):
        seeded = _proposal(ashl_root, p133, p134, p137, "approval_reuse")
        review = _review(
            ashl_root, p133, p134, p137, seeded["proposal"].proposal_id, "approved"
        )["review"]
        first = commit_approved_self_state_successor(
            ashl_root=ashl_root,
            package_133_state_dir=p133,
            package_134_state_dir=p134,
            state_dir=p137,
            review_id=review.review_id,
            process_instance_id="package_137_reuse_first_process",
            allow_self_state_mutation=True,
        )
        head_before = PersistentSessionRecoveryStore(p134).get_active_head()
        second = commit_approved_self_state_successor(
            ashl_root=ashl_root,
            package_133_state_dir=p133,
            package_134_state_dir=p134,
            state_dir=p137,
            review_id=review.review_id,
            process_instance_id="package_137_reuse_second_process",
            allow_self_state_mutation=True,
        )
        head_after = PersistentSessionRecoveryStore(p134).get_active_head()
        attempt = second.get("blocked_attempt")
        passed = bool(
            first["status"] == "committed_reviewed_self_state_successor"
            and second["status"] == "blocked"
            and attempt
            and "already_consumed" in attempt.failure_reason
            and head_before.active_head_sha256 == head_after.active_head_sha256
        )
        return passed, attempt.blocked_attempt_id if attempt else "reuse:no_record"


def _invariance_control(
    ashl_root: str | Path,
    source_133: str | Path,
    source_134: str | Path,
    decision: str,
) -> tuple[bool, str]:
    with _authority_copy(source_133, source_134) as (p133, p134, p137):
        proposal = _proposal(ashl_root, p133, p134, p137, f"{decision}_invariance")["proposal"]
        result = _review(ashl_root, p133, p134, p137, proposal.proposal_id, decision)
        invariance = result["invariance"]
        return bool(
            invariance.authoritative_self_state_unchanged
            and invariance.active_head_unchanged
            and not invariance.mutation_attempted
        ), invariance.invariance_id


def _corrupt_store_control(
    ashl_root: str | Path,
    source_133: str | Path,
    source_134: str | Path,
    target: str,
) -> tuple[bool, str]:
    with _authority_copy(source_133, source_134) as (p133, p134, p137):
        if target == "package_133":
            store = PersistentSelfStateStore(p133)
            with store.connection() as connection:
                connection.execute(
                    "UPDATE persistent_self_state_records SET payload_sha256 = ? WHERE row_id = 1",
                    ("0" * 64,),
                )
                connection.commit()
        else:
            store = PersistentSessionRecoveryStore(p134)
            with store.connection() as connection:
                connection.execute(
                    "UPDATE active_self_state_head SET payload_sha256 = ? WHERE singleton_key = 'active'",
                    ("0" * 64,),
                )
                connection.commit()
        integrity_invalid = not store.audit_integrity()["valid"]
        proposal_blocked = _rejects(
            lambda: create_self_state_successor_proposal(
                ashl_root=ashl_root,
                package_133_state_dir=p133,
                package_134_state_dir=p134,
                state_dir=p137,
                proposed_source_session_id=f"{target}_corrupt_session",
                proposer_process_instance_id=f"{target}_corrupt_process",
            ),
            "",
        )
        return integrity_invalid and proposal_blocked, f"validator:{target}_corruption"


def _append_only_control() -> tuple[bool, str]:
    with TemporaryDirectory(prefix="ashl_package_137_append_only_") as directory:
        store = Package137SelfStateReviewStore(directory)
        blocked = all(
            _rejects(lambda method=method: method(), "append-only")
            for method in (store.update, store.delete, store.replace)
        )
        integrity = store.audit_integrity()
        return bool(
            blocked
            and integrity["valid"]
            and not integrity["active_head_table_present"]
            and not integrity["self_state_history_table_present"]
        ), "store:package_137_append_only_boundary"


def _proposal(
    ashl_root: str | Path,
    p133: Path,
    p134: Path,
    p137: Path,
    suffix: str,
) -> dict[str, Any]:
    return create_self_state_successor_proposal(
        ashl_root=ashl_root,
        package_133_state_dir=p133,
        package_134_state_dir=p134,
        state_dir=p137,
        proposed_source_session_id=f"package_137_control_session:{suffix}",
        proposer_process_instance_id=f"package_137_control_proposer:{suffix}",
    )


def _review(
    ashl_root: str | Path,
    p133: Path,
    p134: Path,
    p137: Path,
    proposal_id: str,
    decision: str,
    *,
    explicit_teacher_action: bool = True,
    teacher_actor: str = "project_owner",
    teacher_role: str = "project_owner",
) -> dict[str, Any]:
    return review_self_state_successor_proposal(
        ashl_root=ashl_root,
        package_133_state_dir=p133,
        package_134_state_dir=p134,
        state_dir=p137,
        proposal_id=proposal_id,
        decision=decision,
        teacher_actor=teacher_actor,
        teacher_role=teacher_role,
        teacher_note=f"Package 137 {decision} control review.",
        explicit_teacher_action=explicit_teacher_action,
    )


@contextmanager
def _authority_copy(
    package_133_state_dir: str | Path,
    package_134_state_dir: str | Path,
) -> Iterator[tuple[Path, Path, Path]]:
    with TemporaryDirectory(prefix="ashl_package_137_control_") as directory:
        root = Path(directory)
        p133 = root / "package_133"
        p134 = root / "package_134"
        p137 = root / "package_137"
        p133.mkdir()
        p134.mkdir()
        p137.mkdir()
        shutil.copytree(
            Path(package_133_state_dir) / PACKAGE_133_DIR,
            p133 / PACKAGE_133_DIR,
        )
        shutil.copytree(
            Path(package_134_state_dir) / PACKAGE_134_DIR,
            p134 / PACKAGE_134_DIR,
        )
        yield p133, p134, p137


def _rejects(call: Callable[[], Any], fragment: str) -> bool:
    try:
        call()
    except (KeyError, RuntimeError, TypeError, ValueError) as error:
        return fragment in str(error)
    return False
