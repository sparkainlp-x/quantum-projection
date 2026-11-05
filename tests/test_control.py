import json

from quantum_projection.control import main, run_control


def test_paired_control_is_reproducible_and_reports_raw_differences():
    first = run_control(seed=61)
    second = run_control(seed=61)
    assert first == second
    assert first["status"] == "PASS"
    assert first["config"]["paired_cases"] == 36
    assert first["paired_results"]["max_complex_overlap_difference"] <= 1e-12
    assert first["paired_results"]["max_normalized_weight_difference"] <= 1e-12
    assert first["paired_results"]["max_pattern_fidelity_difference"] <= 1e-12
    assert first["paired_results"]["winner_mismatches_away_from_ties"] == 0
    assert len(first["paired_results"]["raw_paired_differences"]) == 36
    assert first["config"]["noise_added_before_shared_transform"] is True
    assert first["provenance"]["source_files"]
    assert first["provenance"]["package_version"]
    assert first["provenance"]["python"]
    assert first["provenance"]["platform"]
    json.dumps(first, allow_nan=False)


def test_control_cli_emits_strict_json(capsys):
    assert main(["--seed", "31"]) == 0
    output = capsys.readouterr().out
    result = json.loads(output, parse_constant=lambda value: (_ for _ in ()).throw(
        ValueError(f"invalid JSON number {value}")
    ))
    assert result["status"] == "PASS"
    assert result["provenance"]["command"] == [
        "quantum-projection-control", "--seed", "31"
    ]
    assert result["diagonal_readout_control"]["max_probability_difference"] <= 1e-12
    assert result["interference_control"]["max_amplitude_difference"] <= 1e-12
