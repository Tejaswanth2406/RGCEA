"""
Layer 9 — Ontology Selection Pressure (OSP)
============================================
Evaluates competing OntologyFrames and selects survivors.
Fitness criteria: predictive accuracy, compression efficiency, novelty, robustness.
"""

from __future__ import annotations

import logging
import math
import random
from typing import List, Optional, Tuple

from rgcea.models import Dream, OntologyFrame

logger = logging.getLogger(__name__)

_FITNESS_WEIGHTS = {
    "predictive_accuracy": 0.35,
    "compression_efficiency": 0.25,
    "novel_insight": 0.20,
    "robustness": 0.20,
}


class OntologySelectionPressure:
    """
    Runs evolutionary selection over a population of OntologyFrames.

    Parameters
    ----------
    survival_rate:
        Fraction of population that survives each selection round.
    tournament_size:
        Number of contestants per tournament selection.
    seed:
        Optional random seed.
    """

    def __init__(
        self,
        survival_rate: float = 0.4,
        tournament_size: int = 3,
        seed: Optional[int] = None,
    ) -> None:
        self._survival_rate = survival_rate
        self._tournament_size = tournament_size
        self._rng = random.Random(seed)
        self._selected_history: List[OntologyFrame] = []

    # ------------------------------------------------------------------
    # Selection
    # ------------------------------------------------------------------

    def select(
        self,
        frames: List[OntologyFrame],
        dreams: Optional[List[Dream]] = None,
    ) -> List[OntologyFrame]:
        """
        Score and select the fittest OntologyFrames from *frames*.

        Parameters
        ----------
        frames:
            Candidate frames to evaluate.
        dreams:
            Recent dreams used to estimate predictive accuracy.

        Returns
        -------
        Surviving frames sorted by fitness (descending).
        """
        if not frames:
            return []

        scored: List[Tuple[float, OntologyFrame]] = []
        for frame in frames:
            fitness = self._score(frame, dreams or [])
            frame.fitness_scores["composite"] = fitness
            scored.append((fitness, frame))

        scored.sort(key=lambda x: x[0], reverse=True)
        n_survivors = max(1, int(len(scored) * self._survival_rate))
        survivors = [frame for _, frame in scored[:n_survivors]]
        self._selected_history.extend(survivors)

        logger.info(
            "Selection: %d/%d frames survived (top fitness=%.3f)",
            len(survivors),
            len(frames),
            scored[0][0] if scored else 0.0,
        )
        return survivors

    def tournament_select(self, frames: List[OntologyFrame]) -> OntologyFrame:
        """Pick the best frame from a random tournament sub-sample."""
        k = min(self._tournament_size, len(frames))
        contestants = self._rng.sample(frames, k)
        return max(contestants, key=lambda f: f.fitness_scores.get("composite", 0.0))

    # ------------------------------------------------------------------
    # Fitness scoring
    # ------------------------------------------------------------------

    def _score(
        self,
        frame: OntologyFrame,
        dreams: List[Dream],
    ) -> float:
        components = {
            "predictive_accuracy": self._predictive_accuracy(frame, dreams),
            "compression_efficiency": self._compression_efficiency(frame),
            "novel_insight": self._novelty(frame),
            "robustness": self._robustness(frame),
        }
        frame.fitness_scores.update(components)
        composite = sum(
            v * _FITNESS_WEIGHTS[k] for k, v in components.items()
        )
        return round(composite, 4)

    def _predictive_accuracy(
        self, frame: OntologyFrame, dreams: List[Dream]
    ) -> float:
        """
        Proxy: frames with more axioms aligned to high-coherence dreams score higher.
        """
        if not dreams:
            return self._rng.uniform(0.4, 0.8)
        avg_coherence = sum(d.coherence_score for d in dreams) / len(dreams)
        axiom_count_factor = min(len(frame.axioms) / 10.0, 1.0)
        return round(avg_coherence * 0.7 + axiom_count_factor * 0.3, 3)

    def _compression_efficiency(self, frame: OntologyFrame) -> float:
        """Prefer frames with fewer, denser axioms."""
        n = len(frame.axioms)
        # Optimum around 8 axioms
        return round(1.0 - abs(n - 8) / 10.0, 3)

    def _novelty(self, frame: OntologyFrame) -> float:
        """Penalise frames identical to base; reward meaningful mutations."""
        mutated = sum(1 for k, v in frame.axioms.items() if "probabilistic" in v or "cyclic" in v or "contingent" in v)
        return round(min(mutated / 4.0, 1.0), 3)

    def _robustness(self, frame: OntologyFrame) -> float:
        """Proxy: higher generation = survived more selection rounds."""
        return round(min(frame.generation / 10.0 + self._rng.uniform(0.3, 0.6), 1.0), 3)

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    def stats(self) -> dict:
        return {
            "total_selected": len(self._selected_history),
            "survival_rate": self._survival_rate,
        }

    def __repr__(self) -> str:
        return f"<OSP survival_rate={self._survival_rate}>"
