PQChainSim: Post-Quantum Hash-Based Blockchain Simulation Prototype

PQChainSim is a Python-based simulation framework designed to evaluate hash-based signature (HBS) schemes in blockchain consensus.
It experimentally compares SPHINCS+ (stateless), XMSS (stateful), and LMS (stateful) by measuring key performance metrics—throughput (TPS), verification latency, block size, and validity ratio—under both normal and adversarial (tamper/replay) conditions.

⚠️ Note: PQChainSim is a systems-level simulation tool, not a real cryptographic or peer-to-peer blockchain implementation.
It provides an analytical baseline for post-quantum blockchain performance evaluation.

🚀 Quick Start (Windows / PyCharm)

Open the project folder in PyCharm (or VS Code).

Create and activate a virtual environment when prompted.

Install dependencies:

pip install numpy pandas matplotlib


Run the main experiment:

python main.py


Generate summary plots and tables:

python plot.py

📂 Project Structure
File	Description
main.py	Interactive experiment runner that prompts for parameters (rounds, nodes, payload size, trials, and tags).
consensus.py	Simplified consensus engine implementing round-robin validation with simulated propagation delay.
node.py	Defines blockchain nodes, signature generation, and verification logic, enforcing state management for XMSS/LMS.
hbs.py	Pure-Python simulators for SPHINCS+, XMSS, and LMS providing consistent sign/verify interfaces.
metrics.py	Logs throughput, latency, and block size metrics into blockchain_metrics.csv.
adversary.py	Implements tampering and replay scenarios to test adversarial resilience.
block.py	Minimal data container for block information (payload, signature, timestamp).
plot.py	Generates analytical plots for validity ratio, block size, and verification latency.
📊 Output Artifacts
Output	Description
blockchain_metrics.csv	Per-block performance logs (TPS, latency, block size, validity).
verification_log.csv	Results of adversarial replay/tampering tests.
plot_validity.png	Visualization of verified vs. rejected transactions.
plot_block_size_by_alg.png	Comparison of block size across XMSS, LMS, and SPHINCS+.
plot_verify_time_box.png	Verification latency distribution (p50/p95).

All outputs are automatically generated in the working directory after each simulation run.

🧠 Research Context

PQChainSim was developed exclusively for academic experimentation on post-quantum blockchain security.
It serves as an open, reproducible platform for exploring the trade-offs between stateful and stateless HBS algorithms within blockchain consensus mechanisms.
Its structured logs and figures align with metrics used in performance sections of peer-reviewed studies.

📜 Citation

If you use or adapt PQChainSim, please cite:

Derrick et al, “Empirical Evaluation of Post-Quantum Hash-Based Signature Integration in Blockchain Consensus Using PQChainSim,” 2025.

⚖️ License

Released under the Apache 2.0 License — free for research and educational use.
