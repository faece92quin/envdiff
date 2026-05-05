"""Compare parsed .env files and surface missing or mismatched keys."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DiffResult:
    """Result of comparing two .env files."""

    base_name: str
    target_name: str
    missing_in_target: List[str] = field(default_factory=list)
    missing_in_base: List[str] = field(default_factory=list)
    mismatched: Dict[str, Dict[str, Optional[str]]] = field(default_factory=dict)

    @property
    def has_differences(self) -> bool:
        return bool(self.missing_in_target or self.missing_in_base or self.mismatched)

    def summary(self) -> str:
        lines = [f"Comparing '{self.base_name}' vs '{self.target_name}'"]
        if not self.has_differences:
            lines.append("  No differences found.")
            return "\n".join(lines)
        if self.missing_in_target:
            lines.append(f"  Missing in '{self.target_name}': {', '.join(sorted(self.missing_in_target))}")
        if self.missing_in_base:
            lines.append(f"  Missing in '{self.base_name}': {', '.join(sorted(self.missing_in_base))}")
        if self.mismatched:
            lines.append("  Mismatched values:")
            for key in sorted(self.mismatched):
                base_val = self.mismatched[key]["base"]
                target_val = self.mismatched[key]["target"]
                lines.append(f"    {key}: '{base_val}' != '{target_val}'")
        return "\n".join(lines)


def compare_envs(
    base: Dict[str, Optional[str]],
    target: Dict[str, Optional[str]],
    base_name: str = "base",
    target_name: str = "target",
    ignore_values: bool = False,
) -> DiffResult:
    """Compare two parsed env dicts and return a DiffResult.

    Args:
        base: Parsed env dict treated as the reference.
        target: Parsed env dict to compare against the base.
        base_name: Label for the base environment.
        target_name: Label for the target environment.
        ignore_values: If True, only check for missing keys, not value mismatches.

    Returns:
        A DiffResult describing all differences.
    """
    result = DiffResult(base_name=base_name, target_name=target_name)

    base_keys = set(base.keys())
    target_keys = set(target.keys())

    result.missing_in_target = list(base_keys - target_keys)
    result.missing_in_base = list(target_keys - base_keys)

    if not ignore_values:
        for key in base_keys & target_keys:
            if base[key] != target[key]:
                result.mismatched[key] = {"base": base[key], "target": target[key]}

    return result
