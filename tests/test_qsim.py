import math

import pytest

from quantum_projection.qsim import (H, X, apply_1q, apply_cnot, apply_rzz, basis,
                                     bell_phi_minus, bell_phi_plus,
                                     bell_psi_minus, bell_psi_plus, fidelity,
                                     ghz, inner, noisy, normalize,
                                     plus_product, random_state, rz, w_state,
                                     zero)

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


def test_cnot_asymmetric_basis_indices():
    assert apply_cnot(basis(3, 0b001), 0, 2) == basis(3, 0b101)
    assert apply_cnot(basis(3, 0b100), 2, 0) == basis(3, 0b101)
    assert apply_cnot(basis(3, 0b100), 0, 2) == basis(3, 0b100)


def _max_amplitude_error(actual, expected):
    return max(abs(a - b) for a, b in zip(actual, expected))


def test_rzz_matches_cnot_rz_cnot_for_ordered_pairs():
    max_error = 0.0
    cases = 0
    theta = 0.731
    for n in range(2, 7):
        for control in range(n):
            for target in range(n):
                if control == target:
                    continue
                states = [basis(n, i) for i in range(1 << n)]
                states.extend(random_state(n, 1000 * n + seed) for seed in range(3))
                for state in states:
                    expected = apply_cnot(state, control, target)
                    expected = apply_1q(expected, target, rz(theta))
                    expected = apply_cnot(expected, control, target)
                    actual = apply_rzz(state, control, target, theta)
                    error = _max_amplitude_error(actual, expected)
                    max_error = max(max_error, error)
                    cases += 1
                    assert error < 1e-12, (
                        f"n={n}, control={control}, target={target}, "
                        f"case={cases}, max amplitude error={error:.3e}"
                    )
    assert cases == 3018


def test_rzz_preserves_norm_inverse_composition_and_diagonal_probabilities():
    state = random_state(4, seed=91)
    theta, phi = 0.31, -1.27
    rotated = apply_rzz(state, 1, 3, theta)
    assert abs(sum(abs(c) ** 2 for c in rotated) - 1) < 1e-12
    assert apply_rzz(rotated, 1, 3, -theta) == pytest.approx(state, abs=1e-12)
    composed = apply_rzz(apply_rzz(state, 1, 3, theta), 1, 3, phi)
    combined = apply_rzz(state, 1, 3, theta + phi)
    assert composed == pytest.approx(combined, abs=1e-12)
    swapped = apply_rzz(state, 3, 1, theta)
    assert swapped == pytest.approx(rotated, abs=1e-12)
    assert [abs(c) ** 2 for c in rotated] == pytest.approx(
        [abs(c) ** 2 for c in state], abs=1e-12
    )


@pytest.mark.parametrize(
    ("theta", "diagonal"),
    [
        (0.0, [1, 1, 1, 1]),
        (math.pi, [-1j, 1j, 1j, -1j]),
        (2 * math.pi, [-1, -1, -1, -1]),
        (4 * math.pi, [1, 1, 1, 1]),
    ],
)
def test_rzz_exact_special_angle_matrices(theta, diagonal):
    columns = [apply_rzz(basis(2, i), 0, 1, theta) for i in range(4)]
    matrix = [[columns[column][row] for column in range(4)] for row in range(4)]
    expected = [[diagonal[row] if row == column else 0j
                 for column in range(4)] for row in range(4)]
    error = max(abs(matrix[row][column] - expected[row][column])
                for row in range(4) for column in range(4))
    assert error < 1e-12, f"maximum matrix-entry error={error:.3e}"


def test_exact_amplitudes_are_distinct_from_global_phase_equivalence():
    state = random_state(2, seed=7)
    twice = apply_rzz(state, 0, 1, 2 * math.pi)
    assert twice == pytest.approx([-c for c in state], abs=1e-12)
    assert twice != state
    assert fidelity(twice, state) == pytest.approx(1.0, abs=1e-12)
    assert apply_rzz(state, 0, 1, 4 * math.pi) == pytest.approx(state, abs=1e-12)


def test_rzz_interference_after_hadamards():
    theta = 0.83
    state = zero(2)
    state = apply_1q(state, 0, H)
    state = apply_1q(state, 1, H)
    state = apply_rzz(state, 0, 1, theta)
    state = apply_1q(state, 0, H)
    state = apply_1q(state, 1, H)
    expected = [math.cos(theta / 2), 0j, 0j, -1j * math.sin(theta / 2)]
    error = _max_amplitude_error(state, expected)
    assert error < 1e-12, f"maximum amplitude error={error:.3e}"


@pytest.mark.parametrize("theta", [True, False, "0.5", float("nan"),
                                   float("inf"), -float("inf"), 10 ** 400])
def test_rz_rejects_invalid_angles(theta):
    with pytest.raises(ValueError):
        rz(theta)


@pytest.mark.parametrize("state", [[], [1, 2, 3], [1, float("nan"), 0, 0],
                                   [1, 0, float("inf"), 0], ["1", 0, 0, 0],
                                   [True, 0, 0, 0]])
def test_rzz_rejects_invalid_statevectors(state):
    with pytest.raises(ValueError):
        apply_rzz(state, 0, 1, 0.2)


@pytest.mark.parametrize(("q0", "q1"), [(0, 0), (0, 2), (-1, 1), (0.0, 1),
                                        (True, 1), ("0", 1)])
def test_rzz_rejects_invalid_qubits(q0, q1):
    with pytest.raises(ValueError):
        apply_rzz(zero(2), q0, q1, 0.2)


def test_rzz_accepts_unnormalized_vectors_without_mutating_them():
    state = [1 + 2j, -3j, 4, -5 + 6j]
    original = state[:]
    rotated = apply_rzz(state, 0, 1, 0.42)
    assert state == original
    assert sum(abs(c) ** 2 for c in rotated) == pytest.approx(
        sum(abs(c) ** 2 for c in state), abs=1e-12
    )
    assert rotated != state


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
