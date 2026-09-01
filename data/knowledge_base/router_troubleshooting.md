---
title: "Router Troubleshooting"
category: router_troubleshooting
version: v1
---

# Router Troubleshooting

> **Fictional demo content.** NovaCart is not a real company. This document
> is a synthetic support-knowledge article created for a portfolio project.
> It describes generic, widely-applicable networking troubleshooting steps
> and does not represent the specifications of any real router model.

## Overview

This guide covers troubleshooting for NovaCart-sold home routers and
mesh Wi-Fi systems: no internet connection, slow or dropping Wi-Fi, setup
failures, and firmware problems. It is more detailed than
`technical_support.md` because router issues have the widest impact — a
router problem affects every other smart-home device on the network.

## Understanding the LED Status Lights

Most NovaCart routers use a single status light with these common
meanings (exact colors vary by model; check the quick-start guide in
**Device Settings → Manuals** for the specific model):

| Light behavior | Meaning |
|---|---|
| Solid green/blue | Online, functioning normally |
| Slow pulsing | Starting up or updating firmware |
| Fast blinking | Attempting to connect to the internet, not yet successful |
| Solid red/amber | Hardware fault or no internet signal detected |
| Off | No power reaching the device |

## No Internet Connection At All

1. **Check the modem/ISP connection first.** If the router connects to a
   separate modem, confirm the modem itself shows an online status. A
   router cannot provide internet if the modem has no signal from the
   internet service provider.
2. **Power cycle in the correct order**: unplug the modem, wait 30
   seconds, plug the modem back in and wait until its lights stabilize
   (1–2 minutes), then unplug and replug the router.
3. **Check physical cabling** — the cable between modem and router should
   be firmly seated in the WAN/Internet port on the router, not one of the
   LAN ports.
4. **Check for an ISP outage** using another connected device on cellular
   data, or the ISP's own status page/app.
5. If the modem is online but the router still shows no internet, the
   router's WAN connection type (DHCP, PPPoE, static IP) may be
   misconfigured — this is set in the router's admin panel and should
   match what the ISP requires.

## Wi-Fi Is Slow or Drops Frequently

1. **Check wired speed first.** Connect a device directly to the router
   with an ethernet cable and run a speed test. If wired speed is also
   slow, the problem is upstream of the router (modem or ISP), not the
   router or Wi-Fi itself.
2. **Reduce interference.** Move the router away from microwaves, cordless
   phones, baby monitors, and thick walls or metal surfaces where
   possible; these commonly degrade 2.4GHz Wi-Fi specifically.
3. **Switch or split bands.** 5GHz is faster at short range but has
   shorter reach; 2.4GHz reaches farther but is slower and more crowded.
   If the router broadcasts one combined network name, temporarily
   splitting it into two separate network names in **Router Settings →
   Wireless** can help diagnose whether a device is struggling to pick the
   right band.
4. **Check connected device count.** Older routers (and some budget
   models) slow down noticeably with 20+ simultaneously connected devices.
   NovaCart's mesh systems handle higher device counts better than
   single-unit routers.
5. **Change the Wi-Fi channel.** In congested apartment buildings, nearby
   networks on the same channel cause interference. Most NovaCart routers
   have an **Auto channel** setting in **Router Settings → Wireless →
   Advanced**; toggling it off and back on forces a rescan for a clearer
   channel.
6. **Update firmware** (see below) — Wi-Fi stability issues are one of the
   most common things fixed in firmware updates.

## Setup / Pairing Failures (New Router)

1. Confirm the router's default network name (printed on the device
   label) is visible from the phone or laptop doing setup.
2. Move closer to the router during initial setup — some setup flows
   require a stronger signal than normal day-to-day use.
3. Disable mobile data / cellular temporarily on the phone being used for
   setup, since some setup apps mistakenly use the cellular connection
   instead of the new Wi-Fi network.
4. If the NovaCart app repeatedly fails at the "connecting to your new
   network" step, factory reset the router (recessed button, 10 seconds)
   and restart setup from the beginning rather than retrying the same
   stuck step.

## Mesh System: One Satellite/Node Shows Offline

1. Confirm the offline node has power (check its status light).
2. Move the node closer to the main router or another online node — mesh
   nodes need to be within range of at least one other online node, not
   necessarily the main router directly.
3. Restart the offline node only; a full system restart is rarely needed
   for a single-node issue.
4. If the node stays offline after a restart and is within range, remove
   and re-add it to the mesh system from **Device Settings → Mesh
   Network → Manage Nodes**.

## Firmware Updates

- Router firmware updates automatically overnight by default when the
  router is idle; this can be disabled in **Router Settings → Firmware →
  Automatic Updates**, though NovaCart recommends leaving it enabled for
  security patches.
- A manual check is available at **Router Settings → Firmware → Check
  Now**.
- Never unplug a router mid-update; interrupted firmware updates can
  corrupt the device and require a warranty replacement rather than a
  simple reset. If an update appears stuck for more than 15 minutes,
  contact support before power cycling.

## Changing Wi-Fi Name or Password

1. **Router Settings → Wireless → Network Name/Password.**
2. Changing these disconnects all currently connected devices, which must
   reconnect using the new credentials.
3. NovaCart recommends a password of at least 12 characters; the app will
   warn about weak passwords but will not block them.

## Guest Network

Most NovaCart routers support a separate guest network, isolated from the
main network's connected devices for privacy. This is configured in
**Router Settings → Wireless → Guest Network** and can be toggled on/off
or given a time-limited access schedule.

## Resetting to Factory Defaults

A factory reset erases all custom settings, including Wi-Fi name,
password, and any port forwarding or advanced configuration.

1. In the app: **Device Settings → Advanced → Factory Reset**.
2. Physically: hold the recessed reset button for 10–15 seconds until the
   status light flashes rapidly.
3. After a factory reset, the router broadcasts its original default
   network name and must be set up again from the NovaCart app.

Use a factory reset only as a last resort for persistent issues, or before
giving the router to someone else — it does not fix a hardware fault.

## Warranty and Replacement

Router hardware faults (no lights at all, WAN/LAN ports not detecting a
cable, repeated crashes even on the latest firmware after a factory
reset) follow the same warranty terms as `technical_support.md`: return
within 30 days for a refund/replacement, or warranty replacement within
1 year for confirmed hardware defects.

## When to Escalate

Escalate per `escalation_policy.md` when:

- Wired speed tests confirm the issue is upstream of the router (ISP/modem
  side) but the customer disputes this and wants further NovaCart
  investigation.
- A router has already been factory reset and replaced once, and the same
  issue persists.
- The customer reports the router is physically hot, smoking, or making
  unusual noises — this should be escalated immediately as a potential
  safety issue, and the customer should be advised to unplug the device.

## Worked Examples

**Example 1 — Wired test isolates the fault.** A customer reports "the
Wi-Fi is unusable" with speeds far below what they pay their ISP for. A
wired speed test from a laptop connected directly to the router shows the
same low speed. Since the wired result matches the wireless result, the
router and Wi-Fi are ruled out, and the issue is upstream — most likely
the modem or the ISP connection itself — even though the customer's
initial instinct was to blame the router.

**Example 2 — Band confusion during setup.** A customer's phone keeps
connecting to their existing 5GHz network instead of the new router's
network during setup, causing the setup app to time out. Temporarily
disabling 5GHz on the phone, or moving closer to the new router so its
signal is stronger than the old network's, resolves the ambiguity and lets
setup complete.

**Example 3 — One mesh node dropping repeatedly.** A satellite node in a
detached garage keeps going offline while nodes inside the house stay
connected. Because it's likely out of reliable range from the nearest
online node, moving it to a location roughly halfway between the garage
and the house, or adding an additional node as a bridge, resolves the
issue — restarting the node alone had already been tried without lasting
success.

**Example 4 — Firmware update interrupted by a power outage.** A brief
power outage occurs while a router is mid-update. On power restoration,
the router shows a solid red light and does not come back online. Since
this matches the "interrupted firmware update" failure mode, a warranty
replacement is appropriate rather than repeated reset attempts, and this
should be logged clearly as update-related so it doesn't appear to be a
simple hardware defect unrelated to firmware.

## Frequently Misunderstood Points

- **A wired speed test is the single most useful diagnostic step** —
  it immediately separates "router/Wi-Fi problem" from "everything
  upstream of the router problem," and should usually be done before any
  other troubleshooting.
- **2.4GHz reaching farther is a trade-off, not a defect** — a device
  connecting to 2.4GHz instead of 5GHz at long range is normal behavior,
  not a sign something is broken.
- **Auto channel selection can still land on a congested channel** in
  dense buildings; toggling it forces a fresh scan but doesn't guarantee a
  perfect result every time.
- **A factory reset does not fix a genuine hardware fault** — if the same
  symptom returns immediately after a clean reset and fresh setup, further
  resetting is unlikely to help, and warranty replacement should be
  considered instead.
- **Mesh nodes need a path back to the main router**, not necessarily a
  direct line of sight to it — being near any other online node in the
  mesh is normally sufficient.

## Test Questions

1. My internet is completely down — what's the very first thing I should
   check before touching the router?
2. Why might switching to the 5GHz Wi-Fi band help with slow speeds at
   short range?
3. Is it safe to unplug my router in the middle of a firmware update?
4. One node in my mesh Wi-Fi system shows offline — what should I try
   before removing and re-adding it?
