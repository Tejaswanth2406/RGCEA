"""
Layer 3 — Counterfactual Generative Simulator (CGS)
====================================================
The actual dream engine.  Takes compressed archetypes + raw episodes and
generates "what if?" alternative worlds.
"""

from __future__ import annotations

import logging
import random
from typing import List, Optional

from rgcea.models import Archetype, Dream, DreamType, Episode

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Perturbation templates
# ---------------------------------------------------------------------------
_PERTURBATIONS = [
    "event X never occurred",
    "agent behaved with opposite intent",
    "physical constraints were reversed",
    "time ran backwards",
    "information was perfectly complete",
    "information was entirely absent",
    "all agents acted cooperatively",
    "all agents acted adversarially",
    "resources were infinite",
    "resources were zero",
    "causality was acausal",
    "the goal was redefined mid-task",
    "a hidden third party was involved",
    "the environment was adversarial",
]

_SCENARIO_TEMPLATES = [
    "In a world where {perturbation}, the system encountered {context} and had to adapt.",
    "Suppose {perturbation}. How would {context} change the outcome?",
    "What if {perturbation}? The implications for {context} are explored here.",
    "A counterfactual: {perturbation}. This transforms {context} in the following ways.",
]

_INSIGHT_POOL = [
    "Redundancy in {context} would mitigate this failure class.",
    "The boundary condition exposed here is under-tested.",
    "This reveals a hidden dependency on assumptions about {perturbation}.",
    "A soft invariant becomes brittle under this perturbation.",
    "Novel compression opportunity: this scenario maps to an existing archetype.",
    "Unexpected stability observed — worth investigating why.",
    "Value alignment is stressed under this counterfactual.",
    "Monitoring coverage gaps are exposed in this scenario.",
]


class CounterfactualGenerativeSimulator:
    """
    Generates counterfactual dream scenarios from episodes and archetypes.

    Parameters
    ----------
    dreams_per_cycle:
        How many dreams to generate in each ``generate`` call.
    novelty_bias:
        0 = prefer replaying known patterns; 1 = prefer alien/bizarre scenarios.
    seed:
        Optional random seed for reproducibility.
    """

    def __init__(
        self,
        dreams_per_cycle: int = 10,
        novelty_bias: float = 0.4,
        seed: Optional[int] = None,
    ) -> None:
        self._dreams_per_cycle = dreams_per_cycle
        self._novelty_bias = novelty_bias
        self._rng = random.Random(seed)
        self._dream_history: List[Dream] = []

    # ------------------------------------------------------------------
    # Generation
    # ------------------------------------------------------------------

    def generate(
        self,
        episodes: List[Episode],
        archetypes: List[Archetype],
        n: Optional[int] = None,
    ) -> List[Dream]:
        """
        Produce a batch of counterfactual dreams.

        Each dream picks a random episode (context) + a random perturbation,
        then synthesises a scenario and a handful of insights.
        """
        n = n or self._dreams_per_cycle
        dreams: List[Dream] = []

        for _ in range(n):
            dream = self._generate_one(episodes, archetypes)
            dreams.append(dream)
            self._dream_history.append(dream)

        logger.info("Generated %d counterfactual dreams", len(dreams))
        return dreams

    def _generate_one(
        self,
        episodes: List[Episode],
        archetypes: List[Archetype],
    ) -> Dream:
        perturbation = self._rng.choice(_PERTURBATIONS)

        # Context comes from an episode or archetype
        if episodes and self._rng.random() > self._novelty_bias:
            ep = self._rng.choice(episodes)
            context = ep.outcome or ep.action or "an unknown situation"
            source_ids = [ep.id]
            dream_type = DreamType.MEMORY
        elif archetypes:
            arch = self._rng.choice(archetypes)
            context = arch.description
            source_ids = [arch.id]
            dream_type = DreamType.COUNTERFACTUAL
        else:
            context = "a generic operational scenario"
            source_ids = []
            dream_type = DreamType.ALIEN

        template = self._rng.choice(_SCENARIO_TEMPLATES)
        scenario = template.format(perturbation=perturbation, context=context)

        n_insights = self._rng.randint(1, 3)
        insights = [
            self._rng.choice(_INSIGHT_POOL).format(
                perturbation=perturbation, context=context
            )
            for _ in range(n_insights)
        ]

        novelty = self._rng.uniform(0.3, 1.0)
        coherence = self._rng.uniform(0.5, 1.0)

        return Dream(
            dream_type=dream_type,
            title=f"Dream: if {perturbation[:40]}",
            scenario=scenario,
            perturbation=perturbation,
            insights=insights,
            novelty_score=round(novelty, 3),
            coherence_score=round(coherence, 3),
            source_episodes=source_ids,
        )

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    def recent_dreams(self, k: int = 20) -> List[Dream]:
        return self._dream_history[-k:]

    @property
    def total_generated(self) -> int:
        return len(self._dream_history)

    def stats(self) -> dict:
        if not self._dream_history:
            return {"total": 0}
        novelties = [d.novelty_score for d in self._dream_history]
        coherences = [d.coherence_score for d in self._dream_history]
        return {
            "total": len(self._dream_history),
            "avg_novelty": round(sum(novelties) / len(novelties), 3),
            "avg_coherence": round(sum(coherences) / len(coherences), 3),
        }

    def __repr__(self) -> str:
        return f"<CGS total_dreams={self.total_generated}>"
