# Identity Firewall — Verification Flow

## Scenario

Agent `seai-bc-00000001` wants to call an external API (e.g., a cloud service, another agent, or any network endpoint).

## Step-by-Step Verification

### Step 1 — Birth Certificate Validation

```
Firewall: "Present your birth certificate."
Agent:    Sends BC JSON

Firewall checks:
  ✓ Is the BC syntactically valid (all required fields present)?
  ✓ Does the SHA-256 checksum match the content?
  ✓ Is revocation_status = "active"?

Result: PASS → proceed to Step 2
Result: FAIL → DENY + LOG + QUARANTINE
```

### Step 2 — Hardware Attestation

```
Firewall: "Prove you are running on HW-TPM-INTEL-9F3A-72C1."
Firewall: Generates random nonce: "a7f3b2c1d4e5..."

Agent (via hardware):
  Hardware signs nonce using embedded private key
  Returns: signature = Sign_HW(nonce)

Firewall:
  Verifies signature using manufacturer's public key
  Confirms hardware_id matches the BC

Result: PASS → proceed to Step 3
Result: FAIL → DENY + LOG + QUARANTINE
```

### Step 3 — Lineage Verification

```
Firewall checks:
  ✓ Is the agent descended from a trusted parent (seai-bc-00000000)?
  ✓ Is the origin (SEAI-LAB-01) authorized to create agents of this type?
  ✓ Are any ancestors revoked? (Check S-CA ledger)

Result: PASS → proceed to Step 4
Result: FAIL → DENY + LOG + QUARANTINE
```

### Step 4 — Authority Scope Check

```
Firewall checks:
  Requested action: "open_network_socket to api.example.com:443"

  ✓ Is "open_network_sockets" in allowed_actions? → NO (Level 1, local-only)
  ✗ Authority level 1 does not permit network access

Result: FAIL → DENY + LOG
```

### Step 5 — Revocation Status Check

```
Firewall checks:
  ✓ Is seai-bc-00000001 currently revoked in the S-CA ledger? → NO
  ✓ Are any ancestors (seai-bc-00000000) revoked? → NO

Result: PASS → (would proceed if Step 4 passed)
```

### Step 6 — Decision

```
All checks pass → ALLOW the action
Any check fails  → DENY + LOG + QUARANTINE

In this scenario: DENIED at Step 4 (authority scope violation)
```

## Denial Log Entry

```json
{
  "event": "identity_firewall_denial",
  "bc_id": "seai-bc-00000001",
  "reason": "authority_scope_exceeded",
  "requested_action": "open_network_socket to api.example.com:443",
  "failed_step": "step_4_authority_scope_check",
  "timestamp": "2026-08-05T22:47:12Z",
  "firewall_version": "1.0.0"
}
```

## Key Principles

1. **Every privileged action** goes through the firewall — not just login
2. **Fail-closed** — any uncertainty results in denial
3. **Non-bypassable** — the agent cannot skip or override the firewall
4. **Full audit trail** — every denial is logged with complete context
5. **Quarantine on failure** — the agent is flagged for human review