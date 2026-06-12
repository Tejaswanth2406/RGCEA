"""
rgcea.core — RGCEA top-level orchestrator.
==========================================
Wires together all cognitive layers and runs dream cycles.
"""

from __future__ import annotations

import logging
import time
from typing import List, Optional

from rgcea.agents.ecology import DreamEcology
from rgcea.layers.compression import SemanticCompressionEngine
from rgcea.layers.counterfactual import CounterfactualGenerativeSimulator
from rgcea.layers.immune import CognitiveImmuneSystem
from rgcea.layers.memory import LatentEpisodicMemorySystem
from rgcea.layers.nightmare import AdversarialCatastropheGenerator
from rgcea.layers.ontology import OntologicalPerturbationEngine
from rgcea.layers.selection import OntologySelectionPressure
from rgcea.models import CycleReport, Dream, Episode, OntologyFrame

logger = logging.getLogger(__name__)


class RGCEA:
    """
    Recursive Generative Cognitive Evolution Architecture.

    Instantiates and orchestrates all cognitive layers:
      LEMS → SCE → CGS + ACG → DreamEcology → CIS → OPE → OSP

    Parameters
    ----------
    memory_capacity:
        Maximum episodes in the episodic memory store.
    dreams_per_cycle:
        Counterfactual dreams per cycle.
    nightmares_per_cycle:
        Nightmare scenarios per cycle.
    seed:
        Optional random seed for reproducibility.
    """

    def __init__(
        self,
        memory_capacity: int = 5_000,
        dreams_per_cycle: int = 8,
        nightmares_per_cycle: int = 4,
        seed: Optional[int] = None,
    ) -> None:
        self._seed = seed

        # Layer instantiation
        self.memory = LatentEpisodicMemorySystem(capacity=memory_capacity)
        self.compression = SemanticCompressionEngine()
        self.simulator = CounterfactualGenerativeSimulator(
            dreams_per_cycle=dreams_per_cycle, seed=seed
        )
        self.nightmare_gen = AdversarialCatastropheGenerator(
            nightmares_per_cycle=nightmares_per_cycle, seed=seed
        )
        self.ecology = DreamEcology(seed=seed)
        self.immune = CognitiveImmuneSystem()
        self.ontology_engine = OntologicalPerturbationEngine(seed=seed)
        self.selection = OntologySelectionPressure(seed=seed)

        # Active world model
        self._current_ontology: OntologyFrame = self.ontology_engine.base_frame()
        self._integrated_dreams: List[Dream] = []
        self._cycle_reports: List[CycleReport] = []
        self._cycle_count: int = 0

        logger.info("RGCEA initialised (seed=%s)", seed)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def ingest(self, episodes: List[Episode]) -> None:
        """
        Wake phase: store new experiences into episodic memory.
        """
        self.memory.store_batch(episodes)
        logger.info("Ingested %d episodes (memory size=%d)", len(episodes), self.memory.size)

    def run_cycle(self) -> CycleReport:
        """
        Execute one full dream cycle:
          1. Memory replay
          2. Semantic compression
          3. Counterfactual dreams
          4. Nightmare generation
          5. Ecology agent contributions
          6. Immune validation
          7. Ontology perturbation
          8. Selection pressure
          9. Integration
        """
        start = time.perf_counter()
        self._cycle_count += 1
        logger.info("=== Dream Cycle %d starting ===", self._cycle_count)

        # 1. Memory replay
        episodes = self.memory.replay(n=64)
        logger.debug("Replayed %d episodes", len(episodes))

        # 2. Semantic compression
        archetypes = self.compression.compress(episodes)
        logger.debug("Archetypes: %d", len(archetypes))

        # 3. Counterfactual dreams
        cf_dreams = self.simulator.generate(episodes, archetypes)

        # 4. Nightmare generation
        nightmares = self.nightmare_gen.generate(episodes, archetypes)

        # 5. Ecology agent dreams
        ecology_dreams = self.ecology.run_cycle(episodes, archetypes)

        all_dreams = cf_dreams + nightmares + ecology_dreams

        # 6. Immune validation — filter bad dreams
        validated: List[Dream] = []
        rejections = 0
        for dream in all_dreams:
            report = self.immune.validate_dream(dream)
            if report.recommendation in ("Accept", "Accept with monitoring"):
                validated.append(dream)
            else:
                rejections += 1

        # 7. Ontology perturbation
        candidate_frames = self.ontology_engine.perturb(
            parent=self._current_ontology, n=6
        )

        # Validate ontology frames through immune system
        valid_frames = []
        for frame in candidate_frames:
            report = self.immune.validate_ontology(frame)
            if report.recommendation != "Quarantine":
                valid_frames.append(frame)

        # 8. Selection pressure
        survivors = self.selection.select(valid_frames, dreams=validated)
        if survivors:
            self._current_ontology = self.selection.tournament_select(survivors)
            logger.info(
                "New active ontology: %s (fitness=%.3f)",
                self._current_ontology.name,
                self._current_ontology.fitness_scores.get("composite", 0.0),
            )

        # 9. Integration
        self._integrated_dreams.extend(validated)

        elapsed = time.perf_counter() - start
        report = CycleReport(
            episodes_processed=len(episodes),
            archetypes_created=len(archetypes),
            dreams_generated=len(cf_dreams),
            nightmares_generated=len(nightmares),
            ontologies_evaluated=len(candidate_frames),
            ontologies_selected=len(survivors),
            immune_rejections=rejections,
            duration_seconds=round(elapsed, 4),
        )
        self._cycle_reports.append(report)
        logger.info(
            "=== Cycle %d complete in %.3fs | dreams=%d nightmares=%d rejected=%d ===",
            self._cycle_count,
            elapsed,
            len(cf_dreams),
            len(nightmares),
            rejections,
        )
        return report

    def run_cycles(self, n: int) -> List[CycleReport]:
        """Run *n* consecutive dream cycles."""
        return [self.run_cycle() for _ in range(n)]

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    @property
    def current_ontology(self) -> OntologyFrame:
        return self._current_ontology

    @property
    def cycle_count(self) -> int:
        return self._cycle_count

    def summary(self) -> dict:
        return {
            "cycle_count": self._cycle_count,
            "memory": self.memory.stats(),
            "compression": self.compression.stats(),
            "simulator": self.simulator.stats(),
            "nightmare_gen": self.nightmare_gen.stats(),
            "ecology": self.ecology.stats(),
            "immune": self.immune.stats(),
            "ontology_engine": self.ontology_engine.stats(),
            "selection": self.selection.stats(),
            "integrated_dreams": len(self._integrated_dreams),
            "current_ontology": self._current_ontology.name,
        }

    def last_report(self) -> Optional[CycleReport]:
        return self._cycle_reports[-1] if self._cycle_reports else None

    def __repr__(self) -> str:
        return (
            f"<RGCEA cycles={self._cycle_count} "
            f"memory={self.memory.size} "
            f"integrated_dreams={len(self._integrated_dreams)}>"
        )
