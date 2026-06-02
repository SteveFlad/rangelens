from app.device.optishot_reader import OptiShotReader


def _make_report(*subpackets: tuple[int, int, int, int]) -> list[int]:
    report: list[int] = []
    for front_byte, back_byte, signature, timing in subpackets:
        report.extend([
            front_byte,
            back_byte,
            signature,
            (timing >> 8) & 0xFF,
            timing & 0xFF,
        ])
    report.extend([0] * (60 - len(report)))
    return report


class _FakeDevice:
    def __init__(self, reports: list[list[int]]) -> None:
        self._reports = list(reports)
        self.opened_path = None
        self.nonblocking = None
        self.writes: list[list[int]] = []
        self.closed = False

    def open_path(self, path: bytes) -> None:
        self.opened_path = path

    def set_nonblocking(self, value: bool) -> None:
        self.nonblocking = value

    def read(self, size: int, timeout_ms: int | None = None) -> list[int]:
        if self._reports:
            return self._reports.pop(0)
        return []

    def write(self, report: list[int]) -> None:
        self.writes.append(report)

    def close(self) -> None:
        self.closed = True


class _FakeHidModule:
    def __init__(self, device: _FakeDevice) -> None:
        self._device = device

    def enumerate(self, vendor_id: int, product_id: int) -> list[dict[str, object]]:
        return [
            {
                "path": b"optishot-device",
                "vendor_id": vendor_id,
                "product_id": product_id,
                "manufacturer_string": "OptiShot",
                "product_string": "OptiShot 2",
                "serial_number": "RL-001",
            }
        ]

    def device(self) -> _FakeDevice:
        return self._device


def test_optishot_reader_discovers_and_captures_shot() -> None:
    report = _make_report(
        (0x00, 0x30, 0x81, 60),
        (0x00, 0x40, 0x52, 60),
        (0x38, 0x00, 0x4A, 80),
    )
    device = _FakeDevice([report])
    reader = OptiShotReader(hid_module=_FakeHidModule(device))

    devices = reader.discover_devices()
    shot = reader.capture_shot("7-Iron", timeout_seconds=0.1)
    reader.close()

    assert len(devices) == 1
    assert devices[0].product == "OptiShot 2"
    assert device.opened_path == b"optishot-device"
    assert device.nonblocking is True
    assert device.closed is True
    assert [command[1] for command in device.writes] == [0x50, 0x52, 0x51, 0x52, 0x80]
    assert shot.club == "7-Iron"
    assert shot.source_mode == "device"
    assert shot.club_speed_mph == 115.0
    assert shot.face_angle_deg == 9.2
    assert shot.path_deg == -9.3
    assert shot.contact_point == 1.0
