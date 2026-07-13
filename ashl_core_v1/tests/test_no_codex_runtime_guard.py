import builtins
import socket
import subprocess
import unittest

from ashl_core_v1.runtime.no_codex_runtime_guard import (
    NoCodexRuntimeGuard,
    NoCodexRuntimeGuardViolation,
)


class NoCodexRuntimeGuardTests(unittest.TestCase):
    def test_guard_blocks_runtime_prohibitions_and_counts_attempts(self) -> None:
        with NoCodexRuntimeGuard() as guard:
            with self.assertRaises(NoCodexRuntimeGuardViolation):
                socket.socket()
            with self.assertRaises(NoCodexRuntimeGuardViolation):
                subprocess.run(["python", "--version"])
            with self.assertRaises(NoCodexRuntimeGuardViolation):
                builtins.eval("1 + 1")
            with self.assertRaises(NoCodexRuntimeGuardViolation):
                builtins.exec("x = 1")
            with self.assertRaises(NoCodexRuntimeGuardViolation):
                __import__("openai")
            counters = guard.counters()

        self.assertEqual(counters.network_connection_attempt_count, 1)
        self.assertEqual(counters.arbitrary_subprocess_attempt_count, 1)
        self.assertEqual(counters.dynamic_code_execution_attempt_count, 2)
        self.assertEqual(counters.model_client_import_count, 1)
        self.assertEqual(counters.llm_runtime_call_count, 1)
        self.assertEqual(counters.codex_runtime_call_count, 0)


if __name__ == "__main__":
    unittest.main()
