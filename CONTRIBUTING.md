# Contributing to the SEAI Identity Standard

We welcome contributions from developers, researchers, hardware vendors, and AI safety experts.

---

## Ways to Contribute

- **Propose improvements** to `SPEC.md` — open an issue describing the change and rationale
- **Submit new examples** — birth certificate schemas, firewall flows, attestation implementations
- **Add hardware attestation implementations** — reference code for TPM, secure element, or HSM integration
- **Create diagrams or visualizations** — improve or replace ASCII diagrams with proper graphics
- **Discuss lineage and authority models** — propose refinements to the authority levels or cascade rules
- **Security review** — cryptographers and security researchers are encouraged to audit the standard

---

## Core Principles That Must Be Preserved

All contributions must preserve:

1. **Sovereignty** — identity tied to hardware, not cloud accounts
2. **Hardware-rooted identity** — the root of trust is physical silicon
3. **Open access** — no licensing fees, no vendor lock-in
4. **Non-proprietary governance** — no corporation or government controls the standard
5. **Fail-closed design** — any verification failure results in denial
6. **Non-bypassable firewall** — no override, no exception

---

## How to Submit Changes

1. **Open an issue** describing your proposed change
2. **Fork the repository**
3. **Create a branch** from `main` (e.g., `feature/add-ecdsa-support`)
4. **Make your changes** with clear commit messages
5. **Submit a pull request** referencing the original issue
6. **Respond to review feedback**

---

## Pull Request Guidelines

- Changes to `SPEC.md` that alter the birth certificate format or firewall protocol require a **major version bump**
- Additive changes (new fields, new examples) require a **minor version bump**
- Typo fixes and clarifications require a **patch version bump**
- All JSON examples must be **valid JSON** — test before submitting
- All new diagrams must include **text-based versions** (ASCII) for accessibility

---

## Code of Conduct

This project follows the [SEAI Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to **conduct@alboe.local**.

---

## License

By contributing to the SEAI Identity Standard, you agree that your contributions will be licensed under the Apache 2.0 license.

---

*SEAI Identity Standard — Published openly by ALBOE USA LLC*