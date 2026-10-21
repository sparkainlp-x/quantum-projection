import math

import pytest

from quantum_projection.qsim import (H, X, apply_1q, apply_cnot, basis,
                                     bell_phi_minus, bell_phi_plus,
                                     bell_psi_minus, bell_psi_plus, fidelity,
                                     ghz, inner, noisy, normalize,
                                     plus_product, random_state, w_state, zero)

R = 2 ** -0.5


def test_gates_and_bell():
    plus = apply_1q(zero(1), 0, H)
    assert plus == pytest.approx([R, R])
    assert apply_1q(zero(1), 0, X) == pytest.approx([0, 1])
    assert bell_phi_plus() == pytest.approx([R, 0, 0, R])
    assert bell_phi_minus() == pytest.approx([R, 0, 0, -R])
    assert bell_psi_plus() == pytest.approx([0, R, R, 0])
    assert bell_psi_minus() == pytest.approx([0, R, -R, 0])


def test_bell_basis_orthonormal():
    b = [bell_phi_plus(), bell_phi_minus(), bell_psi_plus(), bell_psi_minus()]
    for i, x in enumerate(b):
        for j, y in enumerate(b):
            assert abs(inner(x, y) - (1 if i == j else 0)) < 1e-12


def test_cnot_on_high_qubits():
    s = apply_cnot(basis(3, 0b100), 2, 0)
    assert s == pytest.approx(basis(3, 0b101))


def test_named_states():
    assert ghz(3)[0] == pytest.approx(R) and ghz(3)[7] == pytest.approx(R)
    w = w_state(3)
    assert [i for i, c in enumerate(w) if c] == [1, 2, 4]
    assert plus_product(3) == pytest.approx([1 / math.sqrt(8)] * 8)


def test_noise_and_random_are_seeded_and_normalized():
    a, b = noisy(ghz(3), 0.3, seed=1), noisy(ghz(3), 0.3, seed=1)
    assert a == b and abs(sum(abs(c) ** 2 for c in a) - 1) < 1e-12
    r = random_state(2, seed=3)
    assert r == random_state(2, seed=3)
    assert abs(fidelity(r, r) - 1) < 1e-12
    assert noisy(ghz(3), 0.0, seed=5) == pytest.approx(ghz(3))


@pytest.mark.parametrize("bad", [[], [0, 0], [float("nan"), 1]])
def test_normalize_rejects(bad):
    with pytest.raises(ValueError):
        normalize(bad)


def test_bad_qubit_and_lengths():
    with pytest.raises(ValueError):
        apply_1q(zero(2), 2, H)
    with pytest.raises(ValueError):
        apply_1q([1, 0, 0], 0, H)
    with pytest.raises(ValueError):
        apply_cnot(zero(2), 1, 1)
    with pytest.raises(ValueError):
        inner([1, 0], [1, 0, 0])
    with pytest.raises(ValueError):
        noisy(zero(1), -1, seed=0)
