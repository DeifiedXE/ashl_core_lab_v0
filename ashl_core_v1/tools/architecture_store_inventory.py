"""SQLite and append-only store inventory for Package 122A."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ashl_core_v1.tools.architecture_repo_scanner import (
    iter_python_files,
    module_path_from_file,
    parse_sqlite_tables,
    plain,
    read_text,
    relpath,
    safe_parse_python,
    stable_id,
)


STORE_SURFACE_SCHEMA_VERSION = "ashl_architecture_store_surface_v0"


@dataclass(frozen=True)
class ArchitectureStoreSurfaceRecord:
    store_record_id: str
    schema_version: str
    store_module: str
    database_path_pattern: str
    table_names: tuple[str, ...]
    immutable_table_names: tuple[str, ...]
    mutable_table_names: tuple[str, ...]
    write_callables: tuple[str, ...]
    read_callables: tuple[str, ...]
    delete_callables: tuple[str, ...]
    explicit_state_dir_required: bool
    append_only_claimed: bool
    append_only_enforced: bool
    upstream_modules: tuple[str, ...]
    downstream_modules: tuple[str, ...]
    store_role: str
    store_risks: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return plain(self)


def _public_functions(tree: ast.Module | None) -> tuple[str, ...]:
    if tree is None:
        return tuple()
    functions: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
            functions.append(node.name)
    return tuple(sorted(set(functions)))


def _filename_pattern(text: str) -> str:
    names = re.findall(r"([A-Z_]*FILENAME)\s*=\s*[\"']([^\"']+)[\"']", text)
    if not names:
        return "<state_dir>/<store>/unknown.sqlite3"
    return "/".join(value for _, value in names)


def _role(module_path: str) -> str:
    if "teacher_gated_session_store" in module_path:
        return "teacher-gated session store"
    if "content_addressed_sensor_artifact_store" in module_path:
        return "sensor artifact store"
    if "perception_primitive_store" in module_path:
        return "perception primitive store"
    if "bounded_multimodal_perception_session_runtime" in module_path:
        return "multimodal session store"
    if "audio_artifact_deletion" in module_path:
        return "audio deletion governance tables"
    return "sqlite store"


def build_store_surface_inventory(repo_root: str | Path) -> tuple[ArchitectureStoreSurfaceRecord, ...]:
    root = Path(repo_root).resolve()
    records: list[ArchitectureStoreSurfaceRecord] = []
    for path in iter_python_files(root):
        if not relpath(path, root).startswith("ashl_core_v1/"):
            continue
        text = read_text(path)
        tables = parse_sqlite_tables(text)
        if not tables and "sqlite3" not in text:
            continue
        module_path = module_path_from_file(path, root)
        tree = safe_parse_python(path)
        functions = _public_functions(tree)
        write_callables = tuple(
            function
            for function in functions
            if function.startswith(("append", "create", "record", "apply", "request", "persist", "insert"))
        )
        read_callables = tuple(
            function
            for function in functions
            if function.startswith(("get", "list", "load", "validate", "show", "audit", "find"))
        )
        delete_callables = tuple(
            function
            for function in functions
            if "delete" in function or function.startswith(("remove", "unlink"))
        )
        update_sql = bool(re.search(r"\bUPDATE\s+", text, flags=re.IGNORECASE))
        delete_sql = bool(re.search(r"\bDELETE\s+FROM\s+", text, flags=re.IGNORECASE))
        immutable = tuple(table for table in tables if not update_sql and "metadata" not in table)
        mutable = tuple(table for table in tables if table not in immutable)
        explicit_state_dir = "state_dir is required" in text or "explicit state_dir" in text or "state_dir:" in text
        append_claimed = "append-only" in text.lower() or any(function.startswith("append") for function in functions)
        append_enforced = append_claimed and not update_sql and not delete_sql
        risks: list[str] = []
        if delete_callables:
            risks.append("delete_callable_present_review_required")
        if append_claimed and not append_enforced:
            risks.append("append_only_claim_has_mutating_sql_or_delete_api")
        if not explicit_state_dir:
            risks.append("explicit_state_dir_not_obvious")
        payload = {"module": module_path, "tables": tables}
        records.append(
            ArchitectureStoreSurfaceRecord(
                store_record_id=stable_id("architecture_store_surface", payload),
                schema_version=STORE_SURFACE_SCHEMA_VERSION,
                store_module=module_path,
                database_path_pattern=_filename_pattern(text),
                table_names=tables,
                immutable_table_names=immutable,
                mutable_table_names=mutable,
                write_callables=write_callables,
                read_callables=read_callables,
                delete_callables=delete_callables,
                explicit_state_dir_required=explicit_state_dir,
                append_only_claimed=append_claimed,
                append_only_enforced=append_enforced,
                upstream_modules=tuple(),
                downstream_modules=tuple(),
                store_role=_role(module_path),
                store_risks=tuple(sorted(risks)),
            )
        )
    return tuple(sorted(records, key=lambda item: item.store_module))
