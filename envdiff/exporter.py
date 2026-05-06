"""Export diff results to structured file formats (JSON, CSV)."""

from __future__ import annotations

import csv
import io
import json
from typing import Literal

from envdiff.comparator import DiffResult
from envdiff.sorter import GroupedDiff

ExportFormat = Literal["json", "csv"]


def _result_to_records(grouped: GroupedDiff) -> list[dict[str, str]]:
    """Flatten a GroupedDiff into a list of row dicts."""
    records: list[dict[str, str]] = []

    for key in sorted(grouped.missing_in_target):
        records.append({"key": key, "status": "missing_in_target", "base": "", "target": ""})

    for key in sorted(grouped.missing_in_base):
        records.append({"key": key, "status": "missing_in_base", "base": "", "target": ""})

    for key, (base_val, target_val) in sorted(grouped.mismatched.items()):
        records.append({
            "key": key,
            "status": "mismatch",
            "base": base_val,
            "target": target_val,
        })

    return records


def export_json(result: DiffResult, grouped: GroupedDiff, indent: int = 2) -> str:
    """Serialise diff result to a JSON string."""
    payload = {
        "summary": {
            "missing_in_target": len(grouped.missing_in_target),
            "missing_in_base": len(grouped.missing_in_base),
            "mismatched": len(grouped.mismatched),
            "has_differences": result.has_differences,
        },
        "details": _result_to_records(grouped),
    }
    return json.dumps(payload, indent=indent)


def export_csv(grouped: GroupedDiff) -> str:
    """Serialise diff result to a CSV string."""
    records = _result_to_records(grouped)
    fieldnames = ["key", "status", "base", "target"]
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(records)
    return buf.getvalue()


def export(result: DiffResult, grouped: GroupedDiff, fmt: ExportFormat) -> str:
    """Dispatch to the appropriate exporter based on *fmt*."""
    if fmt == "json":
        return export_json(result, grouped)
    if fmt == "csv":
        return export_csv(grouped)
    raise ValueError(f"Unsupported export format: {fmt!r}")
