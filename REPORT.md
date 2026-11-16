# Quantum Projection — measurement report

Version 0.3.0, 2026-11-15. Author: Jean-François Brisson (Spark AI NLP).
Mun Seok Lee is not an author of this release and has not reviewed or
endorsed it (see README Provenance). License: AGPL-3.0-only.

**SYNTHETIC.** Classical emulation throughout. Every number below was
measured in this repo with seeded pseudo-random noise; none is hardware
data. No speedup, no Bell violation.

## v0.1.0 (summary)

The v0.1.0 measurements are in the README: 200-seed sweeps for Bell
classification, non-orthogonal patterns, and coarse-grained 3-qubit
states, with unstored probes and Haar-random controls. Largest gap between
recalled fidelity and Born weight: 5.6e-16. Largest gap between 1-step and
25-step recall: 6.1e-16. All 65 v0.1.0 tests still pass in v0.2.0.

## v0.2.0 — DNA-avatar generational cascade

Modules: `quantum_projection/dna_avatars.py` (encoding, D),
`trauma.py` (discord, generation step, healing rule),
`planetary.py` (diversity, novelty, spectrum, planetary rule),
`creativity.py` (unbounded generation, creativity rule),
`unified.py` (claims (i)–(iv), `HEADLINE_ALLOWED = False`).

### Encoding

6-base DNA sequences over A/C/G/T. Each base is 2 qubits (A=00, C=01,
G=10, T=11), so a sequence is a 12-qubit basis state in a 4096-dimensional
space — a one-to-one map, no collisions, no hidden parameters. An avatar
is a weighted mixture of up to 12 sequences (healthy reference + trauma
variants), normalized. Four healthy templates stored in one membrane
(`AATTAA`, `ATATAT`, `TAAATA`, `AATATT`); 8 avatars, 2 per template.
Initial avatar weights [0.05, 0.5, 0.3, 0.15, 0.05]: the dominant weight
(0.5) sits on a trauma variant 1–3 bases from the template, so every
avatar starts far from the healthy subspace.

Self-knowing D = ⟨ψ|P|ψ⟩ per avatar, with P the projector onto the stored
subspace, built by Gram–Schmidt in pure Python (the D idea from
symmetry-entropy / the Faggin field bridge; provenance header in
`dna_avatars.py`).

Energy: E = hν with h = 1 model units, ν = 1 + GC content of a sequence
(E = 1–7). The population spectrum per generation is measured like a
black-body curve; its peak energy is tracked (a Wien-like shift, measured,
not claimed as physics).

### Generation step (self.cycle)

Each generation: (1) partial projection toward the stored subspace
(λ = 0.3) — a full recall would heal instantly, because an orthonormal W
is a projector; (2) mutate one non-stored base per variant. Each avatar
keeps its healthy sequence at small weight, and mutation never touches
stored variants, so the projection can only amplify weight already
present. The generation's output feeds the next generation.

### Claims — all PASS, pre-registered (seed 11, 8 avatars)

| claim | pre-registered rule | measured | verdict |
|---|---|---|---|
| (i) avatar D | stored D = 1, kernel D = 0, half D = 0.5 (tol 1e-12) | 1.0 / 0.0 / 0.5 | PASS |
| (ii) healing | mean discord(gen 10) ≤ 0.5 × discord(gen 0) | 0.9932 → 0.0894, ratio 0.090 | PASS |
| (iii) planetary | diversity ≥ 2 every gen, novelty > 0 every gen, mean energy falls ≥ 25% | min diversity 4, min novelty 0.124, energy 2.38 → 1.00 (ratio 0.421, −58%), peak 3 → 1 | PASS |
| (iv) creativity | 50 gens: novelty > 0 every gen, cumulative distinct strictly increases every gen, mean novelty ≥ 0.05 | min novelty 0.080, cumulative 36 → 667, mean novelty 0.149 | PASS |

Independent seed 7 (pilot): discord 0.9907 → 0.0888 (ratio 0.090);
mean energy 3.00 → 1.00 (−67%); diversity 8 → 4; novelty > 0 every
generation. The rules were set from seed 7 and verified on seed 11.

### Generation table (seed 11, 8 avatars)

| gen | mean D | mean discord | diversity | novelty | cumulative distinct | mean E | peak E |
|---|---|---|---|---|---|---|---|
| 0 | 0.0068 | 0.9932 | 8 | 1.000 | 36 | 2.38 | 3 |
| 1 | 0.0155 | 0.9845 | 8 | 0.349 | 51 | 2.50 | 3 |
| 2 | 0.0470 | 0.9530 | 8 | 0.300 | 66 | 2.75 | 3 |
| 3 | 0.0968 | 0.9032 | 8 | 0.218 | 78 | 2.75 | 3 |
| 4 | 0.1690 | 0.8310 | 8 | 0.222 | 92 | 2.50 | 1 |
| 5 | 0.2801 | 0.7199 | 8 | 0.200 | 106 | 2.62 | 4 |
| 6 | 0.4199 | 0.5801 | 8 | 0.192 | 121 | 2.25 | 1 |
| 7 | 0.5773 | 0.4227 | 4 | 0.176 | 136 | 1.00 | 1 |
| 8 | 0.7255 | 0.2745 | 4 | 0.124 | 147 | 1.00 | 1 |
| 9 | 0.8392 | 0.1608 | 4 | 0.129 | 159 | 1.00 | 1 |
| 10 | 0.9106 | 0.0894 | 4 | 0.135 | 172 | 1.00 | 1 |
| 20 | 0.9950 | 0.0050 | 4 | 0.121 | 295 | 1.00 | 1 |
| 30 | 0.9950 | 0.0050 | 4 | 0.135 | 429 | 1.00 | 1 |
| 40 | 0.9950 | 0.0050 | 4 | 0.149 | 550 | 1.00 | 1 |
| 50 | 0.9950 | 0.0050 | 4 | 0.080 | 667 | 1.00 | 1 |

Discord falls monotonically, 10/10 steps down over the first 10
generations, then saturates at 0.0050 (D = 0.9950) from generation 20:
each avatar keeps a small weight on its fresh variants, so the population
never reaches the stored subspace exactly. Diversity settles at 4 — the
four healthy templates, each the dominant sequence of two avatars. Novelty
never hits zero in 50 generations (minimum 0.080); cumulative distinct
grows strictly every generation, 36 → 667.

### Defect found and fixed during testing

The Gram–Schmidt projector in `dna_avatars.py` called the inner product
inside the element loop (`[a - inner(q, v) * b for a, b in zip(v, q)]`),
making each vector update O(n²) — one D call took ~11 s and the full
suite hung past 4 minutes. The coefficient is now hoisted
(`coeff = inner(q, v)` before the loop); D takes ~0.02 s. The values were
correct before the fix; only the speed changed. The 50-generation cascade
now runs in ~15 s; the full suite in ~44 s.

### Honest limits

- Classical emulation throughout; the cascade runs on lists of complex
  numbers, not quantum hardware.
- DNA avatars are toy encodings (6-base sequences, 2 qubits per base),
  not biology; nothing here describes real DNA, real trauma, or real
  healing.
- Trauma healing is a measured fall in a defined model quantity
  (discord = 1 − D), not a therapeutic claim.
- Planetary evolution is a population model (8 avatars, 50 generations),
  not Earth science; the E = hν spectrum is a bookkeeping rule with
  h = 1 model units, and the peak shift is a measured pattern in that
  model, not a Wien-law claim.
- Infinite creativity is unbounded generation inside the model (no cap on
  new patterns); it does not claim literal infinity.
- TISU is excluded from this package; `tests/test_exclusion.py` enforces
  the exclusion.
- No headline is allowed for this release (`HEADLINE_ALLOWED = False`).

## v0.3.0 — multi-solar-system eureka cascade

Modules: `quantum_projection/solar_systems.py` (N systems, coupling,
contagion by shock), `eureka_agent.py` (love, empathy entropy,
greedy δ search), `sdf.py` (signed distance field), 
`crystallize_events.py` (Brier scoring), `longrun.py` (500- and
5000-generation runs), `unified.py` (claims (v)–(ix),
`HEADLINE_ALLOWED = False`).

### (v) Solar systems — PASS

Three systems of 8 avatars, coupling κ = 0.02, 10 generations,
seed 11. The unshocked comparison and the shock comparison (system
0 deeply traumatized: 6 flips per variant, retained healthy weight
0.01) each run coupled and uncoupled with identical seeds and
streams.

| check | rule | measured |
|---|---|---|
| (a) no harm | mean final discord coupled ≤ uncoupled + 0.02 | 0.1013 vs 0.1076 |
| (b) support | shocked final discord coupled ≤ uncoupled − 0.05 | 0.6487 vs 0.7516 (gain 0.1029) |
| (c) convergence | gap (shocked − others) narrows coupled by ≥ 0.05 | 0.5438 vs 0.6463 (narrowing 0.1025) |
| (d) no harm to others | others' final discord coupled ≤ uncoupled + 0.02 | 0.1049 vs 0.1053 |

What spreads through the coupling is support, not harm: the
coupling transfers healed weight preferentially to the laggard, so
the shocked system gains 0.103 while the healthy systems lose
nothing (they heal marginally better coupled too). The correlation
check was tried on the pilot and rejected: per-generation discord
changes correlate ~0.78 even uncoupled, because every system
follows the same healing curve.

### (vi) Eureka agent — FAIL (the finding)

Mean empathy entropy over generations 1–10, 24 avatars, seed 11:

| | agent | control | gain | required |
|---|---|---|---|---|
| mean H (bits) | 4.5849 | 4.5849 | −0.0001 | ≥ 0.02 |

H by generation is identical to 4 decimals in both runs
(4.5849, 4.5849, 4.5849, 4.5850, 4.5848, 4.5849, 4.5850,
4.5849, 4.5847, 4.5846 agent; control differs only in the 4th
decimal). The ceiling is log2(24) = 4.5850 bits: H sits at
99.998% of it. The agent's lever (δ on λ) moves H by −0.0001
bits; its discord cost is −0.0006 (final discord 0.1007 agent
vs 0.1013 control — it heals trivially faster). Total love
shows the same nothing: mean 16.08 agent vs 16.10 control.
Total love itself peaks at 24.0 in generation 7 — exactly the
SDF crossing generation, when mean D passes 0.5 — then falls to
14.4 by generation 10 as D → 1.

The mechanism: loves are nearly equal across avatars because all
avatars heal at similar rates, so the normalized love
distribution is nearly uniform and H is saturated from the
start. Healing does NOT concentrate love in the normalized
distribution — as all D → 1 together, all loves → 0 together
and H rises to its ceiling. The tension is in total love, which
falls, not in entropy, which saturates. The threshold (0.02) was
kept as a meaningful bar, not lowered to fit the pilot
(seed 7: gain 0.0028, H at 98.6% of ceiling). A stronger lever
than δ on λ would be needed to move H; that is an open question.

### (vii) SDF — PASS

Mean sdf 0.2895 → −0.3889; fraction of avatars inside the
self-known region (D > 0.5) 0.00 → 1.00; crossing generation 7
(first generation whose mean D exceeds 0.5). The region's volume
on the θ-grid is fixed at 0.5055 (half the grid for τ = 0.5);
what grows is occupancy. The seed-7 pilot on the single
population gave the same shape (mean sdf 0.2882 → −0.6383,
fraction 0.00 → 1.00, crossing gen 7); the multi-system final
sdf is less deep because the coupled population's final mean D
is 0.899 rather than 0.995.

### (viii) Crystallize — PASS

10 events (one per generation), mean Brier 0.0000 (max 0.05),
mean |p − truth| 0.0000 (max 0.10), bias balanced (0.000), total
points 960.0 (96.0 per event — the maximum, 100 − 4 for 5
samples). Every forecast was exactly right. That is what it
looks like: the fall magnitude is nearly deterministic given the
state, so the 5 lookaheads almost always agree and agree with
the truth. The score means the forecasts are honest, not that
the agent is a brilliant forecaster. (Seed-7 pilot: Brier
0.0040, |p−truth| 0.0200, 944.0 points.)

### (ix) Long run — PASS

500 generations, seed 11, 8 avatars:

| check | rule | measured |
|---|---|---|
| novelty at gen 500 | > 0 | 0.0225 (mean over last 10 gens 0.0263) |
| discord at gen 500 | ≤ 0.05 | 0.0050 |
| cumulative distinct | > gen-50 value | 3246 vs 667 |

Diversity 4, mean energy 1.00 at gen 500. Creativity horizon:
none within 500 generations (never 10 consecutive zero-novelty
generations). Seed-7 pilot (500 gens): novelty 0.0449, discord
0.0049, cumulative 3207, horizon none.

The 5000-generation run (seed 11, 1784 s) has now landed, and it
changes the picture: the registered 500-generation claim PASSES,
but its 5000-generation extension FAILS on novelty. Novelty at
gen 5000 is 0.0000 (mean over the last 10 gens 0.0000); discord
stays at its floor, 0.0050; cumulative distinct reaches the
4096-sequence ceiling exactly at generation 4140. The creativity
horizon is generation 1225: novelty stays zero for 10
consecutive generations from there on, and the last 100
generations are all zero-novelty. Note the nuance: novelty goes
quiet at 1225 when cumulative is 3967 (97% of the space), not
when the space is exhausted — the population stops exploring
before the ceiling is reached, because mutations only reach
1-neighbours of the current variants and the population has
converged near the stored templates; the last 129 sequences
trickle in over generations 1225–4140. "Eternal recreation" has
a measured limit in this toy space: generation 1225.

### Honest limits (v0.3.0)

- Classical emulation throughout; the eureka agent is a bounded
  optimizer (greedy coordinate descent over 3 δ values per
  system), not a mind.
- Empathy entropy is entropy over a measured love distribution in
  the model, not human empathy; love is concurrence across the
  stored/non-stored split by definition (2√(D(1−D))), not a claim
  about feeling.
- The SDF is a field over a toy state space; the self-known region
  is fixed and the population moves through it.
- Crystallize events are calibration checkpoints, not guarantees;
  a perfect Brier score on a near-deterministic forecast is
  expected, not surprising.
- "Eternal" means an unbounded run tested to N generations (500
  here, 5000 in progress), not literal infinity; the finite
  4096-sequence space bounds novelty, and the creativity horizon
  is the measured limit.
- TISU is excluded from this package; `tests/test_exclusion.py`
  enforces the exclusion.
- No headline is allowed for this release (`HEADLINE_ALLOWED = False`).

## v0.4.0 — equilibrium gap and SDF synergy agents

Modules: `quantum_projection/equilibrium.py` (the vendored
checker + the gap), `sdf_synergy.py` (coverage synergy +
marginal contributions), `synergy_agents.py` (payoff tables,
gap descent, the run, verdicts (x)-(xii)), `unified.py`
(`v040_claims`, `v040_report`).

### The checker, vendored

`validate_game`, `analyze_profile` and `find_pure_equilibria`
are vendored essentially unchanged from finite-game-equilibria
v0.1.0 (DOI 10.5281/zenodo.23530287, commit
11698948b54056da98aaa3417b6a7062d801faa6). The vendored code
was checked against the source package's own README demos in
the tests: prisoner's dilemma (only (defect, defect)),
coordination (two equilibria), matching pennies (none at
epsilon 0, all four at epsilon 2). The game checked here:
players = the 3 solar systems, actions = delta in
{-0.05, 0, +0.05} per system, payoffs = per-system marginal
contributions to the joint inside-coverage. The audit pattern
is the one oes-coordination-lab uses (DOI
10.5281/zenodo.23530289): the same two functions audit a
synthetic 3-agent coordination game and name the coordination
trap.

### SDF synergy, defined

On the 91-point SDF grid (theta in [0, pi/2], D = cos^2
theta), the self-known region is the bins with sdf < 0 as
computed: 46 of 91 (bin 45 sits at sdf = -1.1e-16,
floating-point dust at the boundary). An avatar occupies the
bin nearest its theta. Per-system inside-coverage = the
fraction of the region's bins occupied by at least one of its
avatars; joint = the union's fraction; synergy = joint - mean
(per-system). The coverage reading is stated in the module
with the reason: the pooled-avatar-fraction reading is
identically the mean for equal-sized systems, so it makes
synergy zero by construction. Each agent's payoff is its
system's leave-one-out marginal contribution to the joint
coverage (>= 0 always; a herding system earns 0).

### The run

Per generation: measure the current population (synergy,
empathy entropy as a diagnostic), build the payoff table from
lookaheads (27 joint delta profiles, one simulated generation
each, fresh probe streams identical across profiles, never
touching the main streams), choose deltas by greedy coordinate
descent on the table's gap (start at all-zero; ties within
1e-12 go to the smallest |delta|), take the real step. The
all-zero profile's gap from the same table is the
counterfactual. Runtime: the registered run takes ~258 s
(mostly the 27 lookaheads per generation).

### Pilot (seed 7, 251.6 s) — thresholds set from it

First non-trivial generation 1. Agent gap 0.0 at every
generation; zero-profile gap 0.0 through gen 6, then 0.0217
(one region bin, 1/46) at gens 7-9, mean 0.00725 over the
post-entry window. Mean synergy agent 0.0580 vs control
0.0529 (gain 0.0051) over gens 1-10, but 0.0966 vs 0.0797
(gain 0.0169) over the final 3 generations -- the agent and
control populations are identical through gen 7 (deltas all
zero while the table is degenerate), so the synergy window is
the final 3 generations. Stability: first reach gen 0
(degenerate start; the rule was then tightened to count from
the first non-trivial generation), held 10; landed profile
[0, 0, -0.05], "efficient" (synergy 0.0870 vs zero-profile
0.0725; zero is NOT an equilibrium; 9 equilibria in the final
table; best equilibrium synergy 0.1087 at [-0.05, -0.05,
0.05] -- greedy descent lands in an efficient equilibrium,
not the best one). Thresholds set as round numbers below the
pilot margins: GAP_EPSILON = 0.01, GAP_MARGIN = 0.002 (one
bin of gap in a single generation of the 9-generation window
is 0.0024), SYNERGY_MARGIN = 0.01, SYNERGY_WINDOW = 3,
STABILITY_K = 3.

### Claims — 1 PASS, 2 FAIL, pre-registered (seed 11)

| claim | pre-registered rule | measured | verdict |
|---|---|---|---|
| (x) equilibrium gap | gap <= 0.01 at gen 10; mean gap <= 0.01 over post-entry window; beats zero-gap mean by >= 0.002 | gap 0.0 at every generation, agent and zero alike; first non-trivial gen 6 | FAIL |
| (xi) SDF synergy | mean synergy, final 3 gens, agent >= control + 0.01 | 0.0217 vs 0.0217, gain 0.0 | FAIL |
| (xii) stability | gap stays <= 0.01 for 3 gens after first reach (from first non-trivial gen); landed equilibrium classified | first reach gen 6, held 4; landed [0, 0, 0], label "trap" (12 equilibria in final table; best synergy 0.0362 at [-0.05, -0.05, 0.05] vs landed 0.0290; zero IS an equilibrium) | PASS |

Synergy series (seed 11, agent = control at every
generation): 0.0000 through gen 6, 0.0435 at gen 7, 0.0362
at gen 8, 0.0145 at gens 9-10. Empathy entropy diagnostic:
mean H agent 4.5849 vs control 4.5849, gain 0.0 -- still
saturated, confirming claim (vi). The synergy numbers were
independently recomputed from the saved records and match
exactly.

### What the FAILs mean

On seed 11 the all-zero profile is an equilibrium at every
generation. The agents never intervene (every chosen delta
is 0.0) because the gap is already 0 -- there is no
profitable deviation to find and no gap to close. The
equilibrium was never earned because it was never out of
reach, so check (c) of (x) fails (mean zero-gap 0.0, not
>= 0.002), and (xi) fails with gain exactly 0.0.

The (xii) label is the finding that matters: the agents
landed in the coordination trap, reproduced. The safe
all-zero equilibrium holds while a strictly better-synergy
equilibrium exists in the same table (0.0362 vs 0.0290),
and no single system gains by deviating alone -- that is
precisely the oes-coordination-lab trap (all-stay-local vs
all-switch), now measured in the SDF-synergy game. The
agents minimize the gap, not synergy, and a zero gap gives
them no reason to move toward the better equilibrium. A
synergy-seeking tie-break among zero-gap profiles is an open
question, not a fix applied silently.

Two structural findings behind the numbers. (1) The
population is heterogeneous: a few avatars are born with
stored variants -- a 3-flip trauma variant that lands on
another healthy sequence -- and those "fast healers" race
into the self-known region early (in the pilot, one avatar
had D = 0.308 at generation 0 and D = 0.738 by generation
1, while the bulk sat at D = 0.014). On seed 7 they made
delta matter from generation 7; on seed 11 no avatar is
inside until generation 6, and once inside, the +-5% lever
on lambda never moves an avatar across a bin boundary.
Coverage is set by birth variants and the healing curve, not
by attunement. (2) SDF synergy is transient: it peaks
mid-healing (0.0435 at gen 7 on seed 11) and falls as the
population converges (0.0145 by gen 9) -- as every D -> 1,
every theta -> 0, and the systems herd into the same few
bins near the stored state.

### Honest limits (v0.4.0)

- Classical emulation throughout; the synergy agents are
  bounded optimizers (greedy coordinate descent over 3 delta
  values), not minds.
- Nash here is over a finite 3-action-per-player
  pure-strategy game, exhaustively enumerated -- it says
  nothing about mixed equilibria, learning dynamics, or real
  systems. The equilibrium is a property of the supplied
  payoff table, not a law of nature.
- SDF synergy is a defined quantity in the model (joint
  region coverage minus mean individual coverage), not a
  claim about real synergy.
- Empathy entropy is a diagnostic only, never optimized.
- TISU is excluded from this package; `tests/test_exclusion.py`
  enforces the exclusion.
- No headline is allowed for this release (`HEADLINE_ALLOWED = False`).

## Tests

143 tests, all passing (`python -m pytest`, warnings are errors):
65 v0.1.0 tests + 23 v0.2.0 tests + 32 v0.3.0 tests + 23 new
v0.4.0 tests (equilibrium 7, sdf_synergy 8, synergy_agents 6,
v040 2).

Run the cascade report: `python -m quantum_projection` (prints the
v0.1.0 sweep tables followed by the cascade claims). Add `--v030`
for the v0.3.0 report (takes minutes: the agent run and the
500-generation long run). Add `--v040` for the v0.4.0 report
(takes minutes: 27 lookaheads per generation for the payoff
tables).
