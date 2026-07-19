"""Neutral raw output token registry for Package 122B."""

from __future__ import annotations

from ashl_core_v1.runtime.operator_console_types import RAW_OUTPUT_TOKEN_SCHEMA_VERSION, VALID_TOKEN_CODES, RawOutputToken


def build_raw_output_token_registry() -> tuple[RawOutputToken, ...]:
    return tuple(
        RawOutputToken(
            token_id=f"raw_output_token:{code}",
            schema_version=RAW_OUTPUT_TOKEN_SCHEMA_VERSION,
            token_code=code,
            output_channel="local_text_surface",
            semantic_label=None,
            predefined_meaning=None,
            enabled=True,
        )
        for code in VALID_TOKEN_CODES
    )


def validate_raw_output_tokens(token_codes: tuple[str, ...]) -> tuple[str, ...]:
    tokens = tuple(str(token) for token in token_codes)
    invalid = [token for token in tokens if token not in VALID_TOKEN_CODES]
    if invalid:
        raise ValueError(f"invalid raw output tokens: {invalid}")
    return tokens
