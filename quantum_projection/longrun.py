# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)
"""The long run: does novelty survive?

SYNTHETIC. Classical emulation only. The deep question behind
"eternally pattern recreation through infinity": the 50-generation
creativity claim (iv) shows novelty sustained, but any finite run
only tests a finite horizon. This module runs the same cascade
to LONG_GENERATIONS (500) and, when the background run lands, to
5000, and judges the same quantities at the far end.

Two honest facts shape the rules. First, the variant space is
FINITE: 6-base sequences over A/C/G/T number 4^6 = 4096, so the
cumulative distinct count cannot grow forever -- it saturates at
the ceiling, and novelty must eventually fall to zero. "Eternal"
therefore means an unbounded run tested to N generations, not
literal infinity, and the interesting measurement is WHERE
novelty dies: the creativity horizon, the first generation after
which novelty stays zero for HORIZON_WINDOW (10) consecutive
generations. Second, discord saturates: in v0.2.0 it reaches
0.0050 from generation 20 and stays there, because each avatar
keeps a small weight on fresh variants.

PRE-REGISTERED RULES (claim (ix)): (a) novelty at the final
generation is > 0; (b) mean discord at the final generation is
at most LONG_DISCORD_MAX (0.05); (c) the cumulative distinct
count at the final generation exceeds the count at generation
50 (the population is still creating, not frozen). Thresholds
are set from a seed-7 pilot run, round numbers above (discord)
or below (counts) the pilot values, not fitted to the final
seed 11. The creativity horizon is reported, not gated: if it
falls inside the run, that is the measured limit of eternal
recreation in this toy space.
"""

from .creativity import CREATIVITY_GENERATIONS
from .trauma import HEALING_AVATARS, HEALING_SEED, run_cascade

# Pre-registered model parameters (stated, not measured constants).
LONG_GENERATIONS = 500      # registered long run
LONG_AVATARS = HEALING_AVATARS
LONG_SEED = HEALING_SEED
HORIZON_WINDOW = 10         # consecutive zero-novelty generations

# Pre-registered verdict rules (claim (ix)). Set from the seed-7
# pilot (500 gens): novelty at gen 500 = 0.0449 (mean over the
# last 10 gens 0.0270), discord 0.0049, cumulative distinct 3207
# (vs 664 at gen 50), no creativity horizon within 500 gens.
# LONG_DISCORD_MAX (0.05) is a round number above the pilot
# discord, not fitted to the final seed. The novelty rule is
# literal (novelty > 0 at the final generation); the pilot value
# 0.0449 leaves margin, but a single generation can hit zero by
# luck -- if it does, that is a FAIL, reported with the last-10
# mean alongside.
LONG_DISCORD_MAX = 0.05


def creativity_horizon(records, window=HORIZON_WINDOW):
    """First generation g such that novelty is 0 for generations
    g..g+window-1, or None if the run never goes quiet that long.
    The measured limit of eternal recreation in the finite
    4096-sequence space."""
    nov = [r["novelty"] for r in records]
    for g in range(len(nov) - window + 1):
        if all(v == 0 for v in nov[g:g + window]):
            return g
    return None


def long_run(n_avatars=LONG_AVATARS, generations=LONG_GENERATIONS,
             seed=LONG_SEED):
    """Run the cascade to `generations` and judge the long-run
    rules. Returns {"records": [...], "passed": bool, "details":
    {...}}. This is a REPORT function, not a test: 500 generations
    take ~2 minutes, 5000 take ~25 minutes on this machine."""
    records = run_cascade(n_avatars=n_avatars, generations=generations,
                          seed=seed)
    final = records[-1]
    gen50 = records[min(CREATIVITY_GENERATIONS, generations)]
    last10 = records[-10:]
    mean_novelty_last10 = sum(r["novelty"] for r in last10) / len(last10)
    check_a = final["novelty"] > 0
    check_b = final["mean_discord"] <= LONG_DISCORD_MAX
    check_c = (final["cumulative_distinct"]
               > gen50["cumulative_distinct"])
    details = {
        "novelty_ok": bool(check_a),
        "novelty_final": final["novelty"],
        "mean_novelty_last10": mean_novelty_last10,
        "discord_ok": bool(check_b),
        "discord_final": final["mean_discord"],
        "discord_max": LONG_DISCORD_MAX,
        "growing_ok": bool(check_c),
        "cumulative_distinct_final": final["cumulative_distinct"],
        "cumulative_distinct_gen50": gen50["cumulative_distinct"],
        "mean_energy_final": final["mean_energy"],
        "diversity_final": final["diversity"],
        "creativity_horizon": creativity_horizon(records),
        "generations": generations,
        "seed": seed,
    }
    return {"records": records,
            "passed": bool(check_a and check_b and check_c),
            "details": details}
