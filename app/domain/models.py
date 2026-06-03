from dataclasses import dataclass


@dataclass
class ShotRecord:
    club: str
    club_speed_mph: float
    face_angle_deg: float
    path_deg: float
    contact_point: float
    carry_yards: float
    lateral_yards: float
    shot_shape: str
