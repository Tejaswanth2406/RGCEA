"""
Layer 1 — Latent Episodic Memory System (LEMS)
===============================================
Hippocampal-replay analogue.  Stores (state, action, outcome, uncertainty)
trajectories and replays them for downstream dream generation.
"""

from __future__ import annotations

import logging
import time
from collections import deque
from typing import Deque, Iterator, List, Optional

from rgcea.models import Episode

logger = logging.getLogger(__name__)


class LatentEpisodicMemorySystem:
    """
    A bounded, salience-weighted episodic memory store.

    Parameters
    ----------
    capacity:
        Maximum number of episodes to retain.
    salience_threshold:
        Episodes below this salience are eligible for eviction first.
    """

    def __init__(self, capacity: int = 10_000, salience_threshold: float = 0.3) -> None:
        self._capacity = capacity
        self._salience_threshold = salience_threshold
        self._store: Deque[Episode] = deque(maxlen=capacity)
        self._replay_cursor: int = 0

    # ------------------------------------------------------------------
    # Ingestion
    # ------------------------------------------------------------------

    def store(self, episode: Episode) -> None:
        """Persist a new episode, evicting low-salience entries if full."""
        if len(self._store) >= self._capacity:
            self._evict_low_salience()
        self._store.append(episode)
        logger.debug("Stored episode %s (salience=%.2f)", episode.id, episode.salience)

    def store_batch(self, episodes: List[Episode]) -> None:
        for ep in episodes:
            self.store(ep)

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def replay(self, n: int = 32, min_salience: float = 0.0) -> List[Episode]:
        """
        Return up to *n* episodes for replay.
        High-salience episodes are preferentially selected.
        """
        candidates = [ep for ep in self._store if ep.salience >= min_salience]
        candidates.sort(key=lambda e: e.salience, reverse=True)
        selected = candidates[:n]
        logger.debug("Replaying %d/%d episodes", len(selected), len(self._store))
        return selected

    def iter_recent(self, k: int = 100) -> Iterator[Episode]:
        """Iterate over the *k* most recent episodes."""
        episodes = list(self._store)
        yield from episodes[-k:]

    def search_by_tag(self, tag: str) -> List[Episode]:
        return [ep for ep in self._store if tag in ep.tags]

    def get(self, episode_id: str) -> Optional[Episode]:
        for ep in self._store:
            if ep.id == episode_id:
                return ep
        return None

    # ------------------------------------------------------------------
    # Maintenance
    # ------------------------------------------------------------------

    def _evict_low_salience(self) -> None:
        """Remove the lowest-salience episode to make room."""
        if not self._store:
            return
        min_ep = min(self._store, key=lambda e: e.salience)
        # deque doesn't support arbitrary removal; rebuild without it
        episodes = [ep for ep in self._store if ep.id != min_ep.id]
        self._store = deque(episodes, maxlen=self._capacity)
        logger.debug("Evicted episode %s (salience=%.2f)", min_ep.id, min_ep.salience)

    def clear(self) -> None:
        self._store.clear()

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    @property
    def size(self) -> int:
        return len(self._store)

    @property
    def capacity(self) -> int:
        return self._capacity

    def stats(self) -> dict:
        if not self._store:
            return {"size": 0, "capacity": self._capacity, "avg_salience": 0.0}
        saliences = [ep.salience for ep in self._store]
        return {
            "size": len(self._store),
            "capacity": self._capacity,
            "avg_salience": sum(saliences) / len(saliences),
            "max_salience": max(saliences),
            "min_salience": min(saliences),
        }

    def __repr__(self) -> str:
        return f"<LEMS size={self.size}/{self.capacity}>"
