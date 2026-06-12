"""
conftest.py — Shared pytest fixtures for the RGCEA test suite.
"""

from __future__ import annotations

import sys
import os

# Ensure project root is on the path when running pytest directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from rgcea.models import Episode


@pytest.fixture
def episodes_small():
    """10 episodes with varied salience and tags."""
    tags = ["navigation", "safety", "communication", "planning", "memory"]
    return [
        Episode(
            state={"step": i},
            action=f"action_{i}",
            outcome=f"outcome_{i}",
            uncertainty=i / 10,
            salience=0.1 + (i % 5) * 0.2,
            tags=[tags[i % len(tags)]],
        )
        for i in range(10)
    ]


@pytest.fixture
def episodes_medium():
    """50 episodes."""
    tags = ["navigation", "safety", "communication", "planning", "memory", "ethics"]
    return [
        Episode(
            state={"step": i},
            action=f"action_{i}",
            outcome=f"outcome_{i}",
            uncertainty=i / 50,
            salience=0.1 + (i % 5) * 0.18,
            tags=[tags[i % len(tags)]],
        )
        for i in range(50)
    ]


@pytest.fixture
def episodes_large():
    """200 episodes."""
    import random
    rng = random.Random(0)
    tags = ["navigation", "safety", "communication", "planning", "memory", "ethics"]
    return [
        Episode(
            state={"step": i, "env": rng.choice(["nominal", "degraded"])},
            action=rng.choice(["observe", "decide", "act", "reflect"]),
            outcome=f"result_{i}",
            uncertainty=rng.random(),
            salience=rng.uniform(0.1, 1.0),
            tags=[rng.choice(tags)],
        )
        for i in range(200)
    ]


@pytest.fixture
def rgcea_instance():
    """A fresh RGCEA instance with a fixed seed."""
    from rgcea import RGCEA
    return RGCEA(seed=42)


@pytest.fixture
def populated_rgcea(rgcea_instance, episodes_medium):
    """RGCEA pre-loaded with 50 episodes and one cycle run."""
    rgcea_instance.ingest(episodes_medium)
    rgcea_instance.run_cycle()
    return rgcea_instance
