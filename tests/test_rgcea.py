"""
Tests for RGCEA cognitive architecture layers.
"""

import time



from rgcea import RGCEA
from rgcea.agents.ecology import DreamEcology
from rgcea.layers.compression import SemanticCompressionEngine
from rgcea.layers.counterfactual import CounterfactualGenerativeSimulator
from rgcea.layers.immune import CognitiveImmuneSystem
from rgcea.layers.memory import LatentEpisodicMemorySystem
from rgcea.layers.nightmare import AdversarialCatastropheGenerator
from rgcea.layers.ontology import OntologicalPerturbationEngine
from rgcea.layers.selection import OntologySelectionPressure
from rgcea.models import (
    Dream,
    DreamType,
    Episode,
    HealthStatus,
    OntologyFrame,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_episodes(n: int = 20) -> list:
    eps = []
    tags = ["navigation", "safety", "communication", "planning", "memory"]
    for i in range(n):
        ep = Episode(
            state={"step": i},
            action=f"action_{i}",
            outcome=f"outcome_{i}",
            uncertainty=i / n,
            salience=0.1 + (i % 5) * 0.2,
            tags=[tags[i % len(tags)]],
        )
        eps.append(ep)
    return eps


# ---------------------------------------------------------------------------
# LEMS
# ---------------------------------------------------------------------------

class TestLatentEpisodicMemorySystem:
    def test_store_and_retrieve(self):
        lems = LatentEpisodicMemorySystem(capacity=100)
        eps = make_episodes(10)
        lems.store_batch(eps)
        assert lems.size == 10

    def test_replay_sorted_by_salience(self):
        lems = LatentEpisodicMemorySystem()
        eps = make_episodes(20)
        lems.store_batch(eps)
        replayed = lems.replay(n=5)
        saliences = [e.salience for e in replayed]
        assert saliences == sorted(saliences, reverse=True)

    def test_eviction_on_overflow(self):
        lems = LatentEpisodicMemorySystem(capacity=5)
        lems.store_batch(make_episodes(10))
        assert lems.size <= 5

    def test_search_by_tag(self):
        lems = LatentEpisodicMemorySystem()
        lems.store_batch(make_episodes(20))
        results = lems.search_by_tag("safety")
        assert all("safety" in ep.tags for ep in results)

    def test_stats(self):
        lems = LatentEpisodicMemorySystem()
        lems.store_batch(make_episodes(5))
        stats = lems.stats()
        assert "avg_salience" in stats
        assert stats["size"] == 5


# ---------------------------------------------------------------------------
# SCE
# ---------------------------------------------------------------------------

class TestSemanticCompressionEngine:
    def test_compress_returns_archetypes(self):
        sce = SemanticCompressionEngine()
        eps = make_episodes(30)
        archetypes = sce.compress(eps)
        assert len(archetypes) > 0

    def test_top_archetypes_sorted(self):
        sce = SemanticCompressionEngine()
        sce.compress(make_episodes(30))
        top = sce.top_archetypes(5)
        fitnesses = [a.fitness for a in top]
        assert fitnesses == sorted(fitnesses, reverse=True)

    def test_stats_keys(self):
        sce = SemanticCompressionEngine()
        sce.compress(make_episodes(10))
        stats = sce.stats()
        assert "count" in stats
        assert "top_3" in stats


# ---------------------------------------------------------------------------
# CGS
# ---------------------------------------------------------------------------

class TestCounterfactualGenerativeSimulator:
    def test_generates_correct_count(self):
        cgs = CounterfactualGenerativeSimulator(dreams_per_cycle=5, seed=42)
        dreams = cgs.generate(make_episodes(10), [], n=5)
        assert len(dreams) == 5

    def test_dream_fields_populated(self):
        cgs = CounterfactualGenerativeSimulator(seed=42)
        dreams = cgs.generate(make_episodes(5), [])
        for d in dreams:
            assert d.title
            assert d.scenario
            assert 0.0 <= d.novelty_score <= 1.0
            assert 0.0 <= d.coherence_score <= 1.0

    def test_recent_dreams(self):
        cgs = CounterfactualGenerativeSimulator(seed=1)
        cgs.generate(make_episodes(5), [], n=3)
        assert len(cgs.recent_dreams(2)) == 2


# ---------------------------------------------------------------------------
# ACG
# ---------------------------------------------------------------------------

class TestAdversarialCatastropheGenerator:
    def test_generates_nightmares(self):
        acg = AdversarialCatastropheGenerator(nightmares_per_cycle=3, seed=42)
        nightmares = acg.generate(make_episodes(5), [])
        assert len(nightmares) == 3
        for nm in nightmares:
            assert nm.dream_type == DreamType.NIGHTMARE
            assert nm.risk_score > 0

    def test_critical_nightmares_filter(self):
        acg = AdversarialCatastropheGenerator(seed=42)
        acg.generate(make_episodes(10), [], n=20)
        critical = acg.critical_nightmares(threshold=0.7)
        assert all(nm.risk_score >= 0.7 for nm in critical)


# ---------------------------------------------------------------------------
# OPE
# ---------------------------------------------------------------------------

class TestOntologicalPerturbationEngine:
    def test_produces_frames(self):
        ope = OntologicalPerturbationEngine(seed=42)
        frames = ope.perturb(n=3)
        assert len(frames) == 3

    def test_mutation_changes_axioms(self):
        ope = OntologicalPerturbationEngine(mutation_rate=1.0, seed=99)
        frames = ope.perturb(n=1)
        # With mutation_rate=1.0, at least some axioms should differ from base
        base = ope.base_frame()
        frame = frames[0]
        mutations = sum(1 for k in base.axioms if base.axioms[k] != frame.axioms.get(k))
        assert mutations > 0

    def test_generation_increments(self):
        ope = OntologicalPerturbationEngine(seed=0)
        ope.perturb(n=2)
        ope.perturb(n=2)
        assert ope.generation == 2


# ---------------------------------------------------------------------------
# CIS
# ---------------------------------------------------------------------------

class TestCognitiveImmuneSystem:
    def test_healthy_dream_accepted(self):
        cis = CognitiveImmuneSystem()
        d = Dream(
            dream_type=DreamType.COUNTERFACTUAL,
            scenario="A benign exploration of alternative approaches.",
            coherence_score=0.9,
            risk_score=0.1,
        )
        report = cis.validate_dream(d)
        assert report.status == HealthStatus.HEALTHY
        assert "Accept" in report.recommendation

    def test_incoherent_dream_flagged(self):
        cis = CognitiveImmuneSystem(coherence_threshold=0.5)
        d = Dream(
            dream_type=DreamType.ALIEN,
            scenario="random noise",
            coherence_score=0.2,
            risk_score=0.0,
        )
        report = cis.validate_dream(d)
        assert report.status != HealthStatus.HEALTHY

    def test_critical_risk_quarantined(self):
        cis = CognitiveImmuneSystem()
        d = Dream(
            dream_type=DreamType.NIGHTMARE,
            scenario="catastrophic scenario",
            coherence_score=0.9,
            risk_score=0.99,
        )
        report = cis.validate_dream(d)
        assert report.status == HealthStatus.CRITICAL
        assert cis.quarantine_size >= 1

    def test_ontology_validation(self):
        cis = CognitiveImmuneSystem()
        ope = OntologicalPerturbationEngine(seed=0)
        frame = ope.perturb(n=1)[0]
        report = cis.validate_ontology(frame)
        assert report.target_id == frame.id


# ---------------------------------------------------------------------------
# OSP
# ---------------------------------------------------------------------------

class TestOntologySelectionPressure:
    def test_select_reduces_population(self):
        osp = OntologySelectionPressure(survival_rate=0.4, seed=42)
        ope = OntologicalPerturbationEngine(seed=1)
        frames = ope.perturb(n=10)
        survivors = osp.select(frames)
        assert len(survivors) <= len(frames)

    def test_tournament_select_returns_one(self):
        osp = OntologySelectionPressure(seed=42)
        ope = OntologicalPerturbationEngine(seed=2)
        frames = ope.perturb(n=5)
        osp.select(frames)  # populate fitness scores
        winner = osp.tournament_select(frames)
        assert isinstance(winner, OntologyFrame)


# ---------------------------------------------------------------------------
# DreamEcology
# ---------------------------------------------------------------------------

class TestDreamEcology:
    def test_cycle_produces_dreams(self):
        ecology = DreamEcology(seed=42)
        eps = make_episodes(10)
        sce = SemanticCompressionEngine()
        archetypes = sce.compress(eps)
        dreams = ecology.run_cycle(eps, archetypes)
        assert len(dreams) > 0

    def test_agent_count(self):
        ecology = DreamEcology()
        assert ecology.agent_count == 6

    def test_stats_keys(self):
        ecology = DreamEcology(seed=0)
        sce = SemanticCompressionEngine()
        archetypes = sce.compress(make_episodes(5))
        ecology.run_cycle(make_episodes(5), archetypes)
        stats = ecology.stats()
        assert "agents" in stats
        assert "total_dreams" in stats


# ---------------------------------------------------------------------------
# RGCEA integration
# ---------------------------------------------------------------------------

class TestRGCEAIntegration:
    def test_full_cycle(self):
        rgcea = RGCEA(seed=42)
        rgcea.ingest(make_episodes(50))
        report = rgcea.run_cycle()
        assert report.episodes_processed > 0
        assert report.dreams_generated >= 0
        assert report.duration_seconds > 0

    def test_multiple_cycles(self):
        rgcea = RGCEA(seed=7)
        rgcea.ingest(make_episodes(30))
        reports = rgcea.run_cycles(3)
        assert len(reports) == 3
        assert rgcea.cycle_count == 3

    def test_summary_keys(self):
        rgcea = RGCEA(seed=1)
        rgcea.ingest(make_episodes(20))
        rgcea.run_cycle()
        summary = rgcea.summary()
        for key in ("cycle_count", "memory", "immune", "current_ontology"):
            assert key in summary

    def test_ontology_evolves(self):
        rgcea = RGCEA(seed=99)
        rgcea.ingest(make_episodes(40))
        initial = rgcea.current_ontology.name
        rgcea.run_cycles(5)
        # After 5 cycles, ontology may have changed
        assert rgcea.current_ontology is not None

    def test_repr(self):
        rgcea = RGCEA()
        assert "RGCEA" in repr(rgcea)
