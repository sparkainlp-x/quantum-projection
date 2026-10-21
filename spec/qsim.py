"""Minimal stdlib quantum statevector simulator (2-4 qubits).

Just enough to prepare interesting states to project into the
membrane: single-qubit gates, CNOT, Bell states, GHZ, and noisy
probes. Not a quantum SDK -- a statevector scratchpad.
"""

import cmath
import math
import random

SQRT1_2 = 1.0 / math.sqrt(2.0)

H = [[SQRT1_2, SQRT1_2], [SQRT1_2, -SQRT1_2]]
X = [[0, 1], [1, 0]]


def ry(theta):
    c, s = math.cos(theta / 2), math.sin(theta / 2)
    return [[c, -s], [s, c]]


def zero(n):
    s = [0j] * (1 << n)
    s[0] = 1.0 + 0j
    return s


def normalize(v):
    nrm = math.sqrt(sum(abs(c) ** 2 for c in v))
    return [c / nrm for c in v]


def apply_1q(state, n, target, mat):
    """Apply a 2x2 gate to `target` (0 = least-significant qubit)."""
    out = [0j] * len(state)
    for i0 in range(0, len(state), 1 << (target + 1)):
        for k in range(1 << target):
            a, b = i0 + k, i0 + k + (1 << target)
            sa, sb = state[a], state[b]
            out[a] = mat[0][0] * sa + mat[0][1] * sb
            out[b] = mat[1][0] * sa + mat[1][1] * sb
    return out


def apply_cnot(state, n, control, target):
    out = list(state)
    for i in range(len(state)):
        if (i >> control) & 1:
            j = i ^ (1 << target)
            if j > i:  # swap each pair once
                out[i], out[j] = state[j], state[i]
    return out


def bell_phi_plus():
    s = apply_1q(zero(2), 2, 0, H)
    return apply_cnot(s, 2, 0, 1)


def bell_phi_minus():
    s = bell_phi_plus()
    return apply_1q(s, 2, 1, [[1, 0], [0, -1]])  # Z on qubit 1


def bell_psi_plus():
    s = bell_phi_plus()
    return apply_1q(s, 2, 1, X)


def ghz(n=3):
    s = apply_1q(zero(n), n, 0, H)
    for c in range(n - 1):
        s = apply_cnot(s, n, c, c + 1)
    return s


def noisy(state, sigma, seed=7):
    rng = random.Random(seed)
    out = [c + complex(rng.gauss(0, sigma), rng.gauss(0, sigma))
           for c in state]
    return normalize(out)


def fidelity(a, b):
    """|<a|b>|^2 for normalized statevectors."""
    return abs(sum(x.conjugate() * y for x, y in zip(a, b))) ** 2
