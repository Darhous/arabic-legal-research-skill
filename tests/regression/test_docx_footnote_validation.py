from __future__ import annotations

import json
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from legal_research_skill.docx import validation
from legal_research_skill.docx.render_model import RenderConfig, build_render_model
from legal_research_skill.docx.renderer import render_docx
from legal_research_skill.docx.validation import validate_docx
from legal_research_skill.models import ResearchState
from legal_research_skill.pipeline import run_pipeline

W = validation.W


def _footnote_free_model(root):
    """A schema-valid research state with an empty footnotes array.

    Built from a copy of the tracked minimal-valid fixture (never mutates
    the tracked file); this reproduces the DOCX-1 finding, where a
    legitimately footnote-free document was incorrectly rejected by
    structural validation.
    """
    source = root / "examples" / "fixtures" / "valid" / "minimal-valid.json"
    data = json.loads(source.read_text(encoding="utf-8"))
    assert data["footnotes"], "fixture assumption changed: expected at least one footnote to strip"
    data["footnotes"] = []
    return data


def test_rendered_document_without_footnotes_passes_structural_validation(root, tmp_path):
    data = _footnote_free_model(root)
    state = ResearchState(data)
    # run_pipeline reads straight from disk, so materialize the modified
    # state into a scratch file rather than the tracked fixture.
    scratch_input = tmp_path / "footnote-free.json"
    scratch_input.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    report = run_pipeline(scratch_input)
    model = build_render_model(state, report, config=RenderConfig(created_at="2026-07-02T00:00:00Z"))
    assert model.footnotes == ()

    output = tmp_path / "footnote-free.docx"
    render_docx(model, output)
    docx_report = validate_docx(output)

    assert docx_report.status == "pass", docx_report.to_dict()
    assert not any(finding.code == "footnote_rtl_missing" for finding in docx_report.findings)
    with ZipFile(output) as archive:
        footnotes_xml = ET.fromstring(archive.read("word/footnotes.xml"))
    ids = {node.attrib.get(f"{W}id") for node in footnotes_xml.findall(f"{W}footnote")}
    assert ids == {"-1", "0"}, "only the mandatory separator/continuation entries should be present"


def test_rendered_document_with_real_footnote_still_passes(root, tmp_path):
    path = root / "examples" / "fixtures" / "valid" / "approved-plan-locked.json"
    report = run_pipeline(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    model = build_render_model(ResearchState(data), report, config=RenderConfig(created_at="2026-07-02T00:00:00Z"))
    assert model.footnotes, "fixture assumption changed: expected at least one real footnote"

    output = tmp_path / "with-footnote.docx"
    render_docx(model, output)
    docx_report = validate_docx(output)
    assert docx_report.status == "pass", docx_report.to_dict()


def _footnotes_xml(*bodies: str) -> ET.Element:
    w_ns = W.removeprefix("{").removesuffix("}")
    return ET.fromstring(f'<w:footnotes xmlns:w="{w_ns}">{"".join(bodies)}</w:footnotes>')


def _document_with_refs(*ref_ids: str) -> ET.Element:
    w_ns = W.removeprefix("{").removesuffix("}")
    refs = "".join(f'<w:footnoteReference w:id="{ref_id}"/>' for ref_id in ref_ids)
    return ET.fromstring(f'<w:document xmlns:w="{w_ns}"><w:body><w:p><w:r>{refs}</w:r></w:p></w:body></w:document>')


SEPARATOR_ONLY = (
    '<w:footnote w:type="separator" w:id="-1"><w:p><w:r><w:separator/></w:r></w:p></w:footnote>',
    '<w:footnote w:type="continuationSeparator" w:id="0"><w:p><w:r><w:continuationSeparator/></w:r></w:p></w:footnote>',
)


def test_separator_only_footnotes_part_has_no_findings():
    document = _document_with_refs()
    footnotes = _footnotes_xml(*SEPARATOR_ONLY)
    assert validation._footnote_findings(document, footnotes) == []


def test_real_footnote_with_bidi_and_matching_reference_has_no_findings():
    document = _document_with_refs("2")
    footnotes = _footnotes_xml(
        *SEPARATOR_ONLY,
        '<w:footnote w:id="2"><w:p><w:pPr><w:bidi/></w:pPr><w:r><w:t>x</w:t></w:r></w:p></w:footnote>',
    )
    assert validation._footnote_findings(document, footnotes) == []


def test_real_footnote_missing_bidi_is_reported_with_id():
    document = _document_with_refs("2")
    footnotes = _footnotes_xml(
        *SEPARATOR_ONLY,
        '<w:footnote w:id="2"><w:p><w:r><w:t>x</w:t></w:r></w:p></w:footnote>',
    )
    findings = validation._footnote_findings(document, footnotes)
    rtl_findings = [f for f in findings if f.code == "footnote_rtl_missing"]
    assert len(rtl_findings) == 1
    assert rtl_findings[0].evidence["ids"] == ["2"]


def test_orphan_real_footnote_without_reference_is_reported():
    document = _document_with_refs()  # no references at all
    footnotes = _footnotes_xml(
        *SEPARATOR_ONLY,
        '<w:footnote w:id="2"><w:p><w:pPr><w:bidi/></w:pPr><w:r><w:t>x</w:t></w:r></w:p></w:footnote>',
    )
    findings = validation._footnote_findings(document, footnotes)
    assert any(f.code == "orphan_footnotes" and f.evidence["ids"] == ["2"] for f in findings)


def test_duplicate_regular_footnote_ids_are_reported():
    document = _document_with_refs("2")
    footnotes = _footnotes_xml(
        *SEPARATOR_ONLY,
        '<w:footnote w:id="2"><w:p><w:pPr><w:bidi/></w:pPr><w:r><w:t>a</w:t></w:r></w:p></w:footnote>',
        '<w:footnote w:id="2"><w:p><w:pPr><w:bidi/></w:pPr><w:r><w:t>b</w:t></w:r></w:p></w:footnote>',
    )
    findings = validation._footnote_findings(document, footnotes)
    assert any(f.code == "duplicate_footnote_id" for f in findings)


def test_footnote_reference_without_footnotes_part_is_reported(tmp_path):
    # A crafted package where document.xml references a footnote but the
    # word/footnotes.xml part was never included at all.
    path = tmp_path / "broken.docx"
    with ZipFile(path, "w") as archive:
        for part in validation.REQUIRED_PARTS:
            if part == "word/document.xml":
                archive.writestr(
                    part,
                    '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                    "<w:body><w:p><w:r><w:t>x</w:t></w:r>"
                    '<w:footnoteReference w:id="2"/></w:p>'
                    "<w:sectPr><w:pgSz/><w:pgMar/></w:sectPr>"
                    "</w:body></w:document>",
                )
            else:
                archive.writestr(part, "<x/>")
    report = validate_docx(path)
    assert report.status == "fail"
    assert any(finding.code == "footnotes_part_missing" for finding in report.findings)


def test_no_references_and_no_footnotes_part_is_not_penalized_for_footnotes():
    # Absence of the footnotes part is only a problem when the document
    # actually references a footnote; a document that never uses footnotes
    # at all should not be forced to carry an empty footnotes.xml part.
    document = _document_with_refs()
    assert validation._has_footnote_references(document) is False
