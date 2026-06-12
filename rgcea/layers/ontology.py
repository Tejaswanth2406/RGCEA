"""
Layer 5 — Ontological Perturbation Engine (OPE)
================================================
Mutates conceptual axioms to explore alternative world-models.
Analogous to conceptual blending, meta-learning, and automated theory formation.
"""

from __future__ import annotations

import copy
import logging
import random
from typing import Dict, List, Optional

from rgcea.models import OntologyFrame

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Base axiom vocabulary
# ---------------------------------------------------------------------------
_BASE_AXIOMS: Dict[str, str] = {
    "object_permanence": "objects continue to exist when not observed",
    "causality": "every effect has a prior cause",
    "identity": "an entity remains the same entity over time",
    "logic": "propositions obey classical two-valued logic",
    "agency": "agents have goals and take goal-directed actions",
    "time": "time flows in one direction",
    "space": "space is continuous and three-dimensional",
    "information": "information cannot be created from nothing",
    "consciousness": "consciousness supervenes on physical processes",
    "mathematics": "mathematical truths are necessary and universal",
}

_MUTATIONS: Dict[str, str] = {
    "object_permanence": "objects exist probabilistically; observation collapses their state",
    "causality": "effects can precede causes; retrocausality is possible",
    "identity": "identity is a gradient, not a binary",
    "logic": "propositions exist in superposition until context resolves them",
    "agency": "agency is an emergent illusion of distributed processes",
    "time": "time is cyclic and branching",
    "space": "space is discrete and locally finite",
    "information": "information is conserved but not necessarily accessible",
    "consciousness": "consciousness is fundamental, not emergent",
    "mathematics": "mathematical truths are contingent on the axiom set chosen",
}


class OntologicalPerturbationEngine:
    """
    Generates mutated OntologyFrames by replacing axioms with alternatives.

    Parameters
    ----------
    mutation_rate:
        Fraction of axioms to perturb per generation (0–1).
    max_frames_per_cycle:
        How many mutated frames to produce per call.
    seed:
        Optional random seed.
    """

    def __init__(
        self,
        mutation_rate: float = 0.3,
        max_frames_per_cycle: int = 5,
        seed: Optional[int] = None,
    ) -> None:
        self._mutation_rate = mutation_rate
        self._max_frames = max_frames_per_cycle
        self._rng = random.Random(seed)
        self._frame_history: List[OntologyFrame] = []
        self._generation: int = 0

    # ------------------------------------------------------------------
    # Generation
    # ------------------------------------------------------------------

    def perturb(
        self,
        parent: Optional[OntologyFrame] = None,
        n: Optional[int] = None,
    ) -> List[OntologyFrame]:
        """
        Produce *n* mutated ontology frames derived from *parent*.
        If parent is None, uses the base axiom set.
        """
        n = n or self._max_frames
        base_axioms = (
            copy.deepcopy(parent.axioms) if parent else copy.deepcopy(_BASE_AXIOMS)
        )
        parent_id = parent.id if parent else None
        frames: List[OntologyFrame] = []

        for _ in range(n):
            frame = self._mutate(base_axioms, parent_id)
            frames.append(frame)
            self._frame_history.append(frame)

        self._generation += 1
        logger.info(
            "Generation %d: produced %d ontology frames", self._generation, len(frames)
        )
        return frames

    def _mutate(
        self,
        base_axioms: Dict[str, str],
        parent_id: Optional[str],
    ) -> OntologyFrame:
        axioms = copy.deepcopy(base_axioms)
        mutated_keys: List[str] = []

        for key in list(axioms.keys()):
            if self._rng.random() < self._mutation_rate:
                if key in _MUTATIONS:
                    axioms[key] = _MUTATIONS[key]
                    mutated_keys.append(key)

        name = (
            f"OntologyGen{self._generation}:{','.join(mutated_keys[:3]) or 'base'}"
        )
        return OntologyFrame(
            name=name,
            axioms=axioms,
            generation=self._generation,
            parent_id=parent_id,
        )

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    def base_frame(self) -> OntologyFrame:
        return OntologyFrame(
            name="BaseOntology",
            axioms=copy.deepcopy(_BASE_AXIOMS),
            generation=0,
        )

    def recent_frames(self, k: int = 10) -> List[OntologyFrame]:
        return self._frame_history[-k:]

    @property
    def generation(self) -> int:
        return self._generation

    def stats(self) -> dict:
        return {
            "generation": self._generation,
            "total_frames": len(self._frame_history),
            "mutation_rate": self._mutation_rate,
        }

    def __repr__(self) -> str:
        return f"<OPE generation={self.generation} frames={len(self._frame_history)}>"
