# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)
"""Infinite creativity as an unbounded generation rule.

SYNTHETIC. Classical emulation only. "Infinite" means the generation
rule has no built-in cap: every generation each avatar gains a fresh
mutated variant, so the population's variant set can keep growing
without bound. This is not literal infinity (any finite run sees a
finite count); the claim is that novelty is SUSTAINED, never hitting
zero, over a long run. The number is measured, not asserted.

PRE-REGISTERED RULES (claim iv) over CREATIVITY_GENERATIONS (50):
(a) novelty > 0 in every generation after generation 0;
(b) cumulative distinct variants strictly increase every generation;
(c) mean novelty over the run >= MEAN_NOVELTY_FLOOR (0.05).
Thresholds were set from a pilot run (seed 7: min novelty 0.09 over
50 generations, cumulative strictly increasing every generation;
independent seed 11: min novelty 0.094, mean novelty ~0.13) and are
round numbers below the pilot values, not fitted to the final seed.
"""

from .trauma import HEALING_AVATARS, HEALING_SEED, run_cascade

# Pre-registered verdict rules (claim iv).
CREATIVITY_GENERATIONS = 50
CREATIVITY_SEED = HEALING_SEED
CREATIVITY_AVATARS = HEALING_AVATARS
MEAN_NOVELTY_FLOOR = 0.05


def creativity_verdict(records):
    """All three pre-registered conditions. Returns
    (passed, details dict)."""
    rest = records[1:]
    novelty_ok = all(r["novelty"] > 0 for r in rest)
    cum = [r["cumulative_distinct"] for r in records]
    increasing_ok = all(b > a for a, b in zip(cum, cum[1:]))
    mean_novelty = sum(r["novelty"] for r in rest) / len(rest)
    mean_ok = mean_novelty >= MEAN_NOVELTY_FLOOR
    details = {
        "novelty_ok": novelty_ok,
        "min_novelty": min(r["novelty"] for r in rest),
        "increasing_ok": increasing_ok,
        "cumulative_distinct_final": cum[-1],
        "mean_novelty_ok": mean_ok,
        "mean_novelty": mean_novelty,
    }
    return novelty_ok and increasing_ok and mean_ok, details


def creativity_run(n_avatars=CREATIVITY_AVATARS,
                   generations=CREATIVITY_GENERATIONS,
                   seed=CREATIVITY_SEED):
    """Run the long cascade and judge it by the creativity rules."""
    records = run_cascade(n_avatars=n_avatars, generations=generations,
                          seed=seed)
    passed, details = creativity_verdict(records)
    return {"records": records, "passed": passed, "details": details}
