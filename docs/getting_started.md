# Getting Started with RGCEA

## Installation

```bash
# From the project root
pip install -e ".[dev]"
```

RGCEA has **zero mandatory runtime dependencies** — it runs on the Python standard
library alone. The `[dev]` extra installs `pytest` and `pytest-cov` for testing.

---

## Your First Dream Cycle

```python
from rgcea import RGCEA
from rgcea.models import Episode

# 1. Create the architecture
rgcea = RGCEA(seed=42)

# 2. Wake phase — feed it some experiences
episodes = [
    Episode(
        state={"environment": "production", "load": 0.7},
        action="serve_request",
        outcome="success",
        uncertainty=0.1,
        salience=0.4,
        tags=["api"],
    ),
    Episode(
        state={"environment": "production", "load": 0.95},
        action="serve_request",
        outcome="timeout",
        uncertainty=0.6,
        salience=0.9,          # high salience — anomalous!
        tags=["api", "failure"],
    ),
]
rgcea.ingest(episodes)

# 3. Dream phase
report = rgcea.run_cycle()
print(f"Dreams: {report.dreams_generated}, Nightmares: {report.nightmares_generated}")
print(f"Active ontology: {rgcea.current_ontology.name}")
```

---

## Running Multiple Cycles

```python
rgcea.ingest(my_episodes)
reports = rgcea.run_cycles(10)

for i, r in enumerate(reports, 1):
    print(f"Cycle {i}: {r.dreams_generated} dreams, {r.immune_rejections} rejected")
```

---

## Inspecting Results

```python
summary = rgcea.summary()

# Top archetypes (compressed failure classes)
for arch in rgcea.compression.top_archetypes(5):
    print(f"[{arch.fitness:.3f}] {arch.name}: {arch.description}")

# Critical nightmares
for nm in rgcea.nightmare_gen.critical_nightmares(threshold=0.9):
    print(f"⚠ {nm.title}")
    for insight in nm.insights:
        print(f"  → {insight}")

# Immune system health
print(rgcea.immune.stats())
```

---

## Running the Demo Script

```bash
# Default run (3 cycles, 200 episodes)
python scripts/rgcea_demo.py

# Custom run
python scripts/rgcea_demo.py --cycles 10 --episodes 1000 --seed 7 --log-level DEBUG
```

---

## Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=rgcea --cov-report=term-missing

# Single layer
pytest tests/test_rgcea.py::TestAdversarialCatastropheGenerator -v
```

---

## Extending RGCEA

### Custom Dream Agent

```python
from rgcea.agents.ecology import DreamAgent
from rgcea.models import AgentRole, Dream, DreamType, Episode, Archetype
from typing import List

class MyCustomAgent(DreamAgent):
    def __init__(self):
        super().__init__(role=AgentRole.SCIENTIST)

    def dream(self, episodes: List[Episode], archetypes: List[Archetype]) -> List[Dream]:
        return [
            Dream(
                dream_type=DreamType.COUNTERFACTUAL,
                title="My custom dream",
                scenario="Custom scenario here.",
                perturbation="custom perturbation",
                insights=["insight 1"],
                novelty_score=0.8,
                coherence_score=0.9,
            )
        ]

# Inject into ecology
rgcea.ecology._agents.append(MyCustomAgent())
```

### Custom Archetype

```python
from rgcea.models import Archetype

my_arch = Archetype(
    name="The Overconfident Classifier",
    description="High-confidence predictions in out-of-distribution regions",
    tags=["ml", "safety"],
)
rgcea.compression._archetypes[my_arch.id] = my_arch
```
