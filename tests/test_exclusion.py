# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)
"""Exclusion guard: TISU and related private-theory terms must not
appear anywhere in the package or its tests. Also: every new
source/test file carries the SPDX + copyright header."""

import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
FORBIDDEN = ("tisu", "belkadi", "stress-test", "stress_test",
             "chrono-gravitation")


def test_no_forbidden_terms_in_code():
    hits = []
    for path in list((ROOT / "quantum_projection").glob("*.py")) + \
            list((ROOT / "tests").glob("*.py")):
        text = path.read_text(encoding="utf-8").lower()
        for term in FORBIDDEN:
            if term in text and term not in path.name:
                # The exclusion test itself names the terms; skip it.
                if path.name != "test_exclusion.py":
                    hits.append((str(path), term))
    assert hits == []


def test_copyright_headers_on_new_files():
    for name in ("dna_avatars.py", "trauma.py", "planetary.py",
                 "creativity.py", "unified.py", "solar_systems.py",
                 "eureka_agent.py", "sdf.py", "crystallize_events.py",
                 "longrun.py", "equilibrium.py", "sdf_synergy.py",
                 "synergy_agents.py"):
        text = (ROOT / "quantum_projection" / name).read_text(encoding="utf-8")
        assert "# SPDX-License-Identifier: AGPL-3.0-only" in text
        assert "# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)" in text
    for name in ("test_dna_avatars.py", "test_trauma.py",
                 "test_planetary.py", "test_creativity.py", "test_unified.py",
                 "test_exclusion.py", "test_metadata.py",
                 "test_solar_systems.py", "test_eureka_agent.py",
                 "test_sdf.py", "test_crystallize_events.py",
                 "test_longrun.py", "test_v030.py", "test_equilibrium.py",
                 "test_sdf_synergy.py", "test_synergy_agents.py",
                 "test_v040.py"):
        text = (ROOT / "tests" / name).read_text(encoding="utf-8")
        assert "# SPDX-License-Identifier: AGPL-3.0-only" in text
        assert "# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)" in text
