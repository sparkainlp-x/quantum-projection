"""Bounded paired control for shared ZZ transformations.

SYNTHETIC classical statevector emulation only; no hardware or advantage
claim. The control checks the expected invariance, not recognition gain.
"""

import argparse
import hashlib
import json
import math
import platform
from pathlib import Path
import sys
from importlib.metadata import PackageNotFoundError, version

from . import __version__
from .membrane import HolographicMembrane
from .qsim import (H, apply_1q, apply_rzz, bell_phi_minus, bell_phi_plus,
                   bell_psi_plus, fidelity, noisy, plus_product, random_state,
                   zero)

ANGLE = 0.73
NOISE_SIGMA = 0.2
QUERY_SEEDS_PER_PATTERN = 12
TOLERANCE = 1e-12
WINNER_TIE_TOLERANCE = 1e-12


def _complex_pair(value):
    return [value.real, value.imag]


def _max_margin(overlaps):
    magnitudes = sorted((abs(value) for value in overlaps), reverse=True)
    return magnitudes[0] - magnitudes[1]


def _sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run_control(seed=2026, command=None):
    """Run a deterministic paired identity-vs-shared-RZZ control."""
    patterns = [random_state(2, seed + i) for i in range(3)]
    identity_membrane = HolographicMembrane(patterns)
    transformed_patterns = [apply_rzz(p, 0, 1, ANGLE) for p in patterns]
    transformed_membrane = HolographicMembrane(transformed_patterns)

    raw_differences = []
    winner_mismatches = 0
    excluded_ties = 0
    max_overlap_difference = 0.0
    max_probability_difference = 0.0
    max_fidelity_difference = 0.0
    query_seeds = []
    for pattern_index, pattern in enumerate(patterns):
        for replicate in range(QUERY_SEEDS_PER_PATTERN):
            query_seed = seed + 1000 + pattern_index * QUERY_SEEDS_PER_PATTERN + replicate
            query_seeds.append(query_seed)
            query = noisy(pattern, NOISE_SIGMA, query_seed)
            transformed_query = apply_rzz(query, 0, 1, ANGLE)
            identity_result = identity_membrane.project(query)
            transformed_result = transformed_membrane.project(transformed_query)
            overlap_differences = [
                a - b for a, b in zip(identity_result["overlaps"],
                                      transformed_result["overlaps"])
            ]
            probability_differences = [
                a - b for a, b in zip(identity_result["probs"],
                                      transformed_result["probs"])
            ]
            fidelity_differences = [
                fidelity(p, query) - fidelity(tp, transformed_query)
                for p, tp in zip(identity_membrane.patterns,
                                 transformed_membrane.patterns)
            ]
            overlap_error = max(abs(value) for value in overlap_differences)
            probability_error = max(abs(value) for value in probability_differences)
            fidelity_error = max(abs(value) for value in fidelity_differences)
            max_overlap_difference = max(max_overlap_difference, overlap_error)
            max_probability_difference = max(
                max_probability_difference, probability_error
            )
            max_fidelity_difference = max(max_fidelity_difference, fidelity_error)
            identity_margin = _max_margin(identity_result["overlaps"])
            transformed_margin = _max_margin(transformed_result["overlaps"])
            eligible = (identity_margin > WINNER_TIE_TOLERANCE
                        and transformed_margin > WINNER_TIE_TOLERANCE)
            if not eligible:
                excluded_ties += 1
            elif identity_result["winner"] != transformed_result["winner"]:
                winner_mismatches += 1
            raw_differences.append({
                "pattern_index": pattern_index,
                "query_seed": query_seed,
                "identity_winner": identity_result["winner"],
                "zz_winner": transformed_result["winner"],
                "winner_comparison_eligible": eligible,
                "identity_winner_margin": identity_margin,
                "zz_winner_margin": transformed_margin,
                "complex_overlap_differences_real_imag": [
                    _complex_pair(value) for value in overlap_differences
                ],
                "probability_differences": probability_differences,
                "pattern_fidelity_differences": fidelity_differences,
            })

    readout_state = plus_product(2)
    readout_after_zz = apply_rzz(readout_state, 0, 1, ANGLE)
    probabilities_before = [abs(c) ** 2 for c in readout_state]
    probabilities_after = [abs(c) ** 2 for c in readout_after_zz]

    interference_state = zero(2)
    interference_state = apply_1q(interference_state, 0, H)
    interference_state = apply_1q(interference_state, 1, H)
    interference_state = apply_rzz(interference_state, 0, 1, ANGLE)
    interference_state = apply_1q(interference_state, 0, H)
    interference_state = apply_1q(interference_state, 1, H)
    interference_expected = [
        math.cos(ANGLE / 2), 0j, 0j, -1j * math.sin(ANGLE / 2)
    ]
    interference_error = max(
        abs(actual - expected)
        for actual, expected in zip(interference_state, interference_expected)
    )
    readout_probability_difference = max(
        abs(a - b) for a, b in zip(probabilities_before, probabilities_after)
    )

    package_dir = Path(__file__).resolve().parent
    source_files = {
        name: {
            "path": str(package_dir / name),
            "sha256": _sha256(package_dir / name),
        }
        for name in ("qsim.py", "membrane.py", "control.py")
    }
    try:
        package_version = version("quantum-projection")
    except PackageNotFoundError:
        package_version = __version__
    source_kind = ("checkout" if (package_dir.parent / "pyproject.toml").is_file()
                   else "installed_package")

    passed = (
        max_overlap_difference <= TOLERANCE
        and max_probability_difference <= TOLERANCE
        and max_fidelity_difference <= TOLERANCE
        and winner_mismatches == 0
        and readout_probability_difference <= TOLERANCE
        and interference_error <= TOLERANCE
    )
    return {
        "title": "Shared fixed ZZ layer paired invariance control",
        "label": "SYNTHETIC; classical statevector emulation; no hardware; no advantage claim",
        "expected_outcome": "invariance; no free recognition improvement",
        "status": "PASS" if passed else "FAIL",
        "provenance": {
            "source_kind": source_kind,
            "source_files": source_files,
            "package": "quantum-projection",
            "package_version": package_version,
            "python": sys.version,
            "platform": platform.platform(),
            "command": command or ["python", "-m", "quantum_projection.control",
                                   "--seed", str(seed)],
            "seeds": {
                "base": seed,
                "pattern_seeds": [seed + i for i in range(3)],
                "query_seeds": query_seeds,
            },
        },
        "config": {
            "qubits": 2,
            "patterns": 3,
            "queries_per_pattern": QUERY_SEEDS_PER_PATTERN,
            "paired_cases": len(raw_differences),
            "noise_sigma_per_real_component": NOISE_SIGMA,
            "noise_added_before_shared_transform": True,
            "rzz_angle_radians": ANGLE,
            "tolerance_absolute": TOLERANCE,
            "winner_tie_tolerance_on_overlap_magnitudes": WINNER_TIE_TOLERANCE,
        },
        "paired_results": {
            "max_complex_overlap_difference": max_overlap_difference,
            "max_normalized_weight_difference": max_probability_difference,
            "max_pattern_fidelity_difference": max_fidelity_difference,
            "winner_mismatches_away_from_ties": winner_mismatches,
            "excluded_tie_cases": excluded_ties,
            "raw_paired_differences": raw_differences,
        },
        "diagonal_readout_control": {
            "description": "RZZ changes phases only; computational probabilities are unchanged absent interference.",
            "probabilities_before": probabilities_before,
            "probabilities_after": probabilities_after,
            "max_probability_difference": readout_probability_difference,
        },
        "interference_control": {
            "description": "H tensor H -> RZZ(theta) -> H tensor H on |00>.",
            "basis_order": "|00>, |01>, |10>, |11>; qubit 0 is least-significant.",
            "actual_amplitudes_real_imag": [
                _complex_pair(value) for value in interference_state
            ],
            "analytical_amplitudes_real_imag": [
                _complex_pair(value) for value in interference_expected
            ],
            "max_amplitude_difference": interference_error,
            "probability_changes_only_after_interference": True,
        },
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="quantum-projection-control",
        description=("Bounded SYNTHETIC classical paired identity/ZZ invariance control; "
                     "outputs strict JSON.")
    )
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args(argv)
    result = run_control(args.seed, command=sys.argv)
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
