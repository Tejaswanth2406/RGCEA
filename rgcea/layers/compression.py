"""
Layer 2 — Semantic Compression Engine (SCE)
============================================
Transforms raw episodes into reusable cognitive primitives (Archetypes).
Analogous to hierarchical variational autoencoders / sparse autoencoders.
"""

from __future__ import annotations

import logging
import math
import random
import time
from typing import Dict, List, Optional, Tuple

from rgcea.models import Archetype, Episode

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Default archetype templates  (seed pool for demo; real system would learn)
# ---------------------------------------------------------------------------
_SEED_ARCHETYPES: List[Tuple[str, str]] = [
    ("The Blind Navigator", "Catastrophic navigation failure across all sensor modalities"),
    ("The False Oracle", "High-confidence prediction that is systematically wrong"),
    ("The Silent Sensor", "Critical information channel producing no signal"),
    ("The Missing Node", "A required dependency that is absent at execution time"),
    ("The Broken Map", "World model that is internally consistent but factually incorrect"),
    ("The Infinite Loop", "Recursive process with no halting condition"),
    ("The Scattered Self", "Goal conflict leading to paralysis or incoherence"),
    ("The Borrowed Light", "Understanding derived entirely from a single flawed source"),
    ("The Slow Collapse", "Gradual degradation that goes undetected until catastrophic failure"),
    ("The Mirror Trap", "Self-referential process that amplifies errors recursively"),
]


class SemanticCompressionEngine:
    """
    Clusters episodic memories into compressed Archetypes.

    In production this layer would use a learned VAE or sparse autoencoder.
    Here we implement a heuristic clustering approach that is deterministic,
    inspectable, and fast — suitable for integration testing.

    Parameters
    ----------
    n_archetypes:
        Maximum number of archetypes to maintain.
    compression_ratio:
        Target episodes-per-archetype.
    """

    def __init__(
        self,
        n_archetypes: int = 40,
        compression_ratio: int = 50,
    ) -> None:
        self._n_archetypes = n_archetypes
        self._compression_ratio = compression_ratio
        self._archetypes: Dict[str, Archetype] = {}
        self._seed_pool = list(_SEED_ARCHETYPES)
        self._init_seed_archetypes()

    # ------------------------------------------------------------------
    # Init
    # ------------------------------------------------------------------

    def _init_seed_archetypes(self) -> None:
        for name, description in self._seed_pool:
            arch = Archetype(name=name, description=description)
            self._archetypes[arch.id] = arch
        logger.debug("Initialised %d seed archetypes", len(self._archetypes))

    # ------------------------------------------------------------------
    # Compression
    # ------------------------------------------------------------------

    def compress(self, episodes: List[Episode]) -> List[Archetype]:
        """
        Assign episodes to archetypes and produce updated archetype list.

        Strategy
        --------
        1. Group episodes by dominant tag.
        2. Each tag group merges into the nearest archetype (by name similarity).
        3. If no match, spawn a new archetype.
        4. Prune archetypes that have accumulated zero episodes.
        """
        if not episodes:
            return list(self._archetypes.values())

        tag_groups: Dict[str, List[Episode]] = {}
        for ep in episodes:
            key = ep.tags[0] if ep.tags else "general"
            tag_groups.setdefault(key, []).append(ep)

        for tag, group in tag_groups.items():
            arch = self._find_or_create_archetype(tag, group)
            arch.compressed_episodes += len(group)
            arch.fitness = self._score_fitness(arch)
            logger.debug(
                "Archetype '%s' now covers %d episodes (fitness=%.2f)",
                arch.name,
                arch.compressed_episodes,
                arch.fitness,
            )

        return list(self._archetypes.values())

    def _find_or_create_archetype(
        self, tag: str, group: List[Episode]
    ) -> Archetype:
        # Try fuzzy name match
        tag_lower = tag.lower()
        for arch in self._archetypes.values():
            if tag_lower in arch.name.lower() or tag_lower in arch.description.lower():
                return arch

        # Spawn new archetype if capacity allows
        if len(self._archetypes) < self._n_archetypes:
            arch = Archetype(
                name=f"Archetype:{tag.title()}",
                description=f"Auto-generated archetype for '{tag}' episode cluster",
                tags=[tag],
            )
            self._archetypes[arch.id] = arch
            logger.info("Spawned new archetype: %s", arch.name)
            return arch

        # At capacity — merge into lowest-fitness archetype
        worst = min(self._archetypes.values(), key=lambda a: a.fitness)
        worst.tags.append(tag)
        worst.description += f"; extends to '{tag}'"
        return worst

    # ------------------------------------------------------------------
    # Fitness
    # ------------------------------------------------------------------

    def _score_fitness(self, arch: Archetype) -> float:
        """
        Composite fitness:  coverage × novelty × recency_decay
        All components normalised to [0, 1].
        """
        coverage = min(arch.compressed_episodes / self._compression_ratio, 1.0)
        novelty = 1.0 / (1.0 + math.log1p(arch.compressed_episodes))
        # recency: fitness decays if nothing has been added recently
        return round((coverage * 0.6 + novelty * 0.4), 4)

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    def get_archetype(self, arch_id: str) -> Optional[Archetype]:
        return self._archetypes.get(arch_id)

    def top_archetypes(self, n: int = 10) -> List[Archetype]:
        ranked = sorted(self._archetypes.values(), key=lambda a: a.fitness, reverse=True)
        return ranked[:n]

    def all_archetypes(self) -> List[Archetype]:
        return list(self._archetypes.values())

    @property
    def archetype_count(self) -> int:
        return len(self._archetypes)

    def stats(self) -> dict:
        archs = list(self._archetypes.values())
        if not archs:
            return {}
        return {
            "count": len(archs),
            "total_episodes_compressed": sum(a.compressed_episodes for a in archs),
            "avg_fitness": sum(a.fitness for a in archs) / len(archs),
            "top_3": [a.name for a in self.top_archetypes(3)],
        }

    def __repr__(self) -> str:
        return f"<SCE archetypes={self.archetype_count}>"
