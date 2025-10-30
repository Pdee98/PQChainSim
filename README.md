Post-Quantum Chain Simulator (PQChainSim)
This project is a simulation prototype for evaluating hash‑based signatures (HBS) in a blockchain consensus context. It compares SPHINCS+ (stateless), XMSS (stateful), and LMS (stateful) and measures throughput (TPS), verification latency, block size, and validity under simple adversarial checks (tamper/replay).

Note: This is a systems-level simulation (not real cryptography nor a P2P network). 

Quick Start (Windows/PyCharm friendly)
Open this folder in PyCharm and create a virtual environment when prompted.
Install deps:
pip install pandas matplotlib
Run interactive experiments:
python main.py
Generate figures:
python plot.py

Files
main.py — interactive experiment runner (prompts for rounds/nodes/payload/trials/tag).
consensus.py — simple round‑robin consensus with simulated propagation delay.
node.py — node wrapper using HBS simulators; enforces index anti‑replay for stateful schemes.
hbs.py — pure‑Python simulators for SPHINCS/XMSS/LMS with consistent sign/verify behavior.
metrics.py — logs per‑block metrics to blockchain_metrics.csv and prints TPS/latency stats.
adversary.py — optional tamper/replay helpers used in checks.
plot.py — robust plots for validity, block size, and verification latency.
block.py — simple dataclass‑like container for block fields.

Typical Outputs
blockchain_metrics.csv, verification_log.csv
plot_validity.png, plot_block_size_by_alg.png, plot_verify_time_box.png
