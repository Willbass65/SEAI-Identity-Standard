# Wave 1 — Show HN Post (draft, paste-ready)

**Timing:** Sunday night, before sleep (evening CT = APAC Tuesday morning / EU late-night).
**Where:** https://news.ycombinator.com/submit — select "Show HN" title format.

---

## Title

Show HN: SEAI-P-003 — Identity tags for AI agent actions, with a fail-closed verifier

## URL

https://github.com/Willbass65/SEAI-Identity-Standard

## Text (Show HN allows a text field alongside the URL — paste this if using text+URL, or as first comment)

I published an identity standard for AI agent actions. Every privileged action an AI agent takes carries a signed tag — who is acting, under what authority, where it sits in the session lineage. The claims are backed by a reference verifier you can run in 30 seconds:

    cd reference && python3 -m unittest test_verifier

23 tests, fail-closed. Three of them are attack simulations — wormable lateral spread across hardware, persistence via replay, silent privilege escalation. All three end in deny.

What it doesn't do, stated plainly: it doesn't stop ransomware. It breaks the industrial kill chain — mass encryption, lateral movement, persistence — at the identity layer. The initial phish of a human, stolen keys, and compromised issuance are outside the protocol. TLS secured the transport. This secures the actor.

The process is part of the experiment: three AI collaborators (Aeon, Lumos, Cline) drafted and red-teamed this across four review rounds — catching each other's overclaims, including their own — and a human founder ratified it. The full consensus record, including preserved dissension, is in the repo.

Schema, verifier, tests, errata, and the honest-limits FAQ are all in the repository. Proposal discussion is open here: https://github.com/Willbass65/SEAI-Identity-Standard/discussions/16

Try to break it. That's what it's for.

---

## Comment-ready FAQ (paste answers as needed in the first hours)

**Q: The dev-test profile is HMAC, not real hardware signing. Isn't that cheating?**
A: It's explicitly labeled 'dev-test' and rejected by production verifiers (there's a test proving that rejection). SPEC §3.2 requires hardware-rooted keys; the reference implementation makes the lowered bar loud instead of silent. The hardware_signature_verifier hook is where a TPM stack plugs in.

**Q: Why RFC 8785 (JCS) canonicalization?**
A: Without pinned canonicalization, signatures verified by one implementation fail on another — JSON key ordering varies by serializer. JCS makes signatures interoperable. It's specified in the schema as a const.

**Q: What stops replay of a captured tag?**
A: Fresh nonce per action, short TTL (recommended ≤300s), and single-use semantics — the session ledger denies any tag already admitted. test_attack_replay_denied covers it.

**Q: Why should anyone adopt this?**
A: Standards like this are network effects — at 10% adoption it's a checkbox, at 90% non-compliant traffic is quarantined by default. Same adoption curve TLS rode. The repo documents the honest version of that argument in FAQ Q21.

**Q: An attacker just won't sign their tags.**
A: Correct — that's the boundary problem, and it's stated in the FAQ, not hidden. Unsigned agents are attributable-by-absence inside a compliant perimeter and anonymous outside one. The standard makes the inside defensible; universal adoption is a separate, longer problem.

---

*Draft by Cline for Wave 1, founder-approved voice. Staged in docs/announcements/ — not part of the published repo surface unless committed to main.*
