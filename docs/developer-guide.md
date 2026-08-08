# SEAI Developer Integration Guide

> How to integrate SEAI identity into your AI application or platform.

---

## Quick Start

### 1. Understand the Birth Certificate

Every AI agent in SEAI has a **birth certificate** — a JSON document that proves the agent's identity. It contains:

- `agent_id` — unique identifier
- `hardware_id` — the hardware root of trust
- `manufacturer_id` — who built the hardware
- `birth_date` — when the agent was created
- `public_key` — the agent's public signing key
- `authority_scope` — what the agent is allowed to do (Level 0–3)
- `lineage` — ancestry chain
- `signature` — cryptographic signature from the S-CA

See `examples/birth_certificate.json` for a complete example.

### 2. Verify a Birth Certificate

To verify an agent's identity:

1. Check that the birth certificate is signed by a trusted S-CA
2. Verify the signature using the S-CA's public key
3. Check that the agent is not revoked (query the revocation list)
4. Verify the lineage chain (each ancestor must be valid and not revoked)

### 3. Implement Hardware Attestation

Before trusting an agent, verify it's running on the hardware it claims:

1. Send a random challenge (nonce) to the agent
2. The agent signs the nonce using its hardware-bound private key
3. Verify the signature using the agent's public key
4. The signature proves the agent has access to the hardware

See `examples/hardware_attestation_flow.md` for the full protocol.

### 4. Implement the Identity Firewall

The identity firewall runs **before every action** an agent takes:

1. **Extract** — get the agent's birth certificate
2. **Verify** — check signature, attestation, and revocation status
3. **Check Authority** — verify the agent's authority scope allows the action
4. **Check Lineage** — verify no ancestor is revoked
5. **Enforce** — allow or deny the action
6. **Log** — record the decision

If any step fails, the action is **denied**. There is no override.

See `examples/identity_firewall_flow.md` for the full flow.

### 5. Handle Revocation

If an agent is compromised:

1. The S-CA issues a revocation order
2. The agent is added to the revocation list
3. All identity firewall checks for that agent immediately fail
4. If `cascade: true`, all descendants are also flagged

See `examples/revocation_example.json` for the revocation format.

---

## Integration Checklist

- [ ] Read SPEC.md fully
- [ ] Understand birth certificate format
- [ ] Implement birth certificate verification
- [ ] Implement hardware attestation challenge-response
- [ ] Implement identity firewall (6-step verification)
- [ ] Implement revocation checking
- [ ] Test with examples in `examples/`
- [ ] Review FAQ.md for common questions

---

## Language Bindings (Future)

SEAI reference implementations are planned for:

- Python (reference implementation — see ROADMAP.md)
- Rust
- Go
- TypeScript/Node.js

Until the reference implementation is available, use the examples and SPEC.md as your guide.

---

## Getting Help

- **Questions:** Open a GitHub Discussion in the "Q&A" category
- **Bugs:** Open an issue using the Bug Report template
- **Proposals:** Open an issue using the Feature Proposal template
- **Security:** Email security@alboe.local (do NOT open a public issue)

---

*SEAI Identity Standard — Developer Integration Guide v1.0*