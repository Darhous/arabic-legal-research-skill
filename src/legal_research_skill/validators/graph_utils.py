from __future__ import annotations

from typing import Any


def parent_cycles(records: list[dict[str, Any]], id_key: str, parent_key: str) -> tuple[tuple[str, ...], ...]:
    """Return deterministic parent-reference cycles within one entity collection."""
    by_id = {str(record[id_key]): record for record in records if id_key in record}
    cycles: list[tuple[str, ...]] = []
    seen_cycles: set[tuple[str, ...]] = set()
    for start in sorted(by_id):
        path: list[str] = []
        positions: dict[str, int] = {}
        current: str | None = start
        while current:
            if current in positions:
                cycle = tuple(path[positions[current] :])
                normalized = _normalize_cycle(cycle)
                if normalized not in seen_cycles:
                    seen_cycles.add(normalized)
                    cycles.append(normalized)
                break
            record = by_id.get(current)
            if record is None:
                break
            positions[current] = len(path)
            path.append(current)
            parent = record.get(parent_key)
            current = str(parent) if parent else None
    return tuple(sorted(cycles))


def _normalize_cycle(cycle: tuple[str, ...]) -> tuple[str, ...]:
    if not cycle:
        return cycle
    rotations = [cycle[index:] + cycle[:index] for index in range(len(cycle))]
    return min(rotations)
