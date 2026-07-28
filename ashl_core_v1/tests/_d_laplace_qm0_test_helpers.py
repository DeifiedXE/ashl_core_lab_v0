from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from ashl_core_v1.migration_audit.d_laplace_source_manifest import (
    AUTHORITATIVE_DOCUMENT_NAMES,
)


STATUS_TEXT = """
D-LAPLACE PROJECT v1
SYNTHETIC PHASE: COMPLETED
REAL-WORLD R TRACK: NOT ENTERED
PRIMITIVE-AUTHORIZATION DEPTH: UNRESOLVED
OVERALL SCOPE: SYNTHETIC RESEARCH CLOSED
"""


def build_complete_source(root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    for name in AUTHORITATIVE_DOCUMENT_NAMES:
        body = STATUS_TEXT
        if name == "06_QINGYIN_MIGRATION_BLUEPRINT.md":
            body += "\nCost quota anonymous registry lineage snapshot rollback Q-M0 Q-M1\n"
        if name == "06A_QINGYIN_SELF_AUDIT_ENGINE_REQUIREMENTS.md":
            body += """
1 family analysis tag template
2 primitive authorization template
3 positive control reference fail search
4 locked top_1 pool
5 frontier search_space budget_exhausted
6 reference expander invariant
7 NOT_RUN collision holdout
8 concentration entropy corpus
9 calibration score cost_sensitivity
10 bootstrap permutation effective_n
11 bid abstain stake credit
12 lineage turnover reallocation hybrid
QINGYIN_MIGRATION_INCOMPLETE_AUDIT_LAYER
"""
        (root / name).write_text(body, encoding="utf-8")
    package = root / "src" / "dlp"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "core.py").write_text(
        """
import json
import numpy
from .registry import Registry

DEFAULT = dict(enabled=True)
GLOBAL_REGISTRY = {}

def main():
    return Registry()
""",
        encoding="utf-8",
    )
    (package / "registry.py").write_text(
        """
class IdAllocator:
    def allocate_anonymous_organ(self):
        return "organ-0001"

class Registry:
    def add_candidate(self, parent_id=None):
        return {"lineage": {"parent_id": parent_id, "ancestor_ids": []}}
""",
        encoding="utf-8",
    )
    (package / "snapshot.py").write_text(
        """
import shutil

def create_snapshot(path):
    path.mkdir(parents=True, exist_ok=True)
    (path / "snapshot.json").write_text("{}", encoding="utf-8")

def rollback(snapshot, registry):
    shutil.copy2(snapshot, registry)
""",
        encoding="utf-8",
    )
    (package / "synthetic.py").write_text(
        """
SCORE_MAP = {"world_a": 10, "world_b": 20}

def graph_for_family(family):
    return {"organ": family, "nodes": ["ANSWER_TEMPLATE"]}

def candidate_selector(candidate, family):
    return SCORE_MAP[family] + candidate["cost"]
""",
        encoding="utf-8",
    )
    (package / "teacher.py").write_text(
        """
def create_organ(label):
    return {"organ": label}

def teacher_rule(packet):
    organs = []
    organs.append(create_organ(packet["family"]))
    return organs
""",
        encoding="utf-8",
    )
    (package / "analysis.py").write_text(
        """
def analysis_non_interference_proof(candidates):
    baseline = tuple(item["cost"] for item in candidates)
    analysis_tags = {"family": "human_only"}
    tagged = tuple(item["cost"] for item in candidates)
    return baseline == tagged and bool(analysis_tags)
""",
        encoding="utf-8",
    )
    (package / "authority.py").write_text(
        """
import pickle
import os
import random
import requests
import subprocess

def reset_state(state):
    state.clear()

def fork_individual(state):
    return dict(state)

def run_shell():
    return subprocess.run(["echo", "x"])

def network_call():
    return requests.get("https://example.invalid")

def unsafe_load(stream):
    return pickle.load(stream)

def write_result(path):
    path.write_text("result", encoding="utf-8")

def mutate_environment():
    os.putenv("DLP_TEST", "1")

def mutate_seed():
    random.seed(7)
""",
        encoding="utf-8",
    )
    (package / "primitive.py").write_text(
        """
ALLOWED_PRIMITIVES = ("INPUT_SCALAR", "ADD", "ACTION_BID", "ABSTAIN")
FORBIDDEN_HIGH_LEVEL_PRIMITIVES = ("FRAME_DIFF", "OBJECT_DETECTOR")
""",
        encoding="utf-8",
    )
    tests = root / "tests"
    tests.mkdir()
    (tests / "test_analysis.py").write_text(
        """
def test_analysis_tags_do_not_affect_selector_cost_or_regeneration():
    assert True

def test_locked_top_1_pool():
    assert True

def test_not_run_holdout():
    assert True
""",
        encoding="utf-8",
    )
    outputs = root / "outputs" / "run-1"
    outputs.mkdir(parents=True)
    (outputs / "analysis_non_interference_proof.json").write_text(
        '{"status": "PASS"}',
        encoding="utf-8",
    )
    (outputs / "bootstrap_permutation_effective_n.json").write_text(
        '{"status": "PASS"}',
        encoding="utf-8",
    )
    (outputs / "raw.npy").write_bytes(b"not-an-executable-fixture")
    environment = root / ".venv" / "site-packages"
    environment.mkdir(parents=True)
    (environment / "ignored.py").write_text("raise RuntimeError()", encoding="utf-8")
    return root


def build_source_zip(source_root: Path, archive_path: Path) -> Path:
    with ZipFile(archive_path, "w", compression=ZIP_DEFLATED) as archive:
        for path in sorted(source_root.rglob("*")):
            if path.is_file():
                archive.write(
                    path,
                    ("D_lps/" + path.relative_to(source_root).as_posix()),
                )
    return archive_path


def add_zip_symlink(archive_path: Path, name: str, target: str) -> None:
    info = ZipInfo(name)
    info.create_system = 3
    info.external_attr = 0o120777 << 16
    with ZipFile(archive_path, "a") as archive:
        archive.writestr(info, target)
