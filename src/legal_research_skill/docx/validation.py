from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZipFile

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
REL = "{http://schemas.openxmlformats.org/package/2006/relationships}"

REQUIRED_PARTS = {
    "[Content_Types].xml",
    "_rels/.rels",
    "word/document.xml",
    "word/styles.xml",
    "word/settings.xml",
    "word/_rels/document.xml.rels",
}
BLOCKED_SUFFIXES = (".bin", ".exe", ".dll", ".vba", ".vbs", ".js", ".ole")
MAX_PARTS = 512
MAX_DOCX_BYTES = 50 * 1024 * 1024
MAX_COMPRESSION_RATIO = 100


@dataclass(frozen=True, slots=True)
class DocxFinding:
    code: str
    status: str
    message: str
    evidence: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "status": self.status,
            "message": self.message,
            "evidence": self.evidence,
        }


@dataclass(frozen=True, slots=True)
class DocxValidationReport:
    path: str
    status: str
    findings: tuple[DocxFinding, ...]
    checks: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_type": "docx_validation",
            "path": self.path,
            "status": self.status,
            "checks": list(self.checks),
            "findings": [finding.to_dict() for finding in self.findings],
        }


def validate_docx(path: Path) -> DocxValidationReport:
    findings: list[DocxFinding] = []
    checks: list[str] = []
    if not path.exists() or not path.is_file():
        return _report(path, [DocxFinding("missing_file", "fail", "DOCX file does not exist.", {})], checks)
    if path.stat().st_size > MAX_DOCX_BYTES:
        return _report(
            path, [DocxFinding("package_too_large", "fail", "DOCX exceeds configured size limit.", {})], checks
        )
    try:
        with ZipFile(path) as archive:
            names = archive.namelist()
            findings.extend(_package_findings(names))
            findings.extend(_compression_findings(archive))
            if not findings:
                findings.extend(_xml_findings(archive))
                checks.extend(
                    [
                        "zip_package",
                        "required_parts",
                        "relationships",
                        "document_xml",
                        "styles_outline",
                        "rtl_properties",
                        "fields",
                        "footnotes",
                        "page_setup",
                        "security",
                    ]
                )
    except BadZipFile:
        findings.append(DocxFinding("invalid_zip", "fail", "DOCX is not a valid ZIP package.", {}))
    status = "pass" if not findings else "fail"
    return DocxValidationReport(str(path), status, tuple(findings), tuple(checks))


def report_to_json(report: DocxValidationReport, *, compact: bool = False) -> str:
    if compact:
        return json.dumps(report.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    return json.dumps(report.to_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def report_to_text(report: DocxValidationReport) -> str:
    lines = [f"DOCX validation: {report.status}", f"Path: {report.path}"]
    for finding in report.findings:
        lines.append(f"- {finding.code}: {finding.message}")
    return "\n".join(lines) + "\n"


def _report(path: Path, findings: list[DocxFinding], checks: list[str]) -> DocxValidationReport:
    return DocxValidationReport(str(path), "fail", tuple(findings), tuple(checks))


def _package_findings(names: list[str]) -> list[DocxFinding]:
    findings: list[DocxFinding] = []
    name_set = set(names)
    if len(names) > MAX_PARTS:
        findings.append(
            DocxFinding("too_many_parts", "fail", "DOCX contains too many package parts.", {"count": len(names)})
        )
    missing = sorted(REQUIRED_PARTS - name_set)
    if missing:
        findings.append(
            DocxFinding("missing_parts", "fail", "DOCX is missing required OOXML parts.", {"missing": missing})
        )
    for name in names:
        pure = PurePosixPath(name)
        if pure.is_absolute() or ".." in pure.parts or "\\" in name:
            findings.append(
                DocxFinding("unsafe_part_name", "fail", "DOCX contains an unsafe part path.", {"part": name})
            )
        if name.lower().endswith(BLOCKED_SUFFIXES) or "vbaProject" in name:
            findings.append(
                DocxFinding("embedded_executable", "fail", "DOCX contains a blocked embedded object.", {"part": name})
            )
    return findings


def _xml_findings(archive: ZipFile) -> list[DocxFinding]:
    findings: list[DocxFinding] = []
    document = _parse(archive, "word/document.xml", findings)
    styles = _parse(archive, "word/styles.xml", findings)
    rels = _parse(archive, "word/_rels/document.xml.rels", findings)
    footer = _parse(archive, "word/footer1.xml", findings) if "word/footer1.xml" in archive.namelist() else None
    footnotes = _parse(archive, "word/footnotes.xml", findings) if "word/footnotes.xml" in archive.namelist() else None
    if document is None or styles is None or rels is None:
        return findings
    findings.extend(_relationship_findings(rels))
    findings.extend(_document_findings(document, footer))
    findings.extend(_style_findings(styles))
    if footnotes is not None:
        findings.extend(_footnote_findings(document, footnotes))
    return findings


def _parse(archive: ZipFile, name: str, findings: list[DocxFinding]) -> ET.Element | None:
    try:
        return ET.fromstring(archive.read(name))
    except ET.ParseError as exc:
        findings.append(
            DocxFinding(
                "malformed_xml", "fail", "OOXML part is not well-formed XML.", {"part": name, "error": str(exc)}
            )
        )
    return None


def _relationship_findings(rels: ET.Element) -> list[DocxFinding]:
    findings = []
    ids: list[str] = []
    for rel in rels.findall(f"{REL}Relationship"):
        rel_id = rel.attrib.get("Id")
        if rel_id:
            ids.append(rel_id)
        target = rel.attrib.get("Target", "")
        mode = rel.attrib.get("TargetMode", "")
        if mode.lower() == "external":
            findings.append(
                DocxFinding(
                    "external_relationship", "fail", "External relationships are not allowed.", {"target": target}
                )
            )
    if len(ids) != len(set(ids)):
        findings.append(DocxFinding("duplicate_relationship_id", "fail", "Relationship IDs must be unique.", {}))
    return findings


def _compression_findings(archive: ZipFile) -> list[DocxFinding]:
    findings = []
    for info in archive.infolist():
        if info.file_size <= 0:
            continue
        compressed = max(info.compress_size, 1)
        ratio = info.file_size / compressed
        if ratio > MAX_COMPRESSION_RATIO:
            findings.append(
                DocxFinding(
                    "suspicious_compression_ratio",
                    "fail",
                    "DOCX part has a suspicious compression ratio.",
                    {"part": info.filename, "ratio": round(ratio, 3)},
                )
            )
    return findings


def _document_findings(document: ET.Element, footer: ET.Element | None) -> list[DocxFinding]:
    findings = []
    if document.find(f".//{W}sectPr/{W}pgSz") is None or document.find(f".//{W}sectPr/{W}pgMar") is None:
        findings.append(DocxFinding("missing_page_setup", "fail", "Section page size or margins are missing.", {}))
    if document.find(f".//{W}bidi") is None or document.find(f".//{W}rtl") is None:
        findings.append(
            DocxFinding("missing_rtl", "fail", "Required paragraph bidi or run RTL properties are missing.", {})
        )
    instr = "".join(node.text or "" for node in document.findall(f".//{W}instrText"))
    if footer is not None:
        instr += "".join(node.text or "" for node in footer.findall(f".//{W}instrText"))
    if "TOC" not in instr:
        findings.append(DocxFinding("missing_toc_field", "fail", "TOC field code is missing.", {}))
    if "PAGE" not in instr:
        findings.append(DocxFinding("missing_page_field", "fail", "PAGE field code is missing.", {}))
    if not "".join(node.text or "" for node in document.findall(f".//{W}t")).strip():
        findings.append(DocxFinding("missing_text", "fail", "Document contains no text.", {}))
    return findings


def _style_findings(styles: ET.Element) -> list[DocxFinding]:
    findings = []
    for level in range(1, 6):
        style = styles.find(f".//{W}style[@{W}styleId='Heading{level}']")
        if style is None or style.find(f".//{W}outlineLvl") is None:
            findings.append(
                DocxFinding("missing_heading_outline", "fail", "Heading style lacks outline level.", {"level": level})
            )
    return findings


def _footnote_findings(document: ET.Element, footnotes: ET.Element) -> list[DocxFinding]:
    refs = {node.attrib[f"{W}id"] for node in document.findall(f".//{W}footnoteReference") if f"{W}id" in node.attrib}
    ids = [node.attrib[f"{W}id"] for node in footnotes.findall(f"{W}footnote") if f"{W}id" in node.attrib]
    regular_ids = {item for item in ids if item not in {"-1", "0"}}
    findings = []
    if len(ids) != len(set(ids)):
        findings.append(DocxFinding("duplicate_footnote_id", "fail", "Footnote IDs must be unique.", {}))
    missing = sorted(refs - regular_ids)
    orphan = sorted(regular_ids - refs)
    if missing:
        findings.append(
            DocxFinding("missing_footnotes", "fail", "Footnote references lack footnote bodies.", {"ids": missing})
        )
    if orphan:
        findings.append(DocxFinding("orphan_footnotes", "fail", "Footnote bodies lack references.", {"ids": orphan}))
    if footnotes.find(f".//{W}bidi") is None:
        findings.append(
            DocxFinding("footnote_rtl_missing", "fail", "Footnote RTL paragraph properties are missing.", {})
        )
    return findings
