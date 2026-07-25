from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ashl_core_v1.runtime.package_125_observation_extension_audit import (
    SYNTHETIC_PACKAGE_125_PASS_STATUS,
    audit_package_125_observation_extension,
)
from ashl_core_v1.runtime.package_125_observation_extension_runtime import (
    run_synthetic_observation_extension_scenario,
    run_synthetic_package_125_suite,
)
from ashl_core_v1.runtime.package_125_observation_extension_store import (
    Package125ObservationExtensionStore,
)


class Package125AuditTests(unittest.TestCase):
    def test_scoped_synthetic_audit_passes_with_multiple_scenarios(self) -> None:
        with tempfile.TemporaryDirectory() as state_dir:
            suite = run_synthetic_package_125_suite(state_dir=state_dir)
        self.assertEqual(suite["audit"]["audit_status"], SYNTHETIC_PACKAGE_125_PASS_STATUS)
        self.assertEqual(suite["audit"]["failure_reasons"], [])
        self.assertFalse(suite["audit"]["real_source_capture_verified"])
        self.assertTrue(suite["audit"]["active_capture_identity_chain_verified"])

    def test_other_window_and_session_evidence_cannot_satisfy_target_audit(self) -> None:
        with tempfile.TemporaryDirectory() as state_dir:
            group_id = "audit_group:scope-negative"
            target = run_synthetic_observation_extension_scenario(
                state_dir=state_dir,
                scenario="stable_baseline_control",
                audit_group_id=group_id,
            )
            other = run_synthetic_observation_extension_scenario(
                state_dir=state_dir,
                scenario="late_event",
                audit_group_id=group_id,
            )
            self.assertNotEqual(
                target["observation_window"]["runtime_session_id"],
                other["candidate"]["runtime_session_id"],
            )
            audit = audit_package_125_observation_extension(
                state_dir=state_dir,
                observation_window_id=target["observation_window"]["observation_window_id"],
                append=False,
                require_real_source_capture=False,
            )
        self.assertEqual(audit.audit_status, "blocked_bounded_observation_window_extension_audit")
        self.assertIn("missing_candidate_from_tail_evidence", audit.failure_reasons)
        self.assertIn("active_capture_identity_chain_invalid", audit.failure_reasons)

    def test_event_stream_failure_is_persisted_and_blocks_audit(self) -> None:
        with tempfile.TemporaryDirectory() as state_dir:
            with patch(
                "ashl_core_v1.runtime.package_125_observation_extension_runtime.LocalOperatorEventStream.append_event",
                side_effect=RuntimeError("event stream unavailable"),
            ):
                suite = run_synthetic_package_125_suite(state_dir=state_dir)
            failures = Package125ObservationExtensionStore(state_dir).list_payloads(
                "operator_event_delivery_failures"
            )
        self.assertTrue(failures)
        self.assertEqual(suite["audit"]["audit_status"], "blocked_bounded_observation_window_extension_audit")
        self.assertIn("operator_event_delivery_failure", suite["audit"]["failure_reasons"])

    def test_strict_event_stream_mode_raises_after_recording_failure(self) -> None:
        with tempfile.TemporaryDirectory() as state_dir:
            with patch(
                "ashl_core_v1.runtime.package_125_observation_extension_runtime.LocalOperatorEventStream.append_event",
                side_effect=RuntimeError("strict event stream failure"),
            ):
                with self.assertRaisesRegex(RuntimeError, "strict event stream failure"):
                    run_synthetic_observation_extension_scenario(
                        state_dir=state_dir,
                        strict_event_stream=True,
                    )
            failures = Package125ObservationExtensionStore(state_dir).list_payloads(
                "operator_event_delivery_failures"
            )
        self.assertEqual(len(failures), 1)
        self.assertTrue(failures[0]["strict_mode"])

    def test_package_125_does_not_rewrite_existing_raw_sentinel(self) -> None:
        with tempfile.TemporaryDirectory() as state_dir:
            sentinel = Path(state_dir) / "raw_trace_and_artifact_sentinel.bin"
            sentinel.write_bytes(b"append-only-raw-evidence")
            before = hashlib.sha256(sentinel.read_bytes()).hexdigest()
            run_synthetic_package_125_suite(state_dir=state_dir)
            after = hashlib.sha256(sentinel.read_bytes()).hexdigest()
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
