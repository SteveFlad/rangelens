from app.device.mock_reader import ShotInput
from app.domain.models import ShotRecord


def classify_shape(face_angle_deg: float, path_deg: float) -> str:
    delta = face_angle_deg - path_deg
    if delta > 2:
        return "fade"
    if delta < -2:
        return "draw"
    return "straight"


def estimate_shot(shot: ShotInput) -> ShotRecord:
    carry = max(40.0, shot.club_speed_mph * 1.9)
    lateral = (shot.face_angle_deg * 2.0) + (shot.path_deg * 1.2)
    return ShotRecord(
        timestamp=shot.timestamp.isoformat(timespec="seconds"),
        club=shot.club,
        club_speed_mph=shot.club_speed_mph,
        face_angle_deg=shot.face_angle_deg,
        path_deg=shot.path_deg,
        carry_yards=round(carry, 1),
        lateral_yards=round(lateral, 1),
        shot_shape=classify_shape(shot.face_angle_deg, shot.path_deg),
    )
