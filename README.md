<img width="1983" height="793" alt="image" src="https://github.com/user-attachments/assets/9121d5f7-ee74-435d-9d01-7929b050d129" />
# RGCEA — Recursive Generative Cognitive Evolution Architecture

A production-grade Python implementation of the **dream-inspired AI cognition** framework described in the source documents.

## Overview

RGCEA models intelligence as a continuously evolving ecosystem of cognitive processes organised into layered subsystems — analogous to the dream/wake cycle in biological brains.

```
Experience
    ↓
Memory Store (LEMS)
    ↓
Semantic Compression (SCE)
    ↓
Counterfactual Dreams (CGS) ←→ Nightmare Engine (ACG)
    ↓
Dream Ecology (6 specialised agents)
    ↓
Cognitive Immune System (CIS)
    ↓
Ontology Perturbation (OPE)
    ↓
Selection Pressure (OSP)
    ↓
Improved World Model
```

## Architecture Layers

| Layer | Class | Purpose |
|---|---|---|
| 1 | `LatentEpisodicMemorySystem` | Salience-weighted experience replay |
| 2 | `SemanticCompressionEngine` | Compress episodes into archetypes |
| 3 | `CounterfactualGenerativeSimulator` | "What if?" dream generation |
| 4 | `AdversarialCatastropheGenerator` | Worst-case nightmare generation |
| 5 | `OntologicalPerturbationEngine` | Mutate world-model axioms |
| 6 | `DreamEcology` | Multi-agent dream ecosystem |
| 7 | `CognitiveImmuneSystem` | Validate and quarantine bad dreams |
| 8 | `OntologySelectionPressure` | Evolutionary selection over world models |

## Installation

```bash
pip install -e ".[dev]"
```

## Quick Start

```python
from rgcea import RGCEA
from rgcea.models import Episode

# Create the architecture
rgcea = RGCEA(seed=42)

# Ingest experiences (wake phase)
episodes = [
    Episode(
        state={"env": "nominal"},
        action="navigate",
        outcome="success",
        salience=0.8,
        tags=["navigation"],
    )
    for _ in range(100)
]
rgcea.ingest(episodes)

# Run dream cycles
for report in rgcea.run_cycles(3):
    print(f"Dreams: {report.dreams_generated}, Nightmares: {report.nightmares_generated}")

# Inspect results
print(rgcea.summary())
print(rgcea.current_ontology.name)
```

## Running the Demo

```bash
python scripts/rgcea_demo.py --cycles 5 --episodes 500 --seed 42
```

## Running Tests

```bash
pytest
# with coverage:
pytest --cov=rgcea --cov-report=term-missing
```

## Project Structure

```
rgcea/
├── rgcea/
│   ├── __init__.py
│   ├── core.py                  # RGCEA orchestrator
│   ├── models.py                # Shared data models
│   ├── layers/
│   │   ├── memory.py            # LEMS
│   │   ├── compression.py       # SCE
│   │   ├── counterfactual.py    # CGS
│   │   ├── nightmare.py         # ACG
│   │   ├── ontology.py          # OPE
│   │   ├── immune.py            # CIS
│   │   └── selection.py         # OSP
│   ├── agents/
│   │   └── ecology.py           # DreamEcology + 6 agent types
│   └── utils/
│       └── logging.py
├── tests/
│   └── test_rgcea.py
├── scripts/
│   └── rgcea_demo.py
├── pyproject.toml
└── README.md
```

## Conceptual Background

From the source documents:

> "General intelligence does not emerge solely from learning reality. It emerges from maintaining a continuously evolving ecosystem of counterfactual worlds, adversarial failures, alternative ontologies, and self-models that compete for integration into the active cognitive substrate."

The nine cognitive archetypes built into the `SemanticCompressionEngine` — *The Blind Navigator*, *The False Oracle*, *The Silent Sensor*, etc. — represent compressed representations of entire failure classes, inspired by the "nightmare compression" theory described in the documents.

## License

MIT
