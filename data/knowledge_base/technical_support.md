---
title: "Technical Support"
category: technical_support
version: v1
---

# Technical Support

> **Fictional demo content.** NovaCart is not a real company. This document
> is a synthetic support-knowledge article created for a portfolio project
> and does not represent the real specifications of any product or company.

## Overview

This article covers general troubleshooting for NovaCart-sold electronics
(smart plugs, smart speakers, streaming devices, and home networking
equipment) that are not connecting, not powering on, or behaving
unexpectedly. Router-specific issues have a dedicated, more detailed guide
in `router_troubleshooting.md`; this document covers the shared basics that
apply across most NovaCart smart-home devices.

## Before You Start

Have the following ready, since support will usually ask for them:

- The exact product name and model number (usually on a label on the
  device or in the NovaCart app's device settings).
- The NovaCart order number, if requesting a warranty repair or
  replacement.
- Whether the device ever worked correctly, or has never worked since
  unboxing.

## Device Won't Power On

1. Confirm the power cable is fully seated at both the device and the
   outlet.
2. Try a different outlet to rule out a dead outlet or tripped circuit.
3. If the device uses a power adapter/brick, check for a small LED on the
   adapter itself, if present, to confirm the adapter is supplying power.
4. Hold the power button for 10 seconds to rule out a frozen state.
5. If the device still shows no sign of life (no LED, no sound, no
   warmth) after these steps, it likely has a hardware fault. Proceed to
   **Warranty and Replacement** below.

## Device Won't Connect to Wi-Fi

1. Confirm the home Wi-Fi network itself is online by checking another
   device (phone, laptop).
2. Make sure the device is within reasonable range of the router — most
   smart-home devices lose reliable connectivity beyond roughly 30 feet
   through multiple walls.
3. Many NovaCart smart devices only support 2.4GHz Wi-Fi, not 5GHz. If the
   home network broadcasts a single combined network name, temporarily
   splitting it into separate 2.4GHz and 5GHz names (in the router's
   settings) often resolves setup failures. See `router_troubleshooting.md`
   for router-side steps.
4. Forget the device's saved network in the NovaCart app and redo the
   setup/pairing process from scratch.
5. Restart the device (power cycle) and the router, in that order, waiting
   30 seconds between steps.
6. If the device connects but disconnects repeatedly (not a one-time
   failure), this points to a Wi-Fi stability issue rather than a device
   defect — see `router_troubleshooting.md`.

## App Shows "Device Offline" but It Seems to Be Working

This usually means the device lost contact with NovaCart's cloud service
even though it is still on the local network.

1. Check the NovaCart system status page in the app (**Settings → System
   Status**) for a known outage.
2. Restart the device.
3. Confirm the account is signed in on the same NovaCart account that
   originally set up the device — devices moved between accounts without
   proper transfer can appear offline to the new account.
4. If only one device out of several is affected, the issue is more likely
   device-specific; if all devices on the account show offline
   simultaneously, it is more likely an account, app, or network-wide
   issue.

## Firmware Updates

- Most devices update automatically when idle and connected to power and
  Wi-Fi.
- Manual updates can be triggered from **Device Settings → Firmware →
  Check for Updates** in the NovaCart app.
- A device stuck "updating" for more than 30 minutes should be power
  cycled once; this is safe and does not corrupt the update in the vast
  majority of cases, though it may require restarting the update from the
  beginning.
- NovaCart does not recommend downgrading firmware manually; if a recent
  update caused a regression, support should be contacted so it can be
  reported and a fix can be issued centrally.

## Factory Reset

A factory reset erases all device settings and removes it from the
account. Use this as a last resort, or when preparing to give the device
to someone else.

1. In the app: **Device Settings → Advanced → Factory Reset**.
2. Physically, most devices support a reset via a recessed button held for
   10–15 seconds (exact timing varies by product; check the product's
   quick-start guide, viewable in **Device Settings → Manuals**).
3. After resetting, the device must be set up again from the NovaCart app
   as if new.

## App Issues (Not Device-Specific)

- Force-close and reopen the NovaCart app.
- Confirm the app is up to date in the relevant app store.
- Sign out and back in if devices are missing from the dashboard after an
  update.
- Clear the app's cache (Android: app info → storage → clear cache; this
  does not delete account data) if the app is slow or unresponsive.

## Warranty and Replacement

NovaCart-sold electronics include a **1-year manufacturer warranty**
against hardware defects, separate from the 30-day return window in
`refund_policy.md`.

- Within 30 days of delivery: a defective device is handled as a standard
  return/refund or replacement, per `refund_policy.md`.
- Between 30 days and 1 year: the device qualifies for a warranty
  replacement if troubleshooting confirms a hardware fault. The customer
  ships the faulty unit back using a prepaid label, and a replacement
  ships once the return is scanned by the carrier (not after it arrives at
  the warehouse, to minimize downtime).
- After 1 year: the device is out of warranty. Support can still advise on
  troubleshooting, but replacement is at the customer's own cost.
- Physical damage (drops, liquid, unauthorized modification) is not
  covered by the standard warranty; an optional protection plan
  (mentioned in `cancellation_policy.md`) can cover this if purchased.

## When to Escalate

Escalate to a specialist per `escalation_policy.md` when:

- The same device has failed troubleshooting twice and a third replacement
  is being considered.
- The issue affects a safety-relevant device category (e.g., smart locks,
  smoke/carbon-monoxide sensors).
- The customer reports the issue is affecting multiple devices
  simultaneously, which may indicate a broader NovaCart service issue
  rather than an individual device problem.

## Worked Examples

**Example 1 — Dead-on-arrival smart plug.** A customer unboxes a smart
plug and it shows no LED at all, even in a different outlet and after
holding the power button. Since there is no sign of life after the basic
checks, this is treated as a hardware fault. If it's within 30 days of
delivery, it's a standard return/replacement under `refund_policy.md`; a
device this clearly non-functional does not need extended troubleshooting
before offering a replacement.

**Example 2 — Intermittent Wi-Fi drops on one speaker.** A smart speaker
connects fine but drops offline several times a day, while every other
device on the same network stays connected. Because only one device is
affected, this points to a device-specific issue (possibly a weak Wi-Fi
antenna) rather than a network-wide problem, and troubleshooting should
focus on the device: distance from the router, band (2.4GHz vs 5GHz), and
a factory reset before considering replacement.

**Example 3 — Firmware update stuck at 40%.** A device shows "Updating…"
for 45 minutes with no progress. Since this exceeds the 30-minute
guidance, a single power cycle is appropriate; if the update restarts
cleanly and completes, no further action is needed. If it gets stuck
again, this should be reported rather than repeatedly power-cycled, since
repeated interruption risks corrupting the firmware.

**Example 4 — Warranty replacement at month 4.** A device that worked
correctly for three months develops a hardware fault (won't power on).
Because this is past the 30-day return window but within the 1-year
warranty, the customer ships the faulty unit back with a prepaid label,
and NovaCart ships the replacement as soon as the carrier scans the
returned package, not after it physically arrives at the warehouse.

## Frequently Misunderstood Points

- **A device that "never worked since unboxing" is treated differently
  from one that "used to work and stopped."** The former is more likely a
  setup or hardware defect from the start; the latter is more likely a
  network change, firmware issue, or wear-related fault.
- **The 30-day return window and the 1-year warranty are not the same
  thing** — the return window is about the right to change your mind or
  get a fast no-questions-asked resolution; the warranty is specifically
  about confirmed hardware defects.
- **"Offline in the app" does not always mean "not working locally"** —
  some devices continue functioning on the local network (e.g., a smart
  plug can still be switched physically) even while cloud connectivity is
  down.
- **Clearing an app's cache does not delete account data** — customers
  are sometimes hesitant to do this, worrying it will sign them out of
  everything or remove their devices, but it only clears temporary local
  app data.
- **Moving a device between accounts must go through the app's official
  transfer flow** — simply resetting and re-adding a device without using
  transfer can leave it appearing offline to the new account.

## Relationship to Router Troubleshooting

If multiple unrelated devices lose connectivity at the same time, the
underlying problem is very likely the router or home network itself
rather than any individual device — in that case, `router_troubleshooting.md`
should be used instead of repeating this document's single-device steps
for each affected device.

## Test Questions

1. My smart plug won't connect to Wi-Fi during setup — what should I check
   first?
2. Is it safe to restart my device if a firmware update seems stuck?
3. What's the difference between the 30-day return window and the 1-year
   warranty for a defective device?
4. What information should I have ready before contacting support about a
   broken device?
