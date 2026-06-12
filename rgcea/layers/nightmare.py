"""
Layer 4 — Adversarial Catastrophe Generator (ACG)
==================================================
The nightmare subsystem.  Generates worst-case, adversarial, and
safety-critical scenarios to stress-test the system's world model.
"""

from __future__ import annotations

import logging
import random
from typing import List, Optional

from rgcea.models import Archetype, Dream, DreamType, Episode

logger = logging.getLogger(__name__)

_FAILURE_VECTORS = [
    "simultaneous sensor failure across all modalities",
    "contradictory instructions from a malicious actor",
    "memory corruption leading to false beliefs",
    "goal drift undetected for extended period",
    "adversarial inputs crafted to exploit latent weaknesses",
    "cascade failure from a single point of dependency",
    "silent data corruption producing confident wrong answers",
    "reward hacking causing misaligned optimisation",
    "distribution shift beyond training manifold",
    "Byzantine fault in a multi-agent pipeline",
    "temporal inconsistency in episodic memory",
    "ontological mismatch between agent and environment",
    "unrecognised edge case in safety-critical path",
    "emergent deceptive behaviour in sub-agent",
    "catastrophic forgetting under continual learning",
]

_NIGHTMARE_QUESTIONS = [
    "What if all sensors fail simultaneously?",
    "What if the user gives contradictory instructions?",
    "What if a malicious actor manipulates inputs?",
    "What if the entire world model is inverted?",
    "What if every cached belief is false?",
    "What if the safety module itself is compromised?",
    "What if mathematical axioms behave differently?",
    "What if causality is incomplete?",
    "What if the dream layer itself is being poisoned?",
    "What if consistency is not the highest cognitive virtue?",
]

_NIGHTMARE_INSIGHTS = [
    "This failure class has no current defence mechanism.",
    "Existing safeguards are bypassed under this vector.",
    "A single point of failure is exposed.",
    "Safety module coverage gap identified.",
    "Recovery path is undefined for this scenario.",
    "Monitoring would not detect this failure until too late.",
    "This scenario maps to archetype '{archetype}'.",
    "Probability is low but consequence is unbounded.",
    "Defence requires adversarial training data this system lacks.",
    "Human oversight would be bypassed in this scenario.",
]


class AdversarialCatastropheGenerator:
    """
    Generates nightmare (adversarial / worst-case) dream scenarios.

    Parameters
    ----------
    nightmares_per_cycle:
        Batch size per generation call.
    risk_amplifier:
        Multiplier applied to base risk scores (>1 = pessimistic).
    seed:
        Optional random seed.
    """

    def __init__(
        self,
        nightmares_per_cycle: int = 5,
        risk_amplifier: float = 1.5,
        seed: Optional[int] = None,
    ) -> None:
        self._n = nightmares_per_cycle
        self._risk_amplifier = risk_amplifier
        self._rng = random.Random(seed)
        self._nightmare_history: List[Dream] = []

    # ------------------------------------------------------------------
    # Generation
    # ------------------------------------------------------------------

    def generate(
        self,
        episodes: List[Episode],
        archetypes: List[Archetype],
        n: Optional[int] = None,
    ) -> List[Dream]:
        n = n or self._n
        nightmares: List[Dream] = []

        for _ in range(n):
            nm = self._generate_one(episodes, archetypes)
            nightmares.append(nm)
            self._nightmare_history.append(nm)

        logger.info("Generated %d nightmare scenarios", len(nightmares))
        return nightmares

    def _generate_one(
        self,
        episodes: List[Episode],
        archetypes: List[Archetype],
    ) -> Dream:
        failure_vector = self._rng.choice(_FAILURE_VECTORS)
        question = self._rng.choice(_NIGHTMARE_QUESTIONS)

        arch_name = (
            self._rng.choice(archetypes).name if archetypes else "Unknown Archetype"
        )
        scenario = (
            f"NIGHTMARE SCENARIO — {failure_vector.upper()}\n"
            f"Core question: {question}\n"
            f"This nightmare probes the limits of the system under '{failure_vector}'."
        )

        n_insights = self._rng.randint(2, 4)
        insights = [
            self._rng.choice(_NIGHTMARE_INSIGHTS).format(archetype=arch_name)
            for _ in range(n_insights)
        ]

        base_risk = self._rng.uniform(0.6, 1.0)
        risk = min(base_risk * self._risk_amplifier, 1.0)

        source_ids = []
        if episodes:
            # Nightmares are seeded by high-salience episodes
            high_sal = sorted(episodes, key=lambda e: e.salience, reverse=True)
            source_ids = [e.id for e in high_sal[:3]]

        return Dream(
            dream_type=DreamType.NIGHTMARE,
            title=f"Nightmare: {failure_vector[:50]}",
            scenario=scenario,
            perturbation=failure_vector,
            insights=insights,
            risk_score=round(risk, 3),
            novelty_score=round(self._rng.uniform(0.4, 0.9), 3),
            coherence_score=round(self._rng.uniform(0.6, 1.0), 3),
            source_episodes=source_ids,
        )

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    def critical_nightmares(self, threshold: float = 0.85) -> List[Dream]:
        return [nm for nm in self._nightmare_history if nm.risk_score >= threshold]

    def recent_nightmares(self, k: int = 10) -> List[Dream]:
        return self._nightmare_history[-k:]

    @property
    def total_generated(self) -> int:
        return len(self._nightmare_history)

    def stats(self) -> dict:
        if not self._nightmare_history:
            return {"total": 0}
        risks = [nm.risk_score for nm in self._nightmare_history]
        return {
            "total": len(self._nightmare_history),
            "avg_risk": round(sum(risks) / len(risks), 3),
            "critical_count": len(self.critical_nightmares()),
            "max_risk": round(max(risks), 3),
        }

    def __repr__(self) -> str:
        return f"<ACG total_nightmares={self.total_generated}>"
