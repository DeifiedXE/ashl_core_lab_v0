"""Local non-LLM output dispatcher for Package 122B."""

from __future__ import annotations

from ashl_core_v1.runtime.host_sensor_types import stable_id, utc_now
from ashl_core_v1.runtime.local_operator_console_store import LocalOperatorConsoleStore
from ashl_core_v1.runtime.local_operator_event_stream import LocalOperatorEventStream
from ashl_core_v1.runtime.operator_console_types import (
    DISPATCH_RESULT_SCHEMA_VERSION,
    OUTPUT_INTENT_SCHEMA_VERSION,
    CANCELLATION_SCHEMA_VERSION,
    LocalOutputIntentRecord,
    OutputCancellationRecord,
    OutputDispatchResultRecord,
    OutputRateLimitPolicy,
)
from ashl_core_v1.runtime.operator_status_log import build_operator_status_log_entry
from ashl_core_v1.runtime.operator_text_timeline import append_raw_output_timeline_entry
from ashl_core_v1.runtime.output_rate_limit import build_default_output_rate_limit_policy, rate_limit_allows_dispatch
from ashl_core_v1.runtime.reserved_sound_pattern_registry import get_reserved_sound_pattern


class LocalNonLLMOutputDispatcher:
    def __init__(self, store: LocalOperatorConsoleStore) -> None:
        self.store = store
        self.events = LocalOperatorEventStream(store)

    def create_raw_output_intent(
        self,
        *,
        raw_output_sequence_id: str,
        source_kind: str,
        source_record_refs: tuple[str, ...],
        source_trace_refs: tuple[str, ...] = tuple(),
        fixture_only: bool = True,
        qingyin_authored: bool = False,
    ) -> LocalOutputIntentRecord:
        intent = LocalOutputIntentRecord(
            output_intent_id=stable_id("local_output_intent"),
            schema_version=OUTPUT_INTENT_SCHEMA_VERSION,
            created_at=utc_now(),
            output_kind="raw_text_token_sequence",
            raw_output_sequence_id=raw_output_sequence_id,
            sound_pattern_id=None,
            source_kind=source_kind,
            source_record_refs=source_record_refs,
            source_trace_refs=source_trace_refs,
            semantic_label=None,
            fixture_only=fixture_only,
            qingyin_authored=qingyin_authored,
            cancelable=True,
            requested_sink="local_text_surface",
        )
        self.store.append_output_intent(intent)
        self.events.append_event(
            event_kind="raw_output_intent_received",
            source_record_refs=(intent.output_intent_id,) + intent.source_record_refs,
            source_trace_refs=intent.source_trace_refs,
        )
        return intent

    def create_sound_pattern_intent(
        self,
        *,
        sound_pattern_id: str,
        source_kind: str = "developer_test",
        source_record_refs: tuple[str, ...] = ("developer_test:sound_pattern",),
    ) -> LocalOutputIntentRecord:
        get_reserved_sound_pattern(sound_pattern_id)
        intent = LocalOutputIntentRecord(
            output_intent_id=stable_id("local_output_intent"),
            schema_version=OUTPUT_INTENT_SCHEMA_VERSION,
            created_at=utc_now(),
            output_kind="reserved_sound_pattern",
            raw_output_sequence_id=None,
            sound_pattern_id=sound_pattern_id,
            source_kind=source_kind,
            source_record_refs=source_record_refs,
            source_trace_refs=tuple(),
            semantic_label=None,
            fixture_only=source_kind in {"fixture", "developer_test"},
            qingyin_authored=False,
            cancelable=True,
            requested_sink="local_text_surface",
        )
        self.store.append_output_intent(intent)
        self.events.append_event(event_kind="raw_output_intent_received", source_record_refs=(intent.output_intent_id,))
        return intent

    def cancel_output(
        self,
        *,
        output_intent_id: str,
        requested_by: str = "user",
        cancellation_reason: str = "operator_cancelled",
    ) -> OutputCancellationRecord:
        already_dispatched = self.store.has_dispatch_for_intent(output_intent_id)
        cancellation = OutputCancellationRecord(
            cancellation_id=stable_id("output_cancellation"),
            schema_version=CANCELLATION_SCHEMA_VERSION,
            created_at=utc_now(),
            target_output_intent_id=output_intent_id,
            requested_by=requested_by,
            cancellation_reason=cancellation_reason,
            cancellation_succeeded=not already_dispatched,
            already_dispatched=already_dispatched,
            source_trace_refs=tuple(),
        )
        self.store.append_cancellation(cancellation)
        self.store.append_status_log(
            build_operator_status_log_entry(
                level="notice",
                event_kind="output_cancelled",
                operator_message=(
                    "Output intent was cancelled."
                    if cancellation.cancellation_succeeded
                    else "Output intent was already dispatched and cannot be erased."
                ),
                source_module="ashl_core_v1.runtime.local_non_llm_output_dispatcher",
                source_record_refs=(output_intent_id, cancellation.cancellation_id),
            )
        )
        self.events.append_event(
            event_kind="output_cancelled",
            source_record_refs=(output_intent_id, cancellation.cancellation_id),
        )
        return cancellation

    def dispatch_intent(
        self,
        output_intent_id: str,
        *,
        policy: OutputRateLimitPolicy | None = None,
    ) -> OutputDispatchResultRecord:
        intent_payload = self.store.get_payload("output_intents", "output_intent_id", output_intent_id)
        intent = LocalOutputIntentRecord(**intent_payload)
        policy = policy or self._active_policy()
        volume = self.store.latest_output_volume_state() or {}
        muted = bool(volume.get("muted", False))
        source_trace_refs = intent.source_trace_refs

        if self.store.has_successful_cancellation_for_intent(intent.output_intent_id):
            result = self._result(
                intent=intent,
                status="cancelled",
                rendered_text=None,
                sound_played=False,
                cancelled=True,
                muted=muted,
                rate_limited=False,
                failure_kind=None,
                retryable=False,
                source_trace_refs=source_trace_refs,
            )
            self._record_result(result, "output_cancelled", "Output intent was cancelled before dispatch.")
            return result

        allowed, reason = rate_limit_allows_dispatch(
            policy=policy,
            pending_output_count=max(0, self.store.pending_output_count() - 1),
            latest_dispatch_age_ms=self.store.latest_successful_dispatch_age_ms(),
        )
        if not allowed:
            result = self._result(
                intent=intent,
                status="blocked_rate_limit",
                rendered_text=None,
                sound_played=False,
                cancelled=False,
                muted=muted,
                rate_limited=True,
                failure_kind=reason,
                retryable=True,
                source_trace_refs=source_trace_refs,
            )
            self._record_result(result, "output_rate_limited", "Output intent was rate-limited.")
            return result

        if intent.output_kind == "reserved_sound_pattern":
            result = self._result(
                intent=intent,
                status="blocked_sound_sink_disabled",
                rendered_text=None,
                sound_played=False,
                cancelled=False,
                muted=muted,
                rate_limited=False,
                failure_kind="sound_sink_disabled_by_policy",
                retryable=False,
                source_trace_refs=source_trace_refs,
            )
            self._record_result(result, "output_failed", "Sound output is disabled by Package 122B policy.")
            return result

        sequence_payload = self.store.get_payload(
            "raw_output_sequences",
            "raw_output_sequence_id",
            str(intent.raw_output_sequence_id),
        )
        rendered = " ".join(str(token) for token in sequence_payload["token_codes"])
        result = self._result(
            intent=intent,
            status="dispatched",
            rendered_text=rendered,
            sound_played=False,
            cancelled=False,
            muted=muted,
            rate_limited=False,
            failure_kind=None,
            retryable=False,
            source_trace_refs=source_trace_refs,
        )
        self.store.append_dispatch_result(result)
        append_raw_output_timeline_entry(
            self.store,
            display_text=rendered,
            source_record_id=result.dispatch_result_id,
            source_actor="fixture" if result.fixture_only else "qingyin_runtime",
            fixture_only=result.fixture_only,
            qingyin_authored=result.qingyin_authored,
            source_trace_refs=result.source_trace_refs,
        )
        self.store.append_status_log(
            build_operator_status_log_entry(
                level="info",
                event_kind="output_dispatched",
                operator_message="Raw output tokens dispatched to local text surface.",
                source_module="ashl_core_v1.runtime.local_non_llm_output_dispatcher",
                source_record_refs=(intent.output_intent_id, result.dispatch_result_id),
                source_trace_refs=result.source_trace_refs,
            )
        )
        self.events.append_event(
            event_kind="output_dispatched",
            source_record_refs=(intent.output_intent_id, result.dispatch_result_id),
            source_trace_refs=result.source_trace_refs,
        )
        return result

    def _active_policy(self) -> OutputRateLimitPolicy:
        payload = self.store.latest_rate_limit_policy()
        if payload:
            return OutputRateLimitPolicy(**payload)
        return build_default_output_rate_limit_policy()

    def _result(
        self,
        *,
        intent: LocalOutputIntentRecord,
        status: str,
        rendered_text: str | None,
        sound_played: bool,
        cancelled: bool,
        muted: bool,
        rate_limited: bool,
        failure_kind: str | None,
        retryable: bool,
        source_trace_refs: tuple[str, ...],
    ) -> OutputDispatchResultRecord:
        return OutputDispatchResultRecord(
            dispatch_result_id=stable_id("output_dispatch_result"),
            schema_version=DISPATCH_RESULT_SCHEMA_VERSION,
            created_at=utc_now(),
            output_intent_id=intent.output_intent_id,
            sink_kind="local_text_surface",
            dispatch_status=status,
            rendered_text=rendered_text,
            sound_played=sound_played,
            cancelled=cancelled,
            muted=muted,
            rate_limited=rate_limited,
            failure_kind=failure_kind,
            retryable=retryable,
            qingyin_authored=intent.qingyin_authored,
            fixture_only=intent.fixture_only,
            source_trace_refs=source_trace_refs,
        )

    def _record_result(self, result: OutputDispatchResultRecord, event_kind: str, message: str) -> None:
        self.store.append_dispatch_result(result)
        level = "warning" if result.dispatch_status.startswith("blocked") else "notice"
        self.store.append_status_log(
            build_operator_status_log_entry(
                level=level,
                event_kind=event_kind,
                operator_message=message,
                source_module="ashl_core_v1.runtime.local_non_llm_output_dispatcher",
                source_record_refs=(result.output_intent_id, result.dispatch_result_id),
                source_trace_refs=result.source_trace_refs,
            )
        )
        self.events.append_event(
            event_kind=event_kind,
            source_record_refs=(result.output_intent_id, result.dispatch_result_id),
            source_trace_refs=result.source_trace_refs,
        )
