import zlib
from typing import Dict, Set
from .identifiers import AtomicCounter, CompositeID, generate_nid


class MetadataNode:
    """
    Metadata-driven storage node.
    """

    def __init__(self, name: str, nst=None):
        self.name = name
        self.nid = generate_nid()
        self.nst = nst
        self.clock = AtomicCounter()
        self.index: Dict[str, bytes] = {}
        self.wal = []

    def ingest(self, content: bytes) -> CompositeID:
        lcv = self.clock.increment()
        block_id = CompositeID(self.nid, lcv, self.nst)
        key = block_id.key

        self.wal.append(lcv)
        self.index[key] = content
        return block_id

    def ingest_replica(self, block_id: CompositeID, content: bytes):
        self.index[block_id.key] = content

    def get_ids(self) -> Set[str]:
        return set(self.index.keys())

    def compute_delta(self, other_ids: Set[str]) -> Set[str]:
        return set(self.index.keys()) - other_ids

    def simulate_crash_recover(self):
        if self.wal:
            self.clock = AtomicCounter(self.wal[-1])