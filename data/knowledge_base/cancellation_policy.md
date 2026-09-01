---
title: "Cancellation Policy"
category: cancellation
version: v1
---

# Cancellation Policy

> **Fictional demo content.** NovaCart is not a real company. This document
> is a synthetic support-knowledge article created for a portfolio project
> and does not represent the policy of any real business.

## Overview

This policy explains how and when customers can cancel an order, a
subscription, or an installation/service appointment with NovaCart, and
what happens to payments and shipments already in progress. It works
alongside `refund_policy.md`, which governs money returned once a
cancellation is processed.

## Cancelling a Product Order

Orders move through four stages: **Placed → Processing → Shipped →
Delivered**. Cancellation rules depend on the stage.

### Placed (not yet processing)

- Free, instant cancellation from **Order History → Cancel Order**.
- Full refund of the charge (or the authorization is simply released and
  never captured, depending on payment method).
- Available for up to 30 minutes after checkout, or until the warehouse
  begins picking the item, whichever is sooner.

### Processing (warehouse has started picking/packing)

- Cancellation is no longer self-service in the app.
- Customers must contact support; NovaCart will attempt to intercept the
  shipment.
- If interception succeeds, the order is cancelled and fully refunded minus
  nothing (no fee).
- If interception fails because the package has already left the
  warehouse, the order converts automatically to a standard return once
  delivered, following `refund_policy.md`.

### Shipped

- The order cannot be cancelled in transit.
- The customer may refuse delivery, or accept delivery and initiate a
  return under `refund_policy.md`.

### Delivered

- "Cancellation" no longer applies; this is a return, governed entirely by
  `refund_policy.md`.

## Cancelling a Subscription (NovaCart Plus, protection plans, etc.)

NovaCart offers renewable subscriptions such as NovaCart Plus (free
shipping and returns membership) and optional device protection plans.

1. Go to **Account → Subscriptions**.
2. Select the subscription and choose **Cancel Subscription**.
3. Choose whether to cancel **immediately** or **at the end of the current
   billing period**.

Rules:

- Cancelling immediately stops access right away. A prorated refund for the
  unused portion of the current period is issued **only** if the
  subscription was activated fewer than 14 days ago (the trial/cooling-off
  window). Outside that window, immediate cancellation does not refund the
  remaining days.
- Cancelling "at period end" keeps benefits active until the paid period
  finishes, then the subscription does not renew, and no proration applies
  because the customer used the full period they already paid for.
- Free trials can be cancelled at any time with zero charge, as long as
  cancellation happens before the trial's listed end date.
- If a subscription auto-renewed within the last 48 hours and the customer
  did not intend to renew, NovaCart treats this as an immediate-cancellation
  request with a full refund of that specific renewal charge, provided the
  customer has not materially used the renewed period's benefits (e.g.,
  filed a claim on a protection plan).

## Cancelling an Installation or Technician Appointment

For services such as smart-home device setup or router installation
booked through NovaCart:

- Free cancellation or rescheduling up to **24 hours** before the
  appointment window.
- Cancelling with **less than 24 hours' notice** may incur a $15
  missed-appointment fee, waived on the customer's first occurrence as a
  courtesy.
- If NovaCart needs to cancel or reschedule (technician unavailability,
  weather, etc.), no fee applies and the customer is offered priority
  rebooking.
- No-shows by the customer (technician arrives, no one is available) follow
  the same fee as a late cancellation.

## Cancelling During an Active Support or Repair Case

If a customer opens a repair or replacement case and later decides not to
proceed (for example, they fixed the issue themselves using
`technical_support.md` or `router_troubleshooting.md`), they can close the
case at any time from **Support → My Cases → Close Case**. Closing a case
does not affect any separate order or subscription cancellation.

## What Happens to Payment Authorizations

- A cancelled order that was only **authorized** (not yet captured) simply
  has the authorization released by NovaCart; funds typically become
  available again in 1–5 business days depending on the customer's bank,
  since NovaCart does not control bank-side hold release times.
- A cancelled order that was already **captured** (charged) is refunded per
  `refund_policy.md` processing times.

## Partial Cancellations

Multi-item orders can be partially cancelled — for example, cancelling one
item from a three-item order — as long as that specific item has not yet
started processing. The remaining items ship normally, and shipping charges
are recalculated only if the cancelled item was the sole reason a shipping
threshold (e.g., free shipping over $50) was met; in that case, the
recalculated shipping fee applies to the remaining items.

## Cancellation Confirmation

Every successful cancellation generates:

- An on-screen confirmation with a cancellation reference number.
- An email confirmation within a few minutes.
- An updated order status visible in **Order History**.

If a customer does not receive confirmation within 30 minutes of
cancelling, support should verify the cancellation actually went through
before assuming it failed, since email delivery can be delayed.

## Escalation

If a cancellation request is rejected because the order already shipped,
and the customer disputes the timing (e.g., they cancelled within the free
window but the system still charged them), this should be escalated per
`escalation_policy.md`. Agents must never mark a cancellation as complete
without confirming the order/subscription status has actually changed in
the system.

## Worked Examples

**Example 1 — Order cancelled just in time.** A customer places an order
at 3:00 PM and cancels at 3:20 PM. Since this is within the 30-minute
self-service window and before the warehouse began picking, the
cancellation is free, instant, and fully refunds any captured charge (or
simply releases the authorization if the charge had not yet been
captured).

**Example 2 — Order cancelled after picking started.** The same customer
instead cancels at 3:45 PM, after the warehouse has already begun packing.
Self-service cancellation is no longer available, so the customer contacts
support. Support attempts an interception; if the package has not yet left
the building, the interception succeeds and the order is cancelled with a
full refund and no fee. If the package has already left, the order
proceeds to delivery and becomes a standard return under
`refund_policy.md`.

**Example 3 — Subscription cancelled immediately after renewal.** A
NovaCart Plus membership renews on the 1st of the month. The customer
notices the renewal charge on the 2nd and cancels immediately, without
having used any Plus benefits since the renewal. Because the renewal
happened within the last 48 hours and no benefits were used, this is
treated as an immediate-cancellation request with a full refund of that
specific charge.

**Example 4 — Late appointment cancellation, first occurrence.** A
customer scheduled for a router installation cancels 6 hours before the
appointment window — inside the 24-hour notice requirement. Because this
is their first late cancellation, the $15 fee is waived as a courtesy; a
second late cancellation in the future would not automatically qualify for
the same waiver.

## Frequently Misunderstood Points

- **"Processing" does not mean "shipped."** A customer who sees their
  order status change to "Processing" has not lost the ability to cancel
  entirely — self-service is gone, but a support-assisted interception may
  still succeed if the package hasn't left the warehouse.
- **Cancelling "at period end" is not eligible for proration**, because the
  customer has already used (or had access to) the full period they paid
  for; proration only applies to the 14-day cooling-off window on new
  subscriptions.
- **A missed appointment and a late cancellation are treated the same**
  for fee purposes — showing up and finding no one home is not more
  lenient than cancelling late.
- **An authorization release is not a refund.** If an order was cancelled
  before the charge was captured, there is no "refund" in the strict
  sense — the bank simply releases a hold, and NovaCart does not control
  exactly how fast the customer's bank reflects that release.
- **Partial cancellation can change shipping cost.** Removing one item
  from a multi-item order can, in rare cases, drop the remaining order
  below a free-shipping threshold, which is why the recalculation rule
  exists.

## Relationship to Refunds

Cancellation and refund are related but distinct: a cancellation stops an
order or subscription *before* it is considered "delivered" or "used";
anything after that point is handled as a refund/return instead. Support
agents should determine which stage an order or subscription is in before
deciding whether `cancellation_policy.md` or `refund_policy.md` governs
the specific request, since the fee structures and refund amounts differ
between the two documents.

## Test Questions

1. Can I cancel my order for free if it hasn't started processing yet?
2. What happens if I try to cancel my subscription right after it
   auto-renewed?
3. Will I be charged a fee if I cancel my router installation appointment
   the same day it's scheduled?
4. If I cancel one item from a multi-item order, will my other items still
   ship on time?
