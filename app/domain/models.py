from dataclasses import dataclass


@dataclass
class ShotRecord:
    timestamp: str
    club: str
    club_speed_mph: float
    face_angle_deg: float
    path_deg: float
    carry_yards: float
    lateral_yards: float
    shot_shape: str
