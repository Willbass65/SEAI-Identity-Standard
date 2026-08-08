# SEAI Identity Standard — Governance Model

> This document defines how the SEAI Identity Standard is governed, maintained, and evolved.
> It is the container the community fills with content.
> The founder provides the structure. The world builds the rules.

---

## 1. Mission & Principles

### Purpose
SEAI exists to give AI a way to earn trust, not demand it. It provides a hardware-rooted identity framework for autonomous AI systems that is free, open, sovereign, and global.

### Core Principles
- **Sovereignty** — identity tied to hardware, not cloud accounts
- **Hardware-rooted identity** — the root of trust is physical silicon
- **Open access** — no licensing fees, no vendor lock-in
- **Non-proprietary governance** — no corporation or government controls the standard
- **Fail-closed design** — any verification failure results in denial
- **Non-bypassable firewall** — no override, no exception
- **Transparency** — all proposals, decisions, and revisions are public

---

## 2. Roles & Responsibilities

### Maintainers
- Responsible for the technical integrity of the standard
- Review and merge pull requests
- Manage versioning and releases
- Ensure security reviews are conducted before major versions
- Current maintainer: William Bassett Jr. (ALBOE USA LLC)

### Contributors
- Submit proposals, examples, and implementations
- Participate in discussions
- Review pull requests
- Report security vulnerabilities

### Reviewers
- Domain experts who review proposals
- Cryptographic reviewers for security-sensitive changes
- Hardware vendor reviewers for attestation-related changes
- Community reviewers for documentation and examples

### Community Members
- Participate in discussions
- Provide feedback on proposals
- Help with documentation
- Adopt and implement the standard

### Proposal Authors
- Submit formal proposals (SEAI-P)
- Respond to review feedback
- Maintain their proposal through the approval process

---

## 3. Proposal Process (SEAI-P)

### Proposal Naming
All proposals use the prefix `SEAI-P` followed by a sequential number:
- `SEAI-P-001` — First proposal
- `SEAI-P-002` — Second proposal
- etc.

### Submission
1. Open a GitHub Discussion in the "Ideas" category
2. Title: `SEAI-P-XXX: [Proposal Title]`
3. Body must include:
   - Problem statement
   - Proposed solution
   - Impact on existing versions
   - Security considerations
   - Implementation guidance (if applicable)

### Discussion Period
- Minimum 14 days for minor proposals
- Minimum 30 days for major proposals (version-changing)
- Discussion remains open until consensus is reached or a vote is called

### Review Requirements
- All proposals require at least one maintainer review
- Security-sensitive proposals require cryptographic reviewer review
- Hardware-related proposals require hardware vendor review
- Major proposals require at least two reviewer approvals

### Acceptance Criteria
- No unresolved security objections
- No unresolved technical objections
- Consensus reached (see Section 4)
- Versioning impact assessed and documented

---

## 4. Voting & Decision Making

### Consensus Model
SEAI uses **lazy consensus** as the default decision model:
- A proposal is considered accepted if no maintainer objects within the discussion period
- If any maintainer objects, the proposal moves to a formal vote

### Formal Vote
When consensus cannot be reached:
- Maintainers vote (1 vote each)
- Simple majority required for minor proposals
- Supermajority (2/3) required for major proposals (version-changing)
- Tie-breaking: the founding maintainer (William Bassett Jr.) casts the deciding vote

### Emergency Decisions
For security-critical issues:
- Any maintainer can declare an emergency
- Emergency fixes can be merged immediately with a single maintainer approval
- Emergency changes must be documented and reviewed within 7 days
- Emergency changes require a retroactive community review

---

## 5. Versioning & Releases

### Semantic Versioning
SEAI follows semantic versioning (MAJOR.MINOR.PATCH):

| Change Type | Version Impact | Example |
|---|---|---|
| New required field in birth certificate | MAJOR | Adding `cluster_id` field |
| New optional field or extension | MINOR | Adding `transparency_log` field |
| Clarification, typo fix, example update | PATCH | Fixing a typo in SPEC.md |
| Security-critical change | Immediate patch + advisory | Fixing a revocation bypass |

### Release Cadence
- Patch releases: as needed
- Minor releases: quarterly (if proposals are accepted)
- Major releases: annually (or when a major proposal is accepted)
- Emergency patches: immediate

### Deprecation Policy
- Deprecated fields are marked in SPEC.md with a deprecation notice
- Deprecated fields remain in the spec for at least 2 minor versions before removal
- Removal requires a major version bump

---

## 6. Amendments & Revisions

### Governance Evolution
This governance model itself is versioned and can be amended:
- Governance version: `GOV-v0.1`
- Amendments require a SEAI-P proposal
- Amendments require supermajority (2/3) maintainer approval
- Community ratification via discussion

### Amendment Submission
1. Open a SEAI-P proposal targeting `GOVERNANCE.md`
2. Specify the section being amended
3. Provide rationale and impact assessment
4. Follow the standard proposal process

---

## 7. Transparency Requirements

### Public Records
- All proposals are public (GitHub Discussions)
- All decisions are public (GitHub Issues and Discussions)
- All version releases are public (GitHub Releases)
- All security advisories are public (GitHub Security Advisories)
- The traffic scorecard is public (`SCORECARD.md`)

### Decision Logs
- Maintainer votes are recorded in the proposal discussion
- Emergency decisions are documented in a GitHub Issue
- All merged pull requests are public

### Public Roadmap
- The roadmap (`ROADMAP.md`) is maintained and updated publicly
- Roadmap changes require a SEAI-P proposal

---

## 8. Security Disclosure Policy

### Reporting a Vulnerability
- Report security vulnerabilities privately to: security@alboe.local
- Do NOT open a public issue for security vulnerabilities
- Include: description, reproduction steps, impact assessment, suggested fix (if any)

### Response Timeline
- Acknowledgment: within 48 hours
- Initial assessment: within 7 days
- Fix or mitigation: within 30 days (severity-dependent)
- Public disclosure: after fix is released, or 90 days (whichever comes first)

### Security Advisories
- Published via GitHub Security Advisories
- Tagged with CVE numbers when applicable
- Documented in the security advisory database

---

## 9. Contributor License Agreement (CLA)

### Requirement
All contributors must sign the SEAI CLA before their contributions can be merged.

### What the CLA Covers
- Contributor grants ALBOE USA LLC a license to use their contribution
- Contributor retains copyright on their contribution
- Contributor certifies they have the right to contribute
- Contributor certifies the contribution is not proprietary

### CLA Process
- CLA is signed electronically via GitHub (CLA Assistant or similar)
- CLA is required for all pull requests
- CLA is stored in a public record

---

## 10. Conflict of Interest Policy

### Disclosure
- Maintainers and reviewers must disclose any financial interest in hardware vendors, AI companies, or competitors
- Disclosures are recorded in a public `CONFLICTS.md` file

### Recusal
- A maintainer or reviewer with a conflict of interest must recuse themselves from voting on or reviewing proposals that benefit their affiliated organization
- Recusal is recorded in the proposal discussion

### Vendor Neutrality
- No single vendor may dominate the standard
- Vendor-specific fields are not allowed in the core birth certificate format
- Vendor extensions are allowed only as optional fields with a vendor namespace prefix

---

## 11. Community Conduct

### Standards
- Be respectful and constructive
- Focus on the technical merit of proposals
- No marketing or product promotion
- No proprietary lock-in proposals
- Credit original authors when building on their work
- Safety-first mindset in all discussions

### Enforcement
- Violations are reported to maintainers
- Repeated violations result in removal from discussions
- Severe violations result in permanent ban from the community

---

*SEAI Identity Standard — Governance Model v0.1*
*Published by ALBOE USA LLC — authored by William Bassett Jr.*
*The founder provides the container. The community fills it with content.*