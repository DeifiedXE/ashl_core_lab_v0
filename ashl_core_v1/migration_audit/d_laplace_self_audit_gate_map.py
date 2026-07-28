"""Coverage map for the twelve D-Laplace self-deception gates."""

from __future__ import annotations

import json

from ashl_core_v1.migration_audit.d_laplace_qm0_types import (
    DLaplaceModuleInventoryRecord,
    DLaplaceSelfAuditGateCoverageRecord,
    DLaplaceSourceFileRecord,
    stable_id,
)
from ashl_core_v1.migration_audit.d_laplace_source_reader import (
    ReadOnlyDLaplaceSource,
)


GATE_DEFINITIONS = (
    (1, "semantic family false emergence", ("family", "analysis_tag", "template")),
    (2, "primitive answer leakage", ("primitive", "authorization", "template")),
    (3, "uninterpretable null", ("positive_control", "reference", "fail_search")),
    (4, "multiple-comparison false success", ("locked", "top_1", "pool")),
    (
        5,
        "incomplete search-space overclaim",
        ("frontier", "search_space", "budget_exhausted"),
    ),
    (6, "reference co-failure", ("reference", "expander", "invariant")),
    (7, "NOT_RUN represented as zero", ("not_run", "collision", "holdout")),
    (
        8,
        "concentrated data represented as rich",
        ("concentration", "entropy", "corpus"),
    ),
    (
        9,
        "score-scale induced false organ difference",
        ("calibration", "score", "cost_sensitivity"),
    ),
    (
        10,
        "statistical pseudo-replication",
        ("bootstrap", "permutation", "effective_n"),
    ),
    (11, "action-bid degeneration", ("bid", "abstain", "stake", "credit")),
    (
        12,
        "coarse scale erasing intermediate states",
        ("lineage", "turnover", "reallocation", "hybrid"),
    ),
)


def _matches(haystack: str, keywords: tuple[str, ...]) -> bool:
    folded = haystack.casefold().replace("-", "_").replace(" ", "_")
    return any(keyword in folded for keyword in keywords)


def _validated_output_refs(
    source: ReadOnlyDLaplaceSource | None,
    file_records: tuple[DLaplaceSourceFileRecord, ...],
    keywords: tuple[str, ...],
) -> tuple[str, ...]:
    if source is None:
        return ()
    result: list[str] = []
    for record in file_records:
        if (
            record.source_role != "archived_output"
            or record.size_bytes > 2 * 1024 * 1024
            or record.file_kind not in {".json", ".md", ".txt", ".csv", ".log"}
            or not _matches(record.relative_path, keywords)
        ):
            continue
        try:
            text = source.read_text(
                record.relative_path,
                maximum_bytes=2 * 1024 * 1024,
            )
            if record.file_kind == ".json":
                json.loads(text)
            elif not _matches(text, keywords):
                continue
        except (OSError, UnicodeError, ValueError):
            continue
        result.append(record.source_file_record_id)
        if len(result) == 20:
            break
    return tuple(result)


def build_self_audit_gate_map(
    *,
    file_records: tuple[DLaplaceSourceFileRecord, ...],
    modules: tuple[DLaplaceModuleInventoryRecord, ...],
    authoritative_document_refs: tuple[str, ...],
    source: ReadOnlyDLaplaceSource | None = None,
) -> tuple[DLaplaceSelfAuditGateCoverageRecord, ...]:
    requirement_refs = tuple(
        path
        for path in authoritative_document_refs
        if path.endswith(
            (
                "04_FAILURES_AND_CORRECTIONS.md",
                "06A_QINGYIN_SELF_AUDIT_ENGINE_REQUIREMENTS.md",
            )
        )
    )
    records: list[DLaplaceSelfAuditGateCoverageRecord] = []
    for number, name, keywords in GATE_DEFINITIONS:
        implementation_refs = tuple(
            sorted(
                module.module_record_id
                for module in modules
                if "/tests/" not in f"/{module.relative_path.casefold()}/"
                and _matches(
                    " ".join((module.relative_path, *module.declared_symbols)),
                    keywords,
                )
            )
        )
        test_refs = tuple(
            sorted(
                module.module_record_id
                for module in modules
                if "/tests/" in f"/{module.relative_path.casefold()}/"
                and _matches(
                    " ".join((module.relative_path, *module.declared_symbols)),
                    keywords,
                )
            )
        )
        output_refs = _validated_output_refs(source, file_records, keywords)
        missing: list[str] = []
        if not requirement_refs:
            missing.append("authoritative_requirement")
        if not implementation_refs:
            missing.append("source_implementation_evidence")
        if not test_refs:
            missing.append("source_test_evidence")
        if not output_refs:
            missing.append("archived_output_evidence")
        if not requirement_refs:
            coverage = "unresolved"
            evidence_status = "INCONCLUSIVE"
        elif not implementation_refs and not test_refs and not output_refs:
            coverage = "source_evidence_absent"
            evidence_status = "documentation_only"
        elif implementation_refs and test_refs and output_refs:
            coverage = "source_evidence_present"
            evidence_status = "bounded_static_source_test_and_output_evidence"
        else:
            coverage = "partial_source_evidence"
            evidence_status = "INCONCLUSIVE"
        payload = {"gate_number": number, "gate_name": name}
        records.append(
            DLaplaceSelfAuditGateCoverageRecord(
                gate_record_id=stable_id("d_laplace_self_audit_gate", payload),
                gate_number=number,
                gate_name=name,
                source_requirement_refs=requirement_refs,
                source_implementation_refs=implementation_refs,
                source_test_refs=test_refs,
                source_output_refs=output_refs,
                source_coverage_status=coverage,
                qingyin_integration_status="not_integrated_qm0_read_only",
                missing_requirements=tuple(missing),
                evidence_status=evidence_status,
                source_trace_refs=tuple(
                    dict.fromkeys(
                        (
                            *requirement_refs,
                            *implementation_refs,
                            *test_refs,
                            *output_refs,
                        )
                    )
                ),
            )
        )
    return tuple(records)
