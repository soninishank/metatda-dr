import os
from .metadata_node import MetadataNode


def simulate_partition(num_blocks: int = 1000, block_size: int = 4096) -> tuple:
    """
    Simulate metadata-based reconciliation under a network partition.

    Two nodes (n1, n2) start in sync, then diverge during a simulated
    partition. After the partition resolves, the delta between them is
    computed via set-difference on CompositeIDs — no rehashing required.

    Scenario:
        1. Both nodes ingest ``num_blocks`` identical blocks (baseline sync).
        2. During the partition, each node independently ingests 200 new blocks.
        3. On reconnection, each node computes which IDs the other lacks
           using a single set-difference operation.

    Args:
        num_blocks: Number of blocks ingested before the partition begins
                    (default: 1000).
        block_size: Size of each synthetic random block in bytes
                    (default: 4096 = 4 KB).

    Returns:
        A tuple (delta1, delta2) where:
            - delta1 (int): Number of blocks n1 has that n2 lacks.
            - delta2 (int): Number of blocks n2 has that n1 lacks.

        Under this simulation both values will always equal 200,
        demonstrating disjoint identifier spaces and single-round
        convergence with no hash recomputation.
    """
    n1 = MetadataNode("node1")
    n2 = MetadataNode("node2")

    # Baseline sync: both nodes receive the same blocks
    for _ in range(num_blocks):
        content = os.urandom(block_size)
        bid = n1.ingest(content)
        n2.ingest_replica(bid, content)

    # Partition: each node ingests independently (200 unique blocks each)
    for _ in range(200):
        n1.ingest(os.urandom(block_size))
        n2.ingest(os.urandom(block_size))

    # Reconcile: single set-difference, no re-hash
    delta1 = n1.compute_delta(n2.get_ids())
    delta2 = n2.compute_delta(n1.get_ids())

    return len(delta1), len(delta2)