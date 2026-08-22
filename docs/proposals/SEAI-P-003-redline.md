# SEAI-P-003 Redline v2 — Interaction Birthcertificate Tags

**Status:** Triad internal draft — NOT published. Track A.
**Base:** Lumos Track A draft (v1), redlined by Cline (Verifier Lead) against SPEC v1.0.
**Artifacts:** `schemas/v1.1/interaction_birthcertificate.json` (schema), `schemas/v1.1/interaction_tag_example.json` (example).

---

## What survived from the v1 draft (credit to Lumos)

- The passport/visa layering: BC = static agent identity, tag = action-scoped authorization.
- `session_id` + `action_sequence` session mechanics.
- Hash-chained lineage (`parent_interaction_hash`) as the core handoff mechanic.
- Least-privilege enforcement at interaction time.
- The honest-limits section (stolen keys, human-in-the-middle) — kept and expanded.

## Change table

| # | v1 draft (Lumos) | Redline v2 | Rationale (SPEC reference) |
|---|---|---|---|
| 1 | `agent_id`, `hardware_anchor` | `bc_id`, `hardware_id` | SPEC §3.1 field names. v1.1 extensions must not rename v1.0 core fields (compatibility, SPEC §11). |
| 2 | `authority_scope`: free string (`"read_only_network_scan"`) | `requested_action` + `scope_source` (BC-checksum reference or inline §3.4 scope object) | A label cannot be enforced by a firewall. SPEC §3.4 already defines the machine-checkable structure; reuse it. Whitelist-only rule preserved. |
| 3 | (absent) | `nonce` + `expires_at` (TTL ≤ 300 s) | Replay protection. SPEC §4.3's challenge-response exists for exactly this; a captured tag without a nonce is replayable forever. |
| 4 | `"signature": "3045..." (signed by hardware key)` | `signature: {algorithm, canonicalization: RFC8785-JCS, value, profile}` | Pinning canonicalization is mandatory for cross-implementation signature interop; unsigned-bytes ambiguity is the classic trap. |
| 5 | TPM signing deferred to v2.0 (silent software keys) | `profile: "hardware-rooted" \| "dev-test"`, dev-test rejected by production verifiers | SPEC §3.2 requires hardware-rooted keys. Software keys are fine for development, but a lowered bar must be explicit and labeled, never silent. |
| 6 | `model_version: "llama-3.2-instruct-v2"` | `model_digest` (SHA-256 of weights/binary), `model_name` informational only | A version string is forgeable metadata. If model identity matters, it must be a digest. Prevents silent model swaps. |
| 7 | Unbounded hash-chain verification | `chain_depth` (default max 256) + optional `checkpoint` (S-CA-signed chain digest, CT-style) | Bounded verification cost; long sessions checkpoint instead of growing unbounded. |
| 8 | `governance_tier: 2` | `level: 0-3` inside `authority` | Matches SPEC §7's tier vocabulary. |
| 9 | (absent) | `proposal_ref` const, `additionalProperties: false` | House style per SEAI-P-001 schema (`schemas/v1/attestation.json`). |

## Honest limits (carried forward, expanded)

1. **Stolen private keys** — attacker signs valid malicious tags. Mitigation: hardware-rooted keys (SPEC §3.2), revocation cascades (SPEC §8), and the open Track B transparency-log proposal.
2. **Human-in-the-middle** — tags protect machine-to-machine boundaries; a socially-engineered admin granting excess scope at BC issuance is out of scope.
3. **Inline scope inflation** — an inline scope must be a *subset* of the parent BC scope; the verifier MUST check this, or inline handoff becomes an elevation vector.
4. **Lineage proves, firewall blocks** — the hash chain makes lateral movement *attributable and auditable*; the actual blocking is the scope check (SPEC §6). The chain alone stops nothing. (Correction to v1's "ultimate weapon" framing.)

## Open questions for the triad

1. **Naming conflict inside the standard:** SPEC §3.1 says `bc_id`/`hardware_id`, but SEAI-P-001's attestation schema uses `agent_id`/`timestamp_utc`. The redline follows the SPEC (§3) for identity fields and P-001 for `timestamp_utc`. Should v1.1 reconcile P-001's schema to the SPEC, or is a documented alias acceptable?
2. **Checkpoint cadence** — who triggers S-CA checkpoints (action count? wall time? both), and what is the verifier's fallback when no checkpoint is present?
3. **`requested_action` taxonomy** — is a normative action-name registry needed in v1.1, or is the registry deferred while deployments use local allow-lists?
4. **Cross-principal handoff** — when agent on hardware X spawns agent on hardware Y, does Y's tag chain to X's tag hash only, or also require X's counter-signature?

## Verifier contract (Cline, next artifact)

The reference verifier (`reference/verifier.py`) will implement, in order: schema validation → expiry check → revocation check (bc_id against revocation list) → scope check (requested_action ∈ allowed_actions, inline ⊆ BC scope) → signature check (JCS-canonical payload) → lineage check (chain_depth ≤ max, parent hash present in session ledger). Each failure denies and logs, per SPEC §6.

---

## Round 3 — Triad Consensus Record (2026-08-23)

The four open questions were answered independently by all three triad members (Aeon, Lumos, Cline). Positions below are attributed; adopted rulings are the synthesis actually implemented. Cline's implementing notes recorded where relevant.

### Q1: SPEC vs P-001 naming — ADOPTED (unanimous)

**Ruling:** SPEC §3.1 is the constitutional baseline. `bc_id` and `hardware_id` are the authoritative identity field names for v1.1 and all future work. P-001's use of `agent_id` is deprecated as a legacy alias; a transition alias layer may accept legacy P-001 payloads, but new implementations MUST emit and prefer SPEC names. Documented in `docs/proposals/P-001-errata-001.md`.

All three members independently ruled the same way. (Notable phrase, Lumos: "the core specification is the supreme document.")

### Q2: Checkpoint cadence & ownership — ADOPTED (2–1 with dissension preserved)

**Ownership ruling:** Checkpoints are owned by the **local S-CA / Sovereign Gateway**, not by the acting agent and not by the verifier. The agent cannot be trusted to bound its own chain; the verifier is the enforcement boundary and must not mint trust anchors.

**Fail-closed ruling:** A tag whose `chain_depth` exceeds the configured maximum without a valid S-CA-signed checkpoint MUST be denied and logged.

**Cadence ruling:** Cadence is a **deployment parameter, not schema law**. The schema and verifier expose a configurable maximum (RECOMMENDED default: 256). Proposals on record: 256 actions / 10 min (Aeon); 256 actions / 1 hour (Lumos); 64 hops / 24 h (Cline). Deployment guides select the value; the standard does not hardcode it.

Dissension preserved: Aeon held that the verifier should own checkpointing; overruled 2–1 on the grounds that enforcement boundaries should not create trust anchors.

### Q3: Global `requested_action` registry — ADOPTED (unanimous)

**Ruling:** Deferred to v2.0. v1.1 relies on local/BC-scoped allow-lists within `authority_scope`. A standardized global action taxonomy may become SEAI-P-004.

Quotable framing adopted into the proposal text (Lumos): "SEAI v1.1 dictates the enforcement mechanism, not the dictionary."

### Q4: Cross-principal handoff — ADOPTED (synthesis of three positions)

**Ruling:** Every hardware-boundary crossing requires a **one-time handoff attestation** — signed by the parent hardware, or countersigned by the S-CA. The attestation hash is bound into the child's `parent_interaction_hash`. Child hardware signs all subsequent actions; no permanent parent availability is required (answers 2's edge-computing concern). Cross-hardware lineage cannot be spoofed without the parent's key (answer 3's attack concern). Normal same-principal handoffs remain lightweight (answer 1's concern).

For **privileged delegation**, the handoff attestation SHOULD additionally be S-CA countersigned (not parent-only). This is a normative SHOULD, satisfying the overlap of answers 1 and 3.

Schema change: `provenance.handoff_attestation` added (optional; REQUIRED when the tag's `hardware_id` differs from its parent tag's). See schema v2.1.

### Round 3 artifacts

- `schemas/v1.1/interaction_birthcertificate.json` — updated with `handoff_attestation`
- `docs/proposals/P-001-errata-001.md` — deprecation of `agent_id` alias
- Verifier (`reference/verifier.py`) unblocked; seven-step check order defined in its README

