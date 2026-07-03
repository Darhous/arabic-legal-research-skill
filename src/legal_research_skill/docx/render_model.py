from __future__ import annotations

from dataclasses import asdict, dataclass, fields
from typing import Any

from legal_research_skill.constants import HIERARCHY_LABELS, PACKAGE_VERSION
from legal_research_skill.enums import Decision
from legal_research_skill.errors import ArtifactError
from legal_research_skill.models import ResearchState, ValidationReport, stable_hash

# Deliberately fixed, not datetime.now(): two independent CLI invocations of
# the same input must produce byte-identical DOCX output and manifests (see
# tests/acceptance/test_phase5_acceptance.py::test_reproducibility_...), and
# render_config_digest hashes this value as part of the render config. This
# is a build-epoch constant, not a real wall-clock timestamp -- callers that
# want a document to carry a genuine generation time must pass their own
# value explicitly via RenderConfig(created_at=...).
DEFAULT_BUILD_EPOCH = "2026-07-02T00:00:00Z"


@dataclass(frozen=True, slots=True)
class RenderConfig:
    page_width: int = 11906
    page_height: int = 16838
    margin_top: int = 1440
    margin_right: int = 1440
    margin_bottom: int = 1440
    margin_left: int = 1440
    default_arabic_font: str = "Traditional Arabic"
    fallback_font: str = "Arial"
    body_size_half_points: int = 28
    heading_size_half_points: int = 32
    footnote_size_half_points: int = 22
    line_spacing_twips: int = 420
    language: str = "ar-EG"
    toc_heading: str = "فهرس المحتويات"
    author_fallback: str = "غير محدد في حالة البحث"
    # A fixed build-epoch constant (see DEFAULT_BUILD_EPOCH above), not a
    # real generation timestamp -- do not treat this default as evidence of
    # when a document was actually produced. Pass an explicit value here for
    # a genuine wall-clock generation time.
    created_at: str = DEFAULT_BUILD_EPOCH
    update_fields_on_open: bool = True
    footnote_numbering: str = "sequential"
    include_page_numbers: bool = True

    def validate(self) -> None:
        numeric = (
            self.page_width,
            self.page_height,
            self.margin_top,
            self.margin_right,
            self.margin_bottom,
            self.margin_left,
            self.body_size_half_points,
            self.heading_size_half_points,
            self.footnote_size_half_points,
            self.line_spacing_twips,
        )
        if any(value <= 0 for value in numeric):
            raise ArtifactError("Render configuration numeric values must be positive.")
        if self.margin_left + self.margin_right >= self.page_width:
            raise ArtifactError("Horizontal margins must be smaller than the page width.")
        if self.margin_top + self.margin_bottom >= self.page_height:
            raise ArtifactError("Vertical margins must be smaller than the page height.")
        if not self.default_arabic_font.strip() or not self.fallback_font.strip():
            raise ArtifactError("Arabic font and fallback font must be configured.")
        if self.footnote_numbering not in {"sequential", "per_page_restart"}:
            raise ArtifactError("Footnote numbering must be sequential or per_page_restart.")

    def to_dict(self) -> dict[str, Any]:
        return {field.name: getattr(self, field.name) for field in fields(self)}


@dataclass(frozen=True, slots=True)
class RenderParagraph:
    text: str
    status: str = "verified"
    footnote_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class RenderHeading:
    heading_id: str
    parent_heading_id: str | None
    plan_node_id: str | None
    level_type: str
    display_label: str
    title: str
    order: int
    paragraphs: tuple[RenderParagraph, ...] = ()


@dataclass(frozen=True, slots=True)
class RenderFootnote:
    footnote_id: str
    number: int
    citation_ids: tuple[str, ...]
    content: str
    status: str


@dataclass(frozen=True, slots=True)
class RenderBibliographyEntry:
    bibliography_id: str
    source_ids: tuple[str, ...]
    entry_text: str
    status: str


@dataclass(frozen=True, slots=True)
class DocumentRenderModel:
    title: str
    work_type: str
    author: str
    generated_at: str
    headings: tuple[RenderHeading, ...]
    methodology: tuple[tuple[str, str], ...]
    conclusion: tuple[tuple[str, str], ...]
    footnotes: tuple[RenderFootnote, ...]
    bibliography: tuple[RenderBibliographyEntry, ...]
    config: RenderConfig
    draft_only: bool
    limitations: tuple[str, ...] = ()
    generator_version: str = PACKAGE_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "work_type": self.work_type,
            "author": self.author,
            "generated_at": self.generated_at,
            "headings": [asdict(heading) for heading in self.headings],
            "methodology": list(self.methodology),
            "conclusion": list(self.conclusion),
            "footnotes": [asdict(footnote) for footnote in self.footnotes],
            "bibliography": [asdict(entry) for entry in self.bibliography],
            "config": self.config.to_dict(),
            "draft_only": self.draft_only,
            "limitations": list(self.limitations),
            "generator_version": self.generator_version,
        }

    @property
    def digest(self) -> str:
        return stable_hash(self.to_dict())


METHODOLOGY_LABELS = {
    "preface": "تمهيد",
    "problem": "مشكلة الدراسة",
    "importance": "أهمية الدراسة",
    "previous_studies": "الدراسات السابقة",
    "objectives": "أهداف الدراسة",
    "methodology": "نوع ومنهج الدراسة",
    "scope": "حدود الدراسة",
    "hypotheses": "فروض الدراسة",
    "questions": "تساؤلات الدراسة",
    "tools": "أدوات الدراسة",
    "concepts": "مفاهيم الدراسة",
    "difficulties": "صعوبات الدراسة",
    "plan_presentation": "خطة الدراسة",
}

CONCLUSION_LABELS = {
    "summary": "ملخص الخاتمة",
    "findings": "النتائج",
    "recommendations": "التوصيات",
}


def build_render_model(
    state: ResearchState,
    validation_report: ValidationReport,
    *,
    config: RenderConfig | None = None,
) -> DocumentRenderModel:
    config = config or RenderConfig()
    config.validate()
    decision = validation_report.overall_decision
    if decision in {Decision.FAIL, Decision.PAUSE}:
        raise ArtifactError(f"Phase 3 decision {decision.value} blocks DOCX artifact generation.")

    data = state.serialize()
    metadata = data["research_metadata"]
    title = _status_value(metadata["research_title"], "بحث قانوني عربي")
    author = _status_value(metadata.get("researcher_name", {}), config.author_fallback)
    work_type = str(metadata.get("required_output_type", "docx_requested"))
    footnotes = _render_footnotes(data.get("footnotes", []))
    footnotes_by_heading = _footnotes_by_heading(data.get("footnotes", []))
    headings = tuple(
        _render_heading(item, footnotes_by_heading.get(str(item["heading_id"]), ()))
        for item in sorted(data["body_hierarchy"]["nodes"], key=lambda node: (node["order"], node["heading_id"]))
    )
    limitations = set(validation_report.limitations)
    if decision == Decision.REVISE:
        limitations.add("Phase 3 returned REVISE; generated DOCX is draft-only and requires review.")
    if any(footnote.status == "requires_verification" for footnote in footnotes):
        limitations.add("One or more footnotes require verification and are visibly marked.")
    if data["formatting_profile"].get("rtl_validated") is not True:
        limitations.add("Input state did not previously validate RTL rendering; Phase 4 applies structural RTL.")

    return DocumentRenderModel(
        title=title,
        work_type=work_type,
        author=author,
        generated_at=config.created_at,
        headings=headings,
        methodology=_component_items(data["methodology"]["components"], METHODOLOGY_LABELS),
        conclusion=_component_items(data["methodology"]["conclusion"], CONCLUSION_LABELS),
        footnotes=footnotes,
        bibliography=_render_bibliography(data.get("bibliography", [])),
        config=config,
        draft_only=decision == Decision.REVISE,
        limitations=tuple(sorted(limitations)),
    )


def _status_value(value: dict[str, Any], fallback: str) -> str:
    result = value.get("value") if isinstance(value, dict) else None
    return str(result) if result else fallback


def _component_items(raw: dict[str, Any], labels: dict[str, str]) -> tuple[tuple[str, str], ...]:
    items = []
    for key, label in labels.items():
        item = raw.get(key, {})
        content = item.get("content") if isinstance(item, dict) else None
        if content:
            items.append((label, str(content)))
    return tuple(items)


def _footnotes_by_heading(raw: list[dict[str, Any]]) -> dict[str, tuple[str, ...]]:
    by_heading: dict[str, list[str]] = {}
    for item in raw:
        placement = str(item.get("placement_reference", ""))
        if placement.startswith("body:"):
            by_heading.setdefault(placement.removeprefix("body:"), []).append(str(item["footnote_id"]))
    return {key: tuple(value) for key, value in by_heading.items()}


def _render_heading(item: dict[str, Any], footnote_ids: tuple[str, ...]) -> RenderHeading:
    label = HIERARCHY_LABELS.get(str(item["level_type"]), str(item["display_label"]))
    paragraph = RenderParagraph(
        "لم يتضمن نموذج حالة البحث متنًا تفصيليًا مستقلًا لهذا العنوان؛ لذلك يظهر العنوان مع الإحالات المتاحة فقط.",
        status="draft-only",
        footnote_ids=footnote_ids,
    )
    return RenderHeading(
        heading_id=str(item["heading_id"]),
        parent_heading_id=item.get("parent_heading_id"),
        plan_node_id=item.get("plan_node_id"),
        level_type=str(item["level_type"]),
        display_label=label,
        title=str(item["title"]),
        order=int(item["order"]),
        paragraphs=(paragraph,),
    )


def _render_footnotes(raw: list[dict[str, Any]]) -> tuple[RenderFootnote, ...]:
    return tuple(
        RenderFootnote(
            footnote_id=str(item["footnote_id"]),
            number=index,
            citation_ids=tuple(str(citation_id) for citation_id in item.get("citation_ids", [])),
            content=_with_verification_marker(str(item["content"]), str(item["verification_status"])),
            status=str(item["verification_status"]),
        )
        for index, item in enumerate(sorted(raw, key=lambda node: node["footnote_id"]), start=2)
    )


def _render_bibliography(raw: list[dict[str, Any]]) -> tuple[RenderBibliographyEntry, ...]:
    return tuple(
        RenderBibliographyEntry(
            bibliography_id=str(item["bibliography_id"]),
            source_ids=tuple(str(source_id) for source_id in item.get("source_ids", [])),
            entry_text=_with_verification_marker(str(item["entry_text"]), str(item["verification_status"])),
            status=str(item["verification_status"]),
        )
        for item in sorted(raw, key=lambda node: (node["entry_text"], node["bibliography_id"]))
    )


def _with_verification_marker(text: str, status: str) -> str:
    if status == "requires_verification" and "Requires Verification" not in text:
        return f"{text} [Requires Verification]"
    return text
