"""Thought hints, purpose, and thought-context line for ASHL Core v1."""

from .types import InfluenceTrace, ThoughtReadTrace, ThoughtSignal
from .instinct_layer_types import (
    BoundedInstinctSignalRecord,
    InstinctEvaluationBundleRecord,
    InstinctEvidenceContextRecord,
    InstinctLayerConsumerBoundaryRecord,
    InstinctRuleContractRecord,
    InstinctRuleEvaluationRecord,
)
from .specialized_thought_types import (
    BoundedSpecializedThoughtResultRecord,
    SpecializedThoughtCrossFamilyConflictRecord,
    SpecializedThoughtInstinctConsumerBindingRecord,
    SpecializedThoughtRuleFamilyContractRecord,
)

__all__ = [
    "InfluenceTrace",
    "ThoughtReadTrace",
    "ThoughtSignal",
    "BoundedInstinctSignalRecord",
    "InstinctEvaluationBundleRecord",
    "InstinctEvidenceContextRecord",
    "InstinctLayerConsumerBoundaryRecord",
    "InstinctRuleContractRecord",
    "InstinctRuleEvaluationRecord",
    "BoundedSpecializedThoughtResultRecord",
    "SpecializedThoughtCrossFamilyConflictRecord",
    "SpecializedThoughtInstinctConsumerBindingRecord",
    "SpecializedThoughtRuleFamilyContractRecord",
]
