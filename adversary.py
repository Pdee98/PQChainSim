#!/usr/bin/env python3
"""
adversary.py — simple tamper/replay helpers.
"""
from copy import deepcopy

def tamper(block_dict: dict) -> dict:
    b = deepcopy(block_dict)
    b["data"] = (b.get("data") or "") + "_TAMPER"
    return b

def replay(block_dict: dict) -> dict:
    # identical block; signature/index reused
    return deepcopy(block_dict)
