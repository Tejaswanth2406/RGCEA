# API Reference

## `RGCEA` (core orchestrator)

```python
from rgcea import RGCEA
```

### Constructor

```python
RGCEA(
    memory_capacity: int = 5_000,
    dreams_per_cycle: int = 8,
    nightmares_per_cycle: int = 4,
    seed: Optional[int] = None,
)
```

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `ingest(episodes)` | `None` | Store episodes into memory (wake phase) |
| `run_cycle()` | `CycleReport` | Execute one full dream cycle |
| `run_cycles(n)` | `List[CycleReport]` | Run *n* consecutive cycles |
| `summary()` | `dict` | Aggregate stats from all layers |
| `last_report()` | `CycleReport \| None` | Most recent cycle report |

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `current_ontology` | `OntologyFrame` | Active world model |
| `cycle_count` | `int` | Total cycles run |

---

## Data Models (`rgcea.models`)

### `Episode`
```python
@dataclass
class Episode:
    id: str                         # auto uuid
    state: Dict[str, Any]
    action: Optional[str]
    outcome: Optional[str]
    uncertainty: float              # 0=certain, 1=fully uncertain
    salience: float                 # importance weight 0–1
    timestamp: float
    tags: List[str]
```

### `Dream`
```python
@dataclass
class Dream:
    id: str
    dream_type: DreamType           # MEMORY | COUNTERFACTUAL | NIGHTMARE | ALIEN | RECURSIVE
    title: str
    scenario: str
    perturbation: str
    insights: List[str]
    risk_score: float               # 0–1
    novelty_score: float            # 0–1
    coherence_score: float          # 0–1
    source_episodes: List[str]
    timestamp: float
```

### `Archetype`
```python
@dataclass
class Archetype:
    id: str
    name: str
    description: str
    compressed_episodes: int
    fitness: float
    tags: List[str]
    metadata: Dict[str, Any]
```

### `OntologyFrame`
```python
@dataclass
class OntologyFrame:
    id: str
    name: str
    axioms: Dict[str, str]          # concept → definition
    fitness_scores: Dict[str, float]
    generation: int
    parent_id: Optional[str]
```

### `CycleReport`
```python
@dataclass
class CycleReport:
    cycle_id: str
    episodes_processed: int
    archetypes_created: int
    dreams_generated: int
    nightmares_generated: int
    ontologies_evaluated: int
    ontologies_selected: int
    immune_rejections: int
    duration_seconds: float
    timestamp: float
```

### `ImmuneReport`
```python
@dataclass
class ImmuneReport:
    target_id: str
    status: HealthStatus            # HEALTHY | WARNING | CRITICAL
    issues: List[str]
    passed_checks: List[str]
    recommendation: str             # "Accept" | "Accept with monitoring" | "Quarantine"
```

---

## Layer APIs

### `LatentEpisodicMemorySystem`
```python
lems.store(episode)
lems.store_batch(episodes)
lems.replay(n=32, min_salience=0.0) -> List[Episode]
lems.search_by_tag(tag) -> List[Episode]
lems.get(episode_id) -> Optional[Episode]
lems.stats() -> dict
lems.size  # property
```

### `SemanticCompressionEngine`
```python
sce.compress(episodes) -> List[Archetype]
sce.top_archetypes(n=10) -> List[Archetype]
sce.all_archetypes() -> List[Archetype]
sce.get_archetype(arch_id) -> Optional[Archetype]
sce.stats() -> dict
```

### `CounterfactualGenerativeSimulator`
```python
cgs.generate(episodes, archetypes, n=None) -> List[Dream]
cgs.recent_dreams(k=20) -> List[Dream]
cgs.total_generated  # property
cgs.stats() -> dict
```

### `AdversarialCatastropheGenerator`
```python
acg.generate(episodes, archetypes, n=None) -> List[Dream]
acg.critical_nightmares(threshold=0.85) -> List[Dream]
acg.recent_nightmares(k=10) -> List[Dream]
acg.total_generated  # property
acg.stats() -> dict
```

### `OntologicalPerturbationEngine`
```python
ope.perturb(parent=None, n=None) -> List[OntologyFrame]
ope.base_frame() -> OntologyFrame
ope.recent_frames(k=10) -> List[OntologyFrame]
ope.generation  # property
ope.stats() -> dict
```

### `CognitiveImmuneSystem`
```python
cis.validate_dream(dream) -> ImmuneReport
cis.validate_ontology(frame) -> ImmuneReport
cis.quarantine_size  # property
cis.stats() -> dict
```

### `OntologySelectionPressure`
```python
osp.select(frames, dreams=None) -> List[OntologyFrame]
osp.tournament_select(frames) -> OntologyFrame
osp.stats() -> dict
```

### `DreamEcology`
```python
ecology.run_cycle(episodes, archetypes) -> List[Dream]
ecology.agent_count  # property
ecology.stats() -> dict
```
