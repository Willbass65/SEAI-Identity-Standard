# SEAI Hardware Attestation — Challenge-Response Diagram

```
 ┌──────────┐       ┌──────────────────┐       ┌─────────────────┐
 │  Agent   │       │ Identity Firewall │       │ Hardware (TPM)  │
 └────┬─────┘       └────────┬─────────┘       └────────┬────────┘
      │                      │                          │
      │ 1. Request action    │                          │
      │─────────────────────>│                          │
      │                      │                          │
      │                      │ 2. Generate nonce        │
      │                      │    (random 256 bits)     │
      │                      │                          │
      │ 3. Send nonce        │                          │
      │    + hardware_id     │                          │
      │<─────────────────────│                          │
      │                      │                          │
      │ 4. Forward nonce     │                          │
      │    to hardware       │                          │
      │─────────────────────────────────────────────────>│
      │                      │                          │
      │                      │ 5. Sign nonce with       │
      │                      │    embedded private key  │
      │                      │    (KEY NEVER LEAVES     │
      │                      │     THE CHIP)            │
      │                      │                          │
      │ 6. Return signature  │                          │
      │<─────────────────────────────────────────────────│
      │                      │                          │
      │ 7. Send signature    │                          │
      │─────────────────────>│                          │
      │                      │                          │
      │                      │ 8. Verify signature      │
      │                      │    using manufacturer    │
      │                      │    public key            │
      │                      │                          │
      │                      │ 9. Confirm hardware_id   │
      │                      │    matches BC            │
      │                      │                          │
      │ 10. Decision         │                          │
      │<─────────────────────│                          │
      │                      │                          │
      ▼                      ▼                          ▼
 ┌──────────┐       ┌──────────────────┐
 │  ALLOW   │       │  DENY + LOG      │
 │  or      │       │  + QUARANTINE    │
 │  DENY    │       │                  │
 └──────────┘       └──────────────────┘
```

## Security Properties

| Property | How It's Achieved |
|---|---|
| **Unforgeable** | Private key embedded in silicon — cannot be extracted |
| **Non-replayable** | Nonce is random and single-use per verification |
| **Offline-verifiable** | Manufacturer public key is pre-cached locally |
| **Hardware-bound** | Copied BC on different hardware fails signature check |
| **Tamper-evident** | Physical modification breaks the key pair |

## What This Prevents

```
Attack: Stolen credentials
  └─ SEAI: Credentials alone insufficient — hardware must attest

Attack: Copied birth certificate
  └─ SEAI: BC on wrong hardware fails the nonce signature

Attack: Cloned hardware
  └─ SEAI: Fuse-burn identity cannot be replicated on different silicon

Attack: Replay attack
  └─ SEAI: Nonce is random — old signatures are invalid

Attack: Man-in-the-middle
  └─ SEAI: Signature bound to nonce, not request content