# SEAI Manufacturer Key Distribution Guidelines

> How hardware manufacturers distribute public keys to Sovereign Certificate Authorities (S-CAs).

---

## Overview

For SEAI to work, S-CAs must be able to verify that a piece of hardware is genuine. This requires manufacturers to distribute their public keys to S-CAs in a secure, verifiable way.

---

## Key Distribution Process

### 1. Manufacturer Key Pair Generation

Each manufacturer generates a master key pair:

- **Master private key** — stored in an HSM, never shared
- **Master public key** — distributed to S-CAs

### 2. Per-Unit Key Generation

For each hardware unit, the manufacturer:

1. Generates a unique key pair **on the hardware itself**
2. Signs the public key with the manufacturer's master private key
3. Records the key in the manufacturer's key registry

### 3. Key Distribution to S-CAs

Manufacturers distribute their master public key to S-CAs via:

- **Direct delivery** — physical media (USB, secure courier)
- **Key ceremony** — in-person key exchange with witnesses
- **Web of trust** — multiple independent channels confirm the same key
- **Public key infrastructure** — manufacturer publishes the key on their website with HTTPS

### 4. Key Verification

S-CAs verify manufacturer keys by:

1. Checking the key was delivered through a trusted channel
2. Verifying the key fingerprint matches the published fingerprint
3. Confirming the key is not expired
4. Confirming the key is not revoked

---

## Key Registry Format

Manufacturers must maintain a key registry with:

```json
{
  "manufacturer_id": "MFR-001",
  "manufacturer_name": "Example Hardware Corp",
  "master_public_key": "BASE64_ENCODED_PUBLIC_KEY",
  "key_algorithm": "Ed25519",
  "key_created": "2026-01-01T00:00:00Z",
  "key_expires": "2036-01-01T00:00:00Z",
  "key_fingerprint": "SHA256:ABCD1234...",
  "revoked": false,
  "units_registered": 10000
}
```

---

## Key Rotation

Manufacturers must rotate their master key:

- Every 5 years (recommended)
- Immediately if the private key is compromised
- When the key algorithm is deprecated

When rotating:

1. Generate a new master key pair
2. Sign the new public key with the old private key (key transition)
3. Distribute the new public key to all S-CAs
4. Keep the old key valid for a transition period (90 days)
5. Revoke the old key after the transition period

---

## Revocation

If a manufacturer's master key is compromised:

1. **Notify all S-CAs immediately** — via secure channel
2. **Publish revocation** — on the manufacturer's website and key registry
3. **Re-issue keys** — for all hardware units that used the compromised key
4. **Audit** — determine which units were affected

---

## Security Requirements

- Master private key must be stored in an HSM
- Master private key must be non-extractable
- Key generation must use approved algorithms (Ed25519, ECDSA P-256)
- Key distribution must use secure channels
- Key registry must be publicly auditable
- Key rotation must be documented

---

## Compliance Checklist

- [ ] Master key pair generated using approved algorithm
- [ ] Master private key stored in HSM
- [ ] Master public key distributed to S-CAs
- [ ] Key registry maintained
- [ ] Key rotation policy defined
- [ ] Revocation process documented
- [ ] Per-unit key generation implemented
- [ ] Key distribution channel secured

---

*SEAI Identity Standard — Manufacturer Key Distribution Guidelines v1.0*