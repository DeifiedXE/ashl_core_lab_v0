"""Runtime guard for no-Codex fixture growth workers."""

from __future__ import annotations

import builtins
import socket
import subprocess
from dataclasses import dataclass, fields
from typing import Any


class NoCodexRuntimeGuardViolation(RuntimeError):
    pass


@dataclass(frozen=True)
class NoCodexRuntimeGuardCounters:
    codex_runtime_call_count: int
    llm_runtime_call_count: int
    network_connection_attempt_count: int
    model_client_import_count: int
    arbitrary_subprocess_attempt_count: int
    dynamic_code_execution_attempt_count: int

    def to_dict(self) -> dict[str, int]:
        return {field.name: int(getattr(self, field.name)) for field in fields(self)}


class NoCodexRuntimeGuard:
    """Small monkeypatch guard used only inside Package 118 worker processes."""

    _MODEL_IMPORT_ROOTS = {
        "anthropic",
        "cohere",
        "codex",
        "google.generativeai",
        "mistralai",
        "openai",
    }

    def __init__(self) -> None:
        self.codex_runtime_call_count = 0
        self.llm_runtime_call_count = 0
        self.network_connection_attempt_count = 0
        self.model_client_import_count = 0
        self.arbitrary_subprocess_attempt_count = 0
        self.dynamic_code_execution_attempt_count = 0
        self._originals: dict[str, Any] = {}

    def __enter__(self) -> "NoCodexRuntimeGuard":
        self._originals = {
            "socket": socket.socket,
            "popen": subprocess.Popen,
            "run": subprocess.run,
            "call": subprocess.call,
            "check_call": subprocess.check_call,
            "check_output": subprocess.check_output,
            "eval": builtins.eval,
            "exec": builtins.exec,
            "import": builtins.__import__,
        }
        socket.socket = self._blocked_socket  # type: ignore[assignment]
        subprocess.Popen = self._blocked_popen  # type: ignore[assignment]
        subprocess.run = self._blocked_subprocess  # type: ignore[assignment]
        subprocess.call = self._blocked_subprocess  # type: ignore[assignment]
        subprocess.check_call = self._blocked_subprocess  # type: ignore[assignment]
        subprocess.check_output = self._blocked_subprocess  # type: ignore[assignment]
        builtins.eval = self._blocked_eval  # type: ignore[assignment]
        builtins.exec = self._blocked_exec  # type: ignore[assignment]
        builtins.__import__ = self._guarded_import  # type: ignore[assignment]
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        socket.socket = self._originals["socket"]  # type: ignore[assignment]
        subprocess.Popen = self._originals["popen"]  # type: ignore[assignment]
        subprocess.run = self._originals["run"]  # type: ignore[assignment]
        subprocess.call = self._originals["call"]  # type: ignore[assignment]
        subprocess.check_call = self._originals["check_call"]  # type: ignore[assignment]
        subprocess.check_output = self._originals["check_output"]  # type: ignore[assignment]
        builtins.eval = self._originals["eval"]  # type: ignore[assignment]
        builtins.exec = self._originals["exec"]  # type: ignore[assignment]
        builtins.__import__ = self._originals["import"]  # type: ignore[assignment]

    def counters(self) -> NoCodexRuntimeGuardCounters:
        return NoCodexRuntimeGuardCounters(
            codex_runtime_call_count=self.codex_runtime_call_count,
            llm_runtime_call_count=self.llm_runtime_call_count,
            network_connection_attempt_count=self.network_connection_attempt_count,
            model_client_import_count=self.model_client_import_count,
            arbitrary_subprocess_attempt_count=self.arbitrary_subprocess_attempt_count,
            dynamic_code_execution_attempt_count=self.dynamic_code_execution_attempt_count,
        )

    def _blocked_socket(self, *args: Any, **kwargs: Any) -> Any:
        self.network_connection_attempt_count += 1
        raise NoCodexRuntimeGuardViolation("network socket creation is blocked in no-Codex workers")

    def _blocked_popen(self, *args: Any, **kwargs: Any) -> Any:
        self.arbitrary_subprocess_attempt_count += 1
        raise NoCodexRuntimeGuardViolation("subprocess creation is blocked in no-Codex workers")

    def _blocked_subprocess(self, *args: Any, **kwargs: Any) -> Any:
        self.arbitrary_subprocess_attempt_count += 1
        raise NoCodexRuntimeGuardViolation("subprocess execution is blocked in no-Codex workers")

    def _blocked_eval(self, *args: Any, **kwargs: Any) -> Any:
        self.dynamic_code_execution_attempt_count += 1
        raise NoCodexRuntimeGuardViolation("eval is blocked in no-Codex workers")

    def _blocked_exec(self, *args: Any, **kwargs: Any) -> Any:
        self.dynamic_code_execution_attempt_count += 1
        raise NoCodexRuntimeGuardViolation("exec is blocked in no-Codex workers")

    def _guarded_import(self, name: str, globals: Any = None, locals: Any = None, fromlist: Any = (), level: int = 0) -> Any:
        root = str(name)
        if any(root == item or root.startswith(f"{item}.") for item in self._MODEL_IMPORT_ROOTS):
            self.model_client_import_count += 1
            if root == "codex" or root.startswith("codex."):
                self.codex_runtime_call_count += 1
            else:
                self.llm_runtime_call_count += 1
            raise NoCodexRuntimeGuardViolation(f"model client import is blocked: {root}")
        return self._originals["import"](name, globals, locals, fromlist, level)
