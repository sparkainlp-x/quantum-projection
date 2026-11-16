"""quantum_projection: SYNTHETIC classical emulation of quantum kinematics.

Amplitude-encoded statevectors in a complex outer-product memory,
overlap-based projection, and lossy Haar coarse-graining. Standard
library only. No speedup, no Bell violation.
"""

from .creativity import creativity_run, creativity_verdict
from .crystallize_events import brier, crystallize_points, crystallize_verdict
from .dna_avatars import (HEALTHY_SEQUENCES, avatar_state, dominant_sequence,
                          encode_sequence, energy_of, gc_content,
                          healthy_membrane, index_to_sequence, make_avatar,
                          make_population, mutate_sequence, sequence_index,
                          self_knowing, trauma_variant)
from .eureka_agent import (agent_run, agent_verdict, concurrence_pure,
                           empathy_entropy, love_of_d)
from .equilibrium import (DELTA_GRID, analyze_profile, audit_table,
                          equilibrium_gap, find_pure_equilibria,
                          is_epsilon_equilibrium, validate_game)
from .longrun import creativity_horizon, long_run
from .membrane import HolographicMembrane, KetBraPair, coarse_grain, overlap
from .planetary import planetary_run, planetary_verdict
from .qsim import (bell_phi_minus, bell_phi_plus, bell_psi_minus, bell_psi_plus,
                   fidelity, ghz, inner, noisy, normalize, plus_product,
                   random_state, w_state, zero)
from .sdf import population_sdf, sdf_grid, sdf_of_d, sdf_verdict
from .sdf_synergy import (marginal_contribution, region_bins,
                          region_coverage, synergy_series_from_records)
from .solar_systems import (contagion_verdict, couple_systems,
                            make_shocked_population, run_solar_systems)
from .synergy_agents import (choose_deltas_by_gap, gap_verdict,
                             payoff_table, stability_verdict, synergy_run,
                             synergy_verdict)
from .trauma import (discord, generation_step, healing_verdict, run_cascade)
from .unified import (HEADLINE_ALLOWED, cascade_claims, cascade_report,
                      v030_claims, v030_report, v040_claims, v040_report)

__version__ = "0.4.0"
__all__ = [
    "HolographicMembrane", "KetBraPair", "coarse_grain", "overlap",
    "bell_phi_plus", "bell_phi_minus", "bell_psi_plus", "bell_psi_minus",
    "fidelity", "ghz", "inner", "noisy", "normalize", "plus_product",
    "random_state", "w_state", "zero", "__version__",
    "HEALTHY_SEQUENCES", "avatar_state", "dominant_sequence",
    "encode_sequence", "energy_of", "gc_content", "healthy_membrane",
    "index_to_sequence", "make_avatar", "make_population", "mutate_sequence",
    "sequence_index", "self_knowing", "trauma_variant", "discord",
    "generation_step", "healing_verdict", "run_cascade", "planetary_run",
    "planetary_verdict", "creativity_run", "creativity_verdict",
    "HEADLINE_ALLOWED", "cascade_claims", "cascade_report",
    "run_solar_systems", "couple_systems", "make_shocked_population",
    "contagion_verdict", "love_of_d", "concurrence_pure",
    "empathy_entropy", "agent_run", "agent_verdict", "sdf_of_d",
    "sdf_grid", "population_sdf", "sdf_verdict", "brier",
    "crystallize_points", "crystallize_verdict", "creativity_horizon",
    "long_run", "v030_claims", "v030_report",
    "DELTA_GRID", "validate_game", "analyze_profile",
    "find_pure_equilibria", "equilibrium_gap", "is_epsilon_equilibrium",
    "audit_table", "region_bins", "region_coverage",
    "marginal_contribution", "synergy_series_from_records",
    "payoff_table", "choose_deltas_by_gap", "synergy_run",
    "gap_verdict", "synergy_verdict", "stability_verdict",
    "v040_claims", "v040_report",
]
