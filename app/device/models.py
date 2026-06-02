from dataclasses import dataclass
from datetime import datetime


@dataclass
class DeviceInfo:
    path: bytes | str | None
    vendor_id: int
    product_id: int
    manufacturer: str | None = None
    product: str | None = None
    serial_number: str | None = None


@dataclass
class ShotInput:
    timestamp: datetime
    club: str
    club_speed_mph: float
    face_angle_deg: float
    path_deg: float
    contact_point: float
    source_mode: str
