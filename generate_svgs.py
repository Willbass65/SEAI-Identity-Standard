#!/usr/bin/env python3
"""Generate SVG diagrams for the SEAI Identity Standard."""
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "diagrams")

IDENTITY_FIREWALL_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 950" font-family="Arial, sans-serif" font-size="13">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="#333"/>
    </marker>
    <style>
      .box { fill: #f0f4ff; stroke: #4a6fa5; stroke-width: 2; }
      .step-box { fill: #e8f0fe; stroke: #4a6fa5; stroke-width: 2; }
      .decision-box { fill: #fff3cd; stroke: #856404; stroke-width: 2; }
      .allow-box { fill: #d4edda; stroke: #155724; stroke-width: 2; }
      .deny-box { fill: #f8d7da; stroke: #721c09; stroke-width: 2; }
      .title { font-size: 16px; font-weight: bold; fill: #1a1a2e; }
      .subtitle { font-size: 12px; fill: #555; }
      .label { font-size: 12px; fill: #333; }
      .step-title { font-size: 13px; font-weight: bold; fill: #1a1a2e; }
      .step-detail { font-size: 11px; fill: #555; }
      .arrow-line { stroke: #333; stroke-width: 2; fill: none; }
    </style>
  </defs>
  <text x="450" y="30" text-anchor="middle" class="title">SEAI Identity Firewall</text>
  <text x="450" y="50" text-anchor="middle" class="subtitle">Non-bypassable enforcement layer</text>
  <rect x="250" y="70" width="400" height="100" class="box" rx="8"/>
  <text x="450" y="95" text-anchor="middle" class="step-title">AI Agent (with Birth Certificate)</text>
  <text x="350" y="120" text-anchor="middle" class="label">Birth Certificate</text>
  <text x="350" y="138" text-anchor="middle" class="step-detail">bc_id, hardware_id, lineage</text>
  <text x="550" y="120" text-anchor="middle" class="label">Hardware (TPM/SE)</text>
  <text x="550" y="138" text-anchor="middle" class="step-detail">Embedded Private Key (never leaves)</text>
  <line x1="450" y1="170" x2="450" y2="195" class="arrow-line" marker-end="url(#arrow)"/>
  <text x="460" y="188" class="step-detail">Request privileged action</text>
  <rect x="200" y="200" width="500" height="650" fill="#fafafa" stroke="#4a6fa5" stroke-width="2" rx="8" stroke-dasharray="5,3"/>
  <text x="450" y="222" text-anchor="middle" class="step-title">IDENTITY FIREWALL</text>
  <rect x="230" y="235" width="440" height="60" class="step-box" rx="6"/>
  <text x="450" y="255" text-anchor="middle" class="step-title">Step 1: Birth Certificate Validation</text>
  <text x="450" y="275" text-anchor="middle" class="step-detail">Syntax valid? Checksum match? Revocation = active?</text>
  <line x1="450" y1="295" x2="450" y2="315" class="arrow-line" marker-end="url(#arrow)"/>
  <rect x="230" y="315" width="440" height="60" class="step-box" rx="6"/>
  <text x="450" y="335" text-anchor="middle" class="step-title">Step 2: Hardware Attestation</text>
  <text x="450" y="355" text-anchor="middle" class="step-detail">Challenge nonce, Hardware signs, Verify with manufacturer pubkey</text>
  <line x1="450" y1="375" x2="450" y2="395" class="arrow-line" marker-end="url(#arrow)"/>
  <rect x="230" y="395" width="440" height="60" class="step-box" rx="6"/>
  <text x="450" y="415" text-anchor="middle" class="step-title">Step 3: Lineage Verification</text>
  <text x="450" y="435" text-anchor="middle" class="step-detail">Trusted parent? Authorized origin? Ancestors revoked?</text>
  <line x1="450" y1="455" x2="450" y2="475" class="arrow-line" marker-end="url(#arrow)"/>
  <rect x="230" y="475" width="440" height="60" class="step-box" rx="6"/>
  <text x="450" y="495" text-anchor="middle" class="step-title">Step 4: Authority Scope Check</text>
  <text x="450" y="515" text-anchor="middle" class="step-detail">Action allowed? Forbidden? Authority sufficient?</text>
  <line x1="450" y1="535" x2="450" y2="555" class="arrow-line" marker-end="url(#arrow)"/>
  <rect x="230" y="555" width="440" height="60" class="step-box" rx="6"/>
  <text x="450" y="575" text-anchor="middle" class="step-title">Step 5: Revocation Status Check</text>
  <text x="450" y="595" text-anchor="middle" class="step-detail">BC revoked in S-CA? Ancestors revoked?</text>
  <line x1="450" y1="615" x2="450" y2="635" class="arrow-line" marker-end="url(#arrow)"/>
  <rect x="230" y="635" width="440" height="60" class="decision-box" rx="6"/>
  <text x="450" y="660" text-anchor="middle" class="step-title">Step 6: DECISION</text>
  <text x="450" y="678" text-anchor="middle" class="step-detail">ALL PASS = ALLOW | ANY FAIL = DENY + LOG + QUARANTINE</text>
  <line x1="450" y1="695" x2="450" y2="715" class="arrow-line"/>
  <line x1="300" y1="715" x2="600" y2="715" class="arrow-line"/>
  <line x1="300" y1="715" x2="300" y2="740" class="arrow-line" marker-end="url(#arrow)"/>
  <line x1="600" y1="715" x2="600" y2="740" class="arrow-line" marker-end="url(#arrow)"/>
  <rect x="220" y="740" width="160" height="60" class="allow-box" rx="6"/>
  <text x="300" y="765" text-anchor="middle" class="step-title">ALLOW</text>
  <text x="300" y="785" text-anchor="middle" class="step-detail">Action proceeds</text>
  <rect x="520" y="740" width="160" height="60" class="deny-box" rx="6"/>
  <text x="600" y="765" text-anchor="middle" class="step-title">DENY + LOG</text>
  <text x="600" y="785" text-anchor="middle" class="step-detail">+ QUARANTINE</text>
  <text x="450" y="840" text-anchor="middle" class="step-title">Key Properties</text>
  <text x="450" y="860" text-anchor="middle" class="step-detail">Non-bypassable | Fail-closed | Every privileged action | Full audit log</text>
</svg>'''

LINEAGE_TREE_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 750" font-family="Arial, sans-serif" font-size="13">
  <defs>
    <marker id="arrow2" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="#333"/>
    </marker>
    <style>
      .root-box { fill: #d4edda; stroke: #155724; stroke-width: 2; }
      .active-box { fill: #e8f0fe; stroke: #4a6fa5; stroke-width: 2; }
      .revoked-box { fill: #f8d7da; stroke: #721c09; stroke-width: 2; }
      .suspect-box { fill: #fff3cd; stroke: #856404; stroke-width: 2; }
      .result-box { fill: #f0f4ff; stroke: #4a6fa5; stroke-width: 2; }
      .title { font-size: 16px; font-weight: bold; fill: #1a1a2e; }
      .node-title { font-size: 12px; font-weight: bold; fill: #1a1a2e; }
      .node-detail { font-size: 11px; fill: #555; }
      .arrow-line { stroke: #333; stroke-width: 2; fill: none; }
      .label { font-size: 11px; fill: #555; }
    </style>
  </defs>
  <text x="400" y="30" text-anchor="middle" class="title">SEAI Lineage Tree</text>
  <rect x="250" y="50" width="300" height="80" class="root-box" rx="6"/>
  <text x="400" y="72" text-anchor="middle" class="node-title">seai-bc-00000000 (Root)</text>
  <text x="400" y="90" text-anchor="middle" class="node-detail">Origin: SEAI-LAB-01</text>
  <text x="400" y="105" text-anchor="middle" class="node-detail">Level: 0 (Sandbox) | Status: ACTIVE</text>
  <line x1="400" y1="130" x2="400" y2="160" class="arrow-line" marker-end="url(#arrow2)"/>
  <text x="410" y="150" class="label">birth</text>
  <rect x="250" y="160" width="300" height="80" class="active-box" rx="6"/>
  <text x="400" y="182" text-anchor="middle" class="node-title">seai-bc-00000001</text>
  <text x="400" y="200" text-anchor="middle" class="node-detail">Local Reasoning Agent</text>
  <text x="400" y="215" text-anchor="middle" class="node-detail">Parent: 00000000 | Level: 1 | ACTIVE</text>
  <line x1="400" y1="240" x2="400" y2="270" class="arrow-line" marker-end="url(#arrow2)"/>
  <text x="410" y="260" class="label">birth</text>
  <rect x="250" y="270" width="300" height="80" class="active-box" rx="6"/>
  <text x="400" y="292" text-anchor="middle" class="node-title">seai-bc-00000002</text>
  <text x="400" y="310" text-anchor="middle" class="node-detail">Monitoring/Logging Agent</text>
  <text x="400" y="325" text-anchor="middle" class="node-detail">Parent: 00000001 | Level: 1 | ACTIVE</text>
  <line x1="400" y1="350" x2="400" y2="370" class="arrow-line"/>
  <line x1="200" y1="370" x2="600" y2="370" class="arrow-line"/>
  <line x1="200" y1="370" x2="200" y2="390" class="arrow-line" marker-end="url(#arrow2)"/>
  <line x1="600" y1="370" x2="600" y2="390" class="arrow-line" marker-end="url(#arrow2)"/>
  <text x="300" y="365" class="label">birth</text>
  <text x="500" y="365" class="label">birth</text>
  <rect x="80" y="390" width="240" height="80" class="revoked-box" rx="6"/>
  <text x="200" y="412" text-anchor="middle" class="node-title">seai-bc-00000003</text>
  <text x="200" y="430" text-anchor="middle" class="node-detail">Network Agent</text>
  <text x="200" y="445" text-anchor="middle" class="node-detail">Parent: 00000002 | Level: 2 | REVOKED</text>
  <rect x="480" y="390" width="240" height="80" class="suspect-box" rx="6"/>
  <text x="600" y="412" text-anchor="middle" class="node-title">seai-bc-00000004</text>
  <text x="600" y="430" text-anchor="middle" class="node-detail">Analytics Agent</text>
  <text x="600" y="445" text-anchor="middle" class="node-detail">Parent: 00000002 | Level: 1 | SUSPECT</text>
  <line x1="200" y1="470" x2="200" y2="500" class="arrow-line" marker-end="url(#arrow2)"/>
  <line x1="600" y1="470" x2="600" y2="500" class="arrow-line" marker-end="url(#arrow2)"/>
  <text x="210" y="490" class="label">revocation</text>
  <text x="610" y="490" class="label">cascade flag</text>
  <rect x="100" y="500" width="200" height="70" class="result-box" rx="6"/>
  <text x="200" y="525" text-anchor="middle" class="node-title">REVOCATION</text>
  <text x="200" y="545" text-anchor="middle" class="node-detail">Cannot act, communicate</text>
  <text x="200" y="560" text-anchor="middle" class="node-detail">or impersonate</text>
  <rect x="500" y="500" width="200" height="70" class="result-box" rx="6"/>
  <text x="600" y="525" text-anchor="middle" class="node-title">QUARANTINE</text>
  <text x="600" y="545" text-anchor="middle" class="node-detail">Human review</text>
  <text x="600" y="560" text-anchor="middle" class="node-detail">required</text>
  <text x="400" y="620" text-anchor="middle" class="node-title">Lineage Rules</text>
  <text x="400" y="640" text-anchor="middle" class="node-detail">Every agent has a parent (except root) | Ancestor chain is immutable</text>
  <text x="400" y="655" text-anchor="middle" class="node-detail">Revocation cascades downward | Lineage is verifiable at every action</text>
  <text x="400" y="670" text-anchor="middle" class="node-detail">Origin is permanent</text>
</svg>'''

HARDWARE_ATTESTATION_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 650" font-family="Arial, sans-serif" font-size="13">
  <defs>
    <marker id="arrow3" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="#333"/>
    </marker>
    <style>
      .agent-box { fill: #e8f0fe; stroke: #4a6fa5; stroke-width: 2; }
      .firewall-box { fill: #fff3cd; stroke: #856404; stroke-width: 2; }
      .hw-box { fill: #d4edda; stroke: #155724; stroke-width: 2; }
      .result-box { fill: #f0f4ff; stroke: #4a6fa5; stroke-width: 2; }
      .title { font-size: 16px; font-weight: bold; fill: #1a1a2e; }
      .box-title { font-size: 13px; font-weight: bold; fill: #1a1a2e; }
      .step { font-size: 11px; fill: #333; }
      .step-num { font-size: 11px; font-weight: bold; fill: #4a6fa5; }
      .arrow-line { stroke: #333; stroke-width: 2; fill: none; }
      .dashed { stroke: #999; stroke-width: 1; fill: none; stroke-dasharray: 4,3; }
    </style>
  </defs>
  <text x="450" y="30" text-anchor="middle" class="title">SEAI Hardware Attestation — Challenge-Response</text>
  <rect x="50" y="60" width="180" height="50" class="agent-box" rx="6"/>
  <text x="140" y="90" text-anchor="middle" class="box-title">Agent</text>
  <rect x="360" y="60" width="180" height="50" class="firewall-box" rx="6"/>
  <text x="450" y="90" text-anchor="middle" class="box-title">Identity Firewall</text>
  <rect x="670" y="60" width="180" height="50" class="hw-box" rx="6"/>
  <text x="760" y="90" text-anchor="middle" class="box-title">Hardware (TPM)</text>
  <line x1="140" y1="110" x2="140" y2="530" class="dashed"/>
  <line x1="450" y1="110" x2="450" y2="530" class="dashed"/>
  <line x1="760" y1="110" x2="760" y2="530" class="dashed"/>
  <line x1="140" y1="140" x2="450" y2="140" class="arrow-line" marker-end="url(#arrow3)"/>
  <text x="295" y="135" text-anchor="middle" class="step-num">1. Request action</text>
  <text x="450" y="165" text-anchor="middle" class="step">2. Generate nonce (random 256 bits)</text>
  <line x1="450" y1="180" x2="140" y2="180" class="arrow-line" marker-end="url(#arrow3)"/>
  <text x="295" y="175" text-anchor="middle" class="step-num">3. Send nonce + hardware_id</text>
  <line x1="140" y1="210" x2="760" y2="210" class="arrow-line" marker-end="url(#arrow3)"/>
  <text x="450" y="205" text-anchor="middle" class="step-num">4. Forward nonce to hardware</text>
  <text x="760" y="240" text-anchor="middle" class="step">5. Sign nonce with</text>
  <text x="760" y="255" text-anchor="middle" class="step">embedded private key</text>
  <text x="760" y="270" text-anchor="middle" class="step">(KEY NEVER LEAVES CHIP)</text>
  <line x1="760" y1="285" x2="140" y2="285" class="arrow-line" marker-end="url(#arrow3)"/>
  <text x="450" y="280" text-anchor="middle" class="step-num">6. Return signature</text>
  <line x1="140" y1="315" x2="450" y2="315" class="arrow-line" marker-end="url(#arrow3)"/>
  <text x="295" y="310" text-anchor="middle" class="step-num">7. Send signature</text>
  <text x="450" y="345" text-anchor="middle" class="step">8. Verify signature using</text>
  <text x="450" y="360" text-anchor="middle" class="step">manufacturer public key</text>
  <text x="450" y="380" text-anchor="middle" class="step">9. Confirm hardware_id matches BC</text>
  <line x1="450" y1="400" x2="140" y2="400" class="arrow-line" marker-end="url(#arrow3)"/>
  <text x="295" y="395" text-anchor="middle" class="step-num">10. Decision</text>
  <rect x="50" y="430" width="180" height="50" class="result-box" rx="6"/>
  <text x="140" y="460" text-anchor="middle" class="box-title">ALLOW or DENY</text>
  <rect x="360" y="430" width="180" height="50" class="result-box" rx="6"/>
  <text x="450" y="460" text-anchor="middle" class="box-title">DENY + LOG + QUARANTINE</text>
  <text x="450" y="510" text-anchor="middle" class="box-title">Security Properties</text>
  <text x="450" y="530" text-anchor="middle" class="step">Unforgeable | Non-replayable | Offline-verifiable | Hardware-bound | Tamper-evident</text>
  <text x="450" y="560" text-anchor="middle" class="step">Prevents: Stolen credentials, Copied BC, Cloned hardware, Replay attacks, MITM</text>
</svg>'''

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    svgs = {
        "identity_firewall.svg": IDENTITY_FIREWALL_SVG,
        "lineage_tree.svg": LINEAGE_TREE_SVG,
        "hardware_attestation.svg": HARDWARE_ATTESTATION_SVG,
    }
    for name, content in svgs.items():
        path = os.path.join(OUTPUT_DIR, name)
        with open(path, "w") as f:
            f.write(content.strip() + "\n")
        print(f"Created: {path}")
    print("All SVG diagrams generated successfully.")

if __name__ == "__main__":
    main()