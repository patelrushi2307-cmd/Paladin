"""Create small offline labelled JSONL fixtures for the final demo.
These are controlled observation records, not packets and never transmitted.
"""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path

ROOT = Path(__file__).parents[1] / "data" / "scenarios"
RAW = Path(__file__).parents[1] / "data" / "raw" / "scenarios"
BASE = datetime(2026, 9, 19, 12, 0, tzinfo=timezone.utc)

def flow(event_id, timestamp, src, dst, *, packets=10, bytes_total=1000, protocol="TCP", dst_port=443, direction="unknown", label="BENIGN", **extra):
    return {"event_id": event_id, "timestamp": timestamp.isoformat().replace("+00:00", "Z"), "src_ip": src, "dst_ip": dst, "src_port": 40000, "dst_port": dst_port, "protocol": protocol, "packets": packets, "bytes": bytes_total, "duration": .5, "direction": direction, "source_type": "jsonl", **extra}

def write(name, records, truth):
    folder = ROOT / name; folder.mkdir(parents=True, exist_ok=True); path = RAW / f"{name}.jsonl"; path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8")
    (folder / "ground_truth.json").write_text(json.dumps({"scenario_id": name, "events": truth}, indent=2), encoding="utf-8")
    (folder / "manifest.yaml").write_text(f"scenario_id: {name}\nsources: [raw/scenarios/{name}.jsonl]\nlabels: {[item['threat_class'] for item in truth]}\nnotes: Controlled offline JSONL observations; ground truth is evaluation metadata only.\n", encoding="utf-8")

normal = [flow(f"normal-{i}", BASE + timedelta(seconds=i*0.8 + (0.4 if i % 2 else 0.1)), f"10.0.0.{10+i}", f"10.0.0.{20+i}", packets=14+i*4, bytes_total=1400+i*350, label="BENIGN") for i in range(5)]
ddos = [flow(f"ddos-{i}", BASE + timedelta(seconds=i), f"10.0.1.{i+1}", "10.0.2.5", packets=5000, bytes_total=500000, dst_port=80, tcp_flags="S", label="DDOS") for i in range(8)]
recon = [flow(f"recon-{i}", BASE + timedelta(seconds=i), "10.0.3.5", f"10.0.4.{i+1}", packets=2, bytes_total=120, dst_port=1000+i, tcp_flags="S", label="RECON") for i in range(8)]
c2 = [flow(f"c2-{i}", BASE + timedelta(seconds=i), "10.0.5.5", "198.51.100.9", packets=3, bytes_total=180, dst_port=443, label="C2_BEACON", tls_version="TLSv1.3", tls_sni="beacon.example.test") for i in range(6)]
exfil = [flow("exfil-0", BASE, "10.0.6.5", "203.0.113.9", packets=10000, bytes_total=50000000, dst_port=443, direction="outbound", label="DATA_EXFILTRATION", duration=120)]
dga = [flow("dga-0", BASE, "10.0.7.5", "10.0.7.53", packets=1, bytes_total=200, protocol="UDP", dst_port=53, label="DGA_DNS_TUNNEL", dns_query="x8j29dk29q8s1m7.example.test", dns_record_type="A")]
tunnel = [flow(f"tunnel-{i}", BASE + timedelta(seconds=i), "10.0.8.5", "10.0.8.53", packets=1, bytes_total=400, protocol="UDP", dst_port=53, label="DGA_DNS_TUNNEL", dns_query=f"longencodedpayload{i}x8j29dk29q8s1m7.example.test", dns_record_type="TXT") for i in range(6)]
encrypted = [flow("encrypted-0", BASE, "10.0.9.5", "198.51.100.20", packets=100, bytes_total=30000, dst_port=443, label="ENCRYPTED_MALWARE", tls_version="TLSv1.3", tls_ja4="t13d1516h2", alpn="h2", packet_size_summary={"min": 40, "max": 1400, "mean": 220, "std": 260})]
def shifted(records, offset_seconds):
    out = []
    for r in records:
        c = dict(r)
        orig_t = datetime.fromisoformat(r["timestamp"].replace("Z", "+00:00"))
        new_t = orig_t + timedelta(seconds=offset_seconds)
        c["timestamp"] = new_t.isoformat().replace("+00:00", "Z")
        out.append(c)
    return out

for name, records, threat in [("01_normal", normal, "BENIGN"), ("02_ddos", ddos, "DDOS"), ("03_recon", recon, "RECON"), ("04_c2", c2, "C2_BEACON"), ("05_exfil", exfil, "DATA_EXFILTRATION"), ("06_dga", dga, "DGA_DNS_TUNNEL"), ("07_dns_tunnel", tunnel, "DGA_DNS_TUNNEL"), ("08_encrypted", encrypted, "ENCRYPTED_MALWARE")]:
    write(name, records, [{"start_time": records[0]["timestamp"], "end_time": records[-1]["timestamp"], "threat_class": threat, "subtype": None, "source": records[0]["src_ip"], "destination": records[0]["dst_ip"], "notes": "Evaluation metadata only"}])

mixed_phases = [
    (normal, 0, "BENIGN"),
    (ddos, 10, "DDOS"),
    (recon, 20, "RECON"),
    (c2, 30, "C2_BEACON"),
    (exfil, 40, "DATA_EXFILTRATION"),
    (dga, 50, "DGA_DNS_TUNNEL"),
    (tunnel, 52, "DGA_DNS_TUNNEL"),
    (encrypted, 60, "ENCRYPTED_MALWARE"),
]
mixed_records = []
mixed_truth = []
for p_records, offset, threat in mixed_phases:
    shifted_recs = shifted(p_records, offset)
    mixed_records.extend(shifted_recs)
    mixed_truth.append({
        "start_time": shifted_recs[0]["timestamp"],
        "end_time": shifted_recs[-1]["timestamp"],
        "threat_class": threat,
        "subtype": None,
        "source": shifted_recs[0]["src_ip"],
        "destination": shifted_recs[0]["dst_ip"],
        "flow_count": len(shifted_recs),
        "notes": f"Phase {threat} offline observation window"
    })

write("09_mixed_demo", mixed_records, mixed_truth)
print(f"Created 9 offline scenario inputs under {RAW}")
