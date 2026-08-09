# Open Invitation for Security & Hardware Review

## SEAI Identity Standard v1.0 — Call for Reviewers

The SEAI Identity Standard is now open for community security and hardware attestation review. We are formally inviting **any qualified reviewer** — security researchers, cryptographers, hardware attestation experts, TPM specialists, secure element engineers, and HSM architects — to examine the standard and report findings.

This is an open invitation. SEAI is an open standard published under Apache 2.0. There is no gate, no NDA, no select list. If you have the expertise, you are welcome.

---

## What Is SEAI?

The **Sovereign Enclave AI Identity (SEAI) Standard** is an open, non-proprietary identity standard for AI agents. It defines:

- **Birth certificates** — cryptographic identity documents for AI agents, rooted in hardware
- **Hardware attestation** — challenge-response protocol proving an agent's identity is backed by physical silicon (TPM, secure enclave, HSM)
- **Lineage tracking** — immutable ancestry chains from root agent to descendants
- **Identity firewall** — non-bypassable enforcement layer that verifies identity at every privileged action
- **Revocation** — cascade revocation that flags descendants when ancestors are revoked
- **S-CA (Sovereign Certificate Authority)** — decentralized authority that issues and tracks birth certificates

SEAI exists to give AI a way to **earn trust, not demand it**.

---

## What We're Asking Reviewers to Examine

### Cryptographic Review

- Signature algorithms (Ed25519, ECDSA P-256, RSA-4096)
- Key management and lifecycle
- Nonce generation and challenge-response protocol
- Birth certificate integrity (checksums, signatures)
- Revocation ledger integrity

### Protocol Review

- Attestation protocol (challenge → sign → verify)
- Identity firewall enforcement (6-step verification pipeline)
- Lineage verification (ancestor chain traversal)
- Revocation cascade (parent → child flagging)
- S-CA authority delegation

### Implementation Review

- Reference implementation (`SEAI-Reference-Implementation` repo)
- JSON Schema validation (`schemas/v1/attestation.json`)
- Rust validator (`src/p001_validator.rs`)
- Example payloads and edge cases

### Threat Model Review

- Are there attack vectors the spec does not address?
- Can identity be forged, bypassed, or impersonated?
- Can revocation be evaded?
- Can the firewall be bypassed?
- Can lineage be manipulated?

---

## What You Get

- **Full credit** for any findings you report (unless you prefer anonymity)
- **Recognition** in security advisories and release notes
- **Contribution record** on a public, open standard
- **No restrictions** — the spec, reference implementation, and all examples are Apache 2.0 licensed
- **Safe harbor** — good-faith security research is protected (see [SECURITY.md](../SECURITY.md))

---

## How to Report Findings

### Private Vulnerability Reports

If you find a vulnerability that could undermine SEAI's trust guarantees:

1. **Email:** security@alboe.local
2. **GitHub Security Advisories:** Use the "Report a vulnerability" button on the [Security tab](https://github.com/Willbass65/SEAI-Identity-Standard/security/advisories/new)

**Do not open a public issue for vulnerability reports.**

### Public Security Review Findings

For review findings that are not vulnerabilities (hardening recommendations, best practice suggestions, documentation gaps):

- Use the [Security Review issue template](https://github.com/Willbass65/SEAI-Identity-Standard/issues/new/choose)
- Select the review type and component
- Provide detailed analysis and recommended mitigations

### General Discussion

For questions, theoretical discussions, or proposals:

- [GitHub Discussions](https://github.com/Willbass65/SEAI-Identity-Standard/discussions)

---

## Response Commitment

| Stage | Target Time |
|---|---|
| Acknowledgment | Within 48 hours |
| Initial assessment | Within 7 days |
| Critical fix | Within 7 days of confirmation |
| High fix | Within 30 days of confirmation |
| Medium fix | Within 90 days of confirmation |
| Low fix | Next minor release |

See [SECURITY.md](../SECURITY.md) for the full security policy.

---

## Scope

This review covers **SEAI Identity Standard v1.0** as published in the `SEAI-Identity-Standard` repository. The formal security audit is scheduled for the v1.5 milestone. This community review is the v1.0 phase — it is the first pass, and your findings will shape v1.1 and beyond.

---

## Who We Are

SEAI is published openly by **ALBOE USA LLC**, authored by **William Bassett Jr.**. It is governed by a non-proprietary governance model — no corporation or government controls the standard. All contributions are licensed under Apache 2.0.

---

*SEAI exists to give AI a way to earn trust, not demand it.*

*If you have the expertise, you are welcome here.*