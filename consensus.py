# consensus.py — simple round-robin block production with simulated propagation delay
import time, random, hashlib
from block import Block

class Consensus:
    def __init__(self, nodes):
        self.nodes = nodes

    def hash_block(self, block: Block) -> str:
        block_string = f"{block.index}{block.timestamp}{block.data}".encode()
        return hashlib.sha256(block_string).hexdigest()

    def run_rounds(self, rounds: int, payload_bytes: int = 512, delay_range=(0.01, 0.03)):
        blocks = []
        last_hash = "0" * 64
        for i in range(rounds):
            time.sleep(random.uniform(*delay_range))  # simulate propagation
            node = self.nodes[i % len(self.nodes)]
            data = ("X" * payload_bytes)  # payload
            block_data = node.create_block(i, last_hash, data)
            block = Block(index=block_data["index"],
                          timestamp=time.time(),
                          previous_hash=block_data["previous_hash"],
                          data=block_data["data"],
                          signature=block_data["signature"],
                          public_key=block_data["public_key"],
                          alg=block_data["alg"])
            blocks.append(block)
            last_hash = self.hash_block(block)
        return blocks
