"""
rto_model.py

Closed-form analytical RTO models for both the hash-based and
metadata-driven disaster recovery frameworks, as derived in the paper.

All parameters use SI byte units (bytes, bytes/sec). Convert before calling:
    1 TiB = 1024**4 bytes
    1 GiB = 1024**3 bytes
    1 MB/s = 1024**2 bytes/sec
"""


def rto_hash_based(
    D: float,
    delta: float,
    H: float,
    C: int,
    N: int,
    S: int,
    B: float,
) -> float:
    """
    Compute RTO for the hash-based disaster recovery framework.

    Formula:
        RTO_hash = D / (H * C) + (N * S) / B + delta / B

    Args:
        D:     Total stored data in bytes.
        delta: Data delta (bytes written during outage) in bytes.
        H:     Hash throughput per core in bytes/sec
               (e.g. 500 MB/s = 500 * 1024**2).
        C:     Number of CPU cores available for parallel hashing.
        N:     Total number of data blocks.
        S:     Index entry size in bytes (e.g. 64 for SHA-256 hex + metadata).
        B:     Network bandwidth in bytes/sec (e.g. 10 GbE = 10 * 1024**3).

    Returns:
        Estimated RTO in **seconds**.

    Raises:
        ValueError: If H, C, or B are <= 0.
    """
    if H <= 0:
        raise ValueError(f"Hash throughput H must be > 0, got {H}")
    if C <= 0:
        raise ValueError(f"CPU core count C must be > 0, got {C}")
    if B <= 0:
        raise ValueError(f"Network bandwidth B must be > 0, got {B}")

    T_hash = D / (H * C)
    T_index = (N * S) / B
    T_delta = delta / B
    return T_hash + T_index + T_delta


def rto_metadata(
    delta: float,
    N: int,
    S: int,
    B: float,
) -> float:
    """
    Compute RTO for the metadata-driven disaster recovery framework.

    The full rehash term D/(H*C) is eliminated because blocks are
    identified by composite metadata IDs assigned at ingestion time.

    Formula:
        RTO_meta = (N * S) / B + delta / B

    Args:
        delta: Data delta (bytes written during outage) in bytes.
        N:     Total number of data blocks.
        S:     Index entry size in bytes.
        B:     Network bandwidth in bytes/sec.

    Returns:
        Estimated RTO in **seconds**.

    Raises:
        ValueError: If B is <= 0.
    """
    if B <= 0:
        raise ValueError(f"Network bandwidth B must be > 0, got {B}")

    T_index = (N * S) / B
    T_delta = delta / B
    return T_index + T_delta