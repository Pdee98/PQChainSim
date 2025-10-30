# main.py — interactive runner for experiments
import time
from consensus import Consensus
from node import Node
from metrics import log_metrics
from adversary import tamper, replay

ALG_LIST = ["sphincs-sim", "xmss-sim", "lms-sim"]

def run_for_alg(alg: str, rounds: int, nodes_n: int, payload: int, tag: str):
    nodes = [Node(f"{alg}-Node{i}", alg=alg) for i in range(nodes_n)]
    cons = Consensus(nodes)
    t0 = time.time()
    blocks = cons.run_rounds(rounds, payload_bytes=payload)
    t1 = time.time()
    log_metrics(blocks, nodes, label=alg, started_at=t0, ended_at=t1,
                meta={"exp_tag": tag, "nodes": nodes_n, "rounds": rounds, "payload_bytes": payload})

    # Adversarial checks (simple functional checks)
    tampered = tamper(blocks[0].__dict__)
    tamper_ok = not nodes[0].verify_block(tampered)
    replayed = replay(blocks[1].__dict__)
    is_stateless = "sphincs" in alg
    replay_ok = (not nodes[1].verify_block(replayed)) if not is_stateless else nodes[1].verify_block(replayed)

    print("Adversarial checks:")
    print(f" - Tamper: {'PASS' if tamper_ok else 'FAIL'}")
    print(f" - Replay: {'PASS' if replay_ok else 'FAIL'}")
    return blocks

def prompt_int(prompt, default):
    s = input(f"{prompt} [{default}]: ").strip()
    return int(s) if s else int(default)

def prompt_str(prompt, default):
    s = input(f"{prompt} [{default}]: ").strip()
    return s if s else default

def main():
    print("Interactive experiment runner (press Enter to accept defaults)")
    rounds = prompt_int("Number of blocks (ROUNDS)", 200)
    nodes_n = prompt_int("Number of nodes (NODES)", 8)
    payload = prompt_int("Payload size in bytes (PAYLOAD: 512≈0.5KB, 2048≈2KB)", 512)
    trials  = prompt_int("Number of trials (repeat runs)", 3)
    tag_prefix = prompt_str("Tag prefix for this experiment set (EXP_TAG)", "interactive")

    for t in range(1, trials+1):
        tag = f"{tag_prefix}_t{t}_p{payload}"
        for alg in ALG_LIST:
            print(f"\n=== Algorithm: {alg} | rounds={rounds}, nodes={nodes_n}, payload={payload}B, tag={tag} ===")
            run_for_alg(alg, rounds, nodes_n, payload, tag)

    ans = prompt_str("Also repeat the same trials with PAYLOAD=2048 (2KB)? y/n", "y").lower()
    if ans.startswith("y"):
        payload2 = 2048
        for t in range(1, trials+1):
            tag = f"{tag_prefix}_t{t}_p{payload2}"
            for alg in ALG_LIST:
                print(f"\n=== Algorithm: {alg} | rounds={rounds}, nodes={nodes_n}, payload={payload2}B, tag={tag} ===")
                run_for_alg(alg, rounds, nodes_n, payload2, tag)

    print("All runs complete. Results appended to 'blockchain_metrics.csv' and 'verification_log.csv'.")
    print("Generate figures with:  python plot.py")

if __name__ == "__main__":
    main()
