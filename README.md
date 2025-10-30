**PQChainSim: Post-Quantum Hash-Based Blockchain Simulation Prototype**

PQChainSim is a Python-based simulation framework for evaluating hash-based signature (HBS) schemes in blockchain consensus.
It experimentally compares SPHINCS+ (stateless), XMSS (stateful), and LMS (stateful) by measuring throughput (TPS), verification latency, block size, and validity ratio under both normal and adversarial (tamper/replay) conditions.

⚠️ **Note:** PQChainSim is a systems-level simulation, not a real cryptographic or peer-to-peer blockchain implementation.
It provides an analytical baseline for post-quantum blockchain performance evaluation.

**🚀 Quick Start (Windows / PyCharm)**

Open this folder in **PyCharm** (or VS Code) and create a virtual environment when prompted.

Install dependencies:

pip install numpy pandas matplotlib


Run an experiment interactively:

python main.py


Generate plots and tables:

python plot.py

**📂 Files and Structure**

main.py — interactive experiment runner (prompts for rounds, nodes, payload, trials, and tags).

consensus.py — simple consensus engine implementing round-robin validation with propagation delay.

node.py — defines blockchain nodes with signature generation, verification, and state handling (for XMSS/LMS).

hbs.py — pure-Python simulators for SPHINCS+, XMSS, and LMS with consistent sign/verify logic.

metrics.py — logs performance data (TPS, latency, block size) to blockchain_metrics.csv.

adversary.py — simulates tampering and replay attacks for adversarial testing.

block.py — lightweight data container for block structure (payload, signature, timestamp).

plot.py — generates performance plots: validity ratio, block size, and verification latency.

**📊 Typical Outputs**

blockchain_metrics.csv — per-block performance metrics (TPS, latency, block size, validity ratio).

verification_log.csv — adversarial test results (replay/tamper rejection).

plot_validity.png — valid vs. tampered/replayed transactions.

plot_block_size_by_alg.png — average block size comparison across algorithms.

plot_verify_time_box.png — latency distribution (median and p95).

All files are automatically generated after each simulation run in the project directory.

**🧠 Research Context**

PQChainSim was developed exclusively for this study to evaluate post-quantum blockchain consensus.
It serves as an open, reproducible experimental platform that enables comparative analysis of stateful (XMSS, LMS) and stateless (SPHINCS+) hash-based signatures.
The generated metrics and figures align with standard performance indicators used in peer-reviewed cryptographic and distributed-ledger research.

**📜 Citation**

If you use or extend PQChainSim, please cite:

Derrick et al, “Empirical Evaluation of Post-Quantum Hash-Based Signature Integration in Blockchain Consensus Using PQChainSim,” 2025.

**⚖️ License**

Released under the Apache License 2.0 — free for research, academic, and educational use.
