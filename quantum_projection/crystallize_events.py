# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)
"""Crystallize events: calibration checkpoints INSIDE the loop.

SYNTHETIC. Classical emulation only. A crystallize event is a
committed forecast about the next generation, scored the way the
Crystallize game scores it (see crystallize/game.js and the
membrane-arena Crystallize injection, which used the same
formulas): Brier = (p - truth)^2, points = 100 * (1 - 4 * Brier)
minus a sampling cost of 0.8 points per sample. The forecast here
is one per generation, over all systems: "the mean discord across
systems will fall by at least FALL_THRESHOLD (0.05) next
generation". The agent estimates p from FORECAST_SAMPLES (5)
lookahead simulations with fresh probe seeds; the truth is the
realized fall. The system CREATES events (every generation
produces a commit opportunity) and NEEDS them (the Brier ledger
is what measures whether the eternal loop stays honest -- without
a checkpoint, nothing would notice if the forecasts drifted).

The precedent, stated honestly: the membrane-arena Crystallize
injection scored NEGATIVE, because the ledger punishes
overconfident 0.75 commits on near-even events. The same
punishment applies here: committing p = 1.0 to a fall that does
not happen scores 100 * (1 - 4) - 4 = -304. A good score here
means the agent's lookaheads genuinely predict the falls, not
that the forecast was easy.

PRE-REGISTERED RULE (claim (viii)): over the run's events, the
mean Brier score is at most BRIER_MAX (0.10) and the mean
|p - truth| is at most CALIBRATION_MAX (0.25), so the agent is
calibrated rather than systematically over- or underconfident.
Thresholds are set from a seed-7 pilot run, round numbers above
the pilot values, not fitted to the final seed 11. Whether the
agent is overconfident (mean(p - truth) > 0.1) or underconfident
(< -0.1) is reported, not gated.
"""

# Pre-registered model parameters (stated, not measured constants).
FALL_THRESHOLD = 0.05       # forecast: mean discord falls by >= this
FORECAST_SAMPLES = 5        # lookahead simulations per forecast
SAMPLE_COST = 0.8           # Crystallize reading cost, points per sample

# Pre-registered verdict rules (claim (viii)). Set from the
# seed-7 pilot: mean Brier 0.0040, mean |p - truth| 0.0200,
# total points 944.0 over 10 events, bias balanced (+0.020).
# BRIER_MAX (0.05) and CALIBRATION_MAX (0.10) are round numbers
# above the pilot values, not fitted to the final seed.
BRIER_MAX = 0.05
CALIBRATION_MAX = 0.10


def brier(p, truth):
    """(p - truth)^2, with truth in {0, 1}."""
    if not 0.0 <= p <= 1.0:
        raise ValueError(f"probability p must be in [0, 1], got {p}")
    if truth not in (0, 1):
        raise ValueError(f"truth must be 0 or 1, got {truth!r}")
    return (p - truth) ** 2


def crystallize_points(p, truth, n_samples=FORECAST_SAMPLES):
    """Crystallize score for one event: 100 * (1 - 4 * Brier) minus
    0.8 points per sample. Negative when the commit is wrong with
    confidence, by design."""
    return 100.0 * (1.0 - 4.0 * brier(p, truth)) - SAMPLE_COST * n_samples


def crystallize_verdict(events):
    """Pre-registered rule (claim (viii)): mean Brier <= BRIER_MAX
    and mean |p - truth| <= CALIBRATION_MAX. `events` is a list of
    dicts with keys p, truth, brier, points. Returns (passed,
    details dict)."""
    if not events:
        raise ValueError("need at least one crystallize event")
    n = len(events)
    mean_brier = sum(e["brier"] for e in events) / n
    mean_abs_err = sum(abs(e["p"] - e["truth"]) for e in events) / n
    mean_p = sum(e["p"] for e in events) / n
    mean_truth = sum(e["truth"] for e in events) / n
    mean_bias = sum(e["p"] - e["truth"] for e in events) / n
    total_points = sum(e["points"] for e in events)
    check_brier = mean_brier <= BRIER_MAX
    check_cal = mean_abs_err <= CALIBRATION_MAX
    if mean_bias > 0.1:
        bias_label = "overconfident"
    elif mean_bias < -0.1:
        bias_label = "underconfident"
    else:
        bias_label = "balanced"
    details = {
        "n_events": n,
        "calibrated_ok": bool(check_brier and check_cal),
        "mean_brier": mean_brier,
        "brier_max": BRIER_MAX,
        "mean_abs_error": mean_abs_err,
        "calibration_max": CALIBRATION_MAX,
        "mean_p": mean_p,
        "mean_truth": mean_truth,
        "mean_bias": mean_bias,
        "bias_label": bias_label,
        "total_points": total_points,
        "mean_points_per_event": total_points / n,
    }
    return check_brier and check_cal, details
