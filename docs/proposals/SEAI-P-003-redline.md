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
