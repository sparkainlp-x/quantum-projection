# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)
"""Tests for the SDF synergy agents (v0.4.0). Small sizes only;
the registered measurement (seed 11, 3 systems x 8 avatars,
10 generations) runs in unified.v040_claims."""

from quantum_projection.equilibrium import DELTA_GRID, equilibrium_gap
from quantum_projection.sdf_synergy import region_coverage
from quantum_projection.synergy_agents import (
    choose_deltas_by_gap, gap_verdict, payoff_table, stability_verdict,
    synergy_run, synergy_verdict)


def _tiny_table():
    from quantum_projection.dna_avatars import healthy_membrane, make_population
    mem = healthy_membrane()
    avatars = [make_population(2, 7000 + s) for s in range(2)]
    return payoff_table(avatars, mem, coupling=0.02, generation=0,
                        n_systems=2)


def test_payoff_table_shape():
    table = _tiny_table()
    assert len(table["actions"]) == 2
    assert len(table["payoffs"]) == 3 ** 2  # 9 joint delta profiles
    for profile, pay in table["payoffs"].items():
        assert len(profile) == 2
        assert len(pay) == 2
        assert all(u >= 0 for u in pay)  # marginal contributions
        assert all(u <= 1.0 for u in pay)
    for syn in table["synergies"].values():
        assert 0.0 <= syn <= 1.0 + 1e-12


def test_payoff_table_deterministic():
    t1 = _tiny_table()
    t2 = _tiny_table()
    assert t1["payoffs"] == t2["payoffs"]
    assert t1["synergies"] == t2["synergies"]


def test_gap_descent_never_worse_than_zero():
    table = _tiny_table()
    actions = table["actions"]
    chosen, gap = choose_deltas_by_gap(actions, table["payoffs"])
    zero = (0.0, 0.0)
    assert gap <= equilibrium_gap(actions, table["payoffs"], zero) + 1e-12
    assert all(d in DELTA_GRID for d in chosen)
    # The chosen profile's gap is the minimum over the descent path;
    # it cannot exceed the gap of the starting profile.
    assert gap >= 0.0


def test_synergy_run_tiny_structure():
    res = synergy_run(n_systems=2, n_avatars=2, generations=2,
                      coupling=0.02, seed=7)
    assert len(res["records"]) == 3
    assert len(res["tables"]) == 2
    for rec in res["records"][:-1]:
        assert rec["deltas"] is not None
        assert rec["gap"] is not None
        assert rec["gap_zero"] is not None
        assert 0.0 <= rec["synergy"] <= 1.0 + 1e-12
        assert rec["gap"] <= rec["gap_zero"] + 1e-12  # descent property
    assert res["records"][-1]["deltas"] is None  # final: no step
    # Entropy diagnostic is present but never optimized.
    assert all("entropy_bits" in r for r in res["records"])


def test_synergy_run_deterministic():
    r1 = synergy_run(n_systems=2, n_avatars=2, generations=2,
                     coupling=0.02, seed=7)
    r2 = synergy_run(n_systems=2, n_avatars=2, generations=2,
                     coupling=0.02, seed=7)
    assert [r["deltas"] for r in r1["records"]] == \
        [r["deltas"] for r in r2["records"]]
    assert [r["gap"] for r in r1["records"]] == \
        [r["gap"] for r in r2["records"]]


def test_verdicts_return_bools_on_tiny_run():
    from quantum_projection.solar_systems import run_solar_systems
    run = synergy_run(n_systems=2, n_avatars=2, generations=2,
                      coupling=0.02, seed=7)
    control = run_solar_systems(n_systems=2, n_avatars=2, generations=2,
                                coupling=0.02, seed=7)
    passed, details = gap_verdict(run)
    assert isinstance(passed, bool)
    assert "first_nontrivial" in details
    passed, details = synergy_verdict(run, control["records"])
    assert isinstance(passed, bool)
    assert "mean_synergy_agent" in details
    passed, details = stability_verdict(run)
    assert isinstance(passed, bool)
    assert details["label"] in ("trap", "efficient", "other")
    assert "landed_profile" in details
