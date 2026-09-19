# Feature Catalog

Feature engineering is an observation layer. It uses only normalized `FlowEvent` fields and does not resolve DNS, decrypt TLS/QUIC, probe endpoints, or transmit traffic. Missing inputs remain `null` and are marked `false` in `FeatureVector.availability`.

| Feature | Group | Type | Formula / method | Scope | Availability | Future consumers |
|---|---|---|---|---|---|---|
| `packets_total` | traffic | int | Sum of observed packets | window | Always for valid flows | DDoS, exfil |
| `bytes_total` | traffic | int | Sum of observed bytes | window | Always for valid flows | DDoS, exfil |
| `packets_per_sec` | traffic | float | packets / event-time window seconds | window | Event timestamps | DDoS |
| `bytes_per_sec` | traffic | float | bytes / event-time window seconds | window | Event timestamps | DDoS, exfil |
| `flows_per_sec` | traffic | float | flow count / window seconds | window | Event timestamps | DDoS, recon |
| `flow_duration` | flow | float | `last_seen - first_seen` from source | flow | Source provides duration | C2, exfil |
| `syn_ratio`, `ack_ratio`, `rst_ratio`, `fin_ratio` | flow | float | Flag count / TCP flow count | window | TCP flags present | DDoS |
| `unique_src_count` | diversity | int | Count of source IP values in window | window | Valid source values | DDoS |
| `unique_dst_hosts` | diversity | int | Count of destination IP values | source/window | Valid destination values | recon |
| `unique_dst_ports` | diversity | int | Count of destination ports | source/window | Ports present | recon |
| `source_ip_entropy` | diversity | float | $-\sum p(x)\log_2 p(x)$ | window | Source values present | DDoS |
| `destination_concentration` | diversity | float | largest destination byte share / total bytes | window | Positive bytes | DDoS |
| `iat_mean`, `iat_std`, `iat_cv` | temporal | float | Statistics over sorted event-time deltas | window | At least two timestamps | C2 |
| `periodicity_score` | temporal | float | `1 / (1 + CV)`, bounded 0-1 | window | At least two intervals | C2 |
| `dns_query_length` | DNS | int | Length of normalized query | flow | Valid passive DNS metadata | DGA/tunnel |
| `dns_query_entropy` | DNS | float | Character entropy of query labels | flow | Valid passive DNS metadata | DGA/tunnel |
| `digit_ratio`, `character_diversity`, `label_count` | DNS | float/int | Character and label statistics | flow | Valid passive DNS metadata | DGA/tunnel |
| `ngram_score` | DNS | float | Reserved interface; no model in Part 3 | flow | Unavailable until model exists | DGA/tunnel |
| `tls_metadata_available` | TLS | bool | Presence of observed TLS metadata | flow/window | TLS fields supplied | encrypted traffic |
| `tls_ja3`, `tls_ja3s`, `tls_ja4`, `tls_sni_present`, `alpn` | TLS | string/bool | Passively copied metadata | flow | Source supplies field | encrypted traffic |
| `packet_size_mean/std/min/max/median` | packet shape | float | Summary over bounded packet-size metadata | flow/window | Source supplies summaries | encrypted traffic |
| `fanout_hosts`, `fanout_ports` | recon | int | Distinct destinations/ports | source/window | Values present | recon |
| `scan_velocity` | recon | float | `(unique hosts + unique ports) / seconds` | source/window | Event timestamps | recon |
| `outbound_bytes`, `inbound_bytes` | direction | int | Sum using configured/event direction | window | Direction known | exfil |
| `outbound_inbound_ratio` | direction | float | outbound bytes / inbound bytes | window | Both positive | exfil |

The registry in `backend/app/features/registry.py` is the extension point for additional definitions. Features are raw/derived values; scaling and categorical encoding belong in a future model preprocessing layer.
