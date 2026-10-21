import cmath

import pytest

from quantum_projection import (HolographicMembrane, KetBraPair, coarse_grain,
                                fidelity, ghz, noisy, normalize, random_state,
                                w_state, zero)
from quantum_projection.qsim import (H, apply_1q, basis, bell_phi_minus,
                                     bell_phi_plus, bell_psi_plus, inner)

BELL3 = [bell_phi_plus(), bell_phi_minus(), bell_psi_plus()]


def test_exact_projection_on_stored_state():
    r = HolographicMembrane(BELL3).project(bell_phi_minus())
    assert r["winner"] == 1
    assert abs(r["overlaps"][1] - 1) < 1e-12
    assert abs(r["overlaps"][0]) < 1e-12 and abs(sum(r["probs"]) - 1) < 1e-12


@pytest.mark.parametrize("seed", range(20))
def test_orthonormal_w_is_projector_one_step_fixed_point(seed):
    mem = HolographicMembrane(BELL3)
    probe = noisy(bell_phi_plus(), 0.4, seed=seed)
    one, _, _ = mem.recall(probe, steps=1)
    many, _, traj = mem.recall(probe, steps=25)
    assert max(abs(a - b) for a, b in zip(one, many)) < 1e-12
    assert len(set(traj)) == 1
    w = mem.project(probe)["probs"]
    for mu, p in enumerate(mem.patterns):
        assert abs(fidelity(one, p) - w[mu]) < 1e-12   # fidelity == Born weight
    # W^2 = W on an arbitrary vector
    v = random_state(2, seed)
    w1 = mem.apply_w(v)
    assert max(abs(a - b) for a, b in zip(mem.apply_w(w1), w1)) < 1e-12


def test_nonorthogonal_recall_drifts_to_dominant_eigenvector():
    p0, p1 = zero(2), normalize(apply_1q(zero(2), 1, H))
    mem = HolographicMembrane([p0, p1])
    dom = normalize([a + b for a, b in zip(p0, p1)])
    a1, w1, _ = mem.recall(p0, steps=1)
    a25, _, _ = mem.recall(p0, steps=25)
    assert w1 == 0 and abs(fidelity(a1, p0) - 0.9) < 1e-12
    assert fidelity(a25, dom) > 1 - 1e-12
    assert abs(fidelity(a25, p0) - fidelity(a25, p1)) < 1e-9  # no longer separates them


@pytest.mark.parametrize("seed", range(10))
def test_ket_bra_matches_complex_overlaps_with_phase(seed):
    kets = [random_state(2, 100 + seed), random_state(2, 200 + seed),
            [c * cmath.exp(0.7j) for c in bell_phi_plus()]]
    probe = random_state(2, 300 + seed)
    r1 = KetBraPair(kets).project(probe)
    r2 = HolographicMembrane(kets).project(probe)
    for a, b in zip(r1["overlaps"], r2["overlaps"]):
        assert abs(a - b) < 1e-12          # complex values, phase included
        assert abs(a) > 1e-6
    assert r1["probs"] == pytest.approx(r2["probs"], abs=1e-12)


def test_overlap_phase_is_conjugate_linear():
    k = bell_phi_plus()
    probe = [c * cmath.exp(1.1j) for c in k]
    m = HolographicMembrane([k]).overlaps(probe)[0]
    assert abs(m - cmath.exp(1.1j)) < 1e-12
    m2 = HolographicMembrane([probe]).overlaps(k)[0]
    assert abs(m2 - cmath.exp(-1.1j)) < 1e-12


def _plus_on(state, q):
    s = apply_1q(state, q, H)       # <+|_q is row 0 of H
    bit = 1 << q
    low = bit - 1
    return normalize([s[((j & ~low) << 1) | (j & low)] for j in range(len(s) // 2)])


@pytest.mark.parametrize("q", [0, 1, 2])
@pytest.mark.parametrize("seed", range(5))
def test_coarse_grain_equals_projecting_qubit_onto_plus(q, seed):
    s = random_state(3, seed)
    cg = coarse_grain(s, q)
    assert len(cg) == 4
    assert abs(sum(abs(c) ** 2 for c in cg) - 1) < 1e-12
    assert max(abs(a - b) for a, b in zip(cg, _plus_on(s, q))) < 1e-12


def test_coarse_grain_default_is_qubit0_and_loses_information():
    s = random_state(3, 9)
    assert coarse_grain(s) == coarse_grain(s, 0)
    assert coarse_grain(zero(3)) == pytest.approx(coarse_grain(basis(3, 1)))
    assert coarse_grain(ghz(3)) == pytest.approx(bell_phi_plus())
    minus0 = [1 / 2 ** 0.5, -1 / 2 ** 0.5, 0, 0]
    with pytest.raises(ValueError):
        coarse_grain(minus0)
    with pytest.raises(ValueError):
        coarse_grain(ghz(3), 3)
    with pytest.raises(ValueError):
        coarse_grain([1.0])


def test_input_validation():
    with pytest.raises(ValueError):
        HolographicMembrane([])
    with pytest.raises(ValueError):
        HolographicMembrane([zero(2), zero(3)])
    with pytest.raises(ValueError):
        HolographicMembrane([[0, 0]])
    mem = HolographicMembrane([zero(2)])
    with pytest.raises(ValueError):
        mem.project(zero(3))
    with pytest.raises(ValueError):
        mem.project([0, 0, 0, 0])
    with pytest.raises(ValueError):
        mem.recall(basis(2, 3))            # orthogonal to every pattern
    with pytest.raises(ValueError):
        mem.recall(zero(2), steps=0)
    with pytest.raises(ValueError):
        KetBraPair([])


def test_orthogonal_probe_gets_zero_weights():
    r = HolographicMembrane([zero(2)]).project(basis(2, 3))
    assert r["probs"] == [0.0]
    assert abs(inner(zero(2), basis(2, 3))) == 0
