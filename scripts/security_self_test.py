"""Offline security invariant self-test. Exits nonzero on failure."""
from pathlib import Path
import re, sys
sys.path.insert(0, str(Path(__file__).parents[1] / "backend"))
from app.system_contract import ACTIVE_PROBING, INLINE_MITIGATION, ONE_WAY_ONLY, PAYLOAD_DECRYPTION

checks = {"receive_only": ONE_WAY_ONLY is True, "return_path": ONE_WAY_ONLY is True, "active_probing": ACTIVE_PROBING is False, "payload_decryption": PAYLOAD_DECRYPTION is False, "inline_mitigation": INLINE_MITIGATION is False}
source = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in (Path(__file__).parents[1] / "backend" / "app").rglob("*.py"))
for name, pattern in {"packet_transmission": r"(?<!json)sendp?\s*\(", "live_probe": r"\bsr1?\s*\(|\bsrp\s*\(|\bsniff\s*\(", "external_dns": r"gethostbyname|getaddrinfo|dns\.resolver"}.items(): checks[name] = re.search(pattern, source) is None
for name, passed in checks.items(): print(f"{name}: {'PASS' if passed else 'FAIL'}")
sys.exit(0 if all(checks.values()) else 1)
