from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"
HERO = ROOT / "assets" / "readme" / "hero-arabic-legal-framework.svg"


def test_readme_hero_exists_and_svg_is_safe():
    assert HERO.is_file()
    text = HERO.read_text(encoding="utf-8")
    root = ET.fromstring(text)
    assert root.tag.endswith("svg")
    assert root.attrib.get("viewBox")
    assert "<script" not in text.lower()
    assert "javascript:" not in text.lower()
    assert re.search(r"<image\b", text, re.IGNORECASE) is None
    assert re.search(r"@font-face|data:font|url\((?!#)", text, re.IGNORECASE) is None
    assert "arabic-legal-research-skill" in text
    assert "Ahmed Darhous" in text


def test_readme_footer_links_and_signature_are_exact():
    text = README.read_text(encoding="utf-8")
    expected = [
        "https://www.instagram.com/darhous/",
        "https://www.linkedin.com/in/darhous/",
        "https://www.facebook.com/ahmed.darhous",
        "https://wa.me/201030002331",
        "https://github.com/darhous",
    ]
    positions = [text.index(url) for url in expected]
    assert positions == sorted(positions)
    for label, url in zip(["Instagram", "LinkedIn", "Facebook", "WhatsApp", "GitHub"], expected, strict=True):
        pattern = (
            rf'<a href="{re.escape(url)}" target="_blank" rel="noopener noreferrer" '
            rf'aria-label="{label}">{label}</a>'
        )
        assert re.search(pattern, text)
    assert 'Designed &amp; Developed by <a href="mailto:ahmeddarhous@gmail.com">Ahmed Darhous</a>' in text


def test_readme_relative_links_exist_and_no_local_artifact_paths():
    text = README.read_text(encoding="utf-8")
    assert "tests_tmp" not in text
    assert "C:\\Users\\" not in text
    assert "/home/" not in text
    for target in re.findall(r"\]\(([^)]+)\)", text):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        assert not target.startswith("tests_tmp")
        assert (ROOT / target).exists(), target


def test_readme_cli_commands_use_existing_subcommands():
    text = README.read_text(encoding="utf-8")
    commands = re.findall(r"^legal-research-skill\s+([a-z-]+)", text, re.MULTILINE)
    assert commands
    allowed = {
        "validate",
        "schema-check",
        "list-validators",
        "explain",
        "render-docx",
        "validate-docx",
        "finalize-word",
        "build-artifact",
    }
    assert set(commands).issubset(allowed)


def test_readme_has_no_unsupported_english_claims():
    text = README.read_text(encoding="utf-8").lower()
    prohibited = [
        "print-ready",
        "word validated",
        "legal correctness",
        "submission-ready",
        "court-ready",
        "human reviewed",
        "source authenticity verified",
    ]
    for claim in prohibited:
        assert claim not in text
