#!/usr/bin/env python3
"""
plot_figures.py — generates paper figures (matplotlib, one plot per figure, no color themes)
"""
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def load_csv(path):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Missing {path}. Run main_with_adversary.py first.")
    return pd.read_csv(p)

def fig1_tps_by_payload(vlog):
    # keep only summary rows
    s = vlog[vlog['kind'].astype(str).str.lower() == 'summary'].copy()

    # cast to numeric (handles strings like "89241.892063")
    s['tps'] = pd.to_numeric(s['tps'], errors='coerce')
    s['payload_bytes'] = pd.to_numeric(s['payload_bytes'], errors='coerce')

    # drop rows where tps is NaN after coercion
    s = s.dropna(subset=['tps', 'payload_bytes'])

    # median TPS per alg & payload
    piv = s.groupby(['alg', 'payload_bytes'])['tps'].median().reset_index()

    plt.figure()
    for alg in piv['alg'].unique():
        sub = piv[piv['alg'] == alg]
        plt.plot(sub['payload_bytes'], sub['tps'], marker='o', label=alg)
    plt.xlabel("Payload (bytes)")
    plt.ylabel("TPS (verification proxy)")
    plt.title("Figure 1 – TPS by Payload")
    plt.legend()
    plt.tight_layout()
    plt.savefig("Figure_1_TPS_by_Payload.png", dpi=200)
    plt.close()



def fig2_latency_box(metrics):
    plt.figure()
    order = list(metrics['alg'].unique())
    data_ms = [metrics[metrics['alg']==alg]['verify_time_sec']*1000.0 for alg in order]
    plt.boxplot(data_ms, labels=order)
    plt.ylabel("Verification time (ms)")
    plt.title("Figure 2 – Verification Latency by Algorithm")
    plt.tight_layout()
    plt.savefig("Figure_2_Latency_Box_by_Alg.png", dpi=200)
    plt.close()

def fig3_block_size(metrics):
    piv = metrics.groupby('alg')['block_size'].median().reset_index()
    plt.figure()
    plt.bar(piv['alg'], piv['block_size'])
    plt.ylabel("Block size (bytes, median)")
    plt.title("Figure 3 – Block Size by Algorithm")
    plt.tight_layout()
    plt.savefig("Figure_3_Block_Size_by_Alg.png", dpi=200)
    plt.close()

def fig4_validity(metrics):
    piv = metrics.groupby('alg')['valid'].mean().reset_index()
    piv['valid_pct'] = piv['valid']*100.0
    plt.figure()
    plt.bar(piv['alg'], piv['valid_pct'])
    plt.ylabel("Validity (%)")
    plt.title("Figure 4 – Validity by Algorithm")
    plt.ylim(0, 105)
    plt.tight_layout()
    plt.savefig("Figure_4_Validity_by_Alg.png", dpi=200)
    plt.close()

def main():
    metrics = load_csv("blockchain_metrics.csv")
    vlog = load_csv("verification_log.csv")

    # normalize validity to bool if needed
    if 'valid' in metrics.columns and metrics['valid'].dtype != bool:
        metrics['valid'] = metrics['valid'].astype(str).str.lower().isin(['true','1','t','yes','y'])

    # also coerce numeric columns used in other figs
    if 'verify_time_sec' in metrics.columns:
        metrics['verify_time_sec'] = pd.to_numeric(metrics['verify_time_sec'], errors='coerce')
    if 'block_size' in metrics.columns:
        metrics['block_size'] = pd.to_numeric(metrics['block_size'], errors='coerce')

    fig1_tps_by_payload(vlog)
    fig2_latency_box(metrics)
    fig3_block_size(metrics)
    fig4_validity(metrics)
    print("Figures saved: Figure_1..Figure_4.")

if __name__ == "__main__":
    main()
