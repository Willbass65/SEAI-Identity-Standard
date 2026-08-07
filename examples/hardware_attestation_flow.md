# Hardware Attestation — Challenge-Response Handshake

## Overview

Hardware attestation proves that an AI agent is running on the physical hardware it claims in its birth certificate. The private key never leaves the hardware — only the signature is transmitted.

## Participants

| Participant | Role |
|---|---|
| **Agent** | The AI system requesting a privileged action |
| **Identity Firewall** | The verification layer that enforces SEAI rules |
| **Hardware (TPM/SE/HSM)** | The physical chip that holds the private key |
| **Manufacturer Public Key** | Pre-published key used to verify hardware signatures |

## Handshake Flow

```
┌─────────────┐          ┌──────────────────┐          ┌─────────────┐
│   Agent     │          │ Identity Firewall │          │  Hardware   │
│             │          │                  │          │ (TPM/SE/HSM)│
└──────┬──────┘          └────────┬─────────┘          └──────┬──────┘
       │                          │                           │
       │  1. Request action       │                           │
       │ ────────────────────────>│                           │
       │                          │                           │
       │                          │  2. Generate nonce        │
       │                          │  (random 256-bit value)   │
       │                          │                           │
       │  3. Send nonce +         │                           │
       │     hardware_id          │                           │
       │ <────────────────────────│                           │
       │                          │                           │
       │  4. Forward nonce        │                           │
       │     to hardware          │                           │
       │ ────────────────────────────────────────────────────>│
       │                          │                           │
       │                          │  5. Hardware signs nonce  │
       │                          │     using embedded        │
       │                          │     private key           │
       │                          │     (key NEVER leaves     │
       │                          │      the chip)            │
       │                          │                           │
       │  6. Return signature     │                           │
       │ <────────────────────────────────────────────────────│
       │                          │                           │
       │  7. Send signature       │                           │
       │ ────────────────────────>│                           │
       │                          │                           │
       │                          │  8. Verify signature      │
       │                          │     using manufacturer's  │
       │                          │     public key            │
       │                          │                           │
       │                          │  9. Confirm hardware_id   │
       │                          │     matches birth cert    │
       │                          │                           │
       │                          │  10. Result:              │
       │                          │      PASS → continue      │
       │                          │      FAIL → DENY + LOG    │
       │                          │                           │
       │  11. Decision            │                           │
       │ <────────────────────────│                           │
       │                          │                           │
```

## Pseudocode

```
# Firewall side
function verify_hardware_attestation(agent, birth_certificate):
    nonce = generate_random_nonce(256)
    hardware_id = birth_certificate.hardware_id

    # Send challenge to agent
    signature = agent.request_hardware_signature(nonce)

    # Look up manufacturer public key for this hardware_id
    manufacturer_pubkey = lookup_manufacturer_key(hardware_id)

    # Verify the signature
    if verify_signature(manufacturer_pubkey, nonce, signature):
        # Signature is valid — hardware is genuine
        if hardware_id == birth_certificate.hardware_id:
            return ATTESTATION_PASS
        else:
            return ATTESTATION_FAIL  # hardware_id mismatch
    else:
        return ATTESTATION_FAIL  # invalid signature

# Hardware side (inside TPM/SE/HSM)
function sign_nonce(nonce):
    # Private key is embedded in hardware — CANNOT be extracted
    private_key = hardware_embedded_key()
    signature = rsa_sign(private_key, nonce)
    return signature
    # Key NEVER leaves the chip
```

## Security Properties

1. **Unforgeable** — the private key is embedded in silicon and cannot be extracted
2. **Non-replayable** — each nonce is random and single-use
3. **Offline-verifiable** — the manufacturer's public key is pre-published; no cloud needed
4. **Hardware-bound** — a copied birth certificate on different hardware will fail attestation
5. **Tamper-evident** — any modification to the hardware breaks the key pair

## What This Prevents

| Attack | How SEAI Attestation Stops It |
|---|---|
| Stolen credentials | Credentials alone are insufficient — hardware must match |
| Copied birth certificate | BC on different hardware fails the signature check |
| Cloned hardware | Fuse-burn identity cannot be replicated on different silicon |
| Replay attack | Nonce is random and single-use per verification |
| Man-in-the-middle | Signature is bound to the nonce, not the request content |

## Manufacturer Key Distribution

Manufacturers publish their public keys through:

- Their official website / developer portal
- Hardware specification documents
- SEAI community registry (mirrored, not authoritative)

The firewall maintains a local cache of manufacturer public keys. Keys are never fetched at verification time (to prevent network-based attacks on the verification process itself).