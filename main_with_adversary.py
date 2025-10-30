#!/usr/bin/env python3
"""
main_with_adversary.py
Defaults chosen to match paper:
- NODES = 8
- ROUNDS = 200  (paper range 100–200; choose upper bound by default)
- TRIALS = 3
- PAYLOADS = [512, 2048]
"""
import time
import uuid
import random
from pathlib import Path

import hbs
from node import Node
from metrics import log_metrics
import adversary

DEFAULT_ROUNDS = 200
DEFAULT_NODES = 8
DEFAULT_TRIALS = 3
DEFAULT_PAYLOADS = [512, 2048]
DEFAULT_TAG_PREFIX = "EXP"
ADV_SAMPLES_PER_RUN = 5

def _ensure_outdir() -> Path:
    out = Path("."); out.mkdir(exist_ok=True, parents=True); return out

def _adversarial_check(blocks, node: Node, run_id: str, alg: str, payload_bytes: int, exp_tag: str, nodes: int, rounds: int):
    sampled = random.sample(blocks, k=min(ADV_SAMPLES_PER_RUN, len(blocks)))
    tamper_rejected = 0
    replay_rejected = 0
    for b in sampled:
        tb = adversary.tamper(b.copy())
        if not node.verify_block(tb):
            tamper_rejected += 1
        rb = adversary.replay(b.copy())
        if not node.verify_block(rb):
            replay_rejected += 1

    vpath = _ensure_outdir() / "verification_log.csv"
    header_needed = not vpath.exists()
    with vpath.open("a", encoding="utf-8") as vf:
        if header_needed:
            vf.write("timestamp,run_id,exp_tag,alg,payload_bytes,nodes,rounds,kind,details\n")
        details = f"tamper_total={len(sampled)};tamper_rejected={tamper_rejected};replay_total={len(sampled)};replay_rejected={replay_rejected}"
        vf.write(f"{time.time():.3f},{run_id},{exp_tag},{alg},{payload_bytes},{nodes},{rounds},adversarial,{details}\n")

    return {"tamper_total": len(sampled), "tamper_rejected": tamper_rejected,
            "replay_total": len(sampled), "replay_rejected": replay_rejected}

def run_experiment(rounds=DEFAULT_ROUNDS, nodes=DEFAULT_NODES, trials=DEFAULT_TRIALS,
                   tag_prefix=DEFAULT_TAG_PREFIX, payloads=DEFAULT_PAYLOADS):
    algorithms = ["sphincs-sim", "xmss-sim", "lms-sim"]

    for payload_bytes in payloads:
        for trial in range(1, trials + 1):
            for alg in algorithms:
                run_id = str(uuid.uuid4())[:8]
                exp_tag = f"{tag_prefix}_{alg}_{payload_bytes}B_T{trial}"
                print(f"\n=== RUN {exp_tag} (run_id={run_id}) ===")
                print(f"Rounds={rounds}  Nodes={nodes}  Payload={payload_bytes}  Alg={alg}")

                # Node: accept (alg) to build its own signer
                node = Node(alg=alg, node_id="N0")

                # produce chain
                produced_blocks = []
                prev_hash = "GENESIS"
                for i in range(rounds):
                    data = "X" * payload_bytes
                    blk = node.create_block(index=i, previous_hash=prev_hash, data=data)
                    produced_blocks.append(blk)
                    prev_hash = blk["block_hash"]

                # metrics summary with TPS/p50/p95/valid_ratio
                summary = log_metrics(
                    blocks=produced_blocks,
                    node=node,
                    alg=alg,
                    nodes=nodes,
                    rounds=rounds,
                    payload_bytes=payload_bytes,
                    exp_tag=exp_tag,
                    run_id=run_id
                )
                print(f"Summary: {summary}")

                # adversarial
                adv_summary = _adversarial_check(
                    blocks=produced_blocks,
                    node=node,
                    run_id=run_id,
                    alg=alg,
                    payload_bytes=payload_bytes,
                    exp_tag=exp_tag,
                    nodes=nodes,
                    rounds=rounds
                )
                print(f"Adversarial Summary: {adv_summary}")

def main():
    run_experiment()

if __name__ == "__main__":
    main()
