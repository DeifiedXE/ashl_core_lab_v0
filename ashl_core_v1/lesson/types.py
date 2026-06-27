"""First-stage learning intake and review data shapes for ASHL Core v1."""

from dataclasses import dataclass, fields
from typing import Any, ClassVar


def _plain(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_plain(item) for item in value]
    if isinstance(value, dict):
        return {key: _plain(item) for key, item in value.items()}
    return value


def _range_0_1(name: str, value: float) -> float:
    numeric = float(value)
    if not 0.0 <= numeric <= 1.0:
        raise ValueError(f"{name} must be between 0.0 and 1.0")
    return numeric


def _tuple_of_str(name: str, value: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    refs = tuple(value)
    if not all(isinstance(item, str) for item in refs):
        raise TypeError(f"{name} must contain only strings")
    return refs


@dataclass(frozen=True)
class LearningDigest:
    """Learning intake draft produced before teacher review."""

    learning_digest_id: str
    source_perception_refs: tuple[str, ...]
    source_endocrine_refs: tuple[str, ...]
    before_state_ref: str | None
    event_or_action_ref: str | None
    after_state_ref: str | None
    digest_type: str
    digest_payload: dict[str, object]
    generalization_scope: str
    uncertainty: float
    source_trace_refs: tuple[str, ...]
    review_required: bool = True

    def __post_init__(self) -> None:
        if not self.learning_digest_id:
            raise ValueError("learning_digest_id is required")
        if not self.digest_type:
            raise ValueError("digest_type is required")
        if not self.generalization_scope:
            raise ValueError("generalization_scope is required")
        object.__setattr__(
            self,
            "source_perception_refs",
            _tuple_of_str("source_perception_refs", self.source_perception_refs),
        )
        object.__setattr__(
            self,
            "source_endocrine_refs",
            _tuple_of_str("source_endocrine_refs", self.source_endocrine_refs),
        )
        object.__setattr__(self, "digest_payload", dict(self.digest_payload))
        object.__setattr__(self, "uncertainty", _range_0_1("uncertainty", self.uncertainty))
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )
        object.__setattr__(self, "review_required", bool(self.review_required))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "LearningDigest":
        return cls(**dict(data))


@dataclass(frozen=True)
class LearningReviewRecord:
    """Human teacher review record for a LearningDigest."""

    ALLOWED_REVIEW_STATUSES: ClassVar[set[str]] = {
        "approved",
        "rejected",
        "deferred",
        "needs_more_evidence",
        "conflict_detected",
    }

    review_record_id: str
    source_learning_digest_id: str
    review_status: str
    teacher_note: str
    reviewer_ref: str
    approved_scope: str | None
    created_at_tick: int | None = None

    def __post_init__(self) -> None:
        if not self.review_record_id:
            raise ValueError("review_record_id is required")
        if not self.source_learning_digest_id:
            raise ValueError("source_learning_digest_id is required")
        if self.review_status not in self.ALLOWED_REVIEW_STATUSES:
            raise ValueError(f"unknown review_status: {self.review_status}")
        if not self.reviewer_ref:
            raise ValueError("reviewer_ref is required")

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "LearningReviewRecord":
        return cls(**dict(data))


@dataclass(frozen=True)
class ReviewedLearningDigest:
    """Reviewed learning data that may enter the memory module."""

    ALLOWED_REVIEW_STATUSES: ClassVar[set[str]] = LearningReviewRecord.ALLOWED_REVIEW_STATUSES

    reviewed_digest_id: str
    source_learning_digest_id: str
    source_review_record_id: str
    review_status: str
    approved_scope: str | None
    reviewed_payload: dict[str, object]
    source_trace_refs: tuple[str, ...]
    memory_entry_allowed: bool

    def __post_init__(self) -> None:
        if not self.reviewed_digest_id:
            raise ValueError("reviewed_digest_id is required")
        if not self.source_learning_digest_id:
            raise ValueError("source_learning_digest_id is required")
        if not self.source_review_record_id:
            raise ValueError("source_review_record_id is required")
        if self.review_status not in self.ALLOWED_REVIEW_STATUSES:
            raise ValueError(f"unknown review_status: {self.review_status}")
        if self.review_status != "approved" and self.memory_entry_allowed:
            raise ValueError("memory_entry_allowed can be true only when review_status is approved")
        object.__setattr__(self, "reviewed_payload", dict(self.reviewed_payload))
        object.__setattr__(
            self,
            "source_trace_refs",
            _tuple_of_str("source_trace_refs", self.source_trace_refs),
        )
        object.__setattr__(self, "memory_entry_allowed", bool(self.memory_entry_allowed))

    def to_dict(self) -> dict[str, object]:
        return {field.name: _plain(getattr(self, field.name)) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ReviewedLearningDigest":
        return cls(**dict(data))
