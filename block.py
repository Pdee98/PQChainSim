# block.py
class Block:
    def __init__(self, index, timestamp, previous_hash, data, signature, public_key, alg):
        self.index = index
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.data = data
        self.signature = signature
        self.public_key = public_key
        self.alg = alg
