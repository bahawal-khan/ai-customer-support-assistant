---
title: "Account Recovery"
category: account_recovery
version: v1
---

# Account Recovery

> **Fictional demo content.** NovaCart is not a real company. This document
> is a synthetic support-knowledge article created for a portfolio project
> and does not represent the policy of any real business. It does not
> describe real authentication systems and must not be used as a security
> reference.

## Overview

This article explains how a NovaCart customer can regain access to their
account if they forget their password, lose access to their two-factor
authentication (2FA) device, or believe their account has been
compromised. It also explains what NovaCart support can and cannot do to
help, since some recovery steps exist specifically to prevent account
takeover.

## Forgot Password

1. On the sign-in page, select **Forgot Password**.
2. Enter the email address associated with the account.
3. NovaCart sends a password reset link to that email, valid for **60
   minutes**.
4. Follow the link and choose a new password (minimum 10 characters,
   including at least one number and one letter).
5. All active sessions on other devices are signed out automatically once
   the password is changed, as a security measure.

If the reset email does not arrive within a few minutes, the customer
should check spam/junk folders and confirm they used the correct email
address. Support agents can resend the email but cannot read, generate, or
share a password reset link on the customer's behalf outside the standard
email flow.

## Lost Access to Two-Factor Authentication (2FA)

Customers who enabled 2FA (authenticator app or SMS) and lost access to
that device have two recovery paths:

### Backup Codes

At 2FA setup, NovaCart provides 10 one-time backup codes. Any unused
backup code can be entered at sign-in instead of the 2FA code to regain
access, after which the customer should generate a fresh set of codes and
re-configure 2FA.

### No Backup Codes Available

If backup codes were lost as well, the customer must complete **identity
verification** before 2FA is removed from the account:

1. Submit a request through **Sign In → Trouble signing in? → Lost my 2FA
   device**.
2. Confirm ownership of the account by verifying at least two of: the
   account email, a recent order number, the last four digits of a
   payment method on file, and the billing postal code.
3. NovaCart reviews the request, typically within 1–2 business days.
4. If verification succeeds, 2FA is reset and the customer is prompted to
   set a new password and re-enable 2FA.

This process is intentionally not instant. It exists to prevent someone
who is not the account owner from removing 2FA protection.

## Account Locked After Failed Sign-In Attempts

After 5 consecutive failed password attempts, NovaCart temporarily locks
the account for 15 minutes as a brute-force protection measure. The
customer can wait for the lock to expire or use **Forgot Password** to
reset immediately, which also clears the lock.

## Suspected Unauthorized Access

If a customer notices sign-ins from unfamiliar locations, orders they did
not place, or profile details (email, address, payment method) they did
not change, this should be treated as a possible account compromise:

1. The customer should immediately use **Forgot Password** to reset their
   password, which signs out all other sessions.
2. Review **Account → Security → Recent Activity** for unrecognized
   sign-ins or changes.
3. Review **Order History** for any unauthorized orders and report them
   through **Support → Report Suspicious Activity**; unauthorized orders
   are cancelled and refunded per `refund_policy.md` once confirmed.
4. Enable 2FA if it was not already active.
5. If a saved payment method may be compromised, remove it and contact the
   card issuer as well, since NovaCart cannot deactivate a card outside
   its own systems.

## Changing the Email on File

Customers can change their account email from **Account → Profile →
Email**, which requires confirming the current password and verifying the
new email address via a confirmation link. This link expires after 24
hours. If a customer no longer has access to their current email *and*
wants to change it, they must go through identity verification (same
process as the no-backup-codes 2FA case above), since email is a primary
recovery channel and changing it blind would weaken account security.

## What Support Agents Can and Cannot Do

**Can:**
- Resend a password reset email to the address on file.
- Guide a customer through identity verification.
- Reset 2FA after identity verification succeeds.
- Review account activity logs with the customer to identify suspicious
  actions.

**Cannot:**
- Read or reset a password directly (NovaCart does not store passwords in
  a readable form).
- Disable 2FA without identity verification, even if the customer sounds
  urgent or upset.
- Share any account details (email, address, order history, payment last
  four digits) with someone who has not passed identity verification,
  even if they claim to be the account owner.
- Accept a password, OTP, or backup code read aloud by the customer as a
  way to "prove" identity — sharing these with support is never required
  and should be actively discouraged, since it also protects the customer
  from social-engineering scams.

## Account Deletion Requests

Customers can request permanent account deletion from **Account → Privacy
→ Delete Account**. This requires password confirmation and a 7-day
cooling-off period during which the request can be cancelled by simply
signing back in. After 7 days, the deletion is processed and cannot be
reversed by support.

## Escalation

Identity verification failures that a customer disputes, suspected account
takeover with financial impact, or any recovery request that cannot be
resolved through the standard flow above should be escalated per
`escalation_policy.md`.

## Worked Examples

**Example 1 — Simple password reset.** A customer forgets their password
but still receives email normally. They use **Forgot Password**, get the
reset link within a minute, set a new password, and are automatically
signed out of an old session on a tablet they no longer use. This is the
fastest and most common recovery path and requires no agent involvement.

**Example 2 — Lost phone, backup codes saved.** A customer's phone with
their authenticator app is stolen. They had saved their 10 backup codes in
a notes app on their laptop. They sign in with a backup code, are prompted
to reconfigure 2FA on a new device, and generate a fresh set of backup
codes. No identity verification is needed because they still hold a valid
account credential (a backup code).

**Example 3 — Lost phone, no backup codes.** The same scenario, but the
customer never saved backup codes. They must go through the identity
verification flow: confirming the account email, a recent order number,
and the last four digits of a card on file. This takes 1–2 business days,
which can feel slow to an anxious customer, but exists specifically so
that someone who merely knows the account email cannot strip 2FA from an
account they don't own.

**Example 4 — Suspected takeover.** A customer notices an order for an
expensive item they never placed, shipping to an address they don't
recognize. They reset their password immediately (signing out all
sessions), report the order as unauthorized, and enable 2FA, which had
been off. The unauthorized order is cancelled and refunded once confirmed,
following `refund_policy.md`, and the case is escalated because financial
harm was already in progress.

## Frequently Misunderstood Points

- **Support truly cannot read a password.** This isn't a policy choice
  agents are enforcing reluctantly — passwords aren't stored in a
  reversible form, so there is nothing for an agent to look up.
- **A backup code and a password are not interchangeable.** A backup code
  only replaces the 2FA step; the account password is still required
  first.
- **Verifying "two of four" identity signals doesn't mean any two random
  facts** — it specifically means two of the listed items (email, recent
  order number, card last-four, billing postal code), not arbitrary
  personal details.
- **Changing the email on file is not simple if the old email is also
  lost** — losing both the password *and* email access at once requires
  the full identity-verification path, since email is itself a recovery
  channel.
- **Account deletion has a 7-day cooling-off period** specifically so an
  accidental or coerced deletion request can still be reversed by simply
  signing back in.

## Why Recovery Isn't Always Instant

Some customers are frustrated that identity verification isn't immediate,
especially when they're locked out of an account they clearly own. The
1–2 business day window exists because the alternative — instantly
removing 2FA or changing account email based on a single unverified claim
— would make account takeover trivially easy for an attacker who simply
claims to be the real owner. Agents should explain this reasoning rather
than simply citing the delay as a fixed rule.

## Test Questions

1. What should I do if I lost my phone and can't get my two-factor
   authentication code anymore?
2. Can a support agent just tell me what my password is if I forget it?
3. What steps should I take if I notice an order in my account that I
   didn't place?
4. Why isn't 2FA removed from my account immediately when I ask for it?
