from __future__ import annotations

from html import escape
from pathlib import Path

from legal_research_skill.docx.fields import page_field, toc_field
from legal_research_skill.docx.package import write_docx_package
from legal_research_skill.docx.render_model import DocumentRenderModel, RenderConfig
from legal_research_skill.docx.rtl import is_ltr_token, paragraph_properties, run_properties
from legal_research_skill.docx.styles import styles_xml

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

HEADING_LEVELS = {"part": 1, "chapter": 2, "section": 3, "subsection": 4, "demand": 5}


def render_docx(model: DocumentRenderModel, output: Path) -> None:
    model.config.validate()
    write_docx_package(_parts(model), output)


def _parts(model: DocumentRenderModel) -> dict[str, str]:
    return {
        "[Content_Types].xml": _content_types(),
        "_rels/.rels": _package_rels(),
        "docProps/app.xml": _app_xml(),
        "docProps/core.xml": _core_xml(model),
        "word/_rels/document.xml.rels": _document_rels(),
        "word/document.xml": _document_xml(model),
        "word/footnotes.xml": _footnotes_xml(model),
        "word/footer1.xml": _footer_xml(model.config),
        "word/header1.xml": _header_xml(model),
        "word/settings.xml": _settings_xml(model.config),
        "word/styles.xml": styles_xml(model.config),
    }


def _content_types() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        '<Override PartName="/word/styles.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
        '<Override PartName="/word/settings.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>'
        '<Override PartName="/word/footnotes.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footnotes+xml"/>'
        '<Override PartName="/word/header1.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"/>'
        '<Override PartName="/word/footer1.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>'
        '<Override PartName="/docProps/core.xml" '
        'ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
        '<Override PartName="/docProps/app.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>'
        "</Types>"
    )


def _package_rels() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="word/document.xml"/>'
        '<Relationship Id="rId2" '
        'Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" '
        'Target="docProps/core.xml"/>'
        '<Relationship Id="rId3" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" '
        'Target="docProps/app.xml"/>'
        "</Relationships>"
    )


def _document_rels() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
        '<Relationship Id="rId2" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>'
        '<Relationship Id="rId3" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footnotes" Target="footnotes.xml"/>'
        '<Relationship Id="rId4" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/header" Target="header1.xml"/>'
        '<Relationship Id="rId5" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/>'
        "</Relationships>"
    )


def _app_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" '
        'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">'
        "<Application>legal_research_skill</Application></Properties>"
    )


def _core_xml(model: DocumentRenderModel) -> str:
    title = escape(model.title)
    author = escape(model.author)
    created = escape(model.generated_at)
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
        'xmlns:dc="http://purl.org/dc/elements/1.1/" '
        'xmlns:dcterms="http://purl.org/dc/terms/" '
        'xmlns:dcmitype="http://purl.org/dc/dcmitype/" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
        f"<dc:title>{title}</dc:title><dc:creator>{author}</dc:creator>"
        "<dc:subject>Arabic legal research DOCX draft</dc:subject>"
        "<cp:keywords>DOCX; RTL; Arabic legal research; structurally validated</cp:keywords>"
        f'<dcterms:created xsi:type="dcterms:W3CDTF">{created}</dcterms:created>'
        f'<dcterms:modified xsi:type="dcterms:W3CDTF">{created}</dcterms:modified>'
        "</cp:coreProperties>"
    )


def _document_xml(model: DocumentRenderModel) -> str:
    footnote_numbers = {footnote.footnote_id: footnote.number for footnote in model.footnotes}
    body = [
        _title_page(model),
        _section_heading("المقدمة المنهجية", 1),
        *(_labeled_paragraph(label, text, model.config) for label, text in model.methodology),
        _section_heading("متن البحث", 1),
    ]
    for heading in model.headings:
        body.append(_heading(heading.display_label, heading.title, HEADING_LEVELS[heading.level_type]))
        for paragraph in heading.paragraphs:
            body.append(
                _paragraph(
                    paragraph.text, model.config, footnote_ids=paragraph.footnote_ids, footnote_numbers=footnote_numbers
                )
            )
    body.extend(
        [
            _section_heading("الخاتمة", 1),
            *(_labeled_paragraph(label, text, model.config) for label, text in model.conclusion),
            _section_heading("قائمة المراجع", 1),
            *(_paragraph(entry.entry_text, model.config) for entry in model.bibliography),
            _page_break(),
            toc_field(escape(model.config.toc_heading)),
            _sect_pr(model.config),
        ]
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:document xmlns:w="{W_NS}" xmlns:r="{R_NS}"><w:body>'
        f"{''.join(body)}"
        "</w:body></w:document>"
    )


def _title_page(model: DocumentRenderModel) -> str:
    return (
        _paragraph(model.title, model.config, style="Title", align="center")
        + _paragraph(model.work_type, model.config, align="center")
        + _paragraph(f"الباحث: {model.author}", model.config, align="center")
        + _paragraph(f"تاريخ التوليد: {model.generated_at}", model.config, align="center")
        + _page_break()
    )


def _section_heading(text: str, level: int) -> str:
    return _heading("", text, level)


def _heading(label: str, title: str, level: int) -> str:
    text = f"{label} {title}".strip()
    page_break = "<w:pageBreakBefore/>" if level == 4 else ""
    return (
        f'<w:p><w:pPr><w:pStyle w:val="Heading{level}"/><w:bidi/><w:keepNext/><w:keepLines/>'
        f'{page_break}<w:jc w:val="center"/></w:pPr><w:r><w:rPr><w:b/><w:rtl/></w:rPr>'
        f"<w:t>{escape(text)}</w:t></w:r></w:p>"
    )


def _labeled_paragraph(label: str, text: str, config: RenderConfig) -> str:
    return _paragraph(f"{label}: {text}", config)


def _paragraph(
    text: str,
    config: RenderConfig,
    *,
    style: str | None = None,
    align: str = "both",
    footnote_ids: tuple[str, ...] = (),
    footnote_numbers: dict[str, int] | None = None,
) -> str:
    ppr = paragraph_properties(style, align=align)
    runs = _text_runs(text, config)
    for footnote_id in footnote_ids:
        number = (footnote_numbers or {}).get(footnote_id)
        if number is not None:
            runs += f'<w:r><w:rPr><w:rtl/></w:rPr><w:footnoteReference w:id="{number}"/></w:r>'
    return f"<w:p>{ppr}{runs}</w:p>"


def _text_runs(text: str, config: RenderConfig) -> str:
    runs = []
    for token in text.split(" "):
        if not token:
            continue
        rtl = not is_ltr_token(token)
        value = escape(token + " ")
        properties = run_properties(
            config.default_arabic_font,
            config.fallback_font,
            config.body_size_half_points,
            config.language,
            rtl=rtl,
        )
        runs.append(f'<w:r>{properties}<w:t xml:space="preserve">{value}</w:t></w:r>')
    return "".join(runs)


def _page_break() -> str:
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def _sect_pr(config: RenderConfig) -> str:
    restart = "eachPage" if config.footnote_numbering == "per_page_restart" else "continuous"
    return (
        "<w:sectPr>"
        '<w:headerReference w:type="default" r:id="rId4"/>'
        '<w:footerReference w:type="default" r:id="rId5"/>'
        f'<w:pgSz w:w="{config.page_width}" w:h="{config.page_height}"/>'
        f'<w:pgMar w:top="{config.margin_top}" w:right="{config.margin_right}" '
        f'w:bottom="{config.margin_bottom}" w:left="{config.margin_left}" w:header="720" w:footer="720" w:gutter="0"/>'
        f'<w:footnotePr><w:numRestart w:val="{restart}"/></w:footnotePr>'
        "</w:sectPr>"
    )


def _footnotes_xml(model: DocumentRenderModel) -> str:
    notes = [
        '<w:footnote w:type="separator" w:id="-1"><w:p><w:r><w:separator/></w:r></w:p></w:footnote>',
        '<w:footnote w:type="continuationSeparator" w:id="0">'
        "<w:p><w:r><w:continuationSeparator/></w:r></w:p></w:footnote>",
    ]
    for note in model.footnotes:
        note_text = _text_runs(note.content, model.config)
        notes.append(
            f'<w:footnote w:id="{note.number}"><w:p>{paragraph_properties("FootnoteText", align="right")}'
            f"<w:r><w:rPr><w:rtl/></w:rPr><w:footnoteRef/></w:r>{note_text}</w:p></w:footnote>"
        )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:footnotes xmlns:w="{W_NS}">{"".join(notes)}</w:footnotes>'
    )


def _header_xml(model: DocumentRenderModel) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:hdr xmlns:w="{W_NS}" xmlns:r="{R_NS}">'
        f"{_paragraph(model.title, model.config, align='center')}</w:hdr>"
    )


def _footer_xml(config: RenderConfig) -> str:
    content = page_field() if config.include_page_numbers else ""
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:ftr xmlns:w="{W_NS}" xmlns:r="{R_NS}"><w:p>{paragraph_properties(align="center")}{content}</w:p></w:ftr>'
    )


def _settings_xml(config: RenderConfig) -> str:
    update = '<w:updateFields w:val="true"/>' if config.update_fields_on_open else ""
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:settings xmlns:w="{W_NS}">{update}<w:defaultTabStop w:val="720"/></w:settings>'
    )
