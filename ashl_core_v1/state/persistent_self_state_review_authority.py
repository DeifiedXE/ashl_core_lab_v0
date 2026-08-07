"""Source-grounded adapter to the existing explicit teacher-review authority."""

from __future__ import annotations

from pathlib import Path

from ashl_core_v1.runtime.host_sensor_types import sha256_bytes, sha256_payload, utc_now
from ashl_core_v1.runtime.teacher_gated_session_store import ALLOWED_DECISIONS
from ashl_core_v1.state.cradle_state_resume_selection_authorization import (
    ALLOWED_TEACHER_ACTORS,
    ALLOWED_TEACHER_ROLES,
)
from ashl_core_v1.state.persistent_self_state_review_types import (
    ALLOWED_REVIEW_DECISIONS,
    TEACHER_AUTHORITY,
    TEACHER_BINDING_SCHEMA_VERSION,
    ExistingTeacherReviewAuthorityBindingRecord,
)


_SOURCE_SPECS = (
    (
        "ashl_core_v1.state.cradle_state_resume_selection_authorization",
        "ashl_core_v1/state/cradle_state_resume_selection_authorization.py",
        (
            "ALLOWED_TEACHER_ACTORS",
            "ALLOWED_TEACHER_ROLES",
            "TeacherResumeAuthorizationRecord",
            "validate_teacher_resume_authorization",
        ),
    ),
    (
        "ashl_core_v1.runtime.teacher_gated_session_resume_commit",
        "ashl_core_v1/runtime/teacher_gated_session_resume_commit.py",
        (
            "TeacherDecisionRecord",
            "validate_teacher_decision_record",
            "explicit_teacher_action",
            "explicit_target_binding",
        ),
    ),
    (
        "ashl_core_v1.runtime.teacher_gated_session_store",
        "ashl_core_v1/runtime/teacher_gated_session_store.py",
        ("ALLOWED_DECISIONS", "FINAL_DECISIONS", "teacher_decisions"),
    ),
)


def build_existing_teacher_review_authority_binding(
    ashl_root: str | Path,
    *,
    created_at: str | None = None,
) -> ExistingTeacherReviewAuthorityBindingRecord:
    root = Path(ashl_root).resolve()
    module_refs: list[str] = []
    source_hashes: list[str] = []
    symbol_refs: list[str] = []
    source_refs: list[str] = []
    for module_ref, relative_path, symbols in _SOURCE_SPECS:
        path = root / relative_path
        if not path.is_file():
            raise FileNotFoundError(path)
        text = path.read_text(encoding="utf-8")
        missing = tuple(symbol for symbol in symbols if symbol not in text)
        if missing:
            raise RuntimeError(
                f"blocked_existing_teacher_authority_symbols_missing:{relative_path}:{missing}"
            )
        digest = sha256_bytes(path.read_bytes())
        module_refs.append(module_ref)
        source_hashes.append(digest)
        symbol_refs.extend(f"{module_ref}.{symbol}" for symbol in symbols)
        source_refs.append(f"source_file:{digest}")
    if not set(ALLOWED_REVIEW_DECISIONS).issubset(ALLOWED_DECISIONS):
        raise RuntimeError("blocked_existing_teacher_decision_vocabulary_incompatible")
    payload = {
        "authority_binding_id": "",
        "authority_binding_sha256": "",
        "schema_version": TEACHER_BINDING_SCHEMA_VERSION,
        "created_at": created_at or utc_now(),
        "source_engine": "state_engine",
        "teacher_authority": TEACHER_AUTHORITY,
        "source_module_refs": tuple(module_refs),
        "source_file_sha256s": tuple(source_hashes),
        "required_symbol_refs": tuple(symbol_refs),
        "allowed_teacher_actors": tuple(sorted(ALLOWED_TEACHER_ACTORS)),
        "allowed_teacher_roles": tuple(sorted(ALLOWED_TEACHER_ROLES)),
        "allowed_review_decisions": ALLOWED_REVIEW_DECISIONS,
        "explicit_teacher_action_required": True,
        "exact_target_binding_required": True,
        "existing_teacher_authority_reused": True,
        "second_teacher_system_created": False,
        "learning_approval_scope_reused": False,
        "binding_status": "bound_to_existing_state_engine_teacher_review_authority",
        "source_record_refs": tuple(source_refs),
    }
    identity = dict(payload)
    identity.pop("authority_binding_id")
    identity.pop("authority_binding_sha256")
    identity.pop("created_at")
    digest = sha256_payload(identity)
    payload["authority_binding_sha256"] = digest
    payload["authority_binding_id"] = f"self_state_teacher_authority_binding:{digest[:16]}"
    return ExistingTeacherReviewAuthorityBindingRecord(**payload)


def teacher_identity_allowed(actor: str, role: str) -> bool:
    return actor in ALLOWED_TEACHER_ACTORS and role in ALLOWED_TEACHER_ROLES
