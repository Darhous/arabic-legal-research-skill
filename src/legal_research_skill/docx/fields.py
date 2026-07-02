from __future__ import annotations


def toc_field(heading: str) -> str:
    return (
        '<w:p><w:pPr><w:pStyle w:val="Heading1"/><w:bidi/><w:jc w:val="center"/></w:pPr>'
        f"<w:r><w:t>{heading}</w:t></w:r></w:p>"
        '<w:p><w:pPr><w:bidi/><w:jc w:val="right"/></w:pPr>'
        '<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
        '<w:r><w:instrText xml:space="preserve">TOC \\o "1-5" \\h \\z \\u</w:instrText></w:r>'
        '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
        "<w:r><w:t>سيتم تحديث الفهرس في Microsoft Word.</w:t></w:r>"
        '<w:r><w:fldChar w:fldCharType="end"/></w:r>'
        "</w:p>"
    )


def page_field() -> str:
    return (
        "<w:r><w:t>صفحة </w:t></w:r>"
        '<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
        '<w:r><w:instrText xml:space="preserve">PAGE</w:instrText></w:r>'
        '<w:r><w:fldChar w:fldCharType="end"/></w:r>'
    )
