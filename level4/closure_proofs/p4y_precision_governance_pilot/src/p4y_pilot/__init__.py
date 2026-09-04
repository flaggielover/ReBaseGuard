"""P4Y pre-freeze pilot -- precision governance only.

NON-BINDING.  This package is a pilot.  It creates no checkpoint, runs no
result-bearing production, and changes nothing about the P4 scientific line.

Scope is deliberately narrow: the *allocation and execution governance*
machinery that failed in the P4X successor campaign.

  G1  precision was targeted in expectation with one deterministic top-up, so
      a route could end in a third state -- neither at r* nor capped.
  G2  K-way sharding used ceil(B/K) blocks per shard, so K*ceil(B/K) >= B
      blocks executed and the frozen total was silently exceeded.

Nothing here imports, reads, writes or re-labels the P4X namespace, which is
not present on this branch at all.
"""

__all__ = ["shard", "blocks", "rules", "stats"]
