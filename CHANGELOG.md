# Changelog

All notable changes to RGCEA are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [1.0.0] — 2024-06-12

### Added
- `LatentEpisodicMemorySystem` (LEMS) — salience-weighted episodic replay store
- `SemanticCompressionEngine` (SCE) — episode → archetype compression with 10 seed archetypes
- `CounterfactualGenerativeSimulator` (CGS) — "what if?" dream generation engine
- `AdversarialCatastropheGenerator` (ACG) — adversarial nightmare engine with 15 failure vectors
- `OntologicalPerturbationEngine` (OPE) — axiom-level world-model mutation
- `CognitiveImmuneSystem` (CIS) — coherence, risk, and value-alignment validation + quarantine
- `OntologySelectionPressure` (OSP) — evolutionary fitness selection over ontology frames
- `DreamEcology` — six specialised dream agents (Scientist, Engineer, Philosopher, Skeptic, Adversary, Artist)
- `RGCEA` core orchestrator — wires all layers into a single dream cycle API
- `CycleReport` dataclass — per-cycle diagnostics
- `ImmuneReport` dataclass — per-artifact immune validation result
- CLI demo script `scripts/rgcea_demo.py`
- 30-test suite covering all layers and integration paths
- Docs: architecture, API reference, getting started guide
- Zero mandatory runtime dependencies
