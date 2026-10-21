"""Projection of quantum statevectors into a holographic membrane.

The membrane holds complex amplitudes (not just phases): oscillator k
holds c_k, the k-th amplitude of the encoded state. Stored patterns
are quantum states; the membrane's native recall operation IS the
projective measurement:

    m_mu = <p^mu|field>          (overlap = projection amplitude)
    P_mu|field> ~ m_mu |p^mu>    (recalled = projected component)
    |m_mu|^2 / sum |m|^2         (Born-rule-like outcome probabilities)

Iterated recall a <- W a / ||W a|| with W = sum_mu |p^mu><p^mu| is
projected gradient flow onto the stored subspace: the field
collapses onto the nearest stored pattern, the classical shadow of
wavefunction collapse onto a measurement eigenstate.

KetBraPair splits the inner product across two conjugate membranes:
yin holds the kets |p^mu>, yang holds the bras <p^mu| (conjugates).
<m|field> is then computed *between* the membranes -- the tic of the
yin-yang loop, now as a measurement device.

Coarse-graining: 2^n amplitudes -> M oscillators by pairwise Haar
low-pass + renormalization. LOSSY on purpose: the high-pass energy is
discarded. The engineering knob for n too large to hold exactly --
and its information cost must be measured, not assumed.
"""

import math

from qsim import normalize


def overlap(field, pattern):
    """<pattern|field> for normalized vectors."""
    return sum(p.conjugate() * f for p, f in zip(pattern, field))


def coarse_grain(state):
    """Pairwise Haar low-pass: 2^n -> 2^(n-1) amplitudes, then
    renormalized. LOSSY by design: the high-pass (difference) energy
    is discarded -- that is what coarse-graining means. What survives
    is the smooth, low-frequency content of the state."""
    assert len(state) % 2 == 0
    s2 = math.sqrt(2.0)
    return normalize([(state[2 * j] + state[2 * j + 1]) / s2
                      for j in range(len(state) // 2)])


class HolographicMembrane:
    def __init__(self, patterns):
        """patterns: list of normalized statevectors (lists of complex)."""
        self.patterns = [normalize(p) for p in patterns]
        self.n = len(self.patterns[0])
        assert all(len(p) == self.n for p in self.patterns)

    def overlaps(self, field):
        return [overlap(field, p) for p in self.patterns]

    def project(self, field):
        """One-shot projective measurement: overlaps + Born-like probs."""
        ms = self.overlaps(field)
        tot = sum(abs(m) ** 2 for m in ms)
        probs = [abs(m) ** 2 / tot if tot else 0.0 for m in ms]
        winner = max(range(len(ms)), key=lambda i: abs(ms[i]))
        return {"overlaps": ms, "probs": probs, "winner": winner}

    def recall(self, field, steps=25):
        """Iterated projection: collapse the field onto the nearest
        stored pattern. Returns (final_field, winner, trajectory)."""
        a = normalize(list(field))
        traj = []
        for _ in range(steps):
            ms = self.overlaps(a)
            # a <- sum_mu p^mu <p^mu|a>  (= W a), then renormalize
            b = [0j] * self.n
            for p, m in zip(self.patterns, ms):
                for j in range(self.n):
                    b[j] += p[j] * m
            nrm = math.sqrt(sum(abs(c) ** 2 for c in b)) or 1.0
            a = [c / nrm for c in b]
            traj.append(max(range(len(ms)), key=lambda i: abs(ms[i])))
        ms = self.overlaps(a)
        winner = max(range(len(ms)), key=lambda i: abs(ms[i]))
        return a, winner, traj


class KetBraPair:
    """Yin holds kets |p^mu>; yang holds bras <p^mu| (conjugates).
    The bracket <m|field> is computed *between* the membranes."""

    def __init__(self, kets):
        self.kets = [normalize(k) for k in kets]
        self.bras = [[c.conjugate() for c in k] for k in self.kets]

    def bracket(self, mu, field):
        """<p^mu|field> via the bra membrane."""
        return sum(b * f for b, f in zip(self.bras[mu], field))

    def project(self, field):
        ms = [self.bracket(mu, field) for mu in range(len(self.kets))]
        tot = sum(abs(m) ** 2 for m in ms)
        probs = [abs(m) ** 2 / tot if tot else 0.0 for m in ms]
        return {"overlaps": ms, "probs": probs,
                "winner": max(range(len(ms)), key=lambda i: abs(ms[i]))}
