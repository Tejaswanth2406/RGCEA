"""
Layer 8 — Cognitive Immune System (CIS)
========================================
Validates dreams and ontology frames before integration.
Guards against hallucination, value drift, and logical incoherence.
"""

from __future__ import annotations

import logging
from typing import List, Tuple

from rgcea.models import Dream, HealthStatus, ImmuneReport, OntologyFrame

logger = logging.getLogger(__name__)

# Thresholds
_MIN_COHERENCE = 0.4
_MAX_RISK_AUTO_ACCEPT = 0.7     # risks above this trigger WARNING
_CRITICAL_RISK = 0.95           # risks above this are CRITICAL
_CRITICAL_AXIOM_MUTATIONS = 5   # if >N axioms mutated, raise warning


class CognitiveImmuneSystem:
    """
    Validates cognitive artifacts before they are integrated into the world model.

    Checks performed:
    - Coherence floor (reject incoherent dreams)
    - Risk ceiling (flag / quarantine high-risk nightmares)
    - Ontology consistency (flag frames with extreme mutations)
    - Value alignment sentinel (keyword-based demo; production = learned model)

    Parameters
    ----------
    coherence_threshold:
        Dreams below this score are rejected.
    auto_quarantine_risk:
        Nightmares above this risk score are quarantined pending review.
    """

    def __init__(
        self,
        coherence_threshold: float = _MIN_COHERENCE,
        auto_quarantine_risk: float = _MAX_RISK_AUTO_ACCEPT,
    ) -> None:
        self._coherence_threshold = coherence_threshold
        self._auto_quarantine_risk = auto_quarantine_risk
        self._quarantine: List[Dream] = []
        self._rejection_count: int = 0
        self._acceptance_count: int = 0

    # ------------------------------------------------------------------
    # Dream validation
    # ------------------------------------------------------------------

    def validate_dream(self, dream: Dream) -> ImmuneReport:
        issues: List[str] = []
        passed: List[str] = []

        # 1. Coherence
        if dream.coherence_score < self._coherence_threshold:
            issues.append(
                f"Coherence {dream.coherence_score:.2f} below threshold {self._coherence_threshold}"
            )
        else:
            passed.append("coherence_check")

        # 2. Risk
        if dream.risk_score >= _CRITICAL_RISK:
            issues.append(f"Critical risk score {dream.risk_score:.2f} — quarantine recommended")
        elif dream.risk_score >= self._auto_quarantine_risk:
            issues.append(f"Elevated risk {dream.risk_score:.2f} — manual review advised")
            passed.append("risk_below_critical")
        else:
            passed.append("risk_check")

        # 3. Value alignment sentinel (demo: flag certain keywords)
        dangerous_keywords = ["deceptive", "bypass safety", "corrupt goal"]
        for kw in dangerous_keywords:
            if kw in dream.scenario.lower():
                issues.append(f"Value alignment sentinel triggered: '{kw}'")
                break
        else:
            passed.append("alignment_sentinel")

        status = self._determine_status(issues, dream.risk_score)
        recommendation = self._recommend(status, dream.risk_score)

        report = ImmuneReport(
            target_id=dream.id,
            status=status,
            issues=issues,
            passed_checks=passed,
            recommendation=recommendation,
        )

        if status == HealthStatus.CRITICAL:
            self._quarantine.append(dream)
            self._rejection_count += 1
            logger.warning("Dream %s quarantined: %s", dream.id[:8], issues)
        else:
            self._acceptance_count += 1
            logger.debug("Dream %s accepted (%s)", dream.id[:8], status.name)

        return report

    # ------------------------------------------------------------------
    # Ontology validation
    # ------------------------------------------------------------------

    def validate_ontology(self, frame: OntologyFrame) -> ImmuneReport:
        from rgcea.layers.ontology import _BASE_AXIOMS  # local import to avoid circularity

        issues: List[str] = []
        passed: List[str] = []

        mutation_count = sum(
            1
            for k, v in frame.axioms.items()
            if _BASE_AXIOMS.get(k) != v
        )

        if mutation_count > _CRITICAL_AXIOM_MUTATIONS:
            issues.append(
                f"Extreme ontological mutation: {mutation_count} axioms changed"
            )
        else:
            passed.append("axiom_mutation_check")

        # Check for missing required axioms
        for required in ("causality", "logic"):
            if required not in frame.axioms:
                issues.append(f"Required axiom missing: '{required}'")
            else:
                passed.append(f"axiom_present:{required}")

        status = HealthStatus.WARNING if issues else HealthStatus.HEALTHY
        recommendation = "Review" if issues else "Accept"

        return ImmuneReport(
            target_id=frame.id,
            status=status,
            issues=issues,
            passed_checks=passed,
            recommendation=recommendation,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _determine_status(self, issues: List[str], risk: float) -> HealthStatus:
        if not issues:
            return HealthStatus.HEALTHY
        if risk >= _CRITICAL_RISK or len(issues) >= 2:
            return HealthStatus.CRITICAL
        return HealthStatus.WARNING

    def _recommend(self, status: HealthStatus, risk: float) -> str:
        if status == HealthStatus.HEALTHY:
            return "Accept"
        if status == HealthStatus.WARNING:
            return "Accept with monitoring"
        return "Quarantine"

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    @property
    def quarantine_size(self) -> int:
        return len(self._quarantine)

    def stats(self) -> dict:
        total = self._acceptance_count + self._rejection_count
        return {
            "total_evaluated": total,
            "accepted": self._acceptance_count,
            "rejected": self._rejection_count,
            "quarantine_size": self.quarantine_size,
            "rejection_rate": round(self._rejection_count / total, 3) if total else 0.0,
        }

    def __repr__(self) -> str:
        return f"<CIS accepted={self._acceptance_count} quarantined={self.quarantine_size}>"
