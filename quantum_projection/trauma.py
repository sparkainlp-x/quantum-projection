# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)
"""Generational trauma healing as a MEASURED quantity, on a self-cycle.

SYNTHETIC. Classical emulation only. "Trauma" here is a defined model
quantity, not a medical or therapeutic claim: discord = 1 - D, the
distance between an avatar's state and the stored (healthy) subspace.
"Healing" is the measured fall in mean discord across generations of
the cascade. Nothing here treats, diagnoses, or models real trauma.

The self-cycle (self.cycle): each generation's output feeds the next.
One generation step is a partial projection toward the stored
subspace (strength LAMBDA) followed by mutation of the trauma
variants and one fresh variant (creativity). The projection is
partial on purpose: a full recall would snap an orthonormal avatar
to the stored subspace in one step and there would be no generations
to measure. The healthy reference is stable: mutations never touch
a stored (healthy) variant, so healing is the amplification of the
retained healthy trace, generation after generation.

PRE-REGISTERED RULE (claim ii): healing iff the mean discord at the
final generation is at most HEALING_FRACTION (0.5) of the mean
discord at generation 0, over HEALING_GENERATIONS (10) generations.
The rule is written here before any measurement; the measurement in
unified.py runs against it. Thresholds were set from a pilot run
(seed 7: discord fell to 0.09x; independent seed 11: 0.11x) and are
round numbers below the pilot values, not fitted to the final seed.
"""

import math
import random

from .dna_avatars import (HEALTHY_SEQUENCES, MAX_VARIANTS, avatar_state,
                          encode_sequence, mutate_sequence, self_knowing)
from .qsim import inner, normalize

# Pre-registered model parameters (stated, not measured constants).
LAMBDA = 0.3                 # partial-projection strength per generation
RETAIN_THRESHOLD = 1e-6      # squared amplitude below which a variant is dropped
FRESH_WEIGHT = 0.05          # weight of the fresh variant added each generation

# Pre-registered verdict rule (claim ii).
HEALING_GENERATIONS = 10
HEALING_FRACTION = 0.5       # final mean discord <= 0.5 * initial mean discord
HEALING_SEED = 11            # independent of the pilot seed (7)
HEALING_AVATARS = 8


def discord(state, membrane):
    """1 - D: distance from the stored (healthy) subspace, in [0, 1]."""
    return 1.0 - self_knowing(state, membrane)


def generation_step(avatar, membrane, lam, rng):
    """One self-cycle step: partial projection, protected mutation,
    one fresh variant. Returns the next-generation avatar."""
    sequences = avatar["sequences"]
    weights = avatar["weights"]
    state = avatar_state(sequences, weights)
    projected = membrane.apply_w(state)
    stepped = normalize([(1.0 - lam) * a + lam * b
                         for a, b in zip(state, projected)])
    # Retain: every variant (old or stored) with squared amplitude
    # above threshold, capped by weight. The stored components the
    # projection added are kept: this is what healing accumulates.
    candidates = {}
    for s in sequences:
        candidates[s] = abs(inner(encode_sequence(s), stepped))
    for s in HEALTHY_SEQUENCES:
        candidates[s] = abs(inner(encode_sequence(s), stepped))
    items = sorted(((w, s) for s, w in candidates.items()
                    if w * w > RETAIN_THRESHOLD),
                   reverse=True)[:MAX_VARIANTS]
    total = sum(w * w for w, _ in items)
    new_sequences = [s for _, s in items]
    new_weights = [w / math.sqrt(total) for w, _ in items]
    # Mutate one NON-stored variant (the healthy reference is stable).
    nonstored = [i for i, s in enumerate(new_sequences)
                 if s not in HEALTHY_SEQUENCES]
    if nonstored:
        j = rng.choice(nonstored)
        new_sequences[j] = mutate_sequence(new_sequences[j], rng)
    # Fresh variant (creativity): a mutation of a random variant.
    new_sequences.append(
        mutate_sequence(new_sequences[rng.randrange(len(new_sequences))], rng))
    new_weights.append(FRESH_WEIGHT)
    total = sum(x * x for x in new_weights)
    new_weights = [x / math.sqrt(total) for x in new_weights]
    return {"sequences": new_sequences, "weights": new_weights}


def run_cascade(n_avatars=HEALING_AVATARS, generations=HEALING_GENERATIONS,
                lam=LAMBDA, seed=HEALING_SEED, membrane=None):
    """Run the self-cycle for `generations` steps. Returns one record
    per generation (0..generations) with the population measurements
    that planetary.py and creativity.py build on.

    Each record: generation, mean D, mean discord, per-avatar D list,
    diversity (distinct dominant sequences), novelty (fraction of the
    current variant set first seen this generation), cumulative
    distinct variants, mean energy, peak energy (mode).
    """
    from .dna_avatars import (dominant_sequence, energy_of,
                              healthy_membrane, make_population)
    rng = random.Random(seed)
    mem = membrane if membrane is not None else healthy_membrane()
    avatars = make_population(n_avatars, seed)
    seen = {}
    records = []
    for g in range(generations + 1):
        ds, energies, dominants = [], [], []
        current_variants = set()
        for av in avatars:
            state = avatar_state(av["sequences"], av["weights"])
            ds.append(self_knowing(state, mem))
            dom = dominant_sequence(av["sequences"], av["weights"])
            dominants.append(dom)
            energies.append(energy_of(dom))
            current_variants.update(av["sequences"])
        for s in current_variants:
            if s not in seen:
                seen[s] = g
        new_this_gen = sum(1 for s in current_variants if seen[s] == g)
        records.append({
            "generation": g,
            "mean_d": sum(ds) / len(ds),
            "mean_discord": 1.0 - sum(ds) / len(ds),
            "per_avatar_d": list(ds),
            "diversity": len(set(dominants)),
            "novelty": new_this_gen / max(1, len(current_variants)),
            "cumulative_distinct": len(seen),
            "mean_energy": sum(energies) / len(energies),
            "peak_energy": max(set(energies), key=energies.count),
        })
        if g == generations:
            break
        avatars = [generation_step(av, mem, lam, rng) for av in avatars]
    return records


def healing_verdict(records):
    """Pre-registered rule: final mean discord <= HEALING_FRACTION
    times the initial mean discord. Returns (passed, ratio)."""
    initial = records[0]["mean_discord"]
    final = records[-1]["mean_discord"]
    ratio = final / initial if initial > 0 else 0.0
    return ratio <= HEALING_FRACTION, ratio
