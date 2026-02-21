import hashlib
from typing import Dict, Set


class HashNode:
    """
    SHA-256-based storage node — hash-framework baseline.

    Simulates a traditional content-addressed storage node that must
    recompute its hash index from raw block data after a crash.

    Attributes:
        name:       Human-readable node label.
        store:      Address-keyed raw block store (addr -> bytes).
        hash_index: SHA-256 hex digest -> block content mapping.
        next_addr:  Monotonic integer address for the next ingested block.
    """

    def __init__(self, name: str):
        self.name = name
        self.store: Dict[int, bytes] = {}
        self.hash_index: Dict[str, bytes] = {}
        self.next_addr: int = 0

    def ingest(self, content: bytes) -> str:
        """
        Ingest a block: compute its SHA-256 hash, store it, and index it.

        Args:
            content: Raw block bytes.

        Returns:
            SHA-256 hex digest string of the block.
        """
        h = hashlib.sha256(content).hexdigest()
        self.store[self.next_addr] = content
        self.hash_index[h] = content
        self.next_addr += 1
        return h

    def invalidate_index(self) -> None:
        """
        Simulate hash index loss (e.g. crash or index-store failure).

        Clears the in-memory hash index; ``store`` is retained so the
        node can rebuild the index via ``rebuild_index()``.
        """
        self.hash_index.clear()

    def rebuild_index(self, hash_throughput_bps: float, cpu_cores: int) -> float:
        """
        Estimate the time (in seconds) to rehash all stored blocks.

        This models the dominant RTO term for the hash-based framework:
            T_hash = D / (H * C)

        Args:
            hash_throughput_bps: Hash throughput per core in bytes/sec
                                 (e.g. 500 * 1024**2 for 500 MB/s).
            cpu_cores:           Number of parallel hashing cores.

        Returns:
            Estimated rehash duration in **seconds**.

        Raises:
            ValueError: If hash_throughput_bps or cpu_cores is <= 0.
        """
        if hash_throughput_bps <= 0:
            raise ValueError(f"hash_throughput_bps must be > 0, got {hash_throughput_bps}")
        if cpu_cores <= 0:
            raise ValueError(f"cpu_cores must be > 0, got {cpu_cores}")

        total_bytes = sum(len(v) for v in self.store.values())
        return total_bytes / (hash_throughput_bps * cpu_cores)

    def get_hashes(self) -> Set[str]:
        """Return the set of SHA-256 hex digests currently in the index."""
        return set(self.hash_index.keys())