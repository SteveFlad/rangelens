import random

from datetime import UTC, datetime

from app.device.models import ShotInput


class MockReader:
    def generate_shot(self, club: str = "7-Iron") -> ShotInput:
        return ShotInput(
            timestamp=datetime.now(UTC),
            club=club,
            club_speed_mph=round(random.uniform(75, 95), 1),
            face_angle_deg=round(random.uniform(-4, 4), 1),
            path_deg=round(random.uniform(-5, 5), 1),
            contact_point=round(random.uniform(-2, 2), 1),
            source_mode="mock",
        )
