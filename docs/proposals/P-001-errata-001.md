# SEAI-P-001 Errata 001 — Deprecation of `agent_id` field name

**Status:** Triad internal draft — NOT published.
**Date:** 2026-08-23
**Applies to:** `schemas/v1/attestation.json` (SEAI-P-001 Hardware Attestation Payload)
**Origin:** Round 3, Q1 consensus ruling (unanimous) of the triad (Aeon, Lumos, Cline), recorded in `SEAI-P-003-redline.md`.

---

## Issue

SEAI-P-001's attestation schema uses `agent_id` and free-form field naming, while the core specification (SPEC §3.1) defines the authoritative identity vocabulary: `bc_id` and `hardware_id`. Two names for the same concept create fragmentation risk — a verifier would need to parse multiple identifiers for one identity, which is a security bug class, not a style issue.

## Ruling

SPEC §3.1 is the constitutional baseline:

1. `bc_id` and `hardware_id` are the authoritative field names for v1.1 and all future SEAI artifacts.
2. P-001's `agent_id` is hereby **deprecated** as a legacy alias for `bc_id`.
3. During a transition window, parsers MAY accept legacy P-001 payloads that use `agent_id`.
4. New implementations MUST emit SPEC field names; emitting `agent_id` in new artifacts is non-compliant.

## Required changes to `schemas/v1/attestation.json` (when published)

| Current (P-001) | Authoritative (SPEC §3.1) |
|---|---|
| `agent_id` | `bc_id` (with transition alias accepted on input) |
| (absent) | `hardware_id` (P-001's `hardware_provider` remains distinct: it names the anchor *type*, not the instance) |

`timestamp_utc` is unaffected (already SPEC-compatible naming).

## Note for reviewers

This errata intentionally does not rewrite the v1.0 schema file in place. Standards bodies log corrections via errata documents and apply them at the next schema revision, preserving the audit trail of what v1.0 actually said. This document is the paper trail.
