#!/usr/bin/env python3
"""
make_tables.py — builds Chapter 4 tables from blockchain_metrics.csv and verification_log.csv
Robust to mixed dtypes (casts numerics), and uses string aggregations to avoid FutureWarnings.
"""
from pathlib import Path
import sys
import pandas as pd
import numpy as np

OUT_DIR = Path(".")

def load_csv_safely(path):
    p = Path(path)
    if not p.exists():
        print(f"[WARN] Missing file: {p.resolve()}"); return None
    try:
        return pd.read_csv(p)
    except Exception as e:
        print(f"[ERROR] Failed to read {p}: {e}"); return None

def to_num(df, cols):
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

def main():
    metrics_df = load_csv_safely("blockchain_metrics.csv")
    vlog_df    = load_csv_safely("verification_log.csv")
    if metrics_df is None:
        print("[FATAL] Run main_with_adversary.py first."); sys.exit(1)

    # --- Normalize METRICS dtypes ---
    # valid -> bool
    if "valid" in metrics_df.columns and metrics_df["valid"].dtype != bool:
        metrics_df["valid"] = metrics_df["valid"].astype(str).str.lower().isin(["1","true","t","yes","y"])
    # numeric cols
    metrics_df = to_num(metrics_df, ["verify_time_sec", "block_size", "payload_bytes"])
    # (alg stays string)

    # --- Normalize VLOG dtypes ---
    if vlog_df is not None:
        vlog_df = to_num(vlog_df, ["tps", "payload_bytes", "nodes", "rounds"])
        # keep only rows with numeric tps for summary table
        if "tps" in vlog_df.columns:
            vlog_df = vlog_df[pd.notna(vlog_df["tps"])]

    # ------------------ Table 4.1 — summary by algorithm ------------------
    t41 = (
        metrics_df
        .groupby("alg", dropna=False)
        .agg(
            rows=("valid", "size"),
            valid_rate=("valid", "mean"),
            block_size_mean=("block_size", "mean"),
            verify_time_mean=("verify_time_sec", "mean"),
        )
        .reset_index()
    )
    t41["valid_rate"] = (t41["valid_rate"] * 100.0).round(2)
    t41.to_csv(OUT_DIR / "Table_4_1_summary_by_algorithm.csv", index=False)

    # ------------- Table 4.2 — verify-time distribution by algorithm -------------
    # Use string aggregations to avoid FutureWarnings
    t42 = (
        metrics_df
        .groupby("alg", dropna=False)["verify_time_sec"]
        .agg(median="median", p95=lambda s: np.percentile(s.dropna(), 95) if len(s.dropna()) else np.nan)
        .reset_index()
    )
    t42["median_ms"] = t42["median"] * 1000.0
    t42["p95_ms"]    = t42["p95"] * 1000.0
    t42 = t42.drop(columns=["median", "p95"])
    t42.to_csv(OUT_DIR / "Table_4_2_verify_time_by_algorithm.csv", index=False)

    # ----------------- Table 4.3 — block size by algorithm -----------------
    t43 = (
        metrics_df
        .groupby("alg", dropna=False)["block_size"]
        .agg(mean="mean", median="median")
        .reset_index()
    )
    t43.to_csv(OUT_DIR / "Table_4_3_block_size_by_algorithm.csv", index=False)

    # ----------------- Table 4.4 — TPS by payload (from vlog) --------------
    if vlog_df is not None and {"alg","payload_bytes","kind","tps"}.issubset(vlog_df.columns):
        s = vlog_df[vlog_df["kind"].astype(str).str.lower() == "summary"].copy()
        # ensure numeric
        s = to_num(s, ["tps", "payload_bytes"])
        s = s.dropna(subset=["tps"])
        if not s.empty:
            t44 = (
                s.groupby(["alg","payload_bytes"], dropna=False)["tps"]
                .agg(mean_tps="mean", median_tps="median", runs="size")
                .reset_index()
            )
            t44.to_csv(OUT_DIR / "Table_4_4_tps_by_payload.csv", index=False)
        else:
            print("[INFO] No numeric TPS rows found for Table_4_4.")
    else:
        print("[INFO] verification_log.csv missing required columns for Table_4_4 (alg, payload_bytes, kind, tps).")

    # ---------------- adversarial outcomes (optional) ----------------
    if vlog_df is not None and "kind" in vlog_df.columns:
        adv = vlog_df[vlog_df["kind"].astype(str).str.lower() == "adversarial"].copy()
        if not adv.empty and "details" in adv.columns:
            def parse_details(txt):
                d={}
                for part in str(txt).split(";"):
                    if "=" in part:
                        k,v = part.split("=",1)
                        try: v = int(v.strip())
                        except: v = v.strip()
                        d[k.strip()] = v
                return d
            parsed = adv["details"].apply(parse_details).apply(pd.Series)
            out = pd.concat([adv[["run_id","exp_tag","alg","payload_bytes"]].reset_index(drop=True), parsed], axis=1)
            out.to_csv(OUT_DIR / "adversarial_outcomes.csv", index=False)

    print("✅ Tables written (current folder).")

if __name__ == "__main__":
    main()
