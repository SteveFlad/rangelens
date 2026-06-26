from dataclasses import dataclass
from math import sqrt

from app.domain.models import ShotRecord


@dataclass
class DispersionSummary:
    shot_count: int
    avg_carry: float
    avg_lateral: float
    avg_contact: float
    max_radius: float
    dominant_miss: str


def summarize_dispersion(shots: list[ShotRecord]) -> DispersionSummary:
    if not shots:
        return DispersionSummary(0, 0.0, 0.0, 0.0, 0.0, "none")

    avg_carry = sum(s.carry_yards for s in shots) / len(shots)
    avg_lateral = sum(s.lateral_yards for s in shots) / len(shots)
    avg_contact = sum(s.contact_point for s in shots) / len(shots)
    max_radius = max(sqrt((s.carry_yards - avg_carry) ** 2 + (s.lateral_yards - avg_lateral) ** 2) for s in shots)
    dominant_miss = "right" if avg_lateral > 2 else "left" if avg_lateral < -2 else "center"
    return DispersionSummary(
        shot_count=len(shots),
        avg_carry=round(avg_carry, 1),
        avg_lateral=round(avg_lateral, 1),
        avg_contact=round(avg_contact, 2),
        max_radius=round(max_radius, 1),
        dominant_miss=dominant_miss,
    )
