# SEAI Identity Firewall — Architecture Diagram

```
                    ┌─────────────────────────────────────────────┐
                    │              AI AGENT (with BC)              │
                    │                                             │
                    │  ┌─────────────┐  ┌──────────────────────┐  │
                    │  │ Birth Cert  │  │  Hardware (TPM/SE)   │  │
                    │  │             │  │  ┌────────────────┐  │  │
                    │  │ bc_id       │  │  │ Embedded       │  │  │
                    │  │ hardware_id │  │  │ Private Key    │  │  │
                    │  │ lineage     │  │  │ (never leaves) │  │  │
                    │  │ authority   │  │  └────────────────┘  │  │
                    │  │ revocation  │  └──────────────────────┘  │
                    │  └─────────────┘                             │
                    └──────────────────┬──────────────────────────┘
                                       │
                                       │ Request privileged action
                                       ▼
                    ┌─────────────────────────────────────────────┐
                    │          IDENTITY FIREWALL                  │
                    │     (Non-bypassable enforcement layer)      │
                    │                                             │
                    │  ┌───────────────────────────────────────┐  │
                    │  │ Step 1: Birth Certificate Validation   │  │
                    │  │   • Syntax valid?                     │  │
                    │  │   • Checksum match?                   │  │
                    │  │   • Revocation status = active?       │  │
                    │  └──────────────┬────────────────────────┘  │
                    │                 │                           │
                    │                 ▼                           │
                    │  ┌───────────────────────────────────────┐  │
                    │  │ Step 2: Hardware Attestation           │  │
                    │  │   • Challenge: send nonce              │  │
                    │  │   • Hardware signs nonce               │  │
                    │  │   • Verify with manufacturer pubkey    │  │
                    │  │   • hardware_id matches BC?            │  │
                    │  └──────────────┬────────────────────────┘  │
                    │                 │                           │
                    │                 ▼                           │
                    │  ┌───────────────────────────────────────┐  │
                    │  │ Step 3: Lineage Verification           │  │
                    │  │   • Trusted parent?                   │  │
                    │  │   • Authorized origin?                │  │
                    │  │   • Any ancestors revoked?             │  │
                    │  └──────────────┬────────────────────────┘  │
                    │                 │                           │
                    │                 ▼                           │
                    │  ┌───────────────────────────────────────┐  │
                    │  │ Step 4: Authority Scope Check          │  │
                    │  │   • Action in allowed_actions?        │  │
                    │  │   • Action in forbidden_actions?      │  │
                    │  │   • Authority level sufficient?       │  │
                    │  └──────────────┬────────────────────────┘  │
                    │                 │                           │
                    │                 ▼                           │
                    │  ┌───────────────────────────────────────┐  │
                    │  │ Step 5: Revocation Status Check        │  │
                    │  │   • BC revoked in S-CA ledger?        │  │
                    │  │   • Any ancestors revoked?             │  │
                    │  └──────────────┬────────────────────────┘  │
                    │                 │                           │
                    │                 ▼                           │
                    │  ┌───────────────────────────────────────┐  │
                    │  │ Step 6: DECISION                       │  │
                    │  │   ALL PASS → ALLOW                     │  │
                    │  │   ANY FAIL → DENY + LOG + QUARANTINE   │  │
                    │  └──────────────┬────────────────────────┘  │
                    └─────────────────┼───────────────────────────┘
                                      │
                         ┌────────────┴────────────┐
                         │                         │
                         ▼                         ▼
                   ┌──────────┐             ┌──────────────┐
                   │  ALLOW   │             │ DENY + LOG   │
                   │          │             │ + QUARANTINE │
                   │ Action   │             │              │
                   │ proceeds │             │ Human review │
                   └──────────┘             │ required     │
                                            └──────────────┘
```

## Key Properties

- **Non-bypassable** — the agent cannot skip any step
- **Fail-closed** — any uncertainty = denial
- **Every action** — not just login, every privileged operation
- **Full audit** — every decision is logged with complete context