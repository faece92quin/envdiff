"""High-level diff driver that combines filtering, sorting, and comparison."""

from dataclasses import dataclass, field
from typing import Optional

from envdiff.comparator import DiffResult, compare_envs
from envdiff.filter import filter_by_prefix, filter_by_keys, filter_by_status
from envdiff.sorter import sort_keys_by_status
from envdiff.loader import EnvFile


@dataclass
class DiffOptions:
    """Configuration options for a diff run."""

    ignore_values: bool = False
    prefix: Optional[str] = None
    only_keys: Optional[list] = field(default_factory=list)
    statuses: Optional[list] = field(default_factory=list)


def run_diff(
    base: EnvFile,
    target: EnvFile,
    options: Optional[DiffOptions] = None,
) -> DiffResult:
    """Compare *base* against *target* applying any filters from *options*.

    Steps
    -----
    1. Compare the two env files.
    2. Optionally restrict to a key prefix.
    3. Optionally restrict to an explicit key list.
    4. Optionally restrict to specific diff statuses.

    Returns a (possibly filtered) :class:`~envdiff.comparator.DiffResult`.
    """
    if options is None:
        options = DiffOptions()

    result: DiffResult = compare_envs(base, target, ignore_values=options.ignore_values)

    if options.prefix:
        result = filter_by_prefix(result, options.prefix)

    if options.only_keys:
        result = filter_by_keys(result, options.only_keys)

    if options.statuses:
        result = filter_by_status(result, options.statuses)

    return result


def sorted_diff(
    base: EnvFile,
    target: EnvFile,
    options: Optional[DiffOptions] = None,
) -> dict:
    """Return diff results grouped and sorted by status.

    Returns a mapping of ``status -> sorted list of keys`` for use by
    reporters and exporters.
    """
    result = run_diff(base, target, options)
    return sort_keys_by_status(result)
