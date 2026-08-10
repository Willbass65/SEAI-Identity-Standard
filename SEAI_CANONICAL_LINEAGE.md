# SEAI Canonical Lineage

> **This file is the declarative origin marker for the SEAI Identity Standard.**
> It exists to disambiguate the official SEAI project from any forks, clones, or
> impostor repositories. This is a **human-readable declaration of provenance** —
> it names the canonical repository, steward, governance, and proposal pipeline.
> Cryptographic verification of releases is provided separately by signed Git tags.

---

## 1. Canonical Repository

The single official home of the SEAI Identity Standard is:

| Field | Value |
|---|---|
| **Repository** | [`Willbass65/SEAI-Identity-Standard`](https://github.com/Willbass65/SEAI-Identity-Standard) |
| **Canonical URL** | `https://github.com/Willbass65/SEAI-Identity-Standard` |
| **Default branch** | `main` |
| **License** | Apache 2.0 |
| **Visibility** | Public |

> Any copy of SEAI hosted at a different URL is **not canonical**. Always verify
> against this repository before treating code, schemas, or proposals as official.

---

## 2. Canonical Steward

| Field | Value |
|---|---|
| **Steward** | ALBOE USA LLC |
| **Author** | William Earl Bassett Jr. |
| **Role** | Founder / Initial Maintainer |
| **Contact** | `security@alboe.local` (security only) |

The steward is the identity anchor for SEAI governance and release signing.

---

## 3. Canonical Governance

The official governance of SEAI is defined by these documents (all in this repository):

| Document | Purpose |
|---|---|
| `GOVERNANCE.md` | Core governance model, roles, and SEAI-P proposal process |
| `GOVERNANCE_WORKING_GROUPS.md` | Working Group framework and anti-domination guardrails |
| `CODE_OF_CONDUCT.md` | Community conduct (Contributor Covenant v2.1) |
| `SECURITY.md` | Vulnerability reporting and security policy |
| `CONFLICTS.md` | Conflict-of-interest disclosures |
| `CONTRIBUTING.md` | Contribution guidelines |
| `CLA.md` | Contributor License Agreement |

---

## 4. Canonical Proposal Pipeline

Official SEAI proposals are known as **SEAI-P** proposals and follow the process
defined in `GOVERNANCE.md` §3:

1. Proposal posted in the **Ideas** discussion category
2. RFC review window opens (14 days minor / 30 days major)
3. Community review and working-group evaluation
4. Lazy consensus / milestone assignment (per the SEAI-P process)
5. Steward verification
6. Integration + scorecard update

A clone cannot make a proposal SEAI-official — only the canonical pipeline can.

Current proposals:
- **SEAI-P-001** — Hardware-Rooted Attestation Layers
- **SEAI-P-002** — Behavioral Integrity & Continuous Identity Verification *(RFC open)*

---

## 5. Canonical Versioning

SEAI follows **semantic versioning** (see `ROADMAP.md`).

Official releases are marked with **signed Git tags** in the pattern:

```
seai-v<major>.<minor>.<patch>
```

Example: `seai-v1.0.0`

Official release tags are:
- **signed** (GPG/SSH signature of the steward identity)
- **immutable** (altering the underlying commit breaks the signature)
- **tied to this canonical repository**

A clone cannot produce canonical tags, because canonical tags require the
canonical repo, canonical governance, and the steward's signature.

---

## 6. Canonical Working Groups

Active working groups (see `GOVERNANCE_WORKING_GROUPS.md` §9):

| WG | Scope | Primary Proposal |
|---|---|---|
| **WG-01** | Hardware Attestation | SEAI-P-001 |
| **WG-02** | Behavioral Integrity | SEAI-P-002 |

---

## 7. Canonical Scorecard

The public adoption and governance ledger is maintained at:

- **`SCORECARD.md`** — traffic, adoption, and governance metrics
- Updated daily by the SEAI Steward automation

---

## 8. Authenticity Statement

SEAI is deliberately **open** and **forkable** under Apache 2.0. Anyone may copy,
modify, and build upon the code. Legitimate forks are encouraged.

However, **authority and lineage are not forkable.** The following are canonical
to this repository only and cannot be claimed by a clone:

- The canonical repository URL
- SEAI governance and the SEAI-P proposal pipeline
- Official signed release tags
- The public scorecard and steward automation
- Stewardship by ALBOE USA LLC

> **To verify you are working with the official SEAI:** check that the repository
> URL is `Willbass65/SEAI-Identity-Standard`, that this lineage file is present,
> and (for releases) that the Git tag carries a valid signature from the steward.

---

*SEAI Canonical Lineage — v1.0*
*Published by ALBOE USA LLC — authored by William Earl Bassett Jr.*
*Clones can copy code. They cannot copy lineage.*
