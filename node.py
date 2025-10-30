#!/usr/bin/env python3
"""
node.py — wraps a signer, creates and verifies blocks, and enforces anti-replay for stateful HBS.
"""
import hashlib
import time
import struct
import hbs as hbs_mod

def _hash_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def _parse_idx_from_sig(sig: bytes):
    # Our stateful sims append a 4-byte big-endian index at the tail.
    if len(sig) < 4:
        return None
    return struct.unpack(">I", sig[-4:])[0]

class Node:
    def __init__(self, alg=None, node_id="N0", signer=None):
        # allow either alg or a ready-made signer
        self.signer = signer if signer is not None else hbs_mod.make_signer(alg)
        self.node_id = node_id
        self.used_indices = set()  # for stateful anti-replay

    def _msg_bytes(self, index: int, prev_hash: str, data: str) -> bytes:
        return f"{index}|{prev_hash}|{data}".encode("utf-8")

    def create_block(self, index: int, previous_hash: str, data: str) -> dict:
        ts = time.time()
        msg = self._msg_bytes(index, previous_hash, data)
        sig = self.signer.sign(msg)
        blk_hash = _hash_hex(f"{index}|{ts}|{previous_hash}|{data}".encode("utf-8"))
        return {
            "index": index,
            "timestamp": ts,
            "previous_hash": previous_hash,
            "data": data,
            "signature": sig,
            "public_key": self.signer.pk,
            "alg": self.signer.name,
            "producer": self.node_id,
            "block_hash": blk_hash,
        }

    def verify_block(self, b: dict) -> bool:
        import struct, hashlib

        def _h(x: bytes) -> bytes:
            return hashlib.sha256(x).digest()

        # reconstruct message
        msg = self._msg_bytes(b.get("index", -1), b.get("previous_hash", ""), b.get("data", ""))
        sig = b.get("signature", b"")
        pk = b.get("public_key", b"")
        alg = (b.get("alg") or "").lower()

        # is this a stateful scheme?
        stateful = ("xmss" in alg) or ("lms" in alg)

        # for XMSS/LMS, the last 4 bytes of sig encode the index used during signing
        idx = None
        if stateful:
            if len(sig) < 4:
                return False
            idx = struct.unpack(">I", sig[-4:])[0]

            # anti-replay: reject if index already used
            if idx in self.used_indices:
                return False

            expected_mac = _h(pk + msg + struct.pack(">I", idx))[:8]
        else:
            expected_mac = _h(pk + msg)[:8]

        ok = (sig[:8] == expected_mac)

        # record index only on success for stateful schemes
        if ok and stateful and idx is not None:
            self.used_indices.add(idx)

        return ok
