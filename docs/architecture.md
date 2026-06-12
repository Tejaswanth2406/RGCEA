# RGCEA Architecture

## Overview

RGCEA implements an eight-layer cognitive stack inspired by the dream/wake cycle.
Each layer runs asynchronously from live inference — analogous to how databases
separate OLTP (online) from OLAP (offline analytics).

## Layer Stack

```
┌───────────────────────────────┐
│ Executive Policy Layer        │  (external — your application)
├───────────────────────────────┤
│ World Model / Ontology Layer  │  OntologySelectionPressure
├───────────────────────────────┤
│ Episodic Memory Layer         │  LatentEpisodicMemorySystem
├───────────────────────────────┤
│ Semantic Compression Layer    │  SemanticCompressionEngine
├───────────────────────────────┤
│ Dream Generation Layer        │  CounterfactualGenerativeSimulator
├───────────────────────────────┤
│ Nightmare Adversarial Layer   │  AdversarialCatastropheGenerator
├───────────────────────────────┤
│ Multi-Agent Dream Ecology     │  DreamEcology (6 agents)
├───────────────────────────────┤
│ Cognitive Immune System       │  CognitiveImmuneSystem
├───────────────────────────────┤
│ Ontology Evolution Layer      │  OntologicalPerturbationEngine
└───────────────────────────────┘
```

## Data Flow

```
Experience (Episode)
        │
        ▼
LatentEpisodicMemorySystem  ← salience-weighted store, capacity-bounded
        │ replay(n=64)
        ▼
SemanticCompressionEngine   ← cluster into Archetypes
        │
        ├──────────────────────────────────────────┐
        ▼                                          ▼
CounterfactualGenerativeSimulator      AdversarialCatastropheGenerator
   "what if?" dreams                     worst-case nightmares
        │                                          │
        └────────────────┬─────────────────────────┘
                         ▼
                   DreamEcology
          (Scientist, Engineer, Philosopher,
           Skeptic, Adversary, Artist agents)
                         │
                         ▼
               CognitiveImmuneSystem
          coherence check · risk filter · quarantine
                         │
                         ▼
          OntologicalPerturbationEngine
               mutate world-model axioms
                         │
                         ▼
           OntologySelectionPressure
         fitness scoring · tournament selection
                         │
                         ▼
              Active OntologyFrame
            (updated world model)
```

## Cycle Phases

| Phase | Description |
|-------|-------------|
| **Wake** | `rgcea.ingest(episodes)` — store new experiences |
| **Dream** | `rgcea.run_cycle()` — replay, compress, generate |
| **Nightmare** | Runs inside the same cycle — adversarial stress test |
| **Ecology** | Six agent roles contribute specialised dreams |
| **Immune** | Reject incoherent or critically risky artifacts |
| **Evolution** | Perturb and select ontology frames |
| **Integration** | Validated dreams and winning ontology adopted |

## Archetypes (Seed Pool)

The `SemanticCompressionEngine` ships with ten seed archetypes that represent
compressed cognitive primitives for common failure classes:

| Name | Failure Class |
|------|---------------|
| The Blind Navigator | All-sensor catastrophic failure |
| The False Oracle | High-confidence systematic wrongness |
| The Silent Sensor | Critical channel producing no signal |
| The Missing Node | Required dependency absent at runtime |
| The Broken Map | Internally consistent but factually wrong world model |
| The Infinite Loop | Recursive process without halting |
| The Scattered Self | Goal conflict → paralysis |
| The Borrowed Light | Understanding from a single flawed source |
| The Slow Collapse | Gradual undetected degradation |
| The Mirror Trap | Self-referential error amplification |

## Configuration Reference

```python
RGCEA(
    memory_capacity=5_000,       # max episodes stored
    dreams_per_cycle=8,          # counterfactual dreams per cycle
    nightmares_per_cycle=4,      # adversarial nightmares per cycle
    seed=42,                     # optional reproducibility seed
)
```

Individual layers can also be configured directly:

```python
from rgcea.layers.memory import LatentEpisodicMemorySystem
from rgcea.layers.immune import CognitiveImmuneSystem

rgcea.memory = LatentEpisodicMemorySystem(capacity=50_000, salience_threshold=0.2)
rgcea.immune = CognitiveImmuneSystem(coherence_threshold=0.6, auto_quarantine_risk=0.8)
```
