# Training Lifecycle

Training accepts local JSONL/CSV through `DatasetAdapter` implementations. Dataset manifests record provenance and licensing as known; unknown fields remain unknown. `dataset_inspect.py`, `dataset_prepare.py`, and `dataset_validate.py` report missing values, labels, duplicates, invalid values, class distribution, and groups.

Prepared records map to explicit ordered feature lists in `backend/app/ml/training.py`. Models use a grouped scenario split rather than random rows to reduce session leakage. The baseline model is a seeded RandomForest with median imputation and balanced classes. Metadata records seed, split strategy, feature schema, metrics, confusion matrix, artifact, and `NOT_CALIBRATED` status. Model artifacts are optional; statistical detectors remain the runtime fallback.

No external dataset is required, and no dataset license is invented. TLS/QUIC training features are metadata-only.
