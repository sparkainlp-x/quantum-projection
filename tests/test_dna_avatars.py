# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)
"""Tests for the DNA-avatar encoding and self-knowing D."""

import math
import random

import pytest

from quantum_projection import (HEALTHY_SEQUENCES, avatar_state,
                                dominant_sequence, encode_sequence, energy_of,
                                gc_content, healthy_membrane, make_avatar,
                                make_population, mutate_sequence, self_knowing,
                                trauma_variant)


def test_encode_sequence_is_basis_state():
    v = encode_sequence("AATTAA")
    assert len(v) == 1 << 12
    assert sum(abs(c) ** 2 for c in v) == pytest.approx(1.0)
    assert sum(1 for c in v if c != 0j) == 1
    # A=00 C=01 G=10 T=11: "AA" -> index 0, "CCCCCC" -> index 0b010101010101
    assert encode_sequence("AAAAAA")[0] == 1.0 + 0j
    assert encode_sequence("CCCCCC")[0b010101010101] == 1.0 + 0j
    with pytest.raises(ValueError):
        encode_sequence("AATT")  # wrong length
    with pytest.raises(ValueError):
        encode_sequence("AATTAX")  # bad base


def test_avatar_state_normalized_and_dominant():
    av = make_avatar("AATTAA", random.Random(1))
    assert av["sequences"][0] == "AATTAA"  # healthy seed first
    assert len(av["sequences"]) == 5
    st = avatar_state(av["sequences"], av["weights"])
    assert abs(sum(abs(c) ** 2 for c in st) - 1.0) < 1e-12
    assert dominant_sequence(av["sequences"], av["weights"]) == av["sequences"][1]


def test_self_knowing_exact_values():
    mem = healthy_membrane()
    stored = avatar_state(["AATTAA"], [1.0])
    assert abs(self_knowing(stored, mem) - 1.0) < 1e-12
    kernel = avatar_state(["CCCCCC"], [1.0])
    assert abs(self_knowing(kernel, mem)) < 1e-12
    from quantum_projection import normalize
    half = normalize([a + b for a, b in zip(stored, kernel)])
    assert abs(self_knowing(half, mem) - 0.5) < 1e-12
    # D stays in [0, 1] for a random avatar
    rng = random.Random(3)
    for m in range(4):
        av = make_avatar(HEALTHY_SEQUENCES[m], rng)
        d = self_knowing(avatar_state(av["sequences"], av["weights"]), mem)
        assert 0.0 <= d <= 1.0


def test_energy_is_gc_plus_one():
    assert gc_content("AATTAA") == 0
    assert energy_of("AATTAA") == 1.0
    assert gc_content("CCCCCC") == 6
    assert energy_of("CCCCCC") == 7.0
    assert gc_content("GCGCGC") == 6
    assert energy_of("ATGCAT") == 3.0


def test_mutation_changes_exactly_one_base():
    rng = random.Random(5)
    for _ in range(20):
        s = mutate_sequence("AATTAA", rng)
        assert len(s) == 6
        assert sum(1 for a, b in zip(s, "AATTAA") if a != b) == 1
    # A trauma variant differs from its healthy template
    t = trauma_variant("AATTAA", random.Random(9))
    assert sum(1 for a, b in zip(t, "AATTAA") if a != b) <= 3


def test_population_cycles_templates():
    pop = make_population(8, seed=11)
    assert len(pop) == 8
    assert [p["sequences"][0] for p in pop] == HEALTHY_SEQUENCES * 2
