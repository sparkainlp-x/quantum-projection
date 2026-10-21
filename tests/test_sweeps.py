import pytest

from quantum_projection.__main__ import main
from quantum_projection.sweeps import bell_sweep, ghz_sweep, nonorthogonal_sweep


@pytest.fixture(scope="module")
def bell():
    return bell_sweep()


def test_bell_sweep_numbers(bell):
    t = bell["table"]
    for n in ("Phi+", "Phi-", "Psi+"):
        assert t[(n, 0.1)]["accuracy"] == 1.0
        assert t[(n, 0.25)]["accuracy"] >= 0.95
        assert t[(n, 1.0)]["accuracy"] < 0.7
    # Unstored Psi- is orthogonal to every stored pattern: assignment is noise.
    assert max(t[("Psi- (not stored)", 0.1)]["counts"]) < 100
    assert bell["max_born_vs_fidelity_gap"] < 1e-12
    assert bell["max_one_vs_25_step_gap"] < 1e-12
    assert sum(bell["controls_random"]["counts"]) == 200


def test_nonorthogonal_sweep_numbers():
    r = nonorthogonal_sweep()
    assert abs(r["pattern_overlap"] - 2 ** -0.5) < 1e-12
    assert r["table"][("|00>", 0.1)]["accuracy"] == 1.0
    assert r["table"][("|+0>", 1.0)]["accuracy"] < 0.7
    assert r["iteration_from_clean_00"][-1]["fid_to_dominant_eigvec"] > 1 - 1e-12
    assert r["recall25_flips_at_sigma_0.25"] > 0.5


def test_ghz_sweep_numbers_and_collision():
    r = ghz_sweep()
    assert r["table"][("GHZ", 0.1)]["accuracy"] >= 0.95
    assert r["table"][("|001> (not stored)", 0.1)]["counts"][2] == 200
    assert r["table"][("GHZ", 1.0)]["accuracy"] < 0.5
    alt = ghz_sweep(seeds=20, qubit=2)
    assert alt["table"][("GHZ", 0.1)]["accuracy"] >= 0.9


def test_sweeps_deterministic():
    assert ghz_sweep(seeds=10) == ghz_sweep(seeds=10)


def test_cli(capsys):
    assert main(["--seeds", "5"]) == 0
    out = capsys.readouterr().out
    assert "SYNTHETIC" in out and "Verified" not in out
    with pytest.raises(SystemExit):
        main(["--seeds", "0"])
