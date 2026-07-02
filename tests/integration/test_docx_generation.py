from __future__ import annotations

import json
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from legal_research_skill.docx.render_model import RenderConfig, build_render_model
from legal_research_skill.docx.renderer import render_docx
from legal_research_skill.docx.validation import validate_docx
from legal_research_skill.models import ResearchState
from legal_research_skill.pipeline import run_pipeline

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def _model(root):
    path = root / "examples/fixtures/valid/approved-plan-locked.json"
    report = run_pipeline(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    return build_render_model(ResearchState(data), report, config=RenderConfig(created_at="2026-07-02T00:00:00Z"))


def test_docx_generation_is_structurally_valid_and_contains_arabic_ooxml(root, tmp_path):
    output = tmp_path / "بحث.docx"
    render_docx(_model(root), output)
    report = validate_docx(output)
    assert report.status == "pass"
    with ZipFile(output) as archive:
        names = set(archive.namelist())
        assert "word/document.xml" in names
        assert "word/footnotes.xml" in names
        document = ET.fromstring(archive.read("word/document.xml"))
        footer = ET.fromstring(archive.read("word/footer1.xml"))
        styles = ET.fromstring(archive.read("word/styles.xml"))
        text = "".join(node.text or "" for node in document.findall(f".//{W}t"))
        instr = "".join(node.text or "" for node in document.findall(f".//{W}instrText"))
        instr += "".join(node.text or "" for node in footer.findall(f".//{W}instrText"))
    assert "المسؤولية المدنية" in text
    assert "TOC" in instr
    assert "PAGE" in instr
    assert document.find(f".//{W}bidi") is not None
    assert document.find(f".//{W}rtl") is not None
    assert document.find(f".//{W}footnoteReference") is not None
    assert styles.find(f".//{W}style[@{W}styleId='Heading1']/{W}pPr/{W}outlineLvl") is not None


def test_pre_word_docx_generation_is_byte_deterministic(root, tmp_path):
    model = _model(root)
    first = tmp_path / "first.docx"
    second = tmp_path / "second.docx"
    render_docx(model, first)
    render_docx(model, second)
    assert first.read_bytes() == second.read_bytes()


def test_docx_validator_rejects_malicious_package(tmp_path):
    path = tmp_path / "bad.docx"
    with ZipFile(path, "w") as archive:
        archive.writestr("../evil.xml", "<x/>")
    report = validate_docx(path)
    assert report.status == "fail"
    assert any(finding.code == "unsafe_part_name" for finding in report.findings)
