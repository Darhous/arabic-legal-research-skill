from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from legal_research_skill.constants import PACKAGE_VERSION
from legal_research_skill.models import stable_hash, stable_json


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass(frozen=True, slots=True)
class ArtifactManifest:
    input_identifier: str
    input_digest: str
    phase3_baseline_hash: str
    generator_version: str
    render_config_digest: str
    pre_word_docx_path: str | None
    pre_word_docx_digest: str | None
    word_finalized_docx_path: str | None
    word_finalized_docx_digest: str | None
    word_evidence: dict[str, Any]
    generated_at: str
    """Sourced from RenderConfig.created_at (see docx/render_model.py).

    Defaults to a fixed build-epoch constant, not a real wall-clock
    timestamp, so that independent CLI invocations of the same input
    produce byte-identical manifests and DOCX output. Do not treat this
    field as evidence of when an artifact was actually produced unless the
    caller explicitly supplied a real timestamp via RenderConfig.
    """
    validations: tuple[dict[str, Any], ...]
    allowed_claims: tuple[str, ...]
    prohibited_claims: tuple[str, ...]
    limitations: tuple[str, ...]
    final_artifact_status: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "manifest_schema_version": "0.4.0",
            "metadata": {
                "tool": "legal_research_skill",
                "package_version": PACKAGE_VERSION,
                **self.metadata,
            },
            "input_identifier": self.input_identifier,
            "input_digest": self.input_digest,
            "phase3_baseline_hash": self.phase3_baseline_hash,
            "generator_version": self.generator_version,
            "render_config_digest": self.render_config_digest,
            "pre_word_docx": {
                "path": self.pre_word_docx_path,
                "sha256": self.pre_word_docx_digest,
            },
            "word_finalized_docx": {
                "path": self.word_finalized_docx_path,
                "sha256": self.word_finalized_docx_digest,
            },
            "word_evidence": self.word_evidence,
            "generated_at": self.generated_at,
            "validations": list(self.validations),
            "allowed_claims": sorted(set(self.allowed_claims)),
            "prohibited_claims": sorted(set(self.prohibited_claims)),
            "limitations": sorted(set(self.limitations)),
            "final_artifact_status": self.final_artifact_status,
        }


def render_config_digest(config: Any) -> str:
    if hasattr(config, "to_dict"):
        return stable_hash(config.to_dict())
    return stable_hash(config)


def manifest_to_json(manifest: ArtifactManifest, *, compact: bool = False) -> str:
    if compact:
        return stable_json(manifest.to_dict()) + "\n"
    return json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
