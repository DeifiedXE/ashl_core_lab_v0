"""Reserved neutral sound-pattern descriptors for Package 122B."""

from __future__ import annotations

from ashl_core_v1.runtime.operator_console_types import (
    SOUND_PATTERN_SCHEMA_VERSION,
    VALID_SOUND_PATTERN_CODES,
    ReservedSoundPatternDescriptor,
)


def build_reserved_sound_pattern_registry() -> tuple[ReservedSoundPatternDescriptor, ...]:
    return tuple(
        ReservedSoundPatternDescriptor(
            sound_pattern_id=f"reserved_sound_pattern:{code}",
            schema_version=SOUND_PATTERN_SCHEMA_VERSION,
            pattern_code=code,
            oscillator_segments=tuple(
                {
                    "segment_index": index,
                    "duration_ms": 50,
                    "relative_frequency": round(1.0 + (index * 0.05), 3),
                    "relative_gain": 0.25,
                }
                for index in range(1)
            ),
            maximum_duration_ms=250,
            semantic_label=None,
            predefined_meaning=None,
            output_enabled=False,
        )
        for code in VALID_SOUND_PATTERN_CODES
    )


def get_reserved_sound_pattern(pattern_code_or_id: str) -> ReservedSoundPatternDescriptor:
    for pattern in build_reserved_sound_pattern_registry():
        if pattern.pattern_code == pattern_code_or_id or pattern.sound_pattern_id == pattern_code_or_id:
            return pattern
    raise ValueError(f"unknown reserved sound pattern: {pattern_code_or_id}")
