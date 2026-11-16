# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)
"""Tests for the vendored equilibrium checker (v0.4.0). The game
examples are the source package's own README demos."""

import pytest

from quantum_projection.equilibrium import (DELTA_GRID, analyze_profile,
                                           audit_table, equilibrium_gap,
                                           find_pure_equilibria,
                                           is_epsilon_equilibrium,
                                           validate_game)


def test_prisoners_dilemma():
    actions = (("cooperate", "defect"), ("cooperate", "defect"))
    payoffs = {
        ("cooperate", "cooperate"): (3, 3),
        ("cooperate", "defect"): (0, 5),
        ("defect", "cooperate"): (5, 0),
        ("defect", "defect"): (1, 1),
    }
    eqs = find_pure_equilibria(actions, payoffs)
    assert [e["profile"] for e in eqs] == [["defect", "defect"]]
    audit = analyze_profile(actions, payoffs, ("cooperate", "cooperate"))
    assert [p["deviation_gain"] for p in audit["players"]] == [2, 2]
    assert audit["max_deviation_gain"] == 2


def test_coordination_game_two_equilibria():
    actions = (("left", "right"), ("left", "right"))
    payoffs = {
        ("left", "left"): (2, 2),
        ("left", "right"): (0, 0),
        ("right", "left"): (0, 0),
        ("right", "right"): (1, 1),
    }
    eqs = find_pure_equilibria(actions, payoffs)
    assert sorted(tuple(e["profile"]) for e in eqs) == [
        ("left", "left"), ("right", "right")]
    # The (right, right) equilibrium is the safe-but-inefficient one:
    # it is an equilibrium, but its payoffs are below (left, left).
    assert is_epsilon_equilibrium(actions, payoffs, ("right", "right"), 0.0)


def test_matching_pennies_no_pure_equilibrium():
    actions = (("h", "t"), ("h", "t"))
    payoffs = {
        ("h", "h"): (1, -1),
        ("h", "t"): (-1, 1),
        ("t", "h"): (-1, 1),
        ("t", "t"): (1, -1),
    }
    assert find_pure_equilibria(actions, payoffs) == []
    # With epsilon = 2 every profile qualifies.
    assert len(find_pure_equilibria(actions, payoffs, epsilon=2.0)) == 4


def test_equilibrium_gap_zero_at_equilibrium():
    actions = (("a", "b"), ("a", "b"))
    payoffs = {
        ("a", "a"): (2, 2),
        ("a", "b"): (0, 0),
        ("b", "a"): (0, 0),
        ("b", "b"): (1, 1),
    }
    assert equilibrium_gap(actions, payoffs, ("a", "a")) == 0
    assert equilibrium_gap(actions, payoffs, ("a", "b")) == 2
    assert is_epsilon_equilibrium(actions, payoffs, ("a", "a"), 0.0)
    assert not is_epsilon_equilibrium(actions, payoffs, ("a", "b"), 0.0)
    assert is_epsilon_equilibrium(actions, payoffs, ("a", "b"), 2.0)


def test_audit_table():
    actions = (("a", "b"), ("a", "b"))
    payoffs = {
        ("a", "a"): (2, 2),
        ("a", "b"): (0, 0),
        ("b", "a"): (0, 0),
        ("b", "b"): (1, 1),
    }
    audit = audit_table(actions, payoffs, epsilon=0.0)
    assert audit["min_gap"] == 0
    assert audit["min_gap_profile"] == ["a", "a"]
    assert audit["n_equilibria"] == 2
    assert audit["gaps"][("a", "b")] == 2


def test_validate_game_rejects():
    actions = (("a", "b"), ("a", "b"))
    with pytest.raises(ValueError):
        validate_game(actions, {("a", "a"): (1, 1)})  # incomplete table
    with pytest.raises(ValueError):
        validate_game(actions, {("a", "a"): (1, 1), ("a", "b"): (1, 1),
                                ("b", "a"): (1, 1), ("b", "b"): (1,)})
    with pytest.raises(ValueError):
        find_pure_equilibria(actions, {
            ("a", "a"): (1, 1), ("a", "b"): (1, 1),
            ("b", "a"): (1, 1), ("b", "b"): (1, 1)}, epsilon=-1)


def test_delta_grid():
    assert DELTA_GRID == (-0.05, 0.0, 0.05)
