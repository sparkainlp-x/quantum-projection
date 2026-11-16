# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)
"""DNA avatars as toy state vectors, with self-knowing D per avatar.

SYNTHETIC. Classical emulation only: a DNA avatar is a toy encoding,
not biology. A sequence of L bases is a basis state of 2L qubits
(2 qubits per base: A=00, C=01, G=10, T=11), and an avatar is a
normalized superposition over a small list of variant sequences
("its genome"). The encoding is exact and lossless for the sequence;
the superposition models the avatar as a distribution over possible
genomes. Nothing here is a biological claim.

Self-knowing D = <psi|P|psi> is the self-determinism factor: P is the
orthogonal projector onto the stored (healthy) subspace. The idea is
vendored from symmetry-entropy's self_determinism_factor and the
Faggin field bridge's self_knowing.py (Brisson); the implementation
here is original (Gram-Schmidt with this package's own inner product,
standard library only). For orthonormal stored patterns D equals the
total Born weight on the stored subspace.

Energy: each sequence carries E = h*nu with h = 1 in model units and
nu = 1 + GC content (the number of G/C bases plus one). This is
Planck's relation used as the cascade's quantization rule: the
population's energy spectrum per generation is the histogram of
avatar energies, and its peak is tracked like a black-body peak.
The units are model units; no physical energy is claimed.
"""

import math
import random

from .membrane import HolographicMembrane
from .qsim import inner, normalize

BASES = "ACGT"
_BASE_INDEX = {"A": 0, "C": 1, "G": 2, "T": 3}

# Stored ("healthy") reference sequences: low GC, all A/T. They are the
# stored subspace of the membrane. Chosen fixed so every run measures
# against the same reference.
HEALTHY_SEQUENCES = ["AATTAA", "ATATAT", "TAAATA", "AATATT"]

# Model parameters (stated, not measured constants).
SEQUENCE_LENGTH = 6          # bases per sequence (12 qubits, 4096 dims)
TRAUMA_FLIPS = 3             # base flips turning a healthy sequence into a trauma variant
SEED_WEIGHT = 0.05           # weight of the retained healthy sequence in a new avatar
VARIANT_WEIGHTS = (0.5, 0.3, 0.15, 0.05)  # weights of the trauma variants
MAX_VARIANTS = 12            # cap on an avatar's variant list per generation

_encode_cache = {}


def encode_sequence(seq):
    """Basis state for a DNA sequence (2 qubits per base)."""
    if len(seq) != SEQUENCE_LENGTH or any(b not in BASES for b in seq):
        raise ValueError(f"sequence must be {SEQUENCE_LENGTH} bases in ACGT, got {seq!r}")
    if seq not in _encode_cache:
        idx = 0
        for b in seq:
            idx = (idx << 2) | _BASE_INDEX[b]
        v = [0j] * (1 << (2 * SEQUENCE_LENGTH))
        v[idx] = 1.0 + 0j
        _encode_cache[seq] = v
    return _encode_cache[seq]


def sequence_index(seq):
    """Basis index of a sequence (the same bit-packing as
    encode_sequence, without building the 4096-vector)."""
    if len(seq) != SEQUENCE_LENGTH or any(b not in BASES for b in seq):
        raise ValueError(f"sequence must be {SEQUENCE_LENGTH} bases in ACGT, got {seq!r}")
    idx = 0
    for b in seq:
        idx = (idx << 2) | _BASE_INDEX[b]
    return idx


def index_to_sequence(idx):
    """Inverse of sequence_index."""
    if not 0 <= idx < (1 << (2 * SEQUENCE_LENGTH)):
        raise ValueError(f"index out of range for {SEQUENCE_LENGTH} bases: {idx}")
    chars = []
    for _ in range(SEQUENCE_LENGTH):
        chars.append(BASES[idx & 3])
        idx >>= 2
    return "".join(reversed(chars))


def avatar_state(sequences, weights):
    """Normalized superposition sum_i weights[i] * |sequences[i]>."""
    if len(sequences) != len(weights):
        raise ValueError("sequences and weights must have the same length")
    if not sequences:
        raise ValueError("need at least one variant sequence")
    dim = 1 << (2 * SEQUENCE_LENGTH)
    out = [0j] * dim
    for s, w in zip(sequences, weights):
        v = encode_sequence(s)
        for j in range(dim):
            out[j] += w * v[j]
    return normalize(out)


def gc_content(seq):
    """Number of G/C bases (0..SEQUENCE_LENGTH)."""
    return sum(1 for b in seq if b in "GC")


def energy_of(seq):
    """E = h*nu with h = 1 (model units) and nu = 1 + GC content."""
    return 1.0 + gc_content(seq)


def dominant_sequence(sequences, weights):
    """The variant with the largest weight (the avatar's dominant genome)."""
    return sequences[max(range(len(weights)), key=lambda i: weights[i])]


def mutate_sequence(seq, rng):
    """Flip one uniformly chosen base to a different base."""
    i = rng.randrange(len(seq))
    choices = [b for b in BASES if b != seq[i]]
    return seq[:i] + rng.choice(choices) + seq[i + 1:]


def trauma_variant(healthy, rng, nflips=TRAUMA_FLIPS):
    """A healthy sequence with `nflips` random base flips."""
    s = healthy
    for _ in range(nflips):
        s = mutate_sequence(s, rng)
    return s


def make_avatar(healthy, rng):
    """A new avatar: one retained healthy sequence (small weight) plus
    trauma variants of it. The retained healthy sequence is the seed
    of health the cascade amplifies; without it the projection could
    never create stored weight, only amplify what is already there."""
    variants = [healthy] + [trauma_variant(healthy, rng) for _ in VARIANT_WEIGHTS]
    weights = [SEED_WEIGHT] + list(VARIANT_WEIGHTS)
    return {"sequences": list(variants), "weights": list(weights)}


def make_population(n_avatars, seed):
    """M avatars, cycling through the healthy references as templates."""
    rng = random.Random(seed)
    return [make_avatar(HEALTHY_SEQUENCES[m % len(HEALTHY_SEQUENCES)], rng)
            for m in range(n_avatars)]


def healthy_membrane():
    """HolographicMembrane storing the healthy reference sequences."""
    return HolographicMembrane([encode_sequence(s) for s in HEALTHY_SEQUENCES])


def _projector_basis(patterns):
    """Orthonormal basis for span{patterns} by modified Gram-Schmidt.

    Uses this package's own inner product. For orthonormal patterns
    (the healthy sequences are basis states) the basis is the patterns
    themselves. Near-zero vectors are dropped.
    """
    basis = []
    for p in patterns:
        v = [complex(c) for c in p]
        for q in basis:
            coeff = inner(q, v)  # hoisted: one inner product per basis vector
            v = [a - coeff * b for a, b in zip(v, q)]
        n = math.sqrt(sum(abs(c) ** 2 for c in v))
        if n > 1e-10:
            basis.append([c / n for c in v])
    return basis


def self_knowing(state, membrane):
    """D = <psi|P|psi> in [0, 1]: how much of the avatar lies in the
    stored (healthy) subspace. D = 1 means fully stored; D = 0 means
    orthogonal to every stored pattern (the kernel: fully blind)."""
    basis = _projector_basis(membrane.patterns)
    d = sum(abs(inner(q, state)) ** 2 for q in basis)
    return min(1.0, max(0.0, d))
