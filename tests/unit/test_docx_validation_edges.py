from __future__ import annotations

import json
from xml.etree import ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile

from legal_research_skill.docx import validation
from legal_research_skill.docx.validation import (
    DocxFinding,
    DocxValidationReport,
    report_to_json,
    report_to_text,
    validate_docx,
)


def test_docx_validator_reports_missing_invalid_and_oversized(tmp_path, monkeypatch):
    missing = validate_docx(tmp_path / "missing.docx")
    assert missing.status == "fail"
    assert missing.findings[0].code == "missing_file"

    invalid = tmp_path / "invalid.docx"
    invalid.write_text("not a zip", encoding="utf-8")
    assert validate_docx(invalid).findings[0].code == "invalid_zip"

    monkeypatch.setattr(validation, "MAX_DOCX_BYTES", 1)
    oversized = tmp_path / "oversized.docx"
    oversized.write_bytes(b"123")
    assert validate_docx(oversized).findings[0].code == "package_too_large"


def test_docx_report_serializers_cover_compact_and_text():
    report = DocxValidationReport(
        "x.docx",
        "fail",
        (DocxFinding("bad", "fail", "Bad package", {"part": "x"}),),
        ("zip_package",),
    )
    assert json.loads(report_to_json(report, compact=True))["findings"][0]["code"] == "bad"
    assert "Bad package" in report_to_text(report)


def test_package_security_findings_cover_blocked_parts():
    findings = validation._package_findings(
        [
            "[Content_Types].xml",
            "_rels/.rels",
            "word/document.xml",
            "word/styles.xml",
            "word/settings.xml",
            "word/_rels/document.xml.rels",
            "word/vbaProject.bin",
            "word/active.dll",
            "/absolute.xml",
            "word/../evil.xml",
            "word\\bad.xml",
        ]
    )
    codes = {finding.code for finding in findings}
    assert {"embedded_executable", "unsafe_part_name"} <= codes


def test_xml_semantic_findings_cover_relationships_styles_and_footnotes():
    w_ns = validation.W.removeprefix("{").removesuffix("}")
    rels = ET.fromstring(
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" TargetMode="External" Target="https://example.test"/>'
        "</Relationships>"
    )
    document = ET.fromstring(
        f'<w:document xmlns:w="{w_ns}">'
        '<w:body><w:p><w:r><w:t>نص</w:t></w:r><w:footnoteReference w:id="9"/></w:p></w:body>'
        "</w:document>"
    )
    styles = ET.fromstring(f'<w:styles xmlns:w="{w_ns}"><w:style w:type="paragraph" w:styleId="Heading1"/></w:styles>')
    footnotes = ET.fromstring(
        f'<w:footnotes xmlns:w="{w_ns}"><w:footnote w:id="2"/><w:footnote w:id="2"/></w:footnotes>'
    )
    codes = {finding.code for finding in validation._relationship_findings(rels)}
    codes |= {finding.code for finding in validation._document_findings(document, None)}
    codes |= {finding.code for finding in validation._style_findings(styles)}
    codes |= {finding.code for finding in validation._footnote_findings(document, footnotes)}
    assert "external_relationship" in codes
    assert "missing_page_setup" in codes
    assert "missing_rtl" in codes
    assert "missing_toc_field" in codes
    assert "missing_page_field" in codes
    assert "missing_heading_outline" in codes
    assert "duplicate_footnote_id" in codes
    assert "missing_footnotes" in codes
    assert "orphan_footnotes" in codes
    assert "footnote_rtl_missing" in codes


def test_relationship_duplicate_ids_are_reported():
    rels = ET.fromstring(
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Target="word/document.xml"/>'
        '<Relationship Id="rId1" Target="word/styles.xml"/>'
        "</Relationships>"
    )
    assert any(finding.code == "duplicate_relationship_id" for finding in validation._relationship_findings(rels))


def test_suspicious_compression_ratio_is_reported(tmp_path):
    path = tmp_path / "compressed.docx"
    with ZipFile(path, "w", compression=ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", "a" * 5000)
    report = validate_docx(path)
    assert any(finding.code == "suspicious_compression_ratio" for finding in report.findings)


def test_malformed_xml_part_is_reported(tmp_path):
    path = tmp_path / "malformed.docx"
    with ZipFile(path, "w") as archive:
        for part in validation.REQUIRED_PARTS:
            archive.writestr(part, "<not-closed" if part == "word/document.xml" else "<x/>")
    report = validate_docx(path)
    assert any(finding.code == "malformed_xml" for finding in report.findings)


def test_too_many_parts_branch():
    findings = validation._package_findings([f"part{i}.xml" for i in range(validation.MAX_PARTS + 1)])
    assert any(finding.code == "too_many_parts" for finding in findings)
