"""In-memory synthetic dataset storage with TTL and bounded size."""

import time
from typing import Any

import numpy as np
from numpy.typing import NDArray

from shared.schemas.synthetic import SyntheticDataset

MAX_DATASETS = 10
TTL_SECONDS = 3600  # 1 hour

# Each entry: {"X": NDArray, "y": NDArray, "feature_names": list[str],
#              "metadata": SyntheticDataset, "created_at": float}
_datasets: dict[str, dict[str, Any]] = {}


def store_dataset(
    dataset_id: str,
    X: NDArray[np.float64],  # noqa: N803
    y: NDArray[np.int_],
    feature_names: list[str],
    metadata: SyntheticDataset,
) -> None:
    """Store a synthetic dataset. Evicts expired/oldest entries as needed."""
    _evict_expired()
    _evict_oldest_if_full()
    _datasets[dataset_id] = {
        "X": X,
        "y": y,
        "feature_names": feature_names,
        "metadata": metadata,
        "created_at": time.monotonic(),
    }


def get_dataset(
    dataset_id: str,
) -> tuple[NDArray[np.float64], NDArray[np.int_], list[str]] | None:
    """Retrieve dataset arrays. Returns None if not found or expired."""
    _evict_expired()
    entry = _datasets.get(dataset_id)
    if entry is None:
        return None
    return entry["X"], entry["y"], entry["feature_names"]


def get_dataset_metadata(dataset_id: str) -> SyntheticDataset | None:
    """Retrieve dataset metadata. Returns None if not found or expired."""
    _evict_expired()
    entry = _datasets.get(dataset_id)
    if entry is None:
        return None
    return entry["metadata"]


def _evict_expired() -> None:
    """Remove datasets older than TTL_SECONDS."""
    now = time.monotonic()
    expired = [k for k, v in _datasets.items() if now - v["created_at"] > TTL_SECONDS]
    for k in expired:
        del _datasets[k]


def _evict_oldest_if_full() -> None:
    """If at capacity, remove the oldest dataset."""
    while len(_datasets) >= MAX_DATASETS:
        oldest_key = min(_datasets, key=lambda k: _datasets[k]["created_at"])
        del _datasets[oldest_key]


def clear_all_datasets() -> None:
    """Clear all stored datasets. Used for testing."""
    _datasets.clear()
