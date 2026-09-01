---
title: "Payment FAQ"
category: payment
version: v1
---

# Payment FAQ

> **Fictional demo content.** NovaCart is not a real company. This document
> is a synthetic support-knowledge article created for a portfolio project
> and does not represent the policy of any real business. It does not
> collect or reference real payment credentials.

## Overview

This FAQ answers the most common questions about paying for NovaCart
orders and subscriptions: accepted payment methods, failed charges,
duplicate charges, disputed charges, and general billing security. It never
asks customers to share full card numbers, passwords, or one-time codes —
see the Security Note at the end.

## Accepted Payment Methods

- Major credit and debit cards.
- A NovaCart-branded digital wallet, funded by card or bank transfer.
- Store credit and NovaCart gift cards.
- "Pay in 4" installment plans on orders over $50, provided through a
  third-party installment partner and subject to that partner's approval.
- Bank transfer for business accounts only, arranged through account
  management (not available at standard checkout).

NovaCart does not accept cash on delivery, checks by mail, or
cryptocurrency at this time.

## Why Was My Payment Declined?

Common reasons a charge is declined:

1. **Insufficient funds or credit limit reached** — the card issuer blocks
   the charge; NovaCart never sees the account balance, only the decline
   code.
2. **Billing address mismatch** — the address entered at checkout does not
   match the address on file with the card issuer.
3. **Card expired or details mistyped** — double-check the card number,
   expiry date, and CVV.
4. **Issuer fraud flag** — some banks automatically decline first-time
   online purchases or unusually large orders; contacting the bank
   directly usually resolves this fastest.
5. **Temporary NovaCart payment processor outage** — rare, but if many
   customers report declines within a short window, this is investigated
   as a system issue rather than an individual account issue.

If a payment is declined, no charge is made and no funds are held — the
order simply does not complete. Customers can retry with the same or a
different payment method.

## Why Do I See a Pending Charge That's More Than My Order Total?

Some card issuers place a temporary authorization hold slightly higher
than the order total (commonly for tips-eligible or estimate-based
purchases, or as a fraud-prevention buffer). This hold is not an actual
charge. It is released automatically by the issuer, typically within 1–7
business days, and NovaCart never captures more than the actual order
total.

## I Was Charged Twice for One Order

This can happen when a payment retry occurs after a slow network response,
even though only one order was created. NovaCart's system automatically
detects duplicate authorizations tied to the same order and voids the
extra one within 3 business days. If both charges show as fully posted
(not just pending) after 3 business days, this should be treated as a
billing dispute — see below.

## Disputing a Charge

A customer should open a payment dispute when:

- They were charged for an order they did not place.
- They were charged the wrong amount and a refund request (see
  `refund_policy.md`) does not resolve it.
- A subscription charge occurred after cancellation was confirmed (see
  `cancellation_policy.md`).

To dispute a charge:

1. Go to **Account → Billing → Transaction History**.
2. Select the charge and choose **Report a Problem**.
3. Choose a reason and submit. NovaCart opens an internal billing case,
   typically resolved within 5 business days.

Customers can also dispute a charge directly with their card issuer at any
time; NovaCart responds to issuer inquiries with order and delivery
evidence when this happens, which is standard for any online retailer.

## Saved Payment Methods

- Customers may save one or more cards for faster checkout. Saved cards
  are tokenized by NovaCart's payment processor; NovaCart's own systems do
  not store full card numbers.
- Saved cards can be removed at any time from **Account → Payment
  Methods**.
- An expired saved card is flagged in the account but not automatically
  deleted, in case the customer wants to update the expiry date instead.

## Installment Plans ("Pay in 4")

- Available on eligible orders over $50.
- The first installment is charged at checkout; the remaining three are
  charged automatically every two weeks to the same payment method.
- Missed installment payments are handled by the installment partner
  directly, not by NovaCart; NovaCart's role is limited to providing order
  details for the partner's approval decision.
- Cancelling or returning an order paid via installments follows
  `refund_policy.md`; any installments already paid are refunded, and
  future scheduled installments are cancelled.

## Currency and Taxes

- Prices are shown in the currency of the customer's selected storefront
  region.
- Applicable sales tax or VAT is calculated at checkout based on the
  shipping address and shown before payment is confirmed.
- NovaCart does not add hidden fees after checkout; if a customer sees a
  charge different from the confirmed order total, this should be treated
  as a billing dispute.

## Gift Cards and Store Credit

- Gift cards never expire and have no fees.
- Store credit issued from a refund also never expires.
- Multiple gift cards can be applied to a single order; any remaining
  balance stays on the card for future use.
- Gift card balances cannot be converted to cash or transferred to a bank
  account.

## Security Note

NovaCart support will never ask a customer for:

- A full card number, CVV, or online banking password.
- A one-time passcode (OTP) sent by their bank or by NovaCart.
- Remote access to their device to "fix" a payment issue.

Any message requesting these should be treated as a scam and reported
through **Support → Report Suspicious Activity**, not acted upon.

## Escalation

If a billing dispute is not resolved within 5 business days, or a customer
reports unauthorized charges they did not make, this should be escalated
immediately per `escalation_policy.md`, since it may indicate account
compromise (see also `account_recovery.md`).

## Worked Examples

**Example 1 — Address-mismatch decline.** A customer recently moved and
updated their shipping address in NovaCart but not their billing address
with their card issuer. Checkout is declined. The fix is not a NovaCart
setting — the customer should either enter the billing address exactly as
it appears with their card issuer, or contact the issuer to update it on
their end.

**Example 2 — Authorization hold confusion.** A customer orders a $120
item and sees a pending charge of $135 on their banking app the same day.
This is a temporary issuer-side authorization buffer, not an overcharge;
NovaCart only captures $120, and the extra hold releases automatically,
typically within a week, without any action needed from NovaCart.

**Example 3 — Genuine duplicate charge.** A customer's order shows one
order confirmation, but their bank statement shows two identical posted
(not pending) charges four days after the order. Since this is beyond the
3-business-day automatic-detection window and both charges are fully
posted, this should be treated as a billing dispute rather than assumed to
self-resolve.

**Example 4 — Installment plan return.** A customer paid for a $200 item
using Pay-in-4 and has completed two of the four $50 installments when
they return the item. The two paid installments are refunded, and the two
remaining scheduled installments are cancelled so the customer is never
charged for an item they no longer have.

## Frequently Misunderstood Points

- **A decline does not mean a charge occurred.** No funds move on a
  declined transaction; there is nothing to "refund" for a simple decline.
- **A pending amount is not the final amount.** Authorization holds can be
  higher than the order total; only the captured amount matters for what
  the customer actually pays.
- **Support cannot see or request full card numbers.** Any interaction
  that asks for a full card number, not just the tokenized last four
  digits already on file, is not a legitimate NovaCart process.
- **Gift card balances are not cash-equivalent for refund purposes** — a
  refund to a gift-card-funded purchase returns as store credit, not to a
  bank account, mirroring the original payment method.
- **Installment plan approval is decided by the installment partner, not
  NovaCart**, so NovaCart support cannot override a declined Pay-in-4
  application.

## How Payment Issues Relate to Other Policies

Payment problems often overlap with other documents: a payment dispute
tied to an order that never arrived should also reference
`delivery_faq.md`; a payment dispute tied to a return should reference
`refund_policy.md`; and any payment issue combined with signs of
unauthorized account access should be treated first as a possible account
compromise per `account_recovery.md`, since securing the account takes
priority over resolving an individual charge.

## Test Questions

1. Why might my card be declined even though I have enough money in my
   account?
2. I see a pending charge higher than my order total — will I actually be
   billed that amount?
3. What should I do if I think I was charged for an order I never placed?
4. Would NovaCart support ever ask me for my card's CVV over chat?
