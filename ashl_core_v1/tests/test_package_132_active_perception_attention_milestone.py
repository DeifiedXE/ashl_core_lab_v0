from __future__ import annotations

import contextlib
import io
import json
import sqlite3
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from ashl_core_v1.host_body.host_body_internal_action_choice import (
    ALLOWED_INTERNAL_ACTION_KINDS,
)
from ashl_core_v1.runtime.host_sensor_types import sha256_payload
from ashl_core_v1.runtime.package_132_perception_attention_milestone_audit import (
    audit_package_132_perception_attention_milestone,
    load_authoritative_closure_contract,
    run_package_132_boundary_controls,
    validate_lineage_records,
    verify_package_132_evidence_unchanged,
)
from ashl_core_v1.runtime.package_132_perception_attention_milestone_cli import (
    main as package_132_cli_main,
)
from ashl_core_v1.runtime.package_132_perception_attention_milestone_store import (
    Package132PerceptionAttentionMilestoneStore,
)
from ashl_core_v1.runtime.perception_attention_closure_types import (
    ABSENT_CAPABILITIES,
    BASELINE_COMMIT,
    CLOSED_PACKAGE_IDS,
    CLOSURE_SCHEMA_VERSION,
    CONTROL_NAMES,
    DOWNSTREAM_FORBIDDEN_AUTHORITIES,
    DOWNSTREAM_READ_ONLY_INTERFACES,
    PACKAGE_COMPLETION_COMMITS,
    PASS_STATUS,
    PERCEPTION_INTERNAL_ACTION_KINDS,
    PRESENT_CAPABILITIES,
    REGRESSION_SCHEMA_VERSION,
    Package132RegressionReceipt,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


class Package132ClosureUnitTests(unittest.TestCase):
    def test_authoritative_contract_is_exact_and_hashed(self) -> None:
        contract = load_authoritative_closure_contract(REPO_ROOT)
        self.assertEqual(contract.schema_version, CLOSURE_SCHEMA_VERSION)
        self.assertEqual(contract.baseline_commit, BASELINE_COMMIT)
        self.assertEqual(contract.closed_package_ids, CLOSED_PACKAGE_IDS)
        self.assertEqual(contract.present_capabilities, PRESENT_CAPABILITIES)
        self.assertEqual(
            contract.perception_internal_action_kinds,
            PERCEPTION_INTERNAL_ACTION_KINDS,
        )
        self.assertEqual(contract.absent_capabilities, ABSENT_CAPABILITIES)
        self.assertEqual(
            contract.downstream_read_only_interfaces,
            DOWNSTREAM_READ_ONLY_INTERFACES,
        )
        self.assertEqual(
            contract.downstream_forbidden_authorities,
            DOWNSTREAM_FORBIDDEN_AUTHORITIES,
        )
        self.assertTrue(contract.perception_capability_construction_frozen)
        self.assertFalse(contract.package_132_adds_runtime_capability)
        self.assertFalse(contract.package_132_adds_internal_action)
        self.assertFalse(contract.package_132a_exists)
        self.assertFalse(contract.package_133_plus_may_extend_perception_capability)
        self.assertEqual(contract.next_core_package, "133")

    def test_boundary_controls_are_actual_rejections(self) -> None:
        contract = load_authoritative_closure_contract(REPO_ROOT)
        controls = run_package_132_boundary_controls(contract)
        self.assertEqual(tuple(dict(controls.controls)), CONTROL_NAMES)
        self.assertEqual(controls.passed_count, len(CONTROL_NAMES))
        self.assertTrue(controls.controls_passed)
        with self.assertRaises(ValueError):
            replace(contract, package_132a_exists=True)
        with self.assertRaises(ValueError):
            replace(
                contract,
                package_130_consumer_scope_preserved="package_133_self_state",
            )

    def test_existing_perception_action_surface_is_closed(self) -> None:
        for action_kind in PERCEPTION_INTERNAL_ACTION_KINDS:
            self.assertIn(action_kind, ALLOWED_INTERNAL_ACTION_KINDS)
        self.assertNotIn("package_132_action", ALLOWED_INTERNAL_ACTION_KINDS)
        self.assertNotIn("observe_forever", ALLOWED_INTERNAL_ACTION_KINDS)

    def test_completion_commits_are_full_and_distinct(self) -> None:
        self.assertEqual(tuple(PACKAGE_COMPLETION_COMMITS), CLOSED_PACKAGE_IDS)
        self.assertEqual(len(set(PACKAGE_COMPLETION_COMMITS.values())), 10)
        self.assertTrue(all(len(value) == 40 for value in PACKAGE_COMPLETION_COMMITS.values()))

    def test_store_is_append_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = Package132PerceptionAttentionMilestoneStore(temp_dir)
            controls = run_package_132_boundary_controls(
                load_authoritative_closure_contract(REPO_ROOT)
            )
            store.append_record("package_132_boundary_control_results", controls)
            self.assertEqual(store.count("package_132_boundary_control_results"), 1)
            with self.assertRaises(ValueError):
                store.append_record("package_132_boundary_control_results", controls)
            self.assertEqual(store.forbidden_mutation_operations(), ("update", "delete"))
            self.assertTrue(store.audit_append_only_store()["valid"])

    def test_lineage_validator_rejects_an_empty_map(self) -> None:
        with self.assertRaises(ValueError):
            validate_lineage_records(tuple())


class Package132EndToEndAuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.archive = self.base / "archive"
        self.evidence = self.base / "evidence"
        self.output = self.base / "output"
        self.archive.mkdir()
        self.evidence.mkdir()
        self._build_archive_fixture()
        self._build_evidence_fixture()
        self._append_regression_receipt()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_end_to_end_closure_passes_without_source_mutation(self) -> None:
        before = _tree_hash(self.evidence)
        audit = audit_package_132_perception_attention_milestone(
            ashl_root=REPO_ROOT,
            state_dir=self.output,
            package_124_archive=self.archive,
            evidence_roots=(self.evidence,),
            archive_verifier=self._archive_verifier,
        )
        self.assertEqual(audit.audit_status, PASS_STATUS)
        self.assertEqual(audit.closed_package_count, 10)
        self.assertEqual(audit.cross_package_lineage_record_count, 12)
        self.assertTrue(audit.all_package_evidence_verified)
        self.assertTrue(audit.all_external_sources_unchanged)
        self.assertTrue(audit.fresh_boundary_controls_passed)
        self.assertTrue(audit.fresh_regressions_passed)
        self.assertFalse(audit.semantic_identity_created)
        self.assertFalse(audit.new_internal_action_created)
        self.assertFalse(audit.persistent_self_state_created)
        self.assertFalse(audit.dlm_1_implemented)
        self.assertEqual(before, _tree_hash(self.evidence))

        store = Package132PerceptionAttentionMilestoneStore(self.output)
        self.assertEqual(store.count("package_132_package_evidence"), 10)
        self.assertEqual(store.count("package_132_cross_package_lineage"), 12)
        serialized = json.dumps(
            store.latest_payload("package_132_audits"), sort_keys=True
        )
        self.assertNotIn(str(self.archive), serialized)
        self.assertNotIn(str(self.evidence), serialized)

    def test_missing_package_audit_is_blocking(self) -> None:
        database = (
            self.evidence
            / "package_128_evidence_sufficiency_stop_v0/package_128.sqlite3"
        )
        database.unlink()
        with self.assertRaisesRegex(RuntimeError, "package_128"):
            audit_package_132_perception_attention_milestone(
                ashl_root=REPO_ROOT,
                state_dir=self.output,
                package_124_archive=self.archive,
                evidence_roots=(self.evidence,),
                archive_verifier=self._archive_verifier,
            )

    def test_post_audit_evidence_mutation_is_visible(self) -> None:
        audit_package_132_perception_attention_milestone(
            ashl_root=REPO_ROOT,
            state_dir=self.output,
            package_124_archive=self.archive,
            evidence_roots=(self.evidence,),
            archive_verifier=self._archive_verifier,
        )
        (self.evidence / "unexpected.txt").write_text("changed", encoding="utf-8")
        result = verify_package_132_evidence_unchanged(
            state_dir=self.output,
            package_124_archive=self.archive,
            evidence_roots=(self.evidence,),
        )
        self.assertFalse(result["all_sources_unchanged"])

    def test_cli_show_commands_use_audit_store_only(self) -> None:
        audit_package_132_perception_attention_milestone(
            ashl_root=REPO_ROOT,
            state_dir=self.output,
            package_124_archive=self.archive,
            evidence_roots=(self.evidence,),
            archive_verifier=self._archive_verifier,
        )
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            code = package_132_cli_main(
                ["show-capabilities", "--state-dir", str(self.output)]
            )
        self.assertEqual(code, 0)
        self.assertIn("real_bounded_multimodal_perception", stream.getvalue())

    def _append_regression_receipt(self) -> None:
        store = Package132PerceptionAttentionMilestoneStore(self.output)
        receipt = Package132RegressionReceipt(
            regression_receipt_id="package_132_regressions:test",
            schema_version=REGRESSION_SCHEMA_VERSION,
            created_at="2026-08-07T00:00:00+00:00",
            baseline_commit=BASELINE_COMMIT,
            source_head=BASELINE_COMMIT,
            command_results=(
                ("targeted_package_132", 0, "a" * 64),
                ("targeted_package_123_to_131", 0, "b" * 64),
                ("full_v1_unittest_discover", 0, "c" * 64),
                ("compileall", 0, "d" * 64),
                ("git_diff_check", 0, "e" * 64),
            ),
            targeted_package_132_passed=True,
            package_123_to_131_regressions_passed=True,
            full_v1_discover_passed=True,
            compileall_passed=True,
            git_diff_check_passed=True,
            pycache_redirected_outside_repo=True,
            fresh_regressions_passed=True,
        )
        store.append_record("package_132_regression_receipts", receipt)

    def _build_archive_fixture(self) -> None:
        package_123_db = (
            self.archive
            / "source_state/package_123_real_perception_v0/package_123.sqlite3"
        )
        _write_payload_database(
            package_123_db,
            "package_123_audit_records",
            _package_123_payload(),
        )
        (self.archive / "ARCHIVE_READ_ONLY").write_text("read only", encoding="utf-8")

    def _build_evidence_fixture(self) -> None:
        specs = {
            "package_124a_temporal_foundation_v0/package_124a_temporal.sqlite3": (
                "package_124a_temporal_audits",
                _package_124a_payload(),
            ),
            "package_125_observation_extension_v0/package_125.sqlite3": (
                "package_125_audits",
                _package_125_payload(),
            ),
            "package_126_bounded_reacquisition_v0/package_126.sqlite3": (
                "package_126_audits",
                _package_126_payload(),
            ),
            "package_127_internal_focus_shift_v0/package_127.sqlite3": (
                "package_127_audits",
                _package_127_payload(),
            ),
            "package_128_evidence_sufficiency_stop_v0/package_128.sqlite3": (
                "package_128_audits",
                _package_128_payload(),
            ),
            "package_129_active_perception_growth_v0/package_129.sqlite3": (
                "package_129_audits",
                _package_129_payload(),
            ),
        }
        for relative, (table, payload) in specs.items():
            _write_payload_database(self.evidence / relative, table, payload)
        p130 = self.evidence / "package_130_grounded_auditory_concept_v0/package_130.sqlite3"
        _write_payload_database(p130, "package_130_audits", _package_130_payload())
        for table, payload in (
            ("grounded_auditory_event_concept_models", _model_payload()),
            ("auditory_grounding_raw_audio_deletion_audits", _deletion_payload()),
            ("auditory_concept_memory_commit_records", _memory_payload()),
            ("expected_audio_primitive_generation_records", _generation_payload()),
        ):
            _append_payload_table(p130, table, payload)
        p131 = self.evidence / "package_131_auditory_predictive_recognition_v0/package_131.sqlite3"
        _write_payload_database(p131, "package_131_audits", _package_131_payload())
        _append_payload_table(p131, "auditory_prediction_consumer_bindings", _binding_payload())
        _append_payload_table(
            p131,
            "auditory_predictive_recognition_pair_comparisons",
            _pair_payload(),
        )

    @staticmethod
    def _archive_verifier(_path: str | Path) -> dict[str, object]:
        return {
            "valid": True,
            "manifest_verification": {"valid": True},
            "certificate_validation": {"valid": True},
            "source_reverification": {"audit": _package_124_payload()},
        }


def _base_payload(package_id: str, audit_id: str) -> dict[str, object]:
    from ashl_core_v1.runtime.perception_attention_closure_types import (
        EXPECTED_AUDIT_STATUSES,
    )

    return {
        "audit_id": audit_id,
        "audit_status": EXPECTED_AUDIT_STATUSES[package_id],
        "failure_reasons": [],
        "created_at": "2026-08-07T00:00:00+00:00",
    }


def _package_123_payload() -> dict[str, object]:
    return {
        **_base_payload("123", "package_123_audit:test"),
        "real_window_capture_verified": True,
        "real_system_audio_loopback_verified": True,
        "real_host_state_verified": True,
        "cycle_2_real_capture_verified": True,
        "cycle_2_new_process_verified": True,
        "cycle_2_readback_influence_verified": True,
        "hard_coded_recognition_detected": False,
        "language_understanding_claimed": False,
        "time_perception_claimed": False,
        "stimulus_ground_truth_entered_learning_path": False,
        "prerecorded_fixture_used": False,
        "qingyin_output_created": False,
        "llm_runtime_calls": 0,
        "codex_runtime_calls": 0,
        "network_runtime_calls": 0,
    }


def _package_124_payload() -> dict[str, object]:
    return {
        **_base_payload("124", "package_124_audit:test"),
        "cycle_1_real_sources_verified": True,
        "cycle_1_transport_verified": True,
        "cycle_2_package_112_influence_verified": True,
        "archive_manifest_verified": True,
        "archive_read_only_reverification_passed": True,
        "semantic_recognition_created": False,
        "time_perception_created": False,
        "language_understanding_created": False,
        "qingyin_output_created": False,
        "runtime_behavior_changed": False,
    }


def _package_124a_payload() -> dict[str, object]:
    return {
        **_base_payload("124A", "package_124a_audit:test"),
        "package_124_archive_verified": True,
        "temporal_anchors_created": True,
        "temporal_spans_created": True,
        "temporal_continuity_created": True,
        "external_gap_boundary_created": True,
        "deterministic_identity_verified": True,
        "archive_modified": False,
        "stimulus_ground_truth_used_for_compilation": False,
        "subjective_time_claimed": False,
        "memory_write_created": False,
        "output_intent_created": False,
    }


def _package_125_payload() -> dict[str, object]:
    return {
        **_base_payload("125", "package_125_audit:test"),
        "audit_mode": "real_active_capture",
        "real_source_capture_verified": True,
        "same_source_sessions_preserved": True,
        "extension_count": 1,
        "all_required_lanes_extended": True,
        "transport_flush_verified": True,
        "temporal_tail_evidence_verified": True,
        **{name: False for name in (
            "focus_selection_created", "memory_write_created", "output_created",
            "external_action_created", "thought_engine_used", "novelty_semantics_claimed",
            "object_or_audio_semantics_claimed",
        )},
    }


def _package_126_payload() -> dict[str, object]:
    return {
        **_base_payload("126", "package_126_audit:test"),
        "package_125_baseline_verified": True,
        "capture_again_real_run_verified": True,
        "listen_again_real_run_verified": True,
        "capture_session_ids_distinct": True,
        "sources_reopened_verified": True,
        "cross_window_gap_recorded": True,
        "audio_deletion_verified": True,
        "raw_audio_retained": False,
        **{name: False for name in (
            "working_readback_created", "focus_selection_created",
            "evidence_sufficiency_runtime_created", "novelty_signal_created",
            "uncertainty_signal_created", "thought_engine_used", "output_created",
            "external_control_created", "same_event_claimed", "same_sound_claimed",
            "speaker_recognition_claimed", "language_understanding_claimed",
            "subjective_listening_claimed",
        )},
    }


def _package_127_payload() -> dict[str, object]:
    return {
        **_base_payload("127", "package_127_audit:test"),
        "real_parent_capture_verified": True,
        "focus_candidate_count": 2,
        "package_126_child_window_used": True,
        "full_frame_capture_preserved": True,
        "focused_region_view_created": True,
        "focus_automatically_released": True,
        **{name: False for name in (
            "memory_write_created", "working_readback_created",
            "evidence_sufficiency_runtime_created", "novelty_signal_created",
            "uncertainty_signal_created", "thought_engine_used", "audio_focus_created",
            "camera_focus_created", "sensor_priority_runtime_created",
            "external_control_created", "output_created", "object_recognition_created",
            "semantic_vision_created",
        )},
    }


def _package_128_payload() -> dict[str, object]:
    return {
        **_base_payload("128", "package_128_audit:test"),
        "package_127_baseline_verified": True,
        "real_focused_child_window_verified": True,
        "final_assessment_sufficient": True,
        "stop_observation_action_created": True,
        "stopped_before_hard_deadline": True,
        "all_required_lanes_stopped": True,
        "flush_completed": True,
        "focus_released_at_completion": True,
        **{name: False for name in (
            "memory_write_created", "working_readback_created", "extension_action_created",
            "reacquisition_action_created", "focus_shift_action_created",
            "novelty_signal_created", "uncertainty_signal_created", "thought_engine_used",
            "output_created", "external_control_created", "semantic_understanding_claimed",
            "recognition_claimed", "certainty_claimed", "subjective_time_claimed",
        )},
    }


def _package_129_payload() -> dict[str, object]:
    return {
        **_base_payload("129", "package_129_audit:test"),
        "cycle_1_real_capture_verified": True,
        "cycle_1_exact_approval_verified": True,
        "cycle_1_reviewed_memory_chain_verified": True,
        "cycle_2_fresh_capture_verified": True,
        "cycle_2_readback_influence_verified": True,
        "cycle_2_readback_contribution": 3.0,
        "cycle_2_actual_runtime_hot_path_verified": True,
        "cycle_2_policy_gate_bypass_detected": False,
        "cycle_1_extension_verified": True,
        "cycle_2_extension_verified": True,
        "cycle_1_capture_again_verified": True,
        "cycle_2_capture_again_verified": True,
        "cycle_1_focus_shift_verified": True,
        "cycle_2_focus_shift_verified": True,
        "cycle_1_stop_observation_verified": True,
        "cycle_2_stop_observation_verified": True,
        **{name: False for name in (
            "new_perception_action_kind_created", "new_sensor_source_created",
            "new_primitive_compiler_created", "new_focus_mode_created",
            "new_sufficiency_contract_kind_created", "semantic_vision_created",
            "object_recognition_created", "auditory_concept_created",
            "auditory_prediction_created", "uncertainty_signal_created",
            "novelty_signal_created", "curiosity_signal_created", "thought_engine_used",
            "qingyin_output_created", "external_control_created",
            "package_132_milestone_claimed",
        )},
    }


def _package_130_payload() -> dict[str, object]:
    return {
        **_base_payload("130", "package_130_audit:test"),
        "package_129_baseline_verified": True,
        "real_grounding_audio_verified": True,
        "positive_episode_count": 4,
        "contrast_episode_count": 3,
        "exact_teacher_approval_verified": True,
        "auditory_concept_model_created": True,
        "grounding_raw_deletion_count": 7,
        "raw_audio_blob_count_after_deletion": 0,
        **{name: False for name in (
            "runtime_recognition_created", "auditory_prediction_runtime_created",
            "speaker_profile_created", "speaker_embedding_created", "transcript_created",
            "semantic_emotion_created", "object_identity_created", "action_identity_created",
            "material_identity_created", "internal_action_created", "output_created",
            "external_control_created",
        )},
    }


def _model_payload() -> dict[str, object]:
    return {
        "auditory_concept_model_id": "model:test",
        "maturity_status": "reviewed_grounded_ready_for_package_131",
        "semantic_label": None,
        "natural_language_name": None,
        "recognition_enabled": False,
        "prediction_error_runtime_enabled": False,
        "automatic_regrounding_enabled": False,
        "package_112_action_influence_allowed": False,
        "package_131_consumer_allowed": True,
        "raw_audio_dependency_active": False,
        "raw_audio_deletion_audit_id": "deletion:test",
    }


def _deletion_payload() -> dict[str, object]:
    return {
        "deletion_audit_id": "deletion:test",
        "raw_blob_count_after_deletion": 0,
        "recoverable_waveform_detected": False,
    }


def _memory_payload() -> dict[str, object]:
    return {
        "memory_commit_record_id": "memory:test",
        "consumer_scope": "package_131_auditory_prediction_only",
        "active_package_112_working_readback_created": False,
    }


def _generation_payload() -> dict[str, object]:
    return {
        "generation_id": "generation:test",
        "stimulus_ground_truth_used": False,
    }


def _package_131_payload() -> dict[str, object]:
    return {
        **_base_payload("131", "package_131_audit:test"),
        "package_130_audit_id": "package_130_audit:test",
        "both_real_wasapi_loopback": True,
        "processes_distinct": True,
        "probe_a_prediction_result": "supported_by_reviewed_anonymous_auditory_concept",
        "probe_b_prediction_result": "not_supported_by_reviewed_anonymous_auditory_concept",
        "cleanup_verified": True,
        **{name: False for name in (
            "semantic_sound_name_created", "object_identity_created", "action_identity_created",
            "material_identity_created", "speaker_profile_created", "speaker_embedding_created",
            "transcript_created", "speech_understanding_created", "emotion_meaning_created",
            "package_112_score_changed", "internal_action_created", "memory_written",
            "teacher_review_created", "working_readback_created", "output_created",
            "external_control_created", "d_laplace_component_used", "dlm_1_implemented",
            "package_132_implemented",
        )},
    }


def _binding_payload() -> dict[str, object]:
    return {
        "binding_id": "binding:test",
        "auditory_concept_model_id": "model:test",
        "consumer_scope": "package_131_auditory_prediction_only",
        "active_working_readback_used": False,
        "raw_audio_dependency_active": False,
        "package_112_action_influence_allowed": False,
    }


def _pair_payload() -> dict[str, object]:
    return {
        "pair_comparison_id": "pair:test",
        "comparison_status": "passed_real_two_probe_anonymous_auditory_prediction",
        "fixture_firewall_passed": True,
    }


def _write_payload_database(path: Path, table: str, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with contextlib.closing(sqlite3.connect(path)) as connection:
        connection.execute(
            f"CREATE TABLE {table} (row_id INTEGER PRIMARY KEY, payload_json TEXT, payload_sha256 TEXT)"
        )
        connection.execute(
            f"INSERT INTO {table} (payload_json, payload_sha256) VALUES (?, ?)",
            (json.dumps(payload, sort_keys=True), sha256_payload(payload)),
        )
        connection.commit()


def _append_payload_table(path: Path, table: str, payload: dict[str, object]) -> None:
    with contextlib.closing(sqlite3.connect(path)) as connection:
        connection.execute(
            f"CREATE TABLE {table} (row_id INTEGER PRIMARY KEY, payload_json TEXT, payload_sha256 TEXT)"
        )
        connection.execute(
            f"INSERT INTO {table} (payload_json, payload_sha256) VALUES (?, ?)",
            (json.dumps(payload, sort_keys=True), sha256_payload(payload)),
        )
        connection.commit()


def _tree_hash(path: Path) -> str:
    entries = []
    for item in sorted(candidate for candidate in path.rglob("*") if candidate.is_file()):
        entries.append((item.relative_to(path).as_posix(), item.read_bytes().hex()))
    return sha256_payload(entries)


if __name__ == "__main__":
    unittest.main()
