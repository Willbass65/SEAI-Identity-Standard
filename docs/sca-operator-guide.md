# SEAI S-CA Operator Guide

> How to operate a Sovereign Certificate Authority (S-CA) for the SEAI Identity Standard.

---

## What is an S-CA?

A **Sovereign Certificate Authority (S-CA)** is the entity that issues birth certificates for AI agents. The S-CA:

- Verifies hardware identity before issuing a birth certificate
- Signs birth certificates with its private key
- Maintains the revocation list
- Issues revocation orders when agents are compromised

---

## S-CA Responsibilities

### 1. Birth Certificate Issuance

When a new AI agent is created:

1. **Verify hardware** — confirm the agent is running on the hardware it claims
2. **Verify manufacturer** — confirm the hardware was manufactured by a trusted vendor
3. **Generate birth certificate** — create the JSON document with all required fields
4. **Sign the birth certificate** — sign with the S-CA's private key
5. **Publish** — make the birth certificate available to verifiers

### 2. Revocation Management

When an agent is compromised:

1. **Receive revocation request** — from the agent's operator, a security team, or automated detection
2. **Verify the request** — confirm the request is legitimate
3. **Issue revocation order** — add the agent to the revocation list
4. **Set cascade flag** — if `cascade: true`, flag all descendants
5. **Publish** — make the revocation list available to all verifiers

### 3. Key Management

The S-CA must:

- Generate a strong key pair (Ed25519 or ECDSA P-256 recommended)
- Store the private key in an HSM or secure element
- Rotate keys according to the key rotation policy
- Publish the public key so verifiers can verify birth certificate signatures

### 4. Audit Logging

The S-CA must log:

- Every birth certificate issued
- Every revocation order issued
- Every key rotation
- Every access to the S-CA private key

---

## S-CA Trust Model

The S-CA is the **root of trust** for the agents it certifies. Verifiers trust the S-CA's signature, not the agent's self-asserted identity.

### Trust Hierarchy

```
S-CA (root of trust)
  └── Birth Certificate (signed by S-CA)
       └── Agent (verified by birth certificate)
            └── Actions (verified by identity firewall)
```

### Multiple S-CAs

SEAI supports multiple S-CAs. Verifiers can trust one or more S-CAs. This enables:

- Vendor-specific S-CAs (e.g., a hardware vendor runs its own S-CA)
- Organization-specific S-CAs (e.g., a company runs its own S-CA)
- Public S-CAs (e.g., a standards body runs a public S-CA)

---

## S-CA Security Requirements

- Private key must be stored in an HSM or secure element
- Private key must be non-extractable
- All S-CA operations must be logged
- S-CA must be auditable
- S-CA must support key rotation
- S-CA must have a disaster recovery plan

---

## S-CA Compliance Checklist

- [ ] Private key stored in HSM/SE
- [ ] Private key is non-extractable
- [ ] Birth certificate issuance process is documented
- [ ] Revocation process is documented
- [ ] Key rotation policy is defined
- [ ] Audit logging is implemented
- [ ] Public key is published
- [ ] Disaster recovery plan exists

---

*SEAI Identity Standard — S-CA Operator Guide v1.0*