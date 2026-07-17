"""Architectural test coverage mapper for Package 122A."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ashl_core_v1.tools.architecture_repo_scanner import (
    iter_python_files,
    module_path_from_file,
    plain,
    read_text,
    relpath,
    stable_id,
)


TEST_COVERAGE_SCHEMA_VERSION = "ashl_architecture_test_coverage_v0"


@dataclass(frozen=True)
class ArchitectureTestCoverageRecord:
    coverage_record_id: str
    schema_version: str
    module_path: str
    direct_test_files: tuple[str, ...]
    integration_test_files: tuple[str, ...]
    real_hardware_smoke_files: tuple[str, ...]
    positive_case_count: int
    negative_case_count: int
    cross_process_tested: bool
    real_hardware_tested: bool
    rollback_tested: bool
    lineage_tested: bool
    coverage_status: str
    missing_test_kinds: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return plain(self)


def _case_counts(text: str) -> tuple[int, int]:
    positive = text.count("assert") + text.count("self.assert")
    negative_tokens = ("reject", "block", "fail", "invalid", "missing", "wrong", "tamper", "no_")
    negative = sum(text.lower().count(token) for token in negative_tokens)
    return positive, negative


def build_test_coverage_map(repo_root: str | Path) -> tuple[ArchitectureTestCoverageRecord, ...]:
    root = Path(repo_root).resolve()
    modules = [
        path
        for path in iter_python_files(root)
        if relpath(path, root).startswith("ashl_core_v1/")
        and not relpath(path, root).startswith("ashl_core_v1/tests/")
    ]
    tests = sorted((root / "ashl_core_v1" / "tests").glob("test_*.py"), key=lambda item: item.as_posix())
    test_texts = {test_path: read_text(test_path) for test_path in tests}
    records: list[ArchitectureTestCoverageRecord] = []
    for module_path_file in modules:
        module_path = module_path_from_file(module_path_file, root)
        stem = module_path_file.stem
        direct: list[str] = []
        integration: list[str] = []
        real_smoke: list[str] = []
        positive = 0
        negative = 0
        flags = {
            "cross_process": False,
            "real_hardware": False,
            "rollback": False,
            "lineage": False,
        }
        for test_path, text in test_texts.items():
            test_rel = relpath(test_path, root)
            direct_match = test_path.stem == f"test_{stem}" or test_path.stem.endswith(stem)
            import_match = module_path in text or stem in text
            if direct_match:
                direct.append(test_rel)
            elif import_match:
                integration.append(test_rel)
            if direct_match or import_match:
                p_count, n_count = _case_counts(text)
                positive += p_count
                negative += n_count
                lower = text.lower()
                flags["cross_process"] = flags["cross_process"] or "process" in lower or "subprocess" in lower
                flags["real_hardware"] = flags["real_hardware"] or "real_" in lower or "hardware" in lower or "smoke" in lower
                flags["rollback"] = flags["rollback"] or "rollback" in lower or "rolled_back" in lower
                flags["lineage"] = flags["lineage"] or "lineage" in lower or "source_trace_refs" in lower
                if "real_" in lower or "smoke" in lower:
                    real_smoke.append(test_rel)
        missing: list[str] = []
        if not direct and not integration:
            missing.append("direct_or_integration_test")
        if negative == 0:
            missing.append("negative_controls")
        status = "verified_by_tests" if (direct or integration) else "missing_tests"
        if missing and (direct or integration):
            status = "partial_architectural_coverage"
        payload = {"module_path": module_path, "direct": direct, "integration": integration}
        records.append(
            ArchitectureTestCoverageRecord(
                coverage_record_id=stable_id("architecture_test_coverage", payload),
                schema_version=TEST_COVERAGE_SCHEMA_VERSION,
                module_path=module_path,
                direct_test_files=tuple(sorted(set(direct))),
                integration_test_files=tuple(sorted(set(integration))),
                real_hardware_smoke_files=tuple(sorted(set(real_smoke))),
                positive_case_count=positive,
                negative_case_count=negative,
                cross_process_tested=flags["cross_process"],
                real_hardware_tested=flags["real_hardware"],
                rollback_tested=flags["rollback"],
                lineage_tested=flags["lineage"],
                coverage_status=status,
                missing_test_kinds=tuple(sorted(set(missing))),
            )
        )
    return tuple(sorted(records, key=lambda item: item.module_path))
