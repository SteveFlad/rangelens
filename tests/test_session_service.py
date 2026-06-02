from datetime import UTC, datetime

from app.device.models import ShotInput
from app.services.session_service import SessionService


class _StubReader:
    def __init__(self) -> None:
        self.club = None

    def capture_shot(self, club: str) -> ShotInput:
        self.club = club
        return ShotInput(
            timestamp=datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC),
            club=club,
            club_speed_mph=90.0,
            face_angle_deg=1.5,
            path_deg=-0.5,
            contact_point=0.0,
            source_mode="device",
        )


def test_session_service_uses_reader_in_device_mode() -> None:
    reader = _StubReader()
    service = SessionService(mock_mode=False, reader=reader)

    record, summary, insights = service.capture_shot("Driver")

    assert reader.club == "Driver"
    assert record.club == "Driver"
    assert record.club_speed_mph == 90.0
    assert summary.shot_count == 1
    assert insights


def test_session_service_closes_reader() -> None:
    reader = _StubReader()
    reader.closed = False
    reader.close = lambda: setattr(reader, "closed", True)
    service = SessionService(mock_mode=False, reader=reader)

    service.close()

    assert reader.closed is True
