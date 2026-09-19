# Exfiltration Detector

`ExfiltrationDetector` requires outbound direction evidence. It combines bounded outbound volume, outbound/inbound asymmetry, rate, duration, and baseline deviation. Unknown or inbound direction returns `insufficient_direction_evidence`; zero inbound is not converted into infinity. A score indicates abnormal outbound transfer behavior, not confirmed exfiltration. No payload is inspected.
