"""Phase 12 priority rule tests (docs/testing/TESTING_SPEC.md "Unit: priority rules").

Pure logic, no ML/DB/network dependency -- see
app/services/priority/service.py for the rule definition and the ambiguity
this resolves.
"""

from __future__ import annotations

from app.services.priority.service import (
    PRIORITY_HIGH,
    PRIORITY_LOW,
    PRIORITY_MEDIUM,
    SENSITIVE_INTENTS,
    PriorityService,
)


def test_negative_sentiment_on_sensitive_intent_is_high():
    service = PriorityService()

    result = service.determine_priority("payment_issue", "negative")

    assert result.level == PRIORITY_HIGH
    assert "payment_issue" in result.reason


def test_negative_sentiment_on_non_sensitive_intent_is_medium():
    service = PriorityService()

    result = service.determine_priority("track_order", "negative")

    assert result.level == PRIORITY_MEDIUM


def test_sensitive_intent_with_neutral_sentiment_is_medium():
    service = PriorityService()

    result = service.determine_priority("get_refund", "neutral")

    assert result.level == PRIORITY_MEDIUM


def test_sensitive_intent_with_positive_sentiment_is_medium():
    service = PriorityService()

    result = service.determine_priority("recover_password", "positive")

    assert result.level == PRIORITY_MEDIUM


def test_non_sensitive_intent_with_positive_sentiment_is_low():
    service = PriorityService()

    result = service.determine_priority("track_order", "positive")

    assert result.level == PRIORITY_LOW


def test_non_sensitive_intent_with_neutral_sentiment_is_low():
    service = PriorityService()

    result = service.determine_priority("delivery_options", "neutral")

    assert result.level == PRIORITY_LOW


def test_every_sensitive_intent_escalates_with_negative_sentiment():
    service = PriorityService()

    for intent in SENSITIVE_INTENTS:
        assert service.determine_priority(intent, "negative").level == PRIORITY_HIGH


def test_reason_is_always_non_empty():
    service = PriorityService()

    for intent in ["payment_issue", "track_order"]:
        for sentiment in ["negative", "neutral", "positive"]:
            result = service.determine_priority(intent, sentiment)
            assert result.reason
