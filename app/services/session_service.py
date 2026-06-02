from uuid import uuid4
from datetime import UTC, datetime

from app.analytics.ball_flight import estimate_shot
from app.analytics.dispersion import summarize_dispersion
from app.analytics.coaching_rules import coaching_insights
from app.device.optishot_reader import OptiShotReader
from app.device.mock_reader import MockReader


class SessionService:
    def __init__(self, mock_mode: bool = False, reader: object | None = None) -> None:
        self.session_id = str(uuid4())
        self.started_at = datetime.now(UTC).isoformat(timespec="seconds")
        self.mock_mode = mock_mode
        self.reader = reader if reader is not None else MockReader() if mock_mode else OptiShotReader()
        self.shots = []

    def capture_shot(self, club: str) -> tuple[object, object, list[str]]:
        if self.mock_mode:
            shot_input = self.reader.generate_shot(club)
        else:
            shot_input = self.reader.capture_shot(club)
        record = estimate_shot(shot_input)
        self.shots.append(record)
        summary = summarize_dispersion(self.shots)
        insights = coaching_insights(summary)
        return record, summary, insights

    def capture_mock_shot(self, club: str) -> tuple[object, object, list[str]]:
        return self.capture_shot(club)

    def close(self) -> None:
        close = getattr(self.reader, "close", None)
        if callable(close):
            close()
