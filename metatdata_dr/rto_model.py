def rto_hash_based(D, delta, H, C, N, S, B):
    """
    Hash-based RTO model.
    """
    T_hash = D / (H * C)
    T_index = (N * S) / B
    T_delta = delta / B
    return T_hash + T_index + T_delta


def rto_metadata(delta, N, S, B):
    """
    Metadata-driven RTO model.
    """
    T_index = (N * S) / B
    T_delta = delta / B
    return T_index + T_delta