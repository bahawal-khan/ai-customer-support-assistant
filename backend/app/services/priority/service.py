"""Phase 12 priority rules.

docs/backend/BACKEND_SPEC.md: "PriorityService: Executes deterministic rules
initially." No priority taxonomy or rule is defined anywhere in the spec
pack (REQUIREMENTS.md, docs/api/API_SPEC.md, and
docs/architecture/SYSTEM_ARCHITECTURE.md all require a `priority` output but
none define how it is computed). Per CLAUDE.md's ambiguity rule this was not
invented silently -- the rule below (sentiment + a fixed "sensitive intent"
escalation list) was confirmed directly with the user before implementation.

Rule:
- high:   negative sentiment AND a sensitive intent
- medium: negative sentiment (any other intent), OR a sensitive intent with
          non-negative sentiment
- low:    otherwise
"""

from __future__ import annotations

from dataclasses import dataclass

PRIORITY_HIGH = "high"
PRIORITY_MEDIUM = "medium"
PRIORITY_LOW = "low"

# Intents (ml/distilbert/artifacts/v2/label_mapping.json) treated as
# high-impact: money/account-access/escalation related.
SENSITIVE_INTENTS = frozenset(
    {
        "payment_issue",
        "get_refund",
        "track_refund",
        "complaint",
        "contact_human_agent",
        "delete_account",
        "recover_password",
        "check_cancellation_fee",
    }
)

_NEGATIVE_SENTIMENT = "negative"


@dataclass(frozen=True)
class PriorityResult:
    level: str
    reason: str


class PriorityService:
    """Deterministic intent+sentiment priority rules (no ML, no external calls)."""

    def determine_priority(self, intent: str, sentiment: str) -> PriorityResult:
        sensitive = intent in SENSITIVE_INTENTS
        negative = sentiment == _NEGATIVE_SENTIMENT

        if negative and sensitive:
            return PriorityResult(
                PRIORITY_HIGH, f"Negative sentiment on a sensitive intent ('{intent}')."
            )
        if negative:
            return PriorityResult(PRIORITY_MEDIUM, "Negative sentiment detected.")
        if sensitive:
            return PriorityResult(
                PRIORITY_MEDIUM,
                f"Sensitive intent ('{intent}') reported without negative sentiment.",
            )
        return PriorityResult(PRIORITY_LOW, "No negative sentiment or sensitive intent detected.")
