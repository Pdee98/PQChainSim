# plot.py — robust plotting with boolean coercion and guaranteed bars
import os
import pandas as pd
import matplotlib.pyplot as plt

CSV = "blockchain_metrics.csv"
if not os.path.exists(CSV):
    raise SystemExit("blockchain_metrics.csv not found. Run main.py first.")

df = pd.read_csv(CSV, engine="python", on_bad_lines="skip")

for col in ("alg","valid","index","block_size","verify_time_sec"):
    if col not in df.columns:
        raise SystemExit(f"CSV missing '{col}'. Delete CSVs and re-run main.py.")

def to_bool(x):
    s = str(x).strip().lower()
    return s in {"true","1","yes","y"}
df["valid"] = df["valid"].apply(to_bool)

def norm_alg(a):
    a = str(a).lower()
    if "sphincs" in a: return "SPHINCS-sim"
    if "xmss"    in a: return "XMSS-sim"
    if "lms"     in a: return "LMS-sim"
    return a
df["alg"] = df["alg"].apply(norm_alg)

# 1) Validity by algorithm (force all three)
expected = ["SPHINCS-sim", "XMSS-sim", "LMS-sim"]
valid = df.groupby("alg", as_index=False)["valid"].mean()
valid["valid_pct"] = (valid["valid"] * 100).round(2)
for alg in expected:
    if alg not in valid["alg"].values:
        valid.loc[len(valid)] = [alg, 0.0, 0.0]
valid = valid.set_index("alg").loc[expected].reset_index()

ax = valid.plot(x="alg", y="valid_pct", kind="bar", legend=False)
ax.set_ylabel("Valid blocks (%)"); ax.set_title("Validity by Algorithm")
plt.grid(True, axis="y"); plt.ylim(0, 100); plt.tight_layout()
plt.savefig("plot_validity.png"); plt.clf()

# 2) Block size over time
for alg, g in df.groupby("alg"):
    g = g.sort_values("index")
    plt.plot(g["index"], g["block_size"], marker='o', linestyle='-', label=alg)
plt.title("Block Size over Time (per algorithm)")
plt.xlabel("Block Index"); plt.ylabel("Block Size (chars)")
plt.grid(True); plt.legend(); plt.tight_layout()
plt.savefig("plot_block_size_by_alg.png"); plt.clf()

# 3) Verify time distribution
df.boxplot(column="verify_time_sec", by="alg")
plt.title("Verify Time Distribution by Algorithm"); plt.suptitle("")
plt.xlabel("Algorithm"); plt.ylabel("Verify time (sec)")
plt.grid(True); plt.tight_layout()
plt.savefig("plot_verify_time_box.png"); plt.clf()

print("✅ Saved: plot_validity.png, plot_block_size_by_alg.png, plot_verify_time_box.png")
print("\nValidity summary (%):")
print(valid.set_index("alg")["valid_pct"])
