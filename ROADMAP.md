# SEAI Identity Standard — Roadmap

> This roadmap defines the planned evolution of the SEAI Identity Standard.
> It is intentionally minimal — providing direction without dictating details.
> The community fills in the implementation.

---

## Current Status

| Version | Status | Description |
|---|---|---|
| v1.0 | ✅ Published | Core identity primitives, birth certificates, attestation, firewall, revocation |

---

## Proposals in Flight

Active SEAI-P proposals are reviewed independently of the version timeline. Per SEAI GOVERNANCE §3, proposals enter the pipeline as Discussions and are assigned to a version milestone only after community review.

| Proposal | Title | Status | Target Milestone |
|---|---|---|---|
| SEAI-P-002 | Behavioral Integrity & Continuous Identity Verification | 🔵 RFC open (14-day window) | Community-decided (none assigned) |

---

## Version Timeline

### v1.0 — Core Identity Primitives ✅

**Status:** Published (Aug 7, 2026)

- Birth certificate format with required and optional fields
- Hardware attestation via TPM/SE/HSM challenge-response
- Lineage tracking with ancestor chain verification
- Authority scopes (Level 0–3) with fail-closed enforcement
- Revocation system with immediate kill and cascade flagging
- Identity firewall — non-bypassable verification before every action

---

### v1.1 — Signature Standardization

**Focus:** Standardize cryptographic signing algorithms and verification rules

- [ ] Define required signature algorithms (Ed25519, ECDSA P-256)
- [ ] Define optional signature algorithms (RSA-PSS, Dilithium for post-quantum)
- [ ] Standardize key rotation guidance and timelines
- [ ] Define signature verification rules for all consumers
- [ ] Multi-vendor signature compatibility requirements
- [ ] Post-quantum signature readiness assessment

---

### v1.2 — Deployment Context Binding

**Focus:** Bind AI identity to physical deployment context

- [ ] Deployment context binding format (data center, edge, facility, mobile)
- [ ] Hardware identity anchoring protocol
- [ ] Transfer and re-anchoring protocol (when hardware changes)
- [ ] Local-only trust boundary definitions
- [ ] Geofencing and jurisdictional scope fields

---

### v1.3 — Transparency Extensions

**Focus:** Operational transparency and disclosure categories

- [ ] Operational transparency fields (uptime, capability changes, model updates)
- [ ] Disclosure categories (what the AI must reveal about itself)
- [ ] Optional metadata extensions
- [ ] Community-driven extension registry
- [ ] Audit trail format for compliance

---

### v1.5 — Formal Security Review 🔒

**Focus:** Independent cryptographic and security review of all v1.x primitives

- [ ] Engage independent cryptographic reviewers
- [ ] Formal analysis of birth certificate format
- [ ] Formal analysis of attestation protocol
- [ ] Formal analysis of revocation cascade logic
- [ ] Formal analysis of identity firewall enforcement
- [ ] Publish security review report
- [ ] Address findings before v2.0

> **This milestone is mandatory before v2.0.** Multi-agent identity cannot be built on unreviewed primitives.

---

### v2.0 — Cross-Vendor Interoperability

**Focus:** Vendor-neutral identity format and standardized verification

- [ ] Vendor-neutral birth certificate format (no vendor-specific fields in core)
- [ ] Standardized verification API specification
- [ ] Compatibility guidelines for hardware vendors (TPM, SE, HSM)
- [ ] Interoperability test suite
- [ ] Reference implementation (separate repository)
- [ ] Community interoperability testing program

> **Note:** Cross-vendor interoperability is placed before multi-agent identity because multi-agent systems require a vendor-neutral foundation. Building multi-agent identity on vendor-specific formats would require costly retrofitting.

---

### v3.0 — Multi-Agent Identity

**Focus:** Identity for agent clusters, delegation, and inter-agent trust

- [ ] Identity for agent clusters (group identity vs individual identity)
- [ ] Parent/child identity relationships and delegation rules
- [ ] Inter-agent trust propagation
- [ ] Cluster-level authority scopes
- [ ] Cluster revocation and cascade rules
- [ ] Multi-agent firewall enforcement

---

### v4.0+ — Long-Term Evolution

**Focus:** Community-driven evolution

- [ ] Community proposals (via SEAI-P governance process)
- [ ] Emerging identity needs (new hardware types, new deployment models)
- [ ] Safety-driven expansions (new threat models, new attack vectors)
- [ ] Governance-approved revisions
- [ ] Cross-standard interoperability (OAuth, W3C DID, OpenID)

---

## Parallel Tracks

These tracks run alongside the version timeline and are not tied to specific versions:

### Reference Implementation Track

- [ ] Reference implementation repository created
- [ ] Python reference library (birth certificate generation, verification)
- [ ] Hardware attestation reference code (TPM, SE)
- [ ] Identity firewall reference implementation
- [ ] CLI tool for birth certificate management

### Community Track

- [ ] Issue templates (bug report, feature proposal, security review)
- [ ] Pull request template
- [ ] Branch protection rules for `main`
- [ ] Contributor License Agreement (CLA)
- [ ] Good first issue labels for new contributors

### Documentation Track

- [ ] Developer integration guide
- [ ] Hardware vendor integration guide
- [ ] S-CA (Sovereign Certificate Authority) operator guide
- [ ] PNG diagrams (replacing ASCII for accessibility)
- [ ] Interactive documentation site

---

## Versioning Policy

SEAI follows semantic versioning:

| Change Type | Version Impact | Example |
|---|---|---|
| New required field in birth certificate | Major (v2.0, v3.0) | Adding `cluster_id` field |
| New optional field or extension | Minor (v1.1, v1.2) | Adding `transparency_log` field |
| Clarification, typo fix, example update | Patch (v1.0.1) | Fixing a typo in SPEC.md |
| Security-critical change | Immediate patch + advisory | Fixing a revocation bypass |

---

*SEAI Identity Standard — Roadmap v0.1*
*Published by ALBOE USA LLC — authored by William Bassett Jr.*
*The community fills in the details. The founder provides the direction.*