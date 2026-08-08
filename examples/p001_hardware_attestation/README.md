# SEAI-P-001: Hardware-Rooted Attestation Layers

> First formal proposal for the SEAI Identity Standard.

## Proposal Summary

SEAI-P-001 defines the schema and validation logic for hardware-rooted attestation payloads. It specifies how AI agents prove they are running on the hardware they claim.

## Files

| File | Description |
|---|---|
| `attestation_example.json` | Valid attestation payload example (TPM 2.0) |
| `../../schemas/v1/attestation.json` | JSON Schema for validation |
| `../../src/p001_validator.rs` | Rust reference validator |

## Schema

The attestation payload contains:

- `seai_version` — SEAI standard version (currently "1.0")
- `proposal_ref` — Always "SEAI-P-001" for this proposal
- `agent_id` — Agent identifier (must match birth certificate)
- `timestamp_utc` — ISO 8601 timestamp (max 300s drift allowed)
- `hardware_provider` — Hardware type (TPM2.0, AWS_Nitro, Apple_Secure_Enclave, HSM_Generic)
- `attestation_quote` — Quote data, signature, and optional PCR values
- `public_key` — JWK-format public key (Ed25519, P-256, or secp256k1)

## Refinements from Original Draft

This proposal was refined from an initial draft by Lumos Pro. Key changes:

1. **`agent_id` format** — Aligned with SPEC.md (simple string, not DID format)
2. **`$id` URL** — Uses GitHub URL, not unregistered domain
3. **`software_fallback` removed** — Hardware-rooted identity requires hardware
4. **PCR fields made optional** — TPM-specific, not all providers use PCR
5. **Signature verification added** — Rust validator now verifies cryptographic signatures
6. **Configurable clock drift** — No longer hardcoded to 300s

## Original Author

Initial draft by Lumos Pro (GitHub Copilot). Refined by Cline for the SEAI Identity Standard.

---

*SEAI-P-001 — Hardware-Rooted Attestation Layers*
*Part of the SEAI Identity Standard v1.0*