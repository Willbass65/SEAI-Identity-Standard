# SEAI Identity Standard — Security Policy

## Reporting a Vulnerability

The SEAI Identity Standard takes security seriously. The standard deals with AI agent identity, hardware attestation, cryptographic signatures, and trust frameworks — a vulnerability in this specification could undermine the trust guarantees that implementers and their users rely on.

If you believe you have found a security vulnerability in the SEAI Identity Standard, **do not open a public issue**. Report it privately through one of these channels:

1. **Email:** security@alboe.local
2. **GitHub Security Advisories:** Use the "Report a vulnerability" button on the [Security tab](https://github.com/Willbass65/SEAI-Identity-Standard/security/advisories/new) of the repository

Please include the following in your report:

- A description of the vulnerability and its potential impact
- The specific component affected (birth certificate, attestation, lineage, firewall, revocation, S-CA)
- Steps to reproduce or a proof of concept
- Your assessment of severity (see severity levels below)
- Any suggested mitigations or fixes
- Whether you wish to be credited for the discovery

---

## What Qualifies as a Security Issue

The SEAI Identity Standard is a specification, not a running application. Security issues fall into these categories:

### Critical

- **Identity bypass** — a method to forge or impersonate a valid SEAI agent identity
- **Attestation forgery** — a way to produce a valid attestation quote without possessing the hardware
- **Revocation evasion** — a revoked agent that continues to pass identity verification
- **Firewall bypass** — a path through the identity firewall that skips verification
- **Key compromise vector** — a spec ambiguity that enables private key extraction or reuse

### High

- **Weakening of trust guarantees** — a spec issue that degrades the security properties the standard claims to provide
- **Signature malleability** — a way to alter a signed payload without invalidating the signature
- **Lineage manipulation** — a method to inject a false parent-child relationship in the lineage tree

### Medium

- **Potential issue under specific conditions** — a weakness that requires specific implementation choices or deployment configurations to exploit
- **Spec ambiguity enabling insecure implementations** — unclear language that could lead implementers to build vulnerable systems

### Low

- **Hardening recommendation** — a suggestion that improves security but is not exploitable as written
- **Documentation gap** — missing security guidance for implementers

### Informational

- **Best practice suggestion** — improvements aligned with industry standards (NIST, ISO, OWASP)

---

## What Does NOT Qualify

The following are **not** security vulnerabilities and should be reported through other channels:

- **Feature requests** — use the [Feature Proposal issue template](https://github.com/Willbass65/SEAI-Identity-Standard/issues/new/choose)
- **Theoretical attacks without proof of concept** — if you cannot demonstrate the attack, it is a discussion topic, not a vulnerability
- **Vulnerabilities in third-party implementations** — report those to the respective project, not to the standard
- **Social engineering** — phishing, impersonation, or physical attacks are out of scope for a specification
- **General questions about the spec** — use [GitHub Discussions](https://github.com/Willbass65/SEAI-Identity-Standard/discussions)

For **public security review findings** (not vulnerability reports), use the [Security Review issue template](https://github.com/Willbass65/SEAI-Identity-Standard/issues/new/choose).

---

## Response Timeline

| Stage | Target Time |
|---|---|
| Acknowledgment of report | Within 48 hours |
| Initial assessment and severity classification | Within 7 days |
| Fix or mitigation for Critical issues | Within 7 days of confirmation |
| Fix or mitigation for High issues | Within 30 days of confirmation |
| Fix or mitigation for Medium issues | Within 90 days of confirmation |
| Fix or mitigation for Low issues | Next minor release |
| Public disclosure (after fix is released) | Within 7 days of fix publication |

We will keep you informed of progress at each stage. If you have not received a response within the target time, please follow up by replying to your original report.

---

## Disclosure Policy

The SEAI Identity Standard follows a **coordinated disclosure** model:

1. **Private reporting** — vulnerabilities are reported privately and kept confidential until a fix is available
2. **Fix development** — the maintainer team develops and tests a fix
3. **Coordinated release** — the fix is published in a new version of the specification
4. **Public disclosure** — a security advisory is published describing the vulnerability, its impact, and the fix, typically within 7 days of the fix release
5. **Credit** — reporters are credited in the advisory unless they prefer to remain anonymous

We request that reporters do not publicly disclose vulnerabilities until a fix has been released and the advisory has been published.

---

## Safe Harbor

We consider security research conducted in good faith to be a valuable contribution to the SEAI Identity Standard. We will not pursue legal action against researchers who:

- Report vulnerabilities through the channels described above
- Do not access or modify data that does not belong to them
- Do not degrade or disrupt the SEAI community or its infrastructure
- Give us reasonable time to respond and remediate before any public disclosure

---

## Security Review

Security researchers and cryptographers are encouraged to conduct and publish independent security reviews of the SEAI Identity Standard. Public review findings (not vulnerability reports) can be submitted using the [Security Review issue template](.github/ISSUE_TEMPLATE/security_review.md).

Areas of particular interest for review:

- **Cryptographic design** — signature algorithms, key management, attestation protocols
- **Threat model completeness** — are there attack vectors the spec does not address?
- **Implementation guidance** — does the spec provide enough security guidance for implementers?
- **Spec clarity** — are there ambiguities that could lead to insecure implementations?

---

## Contact

- **Security reports:** security@alboe.local
- **Code of Conduct reports:** conduct@alboe.local
- **General security discussions:** [GitHub Discussions](https://github.com/Willbass65/SEAI-Identity-Standard/discussions)

---

*SEAI Identity Standard — Published openly by ALBOE USA LLC*
*SEAI exists to give AI a way to earn trust, not demand it.*