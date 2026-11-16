# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)
"""The equilibrium principle, vendored into quantum-projection.

PROVENANCE. The checker below (validate_game, analyze_profile,
find_pure_equilibria and their helpers) is vendored, essentially
unchanged, from Jean's own package:

    finite-game-equilibria, v0.1.0
    https://github.com/sparkainlp-x/finite-game-equilibria
    DOI 10.5281/zenodo.23530287 (concept 10.5281/zenodo.23530286)
    vendored from commit 11698948b54056da98aaa3417b6a7062d801faa6
    (finite_game_equilibria/core.py)

The game it checks here is the SDF-synergy game of
sdf_synergy.py: the players are the solar systems, each player's
actions are the Yin calibrator values delta in [-0.05, 0, +0.05],
and each player's payoff is its system's marginal contribution
to the joint inside-coverage of the self-known region
(leave-one-out). The checker is also the audit used by
oes-coordination-lab (v0.1.0, DOI 10.5281/zenodo.23530289),
where the same two functions audit a synthetic 3-agent
coordination game and name the coordination trap: in the shared
regime there are two pure equilibria, all-switch (efficient)
and all-stay-local (safe but inefficient).

SYNTHETIC. Classical emulation only. A Nash equilibrium here is
a property of the explicitly supplied payoff table: a profile is
an (epsilon-)equilibrium when no player gains more than epsilon
by unilaterally deviating. It says nothing about mixed
equilibria, learning dynamics, real markets, or real systems.
The equilibrium gap -- the maximum profitable unilateral
deviation gain across players -- is the v0.4.0 optimization
variable: it is 0 at equilibrium and positive everywhere else,
a real zero and a real direction. It replaces empathy entropy
as the agent's objective, because claim (vi) FAILED: empathy
entropy was already saturated at 99.998% of its log2(24)
ceiling, so there was nothing left to maximize.
"""

from collections.abc import Hashable, Mapping, Sequence
from itertools import product
from math import isfinite

__all__ = ["validate_game", "analyze_profile", "find_pure_equilibria",
           "equilibrium_gap", "is_epsilon_equilibrium", "audit_table",
           "DELTA_GRID"]

# The game: one Yin calibrator value per solar system.
DELTA_GRID = (-0.05, 0.0, 0.05)


# ------------------------------------------------------------------
# Vendored checker (finite-game-equilibria v0.1.0, core.py).
# ------------------------------------------------------------------

def _is_number(x):
    return not isinstance(x, bool) and isinstance(x, (int, float)) and isfinite(x)


def _is_sequence(x):
    return isinstance(x, Sequence) and not isinstance(x, (str, bytes, bytearray))


def validate_game(actions, payoffs):
    """Validate action sets and a complete joint-action payoff table.

    actions: a sequence (not a string) with one action sequence per player.
    payoffs: a mapping from every joint-action tuple to a sequence of one
    finite number per player. Returns the tuple of all profiles.
    """
    if not _is_sequence(actions) or not actions:
        raise ValueError("actions must be a non-empty sequence of per-player action sequences.")

    for player, choices in enumerate(actions):
        if not _is_sequence(choices):
            raise ValueError(f"Player {player}'s actions must be a sequence (not a string).")
        if not choices:
            raise ValueError("Each player needs at least one action.")
        for action in choices:
            if not isinstance(action, Hashable):
                raise ValueError(f"Player {player} has an unhashable action name: {action!r}.")
            try:
                hash(action)
            except TypeError:
                raise ValueError(f"Player {player} has an unhashable action name: {action!r}.") from None
        if len(set(choices)) != len(choices):
            raise ValueError("Action names must be distinct per player.")

    if not isinstance(payoffs, Mapping):
        raise ValueError("payoffs must be a mapping from profile tuples to utilities.")

    profiles = tuple(product(*actions))

    if set(payoffs) != set(profiles):
        raise ValueError("Payoffs must cover every joint-action profile exactly.")

    for profile in profiles:
        utilities = payoffs[profile]
        if not _is_sequence(utilities):
            raise ValueError(f"Utilities for {profile!r} must be a sequence of numbers.")
        if len(utilities) != len(actions):
            raise ValueError("Provide one utility per player.")
        if not all(_is_number(u) for u in utilities):
            raise ValueError("Utilities must be finite numbers.")

    return profiles


def _check_profile(actions, profile):
    if not _is_sequence(profile):
        raise ValueError("profile must be a sequence of one action per player (not a string).")
    profile = tuple(profile)
    if len(profile) != len(actions):
        raise ValueError(f"profile has {len(profile)} actions; the game has {len(actions)} players.")
    for player, (action, choices) in enumerate(zip(profile, actions)):
        try:
            ok = action in choices
        except TypeError:
            ok = False
        if not ok:
            raise ValueError(f"{action!r} is not an action of player {player}.")
    return profile


def _audit_profile(actions, payoffs, profile):
    """Check deviations while holding every other player fixed."""
    baseline = payoffs[profile]
    player_results = []

    for player, alternatives in enumerate(actions):
        best_action = profile[player]
        best_utility = baseline[player]

        # Includes the current action, so the gain cannot be negative.
        # Ties keep the current action (first strict improvement wins).
        for alternative in alternatives:
            deviated = list(profile)
            deviated[player] = alternative
            utility = payoffs[tuple(deviated)][player]
            if utility > best_utility:
                best_action = alternative
                best_utility = utility

        player_results.append({
            "player": player,
            "current_action": profile[player],
            "current_utility": baseline[player],
            "best_response_action": best_action,
            "best_response_utility": best_utility,
            "deviation_gain": best_utility - baseline[player],
        })

    return {
        "profile": list(profile),
        "players": player_results,
        "max_deviation_gain": max(r["deviation_gain"] for r in player_results),
    }


def analyze_profile(actions, payoffs, profile):
    """Return each player's best unilateral deviation from profile."""
    validate_game(actions, payoffs)
    return _audit_profile(actions, payoffs, _check_profile(actions, profile))


def find_pure_equilibria(actions, payoffs, epsilon=0.0):
    """Find all pure epsilon-Nash profiles in the supplied finite game.

    epsilon=0 keeps profiles with no strictly profitable unilateral
    deviation. epsilon>0 also keeps profiles whose best gain is at most
    epsilon (gain == epsilon counts). Comparisons are direct, with no
    implicit tolerance, so float rounding can matter (see the source
    README). Profiles are returned in the order of itertools.product
    over actions.
    """
    if not _is_number(epsilon) or epsilon < 0:
        raise ValueError("epsilon must be finite and nonnegative.")

    profiles = validate_game(actions, payoffs)
    out = []
    for profile in profiles:
        result = _audit_profile(actions, payoffs, profile)
        if result["max_deviation_gain"] <= epsilon:
            out.append(result)
    return out


# ------------------------------------------------------------------
# The equilibrium gap: the v0.4.0 optimization variable.
# ------------------------------------------------------------------

def equilibrium_gap(actions, payoffs, profile):
    """The maximum profitable unilateral deviation gain at `profile`.

    0 at an equilibrium, positive everywhere else. This is the
    quantity the SDF synergy agents minimize: unlike empathy
    entropy, which saturated at its ceiling in claim (vi), the
    gap has a real zero and a real direction."""
    return analyze_profile(actions, payoffs, profile)["max_deviation_gain"]


def is_epsilon_equilibrium(actions, payoffs, profile, epsilon):
    """True iff `profile` is an epsilon-Nash equilibrium of the
    supplied game (max deviation gain at most epsilon)."""
    return equilibrium_gap(actions, payoffs, profile) <= epsilon


def audit_table(actions, payoffs, epsilon):
    """Audit a whole payoff table at once: the gap of every
    profile, all pure epsilon-equilibria, and the minimum-gap
    profile. Returns a dict; `equilibria` is a list of
    analyze_profile results, `min_gap_profile` is the first
    profile (itertools.product order) attaining the minimum gap."""
    profiles = validate_game(actions, payoffs)
    gaps = {}
    for profile in profiles:
        gaps[profile] = _audit_profile(actions, payoffs, profile)["max_deviation_gain"]
    equilibria = [g for g in (analyze_profile(actions, payoffs, p)
                              for p in profiles)
                  if g["max_deviation_gain"] <= epsilon]
    min_gap = min(gaps.values())
    min_profile = next(p for p in profiles if gaps[p] == min_gap)
    return {
        "gaps": gaps,
        "min_gap": min_gap,
        "min_gap_profile": list(min_profile),
        "equilibria": equilibria,
        "n_equilibria": len(equilibria),
        "epsilon": epsilon,
    }
