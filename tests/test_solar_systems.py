# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)
"""Tests for the multi-solar-system module (v0.3.0). Fast sizes;
the registered measurement (3 systems, 8 avatars, 10 gens,
seed 11) runs in unified.v030_claims, not here."""

import math

from quantum_projection.dna_avatars import (avatar_state, encode_sequence,
                                            index_to_sequence,
                                            sequence_index)
from quantum_projection.solar_systems import (
    avatar_state_dict, contagion_verdict, couple_systems,
    make_shocked_population, run_solar_systems, state_dict_to_avatar)


def test_sequence_index_matches_encoding():
    for seq in ("AATTAA", "ATATAT", "CCCCCC", "GGGGGG", "TTTTTT", "ACGTAC"):
        v = encode_sequence(seq)
        idx = sequence_index(seq)
        assert abs(v[idx] - 1.0) < 1e-12
        assert sum(abs(x) for x in v) == 1.0
        assert index_to_sequence(idx) == seq


def test_avatar_state_dict_matches_dense():
    from quantum_projection.dna_avatars import make_population
    av = make_population(1, 11)[0]
    dense = avatar_state(av["sequences"], av["weights"])
    sparse = avatar_state_dict(av)
    for i, amp in sparse.items():
        assert abs(dense[i] - amp) < 1e-12
    assert abs(sum(abs(v) ** 2 for v in sparse.values()) - 1.0) < 1e-12


def test_state_dict_round_trip_preserves_d():
    from quantum_projection.dna_avatars import (healthy_membrane,
                                                make_population,
                                                self_knowing)
    mem = healthy_membrane()
    av = make_population(1, 11)[0]
    d0 = self_knowing(avatar_state(av["sequences"], av["weights"]), mem)
    av2 = state_dict_to_avatar(avatar_state_dict(av))
    d1 = self_knowing(avatar_state(av2["sequences"], av2["weights"]), mem)
    assert abs(d0 - d1) < 1e-9
    assert abs(sum(w * w for w in av2["weights"]) - 1.0) < 1e-12


def test_couple_single_system_is_identity():
    from quantum_projection.dna_avatars import make_population
    pops = [make_population(2, 11)]
    assert couple_systems(pops, 0.02) == pops


def test_couple_zero_kappa_is_identity():
    from quantum_projection.dna_avatars import make_population
    pops = [make_population(2, 11), make_population(2, 12)]
    assert couple_systems(pops, 0.0) == pops


def test_couple_mixes_and_keeps_valid_avatars():
    from quantum_projection.dna_avatars import make_population
    pops = [make_population(2, 11), make_population(2, 12)]
    out = couple_systems(pops, 0.02)
    assert len(out) == 2
    for system in out:
        for av in system:
            assert len(av["sequences"]) == len(av["weights"])
            assert abs(sum(w * w for w in av["weights"]) - 1.0) < 1e-9
            assert all(len(s) == 6 for s in av["sequences"])


def test_run_solar_systems_small():
    res = run_solar_systems(n_systems=2, n_avatars=2, generations=3,
                            seed=7)
    assert len(res["records"]) == 4
    for recs in res["records"]:
        assert len(recs) == 2
        for r in recs:
            assert 0.0 <= r["mean_discord"] <= 1.0
            assert r["diversity"] >= 1
    first = res["records"][0][0]["mean_discord"]
    last = res["records"][-1][0]["mean_discord"]
    assert last < first  # healing happens in every system


def test_shocked_population_heals_slower():
    res = run_solar_systems(n_systems=2, n_avatars=2, generations=3,
                            seed=7, shocked_system=0)
    assert res["records"][0][0]["mean_discord"] > 0.99
    assert res["records"][-1][0]["mean_discord"] > res["records"][-1][1]["mean_discord"]


def test_contagion_verdict_structure():
    c = run_solar_systems(n_systems=3, n_avatars=4, generations=5,
                          seed=7)
    u = run_solar_systems(n_systems=3, n_avatars=4, generations=5,
                          seed=7, coupling=0.0)
    sc = run_solar_systems(n_systems=3, n_avatars=4, generations=5,
                           seed=7, shocked_system=0)
    su = run_solar_systems(n_systems=3, n_avatars=4, generations=5,
                           seed=7, coupling=0.0, shocked_system=0)
    passed, d = contagion_verdict(c, u, sc, su)
    assert isinstance(passed, bool)
    for key in ("healing_ok", "support_ok", "convergence_ok",
                "no_harm_ok", "support_gain", "gap_coupled",
                "gap_uncoupled"):
        assert key in d
    assert d["healing_ok"] is True
    assert d["support_gain"] > 0  # coupling helps the shocked system


def test_shocked_population_valid():
    pops = make_shocked_population(2, 11)
    assert len(pops) == 2
    for av in pops:
        assert av["weights"][0] == 0.01
        assert all(len(s) == 6 for s in av["sequences"])
