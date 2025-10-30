# ch4_make_tables_and_plots.py
# Generates Chapter 4 tables and figures from blockchain_metrics.csv
# - Table_4_1_summary_by_algorithm.csv
# - Table_4_2_summary_by_payload.csv
# - Table_4_3_alg_by_payload.csv
# - Table_4_4_tps_by_payload.csv
# - Table_4_5_tps_by_alg_payload.csv
# - Figure_4_TPS_by_Payload.png
# - Figure_4_Latency_Bars_by_Alg.png

import pandas as pd, numpy as np
import matplotlib.pyplot as plt

# -----------------------
# Load & basic cleaning
# -----------------------
df = pd.read_csv("blockchain_metrics.csv", engine="python", on_bad_lines="skip")

# Coerce validity to boolean
df["valid_b"] = df["valid"].astype(str).str.lower().isin({"true", "1", "yes", "y"})

# Ensure presence of exp_tag (older runs may not have it)
if "exp_tag" not in df.columns:
    df["exp_tag"] = "default"

# -----------------------
# Table 4.1: Summary by algorithm
# -----------------------
t41 = df.groupby("alg", as_index=True).agg(
    avg_block_size=('block_size', 'mean'),
    median_latency_ms=('verify_time_sec', lambda x: np.median(x) * 1000),
    p95_latency_ms=('verify_time_sec', lambda x: np.percentile(x, 95) * 1000),
    validity_ratio=('valid_b', lambda x: x.mean() * 100)
).round(3)
t41.to_csv("Table_4_1_summary_by_algorithm.csv")

# -----------------------
# Table 4.2: Summary by payload
# -----------------------
t42 = df.groupby("payload_bytes", as_index=True).agg(
    avg_block_size=('block_size', 'mean'),
    median_latency_ms=('verify_time_sec', lambda x: np.median(x) * 1000),
    p95_latency_ms=('verify_time_sec', lambda x: np.percentile(x, 95) * 1000),
    validity_ratio=('valid_b', lambda x: x.mean() * 100)
).round(3)
t42.to_csv("Table_4_2_summary_by_payload.csv")

# -----------------------
# Table 4.3: Algorithm × payload interaction
# -----------------------
t43 = df.groupby(["alg", "payload_bytes"], as_index=True).agg(
    avg_block_size=('block_size', 'mean'),
    median_latency_ms=('verify_time_sec', lambda x: np.median(x) * 1000),
    p95_latency_ms=('verify_time_sec', lambda x: np.percentile(x, 95) * 1000),
    validity_ratio=('valid_b', lambda x: x.mean() * 100)
).round(3)
t43.to_csv("Table_4_3_alg_by_payload.csv")

# -----------------------
# TPS estimation (FutureWarning-safe; no .apply on groups)
# -----------------------
# Per (alg, payload, exp_tag), compute min/max timestamps and block count
g = df.groupby(["alg", "payload_bytes", "exp_tag"], as_index=False).agg(
    start=("timestamp", "min"),
    end=("timestamp", "max"),
    blocks=("index", "count")
)
g["duration"] = (g["end"] - g["start"]).clip(lower=1e-9)
tps_by = g.assign(tps=g["blocks"] / g["duration"])[["alg", "payload_bytes", "exp_tag", "tps"]]

# Table 4.4: TPS by payload (summary across alg/tags)
tps_payload = tps_by.groupby("payload_bytes")["tps"].agg(["mean", "median", "std"]).round(3)
tps_payload.to_csv("Table_4_4_tps_by_payload.csv")

# Table 4.5: TPS by algorithm × payload
tps_alg_payload = tps_by.groupby(["alg", "payload_bytes"])["tps"].agg(["mean", "median", "std"]).round(3)
tps_alg_payload.to_csv("Table_4_5_tps_by_alg_payload.csv")

# -----------------------
# Figures
# -----------------------
# Figure: TPS vs Payload
plt.figure(figsize=(8, 5))
tps_payload["mean"].plot(kind="bar")
plt.ylabel("Average TPS")
plt.xlabel("Payload (bytes)")
plt.title("Throughput (Average TPS) by Payload")
plt.tight_layout()
plt.savefig("Figure_4_TPS_by_Payload.png", dpi=300)

# Figure: Latency bars per algorithm (median & p95) using Table 4.1
lat = t41[["median_latency_ms", "p95_latency_ms"]].copy()
plt.figure(figsize=(9, 5))
lat.plot(kind="bar")
plt.ylabel("Verification Time (ms)")
plt.xlabel("Algorithm")
plt.title("Verification Latency by Algorithm (Median & p95)")
plt.legend(["Median (p50)", "p95"])
plt.tight_layout()
plt.savefig("Figure_4_Latency_Bars_by_Alg.png", dpi=300)

print("\nSaved:")
print(" - Table_4_1_summary_by_algorithm.csv")
print(" - Table_4_2_summary_by_payload.csv")
print(" - Table_4_3_alg_by_payload.csv")
print(" - Table_4_4_tps_by_payload.csv")
print(" - Table_4_5_tps_by_alg_payload.csv")
print(" - Figure_4_TPS_by_Payload.png")
print(" - Figure_4_Latency_Bars_by_Alg.png\n")
