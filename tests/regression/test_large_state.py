from __future__ import annotations

import json

from legal_research_skill.pipeline import run_pipeline


def test_large_synthetic_state_completes(root, minimal_data, tmp_path):
    data = minimal_data
    data["sources"] = []
    data["citations"] = []
    data["footnotes"] = []
    data["bibliography"] = []
    for index in range(500):
        source_id = f"src-{index}"
        data["sources"].append(
            {
                "source_id": source_id,
                "title": f"مصدر {index}",
                "source_type": "law",
                "authority_level": "primary_legal",
                "authors": [],
                "institution": "جهة رسمية",
                "jurisdiction": "Egypt",
                "publication_date": "2020",
                "url_or_location": "archive",
                "uploaded_file": None,
                "exclusive_use": False,
                "verification_status": "verified",
                "verification_notes": "Synthetic source.",
                "bibliographic_data": {"title": f"مصدر {index}", "year": "2020"},
                "used_in_research": True,
                "include_in_bibliography": True,
            }
        )
        data["bibliography"].append(
            {
                "bibliography_id": f"bib-{index}",
                "source_ids": [source_id],
                "entry_text": f"مصدر {index}، 2020.",
                "used_source": True,
                "authorized_unused": False,
                "authorization_reason": None,
                "verification_status": "verified",
            }
        )
    for index in range(1000):
        source_id = f"src-{index % 500}"
        citation_id = f"cite-{index}"
        data["citations"].append(
            {
                "citation_id": citation_id,
                "source_id": source_id,
                "claim_id": f"claim-{index}",
                "usage_type": "support",
                "direct_quote": False,
                "quote_marks_present": False,
                "location": "مادة 1",
                "verification_status": "verified",
                "marker_id": None,
                "footnote_required": True,
            }
        )
        data["footnotes"].append(
            {
                "footnote_id": f"fn-{index}",
                "citation_ids": [citation_id],
                "content": f"إحالة رقم {index}.",
                "purpose_reason": None,
                "placement_reference": "body:heading-part-1",
                "numbering_intent": "sequential",
                "verification_status": "verified",
            }
        )
    path = tmp_path / "large.json"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    report = run_pipeline(path)
    assert report.overall_decision == "PROCEED"
