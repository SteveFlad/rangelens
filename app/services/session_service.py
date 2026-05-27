from uuid import uuid4
from datetime import datetime

from app.analytics.ball_flight import estimate_shot
from app.analytics.dispersion import summarize_dispersion
from app.analytics.coaching_rules import coaching_insights
from app.device.mock_reader import MockReader


class SessionService:
    def __init__(self) -> None:
        self.session_id = str(uuid4())
        self.started_at = datetime.utcnow().isoformat(timespec="seconds")
        self.reader = MockReader()
        self.shots = []

    def capture_mock_shot(self, club: str) -> tuple[object, object, list[str]]:
        shot_input = self.reader.generate_shot(club)
        record = estimate_shot(shot_input)
        self.shots.append(record)
        summary = summarize_dispersion(self.shots)
        insights = coaching_insights(summary)
        return record, summary, insights
