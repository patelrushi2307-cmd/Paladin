# Evaluation and Benchmarks

Available commands inspect local datasets, train a selected model, evaluate registered metadata, benchmark ingestion, benchmark detector throughput, and generate reports. Metrics are written only after an actual command runs; missing experiments are not filled with fabricated values.

Evaluation must keep capture/session/scenario groups separated across train, validation, and held-out test. Threshold tuning and calibration belong on validation data. Part 9 scaffolding records classification reports and confusion matrices from grouped model runs; calibration remains explicitly `NOT_CALIBRATED` until a held-out experiment is performed.

Time-to-detect and end-to-end p50/p95/p99 require a ground-truth scenario and runtime instrumentation. The current benchmark scripts report local processing throughput, latency, drops, and errors only.
