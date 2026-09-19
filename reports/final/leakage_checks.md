# Leakage Checks

Dataset inspection reports stable duplicate hashes and scenario groups. The training helper uses `GroupShuffleSplit` on the scenario/group field rather than random row splitting. The controlled runtime fixtures keep ground truth outside FlowEvent input.

A full same-session/family leakage audit requires a larger labeled training corpus and is therefore PARTIAL. No held-out test metric is claimed.
