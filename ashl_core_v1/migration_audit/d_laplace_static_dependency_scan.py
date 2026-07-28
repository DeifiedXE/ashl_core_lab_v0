"""AST-only dependency and executable-authority inventory."""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from pathlib import PurePosixPath

from ashl_core_v1.migration_audit.d_laplace_qm0_types import (
    DLaplaceModuleInventoryRecord,
    DLaplaceSourceFileRecord,
    MigrationContaminationFinding,
    sha256_payload,
    stable_id,
)
from ashl_core_v1.migration_audit.d_laplace_source_reader import (
    ReadOnlyDLaplaceSource,
)


@dataclass(frozen=True)
class DLaplaceDependencyEdge:
    source_module_ref: str
    target_ref: str
    edge_kind: str

    def to_dict(self) -> dict[str, str]:
        return {
            "source_module_ref": self.source_module_ref,
            "target_ref": self.target_ref,
            "edge_kind": self.edge_kind,
        }


@dataclass(frozen=True)
class DLaplaceStaticDependencyScanResult:
    modules: tuple[DLaplaceModuleInventoryRecord, ...]
    edges: tuple[DLaplaceDependencyEdge, ...]
    findings: tuple[MigrationContaminationFinding, ...]


def _module_name(relative_path: str) -> str:
    path = PurePosixPath(relative_path)
    parts = list(path.with_suffix("").parts)
    if "src" in parts:
        parts = parts[parts.index("src") + 1 :]
    if parts and parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def _call_name(node: ast.Call) -> str:
    value: ast.AST = node.func
    parts: list[str] = []
    while isinstance(value, ast.Attribute):
        parts.append(value.attr)
        value = value.value
    if isinstance(value, ast.Name):
        parts.append(value.id)
    return ".".join(reversed(parts))


def _imports(tree: ast.Module) -> tuple[str, ...]:
    result: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            result.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            prefix = "." * node.level
            result.add(prefix + (node.module or ""))
    return tuple(sorted(result))


def _declared_symbols(tree: ast.Module) -> tuple[str, ...]:
    result: set[str] = {
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    }
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Name):
                    result.add(target.id)
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            result.add(node.target.id)
        if isinstance(node, ast.Dict):
            for key in node.keys:
                if (
                    isinstance(key, ast.Constant)
                    and isinstance(key.value, str)
                    and key.value.isidentifier()
                    and len(key.value) <= 80
                ):
                    result.add(f"schema_field:{key.value}")
    return tuple(sorted(result))


def _resolve_relative_import(current: str, imported: str) -> str:
    if not imported.startswith("."):
        return imported
    level = len(imported) - len(imported.lstrip("."))
    tail = imported[level:]
    base = current.split(".")[:-1]
    if level > 1:
        base = base[: -(level - 1)]
    return ".".join(part for part in [*base, tail] if part)


def _top_level_calls(tree: ast.Module) -> tuple[ast.Call, ...]:
    result: list[ast.Call] = []
    for node in tree.body:
        if isinstance(node, ast.If) and _is_main_guard(node):
            continue
        values: list[ast.AST] = []
        if isinstance(node, ast.Expr):
            values.append(node.value)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            value = getattr(node, "value", None)
            if value is not None:
                values.append(value)
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            values.extend(item.context_expr for item in node.items)
        for value in values:
            result.extend(item for item in ast.walk(value) if isinstance(item, ast.Call))
    return tuple(result)


def _is_main_guard(node: ast.If) -> bool:
    try:
        return (
            isinstance(node.test, ast.Compare)
            and isinstance(node.test.left, ast.Name)
            and node.test.left.id == "__name__"
            and any(
                isinstance(comparator, ast.Constant)
                and comparator.value == "__main__"
                for comparator in node.test.comparators
            )
        )
    except AttributeError:
        return False


def _enclosing_symbols(tree: ast.Module) -> dict[int, str | None]:
    result: dict[int, str | None] = {}

    class Visitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.stack: list[str] = []

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            self.stack.append(node.name)
            self.generic_visit(node)
            self.stack.pop()

        visit_AsyncFunctionDef = visit_FunctionDef

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            self.stack.append(node.name)
            self.generic_visit(node)
            self.stack.pop()

        def visit_Call(self, node: ast.Call) -> None:
            result[id(node)] = ".".join(self.stack) if self.stack else None
            self.generic_visit(node)

    Visitor().visit(tree)
    return result


def _line_range(node: ast.AST) -> str:
    return f"L{getattr(node, 'lineno', 0)}-L{getattr(node, 'end_lineno', getattr(node, 'lineno', 0))}"


def _finding(
    *,
    category: str,
    severity: str,
    relative_path: str,
    symbol_name: str | None,
    node: ast.AST,
    source_text: str,
    migration_effect: str,
    explanation: str,
    module_record_id: str,
) -> MigrationContaminationFinding:
    excerpt = ast.get_source_segment(source_text, node) or ast.dump(node)
    payload = {
        "category": category,
        "relative_path": relative_path,
        "symbol_name": symbol_name,
        "line_range": _line_range(node),
        "excerpt_hash": sha256_payload(excerpt),
    }
    return MigrationContaminationFinding(
        finding_id=stable_id("d_laplace_contamination_finding", payload),
        category=category,
        severity=severity,
        relative_path=relative_path,
        symbol_name=symbol_name,
        line_range=_line_range(node),
        evidence_excerpt_hash=sha256_payload(excerpt),
        finding_status="confirmed_dataflow_or_authority_finding",
        migration_effect=migration_effect,
        explanation=explanation,
        source_trace_refs=(module_record_id,),
    )


def _call_authority_findings(
    *,
    tree: ast.Module,
    source_text: str,
    relative_path: str,
    module_record_id: str,
) -> tuple[MigrationContaminationFinding, ...]:
    findings: list[MigrationContaminationFinding] = []
    symbols = _enclosing_symbols(tree)
    write_methods = {
        "write_text",
        "write_bytes",
        "mkdir",
        "unlink",
        "rmdir",
        "rename",
        "replace",
        "copy",
        "copy2",
        "move",
        "rmtree",
        "dump",
    }
    process_roots = {"subprocess", "os.system", "os.popen", "Popen"}
    network_roots = {
        "requests",
        "httpx",
        "urllib",
        "urlopen",
        "socket",
        "aiohttp",
    }
    unsafe_loaders = {
        "pickle.load",
        "pickle.loads",
        "dill.load",
        "dill.loads",
        "joblib.load",
        "torch.load",
    }
    environment_calls = {"os.putenv", "os.unsetenv"}
    seed_calls = {"random.seed", "numpy.random.seed", "np.random.seed"}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _call_name(node)
        symbol = symbols.get(id(node))
        final = name.rsplit(".", 1)[-1]
        if name in {"open", "Path.open"} or final == "open":
            mode = ""
            if len(node.args) > 1 and isinstance(node.args[1], ast.Constant):
                mode = str(node.args[1].value)
            for keyword in node.keywords:
                if keyword.arg == "mode" and isinstance(keyword.value, ast.Constant):
                    mode = str(keyword.value.value)
            if any(flag in mode for flag in ("w", "a", "x", "+")):
                findings.append(
                    _finding(
                        category="filesystem_write_authority",
                        severity="blocking_for_direct_migration",
                        relative_path=relative_path,
                        symbol_name=symbol,
                        node=node,
                        source_text=source_text,
                        migration_effect="forbidden_direct_migration",
                        explanation="AST call opens a filesystem target with a write-capable mode.",
                        module_record_id=module_record_id,
                    )
                )
        if final in write_methods:
            findings.append(
                _finding(
                    category="filesystem_write_authority",
                    severity="blocking_for_direct_migration",
                    relative_path=relative_path,
                    symbol_name=symbol,
                    node=node,
                    source_text=source_text,
                    migration_effect="forbidden_direct_migration",
                    explanation=f"AST call exposes filesystem mutation through {name}.",
                    module_record_id=module_record_id,
                )
            )
        if any(name == root or name.startswith(root + ".") for root in process_roots):
            findings.append(
                _finding(
                    category="process_or_shell_authority",
                    severity="blocking_for_direct_migration",
                    relative_path=relative_path,
                    symbol_name=symbol,
                    node=node,
                    source_text=source_text,
                    migration_effect="research_harness_only_and_isolated",
                    explanation=f"AST call can launch a process or shell through {name}.",
                    module_record_id=module_record_id,
                )
            )
        if any(
            name == root or name.startswith(root + ".") for root in network_roots
        ):
            findings.append(
                _finding(
                    category="network_authority",
                    severity="blocking_for_direct_migration",
                    relative_path=relative_path,
                    symbol_name=symbol,
                    node=node,
                    source_text=source_text,
                    migration_effect="forbidden_direct_migration",
                    explanation=f"AST call exposes network authority through {name}.",
                    module_record_id=module_record_id,
                )
            )
        if name in unsafe_loaders:
            findings.append(
                _finding(
                    category="unsafe_serialized_execution",
                    severity="blocking_for_qm1",
                    relative_path=relative_path,
                    symbol_name=symbol,
                    node=node,
                    source_text=source_text,
                    migration_effect="forbidden_direct_migration",
                    explanation=f"AST call loads executable serialized content through {name}.",
                    module_record_id=module_record_id,
                )
            )
        if name in environment_calls:
            findings.append(
                _finding(
                    category="absolute_mutation_authority",
                    severity="blocking_for_direct_migration",
                    relative_path=relative_path,
                    symbol_name=symbol,
                    node=node,
                    source_text=source_text,
                    migration_effect="environment_mutation_must_be_removed",
                    explanation=f"AST call mutates process environment through {name}.",
                    module_record_id=module_record_id,
                )
            )
        if name in seed_calls:
            findings.append(
                _finding(
                    category="absolute_mutation_authority",
                    severity="caution",
                    relative_path=relative_path,
                    symbol_name=symbol,
                    node=node,
                    source_text=source_text,
                    migration_effect="global_seed_mutation_requires_isolation",
                    explanation=f"AST call mutates global random state through {name}.",
                    module_record_id=module_record_id,
                )
            )
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        for target in targets:
            expression = ast.dump(target)
            if "Attribute(value=Name(id='os'" in expression and "attr='environ'" in expression:
                findings.append(
                    _finding(
                        category="absolute_mutation_authority",
                        severity="blocking_for_direct_migration",
                        relative_path=relative_path,
                        symbol_name=None,
                        node=node,
                        source_text=source_text,
                        migration_effect="environment_mutation_must_be_removed",
                        explanation="AST assignment mutates os.environ state.",
                        module_record_id=module_record_id,
                    )
                )
    return tuple(findings)


def scan_static_dependencies(
    source: ReadOnlyDLaplaceSource,
    file_records: tuple[DLaplaceSourceFileRecord, ...],
) -> DLaplaceStaticDependencyScanResult:
    python_records = tuple(
        record
        for record in file_records
        if record.included_in_semantic_scan and record.file_kind == ".py"
    )
    module_names = {
        _module_name(record.relative_path): record.relative_path
        for record in python_records
    }
    modules: list[DLaplaceModuleInventoryRecord] = []
    edges: list[DLaplaceDependencyEdge] = []
    findings: list[MigrationContaminationFinding] = []
    for record in python_records:
        relative_path = record.relative_path
        name = _module_name(relative_path)
        source_text = source.read_text(relative_path)
        module_id = stable_id(
            "d_laplace_module",
            {"relative_path": relative_path, "sha256": record.sha256},
        )
        try:
            tree = ast.parse(source_text, filename=relative_path)
        except SyntaxError as error:
            finding = MigrationContaminationFinding(
                finding_id=stable_id(
                    "d_laplace_contamination_finding",
                    {"path": relative_path, "syntax_error": str(error)},
                ),
                category="source_boundary_ambiguity",
                severity="blocking_for_qm1",
                relative_path=relative_path,
                symbol_name=None,
                line_range=f"L{error.lineno or 0}-L{error.lineno or 0}",
                evidence_excerpt_hash=sha256_payload(str(error)),
                finding_status="unresolved",
                migration_effect="unresolved",
                explanation="Python source could not be parsed statically.",
                source_trace_refs=(record.source_file_record_id,),
            )
            findings.append(finding)
            modules.append(
                DLaplaceModuleInventoryRecord(
                    module_record_id=module_id,
                    relative_path=relative_path,
                    declared_symbols=(),
                    imported_modules=(),
                    local_dependency_refs=(),
                    external_dependency_refs=(),
                    detected_entry_points=(),
                    import_time_side_effect_risk=False,
                    runtime_candidate=False,
                    evidence_status="syntax_error_unresolved",
                    source_trace_refs=(record.source_file_record_id,),
                )
            )
            continue
        imported = _imports(tree)
        local_refs: set[str] = set()
        external_refs: set[str] = set()
        for item in imported:
            resolved = _resolve_relative_import(name, item)
            matched = next(
                (
                    local_name
                    for local_name in module_names
                    if resolved == local_name
                    or resolved.startswith(local_name + ".")
                    or local_name.startswith(resolved + ".")
                ),
                None,
            )
            if matched:
                local_refs.add(
                    stable_id(
                        "d_laplace_module",
                        {
                            "relative_path": module_names[matched],
                            "sha256": next(
                                row.sha256
                                for row in python_records
                                if row.relative_path == module_names[matched]
                            ),
                        },
                    )
                )
            else:
                root = resolved.split(".", 1)[0]
                if root and root not in sys.stdlib_module_names:
                    external_refs.add(resolved)
        declared = _declared_symbols(tree)
        top_calls = _top_level_calls(tree)
        entry_points = tuple(
            sorted(
                {
                    "module_main_guard"
                    for node in tree.body
                    if isinstance(node, ast.If) and _is_main_guard(node)
                }
                | {symbol for symbol in declared if symbol == "main" or symbol.startswith("cmd_")}
            )
        )
        module = DLaplaceModuleInventoryRecord(
            module_record_id=module_id,
            relative_path=relative_path,
            declared_symbols=declared,
            imported_modules=imported,
            local_dependency_refs=tuple(sorted(local_refs)),
            external_dependency_refs=tuple(sorted(external_refs)),
            detected_entry_points=entry_points,
            import_time_side_effect_risk=bool(top_calls),
            runtime_candidate=False,
            evidence_status="source_code_ast_parsed",
            source_trace_refs=(record.source_file_record_id,),
        )
        modules.append(module)
        for target in local_refs:
            edges.append(DLaplaceDependencyEdge(module_id, target, "local_import"))
        for target in external_refs:
            edges.append(DLaplaceDependencyEdge(module_id, target, "external_import"))
        if top_calls:
            for call in top_calls:
                findings.append(
                    _finding(
                        category="import_time_side_effect",
                        severity="caution",
                        relative_path=relative_path,
                        symbol_name=None,
                        node=call,
                        source_text=source_text,
                        migration_effect="requires_manual_import_boundary_review",
                        explanation="A top-level executable call is present outside a main guard.",
                        module_record_id=module_id,
                    )
                )
        for node in tree.body:
            if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                continue
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            names = [
                target.id
                for target in targets
                if isinstance(target, ast.Name)
            ]
            if any("registry" in item.casefold() for item in names):
                findings.append(
                    _finding(
                        category="other",
                        severity="caution",
                        relative_path=relative_path,
                        symbol_name=names[0] if names else None,
                        node=node,
                        source_text=source_text,
                        migration_effect="global_registry_requires_explicit_scope",
                        explanation="AST declares mutable registry-like global state.",
                        module_record_id=module_id,
                    )
                )
        findings.extend(
            _call_authority_findings(
                tree=tree,
                source_text=source_text,
                relative_path=relative_path,
                module_record_id=module_id,
            )
        )
    return DLaplaceStaticDependencyScanResult(
        modules=tuple(sorted(modules, key=lambda item: item.relative_path.casefold())),
        edges=tuple(
            sorted(
                edges,
                key=lambda item: (
                    item.source_module_ref,
                    item.target_ref,
                    item.edge_kind,
                ),
            )
        ),
        findings=tuple(sorted(findings, key=lambda item: item.finding_id)),
    )
