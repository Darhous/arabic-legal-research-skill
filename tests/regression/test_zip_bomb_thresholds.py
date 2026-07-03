from __future__ import annotations

from dataclasses import dataclass
from zipfile import ZIP_DEFLATED, ZipFile

from legal_research_skill.docx import validation
from legal_research_skill.docx.validation import validate_docx


@dataclass
class FakeInfo:
    filename: str
    file_size: int
    compress_size: int


class FakeArchive:
    def __init__(self, infos: list[FakeInfo]):
        self._infos = infos

    def infolist(self):
        return self._infos


def _codes(infos: list[FakeInfo]) -> set[str]:
    return {finding.code for finding in validation._compression_findings(FakeArchive(infos))}


# --- Small, legitimate, highly-compressible content must not be flagged ---


def test_small_highly_compressible_xml_is_not_flagged():
    # A tiny part with a huge ratio (e.g. a short, empty, or boilerplate XML
    # part that happens to compress extremely well) is not a bomb risk.
    infos = [FakeInfo("word/empty.xml", file_size=2000, compress_size=10)]
    assert _codes(infos) == set()


def test_legitimate_long_repeated_arabic_text_is_not_flagged():
    # Reproduces the original false-positive: long, legitimate, repetitive
    # text compresses at a very high ratio but the compressed payload is
    # still small.
    infos = [FakeInfo("word/document.xml", file_size=3_000_000, compress_size=3000)]
    assert _codes(infos) == set()


def test_empty_and_zero_size_parts_are_ignored():
    infos = [FakeInfo("word/empty.xml", file_size=0, compress_size=0)]
    assert _codes(infos) == set()


# --- Genuinely suspicious ratios on substantial payloads are still caught -


def test_large_compressed_payload_with_high_ratio_is_flagged():
    infos = [FakeInfo("word/document.xml", file_size=50_000_000, compress_size=50_000)]
    codes = _codes(infos)
    assert "suspicious_compression_ratio" in codes


def test_ratio_at_threshold_boundary_is_not_flagged():
    infos = [FakeInfo("word/document.xml", file_size=500_000, compress_size=5_000)]  # ratio == 100
    assert _codes(infos) == set()


def test_ratio_just_over_threshold_with_large_compressed_size_is_flagged():
    infos = [FakeInfo("word/document.xml", file_size=505_000, compress_size=5_000)]  # ratio == 101
    assert "suspicious_compression_ratio" in _codes(infos)


# --- Per-part and total-uncompressed limits catch bombs that dodge ratio --


def test_single_oversized_part_is_flagged_regardless_of_ratio():
    # A part whose ratio is modest (not individually suspicious) but whose
    # absolute uncompressed size is enormous is still a resource-exhaustion
    # risk and must be rejected on size alone.
    huge = validation.MAX_PART_UNCOMPRESSED_BYTES + 1
    infos = [FakeInfo("word/document.xml", file_size=huge, compress_size=huge // 10)]
    assert "oversized_part" in _codes(infos)


def test_many_moderate_parts_summing_past_total_limit_is_flagged():
    # Each individual part is under every per-part threshold (small ratio,
    # under the per-part size cap), but enough of them together would still
    # exhaust memory on decompression.
    part_size = validation.MAX_PART_UNCOMPRESSED_BYTES // 4
    count = 11  # count * part_size exceeds MAX_TOTAL_UNCOMPRESSED_BYTES while each part stays under the per-part cap
    infos = [FakeInfo(f"word/part{i}.xml", file_size=part_size, compress_size=part_size // 2) for i in range(count)]
    assert sum(info.file_size for info in infos) > validation.MAX_TOTAL_UNCOMPRESSED_BYTES
    assert "oversized_uncompressed_total" in _codes(infos)


def test_total_under_limit_with_many_small_parts_is_not_flagged():
    infos = [FakeInfo(f"word/part{i}.xml", file_size=1000, compress_size=500) for i in range(50)]
    assert _codes(infos) == set()


# --- End-to-end: a real DOCX with legitimate long Arabic text still passes


def test_real_docx_with_long_repetitive_arabic_text_part_passes_validation(tmp_path):
    long_arabic_paragraph = "الحماية القانونية للبيانات الشخصية في التشريع العربي. " * 4000
    path = tmp_path / "long-text.docx"
    with ZipFile(path, "w", compression=ZIP_DEFLATED) as archive:
        for part in validation.REQUIRED_PARTS:
            if part == "word/document.xml":
                archive.writestr(
                    part,
                    '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                    f"<w:body><w:p><w:r><w:t>{long_arabic_paragraph}</w:t></w:r></w:p>"
                    "<w:sectPr><w:pgSz/><w:pgMar/><w:bidi/><w:rtl/></w:sectPr>"
                    "</w:body></w:document>",
                )
            else:
                archive.writestr(part, "<x/>")
    report = validate_docx(path)
    assert not any(finding.code == "suspicious_compression_ratio" for finding in report.findings)
