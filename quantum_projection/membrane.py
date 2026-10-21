"""Amplitude-encoded statevectors stored in a complex outer-product memory.

SYNTHETIC. Classical emulation of quantum kinematics only: no speedup,
no Bell violation (all correlations here are classical numbers in one
array).

Encoding: oscillator k holds the complex amplitude c_k of the state.
Storage: W = sum_mu |p^mu><p^mu|.

project(field)
    Overlaps m_mu = <p^mu|field> and the normalized weights
    |m_mu|^2 / sum |m|^2. For orthonormal patterns these are the Born
    probabilities of measuring the field in that basis, conditioned on
    landing in the stored subspace.

recall(field, steps)
    Iterates a <- W a / ||W a||. This is a projection onto the stored
    subspace, not a collapse onto one pattern:
    * orthonormal patterns: W is an orthogonal projector (W^2 = W), so
      the fixed point P_S a / ||P_S a|| is reached after one step and
      further steps change nothing. The recalled fidelity to pattern mu
      equals its Born weight exactly.
    * non-orthogonal patterns: W is not a projector. Repeated steps are
      power iteration and drift toward W's dominant eigenvector, which is
      in general a superposition of the patterns, not one of them.

KetBraPair stores conjugated patterns ("bras") and multiplies without
conjugating at query time. That is the same inner product written a
second way; it agrees with project() up to floating-point rounding.
"""

import math

from .qsim import inner, normalize, _num_qubits, _check_qubit


def overlap(field, pattern):
    """<pattern|field>."""
    return inner(pattern, field)


def coarse_grain(state, qubit=0):
    """Pairwise Haar low-pass over one qubit, then renormalize.

    Pairs amplitudes whose indices differ only in `qubit` and keeps
    (a + b)/sqrt(2). This is exactly (<+|_qubit (x) I)|state>,
    renormalized: the merged qubit is projected onto |+>. LOSSY: the
    |-> component on that qubit is discarded, and states that differ
    only there become identical (for example |000> and |001> with
    qubit=0 both map to |00>). Raises ValueError if the |+> component
    is zero (e.g. |-> on that qubit).
    """
    _num_qubits(state)
    if len(state) < 2:
        raise ValueError("need at least one qubit to merge")
    _check_qubit(state, qubit)
    bit = 1 << qubit
    low = bit - 1
    s2 = math.sqrt(2.0)
    out = []
    for j in range(len(state) // 2):
        i = ((j & ~low) << 1) | (j & low)   # insert a 0 at position `qubit`
        out.append((state[i] + state[i | bit]) / s2)
    return normalize(out)


def _weights(ms):
    tot = sum(abs(m) ** 2 for m in ms)
    if tot == 0.0:
        return [0.0] * len(ms)
    return [abs(m) ** 2 / tot for m in ms]


def _argmax_abs(ms):
    return max(range(len(ms)), key=lambda i: abs(ms[i]))


def _check_patterns(patterns):
    patterns = list(patterns)
    if not patterns:
        raise ValueError("need at least one pattern")
    out = [normalize(p) for p in patterns]
    dim = len(out[0])
    if any(len(p) != dim for p in out):
        raise ValueError("all patterns must have the same length")
    return out


class HolographicMembrane:
    def __init__(self, patterns):
        self.patterns = _check_patterns(patterns)
        self.dim = len(self.patterns[0])

    def _check_field(self, field):
        if len(field) != self.dim:
            raise ValueError(f"field length {len(field)} != pattern length {self.dim}")
        return normalize(field)

    def overlaps(self, field):
        field = self._check_field(field)
        return [overlap(field, p) for p in self.patterns]

    def project(self, field):
        """Overlaps, normalized weights and the arg-max pattern."""
        ms = self.overlaps(field)
        return {"overlaps": ms, "probs": _weights(ms), "winner": _argmax_abs(ms)}

    def apply_w(self, a):
        """W a = sum_mu p^mu <p^mu|a> (not normalized)."""
        out = [0j] * self.dim
        for p in self.patterns:
            m = overlap(a, p)
            for j in range(self.dim):
                out[j] += p[j] * m
        return out

    def recall(self, field, steps=1):
        """Iterate a <- W a / ||W a||. Returns (final, winner, trajectory).

        Raises ValueError if the field is orthogonal to every pattern.
        """
        if not isinstance(steps, int) or isinstance(steps, bool) or steps < 1:
            raise ValueError("steps must be a positive integer")
        a = self._check_field(field)
        traj = []
        for _ in range(steps):
            a = normalize(self.apply_w(a))
            traj.append(_argmax_abs([overlap(a, p) for p in self.patterns]))
        return a, traj[-1], traj


class KetBraPair:
    """Stores kets and their conjugates (bras); bracket(mu, f) = sum bra*f.

    Mathematically identical to overlap(f, ket[mu]).
    """

    def __init__(self, kets):
        self.kets = _check_patterns(kets)
        self.bras = [[c.conjugate() for c in k] for k in self.kets]

    def bracket(self, mu, field):
        if len(field) != len(self.bras[mu]):
            raise ValueError("field length mismatch")
        return sum(b * f for b, f in zip(self.bras[mu], field))

    def project(self, field):
        field = normalize(field)
        ms = [self.bracket(mu, field) for mu in range(len(self.kets))]
        return {"overlaps": ms, "probs": _weights(ms), "winner": _argmax_abs(ms)}
