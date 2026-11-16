# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)
"""Metadata consistency: version 0.4.0 everywhere, DOIs unchanged
(no new DOI invented; the v0.4.0 version DOI comes from Jean's
Zenodo release)."""

import json
import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent


def test_version_consistent():
    import quantum_projection
    assert quantum_projection.__version__ == "0.4.0"
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'version = "0.4.0"' in pyproject
    zenodo = json.loads((ROOT / ".zenodo.json").read_text(encoding="utf-8"))
    assert zenodo["version"] == "0.4.0"


def test_citation_dois_unchanged():
    with open(ROOT / "CITATION.cff", encoding="utf-8") as fh:
        cff = yaml.safe_load(fh)
    assert cff["version"] == "0.4.0"
    # v0.1.0 version DOI and the concept DOI stay exactly as they were;
    # the v0.4.0 version DOI does not exist yet.
    values = [i["value"] for i in cff["identifiers"]]
    assert "10.5281/zenodo.23530281" in values  # v0.1.0 version DOI
    assert "10.5281/zenodo.23530280" in values  # concept DOI
    assert cff["authors"][0]["family-names"] == "Brisson"
