---
title: "Escalation Policy"
category: escalation
version: v1
---

# Escalation Policy

> **Fictional demo content.** NovaCart is not a real company. This document
> is a synthetic support-knowledge article created for a portfolio project
> and does not represent the real internal process of any business.

## Overview

This policy defines when a customer support case should move beyond
standard self-service or first-line agent handling to a specialist team or
human reviewer. It exists so that both automated assistants and human
agents apply escalation consistently, and so customers are never left
without a clear next step when a policy document does not fully resolve
their issue.

## Core Principle

If the available knowledge base does not contain enough information to
safely and accurately resolve a customer's issue, the correct action is to
**say so explicitly and escalate** — never to guess, improvise a policy
that isn't documented, or promise an outcome that isn't confirmed. This
applies equally to human agents and to any AI-assisted response system
built on top of this knowledge base.

## Escalation Tiers

| Tier | Who handles it | Typical response time |
|---|---|---|
| Tier 0 — Self-service | Knowledge base, FAQ, automated assistant | Immediate |
| Tier 1 — General support agent | Trained generalist agent | Same business day |
| Tier 2 — Specialist team | Billing, technical, or trust & safety specialist | 1–2 business days |
| Tier 3 — Senior review | Team lead or policy exception reviewer | 2–5 business days |

Every case starts at the lowest tier that can plausibly resolve it and
escalates upward only when needed — this keeps simple issues fast while
still guaranteeing complex ones get proper attention.

## When to Escalate from Tier 0/1 to Tier 2

- The knowledge base has no matching policy for the customer's situation,
  or the retrieved information is only partially relevant and a confident
  answer cannot be given.
- The customer explicitly disputes a decision already made (e.g., a denied
  refund, a rejected cancellation, a failed identity verification) and
  provides new information that wasn't part of the original decision.
- The case involves financial amounts above standard authority — for
  example, refunds over $500 that fall outside the documented rules in
  `refund_policy.md`.
- The case involves suspected account compromise (`account_recovery.md`)
  or unauthorized charges (`payment_faq.md`).
- The case involves a potential safety issue (e.g., a device reported as
  overheating, smoking, or otherwise hazardous, per
  `router_troubleshooting.md` and `technical_support.md`).
- The same underlying problem has recurred after two prior resolution
  attempts (e.g., a second replacement device also fails).
- The customer is a NovaCart Plus or business account with a contractual
  service-level agreement not covered by standard consumer policies.

## When to Escalate from Tier 2 to Tier 3

- Resolving the case requires an exception to a documented policy (e.g.,
  refunding outside the 30-day window for a reason not listed as an
  exception).
- The case involves legal, regulatory, or safety liability.
- The case involves a formal complaint about NovaCart staff conduct.
- A specialist has reviewed the case and genuinely cannot reach a
  confident decision within the documented policies.

## What "Insufficient Information" Looks Like

An automated assistant or agent should recognize these signals that a case
needs escalation rather than a direct answer:

- The retrieved knowledge base sources have low relevance to the actual
  question asked.
- The customer's question combines multiple policy areas in a way no
  single document fully covers (e.g., a refund request tied to a disputed
  cancellation *and* a possible account compromise).
- The customer references a prior conversation, promise, or exception that
  isn't reflected in any available record.
- Answering confidently would require inventing a number, date, or rule
  not stated in any policy document.

In all of these cases, the correct response is to clearly tell the
customer that the available information is not sufficient to resolve this
specific point, and that the case is being escalated — not to fill the gap
with a plausible-sounding but unverified answer.

## What Happens After Escalation

1. The case is tagged with a category (billing, technical, account
   security, safety, policy exception) and routed to the appropriate
   specialist queue.
2. The customer receives a reference number and an expected response
   window based on the tier (see table above).
3. The specialist reviews the full case history — the customer should not
   need to repeat information already provided.
4. The customer is notified of the outcome through the same channel the
   case was opened in (email, in-app notification, or chat).

## What Agents and Automated Assistants Must Never Do

- Never claim an action has been completed (a refund issued, a case
  closed, a device replaced) unless the system has actually confirmed it.
- Never invent a policy detail, dollar amount, timeframe, or exception
  that is not present in `refund_policy.md`, `cancellation_policy.md`,
  `payment_faq.md`, `account_recovery.md`, `delivery_faq.md`,
  `technical_support.md`, `router_troubleshooting.md`, or `general_faq.md`.
- Never ask for a password, full card number, or one-time passcode as part
  of resolving or escalating a case.
- Never discourage a customer from escalating; if a customer asks to speak
  with a specialist or supervisor, this request itself is honored and
  routed, even if the agent believes the issue is resolvable at the
  current tier.

## Priority Handling Within Escalations

Escalated cases are additionally marked with a priority level:

- **High** — safety issues, suspected account compromise, or financial
  harm already in progress.
- **Medium** — a clear policy question or dispute without immediate harm.
- **Low** — a policy clarification request or an edge case with no urgent
  customer impact.

Priority affects queue ordering within a tier; it does not skip tiers.

## Worked Examples

**Example 1 — Straightforward Tier 1 resolution.** A customer asks how
long they have to return an unused item. This is fully answered by
`refund_policy.md` with no ambiguity, so it is resolved at Tier 0/1
without escalation.

**Example 2 — Escalation due to missing policy coverage.** A customer
asks whether they can get a refund for an item that broke 45 days after
delivery due to a manufacturing defect, but `refund_policy.md`'s 30-day
window has passed and the customer is asking specifically about a refund,
not a warranty replacement. Because the customer's framing doesn't cleanly
match either the refund window or a documented refund exception, and a
confident refund/no-refund answer would require going beyond what
`refund_policy.md` states, this is escalated to Tier 2 rather than
guessing — even though `technical_support.md` describes a related
warranty path, the specific question asked (a refund, not a replacement)
isn't fully answered by either document alone.

**Example 3 — Immediate Tier 2 due to safety signal.** A customer mentions
their router "got really hot and made a popping sound" while also asking
about a Wi-Fi speed issue. Even though the Wi-Fi question could be
answered from `router_troubleshooting.md`, the safety signal takes
priority: the response should tell the customer to unplug the device
immediately and escalate as High priority, rather than walking through
routine speed troubleshooting first.

**Example 4 — Escalation from a disputed decision.** A customer's refund
was denied because the item showed signs of use. The customer replies that
the "signs of use" were actually pre-existing shipping damage they
photographed on arrival but never reported. This is new information not
part of the original decision, so it is escalated to Tier 2 for review
rather than the original denial simply being repeated.

## Frequently Misunderstood Points

- **Escalation is not a failure state** — it is the correct outcome
  whenever a case genuinely falls outside documented policy, and should
  never be avoided just to appear efficient.
- **A safety signal escalates immediately, even mid-conversation** about
  something else entirely; it doesn't wait for the original topic to be
  resolved first.
- **Tier skipping is not allowed** — a Tier 0/1 case that can't be
  resolved goes to Tier 2 first, not straight to Tier 3, unless it clearly
  involves legal/regulatory/safety liability or staff conduct from the
  start.
- **"I want a supervisor" is always honored** — an agent should never try
  to talk a customer out of escalating, even if the agent is confident
  they could resolve it directly.
- **Priority affects ordering, not eligibility** — a Low-priority
  escalation still gets escalated; it just isn't handled ahead of High or
  Medium cases in the same tier's queue.

## Test Questions

1. What should happen if a customer's question doesn't match anything in
   the knowledge base?
2. Under what circumstances does a case get escalated straight to senior
   review instead of a specialist team?
3. Is it ever acceptable for an agent to tell a customer a refund has been
   issued before confirming it actually was?
4. What information should a customer not have to repeat once their case
   has been escalated?
