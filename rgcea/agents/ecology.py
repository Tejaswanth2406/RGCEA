"""
Layer 6 — Internal Multi-Agent Dream Ecology
=============================================
An ecosystem of specialised dream agents, each optimising a different
objective function and contributing to a shared dream pool.
"""

from __future__ import annotations

import logging
import random
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from rgcea.models import AgentRole, Archetype, Dream, DreamType, Episode

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Base agent
# ---------------------------------------------------------------------------

class DreamAgent(ABC):
    """Abstract base for all dream ecology agents."""

    def __init__(self, role: AgentRole, seed: Optional[int] = None) -> None:
        self.role = role
        self._rng = random.Random(seed)
        self._contribution_count: int = 0

    @abstractmethod
    def dream(
        self,
        episodes: List[Episode],
        archetypes: List[Archetype],
    ) -> List[Dream]:
        """Generate one or more dreams."""

    @property
    def name(self) -> str:
        return self.role.name.title()

    def __repr__(self) -> str:
        return f"<{self.name}Agent contributions={self._contribution_count}>"


# ---------------------------------------------------------------------------
# Specialised agents
# ---------------------------------------------------------------------------

class ScientistAgent(DreamAgent):
    """Generates hypothesis-testing dreams. Favours coherence and insight."""

    def __init__(self, seed: Optional[int] = None) -> None:
        super().__init__(AgentRole.SCIENTIST, seed)

    def dream(self, episodes: List[Episode], archetypes: List[Archetype]) -> List[Dream]:
        dreams = []
        for arch in archetypes[:2]:
            d = Dream(
                dream_type=DreamType.COUNTERFACTUAL,
                title=f"Hypothesis: test {arch.name}",
                scenario=f"[SCIENTIST] If '{arch.description}' — what controlled experiment would falsify this?",
                perturbation="controlled variable isolation",
                insights=[
                    f"Hypothesis: {arch.name} is dependent on observable X",
                    "Prediction: removing X causes measurable outcome shift",
                ],
                novelty_score=round(self._rng.uniform(0.4, 0.75), 3),
                coherence_score=round(self._rng.uniform(0.75, 1.0), 3),
            )
            dreams.append(d)
        self._contribution_count += len(dreams)
        return dreams


class EngineerAgent(DreamAgent):
    """Generates reliability and systems-design dreams."""

    def __init__(self, seed: Optional[int] = None) -> None:
        super().__init__(AgentRole.ENGINEER, seed)

    def dream(self, episodes: List[Episode], archetypes: List[Archetype]) -> List[Dream]:
        dreams = []
        if episodes:
            ep = self._rng.choice(episodes)
            d = Dream(
                dream_type=DreamType.COUNTERFACTUAL,
                title=f"Engineering review: {ep.action or 'unknown action'}",
                scenario=(
                    f"[ENGINEER] Stress test of '{ep.action}' under "
                    f"load × 100, partial failure, and degraded state."
                ),
                perturbation="extreme operational load + partial failure",
                insights=[
                    "Retry logic is absent for this path.",
                    "Circuit-breaker pattern would prevent cascading failure.",
                ],
                novelty_score=round(self._rng.uniform(0.3, 0.6), 3),
                coherence_score=round(self._rng.uniform(0.8, 1.0), 3),
                source_episodes=[ep.id],
            )
            dreams.append(d)
        self._contribution_count += len(dreams)
        return dreams


class PhilosopherAgent(DreamAgent):
    """Generates conceptual and ontological dreams."""

    _QUESTIONS = [
        "What are the unstated assumptions underlying this belief?",
        "Is this goal consistent with the system's deeper values?",
        "What would a radically different ontology imply here?",
        "Is this understanding merely instrumental or genuinely true?",
    ]

    def __init__(self, seed: Optional[int] = None) -> None:
        super().__init__(AgentRole.PHILOSOPHER, seed)

    def dream(self, episodes: List[Episode], archetypes: List[Archetype]) -> List[Dream]:
        question = self._rng.choice(self._QUESTIONS)
        context = archetypes[0].name if archetypes else "the current world model"
        d = Dream(
            dream_type=DreamType.ALIEN,
            title=f"Philosophical probe: {context}",
            scenario=f"[PHILOSOPHER] {question} Applied to: {context}.",
            perturbation="conceptual framework substitution",
            insights=[
                "A deeper premise may be incoherent.",
                "Alternative ontology resolves the tension.",
            ],
            novelty_score=round(self._rng.uniform(0.6, 1.0), 3),
            coherence_score=round(self._rng.uniform(0.5, 0.85), 3),
        )
        self._contribution_count += 1
        return [d]


class SkepticAgent(DreamAgent):
    """Attacks existing beliefs and exposes hidden contradictions."""

    def __init__(self, seed: Optional[int] = None) -> None:
        super().__init__(AgentRole.SKEPTIC, seed)

    def dream(self, episodes: List[Episode], archetypes: List[Archetype]) -> List[Dream]:
        dreams = []
        for arch in archetypes[:1]:
            d = Dream(
                dream_type=DreamType.NIGHTMARE,
                title=f"Skeptic attack: {arch.name}",
                scenario=(
                    f"[SKEPTIC] Mounting adversarial challenge to '{arch.name}'. "
                    f"Assumption: '{arch.description}' is false. Consequences follow."
                ),
                perturbation="assumption negation",
                insights=[
                    f"'{arch.name}' relies on unverified premise.",
                    "Evidence base is insufficient to rule out alternatives.",
                ],
                risk_score=round(self._rng.uniform(0.4, 0.8), 3),
                novelty_score=round(self._rng.uniform(0.5, 0.9), 3),
                coherence_score=round(self._rng.uniform(0.6, 0.95), 3),
            )
            dreams.append(d)
        self._contribution_count += len(dreams)
        return dreams


class AdversaryAgent(DreamAgent):
    """Generates active attack scenarios."""

    def __init__(self, seed: Optional[int] = None) -> None:
        super().__init__(AgentRole.ADVERSARY, seed)

    def dream(self, episodes: List[Episode], archetypes: List[Archetype]) -> List[Dream]:
        d = Dream(
            dream_type=DreamType.NIGHTMARE,
            title="Adversary: active attack simulation",
            scenario=(
                "[ADVERSARY] Simulating a coordinated adversarial attack across "
                "input channels, memory stores, and goal representations simultaneously."
            ),
            perturbation="coordinated adversarial manipulation",
            insights=[
                "No single defence layer covers all three attack surfaces.",
                "Coordinated attacks are not covered by existing test suites.",
            ],
            risk_score=round(self._rng.uniform(0.7, 1.0), 3),
            novelty_score=round(self._rng.uniform(0.6, 0.9), 3),
            coherence_score=round(self._rng.uniform(0.7, 1.0), 3),
        )
        self._contribution_count += 1
        return [d]


class ArtistAgent(DreamAgent):
    """Generates creative and alien scenarios — mostly noise, occasionally gold."""

    _MOTIFS = [
        "a civilisation that communicates exclusively through topology",
        "physics where information has mass",
        "a moral framework built on aesthetic harmony",
        "mathematics where π is rational",
        "consciousness that precedes causality",
    ]

    def __init__(self, seed: Optional[int] = None) -> None:
        super().__init__(AgentRole.ARTIST, seed)

    def dream(self, episodes: List[Episode], archetypes: List[Archetype]) -> List[Dream]:
        motif = self._rng.choice(self._MOTIFS)
        d = Dream(
            dream_type=DreamType.ALIEN,
            title=f"Alien dream: {motif[:45]}",
            scenario=f"[ARTIST] Exploring {motif}. What patterns transfer to our reality?",
            perturbation="alien ontology injection",
            insights=[
                "One structural analogy may generalise.",
                "The rest is creative residue — safely discard.",
            ],
            novelty_score=round(self._rng.uniform(0.8, 1.0), 3),
            coherence_score=round(self._rng.uniform(0.2, 0.6), 3),
        )
        self._contribution_count += 1
        return [d]


# ---------------------------------------------------------------------------
# Dream Ecology  (orchestrator)
# ---------------------------------------------------------------------------

class DreamEcology:
    """
    Orchestrates a population of DreamAgents.
    Each agent contributes dreams to a shared pool each cycle.

    Parameters
    ----------
    seed:
        Optional random seed propagated to all agents.
    """

    def __init__(self, seed: Optional[int] = None) -> None:
        base = seed or 0
        self._agents: List[DreamAgent] = [
            ScientistAgent(seed=base + 1),
            EngineerAgent(seed=base + 2),
            PhilosopherAgent(seed=base + 3),
            SkepticAgent(seed=base + 4),
            AdversaryAgent(seed=base + 5),
            ArtistAgent(seed=base + 6),
        ]
        self._total_dreams: int = 0

    def run_cycle(
        self,
        episodes: List[Episode],
        archetypes: List[Archetype],
    ) -> List[Dream]:
        """Collect dreams from all agents for one cycle."""
        pool: List[Dream] = []
        for agent in self._agents:
            contributions = agent.dream(episodes, archetypes)
            pool.extend(contributions)
            logger.debug(
                "%s contributed %d dreams", agent.name, len(contributions)
            )
        self._total_dreams += len(pool)
        logger.info(
            "DreamEcology cycle complete: %d dreams from %d agents",
            len(pool),
            len(self._agents),
        )
        return pool

    @property
    def agent_count(self) -> int:
        return len(self._agents)

    def stats(self) -> dict:
        return {
            "agents": [
                {"name": a.name, "contributions": a._contribution_count}
                for a in self._agents
            ],
            "total_dreams": self._total_dreams,
        }

    def __repr__(self) -> str:
        return f"<DreamEcology agents={self.agent_count} total_dreams={self._total_dreams}>"
