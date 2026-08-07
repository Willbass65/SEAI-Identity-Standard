# SEAI Lineage Tree — Ancestry Diagram

```
                    ┌─────────────────────────┐
                    │   seai-bc-00000000      │
                    │   Root SEAI Agent       │
                    │   Origin: SEAI-LAB-01   │
                    │   Level: 0 (Sandbox)    │
                    │   Status: ACTIVE        │
                    └───────────┬─────────────┘
                                │
                                │ birth
                                ▼
                    ┌─────────────────────────┐
                    │   seai-bc-00000001      │
                    │   Local Reasoning       │
                    │   Parent: 00000000      │
                    │   Level: 1 (Local-only) │
                    │   Status: ACTIVE        │
                    └───────────┬─────────────┘
                                │
                                │ birth
                                ▼
                    ┌─────────────────────────┐
                    │   seai-bc-00000002      │
                    │   Monitoring/Logging    │
                    │   Parent: 00000001      │
                    │   Level: 1 (Local-only) │
                    │   Status: ACTIVE        │
                    └───────────┬─────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
                    │ birth                 │ birth
                    ▼                       ▼
          ┌─────────────────┐     ┌─────────────────┐
          │ seai-bc-00000003│     │ seai-bc-00000004│
          │ Network Agent   │     │ Analytics Agent │
          │ Parent: 00000002│     │ Parent: 00000002│
          │ Level: 2 (Net)  │     │ Level: 1 (Local)│
          │ Status: REVOKED │     │ Status: SUSPECT │
          └─────────────────┘     └─────────────────┘
               │                         │
               │ revocation              │ cascade flag
               │ reason: unauthorized    │ (ancestor revoked)
               │ behavior                │
               ▼                         ▼
          ┌─────────────────┐     ┌─────────────────┐
          │  REVOCATION     │     │  QUARANTINE     │
          │  Agent cannot   │     │  Human review   │
          │  act, communicate│     │  required before│
          │  or impersonate │     │  agent may act  │
          └─────────────────┘     └─────────────────┘
```

## Lineage Rules

1. **Every agent has a parent** — except the root agent (origin)
2. **Ancestor chain is immutable** — recorded at birth, never modified
3. **Revocation cascades downward** — if a parent is revoked, descendants are flagged suspect
4. **Lineage is verifiable** — the firewall checks the full ancestor chain at every action
5. **Origin is permanent** — the lab/organization that created the root is recorded forever

## Revocation Cascade

```
When seai-bc-00000003 is revoked:

  1. S-CA ledger entry: seai-bc-00000003 → REVOKED
  2. Identity firewall receives revocation notification
  3. seai-bc-00000003: ALL actions denied immediately
  4. seai-bc-00000004 (child): flagged as SUSPECT
     - Actions denied until human review
     - Human may: revoke, reinstate, or re-birth
  5. Any future children of 00000003: birth denied by S-CA