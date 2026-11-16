# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)
"""Tests for discord, the generation step, and the healing rule."""

import random

from quantum_projection import (HEALTHY_SEQUENCES, avatar_state, discord,
                                generation_step, healing_verdict,
                                healthy_membrane, make_avatar, run_cascade,
                                self_knowing)


def test_discord_is_one_minus_d():
    mem = healthy_membrane()
    stored = avatar_state(["AATTAA"], [1.0])
    assert abs(discord(stored, mem)) < 1e-12
    kernel = avatar_state(["CCCCCC"], [1.0])
    assert abs(discord(kernel, mem) - 1.0) < 1e-12


def test_generation_step_never_mutates_stored_variants():
    mem = healthy_membrane()
    rng = random.Random(2)
    av = make_avatar("AATTAA", rng)
    for _ in range(10):
        av = generation_step(av, mem, 0.3, rng)
        # The healthy reference stays in the list once present: the
        # projection keeps adding it and mutation never touches it.
        assert "AATTAA" in av["sequences"]
        st = avatar_state(av["sequences"], av["weights"])
        assert abs(sum(abs(c) ** 2 for c in st) - 1.0) < 1e-9


def test_discord_falls_over_a_short_run():
    recs = run_cascade(n_avatars=4, generations=5, seed=11)
    assert len(recs) == 6
    assert recs[0]["mean_discord"] > recs[-1]["mean_discord"]
    assert all(0.0 <= r["mean_discord"] <= 1.0 for r in recs)
    assert all(0.0 <= d <= 1.0 for r in recs for d in r["per_avatar_d"])


def test_healing_verdict_logic():
    def recs(first, last):
        return [{"mean_discord": first}, {"mean_discord": last}]
    assert healing_verdict(recs(1.0, 0.4))[0] is True
    assert healing_verdict(recs(1.0, 0.5))[0] is True   # boundary inclusive
    assert healing_verdict(recs(1.0, 0.51))[0] is False
    assert healing_verdict(recs(0.0, 0.0))[0] is True   # degenerate: ratio 0


def test_healing_passes_on_the_registered_run():
    recs = run_cascade(n_avatars=8, generations=10, seed=11)
    passed, ratio = healing_verdict(recs)
    assert passed, f"discord ratio {ratio}"
    assert ratio < 0.2  # pilot: 0.09x (seed 7), 0.11x (seed 11)
