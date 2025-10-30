#!/usr/bin/env python3
"""
hbs.py — lightweight simulators for SPHINCS+ (stateless), XMSS (stateful), LMS (stateful).
NOT real crypto. Used for relative performance & state-behavior simulation only.
"""
import hashlib
import os
import struct

def _h(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()

class BaseSigner:
    name = "base"
    stateful = False
    def __init__(self):
        self.pk = os.urandom(32)

    def sign(self, msg: bytes) -> bytes:
        raise NotImplementedError

    def verify(self, msg: bytes, sig: bytes, pk: bytes) -> bool:
        # trivially bind to pk and msg via hash check
        return _h(pk + msg)[:8] == sig[:8]

class SPHINCSSim(BaseSigner):
    name = "sphincs-sim"
    stateful = False
    def sign(self, msg: bytes) -> bytes:
        # pretend large signature; include short MAC
        mac = _h(self.pk + msg)[:8]
        padding = b"S" * 2048   # simulate 2 KB+
        return mac + padding

class XMSSSim(BaseSigner):
    name = "xmss-sim"
    stateful = True
    def __init__(self):
        super().__init__()
        self.idx = 0

    def sign(self, msg: bytes) -> bytes:
        mac = _h(self.pk + msg + struct.pack(">I", self.idx))[:8]
        body = b"X" * 512       # simulate ~0.5 KB
        sig = mac + body + struct.pack(">I", self.idx)
        self.idx += 1
        return sig

class LMSSim(BaseSigner):
    name = "lms-sim"
    stateful = True
    def __init__(self):
        super().__init__()
        self.idx = 0

    def sign(self, msg: bytes) -> bytes:
        mac = _h(self.pk + msg + struct.pack(">I", self.idx))[:8]
        body = b"L" * 256       # simulate ~0.25 KB
        sig = mac + body + struct.pack(">I", self.idx)
        self.idx += 1
        return sig

def make_signer(alg: str) -> BaseSigner:
    a = (alg or "").lower()
    if "sphincs" in a:
        return SPHINCSSim()
    if "xmss" in a:
        return XMSSSim()
    if "lms" in a:
        return LMSSim()   # ← fixed name (LMSSim, not LMSSSim)
    raise ValueError(f"Unknown HBS alg: {alg}")

