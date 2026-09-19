"""Create a small synthetic PCAP fixture offline; never sends packets."""
from datetime import datetime, timezone
from pathlib import Path
from scapy.layers.inet import IP, TCP, UDP
from scapy.utils import PcapWriter

output = Path(__file__).parents[1] / "data" / "raw" / "synthetic_fixture.pcap"
output.parent.mkdir(parents=True, exist_ok=True)
base = datetime(2026, 9, 19, 12, 0, tzinfo=timezone.utc).timestamp()
packets = []
for index in range(12):
    packet = IP(src=f"10.20.0.{index + 1}", dst="10.20.1.5") / TCP(sport=40000 + index, dport=443, flags="S") / (b"x" * (40 + index * 10))
    packet.time = base + index * 0.01
    packets.append(packet)
for index in range(6):
    packet = IP(src="10.20.2.5", dst=f"10.20.3.{index + 1}") / UDP(sport=50000 + index, dport=53) / (b"d" * (30 + index * 20))
    packet.time = base + 2 + index * 0.02
    packets.append(packet)
for index in range(4):
    packet = IP(src="10.20.4.5", dst="198.51.100.10") / TCP(sport=51000, dport=443, flags="PA") / (b"e" * (400 + index * 100))
    packet.time = base + 4 + index * 0.5
    packets.append(packet)
with PcapWriter(str(output), sync=True) as writer:
    for packet in packets:
        writer.write(packet)
print(f"Created synthetic PCAP fixture: {output} ({len(packets)} packets)")

# Also create an extended synthetic PCAP benchmark fixture (500 packets) for latency percentile analysis
bench_output = Path(__file__).parents[1] / "data" / "raw" / "synthetic_benchmark.pcap"
bench_packets = []
# 200 TCP SYN/ACK/PA packets across 20 distinct flow pairs
for i in range(200):
    flow_idx = i % 20
    flags = "S" if i < 20 else ("PA" if i % 2 == 0 else "A")
    payload_len = 40 + (i % 15) * 64
    pkt = IP(src=f"10.30.{flow_idx // 10}.{flow_idx % 10 + 1}", dst="10.30.5.10") / TCP(sport=30000 + flow_idx, dport=443 if flow_idx % 2 == 0 else 80, flags=flags) / (b"p" * payload_len)
    pkt.time = base + i * 0.005
    bench_packets.append(pkt)

# 150 UDP packets (DNS queries and varied payloads)
for i in range(150):
    flow_idx = i % 15
    pkt = IP(src=f"10.30.2.{flow_idx + 1}", dst="10.30.2.53") / UDP(sport=40000 + flow_idx, dport=53) / (b"q" * (48 + (i % 10) * 32))
    pkt.time = base + 2.0 + i * 0.008
    bench_packets.append(pkt)

# 150 Multi-source burst packets (testing flow fanout and exfil volumes)
for i in range(150):
    pkt = IP(src=f"10.30.9.{i % 50 + 1}", dst="198.51.100.50") / TCP(sport=50000 + (i % 10), dport=8443, flags="PA") / (b"z" * (128 + (i % 8) * 128))
    pkt.time = base + 4.0 + i * 0.01
    bench_packets.append(pkt)

with PcapWriter(str(bench_output), sync=True) as writer:
    for packet in bench_packets:
        writer.write(packet)
print(f"Created synthetic benchmark PCAP fixture: {bench_output} ({len(bench_packets)} packets)")

