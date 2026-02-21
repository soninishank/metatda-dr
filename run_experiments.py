#!/usr/bin/env python3
"""
run_experiments.py

Entry point for the Metadata-Driven DR analytical evaluation framework.

Usage:
    python3 run_experiments.py \
        --data-tb 100 \
        --delta-tb 1 \
        --cores 16 \
        --bandwidth-gbps 10

Outputs results to outputs/results.csv and prints a summary to stdout.
"""

import argparse
import csv
import os

from metatdata_dr.rto_model import rto_hash_based, rto_metadata
from metatdata_dr.dr_simulation import simulate_partition

TB = 1024 ** 4        # bytes per TiB
GB = 1024 ** 3        # bytes per GiB
MB = 1024 ** 2        # bytes per MiB

# Hardware defaults from the paper's reproducibility notes
BLOCK_SIZE_DEFAULT = 100 * 1024      # 100 KB average block size (used for block count estimation)
INDEX_ENTRY_SIZE = 64                # bytes per index entry (SHA-256 hex + metadata)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Analytical RTO comparison: Hash-based vs Metadata-driven DR"
    )
    parser.add_argument("--data-tb", type=float, default=100.0,
                        help="Total stored data in TiB (default: 100)")
    parser.add_argument("--delta-tb", type=float, default=1.0,
                        help="Data delta during outage in TiB (default: 1)")
    parser.add_argument("--cores", type=int, default=16,
                        help="Number of CPU cores for hashing (default: 16)")
    parser.add_argument("--bandwidth-gbps", type=float, default=10.0,
                        help="Network bandwidth in Gbps (default: 10)")
    parser.add_argument("--hash-throughput-mbps", type=float, default=500.0,
                        help="Hash throughput per core in MB/s (default: 500)")
    parser.add_argument("--output-dir", type=str, default="outputs",
                        help="Directory to write results.csv (default: outputs/)")
    return parser.parse_args()


def format_duration(seconds: float) -> str:
    """Return a human-readable duration string."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        return f"{seconds / 60:.1f} min"
    else:
        return f"{seconds / 3600:.2f} hr"


def main():
    args = parse_args()

    # Convert units to bytes / bytes-per-second
    D = args.data_tb * TB
    delta = args.delta_tb * TB
    H = args.hash_throughput_mbps * MB
    C = args.cores
    B = args.bandwidth_gbps * GB
    N = int(D / BLOCK_SIZE_DEFAULT)   # estimated number of blocks
    S = INDEX_ENTRY_SIZE

    # --- Analytical RTO ---
    rto_hash = rto_hash_based(D, delta, H, C, N, S, B)
    rto_meta = rto_metadata(delta, N, S, B)
    improvement = rto_hash / rto_meta if rto_meta > 0 else float("inf")

    # --- Partition simulation ---
    print("Running partition convergence simulation...")
    d1, d2 = simulate_partition()

    # --- Print summary ---
    print()
    print("=" * 50)
    print("  Metadata-Driven DR: Analytical RTO Results")
    print("=" * 50)
    print(f"  Dataset size        : {args.data_tb:.1f} TiB")
    print(f"  Delta (outage)      : {args.delta_tb:.1f} TiB")
    print(f"  CPU cores           : {C}")
    print(f"  Hash throughput     : {args.hash_throughput_mbps:.0f} MB/s/core")
    print(f"  Network bandwidth   : {args.bandwidth_gbps:.0f} Gbps")
    print(f"  Estimated blocks    : {N:,}")
    print("-" * 50)
    print(f"  RTO (hash-based)    : {format_duration(rto_hash)}")
    print(f"  RTO (metadata)      : {format_duration(rto_meta)}")
    print(f"  Improvement factor  : {improvement:.1f}x")
    print("-" * 50)
    print(f"  Partition sim delta : node1={d1} blocks, node2={d2} blocks")
    print(f"  Convergence rounds  : 1 (set-difference, no re-hash)")
    print("=" * 50)

    # --- Write CSV ---
    os.makedirs(args.output_dir, exist_ok=True)
    out_path = os.path.join(args.output_dir, "results.csv")
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "data_tb", "delta_tb", "cores", "bandwidth_gbps",
            "hash_throughput_mbps", "num_blocks", "index_entry_bytes",
            "rto_hash_sec", "rto_meta_sec", "improvement_factor",
            "partition_delta_node1", "partition_delta_node2"
        ])
        writer.writerow([
            args.data_tb, args.delta_tb, C, args.bandwidth_gbps,
            args.hash_throughput_mbps, N, S,
            round(rto_hash, 2), round(rto_meta, 2), round(improvement, 2),
            d1, d2
        ])

    print(f"\n  Results saved to: {out_path}")


if __name__ == "__main__":
    main()
