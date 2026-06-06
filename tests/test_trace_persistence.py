import copy
import json
import tempfile
import unittest
from pathlib import Path

from ashl_core.first_output_runtime import generate_minimal_first_output
from ashl_core.mentor_feedback_runtime import build_minimal_mentor_feedback_trace
from ashl_core.trace_persistence import (
    FIRST_OUTPUT_TRACES_FILENAME,
    MENTOR_FEEDBACK_TRACES_FILENAME,
    append_first_output_trace,
    append_mentor_feedback_trace,
)


def _first_output_trace(session_id: str = "final_check") -> dict:
    return generate_minimal_first_output(session_id=session_id)["first_output_trace"]


def _mentor_feedback_trace(session_id: str = "final_check") -> dict:
    first_trace = _first_output_trace(session_id)
    return build_minimal_mentor_feedback_trace(
        source_first_output_trace_id=first_trace["trace_id"],
        session_id=first_trace["session_id"],
        tick=first_trace["tick"],
        mentor_feedback_label="observed",
    )


def _jsonl_rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


class TracePersistenceTests(unittest.TestCase):
    def test_append_first_output_trace_creates_jsonl_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace = _first_output_trace()
            summary = append_first_output_trace(trace, tmp)
            path = Path(tmp) / FIRST_OUTPUT_TRACES_FILENAME

            self.assertTrue(path.exists())
            self.assertEqual(_jsonl_rows(path), [trace])
            self.assertTrue(summary["append_only"])
            self.assertFalse(summary["overwrite"])
            self.assertFalse(summary["mutates_input"])

    def test_append_mentor_feedback_trace_creates_jsonl_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace = _mentor_feedback_trace()
            summary = append_mentor_feedback_trace(trace, tmp)
            path = Path(tmp) / MENTOR_FEEDBACK_TRACES_FILENAME

            self.assertTrue(path.exists())
            self.assertEqual(_jsonl_rows(path), [trace])
            self.assertTrue(summary["append_only"])
            self.assertFalse(summary["overwrite"])
            self.assertFalse(summary["mutates_input"])

    def test_second_append_adds_second_line_without_overwriting_first_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = _first_output_trace("session_one")
            second = _first_output_trace("session_two")
            append_first_output_trace(first, tmp)
            append_first_output_trace(second, tmp)
            rows = _jsonl_rows(Path(tmp) / FIRST_OUTPUT_TRACES_FILENAME)

            self.assertEqual(rows, [first, second])

    def test_missing_required_field_raises_value_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace = _first_output_trace()
            trace.pop("trace_id")

            with self.assertRaises(ValueError):
                append_first_output_trace(trace, tmp)

    def test_invalid_trace_type_raises_value_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace = _mentor_feedback_trace()
            trace["trace_type"] = "wrong_trace_type"

            with self.assertRaises(ValueError):
                append_mentor_feedback_trace(trace, tmp)

    def test_first_output_trace_with_llm_used_true_raises_value_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace = _first_output_trace()
            trace["llm_used"] = True

            with self.assertRaises(ValueError):
                append_first_output_trace(trace, tmp)

    def test_mentor_feedback_trace_with_creates_lesson_candidate_true_raises_value_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace = _mentor_feedback_trace()
            trace["creates_lesson_candidate"] = True

            with self.assertRaises(ValueError):
                append_mentor_feedback_trace(trace, tmp)

    def test_mentor_feedback_trace_with_writes_lesson_store_true_raises_value_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace = _mentor_feedback_trace()
            trace["writes_lesson_store"] = True

            with self.assertRaises(ValueError):
                append_mentor_feedback_trace(trace, tmp)

    def test_mentor_feedback_trace_with_writes_memory_layer_true_raises_value_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace = _mentor_feedback_trace()
            trace["writes_memory_layer"] = True

            with self.assertRaises(ValueError):
                append_mentor_feedback_trace(trace, tmp)

    def test_append_helpers_do_not_mutate_input_dict(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace = _mentor_feedback_trace()
            before = copy.deepcopy(trace)

            append_mentor_feedback_trace(trace, tmp)

            self.assertEqual(trace, before)


if __name__ == "__main__":
    unittest.main()
