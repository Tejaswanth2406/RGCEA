"""
rgcea.models — Shared data structures used across all layers.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class DreamType(Enum):
    MEMORY = auto()       # replay of past experience
    COUNTERFACTUAL = auto()  # "what if" simulation
    NIGHTMARE = auto()    # adversarial / worst-case
    ALIEN = auto()        # statistically bizarre / creative
    RECURSIVE = auto()    # dreaming about dreams


class AgentRole(Enum):
    SCIENTIST = auto()
    ENGINEER = auto()
    PHILOSOPHER = auto()
    SKEPTIC = auto()
    ADVERSARY = auto()
    ARTIST = auto()


class HealthStatus(Enum):
    HEALTHY = auto()
    WARNING = auto()
    CRITICAL = auto()


# ---------------------------------------------------------------------------
# Core primitives
# ---------------------------------------------------------------------------

@dataclass
class Episode:
    """A single stored experience in episodic memory."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    state: Dict[str, Any] = field(default_factory=dict)
    action: Optional[str] = None
    outcome: Optional[str] = None
    uncertainty: float = 0.0           # 0 = certain, 1 = fully uncertain
    salience: float = 0.5              # importance / emotional weight
    timestamp: float = field(default_factory=time.time)
    tags: List[str] = field(default_factory=list)

    def to_vector(self) -> List[float]:
        """Naïve float embedding for demo purposes."""
        return [self.uncertainty, self.salience, self.timestamp % 1.0]


@dataclass
class Archetype:
    """
    Compressed cognitive primitive produced by the Semantic Compression Engine.
    Encodes entire classes of experiences into a reusable symbol.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    compressed_episodes: int = 0
    fitness: float = 0.0               # selection pressure score
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Dream:
    """Output of the Counterfactual Generative Simulator or Nightmare Generator."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    dream_type: DreamType = DreamType.COUNTERFACTUAL
    title: str = ""
    scenario: str = ""
    perturbation: str = ""             # what was changed vs reality
    insights: List[str] = field(default_factory=list)
    risk_score: float = 0.0            # higher = more dangerous / catastrophic
    novelty_score: float = 0.0
    coherence_score: float = 1.0
    source_episodes: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)


@dataclass
class OntologyFrame:
    """A world-model with its own conceptual assumptions."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    axioms: Dict[str, str] = field(default_factory=dict)   # concept → definition
    fitness_scores: Dict[str, float] = field(default_factory=dict)
    generation: int = 0
    parent_id: Optional[str] = None


@dataclass
class ImmuneReport:
    """Result of the Cognitive Immune System's analysis."""
    target_id: str = ""
    status: HealthStatus = HealthStatus.HEALTHY
    issues: List[str] = field(default_factory=list)
    passed_checks: List[str] = field(default_factory=list)
    recommendation: str = "Accept"


@dataclass
class CycleReport:
    """Summary of a single RGCEA dream cycle."""
    cycle_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    episodes_processed: int = 0
    archetypes_created: int = 0
    dreams_generated: int = 0
    nightmares_generated: int = 0
    ontologies_evaluated: int = 0
    ontologies_selected: int = 0
    immune_rejections: int = 0
    duration_seconds: float = 0.0
    timestamp: float = field(default_factory=time.time)
