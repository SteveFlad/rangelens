from dataclasses import dataclass
from datetime import datetime
import random


@dataclass
class ShotInput:
    timestamp: datetime
    club: str
    club_speed_mph: float
    face_angle_deg: float
    path_deg: float
    contact_point: float
    source_mode: str


class MockReader:
    def generate_shot(self, club: str = "7-Iron") -> ShotInput:
        return ShotInput(
            timestamp=datetime.utcnow(),
            club=club,
            club_speed_mph=round(random.uniform(75, 95), 1),
            face_angle_deg=round(random.uniform(-4, 4), 1),
            path_deg=round(random.uniform(-5, 5), 1),
            contact_point=round(random.uniform(-2, 2), 1),
            source_mode="mock",
        )
