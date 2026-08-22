"""Deterministic, recoverable random-number streams.

Two rules govern every formal run:

1.  Every random draw is attributable to a named stream whose full seed
    material is recorded in the run manifest.
2.  The statistical unit of a run (replicate for Gate 4.1, batch for Gate 4.2)
    can be re-simulated *in isolation* and reproduce bit-identical output.

Rule 2 is why Gate 4.1 does not use one generator shared across replicates in
lockstep: that would make replicate 37's numbers depend on how many replicates
happened to be run beside it.  ``PerRowStream`` gives every replicate its own
``PCG64`` stream while still allowing the chains to be advanced with vectorised
NumPy, by buffering each row's own draws and consuming them column-wise.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# Stream identifiers.  These are part of the seed material and must never be
# renumbered: doing so silently changes every historical result.
STREAM_OBS = 0
STREAM_FRESH = 1
STREAM_BOOTSTRAP = 2
STREAM_CONDITIONAL = 3


def seed_sequence(master_seed: int, *key: int) -> np.random.SeedSequence:
    """Derive a ``SeedSequence`` from the master seed and an integer key.

    The key is part of the recorded provenance.  ``SeedSequence`` hashes the
    whole entropy list, so distinct keys give statistically independent streams
    and the mapping (master_seed, key) -> stream is a pure function.
    """
    return np.random.SeedSequence([int(master_seed), *(int(k) for k in key)])


def generator(master_seed: int, *key: int) -> np.random.Generator:
    """A ``Generator`` fully determined by ``(master_seed, key)``."""
    return np.random.Generator(np.random.PCG64(seed_sequence(master_seed, *key)))


class ScalarStream:
    """One generator shared by a batch of independent paths.

    Appropriate when the statistical unit *is* the batch (Gate 4.2): the whole
    batch is reproduced by re-running it with the same key.
    """

    def __init__(self, master_seed: int, *key: int) -> None:
        self.master_seed = int(master_seed)
        self.key = tuple(int(k) for k in key)
        self._rng = generator(master_seed, *key)

    def draw(self, count: int) -> np.ndarray:
        return self._rng.standard_normal(count)

    def provenance(self) -> dict[str, object]:
        return {
            "kind": "ScalarStream",
            "bit_generator": "PCG64",
            "master_seed": self.master_seed,
            "key": list(self.key),
            "entropy": [self.master_seed, *self.key],
        }


@dataclass(slots=True)
class _RowBuffers:
    values: np.ndarray  # (n_rows, chunk)
    cursor: np.ndarray  # (n_rows,)


class PerRowStream:
    """Independent ``PCG64`` stream per row, consumed in vectorised lockstep.

    Row ``r`` draws exactly the sequence ``generator(master_seed, stream_id, r)``
    would produce, in order, no matter how many other rows exist or when they
    finish.  Re-simulating replicate ``r`` alone therefore reproduces it
    bit-for-bit.
    """

    def __init__(
        self,
        master_seed: int,
        stream_id: int,
        n_rows: int,
        *,
        chunk: int = 4096,
        row_offset: int = 0,
    ) -> None:
        if n_rows <= 0 or chunk <= 0:
            raise ValueError("n_rows and chunk must be positive")
        self.master_seed = int(master_seed)
        self.stream_id = int(stream_id)
        self.n_rows = int(n_rows)
        self.chunk = int(chunk)
        self.row_offset = int(row_offset)
        self._rngs = [
            generator(master_seed, stream_id, row_offset + r) for r in range(n_rows)
        ]
        self._buf = _RowBuffers(
            values=np.empty((n_rows, chunk)),
            cursor=np.full(n_rows, chunk, dtype=np.int64),
        )

    def _refill(self, rows: np.ndarray) -> None:
        for r in rows:
            self._buf.values[r] = self._rngs[r].standard_normal(self.chunk)
        self._buf.cursor[rows] = 0

    def draw(self, rows: np.ndarray) -> np.ndarray:
        """One standard normal for each row in ``rows`` (an index array)."""
        exhausted = rows[self._buf.cursor[rows] >= self.chunk]
        if exhausted.size:
            self._refill(exhausted)
        out = self._buf.values[rows, self._buf.cursor[rows]]
        self._buf.cursor[rows] += 1
        return out

    def provenance(self) -> dict[str, object]:
        return {
            "kind": "PerRowStream",
            "bit_generator": "PCG64",
            "master_seed": self.master_seed,
            "stream_id": self.stream_id,
            "n_rows": self.n_rows,
            "row_offset": self.row_offset,
            "chunk": self.chunk,
            "row_entropy_rule": "SeedSequence([master_seed, stream_id, row_index])",
        }

    def row_entropy(self, row: int) -> list[int]:
        """The exact entropy list backing one row, for the raw-data manifest."""
        return [self.master_seed, self.stream_id, self.row_offset + int(row)]
