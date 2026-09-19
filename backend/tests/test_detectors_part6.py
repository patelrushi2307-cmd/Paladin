from datetime import datetime, timezone
from app.detectors.dga import DgaDnsDetector
from app.detectors.encrypted import EncryptedTrafficDetector
from app.schemas.feature import FeatureVector
from app.system_contract import ACTIVE_PROBING, INLINE_MITIGATION, ONE_WAY_ONLY, PAYLOAD_DECRYPTION


def vector(values, scope="FLOW"):
    return FeatureVector(feature_id="f", flow_id="flow", timestamp=datetime.now(timezone.utc), scope=scope, source_type="test", values=values, availability={k: v is not None for k, v in values.items()})


def test_dga_and_tunnel_are_distinct_and_bounded():
    values = {"dns_query_entropy": 4.8, "dns_query_length": 55, "digit_ratio": .3, "character_diversity": .8, "label_count": 4, "subdomain_depth": 2, "ngram_score": None, "txt_record": True}
    result = DgaDnsDetector().detect(vector(values), {})[0]
    assert result.score <= 1
    assert result.subtype in {"DGA_LIKE", "DNS_TUNNEL_LIKE"}
    assert result.evidence["ngram_score"] is None


def test_dga_missing_dns_is_not_applicable():
    result = DgaDnsDetector().detect(vector({"protocol": "TCP"}), {})[0]
    assert result.applicability == "not_applicable"
    assert result.score == 0


def test_encrypted_metadata_only_and_payload_off():
    values = {"protocol": "TLS", "tls_metadata_available": True, "tls_version": "TLSv1.3", "tls_ja4": "ja4", "tls_sni_present": False, "packet_size_mean": 200, "packet_size_std": 250, "iat_cv": .8, "periodicity_score": .7, "flow_duration": 100, "bytes_total": 10000, "packets_total": 50}
    result = EncryptedTrafficDetector().detect(vector(values), {})[0]
    assert result.evidence["payload_decryption"] is False
    assert result.score > 0
    assert PAYLOAD_DECRYPTION is False


def test_encrypted_missing_metadata_is_not_applicable():
    result = EncryptedTrafficDetector().detect(vector({"protocol": "TCP"}), {})[0]
    assert result.applicability == "not_applicable"


def test_security_invariants_remain():
    assert ONE_WAY_ONLY is True
    assert PAYLOAD_DECRYPTION is False
    assert ACTIVE_PROBING is False
    assert INLINE_MITIGATION is False
