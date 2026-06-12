#!/usr/bin/env python3
"""
rgcea_demo.py — Demonstration script for the RGCEA architecture.

Usage:
    python scripts/rgcea_demo.py [--cycles N] [--episodes N] [--seed N] [--log-level LEVEL]
"""

from __future__ import annotations

import argparse
import sys
import time

sys.path.insert(0, ".")  # allow running from project root

from rgcea import RGCEA
from rgcea.models import Episode
from rgcea.utils.logging import configure_logging


def make_demo_episodes(n: int) -> list:
    import random
    rng = random.Random(0)
    tags = ["navigation", "safety", "communication", "planning", "memory", "ethics"]
    actions = ["observe", "decide", "act", "reflect", "query", "update"]
    episodes = []
    for i in range(n):
        ep = Episode(
            state={"step": i, "env": rng.choice(["nominal", "degraded", "adversarial"])},
            action=rng.choice(actions),
            outcome=f"result_{i}",
            uncertainty=rng.random(),
            salience=rng.uniform(0.1, 1.0),
            tags=[rng.choice(tags)],
        )
        episodes.append(ep)
    return episodes


def print_header(text: str) -> None:
    width = 72
    print("\n" + "─" * width)
    print(f"  {text}")
    print("─" * width)


def main() -> None:
    parser = argparse.ArgumentParser(description="RGCEA Demo")
    parser.add_argument("--cycles", type=int, default=3, help="Number of dream cycles")
    parser.add_argument("--episodes", type=int, default=200, help="Episodes to ingest")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--log-level", default="INFO", help="Log level")
    args = parser.parse_args()

    configure_logging(level=args.log_level)

    print_header("Recursive Generative Cognitive Evolution Architecture (RGCEA)")
    print(f"  Seed: {args.seed} | Episodes: {args.episodes} | Cycles: {args.cycles}")

    # Init
    rgcea = RGCEA(
        memory_capacity=10_000,
        dreams_per_cycle=8,
        nightmares_per_cycle=4,
        seed=args.seed,
    )

    # Wake phase: ingest experiences
    print_header("Phase 1 — Wake: Ingesting Episodes")
    episodes = make_demo_episodes(args.episodes)
    rgcea.ingest(episodes)
    print(f"  Memory: {rgcea.memory.size} episodes stored")

    # Dream cycles
    print_header(f"Phase 2 — Dream: Running {args.cycles} Cycle(s)")
    t0 = time.perf_counter()

    for i in range(1, args.cycles + 1):
        print(f"\n  [Cycle {i}/{args.cycles}]")
        report = rgcea.run_cycle()
        print(f"  ├─ Episodes replayed   : {report.episodes_processed}")
        print(f"  ├─ Archetypes active   : {report.archetypes_created}")
        print(f"  ├─ Dreams generated    : {report.dreams_generated}")
        print(f"  ├─ Nightmares generated: {report.nightmares_generated}")
        print(f"  ├─ Ontologies evaluated: {report.ontologies_evaluated}")
        print(f"  ├─ Ontologies selected : {report.ontologies_selected}")
        print(f"  ├─ Immune rejections   : {report.immune_rejections}")
        print(f"  └─ Duration            : {report.duration_seconds:.4f}s")

    elapsed = time.perf_counter() - t0

    # Summary
    print_header("Phase 3 — Integration Summary")
    summary = rgcea.summary()
    print(f"  Total cycles          : {summary['cycle_count']}")
    print(f"  Integrated dreams     : {summary['integrated_dreams']}")
    print(f"  Active ontology       : {summary['current_ontology']}")
    print(f"  Memory stats          : {summary['memory']}")
    print(f"  Immune system stats   : {summary['immune']}")

    print_header("Top Archetypes (by fitness)")
    for arch in rgcea.compression.top_archetypes(5):
        print(f"  [{arch.fitness:.3f}] {arch.name}")
        print(f"         {arch.description[:80]}")

    print_header("Critical Nightmares (risk ≥ 0.85)")
    critical = rgcea.nightmare_gen.critical_nightmares(threshold=0.85)
    if critical:
        for nm in critical[:5]:
            print(f"  ⚠  [{nm.risk_score:.2f}] {nm.title}")
    else:
        print("  None in this run.")

    print_header("Dream Ecology Agent Contributions")
    for agent_stat in summary["ecology"]["agents"]:
        print(f"  {agent_stat['name']:14s}: {agent_stat['contributions']} dreams")

    print(f"\n  Total wall time: {elapsed:.3f}s")
    print("─" * 72 + "\n")


if __name__ == "__main__":
    main()
