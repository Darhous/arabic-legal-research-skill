from __future__ import annotations

from legal_research_skill.docx.render_model import RenderConfig


def styles_xml(config: RenderConfig) -> str:
    heading_styles = "".join(_heading_style(level, config) for level in range(1, 6))
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:docDefaults><w:rPrDefault><w:rPr>"
        f'<w:rFonts w:ascii="{config.fallback_font}" w:hAnsi="{config.fallback_font}" '
        f'w:cs="{config.default_arabic_font}"/>'
        f'<w:sz w:val="{config.body_size_half_points}"/>'
        f'<w:szCs w:val="{config.body_size_half_points}"/>'
        f'<w:lang w:val="{config.language}" w:bidi="{config.language}"/>'
        "</w:rPr></w:rPrDefault></w:docDefaults>"
        '<w:style w:type="paragraph" w:default="1" w:styleId="Normal">'
        '<w:name w:val="Normal"/><w:qFormat/>'
        '<w:pPr><w:bidi/><w:widowControl/><w:jc w:val="both"/>'
        f'<w:spacing w:line="{config.line_spacing_twips}" w:lineRule="auto" w:after="120"/>'
        "</w:pPr></w:style>"
        '<w:style w:type="paragraph" w:styleId="Title">'
        '<w:name w:val="Title"/><w:qFormat/><w:pPr><w:bidi/><w:jc w:val="center"/></w:pPr>'
        f'<w:rPr><w:b/><w:rFonts w:cs="{config.default_arabic_font}" w:ascii="{config.fallback_font}" '
        f'w:hAnsi="{config.fallback_font}"/><w:sz w:val="40"/><w:szCs w:val="40"/></w:rPr></w:style>'
        f"{heading_styles}"
        '<w:style w:type="paragraph" w:styleId="FootnoteText">'
        '<w:name w:val="Footnote Text"/><w:pPr><w:bidi/><w:jc w:val="right"/></w:pPr>'
        f'<w:rPr><w:rFonts w:cs="{config.default_arabic_font}" w:ascii="{config.fallback_font}" '
        f'w:hAnsi="{config.fallback_font}"/><w:sz w:val="{config.footnote_size_half_points}"/>'
        f'<w:szCs w:val="{config.footnote_size_half_points}"/></w:rPr></w:style>'
        "</w:styles>"
    )


def _heading_style(level: int, config: RenderConfig) -> str:
    size = max(config.heading_size_half_points - ((level - 1) * 2), config.body_size_half_points)
    outline = level - 1
    return (
        f'<w:style w:type="paragraph" w:styleId="Heading{level}">'
        f'<w:name w:val="Heading {level}"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/>'
        "<w:pPr><w:keepNext/><w:keepLines/><w:bidi/><w:widowControl/>"
        f'<w:outlineLvl w:val="{outline}"/><w:jc w:val="center"/>'
        '<w:spacing w:before="240" w:after="120"/></w:pPr>'
        f'<w:rPr><w:b/><w:rFonts w:cs="{config.default_arabic_font}" w:ascii="{config.fallback_font}" '
        f'w:hAnsi="{config.fallback_font}"/><w:sz w:val="{size}"/><w:szCs w:val="{size}"/>'
        f'<w:lang w:val="{config.language}" w:bidi="{config.language}"/><w:rtl/></w:rPr>'
        "</w:style>"
    )
