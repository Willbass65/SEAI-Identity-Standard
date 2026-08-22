#!/usr/bin/env python3
"""SEAI-P-003 Reference Verifier — Interaction Birthcertificate Tags.

Implements the seven-step check order adopted in Round 3 of the triad
consensus (see docs/proposals/SEAI-P-003-redline.md):

    1. Schema validation          (schemas/v1.1/interaction_birthcertificate.json)
    2. Expiry check               (expires_at; expired tags are ALWAYS denied)
    3. Revocation check           (bc_id against the revocation list)
    4. Scope check                (requested_action in allowed_actions;
                                   inline scope must be a subset of the BC scope)
    5. Handoff attestation check  (required at hardware-boundary crossings;
                                   privileged delegation requires S-CA countersignature)
    6. Signature check            (RFC 8785 JCS-canonical payload;
                                   dev-test profile rejected in production mode)
    7. Lineage check              (chain_depth <= max (default 256) unless a valid
                                   checkpoint is present; parent hash in session ledger)

Fail-closed: the first failing step denies and logs. A tag is allowed only
when all seven steps pass.

SIGNATURE PROFILES (honest limits, per schema v2.1):
  * 'dev-test'        — HMAC-SHA256 over the JCS-canonical payload with a
                        registered development key. For tests and local dev ONLY.
  * 'hardware-rooted' — verified by the deployment-supplied callback bound to
                        the hardware_id's registered key material (SPEC §3.2).
  This module makes the lowered bar explicit rather than silent.
"""

from __future__ import annotations

import base64
import copy
import datetime as _dt
import hashlib
import hmac
import json
import os
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

import jsonschema

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_HERE, ".."))
SCHEMA_PATH = os.path.join(_REPO_ROOT, "schemas", "v1.1", "interaction_birthcertificate.json")


# RFC 8785 (JCS) canonical serialization for the P-003 vocabulary. The schema
# restricts values to strings, integers, booleans, null, arrays and objects
# (no floats), so UTF-8 + sorted keys + compact separators is exactly JCS for
# this subset. If floats are ever admitted, a full JCS implementation
# (number canonicalization) becomes mandatory.
def jcs(payload: Any) -> bytes:
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _now_utc() -> _dt.datetime:
    return _dt.datetime.now(_dt.timezone.utc)


def _parse_iso(value: str) -> Optional[_dt.datetime]:
    try:
        return _dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def _signed_payload(tag: Dict[str, Any]) -> bytes:
    """Bytes covered by the signature: JCS of the tag with signature.value omitted."""
    stripped = copy.deepcopy(tag)
    stripped.get("signature", {}).pop("value", None)
    return jcs(stripped)


def _b64(raw: bytes) -> str:
    return base64.b64encode(raw).decode("ascii")


@dataclass
class Verdict:
    """Result of one verification. `allowed` is the sole authority."""
    allowed: bool
    step: Optional[str] = None   # e.g. "4-scope"
    reason: str = ""
    event: Optional[Dict[str, Any]] = None  # audit-log record for denials

    @classmethod
    def deny(cls, step: str, reason: str, tag: Dict[str, Any]) -> "Verdict":
        return cls(
            allowed=False,
            step=step,
            reason=reason,
            event={
                "utc": _now_utc().isoformat(),
                "step": step,
                "reason": reason,
                "session_id": (tag.get("interaction") or {}).get("session_id"),
                "action_sequence": (tag.get("interaction") or {}).get("action_sequence"),
                "bc_id": (tag.get("agent_identity") or {}).get("bc_id"),
                "hardware_id": (tag.get("agent_identity") or {}).get("hardware_id"),
            },
        )

    @classmethod
    def allow(cls) -> "Verdict":
        return cls(allowed=True, reason="all seven checks passed")


class BCRecord:
    """The verifier's copy of a Birth Certificate's verifiable facts."""

    def __init__(self, bc_id: str, hardware_id: str, checksum: str,
                 allowed_actions: List[str], forbidden_actions: List[str]):
        self.bc_id = bc_id
        self.hardware_id = hardware_id
        self.checksum = checksum
        self.allowed_actions = set(allowed_actions)
        self.forbidden_actions = set(forbidden_actions)


class SessionLedger:
    """Tags this verifier has already admitted, keyed by session.

    Used by step 7 (parent hash must be known for non-genesis tags) and
    step 5 (parent tag lookup for handoff checks).
    """

    def __init__(self) -> None:
        self._tags: Dict[str, Dict[int, Dict[str, Any]]] = {}

    def record(self, tag: Dict[str, Any]) -> None:
        sess = tag["interaction"]["session_id"]
        self._tags.setdefault(sess, {})[tag["interaction"]["action_sequence"]] = tag

    def parent_of(self, tag: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        sess = tag["interaction"]["session_id"]
        seq = tag["interaction"]["action_sequence"]
        return self._tags.get(sess, {}).get(seq - 1)

    def has_hash(self, tag_hash: str) -> bool:
        for entries in self._tags.values():
            for t in entries.values():
                if hashlib.sha256(jcs(t)).hexdigest() == tag_hash:
                    return True
        return False

    def tag_hash(self, tag: Dict[str, Any]) -> str:
        return hashlib.sha256(jcs(tag)).hexdigest()


@dataclass
class VerifierConfig:
    """Deployment parameters (Round 3, Q2: cadence is config, not schema law)."""
    production: bool = True
    max_chain_depth: int = 256          # RECOMMENDED default; tunable per deployment
    revocation_list: set = field(default_factory=set)        # revoked bc_ids
    bc_registry: Dict[str, BCRecord] = field(default_factory=dict)
    dev_keys: Dict[str, bytes] = field(default_factory=dict)  # hardware_id -> dev HMAC key
    hardware_signature_verifier: Optional[Callable[[str, bytes, str], bool]] = None
    sca_verifier: Optional[Callable[[bytes, str], bool]] = None  # S-CA countersignature check
    clock: Callable[[], _dt.datetime] = _now_utc


class Verifier:
    def __init__(self, config: VerifierConfig):
        self.cfg = config
        with open(SCHEMA_PATH, "r", encoding="utf-8") as fh:
            self.schema = json.load(fh)
        self._validator = jsonschema.Draft202012Validator(self.schema)

    # ---- public API -------------------------------------------------------

    def check(self, tag: Dict[str, Any], session: SessionLedger) -> Verdict:
        """Run the seven-step check order. First failure denies and logs."""
        for step_fn in (
            self._step1_schema,
            self._step2_expiry,
            self._step3_revocation,
            self._step4_scope,
            self._step5_handoff,
            self._step6_signature,
            self._step7_lineage,
        ):
            verdict = step_fn(tag, session)
            if not verdict.allowed:
                return verdict
        session.record(tag)
        return Verdict.allow()

    # ---- steps ------------------------------------------------------------

    def _step1_schema(self, tag, session) -> Verdict:
        errors = sorted(self._validator.iter_errors(tag), key=lambda e: e.json_path)
        if errors:
            detail = "; ".join(f"{e.json_path}: {e.message}" for e in errors[:3])
            return Verdict.deny("1-schema", f"schema violation: {detail}", tag)
        return Verdict.allow()

    def _step2_expiry(self, tag, session) -> Verdict:
        now = self.cfg.clock()
        issued = _parse_iso(tag["interaction"]["timestamp_utc"])
        expires = _parse_iso(tag["interaction"]["expires_at"])
        if issued is None or expires is None:
            return Verdict.deny("2-expiry", "unparseable timestamp_utc/expires_at", tag)
        if expires <= issued:
            return Verdict.deny("2-expiry", "expires_at not after timestamp_utc", tag)
        if expires <= now:
            return Verdict.deny("2-expiry", "tag expired", tag)
        return Verdict.allow()

    def _step3_revocation(self, tag, session) -> Verdict:
        bc_id = tag["agent_identity"]["bc_id"]
        if bc_id in self.cfg.revocation_list:
            return Verdict.deny("3-revocation", f"bc_id {bc_id} is revoked", tag)
        return Verdict.allow()

    def _step4_scope(self, tag, session) -> Verdict:
        bc_id = tag["agent_identity"]["bc_id"]
        bc = self.cfg.bc_registry.get(bc_id)
        if bc is None:
            return Verdict.deny("4-scope", f"no BC on file for {bc_id}", tag)
        requested = tag["authority"]["requested_action"]
        source = tag["authority"]["scope_source"]

        if "bc_checksum" in source:
            if source["bc_checksum"] != bc.checksum:
                return Verdict.deny("4-scope", "bc_checksum does not match the BC on file", tag)
            allowed, forbidden = bc.allowed_actions, bc.forbidden_actions
        else:  # inline scope
            inline = source["inline"]
            allowed = set(inline["allowed_actions"])
            forbidden = set(inline["forbidden_actions"])
            # Inline scope MUST be a subset of the BC scope (redline honest-limit #3):
            # never more allowed, never fewer forbidden, than the BC grants.
            if not allowed.issubset(bc.allowed_actions):
                return Verdict.deny("4-scope", "inline allowed_actions exceeds BC scope", tag)
            if not bc.forbidden_actions.issubset(forbidden):
                return Verdict.deny("4-scope", "inline forbidden_actions drops a BC-forbidden action", tag)

        # SPEC §3.4: whitelist-only. If it is not in allowed, it is forbidden.
        if requested not in allowed:
            return Verdict.deny(
                "4-scope",
                f"action '{requested}' not in allowed_actions (whitelist-only)",
                tag,
            )
        if requested in forbidden:
            return Verdict.deny("4-scope", f"action '{requested}' is explicitly forbidden", tag)
        return Verdict.allow()

    def _step5_handoff(self, tag, session) -> Verdict:
        parent = session.parent_of(tag)
        att = (tag.get("provenance") or {}).get("handoff_attestation")

        if parent is None:
            # Genesis action (no predecessor in this session): no crossing possible.
            return Verdict.allow()

        parent_hw = parent["agent_identity"]["hardware_id"]
        my_hw = tag["agent_identity"]["hardware_id"]
        crossing = parent_hw != my_hw

        if crossing and att is None:
            return Verdict.deny(
                "5-handoff",
                f"hardware-boundary crossing ({parent_hw} -> {my_hw}) without handoff_attestation",
                tag,
            )
        if att is not None:
            if att["parent_hardware_id"] != parent_hw or att["child_hardware_id"] != my_hw:
                return Verdict.deny("5-handoff", "attestation hardware ids do not match the crossing", tag)
            if att.get("privileged"):
                if not att.get("s_ca_countersignature"):
                    return Verdict.deny("5-handoff", "privileged delegation lacks S-CA countersignature", tag)
                if self.cfg.sca_verifier is not None:
                    payload = jcs({k: v for k, v in att.items()
                                   if k != "s_ca_countersignature"})
                    if not self.cfg.sca_verifier(payload, att["s_ca_countersignature"]):
                        return Verdict.deny("5-handoff", "S-CA countersignature invalid", tag)
        return Verdict.allow()

    def _step6_signature(self, tag, session) -> Verdict:
        sig = tag["signature"]
        profile = sig.get("profile", "hardware-rooted")
        if profile == "dev-test" and self.cfg.production:
            return Verdict.deny("6-signature", "dev-test profile rejected in production mode", tag)

        payload = _signed_payload(tag)
        hw = tag["agent_identity"]["hardware_id"]

        if profile == "dev-test":
            key = self.cfg.dev_keys.get(hw)
            if key is None:
                return Verdict.deny("6-signature", f"no dev key registered for {hw}", tag)
            expected = _b64(hmac.new(key, payload, hashlib.sha256).digest())
            if not hmac.compare_digest(expected, sig["value"]):
                return Verdict.deny("6-signature", "dev-test signature mismatch", tag)
            return Verdict.allow()

        # hardware-rooted: deployment-supplied verifier (hardware_id, payload, value)
        if self.cfg.hardware_signature_verifier is None:
            return Verdict.deny("6-signature", "no hardware signature verifier configured", tag)
        if not self.cfg.hardware_signature_verifier(hw, payload, sig["value"]):
            return Verdict.deny("6-signature", "hardware signature invalid", tag)
        return Verdict.allow()

    def _step7_lineage(self, tag, session) -> Verdict:
        prov = tag["provenance"]
        depth = prov["chain_depth"]
        parent_hash = prov["parent_interaction_hash"]
        has_checkpoint = "checkpoint" in prov

        # Replay: a tag already admitted to the ledger is single-use (the nonce
        # makes each tag unique; resubmission of an identical tag is a replay).
        if session.has_hash(session.tag_hash(tag)):
            return Verdict.deny("7-lineage", "replayed tag (already admitted to session ledger)", tag)

        # Fail-closed past the configured maximum without a checkpoint (Round 3, Q2).
        if depth > self.cfg.max_chain_depth and not has_checkpoint:
            return Verdict.deny(
                "7-lineage",
                f"chain_depth {depth} exceeds max {self.cfg.max_chain_depth} without checkpoint",
                tag,
            )

        if parent_hash is None:
            if depth != 0:
                return Verdict.deny("7-lineage", "genesis tag (null parent hash) must have chain_depth 0", tag)
            return Verdict.allow()

        if not session.has_hash(parent_hash):
            # Fall back to direct parent lookup (the common fresh-tag case).
            parent = session.parent_of(tag)
            if parent is None or session.tag_hash(parent) != parent_hash:
                return Verdict.deny("7-lineage", "parent_interaction_hash not found in session ledger", tag)
        return Verdict.allow()


# ---- dev-test signing helper (tests and local demos only) ------------------

def dev_sign(tag: Dict[str, Any], key: bytes) -> Dict[str, Any]:
    """Attach a dev-test HMAC signature to a tag. NEVER for production."""
    tag = copy.deepcopy(tag)
    tag.setdefault("signature", {})["profile"] = "dev-test"
    tag["signature"]["value"] = _b64(hmac.new(key, _signed_payload(tag), hashlib.sha256).digest())
    return tag
