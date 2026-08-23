#!/usr/bin/env python3
"""Unit tests for the SEAI-P-003 reference verifier.

Covers all seven steps of the Round 3 check order, including the three
attack simulations from the triad challenge brief:
  * wormable lateral spread      -> hardware crossing without attestation (step 5)
  * persistence via replay       -> identical tag resubmitted            (step 7)
  * silent privilege escalation  -> action outside allowed_actions       (step 4)

Run: python3 -m unittest discover -s reference -v   (from repo root)
"""

import copy
import datetime as dt
import hashlib
import unittest

from verifier import (
    BCRecord, SessionLedger, Verifier, VerifierConfig, dev_sign,
)

HW_A = "tpm2-node-alpha"
HW_B = "tpm2-node-bravo"
KEY_A = b"dev-key-alpha-0123456789abcdef"
KEY_B = b"dev-key-bravo-0123456789abcdef"
BC_ID = "seai-bc-00000231"
BC_CHECKSUM = hashlib.sha256(b"example-bc-payload").hexdigest()
NOW = dt.datetime(2026, 8, 23, 12, 0, 0, tzinfo=dt.timezone.utc)


def fixed_clock():
    return NOW


def make_bc_registry():
    return {
        BC_ID: BCRecord(
            bc_id=BC_ID,
            hardware_id=HW_A,
            checksum=BC_CHECKSUM,
            allowed_actions=["read_local_files", "write_remote_log"],
            forbidden_actions=["open_network_sockets", "modify_system_binaries", "encrypt_files"],
        )
    }


def make_config(production=False, **overrides):
    cfg = VerifierConfig(
        production=production,
        bc_registry=make_bc_registry(),
        dev_keys={HW_A: KEY_A, HW_B: KEY_B},
        clock=fixed_clock,
    )
    for k, v in overrides.items():
        setattr(cfg, k, v)
    return cfg


def base_tag(seq=1, parent_hash=None, depth=0, hardware_id=HW_A,
             action="write_remote_log", bc_id=BC_ID, scope=None):
    return {
        "seai_version": "1.1",
        "proposal_ref": "SEAI-P-003",
        "interaction": {
            "session_id": "sess_8f92a1b3c7d04e15",
            "action_sequence": seq,
            "timestamp_utc": "2026-08-23T11:58:00Z",
            "nonce": f"bm9uY2UteyBzZXF9LXsgc2VxIH0K{seq:04d}",
            "expires_at": "2026-08-23T12:03:00Z",
        },
        "agent_identity": {
            "bc_id": bc_id,
            "hardware_id": hardware_id,
            "model_digest": "a1b2c3d4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c6d7e8f90",
            "model_name": "llama-3.2-3b-instruct",
        },
        "authority": {
            "level": 2,
            "requested_action": action,
            "scope_source": scope or {"bc_checksum": BC_CHECKSUM},
        },
        "provenance": {
            "parent_interaction_hash": parent_hash,
            "chain_depth": depth,
        },
        "signature": {
            "algorithm": "ECDSA-P256-SHA256",
            "canonicalization": "RFC8785-JCS",
            "value": "placeholder",
            "profile": "dev-test",
        },
    }


def signed(tag, key=KEY_A):
    return dev_sign(tag, key)


class GenesisAllowance(unittest.TestCase):
    def test_valid_genesis_tag_allowed(self):
        v = Verifier(make_config())
        verdict = v.check(signed(base_tag()), SessionLedger())
        self.assertTrue(verdict.allowed, verdict.reason)


class Step1Schema(unittest.TestCase):
    def test_missing_nonce_denied(self):
        tag = signed(base_tag())
        del tag["interaction"]["nonce"]
        v = Verifier(make_config())
        verdict = v.check(tag, SessionLedger())
        self.assertFalse(verdict.allowed)
        self.assertEqual(verdict.step, "1-schema")


class Step2Expiry(unittest.TestCase):
    def test_expired_tag_denied(self):
        tag = base_tag()
        tag["interaction"]["expires_at"] = "2026-08-23T11:59:00Z"  # before NOW
        v = Verifier(make_config())
        verdict = v.check(signed(tag), SessionLedger())
        self.assertFalse(verdict.allowed)
        self.assertEqual(verdict.step, "2-expiry")

    def test_expires_before_issued_denied(self):
        tag = base_tag()
        tag["interaction"]["expires_at"] = "2026-08-23T11:57:00Z"
        v = Verifier(make_config())
        verdict = v.check(signed(tag), SessionLedger())
        self.assertFalse(verdict.allowed)
        self.assertEqual(verdict.step, "2-expiry")


class Step3Revocation(unittest.TestCase):
    def test_revoked_bc_denied(self):
        v = Verifier(make_config(revocation_list={BC_ID}))
        verdict = v.check(signed(base_tag()), SessionLedger())
        self.assertFalse(verdict.allowed)
        self.assertEqual(verdict.step, "3-revocation")


class Step4Scope(unittest.TestCase):
    def test_attack_escalation_action_outside_whitelist_denied(self):
        # Attack simulation: ransomware-style 'encrypt_files' requested by an
        # agent whose BC never allowed it. Whitelist-only (SPEC §3.4).
        v = Verifier(make_config())
        verdict = v.check(signed(base_tag(action="encrypt_files")), SessionLedger())
        self.assertFalse(verdict.allowed)
        self.assertEqual(verdict.step, "4-scope")
        self.assertIn("whitelist-only", verdict.reason)

    def test_explicitly_forbidden_action_denied(self):
        v = Verifier(make_config())
        verdict = v.check(signed(base_tag(action="modify_system_binaries")), SessionLedger())
        self.assertFalse(verdict.allowed)
        self.assertEqual(verdict.step, "4-scope")

    def test_inline_scope_exceeding_bc_denied(self):
        inline = {
            "inline": {
                "allowed_actions": ["write_remote_log", "encrypt_files"],  # not in BC
                "forbidden_actions": ["open_network_sockets", "modify_system_binaries", "encrypt_files"],
            }
        }
        v = Verifier(make_config())
        verdict = v.check(signed(base_tag(scope=inline)), SessionLedger())
        self.assertFalse(verdict.allowed)
        self.assertEqual(verdict.step, "4-scope")
        self.assertIn("exceeds BC scope", verdict.reason)

    def test_bc_checksum_mismatch_denied(self):
        bad = {"bc_checksum": "f" * 64}
        v = Verifier(make_config())
        verdict = v.check(signed(base_tag(scope=bad)), SessionLedger())
        self.assertFalse(verdict.allowed)
        self.assertEqual(verdict.step, "4-scope")

    def test_valid_inline_subset_allowed(self):
        inline = {
            "inline": {
                "allowed_actions": ["write_remote_log"],
                "forbidden_actions": ["open_network_sockets", "modify_system_binaries", "encrypt_files"],
            }
        }
        v = Verifier(make_config())
        verdict = v.check(signed(base_tag(scope=inline)), SessionLedger())
        self.assertTrue(verdict.allowed, verdict.reason)


def admitted_session(v):
    """A ledger holding one admitted genesis tag; returns (ledger, tag, tag_hash)."""
    ledger = SessionLedger()
    tag = signed(base_tag(seq=1))
    verdict = v.check(tag, ledger)
    assert verdict.allowed, verdict.reason
    return ledger, tag, ledger.tag_hash(tag)


class Step5Handoff(unittest.TestCase):
    def test_attack_lateral_spread_without_attestation_denied(self):
        # Attack simulation: worm propagates from node-alpha to node-bravo with
        # no handoff attestation. Denied at the boundary (Round 3 Q4 ruling).
        v = Verifier(make_config())
        ledger, _parent, parent_hash = admitted_session(v)
        child = signed(base_tag(seq=2, parent_hash=parent_hash, depth=1, hardware_id=HW_B), key=KEY_B)
        verdict = v.check(child, ledger)
        self.assertFalse(verdict.allowed)
        self.assertEqual(verdict.step, "5-handoff")
        self.assertIn("without handoff_attestation", verdict.reason)

    def test_crossing_with_valid_attestation_allowed(self):
        v = Verifier(make_config())
        ledger, _parent, parent_hash = admitted_session(v)
        child = base_tag(seq=2, parent_hash=parent_hash, depth=1, hardware_id=HW_B)
        child["provenance"]["handoff_attestation"] = {
            "parent_hardware_id": HW_A,
            "child_hardware_id": HW_B,
            "signature": "MEUCIattest-by-parent-hw",
        }
        verdict = v.check(signed(child, key=KEY_B), ledger)
        self.assertTrue(verdict.allowed, verdict.reason)

    def test_privileged_delegation_without_sca_countersignature_denied(self):
        v = Verifier(make_config())
        ledger, _parent, parent_hash = admitted_session(v)
        child = base_tag(seq=2, parent_hash=parent_hash, depth=1, hardware_id=HW_B)
        child["provenance"]["handoff_attestation"] = {
            "parent_hardware_id": HW_A,
            "child_hardware_id": HW_B,
            "signature": "MEUCIattest-by-parent-hw",
            "privileged": True,
        }
        verdict = v.check(signed(child, key=KEY_B), ledger)
        self.assertFalse(verdict.allowed)
        self.assertEqual(verdict.step, "5-handoff")
        self.assertIn("S-CA countersignature", verdict.reason)

    def test_attestation_wrong_hardware_ids_denied(self):
        v = Verifier(make_config())
        ledger, _parent, parent_hash = admitted_session(v)
        child = base_tag(seq=2, parent_hash=parent_hash, depth=1, hardware_id=HW_B)
        child["provenance"]["handoff_attestation"] = {
            "parent_hardware_id": "tpm2-somewhere-else",
            "child_hardware_id": HW_B,
            "signature": "MEUCIattest",
        }
        verdict = v.check(signed(child, key=KEY_B), ledger)
        self.assertFalse(verdict.allowed)
        self.assertEqual(verdict.step, "5-handoff")


class Step6Signature(unittest.TestCase):
    def test_dev_test_profile_rejected_in_production(self):
        v = Verifier(make_config(production=True))
        verdict = v.check(signed(base_tag()), SessionLedger())
        self.assertFalse(verdict.allowed)
        self.assertEqual(verdict.step, "6-signature")
        self.assertIn("production", verdict.reason)

    def test_scope_valid_tamper_caught_by_signature(self):
        # Sign the tag, then swap the model digest afterward (silent model
        # swap): the signature no longer covers the payload.
        tag = signed(base_tag())
        tag["agent_identity"]["model_digest"] = "b" * 64
        v = Verifier(make_config())
        verdict = v.check(tag, SessionLedger())
        self.assertFalse(verdict.allowed)
        self.assertEqual(verdict.step, "6-signature")

    def test_wrong_dev_key_denied(self):
        v = Verifier(make_config())
        verdict = v.check(signed(base_tag(), key=KEY_B), SessionLedger())
        self.assertFalse(verdict.allowed)
        self.assertEqual(verdict.step, "6-signature")

    def test_hardware_rooted_without_verifier_configured_denied(self):
        tag = signed(base_tag())
        tag["signature"]["profile"] = "hardware-rooted"
        v = Verifier(make_config())
        verdict = v.check(tag, SessionLedger())
        self.assertFalse(verdict.allowed)
        self.assertEqual(verdict.step, "6-signature")
        self.assertIn("no hardware signature verifier", verdict.reason)


class Step7Lineage(unittest.TestCase):
    def test_attack_replay_denied(self):
        # Attack simulation: persistence via resubmitting an admitted tag.
        v = Verifier(make_config())
        ledger, tag, _ = admitted_session(v)
        verdict = v.check(copy.deepcopy(tag), ledger)
        self.assertFalse(verdict.allowed)
        self.assertEqual(verdict.step, "7-lineage")
        self.assertIn("replayed tag", verdict.reason)

    def test_unknown_parent_hash_denied(self):
        v = Verifier(make_config())
        ledger, _tag, _ = admitted_session(v)
        orphan = signed(base_tag(seq=2, parent_hash="e" * 64, depth=1))
        verdict = v.check(orphan, ledger)
        self.assertFalse(verdict.allowed)
        self.assertEqual(verdict.step, "7-lineage")

    def test_depth_over_max_without_checkpoint_denied(self):
        # Fail-closed ruling (Round 3, Q2): no checkpoint, no entry.
        v = Verifier(make_config(max_chain_depth=4))
        tag = signed(base_tag(depth=5, parent_hash=None, seq=1))
        verdict = v.check(tag, SessionLedger())
        self.assertFalse(verdict.allowed)
        self.assertEqual(verdict.step, "7-lineage")
        self.assertIn("without checkpoint", verdict.reason)

    def test_depth_over_max_with_checkpoint_allowed(self):
        v = Verifier(make_config(max_chain_depth=4))
        ledger, _tag, parent_hash = admitted_session(v)
        # Action 2 arrives claiming depth 5 (post-checkpoint chain restart)
        # WITH an S-CA checkpoint: fail-closed rule does not trigger.
        tag = base_tag(seq=2, parent_hash=parent_hash, depth=5)
        tag["provenance"]["checkpoint"] = {
            "chain_digest": "c" * 64,
            "s_ca_signature": "MEUCIsca",
        }
        verdict = v.check(signed(tag), ledger)
        self.assertTrue(verdict.allowed, verdict.reason)

    def test_second_action_with_correct_parent_hash_allowed(self):
        v = Verifier(make_config())
        ledger, _tag, parent_hash = admitted_session(v)
        second = signed(base_tag(seq=2, parent_hash=parent_hash, depth=1))
        verdict = v.check(second, ledger)
        self.assertTrue(verdict.allowed, verdict.reason)


if __name__ == "__main__":
    unittest.main()
