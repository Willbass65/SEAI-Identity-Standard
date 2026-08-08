use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use thiserror::Error;

/// Default maximum clock drift allowed (5 minutes).
const DEFAULT_MAX_CLOCK_DRIFT_SECONDS: i64 = 300;

#[derive(Error, Debug)]
pub enum ValidationError {
    #[error("Invalid SEAI version: {0}")]
    InvalidVersion(String),
    #[error("Invalid proposal reference: {0}")]
    InvalidProposalRef(String),
    #[error("Timestamp outside acceptable drift window ({0}s limit)")]
    TimestampExpired(i64),
    #[error("Serialization error: {0}")]
    JsonError(#[from] serde_json::Error),
    #[error("Signature verification failed: {0}")]
    SignatureVerificationFailed(String),
    #[error("Base64 decode error: {0}")]
    Base64Error(String),
    #[error("Unsupported key type: kty={0}, crv={1}")]
    UnsupportedKeyType(String, String),
}

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone)]
pub enum HardwareProvider {
    #[serde(rename = "TPM2.0")]
    Tpm2,
    #[serde(rename = "AWS_Nitro")]
    AwsNitro,
    #[serde(rename = "Apple_Secure_Enclave")]
    AppleSecureEnclave,
    #[serde(rename = "HSM_Generic")]
    HsmGeneric,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct AttestationQuote {
    pub quote_data: String,
    pub signature: String,
    pub pcr_indices: Option<Vec<u8>>,
    pub pcr_values: Option<HashMap<String, String>>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct PublicKeyJwk {
    pub kty: String,
    pub crv: String,
    pub x: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SeaiAttestationPayload {
    pub seai_version: String,
    pub proposal_ref: String,
    pub agent_id: String,
    pub timestamp_utc: DateTime<Utc>,
    pub hardware_provider: HardwareProvider,
    pub attestation_quote: AttestationQuote,
    pub public_key: PublicKeyJwk,
}

pub struct AttestationValidator {
    pub max_clock_drift_seconds: i64,
}

impl Default for AttestationValidator {
    fn default() -> Self {
        Self {
            max_clock_drift_seconds: DEFAULT_MAX_CLOCK_DRIFT_SECONDS,
        }
    }
}

impl AttestationValidator {
    pub fn new(max_clock_drift_seconds: i64) -> Self {
        Self {
            max_clock_drift_seconds,
        }
    }

    /// Validates the SEAI-P-001 structural, temporal, and cryptographic requirements.
    pub fn validate(&self, payload_json: &str) -> Result<SeaiAttestationPayload, ValidationError> {
        let payload: SeaiAttestationPayload = serde_json::from_str(payload_json)?;

        // 1. Verify Versioning & Proposal Alignment
        if payload.seai_version != "1.0" {
            return Err(ValidationError::InvalidVersion(payload.seai_version));
        }

        if payload.proposal_ref != "SEAI-P-001" {
            return Err(ValidationError::InvalidProposalRef(payload.proposal_ref));
        }

        // 2. Timestamp Freshness Verification (prevents replay attacks)
        let now = Utc::now();
        let drift = (now - payload.timestamp_utc).num_seconds().abs();
        if drift > self.max_clock_drift_seconds {
            return Err(ValidationError::TimestampExpired(self.max_clock_drift_seconds));
        }

        // 3. Signature Verification
        // NOTE: In a production implementation, this would use a Rust crypto library
        // (e.g., `ring`, `ed25519-dalek`, or `p256`) to verify the signature.
        //
        // The verification process:
        // a. Decode the public key `x` from base64
        // b. Decode the `signature` from base64
        // c. Decode the `quote_data` from base64
        // d. Verify the signature against the quote_data using the public key
        //
        // For Ed25519 (kty=OKP, crv=Ed25519):
        //   use ed25519_dalek::{PublicKey, Verifier};
        //   let pubkey = PublicKey::from_bytes(&decoded_x)?;
        //   pubkey.verify(&decoded_quote_data, &decoded_signature)?;
        //
        // For ECDSA P-256 (kty=EC, crv=P-256):
        //   use p256::ecdsa::VerifyingKey;
        //   let vk = VerifyingKey::from_sec1_bytes(&decoded_x)?;
        //   vk.verify(&decoded_quote_data, &signature)?;
        //
        // This stub validates the structure but defers actual crypto verification
        // to the implementer's choice of library.
        self.verify_signature_structure(&payload)?;

        Ok(payload)
    }

    /// Verifies that the signature fields are structurally valid (base64-decodable).
    /// Actual cryptographic verification should be added by the implementer.
    fn verify_signature_structure(&self, payload: &SeaiAttestationPayload) -> Result<(), ValidationError> {
        use base64::Engine;

        // Verify public key is valid base64
        let _decoded_x = base64::engine::general_purpose::STANDARD
            .decode(&payload.public_key.x)
            .map_err(|e| ValidationError::Base64Error(format!("public_key.x: {}", e)))?;

        // Verify signature is valid base64
        let _decoded_sig = base64::engine::general_purpose::STANDARD
            .decode(&payload.attestation_quote.signature)
            .map_err(|e| ValidationError::Base64Error(format!("signature: {}", e)))?;

        // Verify quote_data is valid base64
        let _decoded_quote = base64::engine::general_purpose::STANDARD
            .decode(&payload.attestation_quote.quote_data)
            .map_err(|e| ValidationError::Base64Error(format!("quote_data: {}", e)))?;

        // Verify key type is supported
        match (payload.public_key.kty.as_str(), payload.public_key.crv.as_str()) {
            ("OKP", "Ed25519") => {}
            ("EC", "P-256") => {}
            ("EC", "secp256k1") => {}
            (kty, crv) => {
                return Err(ValidationError::UnsupportedKeyType(kty.to_string(), crv.to_string()));
            }
        }

        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn make_valid_payload_json() -> String {
        format!(
            r#"{{
                "seai_version": "1.0",
                "proposal_ref": "SEAI-P-001",
                "agent_id": "agent-001",
                "timestamp_utc": "{}",
                "hardware_provider": "TPM2.0",
                "attestation_quote": {{
                    "quote_data": "QkFTRTY0X0RBVEE=",
                    "signature": "U0lHTkFUVVJFQkFTRTY0"
                }},
                "public_key": {{
                    "kty": "OKP",
                    "crv": "Ed25519",
                    "x": "TFdOdk1qSW5PVEExT1RJM056ZzM="
                }}
            }}"#,
            Utc::now().to_rfc3339()
        )
    }

    #[test]
    fn test_valid_tpm_attestation() {
        let json = make_valid_payload_json();
        let validator = AttestationValidator::default();
        assert!(validator.validate(&json).is_ok());
    }

    #[test]
    fn test_invalid_version() {
        let json = make_valid_payload_json().replace("\"1.0\"", "\"2.0\"");
        let validator = AttestationValidator::default();
        let result = validator.validate(&json);
        assert!(matches!(result, Err(ValidationError::InvalidVersion(_))));
    }

    #[test]
    fn test_invalid_proposal_ref() {
        let json = make_valid_payload_json().replace("\"SEAI-P-001\"", "\"SEAI-P-999\"");
        let validator = AttestationValidator::default();
        let result = validator.validate(&json);
        assert!(matches!(result, Err(ValidationError::InvalidProposalRef(_))));
    }

    #[test]
    fn test_expired_timestamp() {
        let old_timestamp = "2020-01-01T00:00:00Z";
        let json = format!(
            r#"{{
                "seai_version": "1.0",
                "proposal_ref": "SEAI-P-001",
                "agent_id": "agent-001",
                "timestamp_utc": "{}",
                "hardware_provider": "TPM2.0",
                "attestation_quote": {{
                    "quote_data": "QkFTRTY0X0RBVEE=",
                    "signature": "U0lHTkFUVVJFQkFTRTY0"
                }},
                "public_key": {{
                    "kty": "OKP",
                    "crv": "Ed25519",
                    "x": "TFdOdk1qSW5PVEExT1RJM056ZzM="
                }}
            }}"#,
            old_timestamp
        );
        let validator = AttestationValidator::default();
        let result = validator.validate(&json);
        assert!(matches!(result, Err(ValidationError::TimestampExpired(_))));
    }

    #[test]
    fn test_malformed_json() {
        let json = "{ this is not valid json }";
        let validator = AttestationValidator::default();
        let result = validator.validate(json);
        assert!(matches!(result, Err(ValidationError::JsonError(_))));
    }

    #[test]
    fn test_unsupported_key_type() {
        let json = make_valid_payload_json()
            .replace("\"Ed25519\"", "\"RSA-4096\"");
        let validator = AttestationValidator::default();
        let result = validator.validate(&json);
        assert!(matches!(result, Err(ValidationError::UnsupportedKeyType(_, _))));
    }

    #[test]
    fn test_invalid_base64_signature() {
        let json = make_valid_payload_json()
            .replace("\"U0lHTkFUVVJFQkFTRTY0\"", "\"!!!not-base64!!!\"");
        let validator = AttestationValidator::default();
        let result = validator.validate(&json);
        assert!(matches!(result, Err(ValidationError::Base64Error(_))));
    }

    #[test]
    fn test_configurable_clock_drift() {
        // Use a 10-year drift to allow the old timestamp
        let old_timestamp = "2020-01-01T00:00:00Z";
        let json = format!(
            r#"{{
                "seai_version": "1.0",
                "proposal_ref": "SEAI-P-001",
                "agent_id": "agent-001",
                "timestamp_utc": "{}",
                "hardware_provider": "TPM2.0",
                "attestation_quote": {{
                    "quote_data": "QkFTRTY0X0RBVEE=",
                    "signature": "U0lHTkFUVVJFQkFTRTY0"
                }},
                "public_key": {{
                    "kty": "OKP",
                    "crv": "Ed25519",
                    "x": "TFdOdk1qSW5PVEExT1RJM056ZzM="
                }}
            }}"#,
            old_timestamp
        );
        let validator = AttestationValidator::new(315_532_800); // ~10 years
        let result = validator.validate(&json);
        assert!(result.is_ok());
    }
}