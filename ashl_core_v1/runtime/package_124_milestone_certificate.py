"""Certificate helpers for Package 124 milestone archives."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import canonical_json, stable_id, utc_now
from ashl_core_v1.runtime.package_124_types import (
    PACKAGE_123_CYCLE_1_EVIDENCE_IDENTITY,
    PACKAGE_123_CYCLE_1_SESSION_ID,
    PACKAGE_123_CYCLE_2_SESSION_ID,
    PACKAGE_123_SOURCE_COMMIT,
    PACKAGE_124_CERTIFICATE_SCHEMA_VERSION,
    PACKAGE_124_EXCLUDED_CLAIMS,
    PACKAGE_124_MILESTONE_ID,
    PACKAGE_124_SAFE_CLAIM,
    Package124MilestoneCertificate,
    certificate_sha256,
)


CERTIFICATE_FILENAME = "package_124_milestone_certificate.json"


def build_package_124_certificate(
    *,
    source_audit: dict[str, Any],
    archive_manifest_sha256: str,
    provenance_graph_sha256: str,
) -> Package124MilestoneCertificate:
    identity = dict(source_audit.get("identity") or {})
    audit = dict(source_audit.get("audit") or {})
    payload = {
        "certificate_id": stable_id("package_124_milestone_certificate"),
        "schema_version": PACKAGE_124_CERTIFICATE_SCHEMA_VERSION,
        "created_at": utc_now(),
        "milestone_id": PACKAGE_124_MILESTONE_ID,
        "source_audit_id": str(audit.get("audit_id") or ""),
        "source_identity_hash": str(identity.get("identity_hash") or ""),
        "archive_manifest_sha256": archive_manifest_sha256,
        "provenance_graph_sha256": provenance_graph_sha256,
        "package_123_commit": PACKAGE_123_SOURCE_COMMIT,
        "cycle_1_session_id": PACKAGE_123_CYCLE_1_SESSION_ID,
        "cycle_1_evidence_identity": PACKAGE_123_CYCLE_1_EVIDENCE_IDENTITY,
        "cycle_2_session_id": PACKAGE_123_CYCLE_2_SESSION_ID,
        "capability_claim": PACKAGE_124_SAFE_CLAIM,
        "excluded_claims": PACKAGE_124_EXCLUDED_CLAIMS,
        "certificate_sha256": "",
    }
    payload["certificate_sha256"] = certificate_sha256(payload)
    return Package124MilestoneCertificate(**payload)


def write_package_124_certificate(certificate: Package124MilestoneCertificate, archive_dir: str | Path) -> Path:
    path = Path(archive_dir) / CERTIFICATE_FILENAME
    path.write_text(canonical_json(certificate.to_dict()), encoding="utf-8")
    return path


def load_package_124_certificate(archive_dir: str | Path) -> Package124MilestoneCertificate:
    path = Path(archive_dir) / CERTIFICATE_FILENAME
    return Package124MilestoneCertificate(**json.loads(path.read_text(encoding="utf-8")))


def validate_package_124_certificate(archive_dir: str | Path) -> dict[str, object]:
    try:
        certificate = load_package_124_certificate(archive_dir)
    except Exception as error:
        return {"valid": False, "status": "certificate_missing_or_invalid", "failure_reasons": (str(error),)}
    reasons: list[str] = []
    if certificate.milestone_id != PACKAGE_124_MILESTONE_ID:
        reasons.append("milestone_id_mismatch")
    if certificate.package_123_commit != PACKAGE_123_SOURCE_COMMIT:
        reasons.append("package_123_commit_mismatch")
    if certificate.cycle_1_session_id != PACKAGE_123_CYCLE_1_SESSION_ID:
        reasons.append("cycle_1_session_mismatch")
    if certificate.cycle_1_evidence_identity != PACKAGE_123_CYCLE_1_EVIDENCE_IDENTITY:
        reasons.append("cycle_1_evidence_identity_mismatch")
    if certificate.cycle_2_session_id != PACKAGE_123_CYCLE_2_SESSION_ID:
        reasons.append("cycle_2_session_mismatch")
    if certificate_sha256(certificate.to_dict()) != certificate.certificate_sha256:
        reasons.append("certificate_sha256_mismatch")
    if "consciousness" not in tuple(certificate.excluded_claims):
        reasons.append("missing_excluded_claims")
    return {
        "valid": not reasons,
        "status": "certificate_valid" if not reasons else "certificate_invalid",
        "failure_reasons": tuple(reasons),
        "certificate_id": certificate.certificate_id,
        "certificate_sha256": certificate.certificate_sha256,
    }
