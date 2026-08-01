"""Package 130 baseline, backend, and external-state preflight."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from ashl_core_v1.perception.audio_primitive_compiler import AUDIO_PRIMITIVE_COMPILER_VERSION
from ashl_core_v1.runtime.auditory_grounding_types import BASELINE_COMMIT, BLUR_POLICY_VERSION
from ashl_core_v1.runtime.host_sensor_types import stable_id, utc_now
from ashl_core_v1.runtime.windows_wasapi_loopback_source import WindowsWasapiLoopbackSource


def run_package_130_preflight(
    *,
    state_dir: str | Path,
    render_endpoint: str = "default",
    ashl_root: str | Path | None = None,
    require_clean_tree: bool = False,
) -> dict[str, Any]:
    root = Path(ashl_root or Path(__file__).resolve().parents[2])
    path = Path(state_dir)
    failures: list[str] = []
    head = _git(root, "rev-parse", "HEAD")
    branch = _git(root, "branch", "--show-current")
    baseline_present = subprocess.run(
        ["git", "merge-base", "--is-ancestor", BASELINE_COMMIT, "HEAD"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    ).returncode == 0
    status_short = _git(root, "status", "--short")
    if branch != "main":
        failures.append("branch_not_main")
    if not baseline_present:
        failures.append("required_baseline_not_present")
    if require_clean_tree and status_short:
        failures.append("working_tree_not_clean")
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".package_130_preflight_probe"
        probe.write_text("external-state-write-probe", encoding="ascii")
        probe.unlink()
    except OSError:
        failures.append("external_state_dir_not_writable")
    source = WindowsWasapiLoopbackSource(endpoint_id=render_endpoint)
    descriptor = source.source_descriptor()
    if not descriptor.available:
        failures.append(descriptor.failure_reason or "wasapi_loopback_unavailable")
    return {
        "preflight_id": stable_id("package_130_preflight"),
        "schema_version": "ashl_package_130_preflight_v0",
        "created_at": utc_now(),
        "ashl_root": str(root),
        "state_dir": str(path),
        "head_commit": head,
        "branch": branch,
        "required_baseline_commit": BASELINE_COMMIT,
        "required_baseline_present": baseline_present,
        "package_129_baseline_verified": baseline_present,
        "package_126_audio_baseline_verified": baseline_present,
        "package_120a_deletion_baseline_verified": baseline_present,
        "package_121_audio_primitive_baseline_verified": baseline_present,
        "qm0_baseline_verified": baseline_present,
        "working_tree_clean": not bool(status_short),
        "require_clean_tree": bool(require_clean_tree),
        "render_endpoint": render_endpoint,
        "wasapi_loopback_available": bool(descriptor.available),
        "source_descriptor": descriptor.to_dict(),
        "audio_primitive_compiler_version": AUDIO_PRIMITIVE_COMPILER_VERSION,
        "blur_policy_version": BLUR_POLICY_VERSION,
        "preflight_status": "passed" if not failures else "blocked",
        "failure_reasons": tuple(failures),
    }


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
