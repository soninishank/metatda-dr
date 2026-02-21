import os
from .metadata_node import MetadataNode


def simulate_partition(num_blocks=1000, block_size=4096):
    n1 = MetadataNode("node1")
    n2 = MetadataNode("node2")

    # baseline sync
    for _ in range(num_blocks):
        content = os.urandom(block_size)
        bid = n1.ingest(content)
        n2.ingest_replica(bid, content)

    # partition writes
    for _ in range(200):
        n1.ingest(os.urandom(block_size))
        n2.ingest(os.urandom(block_size))

    # reconcile
    delta1 = n1.compute_delta(n2.get_ids())
    delta2 = n2.compute_delta(n1.get_ids())

    return len(delta1), len(delta2)