# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)
"""Tests for the eureka agent (v0.3.0). Fast sizes; the registered
measurement (seed 11) runs in unified.v030_claims, not here."""

import math

from quantum_projection.eureka_agent import (
    _choose_deltas, agent_run, agent_verdict, concurrence_pure,
    empathy_entropy, love_of_d)


def test_concurrence_pure():
    s = 1.0 / math.sqrt(2.0)
    assert abs(concurrence_pure(s, 0, 0, s) - 1.0) < 1e-12  # Bell pair
    assert concurrence_pure(1, 0, 0, 0) == 0.0  # product state
    assert abs(concurrence_pure(0.6, 0, 0, 0.8) - 2 * 0.6 * 0.8) < 1e-12


def test_love_of_d():
    assert love_of_d(0.0) == 0.0
    assert abs(love_of_d(0.5) - 1.0) < 1e-12  # peaks at half-known
    assert love_of_d(1.0) == 0.0
    assert love_of_d(0.007) < love_of_d(0.5)
    # Cross-check against the vendored pure-state formula.
    for d in (0.0, 0.1, 0.5, 0.9, 1.0):
        assert abs(love_of_d(d) - concurrence_pure(
            math.sqrt(d), 0, 0, math.sqrt(1 - d))) < 1e-12


def test_empathy_entropy():
    assert abs(empathy_entropy([1.0] * 8)["entropy_bits"] - 3.0) < 1e-12
    assert empathy_entropy([1.0] + [0.0] * 7)["entropy_bits"] == 0.0
    assert empathy_entropy([0.0] * 8)["entropy_bits"] == 0.0
    ent = empathy_entropy([1.0, 1.0])
    assert abs(ent["normalized"] - 1.0) < 1e-12
    assert ent["max_bits"] == 1.0


def test_agent_run_tiny():
    res = agent_run(n_systems=2, n_avatars=2, generations=2, seed=7)
    assert len(res["records"]) == 3
    assert len(res["events"]) == 2
    for r in res["records"][:-1]:
        assert r["deltas"] is not None
        assert all(d in (-0.05, 0.0, 0.05) for d in r["deltas"])
        assert 0.0 <= r["entropy_bits"] <= math.log2(4) + 1e-9
    for e in res["events"]:
        assert 0.0 <= e["p"] <= 1.0
        assert e["truth"] in (0, 1)


def test_choose_deltas_in_grid():
    from quantum_projection.dna_avatars import healthy_membrane, make_population
    import random
    mem = healthy_membrane()
    avatars = [make_population(2, 7000 + s) for s in range(2)]
    rngs = [random.Random(70000 + s) for s in range(2)]
    deltas = _choose_deltas(avatars, mem, rngs, 0.02, 0, 2)
    assert len(deltas) == 2
    assert all(d in (-0.05, 0.0, 0.05) for d in deltas)


def test_agent_verdict_structure():
    agent = agent_run(n_systems=2, n_avatars=2, generations=2, seed=7)
    from quantum_projection.solar_systems import run_solar_systems
    control = run_solar_systems(n_systems=2, n_avatars=2, generations=2,
                                seed=7, coupling=0.02)
    passed, d = agent_verdict(agent, control)
    assert isinstance(passed, bool)
    for key in ("mean_entropy_agent", "mean_entropy_control",
                "entropy_gain", "entropy_gain_required",
                "mean_discord_final_agent", "discord_cost",
                "total_love_by_gen_agent"):
        assert key in d
    assert d["entropy_gain_required"] == 0.02
