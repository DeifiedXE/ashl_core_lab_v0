"""Package 113 current ASHL Core v1 status report output."""

from __future__ import annotations

from pathlib import Path
from typing import Any


CURRENT_STATUS_REPORT_PATH = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "current_ashl_core_v1_status_after_package_113.md"
)

PACKAGE_113_MILESTONE_AUDIT_RESULT = (
    "passed_host_body_embodied_learning_closed_loop_milestone_audit"
)

CURRENT_SAFE_LOOP_STEPS = (
    "Host Body event",
    "internal action",
    "LearningFeedbackCandidate",
    "existing learning pipeline",
    "ReviewedConcept readiness",
    "working readback",
    "readback-influenced internal action choice",
)

COMPLETED_MAJOR_LOOPS = (
    "bounded task learning loop v0",
    "ReviewedConcept working readback loop v0",
    "Host Body v0",
    "Host Body evidence to LearningFeedbackCandidate bridge",
    "Host Body feedback through existing learning pipeline",
    "Host Body ReviewedConcept working readback",
    "Host Body readback internal action influence",
)

NEXT_RECOMMENDED_PACKAGES = (
    "114 / Internal Action Home Surface Link",
    "115 / Runtime State Summary / Session Shell",
    "116 / Bounded Embodied Loop Runner",
    "117 / Teacher Console No-Codex Operation Flow",
    "118 / Session End Review + Promote Gate",
    "119 / No-Codex Fixture Embodied Growth Loop Milestone Audit",
    "120+ real low-level camera / mic adapters",
)

FORBIDDEN_CAPABILITY_FLAGS = {
    "real_camera_access_created": False,
    "real_microphone_access_created": False,
    "semantic_vision_created": False,
    "speech_recognition_created": False,
    "task_engine_selected_action_from_host_body_readback_created": False,
    "final_action_created": False,
    "direct_command_created": False,
    "sandbox_execution_created": False,
    "external_control_created": False,
    "os_operation_created": False,
    "mouse_operation_created": False,
    "keyboard_operation_created": False,
    "browser_operation_created": False,
    "file_operation_created": False,
    "network_operation_created": False,
    "shell_operation_created": False,
    "api_operation_created": False,
    "long_term_memory_write_created": False,
    "core_memory_write_created": False,
    "automatic_learning_approval_created": False,
    "teacher_approval_creation_created": False,
    "first_output_created": False,
    "live_qingyin_runtime_session_created": False,
    "thought_engine_behavior_created": False,
    "production_behavior_created": False,
    "gcmc_runtime_implemented": False,
    "cl_token_created": False,
    "concept_compiler_created": False,
    "pattern_miner_created": False,
}

REQUIRED_STATUS_REPORT_FRAGMENTS = (
    "# ASHL Core v1 Current Status After Package 113",
    "Package 113 milestone audit result",
    PACKAGE_113_MILESTONE_AUDIT_RESULT,
    "Host Body embodied learning readback loop status",
    "bounded task learning loop v0",
    "ReviewedConcept working readback loop v0",
    "Host Body v0",
    "Host Body evidence to LearningFeedbackCandidate bridge",
    "Host Body feedback through existing learning pipeline",
    "Host Body ReviewedConcept working readback",
    "Host Body readback internal action influence",
    "Host Body event",
    "readback-influenced internal action choice",
    "real camera access: false / not created",
    "real microphone access: false / not created",
    "semantic vision: false / not created",
    "speech recognition: false / not created",
    "Task Engine selected_action from Host Body readback: false / not created",
    "final_action / direct_command / sandbox execution: false / not created",
    "external control: false / not created",
    "OS / mouse / keyboard / browser / file / network / shell / API operation: false / not created",
    "long-term memory write: false / not created",
    "Core memory write: false / not created",
    "automatic learning approval: false / not created",
    "teacher approval creation: false / not created",
    "first_output: false / not created",
    "live Qingyin runtime session: false / not created",
    "Thought Engine behavior: false / not created",
    "production behavior: false / not created",
    "GCMC v0.3 is future AGE architecture only",
    "Qingyin v1 does not implement GCMC runtime",
    "Qingyin v1 does not create CL tokens",
    "Qingyin v1 does not create Concept Compiler",
    "Qingyin v1 does not create Pattern Miner",
    "Trace Spine format stays unified and time-aligned",
    "Raw trace is append-only during service period and is not summarized",
    "Memory layer stores reviewed interpretation + source_trace_refs",
    "concept_id is not embedded into raw history",
    "formed_under_assumption is not required now because Qingyin v1 does not use CL tokens",
    "bounded embodied loop runner",
    "no-Codex teacher console operation flow",
    "session end review / promote gate",
    "no-Codex fixture embodied growth loop milestone audit",
    "114 / Internal Action Home Surface Link",
    "115 / Runtime State Summary / Session Shell",
    "116 / Bounded Embodied Loop Runner",
    "117 / Teacher Console No-Codex Operation Flow",
    "118 / Session End Review + Promote Gate",
    "119 / No-Codex Fixture Embodied Growth Loop Milestone Audit",
    "120+ real low-level camera / mic adapters",
    "not a live autonomous Qingyin runtime",
    "Qingyin is awake",
    "Qingyin has first_output",
    "Qingyin has live runtime autonomy",
)


def get_current_status_report_markdown() -> str:
    """Return the checked-in Package 113 current status report markdown."""

    return CURRENT_STATUS_REPORT_PATH.read_text(encoding="utf-8")


def validate_current_status_report_text(markdown: str | None = None) -> dict[str, Any]:
    """Validate the Package 113 current status report against required fragments."""

    report_text = get_current_status_report_markdown() if markdown is None else markdown
    missing_fragments = tuple(
        fragment
        for fragment in REQUIRED_STATUS_REPORT_FRAGMENTS
        if fragment not in report_text
    )
    return {
        "valid": not missing_fragments,
        "missing_fragments": missing_fragments,
        "report_path": str(CURRENT_STATUS_REPORT_PATH),
        "report_file_exists": CURRENT_STATUS_REPORT_PATH.exists(),
        "package_113_milestone_audit_result": PACKAGE_113_MILESTONE_AUDIT_RESULT,
        "required_fragment_count": len(REQUIRED_STATUS_REPORT_FRAGMENTS),
    }


def build_current_ashl_core_v1_status_after_package_113_report() -> dict[str, Any]:
    """Build a read-only current situation report payload for Package 113."""

    markdown = get_current_status_report_markdown()
    return {
        "report_kind": "current_ashl_core_v1_status_after_package_113",
        "report_generated_by": "Codex",
        "report_path": str(CURRENT_STATUS_REPORT_PATH),
        "report_markdown": markdown,
        "package_113_milestone_audit_result": PACKAGE_113_MILESTONE_AUDIT_RESULT,
        "host_body_embodied_learning_readback_loop_status": (
            "fixture_only_teacher_gated_readback_influenced_internal_action_choice"
        ),
        "completed_major_loops": COMPLETED_MAJOR_LOOPS,
        "current_safe_loop_steps": CURRENT_SAFE_LOOP_STEPS,
        "next_recommended_packages": NEXT_RECOMMENDED_PACKAGES,
        "validation": validate_current_status_report_text(markdown),
        **FORBIDDEN_CAPABILITY_FLAGS,
    }
