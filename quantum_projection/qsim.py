"""Minimal standard-library statevector scratchpad (a few qubits).

SYNTHETIC. Classical emulation of quantum kinematics only: an n-qubit
state costs 2**n complex numbers, so there is no speedup. Qubit 0 is
the least-significant bit of the basis index.
"""

import cmath
import math
import random

SQRT1_2 = 1.0 / math.sqrt(2.0)

H = ((SQRT1_2, SQRT1_2), (SQRT1_2, -SQRT1_2))
X = ((0.0, 1.0), (1.0, 0.0))
Z = ((1.0, 0.0), (0.0, -1.0))


def _num_qubits(state):
    size = len(state)
    if size < 1 or size & (size - 1):
        raise ValueError(f"state length must be a power of two, got {size}")
    return size.bit_length() - 1


def _check_qubit(state, q):
    n = _num_qubits(state)
    if not isinstance(q, int) or isinstance(q, bool) or not 0 <= q < n:
        raise ValueError(f"qubit index {q!r} out of range for {n} qubits")


def norm(v):
    return math.sqrt(sum(abs(c) ** 2 for c in v))


def normalize(v):
    """Return v / ||v||. Raises ValueError for empty, zero or non-finite input."""
    v = [complex(c) for c in v]
    if not v:
        raise ValueError("cannot normalize an empty vector")
    if not all(cmath.isfinite(c) for c in v):
        raise ValueError("vector has non-finite entries")
    nrm = norm(v)
    if nrm == 0.0:
        raise ValueError("cannot normalize a zero-norm vector")
    return [c / nrm for c in v]


def inner(a, b):
    """<a|b> (conjugate-linear in a)."""
    if len(a) != len(b):
        raise ValueError(f"length mismatch: {len(a)} vs {len(b)}")
    return sum(x.conjugate() * y for x, y in zip(a, b))


def fidelity(a, b):
    """|<a|b>|^2 for normalized statevectors."""
    return abs(inner(a, b)) ** 2


def basis(n, index=0):
    if n < 1 or not 0 <= index < (1 << n):
        raise ValueError("bad basis state")
    s = [0j] * (1 << n)
    s[index] = 1.0 + 0j
    return s


def zero(n):
    return basis(n, 0)


def apply_1q(state, target, mat):
    """Apply a 2x2 matrix to qubit `target` (0 = least-significant)."""
    _check_qubit(state, target)
    out = [0j] * len(state)
    step = 1 << target
    for i in range(len(state)):
        if not i & step:
            a, b = i, i | step
            sa, sb = state[a], state[b]
            out[a] = mat[0][0] * sa + mat[0][1] * sb
            out[b] = mat[1][0] * sa + mat[1][1] * sb
    return out


def apply_cnot(state, control, target):
    _check_qubit(state, control)
    _check_qubit(state, target)
    if control == target:
        raise ValueError("control and target must differ")
    out = list(state)
    for i in range(len(state)):
        if (i >> control) & 1 and not (i >> target) & 1:
            j = i | (1 << target)
            out[i], out[j] = state[j], state[i]
    return out


def bell_phi_plus():
    return apply_cnot(apply_1q(zero(2), 0, H), 0, 1)


def bell_phi_minus():
    return apply_1q(bell_phi_plus(), 1, Z)


def bell_psi_plus():
    return apply_1q(bell_phi_plus(), 1, X)


def bell_psi_minus():
    return apply_1q(bell_psi_plus(), 1, Z)


def ghz(n=3):
    s = apply_1q(zero(n), 0, H)
    for c in range(n - 1):
        s = apply_cnot(s, c, c + 1)
    return s


def w_state(n=3):
    s = [0j] * (1 << n)
    for q in range(n):
        s[1 << q] = 1.0 / math.sqrt(n)
    return s


def plus_product(n):
    s = zero(n)
    for q in range(n):
        s = apply_1q(s, q, H)
    return s


def noisy(state, sigma, seed):
    """Add i.i.d. complex Gaussian noise (std sigma per real part) and renormalize."""
    if sigma < 0:
        raise ValueError("sigma must be >= 0")
    rng = random.Random(seed)
    return normalize([c + complex(rng.gauss(0, sigma), rng.gauss(0, sigma))
                      for c in state])


def random_state(n, seed):
    """Haar-random n-qubit state (normalized complex Gaussian vector)."""
    rng = random.Random(seed)
    return normalize([complex(rng.gauss(0, 1), rng.gauss(0, 1))
                      for _ in range(1 << n)])
