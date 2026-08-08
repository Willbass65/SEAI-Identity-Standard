---
name: Security Review
about: Report a security review finding or request a review of a SEAI component
title: "[SECURITY] "
labels: security
assignees: ''
---

## ⚠️ Important

If you are reporting a **vulnerability**, do NOT use this template. Report privately to: **security@alboe.local**

This template is for **security review findings** and **review requests** only.

---

## Review Type

- [ ] Cryptographic review (signature algorithms, key management)
- [ ] Protocol review (attestation, firewall, revocation)
- [ ] Implementation review (reference code, examples)
- [ ] Threat model review
- [ ] Other (please specify)

## Component Under Review

- [ ] Birth certificate format
- [ ] Hardware attestation protocol
- [ ] Lineage tracking
- [ ] Authority scopes
- [ ] Revocation system
- [ ] Identity firewall
- [ ] S-CA (Sovereign Certificate Authority)
- [ ] Other (please specify)

## Finding Summary

A clear and concise description of the security finding or review request.

## Severity

- [ ] Critical — bypass of identity verification or revocation
- [ ] High — weakening of trust guarantees
- [ ] Medium — potential issue under specific conditions
- [ ] Low — hardening recommendation
- [ ] Informational — best practice suggestion

## Detailed Analysis

Provide a detailed technical analysis of the finding.

## Recommended Mitigation

What should be done to address this finding?

## References

- Relevant SPEC.md sections
- Related SEAI-P proposals
- External references (papers, standards, CVEs)