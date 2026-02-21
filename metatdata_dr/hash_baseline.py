import hashlib
from typing import Dict, Set


class HashNode:
    """
    SHA-256-based storage node baseline.
    """

    def __init__(self, name: str):
        self.name = name
        self.store: Dict[int, bytes] = {}
        self.hash_index: Dict[str, bytes] = {}
        self.next_addr = 0

    def ingest(self, content: bytes):
        h = hashlib.sha256(content).hexdigest()
        self.store[self.next_addr] = content
        self.hash_index[h] = content
        self.next_addr += 1
        return h

    def invalidate_index(self):
        self.hash_index.clear()

    def rebuild_index(self, hash_throughput_bps, cpu_cores):
        total_bytes = sum(len(v) for v in self.store.values())
        return total_bytes / (hash_throughput_bps * cpu_cores)

    def get_hashes(self) -> Set[str]:
        return set(self.hash_index.keys())