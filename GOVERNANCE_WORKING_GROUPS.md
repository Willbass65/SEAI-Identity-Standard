# SEAI Working Group Charter

**Document ID:** `GOVERNANCE_WORKING_GROUPS.md`
**Status:** Draft / Under Review
**Author:** William Earl Bassett Jr., SEAI Maintainers
**Created:** 2026-08-09
**Related:** `GOVERNANCE.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `CONFLICTS.md`, `SECURITY.md`

---

## 1. Mission and Purpose

The Sovereign AI Identity (SEAI) Working Group framework defines how domain experts, researchers, hardware vendors, and AI safety engineers collaborate to evolve the SEAI Identity Standard.

Working Groups (WGs) exist to:

- Research domain-specific challenges in AI identity, trust, attestation, and behavioral integrity.
- Draft, refine, and maintain formal SEAI-P proposals.
- Deliver schemas, reference implementations, and verification suites.
- Ensure all contributions align with SEAI's governance, security, and vendor-neutrality principles.

WGs do **not** replace the SEAI-P proposal process — they support it by providing structured review, expert input, and milestone guidance.

---

## 2. Working Group Lifecycle

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ 1. Formation │ ──> │ 2. RFC Phase │ ──> │ 3. Delivery  │ ──> │ 4. Dissolution│
│  Chartering  │     │ 14/30-Day    │     │ Schema + Ref │     │  Archived/WG │
│              │     │  Windows     │     │              │     │  Maintenance │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

### 2.1 Formation Phase

A Working Group may be proposed by any contributor via a **Working Group Charter Issue**.

Formation requires:

- **Scope Definition** — a clear problem statement and technical boundaries
- **Lead Sponsor** — at least one WG Lead (assigned during formation)
- **Target Deliverables** — schemas, reference code, or specification updates
- **Maintainer Approval** — lazy consensus over a 72-hour window

### 2.2 Active / RFC Execution Phase

During the active phase, WGs:

- Host asynchronous discussions under the Working Groups category
- Draft formal proposals (SEAI-P-series)
- Open 14-day (minor) or 30-day (major) RFC windows per `GOVERNANCE.md`
- Conduct prototype testing in the SEAI Reference Implementation
- Maintain alignment with SEAI governance and security policies

### 2.3 Delivery & Integration

After the RFC window closes and consensus is reached:

- Deliverables are merged into `SEAI-Identity-Standard`
- Proposal status changes from Under Review → Accepted
- **Milestone assignment is determined by community review per the SEAI-P process** (no version is pre-assigned)
- Editors integrate changes into the specification

### 2.4 Sunset / Dissolution

Once deliverables are fully integrated:

- The WG transitions to **Archived / Maintenance Mode**
- Ongoing fixes return to SEAI Core Maintainers

---

## 3. Roles & Responsibilities

| Role | Responsibilities | Appointment |
| --- | --- | --- |
| **WG Lead** | Chairs discussions, enforces Code of Conduct, drives timelines, synthesizes RFC feedback | Assigned during formation; subject to term limits (§7.1) |
| **Domain Editor** | Authors schemas, reference code, documentation | Nominated by WG Lead or members |
| **Reviewer / Contributor** | Participates in RFCs, audits code, submits PRs | Open to all community members (contribution-based) |
| **Core Maintainer Liaison** | Ensures WG output aligns with SEAI architecture/security | Assigned by SEAI Core; staggered terms (§7.1) |

All roles operate under the Contributor Covenant v2.1 (`CODE_OF_CONDUCT.md`).

---

## 4. Decision-Making & Consensus Model

Working Groups follow SEAI's **Lazy Consensus** model:

- **Silence = Consent** — if no blocking objections are raised within 72 hours (or 14/30 days for SEAI-P proposals), the decision passes.
- **Blocking Objections** — must include a technical rationale and an alternative proposal.
- **Escalation** — persistent deadlocks escalate per the Deadlock Resolution process (§7.3).

---

## 5. Deliverables

Working Groups produce:

- SEAI-P proposal drafts and revisions
- Specification updates
- JSON schemas and examples
- Reference implementation modules
- Security considerations
- Roadmap milestone recommendations
- Meeting summaries and decision logs

---

## 6. Meeting Cadence

- Monthly WG meeting (public notes)
- Ad-hoc review sessions during active RFC windows
- Quarterly roadmap review

---

## 7. Governance Rotation & Anti-Domination Guardrails

To ensure SEAI remains a vendor-neutral, non-stagnant open standard capable of enduring for decades, all Working Groups and Maintainer seats strictly observe the following structural bounds.

### 7.1 Mandatory Term Limits & Rotation

- **WG Lead Term Limits:** Working Group Leads serve a fixed term of **twelve (12) months**, renewable once (maximum 2 consecutive years). Upon term expiration, leadership MUST rotate to a new community contributor.
- **Maintainer Staggered Terms:** Core Maintainer positions operate on **two (2) year staggered terms**, where 50% of maintainer seats transition annually to ensure continuous renewal without losing institutional memory.
- **Founder Succession Plan:** Executive leadership and emergency override keys are bound to a documented, multi-signature emergency succession protocol in the event of founder unavailability, acquisition, or retirement.

### 7.2 Diversity & Anti-Capture Numeric Caps

- **Sector Cap:** No single industry sector (e.g., Cloud Providers, Hardware Vendors, AI Model Labs, Academic Institutions) may hold more than **33% (max 3)** of voting or leadership seats within any individual Working Group.
- **Organizational Cap:** No single corporate entity or affiliated parent group may occupy more than **one (1) leadership seat** across all active Working Groups simultaneously.
- **Geographic Balance:** Working Group leadership teams SHOULD maintain geographic diversity spanning at least two distinct global regions.

### 7.3 Deadlock Resolution & Escape Valve

If a Working Group enters a persistent technical deadlock where lazy consensus fails and consensus cannot be reached after **14 calendar days**:

1. The issue is automatically escalated to a joint session with the Core Maintainer Liaison and active WG Leads.
2. If consensus remains unachievable, an open **10-day public vote** across all verified repository contributors resolves the decision by a simple majority (>50%).

---

## 8. Vendor Neutrality & Anti-Capture Guarantees

To protect SEAI's independence:

- No proposal may lock SEAI into a single hardware vendor, cloud provider, or proprietary ecosystem.
- All WG artifacts must be released under SEAI's open licenses (Apache 2.0 / CC0).
- Conflicts of interest must be disclosed per `CONFLICTS.md`.
- Deliverables that violate vendor neutrality are rejected as a non-negotiable acceptance criterion.

---

## 9. Active Working Groups

### WG-01: Hardware Attestation Working Group

- **Scope:** TPM, Secure Enclave, Nitro, HSM attestation flows
- **Primary Proposal:** SEAI-P-001
- **Status:** Active
- **Deliverables:** `schemas/v1/attestation.json`, `src/p001_validator.rs`

### WG-02: Behavioral Integrity Working Group

- **Scope:** Continuous identity verification, drift detection, event logging
- **Primary Proposal:** SEAI-P-002
- **Status:** Active (RFC review window open)
- **Deliverables:** `examples/p002_behavioral_integrity/`

---

*SEAI Working Group Charter — Draft v0.1*
*Published by ALBOE USA LLC — authored by William Earl Bassett Jr.*
*The founder provides the container. The community fills it with content.*
Meetings may be synchronous or asynchronous.