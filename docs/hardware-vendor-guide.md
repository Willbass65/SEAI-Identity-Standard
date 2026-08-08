# SEAI Hardware Vendor Integration Guide

> How to implement SEAI hardware attestation for TPM, Secure Element, and HSM vendors.

---

## Overview

SEAI requires hardware attestation to prove that an AI agent is running on the hardware it claims. This guide explains how hardware vendors can implement the attestation protocol.

---

## Supported Hardware Types

| Hardware | Description | Use Case |
|---|---|---|
| **TPM 2.0** | Trusted Platform Module | Server, desktop, embedded |
| **Secure Element** | Dedicated security chip | Mobile, IoT, edge devices |
| **HSM** | Hardware Security Module | Enterprise, cloud, data center |

---

## Attestation Protocol

### 1. Key Generation

Each hardware unit must generate a key pair:

- **Private key** — stored in the hardware, never extractable
- **Public key** — exported and included in the birth certificate

### 2. Challenge-Response

The attestation protocol is a challenge-response:

1. **Verifier** sends a random nonce to the agent
2. **Agent** signs the nonce using its hardware-bound private key
3. **Verifier** checks the signature using the agent's public key

### 3. Implementation Requirements

- The private key must be **non-extractable** from the hardware
- The signing operation must be **hardware-bound** (cannot be performed in software)
- The hardware must support **key rotation** (see ROADMAP.md v1.1)
- The hardware must support **secure boot** to ensure the attestation is performed on trusted firmware

---

## TPM 2.0 Implementation

### Key Creation

```bash
# Create an attestation key in the TPM
tpm2_createprimary -C o -c primary.ctx
tpm2_create -C primary.ctx -G rsa -u attestation.pub -r attestation.priv
```

### Signing

```bash
# Sign a nonce using the TPM
tpm2_sign -C attestation.priv -g sha256 -m nonce.txt -s signature.bin
```

### Verification

```bash
# Verify the signature
tpm2_verifysignature -c attestation.pub -g sha256 -m nonce.txt -s signature.bin
```

---

## Secure Element Implementation

Secure Elements (e.g., NXP A71CH, Infineon OPTIGA) support:

- Key generation and storage
- Digital signatures
- Secure boot
- Tamper resistance

Implementation varies by vendor — consult your SE vendor's SDK.

---

## HSM Implementation

HSMs (e.g., YubiHSM, Thales Luna) support:

- High-performance key generation
- Hardware-bound signing
- Key rotation
- Audit logging

Implementation varies by vendor — consult your HSM vendor's SDK.

---

## Manufacturer Key Distribution

See `docs/manufacturer-key-distribution.md` for how manufacturers distribute public keys to S-CAs.

---

## Compliance Checklist

- [ ] Private key is non-extractable
- [ ] Signing is hardware-bound
- [ ] Key rotation is supported
- [ ] Secure boot is supported
- [ ] Public key export is supported
- [ ] Challenge-response protocol is implemented
- [ ] Audit logging is supported

---

## Getting Help

- **Questions:** Open a GitHub Discussion in the "Q&A" category
- **Bugs:** Open an issue using the Bug Report template
- **Security:** Email security@alboe.local

---

*SEAI Identity Standard — Hardware Vendor Integration Guide v1.0*