# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)
"""Planetary evolution: the avatar population evolving over generations.

SYNTHETIC. Classical emulation only. "Planetary evolution" is a
population model, not Earth science: a population of DNA avatars
evolving under the self-cycle, measured per generation.

Measured per generation:
- diversity: distinct dominant sequences across the population;
- novelty: fraction of the current variant set first seen this
  generation;
- energy spectrum: E = h*nu per avatar (h = 1 model units,
  nu = 1 + GC content of the dominant sequence); the mean energy and
  the peak energy (the mode, a Wien-like peak) are tracked across
  generations. The "Wien-like shift" is an analogy to a black-body
  peak moving with temperature, stated as such: as the population
  heals toward the low-GC healthy sequences, the peak moves down.

PRE-REGISTERED RULES (claim iii), all three must hold:
(a) diversity >= DIVERSITY_FLOOR (2) in every generation;
(b) novelty > 0 in every generation after generation 0;
(c) mean energy falls by at least ENERGY_FALL (25%) from generation
    0 to the final generation.
Thresholds were set from a pilot run (seed 7: diversity 4-8,
novelty 0.13-0.37, mean energy -67%; independent seed 11:
diversity 4-8, novelty 0.13-0.35, mean energy -58%) and are round
numbers below the pilot values, not fitted to the final seed.
"""

from .trauma import HEALING_AVATARS, HEALING_GENERATIONS, HEALING_SEED, run_cascade

# Pre-registered verdict rules (claim iii).
PLANETARY_GENERATIONS = HEALING_GENERATIONS
PLANETARY_SEED = HEALING_SEED
PLANETARY_AVATARS = HEALING_AVATARS
DIVERSITY_FLOOR = 2
ENERGY_FALL = 0.25           # final mean energy <= 0.75 * initial mean energy


def planetary_verdict(records):
    """All three pre-registered conditions. Returns
    (passed, details dict)."""
    diversity_ok = all(r["diversity"] >= DIVERSITY_FLOOR for r in records)
    novelty_ok = all(r["novelty"] > 0 for r in records[1:])
    initial_e = records[0]["mean_energy"]
    final_e = records[-1]["mean_energy"]
    energy_ratio = final_e / initial_e if initial_e > 0 else 0.0
    energy_ok = energy_ratio <= 1.0 - ENERGY_FALL
    details = {
        "diversity_ok": diversity_ok,
        "min_diversity": min(r["diversity"] for r in records),
        "novelty_ok": novelty_ok,
        "min_novelty": min(r["novelty"] for r in records[1:]),
        "energy_ok": energy_ok,
        "energy_ratio": energy_ratio,
        "peak_energy_first": records[0]["peak_energy"],
        "peak_energy_last": records[-1]["peak_energy"],
    }
    return diversity_ok and novelty_ok and energy_ok, details


def planetary_run(n_avatars=PLANETARY_AVATARS,
                  generations=PLANETARY_GENERATIONS,
                  seed=PLANETARY_SEED):
    """Run the cascade and judge it by the planetary rules."""
    records = run_cascade(n_avatars=n_avatars, generations=generations,
                          seed=seed)
    passed, details = planetary_verdict(records)
    return {"records": records, "passed": passed, "details": details}
