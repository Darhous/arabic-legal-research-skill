from __future__ import annotations

import re

ARABIC_RE = re.compile(r"[\u0600-\u06ff]")
LTR_TOKEN_RE = re.compile(r"^(https?://|www\.|[A-Za-z0-9_.:/#?=&%-]+$)")


def contains_arabic(text: str) -> bool:
    return bool(ARABIC_RE.search(text))


def is_ltr_token(text: str) -> bool:
    return bool(LTR_TOKEN_RE.search(text.strip())) and not contains_arabic(text)


def paragraph_properties(style: str | None = None, *, align: str = "both", keep_next: bool = False) -> str:
    style_xml = f'<w:pStyle w:val="{style}"/>' if style else ""
    keep = "<w:keepNext/>" if keep_next else ""
    return f'<w:pPr>{style_xml}<w:bidi/>{keep}<w:widowControl/><w:jc w:val="{align}"/></w:pPr>'


def run_properties(font: str, fallback_font: str, size: int, language: str, *, rtl: bool = True) -> str:
    rtl_xml = "<w:rtl/>" if rtl else ""
    return (
        "<w:rPr>"
        f'<w:rFonts w:ascii="{fallback_font}" w:hAnsi="{fallback_font}" w:cs="{font}"/>'
        f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>'
        f'<w:lang w:val="{language}" w:bidi="{language}"/>'
        f"{rtl_xml}"
        "</w:rPr>"
    )
