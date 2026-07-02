from __future__ import annotations

import pytest

from legal_research_skill.docx.render_model import RenderConfig, build_render_model
from legal_research_skill.errors import ArtifactError
from legal_research_skill.models import ResearchState
from legal_research_skill.pipeline import run_pipeline


def test_render_config_validation_rejects_invalid_values():
    with pytest.raises(ArtifactError, match="positive"):
        RenderConfig(page_width=0).validate()
    with pytest.raises(ArtifactError, match="Horizontal margins"):
        RenderConfig(page_width=100, margin_left=60, margin_right=60).validate()
    with pytest.raises(ArtifactError, match="Footnote numbering"):
        RenderConfig(footnote_numbering="chapter").validate()


def test_render_model_preserves_order_and_marks_revise(root):
    path = root / "examples/fixtures/valid/requires-verification-valid.json"
    report = run_pipeline(path)
    state = ResearchState(report_to_state(path))
    model = build_render_model(state, report, config=RenderConfig(created_at="2026-07-02T01:02:03Z"))
    assert model.draft_only is True
    assert [heading.order for heading in model.headings] == [1]
    assert "Requires Verification" in model.footnotes[0].content
    assert model.config.to_dict()["page_width"] == 11906


def test_phase3_fail_blocks_docx_generation(root):
    path = root / "examples/fixtures/invalid/unsupported-output-claim.json"
    report = run_pipeline(path)
    with pytest.raises(ArtifactError, match="FAIL"):
        build_render_model(ResearchState(report_to_state(path)), report)


def report_to_state(path):
    import json

    return json.loads(path.read_text(encoding="utf-8"))
