# SEAI-P-003 Reference Verifier

Reference implementation of the Interaction Birthcertificate Tag verifier
(SEAI-P-003, triad consensus Round 3). Python 3.10+, depends only on
`jsonschema`.

## The seven-step check order

| # | Step | Denies when |
|---|---|---|
| 1 | Schema | tag does not validate against `schemas/v1.1/interaction_birthcertificate.json` |
| 2 | Expiry | `expires_at` passed (or not after `timestamp_utc`) — always denied |
| 3 | Revocation | `bc_id` is on the revocation list (SPEC §8) |
| 4 | Scope | `requested_action` not in `allowed_actions` (SPEC §3.4 whitelist-only), explicitly forbidden, or inline scope exceeds the BC scope |
| 5 | Handoff | hardware-boundary crossing without `handoff_attestation`; privileged delegation without S-CA countersignature |
| 6 | Signature | signature invalid over the JCS-canonical payload; `dev-test` profile in production mode |
| 7 | Lineage | tag already admitted (replay); `chain_depth` over max without checkpoint (fail-closed); `parent_interaction_hash` unknown to the session ledger |

Fail-closed: first failing step denies and produces an audit event
(`Verdict.event`). A tag is admitted only when all seven pass.

## Usage

```python
from verifier import Verifier, VerifierConfig, SessionLedger, BCRecord

config = VerifierConfig(
    production=True,                       # rejects dev-test signatures
    max_chain_depth=256,                   # Round 3 Q2: deployment parameter
    bc_registry={bc.bc_id: bc},            # verifier's copy of Birth Certificates
    revocation_list=revoked_ids,
    hardware_signature_verifier=my_hw_fn,  # deployment crypto stack (hw_id, payload, sig)
)
v = Verifier(config)
session = SessionLedger()
verdict = v.check(tag, session)
if verdict.allowed:
    ...  # execute the privileged action
else:
    log(verdict.step, verdict.reason, verdict.event)  # deny + audit
```

## Attack simulations (in `test_verifier.py`)

The three attack scenarios from the triad challenge brief are encoded as
tests and all end in **deny**:

- **Wormable lateral spread** — action crossing hardware without a handoff
  attestation → denied at step 5
- **Persistence via replay** — resubmission of an admitted tag → denied at
  step 7
- **Silent privilege escalation** — `encrypt_files` requested by an agent
  whose BC never allowed it → denied at step 4

Plus: expired tags, revoked BCs, scope inflation via inline scopes,
post-signature tampering (silent model swap), wrong signing key, orphaned
lineage, and unbounded chains without checkpoints.

## Honest limits — what this verifier does NOT do

- **Dev-test signatures are HMAC, not hardware.** Production deployments
  MUST supply `hardware_signature_verifier` (SPEC §3.2 hardware-rooted keys).
  The reference implementation makes the lowered bar explicit and rejects it
  in production mode rather than silently accepting weak keys.
- **No checkpoint signature verification.** The presence of a checkpoint
  bypasses the depth limit; validating the S-CA signature over `chain_digest`
  is the deployment's job (the `sca_verifier` hook is called only for
  privileged handoffs today).
- **No BC-chain verification.** The verifier trusts its BC registry copy;
  validating manufacturer/S-CA signatures on the BC itself (SPEC §3) is
  upstream of this module.
- **Session ledger is in-memory.** Real deployments need persistent,
  tamper-evident storage (the Track B transparency-log proposal).
- **JCS subset.** Canonicalization is exact for the P-003 vocabulary
  (strings/integers/booleans/null/arrays/objects). If floats are ever
  admitted to the schema, a full RFC 8785 implementation is required.
- **Lineage proves, the firewall blocks.** As recorded in the redline: the
  hash chain makes lateral movement attributable and auditable; the actual
  blocking is the step-4 scope check.

## Run the tests

```
cd reference && python3 -m unittest test_verifier -v
```

23 tests, zero dependencies beyond `jsonschema`.
