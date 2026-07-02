from __future__ import annotations

import json
import sys

from legal_research_skill.word.worker import word_worker_entry


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) not in {2, 3}:
        print(
            json.dumps(
                {
                    "status": "FAILED",
                    "error_code": "worker_usage_error",
                    "error": "Worker requires input_path, working_path, and optional diagnostics_path.",
                    "word_validated": False,
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 2
    diagnostics_path = args[2] if len(args) == 3 else None
    result = word_worker_entry(args[0], args[1], diagnostics_path)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result.get("status") == "WORD_VALIDATED" else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
