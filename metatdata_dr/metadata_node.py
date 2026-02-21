from typing import Dict, List, Optional, Set
from .identifiers import AtomicCounter, CompositeID, generate_nid


class MetadataNode:
    """
    Metadata-driven storage node.

    Each node assigns a deterministic CompositeID to every ingested block
    at write time, eliminating content-based hashing from the recovery path.
    Delta computation during DR is a pure set-difference operation over IDs.

    Attributes:
        name:  Human-readable node label (for logging/debugging).
        nid:   128-bit UUID assigned at node creation.
        nst:   Optional namespace/shard tag propagated into all CompositeIDs.
        clock: Thread-safe monotonic logical clock (Logical Clock Value).
        index: In-memory map of CompositeID.key -> block content (bytes).
        wal:   Write-ahead log of LCV values for crash recovery.
    """

    def __init__(self, name: str, nst: Optional[str] = None):
        self.name = name
        self.nid: str = generate_nid()
        self.nst: Optional[str] = nst
        self.clock: AtomicCounter = AtomicCounter()
        self.index: Dict[str, bytes] = {}
        self.wal: List[int] = []

    def ingest(self, content: bytes) -> CompositeID:
        """
        Ingest a new block, assign it a CompositeID, log to WAL, and store.

        Args:
            content: Raw block bytes.

        Returns:
            The CompositeID assigned to this block.
        """
        lcv = self.clock.increment()
        block_id = CompositeID(self.nid, lcv, self.nst)
        key = block_id.key
        self.wal.append(lcv)
        self.index[key] = content
        return block_id

    def ingest_replica(self, block_id: CompositeID, content: bytes) -> None:
        """
        Store a replica block using its already-assigned CompositeID.

        Args:
            block_id: The CompositeID from the primary node.
            content:  Raw block bytes.
        """
        self.index[block_id.key] = content

    def get_ids(self) -> Set[str]:
        """Return the set of all CompositeID keys currently in the index."""
        return set(self.index.keys())

    def compute_delta(self, other_ids: Set[str]) -> Set[str]:
        """
        Compute blocks present on this node but absent on another.

        Args:
            other_ids: The set of CompositeID keys from the remote node.

        Returns:
            Set of CompositeID keys that this node has and the remote lacks.
        """
        return set(self.index.keys()) - other_ids

    def simulate_crash_recover(self) -> None:
        """
        Simulate clock recovery after a crash using the WAL.

        Restores the logical clock to the last committed LCV so that
        subsequent ingests do not produce duplicate IDs.

        .. warning::
            This method restores the **clock only**. The ``index`` is NOT
            repopulated here. In a real system, the block store would be
            re-scanned or replayed from the WAL to rebuild ``self.index``
            before resuming ingestion. This simulation assumes the index
            is restored separately (e.g. by the caller or from durable
            storage).
        """
        if self.wal:
            self.clock = AtomicCounter(self.wal[-1])