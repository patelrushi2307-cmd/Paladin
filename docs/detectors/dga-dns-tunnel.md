# DGA and DNS Tunnelling Detector

`DgaDnsDetector` distinguishes two related but separate indicators. DGA-like scoring combines DNS entropy, length, digit ratio, character diversity, and label structure. DNS tunnel-like scoring combines long/high-entropy queries, subdomain depth, TXT metadata, and unique-query behavior when available. High entropy or length alone is insufficient. Missing DNS metadata returns `not_applicable`, and unavailable n-gram scores remain null. No resolver or external reputation lookup is used.
