"""CLI, teacher-console, worker, and orchestrator surface inventory."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ashl_core_v1.tools.architecture_repo_scanner import (
    iter_python_files,
    module_path_from_file,
    parse_argparse_commands,
    plain,
    read_text,
    relpath,
    safe_parse_python,
    stable_id,
)


OPERATIONAL_SURFACE_SCHEMA_VERSION = "ashl_architecture_operational_surface_v0"


@dataclass(frozen=True)
class ArchitectureOperationalSurfaceRecord:
    surface_record_id: str
    schema_version: str
    surface_kind: str
    module_path: str
    command_name: str
    bound_callable: str | None
    write_capability: bool
    read_only: bool
    explicit_state_dir_required: bool
    explicit_teacher_action_required: bool
    local_capture_confirmation_required: bool
    tested: bool
    test_files: tuple[str, ...]
    operational_status: str

    def to_dict(self) -> dict[str, Any]:
        return plain(self)


def _callable_for_command(command: str, tree: ast.Module | None) -> str | None:
    if tree is None:
        return None
    normalized = command.replace("-", "_")
    functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    for function in functions:
        if normalized in function:
            return function
    return None


def _teacher_console_functions(tree: ast.Module | None) -> tuple[str, ...]:
    if tree is None:
        return tuple()
    names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and (
            node.name.endswith("_from_guided_cradle_growth_console")
            or node.name.startswith(("growth_", "perception_session_", "sensor_", "audio_"))
        ):
            names.append(node.name)
    return tuple(sorted(set(names)))


def _test_files_for_command(root: Path, module_path: str, command: str) -> tuple[str, ...]:
    module_stem = module_path.split(".")[-1]
    command_norm = command.replace("-", "_")
    matches: list[str] = []
    for test_path in (root / "ashl_core_v1" / "tests").glob("test_*.py"):
        text = read_text(test_path)
        if module_stem in text or command in text or command_norm in text or module_stem.replace("_cli", "") in test_path.name:
            matches.append(relpath(test_path, root))
    return tuple(sorted(set(matches)))


def _read_only(command: str) -> bool:
    return command.startswith(("show", "list", "validate", "audit", "status"))


def _write_capability(command: str) -> bool:
    return command.startswith(("run", "create", "capture", "apply", "decide", "approve", "compile", "retain", "request", "start"))


def build_operational_surface_inventory(repo_root: str | Path) -> tuple[ArchitectureOperationalSurfaceRecord, ...]:
    root = Path(repo_root).resolve()
    records: list[ArchitectureOperationalSurfaceRecord] = []
    for path in iter_python_files(root):
        relative = relpath(path, root)
        if not relative.startswith("ashl_core_v1/"):
            continue
        module_path = module_path_from_file(path, root)
        text = read_text(path)
        tree = safe_parse_python(path)
        commands = parse_argparse_commands(text)
        if module_path.endswith("_cli") or commands:
            for command in commands:
                tests = _test_files_for_command(root, module_path, command)
                payload = {"module": module_path, "command": command, "kind": "CLI"}
                records.append(
                    ArchitectureOperationalSurfaceRecord(
                        surface_record_id=stable_id("architecture_operational_surface", payload),
                        schema_version=OPERATIONAL_SURFACE_SCHEMA_VERSION,
                        surface_kind="CLI",
                        module_path=module_path,
                        command_name=command,
                        bound_callable=_callable_for_command(command, tree),
                        write_capability=_write_capability(command),
                        read_only=_read_only(command),
                        explicit_state_dir_required="--state-dir" in text,
                        explicit_teacher_action_required=any(token in command for token in ("approve", "decide", "review")),
                        local_capture_confirmation_required="--confirm-local-capture" in text,
                        tested=bool(tests),
                        test_files=tests,
                        operational_status="tested" if tests else "untested",
                    )
                )
        if module_path == "ashl_core_v1.runtime.guided_cradle_growth_teacher_console":
            for function in _teacher_console_functions(tree):
                command = function.removesuffix("_from_guided_cradle_growth_console").replace("_", "-")
                tests = _test_files_for_command(root, module_path, command)
                payload = {"module": module_path, "command": command, "kind": "guided_teacher_console"}
                records.append(
                    ArchitectureOperationalSurfaceRecord(
                        surface_record_id=stable_id("architecture_operational_surface", payload),
                        schema_version=OPERATIONAL_SURFACE_SCHEMA_VERSION,
                        surface_kind="guided_teacher_console",
                        module_path=module_path,
                        command_name=command,
                        bound_callable=function,
                        write_capability=_write_capability(command),
                        read_only=_read_only(command),
                        explicit_state_dir_required="state_dir" in text,
                        explicit_teacher_action_required=any(token in command for token in ("approve", "review", "teacher")),
                        local_capture_confirmation_required="confirm" in function or "capture" in command,
                        tested=bool(tests),
                        test_files=tests,
                        operational_status="tested" if tests else "untested",
                    )
                )
        if module_path.endswith("_worker") or module_path.endswith("_run"):
            kind = "worker" if module_path.endswith("_worker") else "orchestrator"
            tests = _test_files_for_command(root, module_path, module_path.split(".")[-1])
            payload = {"module": module_path, "command": module_path.split(".")[-1], "kind": kind}
            records.append(
                ArchitectureOperationalSurfaceRecord(
                    surface_record_id=stable_id("architecture_operational_surface", payload),
                    schema_version=OPERATIONAL_SURFACE_SCHEMA_VERSION,
                    surface_kind=kind,
                    module_path=module_path,
                    command_name=module_path.split(".")[-1],
                    bound_callable="main" if "def main" in text else None,
                    write_capability=True,
                    read_only=False,
                    explicit_state_dir_required="state_dir" in text,
                    explicit_teacher_action_required="teacher" in text,
                    local_capture_confirmation_required="confirm" in text,
                    tested=bool(tests),
                    test_files=tests,
                    operational_status="tested" if tests else "untested",
                )
            )
    return tuple(sorted(records, key=lambda item: (item.surface_kind, item.module_path, item.command_name)))
