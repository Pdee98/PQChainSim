#!/usr/bin/env python3
"""
metrics.py
- Verifies each produced block with the provided node.
- Measures per-block verification time (seconds), computes p50/p95.
- Writes per-block rows to blockchain_metrics.csv and a per-run summary to verification_log.csv (kind=summary) including 'tps'.
"""
from __future__ import annotations
import time
from pathlib import Path
import statistics as stats

def _ensure(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)

def log_metrics(blocks, node, alg: str, nodes: int, rounds: int, payload_bytes: int, exp_tag: str, run_id: str):
    out_path = Path("blockchain_metrics.csv")
    _ensure(out_path)
    need_header = not out_path.exists()

    verify_times = []
    valid_count = 0

    with out_path.open("a", encoding="utf-8") as f:
        if need_header:
            f.write("exp_tag,run_id,alg,index,timestamp,producer,nodes,rounds,payload_bytes,block_size,previous_hash,block_hash,verify_time_sec,valid\n")

        for b in blocks:
            t0 = time.perf_counter()
            ok = node.verify_block(b)
            dt = time.perf_counter() - t0  # seconds
            verify_times.append(dt)
            if ok:
                valid_count += 1

            # approximate block size (bytes)
            block_size = len(str(b.get("data", ""))) + len(b.get("signature", b"")) + len(b.get("public_key", b"")) + 64

            f.write(",".join([
                exp_tag,
                run_id,
                alg,
                str(b.get("index", -1)),
                f"{b.get('timestamp', 0.0):.6f}",
                b.get("producer", "N0"),
                str(nodes),
                str(rounds),
                str(payload_bytes),
                str(block_size),
                b.get("previous_hash", ""),
                b.get("block_hash", ""),
                f"{dt:.9f}",
                "True" if ok else "False"
            ]) + "\n")

    # aggregates
    p50 = stats.median(verify_times) if verify_times else 0.0
    p95 = stats.quantiles(verify_times, n=100)[94] if len(verify_times) >= 100 else (max(verify_times) if verify_times else 0.0)
    total_verify_time = sum(verify_times) if verify_times else 1e-9
    tps = rounds / total_verify_time  # verification-throughput proxy
    valid_ratio = valid_count / max(1, rounds)

    vlog = Path("verification_log.csv")
    need_header = not vlog.exists()
    with vlog.open("a", encoding="utf-8") as vf:
        if need_header:
            vf.write("timestamp,run_id,exp_tag,alg,payload_bytes,nodes,rounds,kind,tps,p50_ms,p95_ms,valid_ratio\n")
        vf.write(",".join([
            f"{time.time():.3f}",
            run_id,
            exp_tag,
            alg,
            str(payload_bytes),
            str(nodes),
            str(rounds),
            "summary",
            f"{tps:.6f}",
            f"{p50*1000.0:.6f}",
            f"{p95*1000.0:.6f}",
            f"{valid_ratio:.6f}",
        ]) + "\n")

    return {"tps": tps, "p50_ms": p50 * 1000.0, "p95_ms": p95 * 1000.0, "valid_ratio": valid_ratio}
