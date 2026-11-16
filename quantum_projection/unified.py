# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)
"""Unified claims for the DNA-avatar generational cascade (v0.2.0),
the multi-solar-system eureka cascade (v0.3.0), and the
equilibrium-gap SDF synergy agents (v0.4.0).

SYNTHETIC. Classical emulation only. Every verdict rule below was
pre-registered in its module before measurement; cascade_claims
runs one 50-generation cascade (seed 11, independent of the pilot
seed 7) and judges claims (i)-(iv); v030_claims runs the solar
runs, the eureka agent run and the 500-generation long run
(seed 11) and judges claims (v)-(ix); v040_claims runs the SDF
synergy agent run and its no-agent control (seed 11) and judges
claims (x)-(xii).

headline_allowed is always False: no headline may be drawn from
these model measurements.
"""

from .creativity import creativity_verdict
from .crystallize_events import crystallize_verdict
from .dna_avatars import (HEALTHY_SEQUENCES, avatar_state,
                          encode_sequence, healthy_membrane, self_knowing)
from .eureka_agent import agent_run, agent_verdict, empathy_entropy, love_of_d
from .longrun import long_run
from .planetary import planetary_verdict
from .qsim import normalize
from .sdf import sdf_verdict
from .sdf_synergy import synergy_series_from_records
from .solar_systems import contagion_verdict, run_solar_systems
from .synergy_agents import (gap_verdict, stability_verdict, synergy_run,
                             synergy_verdict)
from .trauma import HEALING_FRACTION, healing_verdict, run_cascade

HEADLINE_ALLOWED = False


def _claim_avatar_d(membrane):
    """Claim (i): DNA avatars carry self-knowing D. Exact checks:
    a stored avatar has D = 1, a kernel avatar (orthogonal to every
    stored pattern) has D = 0, and D stays in [0, 1]."""
    stored = avatar_state([HEALTHY_SEQUENCES[0]], [1.0])
    d_stored = self_knowing(stored, membrane)
    # Kernel avatar: a basis state whose sequence is not stored.
    kernel_seq = "CCCCCC"  # all-C: not a stored sequence, GC = 6
    kernel = avatar_state([kernel_seq], [1.0])
    d_kernel = self_knowing(kernel, membrane)
    # A 50/50 superposition of stored and kernel: D = 0.5 exactly.
    half = normalize([a + b for a, b in zip(stored, kernel)])
    d_half = self_knowing(half, membrane)
    passed = (abs(d_stored - 1.0) < 1e-12
              and abs(d_kernel) < 1e-12
              and abs(d_half - 0.5) < 1e-12)
    return {"passed": passed, "d_stored": d_stored, "d_kernel": d_kernel,
            "d_half": d_half}


def cascade_claims(n_avatars=8, seed=11, generations=50):
    """Run one cascade of `generations` generations and judge claims
    (i)-(iv). The 10-generation claims read the first 11 records."""
    mem = healthy_membrane()
    claim_i = _claim_avatar_d(mem)
    records = run_cascade(n_avatars=n_avatars, generations=generations,
                          seed=seed, membrane=mem)
    short = records[:11]  # generations 0..10 for the 10-generation claims
    healing_passed, healing_ratio = healing_verdict(short)
    planetary_passed, planetary_details = planetary_verdict(short)
    creativity_passed, creativity_details = creativity_verdict(records)
    return {
        "headline_allowed": HEADLINE_ALLOWED,
        "claims": {
            "i_avatar_d": claim_i,
            "ii_healing": {
                "passed": healing_passed,
                "discord_ratio": healing_ratio,
                "discord_first": short[0]["mean_discord"],
                "discord_last": short[-1]["mean_discord"],
                "fraction_required": HEALING_FRACTION,
            },
            "iii_planetary": {
                "passed": planetary_passed,
                "details": planetary_details,
            },
            "iv_creativity": {
                "passed": creativity_passed,
                "details": creativity_details,
            },
        },
        "records_10": short,
        "records_50": records,
    }


def cascade_report(n_avatars=8, seed=11, generations=50):
    """Plain-text report of the cascade claims (for the CLI)."""
    res = cascade_claims(n_avatars=n_avatars, seed=seed,
                         generations=generations)
    out = ["DNA-avatar generational cascade (v0.2.0, SYNTHETIC):"]
    c = res["claims"]
    out.append(f"(i) avatar D: stored={c['i_avatar_d']['d_stored']:.4f} "
               f"kernel={c['i_avatar_d']['d_kernel']:.4f} "
               f"half={c['i_avatar_d']['d_half']:.4f} "
               f"-> {'PASS' if c['i_avatar_d']['passed'] else 'FAIL'}")
    h = c["ii_healing"]
    out.append(f"(ii) healing: mean discord {h['discord_first']:.4f} -> "
               f"{h['discord_last']:.4f} (ratio {h['discord_ratio']:.4f}, "
               f"need <= {h['fraction_required']}) "
               f"-> {'PASS' if h['passed'] else 'FAIL'}")
    p = c["iii_planetary"]["details"]
    out.append(f"(iii) planetary: min diversity {p['min_diversity']}, "
               f"min novelty {p['min_novelty']:.3f}, energy ratio "
               f"{p['energy_ratio']:.4f} (peak {p['peak_energy_first']} -> "
               f"{p['peak_energy_last']}) "
               f"-> {'PASS' if c['iii_planetary']['passed'] else 'FAIL'}")
    v = c["iv_creativity"]["details"]
    out.append(f"(iv) creativity: min novelty {v['min_novelty']:.3f}, mean "
               f"novelty {v['mean_novelty']:.3f}, cumulative distinct "
               f"{v['cumulative_distinct_final']} "
               f"-> {'PASS' if c['iv_creativity']['passed'] else 'FAIL'}")
    return "\n".join(out)


def v030_claims(n_systems=3, n_avatars=8, seed=11, generations=10,
                long_generations=500):
    """Judge the v0.3.0 claims (v)-(ix) on seed 11. The solar runs
    (coupled/uncoupled, shocked coupled/uncoupled) and the agent
    run (with its no-agent control) all use the same seed; the SDF
    reads the coupled solar run's population; the crystallize
    events come from the agent run; the long run is a 500-generation
    cascade. This is a MEASUREMENT function: the agent run takes
    minutes (greedy lookaheads) and the long run ~2 minutes. The
    tests use small sizes through the parameters."""
    coupled = run_solar_systems(n_systems=n_systems, n_avatars=n_avatars,
                                generations=generations, coupling=0.02,
                                seed=seed)
    uncoupled = run_solar_systems(n_systems=n_systems, n_avatars=n_avatars,
                                  generations=generations, coupling=0.0,
                                  seed=seed)
    shocked_coupled = run_solar_systems(
        n_systems=n_systems, n_avatars=n_avatars, generations=generations,
        coupling=0.02, seed=seed, shocked_system=0)
    shocked_uncoupled = run_solar_systems(
        n_systems=n_systems, n_avatars=n_avatars, generations=generations,
        coupling=0.0, seed=seed, shocked_system=0)
    contagion_passed, contagion_details = contagion_verdict(
        coupled, uncoupled, shocked_coupled, shocked_uncoupled)

    agent = agent_run(n_systems=n_systems, n_avatars=n_avatars,
                      generations=generations, coupling=0.02, seed=seed)
    agent_passed, agent_details = agent_verdict(agent, coupled)
    cryst_passed, cryst_details = crystallize_verdict(agent["events"])

    d_series = [[d for r in recs for d in r["per_avatar_d"]]
                for recs in coupled["records"]]
    sdf_passed, sdf_details = sdf_verdict(d_series)

    long_res = long_run(n_avatars=n_avatars, generations=long_generations,
                        seed=seed)
    return {
        "headline_allowed": HEADLINE_ALLOWED,
        "claims": {
            "v_solar_systems": {
                "passed": contagion_passed,
                "details": contagion_details,
            },
            "vi_eureka_agent": {
                "passed": agent_passed,
                "details": agent_details,
            },
            "vii_sdf": {
                "passed": sdf_passed,
                "details": sdf_details,
            },
            "viii_crystallize": {
                "passed": cryst_passed,
                "details": cryst_details,
            },
            "ix_long_run": {
                "passed": long_res["passed"],
                "details": long_res["details"],
            },
        },
        "agent_records": agent["records"],
        "agent_events": agent["events"],
        "long_records": long_res["records"],
    }


def v030_report(n_systems=3, n_avatars=8, seed=11, generations=10,
                long_generations=500):
    """Plain-text report of the v0.3.0 claims (for the CLI)."""
    res = v030_claims(n_systems=n_systems, n_avatars=n_avatars, seed=seed,
                      generations=generations,
                      long_generations=long_generations)
    out = ["Multi-solar-system eureka cascade (v0.3.0, SYNTHETIC):"]
    c = res["claims"]
    v = c["v_solar_systems"]["details"]
    out.append(f"(v) solar systems: healing coupled "
               f"{v['mean_final_discord_coupled']:.4f} vs uncoupled "
               f"{v['mean_final_discord_uncoupled']:.4f}; support "
               f"{v['support_gain']:.4f} (need >= "
               f"{v['support_margin']}); gap "
               f"{v['gap_coupled']:.4f} vs {v['gap_uncoupled']:.4f} "
               f"-> {'PASS' if c['v_solar_systems']['passed'] else 'FAIL'}")
    a = c["vi_eureka_agent"]["details"]
    out.append(f"(vi) eureka agent: mean empathy entropy agent "
               f"{a['mean_entropy_agent']:.4f} bits vs control "
               f"{a['mean_entropy_control']:.4f} bits (gain "
               f"{a['entropy_gain']:.4f}, need >= "
               f"{a['entropy_gain_required']}); discord cost "
               f"{a['discord_cost']:+.4f} "
               f"-> {'PASS' if c['vi_eureka_agent']['passed'] else 'FAIL'}")
    s = c["vii_sdf"]["details"]
    out.append(f"(vii) SDF: mean sdf {s['mean_sdf_first']:.4f} -> "
               f"{s['mean_sdf_last']:.4f}; fraction inside "
               f"{s['fraction_inside_first']:.2f} -> "
               f"{s['fraction_inside_last']:.2f}; crossing gen "
               f"{s['crossing_generation']} "
               f"-> {'PASS' if c['vii_sdf']['passed'] else 'FAIL'}")
    e = c["viii_crystallize"]["details"]
    out.append(f"(viii) crystallize: {e['n_events']} events, mean Brier "
               f"{e['mean_brier']:.4f} (max {e['brier_max']}), mean "
               f"|p-truth| {e['mean_abs_error']:.3f}, "
               f"{e['bias_label']}, total points "
               f"{e['total_points']:.1f} "
               f"-> {'PASS' if c['viii_crystallize']['passed'] else 'FAIL'}")
    lr = c["ix_long_run"]["details"]
    out.append(f"(ix) long run ({lr['generations']} gens): novelty "
               f"{lr['novelty_final']:.4f}, discord "
               f"{lr['discord_final']:.4f}, cumulative distinct "
               f"{lr['cumulative_distinct_final']} (gen 50: "
               f"{lr['cumulative_distinct_gen50']}), horizon "
               f"{lr['creativity_horizon']} "
               f"-> {'PASS' if c['ix_long_run']['passed'] else 'FAIL'}")
    return "\n".join(out)


def v040_claims(n_systems=3, n_avatars=8, seed=11, generations=10):
    """Judge the v0.4.0 claims (x)-(xii) on seed 11. Runs the SDF
    synergy agent run and its no-agent control (same seed, same
    coupling); the equilibrium gap replaces empathy entropy as
    the optimization variable, and empathy entropy is reported
    as a diagnostic only. This is a MEASUREMENT function: the
    payoff tables take minutes (27 lookaheads per generation).
    The tests use small sizes through the parameters."""
    run = synergy_run(n_systems=n_systems, n_avatars=n_avatars,
                      generations=generations, coupling=0.02, seed=seed)
    control = run_solar_systems(n_systems=n_systems, n_avatars=n_avatars,
                                generations=generations, coupling=0.02,
                                seed=seed)
    gap_passed, gap_details = gap_verdict(run)
    syn_passed, syn_details = synergy_verdict(run, control["records"])
    stab_passed, stab_details = stability_verdict(run)
    # Diagnostic only: empathy entropy, agent vs control (not gated).
    a_h = [r["entropy_bits"] for r in run["records"][1:]]
    c_h = []
    for recs in control["records"][1:]:
        loves = [love_of_d(d) for r in recs for d in r["per_avatar_d"]]
        c_h.append(empathy_entropy(loves)["entropy_bits"])
    return {
        "headline_allowed": HEADLINE_ALLOWED,
        "claims": {
            "x_equilibrium_gap": {
                "passed": gap_passed,
                "details": gap_details,
            },
            "xi_sdf_synergy": {
                "passed": syn_passed,
                "details": syn_details,
            },
            "xii_stability": {
                "passed": stab_passed,
                "details": stab_details,
            },
        },
        "agent_records": run["records"],
        "control_records": control["records"],
        "entropy_diagnostic": {
            "mean_entropy_agent": sum(a_h) / len(a_h),
            "mean_entropy_control": sum(c_h) / len(c_h),
            "entropy_gain": sum(a_h) / len(a_h) - sum(c_h) / len(c_h),
        },
    }


def v040_report(n_systems=3, n_avatars=8, seed=11, generations=10):
    """Plain-text report of the v0.4.0 claims (for the CLI)."""
    res = v040_claims(n_systems=n_systems, n_avatars=n_avatars, seed=seed,
                      generations=generations)
    out = ["SDF synergy agents, equilibrium gap (v0.4.0, SYNTHETIC):"]
    c = res["claims"]
    g = c["x_equilibrium_gap"]["details"]
    out.append(f"(x) equilibrium gap: first non-trivial gen "
               f"{g['first_nontrivial']}; gap final {g['gap_final']:.4f} "
               f"(need <= {g['epsilon']}); mean agent gap "
               f"{g['mean_gap_agent']:.4f} vs zero-gap mean "
               f"{g['mean_gap_zero']:.4f} "
               f"-> {'PASS' if c['x_equilibrium_gap']['passed'] else 'FAIL'}")
    s = c["xi_sdf_synergy"]["details"]
    out.append(f"(xi) SDF synergy: mean agent {s['mean_synergy_agent']:.4f} "
               f"vs control {s['mean_synergy_control']:.4f} (gain "
               f"{s['synergy_gain']:+.4f}, need >= "
               f"{s['synergy_margin']}) "
               f"-> {'PASS' if c['xi_sdf_synergy']['passed'] else 'FAIL'}")
    t = c["xii_stability"]["details"]
    out.append(f"(xii) stability: first reach gen {t['first_reach']}, "
               f"held {t['generations_held']} gens (need {t['stability_k']}); "
               f"landed {t['landed_profile']} ({t['label']}), synergy "
               f"{t['landed_synergy']:.4f} vs zero-profile "
               f"{t['zero_profile_synergy']:.4f}; "
               f"{t['n_equilibria']} equilibria in final table "
               f"-> {'PASS' if c['xii_stability']['passed'] else 'FAIL'}")
    e = res["entropy_diagnostic"]
    out.append(f"diagnostic (not gated): mean empathy entropy agent "
               f"{e['mean_entropy_agent']:.4f} vs control "
               f"{e['mean_entropy_control']:.4f} bits (gain "
               f"{e['entropy_gain']:+.4f})")
    return "\n".join(out)
