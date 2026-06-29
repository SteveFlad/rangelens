from __future__ import annotations

import math
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Sequence

from app.config import (
    OPTISHOT_CAPTURE_TIMEOUT_SECONDS,
    OPTISHOT_CMD_ENABLE_SENSORS,
    OPTISHOT_CMD_LED_GREEN,
    OPTISHOT_CMD_LED_RED,
    OPTISHOT_CMD_SHUTDOWN,
    OPTISHOT_LED_SPACING,
    OPTISHOT_PRODUCT_ID,
    OPTISHOT_READ_TIMEOUT_MS,
    OPTISHOT_REPORT_SIZE,
    OPTISHOT_SENSOR_SPACING,
    OPTISHOT_SIGNATURE_CONTINUED,
    OPTISHOT_SIGNATURE_FRONT,
    OPTISHOT_SIGNATURE_ORIGIN,
    OPTISHOT_SPEED_CONVERSION_FACTOR,
    OPTISHOT_SUBPACKET_SIZE,
    OPTISHOT_VENDOR_ID,
)
from app.device.models import DeviceInfo, ShotInput


class OptiShotDeviceError(RuntimeError):
    """Raised when the OptiShot device cannot be used."""


def _decode_text(value: Any) -> str | None:
    if value in (None, ""):
        return None
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="ignore").rstrip("\x00") or None
    return str(value)


def _normalize_device_info(info: dict[str, Any]) -> DeviceInfo:
    return DeviceInfo(
        path=info.get("path"),
        vendor_id=int(info.get("vendor_id", OPTISHOT_VENDOR_ID)),
        product_id=int(info.get("product_id", OPTISHOT_PRODUCT_ID)),
        manufacturer=_decode_text(info.get("manufacturer_string")),
        product=_decode_text(info.get("product_string")),
        serial_number=_decode_text(info.get("serial_number")),
    )


@dataclass
class _ActivationWindow:
    minimum: int = 8
    maximum: int = -1

    def update(self, sensor_index: int) -> None:
        self.minimum = min(self.minimum, sensor_index)
        self.maximum = max(self.maximum, sensor_index)


class OptiShotShotParser:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self._back_origin = False
        self._front_triggered = False
        self._elapsed_time = 0
        self._speed_elapsed = 0
        self._first_front_seen = False
        self._potential_ball_read = False
        self._ball_timing_subtract = 0
        self._subpacket_timings: list[int] = []
        self._front_activations: list[tuple[int, int]] = []
        self._back_activations: list[tuple[int, int]] = []
        self._front_window = _ActivationWindow()
        self._back_window = _ActivationWindow()
        self._first_data_time: float = 0.0  # Track when we first started accumulating data
    
    def is_accumulating(self) -> bool:
        """Check if parser has started accumulating swing data."""
        return self._back_origin or self._front_triggered or len(self._front_activations) > 0 or len(self._back_activations) > 0

    def feed_report(self, report: Sequence[int], club: str, current_time: float) -> ShotInput | None:
        if len(report) < OPTISHOT_REPORT_SIZE:
            return None
        
        # Track first time we see any data
        if not self.is_accumulating() and self._first_data_time == 0.0:
            self._first_data_time = current_time

        for offset in range(0, OPTISHOT_REPORT_SIZE, OPTISHOT_SUBPACKET_SIZE):
            front_byte = int(report[offset])
            back_byte = int(report[offset + 1])
            signature = int(report[offset + 2])
            timing = (int(report[offset + 3]) << 8) + int(report[offset + 4])
            self._subpacket_timings.append(timing)

            if signature == OPTISHOT_SIGNATURE_ORIGIN:
                if front_byte == 0:
                    self._back_origin = True
                self._parse_front(front_byte, timing)
                self._parse_back(back_byte, timing)
                self._elapsed_time += timing
            elif signature == OPTISHOT_SIGNATURE_CONTINUED:
                self._parse_back(back_byte, timing)
                self._elapsed_time += timing
            elif signature == OPTISHOT_SIGNATURE_FRONT:
                self._front_triggered = True
                self._parse_front(front_byte, timing)
                self._elapsed_time += timing
                if not self._first_front_seen:
                    self._first_front_seen = True
                    self._speed_elapsed = self._elapsed_time
                if timing > 0x25:
                    self._potential_ball_read = True
                elif self._potential_ball_read and timing < 0x20 and len(self._subpacket_timings) >= 2:
                    self._ball_timing_subtract = self._subpacket_timings[-2]
                    self._potential_ball_read = False

        if not (self._back_origin and self._front_triggered):
            return None

        shot = self._build_shot(club)
        self.reset()
        return shot

    def _parse_front(self, byte_value: int, timing: int) -> None:
        if byte_value == 0:
            return
        for sensor_index in range(8):
            if (byte_value >> sensor_index) & 0x01:
                self._front_activations.append((sensor_index, timing))
                self._front_window.update(sensor_index)

    def _parse_back(self, byte_value: int, timing: int) -> None:
        if byte_value == 0:
            return
        for sensor_index in range(8):
            if (byte_value >> sensor_index) & 0x01:
                self._back_activations.append((sensor_index, timing))
                self._back_window.update(sensor_index)

    def _build_shot(self, club: str) -> ShotInput:
        speed_elapsed = self._speed_elapsed - self._ball_timing_subtract
        if speed_elapsed <= 0:
            raise OptiShotDeviceError("OptiShot report did not contain a valid swing speed.")

        club_speed_mph = (
            OPTISHOT_SENSOR_SPACING / (speed_elapsed * 18)
        ) * OPTISHOT_SPEED_CONVERSION_FACTOR
        if not 1 <= club_speed_mph <= 160:
            raise OptiShotDeviceError("OptiShot report produced an invalid club speed.")

        x_front = (self._front_window.maximum - self._front_window.minimum) * OPTISHOT_LED_SPACING
        x_back = (self._back_window.maximum - self._back_window.minimum) * OPTISHOT_LED_SPACING
        x_travel = (x_front + (2 * x_back)) / 3
        face_angle_deg = math.degrees(math.atan2(x_travel, OPTISHOT_SENSOR_SPACING))

        avg_front = self._average_sensor(self._front_activations)
        avg_back = self._average_sensor(self._back_activations)
        center = 4.0
        if avg_front < center:
            face_angle_deg = -face_angle_deg

        path_raw = 0.0
        if self._front_window.maximum >= 0 and self._back_window.maximum >= 0:
            path_raw = (
                (self._front_window.maximum - self._back_window.maximum)
                + (self._front_window.minimum - self._back_window.minimum)
            )
        path_deg = math.degrees(path_raw * (OPTISHOT_LED_SPACING / OPTISHOT_SENSOR_SPACING))
        path_deg = max(-15.0, min(15.0, path_deg))

        return ShotInput(
            timestamp=datetime.now(UTC),
            club=club,
            club_speed_mph=round(club_speed_mph, 1),
            face_angle_deg=round(face_angle_deg, 1),
            path_deg=round(path_deg, 1),
            contact_point=round(avg_back - center, 1),
            source_mode="device",
        )

    @staticmethod
    def _average_sensor(activations: list[tuple[int, int]]) -> float:
        if not activations:
            return 4.0
        return sum(sensor_index for sensor_index, _ in activations) / len(activations)


class OptiShotReader:
    def __init__(self, hid_module: Any | None = None) -> None:
        self._hid_module = hid_module
        self._device: Any | None = None
        self._device_info: DeviceInfo | None = None
        self._parser = OptiShotShotParser()
        self._previous_report: list[int] | None = None
        self._parser_timeout = 2.0  # Reset parser if accumulating data for more than 2 seconds

    def discover_devices(self) -> list[DeviceInfo]:
        hid_module = self._get_hid_module()
        return [
            _normalize_device_info(info)
            for info in hid_module.enumerate(OPTISHOT_VENDOR_ID, OPTISHOT_PRODUCT_ID)
        ]

    def connect(self) -> DeviceInfo:
        if self._device is not None and self._device_info is not None:
            return self._device_info

        devices = self.discover_devices()
        if not devices:
            raise OptiShotDeviceError(
                "OptiShot 2 device not found. Connect the launch monitor or run with --mock."
            )

        self._device_info = devices[0]
        hid_module = self._get_hid_module()
        self._device = hid_module.device()
        path = self._device_info.path
        if path and hasattr(self._device, "open_path"):
            self._device.open_path(path)
        else:
            self._device.open(OPTISHOT_VENDOR_ID, OPTISHOT_PRODUCT_ID)
        if hasattr(self._device, "set_nonblocking"):
            self._device.set_nonblocking(True)

        self._initialize_device()
        return self._device_info

    def check_for_swing(self, club: str) -> ShotInput | None:
        """Non-blocking check for swing. Returns shot if detected, None otherwise."""
        self.connect()
        
        current_time = time.monotonic()
        
        # Check if parser has been accumulating data for too long (likely noise)
        if self._parser.is_accumulating():
            elapsed = current_time - self._parser._first_data_time
            if elapsed > self._parser_timeout:
                # Reset parser - it's been collecting noise, not a real swing
                self._parser.reset()
                self._previous_report = None
                return None
        
        report = self._read_report()
        if not report:
            return None
        
        # Ignore duplicate reports
        if self._previous_report is not None and report == self._previous_report:
            return None
        
        # Ignore reports with very minimal activity (likely noise)
        if not self._parser.is_accumulating() and not self._has_significant_activity(report):
            return None
        
        self._previous_report = report
        shot = self._parser.feed_report(report, club, current_time)
        
        if shot is not None:
            # Reset parser for next swing detection
            self._parser.reset()
            # Thorough buffer flush to clear all residual data
            # UI cooldown prevents us from checking again too soon
            self._flush_device_buffer(quick=False)
            self._previous_report = None
            # Visual feedback
            self._send_command(OPTISHOT_CMD_LED_RED)
            self._send_command(OPTISHOT_CMD_LED_GREEN)
        
        return shot
    
    def _has_significant_activity(self, report: list[int]) -> bool:
        """Check if report has significant sensor activity (not just noise)."""
        if len(report) < OPTISHOT_REPORT_SIZE:
            return False
        
        # Count how many sensors are active across all subpackets
        active_count = 0
        for offset in range(0, OPTISHOT_REPORT_SIZE, OPTISHOT_SUBPACKET_SIZE):
            front_byte = int(report[offset])
            back_byte = int(report[offset + 1])
            # Count active sensors (bits set)
            active_count += bin(front_byte).count('1')
            active_count += bin(back_byte).count('1')
        
        # Require at least 3 active sensors to consider it real activity
        return active_count >= 3

    def capture_shot(
        self,
        club: str,
        timeout_seconds: float = OPTISHOT_CAPTURE_TIMEOUT_SECONDS,
    ) -> ShotInput:
        self.connect()
        self._parser.reset()
        self._previous_report = None

        # Turn LED RED to indicate not ready / busy capturing
        self._send_command(OPTISHOT_CMD_LED_RED)

        try:
            deadline = time.monotonic() + timeout_seconds
            while time.monotonic() < deadline:
                current_time = time.monotonic()
                report = self._read_report()
                if not report:
                    time.sleep(0.01)
                    continue
                if self._previous_report is not None and report == self._previous_report:
                    continue
                self._previous_report = report
                shot = self._parser.feed_report(report, club, current_time)
                if shot is not None:
                    # Turn LED GREEN to indicate ready for next swing
                    self._send_command(OPTISHOT_CMD_LED_GREEN)
                    return shot

            # Timeout - turn LED GREEN to indicate ready again
            self._send_command(OPTISHOT_CMD_LED_GREEN)
            raise OptiShotDeviceError("Timed out waiting for an OptiShot swing report.")
        except Exception:
            # On any error, ensure LED turns GREEN again
            self._send_command(OPTISHOT_CMD_LED_GREEN)
            raise

    def close(self) -> None:
        if self._device is None:
            return
        try:
            self._send_command(OPTISHOT_CMD_SHUTDOWN)
        finally:
            self._device.close()
            self._device = None
            self._device_info = None

    def _initialize_device(self) -> None:
        self._send_command(OPTISHOT_CMD_ENABLE_SENSORS)
        time.sleep(0.05)
        self._send_command(OPTISHOT_CMD_LED_GREEN)
        time.sleep(0.01)
        self._send_command(OPTISHOT_CMD_LED_RED)
        time.sleep(0.01)
        self._send_command(OPTISHOT_CMD_LED_GREEN)

    def _read_report(self) -> list[int]:
        assert self._device is not None
        try:
            report = self._device.read(OPTISHOT_REPORT_SIZE, OPTISHOT_READ_TIMEOUT_MS)
        except TypeError:
            report = self._device.read(OPTISHOT_REPORT_SIZE)
        if not report:
            return []
        return list(report[:OPTISHOT_REPORT_SIZE])

    def _send_command(self, command: int) -> None:
        if self._device is None:
            return
        report = [0x00, command] + [0x00] * (OPTISHOT_REPORT_SIZE - 1)
        self._device.write(report)

    def _flush_device_buffer(self, quick: bool = False) -> None:
        """Flush device buffer by reading and discarding reports.
        
        Args:
            quick: If True, only flush for ~50ms or until buffer is empty.
                   If False, flush more thoroughly for ~150ms.
        """
        if self._device is None:
            return
        
        flush_duration = 0.05 if quick else 0.15  # 50ms for quick, 150ms for thorough
        flush_start = time.monotonic()
        empty_count = 0
        
        while time.monotonic() - flush_start < flush_duration:
            report = self._read_report()
            if not report:
                empty_count += 1
                if empty_count >= 2:  # Two consecutive empty reads = buffer clear
                    break
                time.sleep(0.005)  # Brief pause before checking again
            else:
                empty_count = 0  # Reset if we got data

    def _get_hid_module(self) -> Any:
        if self._hid_module is None:
            try:
                import hid
            except ImportError as exc:
                raise OptiShotDeviceError(
                    "hidapi is not installed. Install dependencies before using device mode."
                ) from exc
            self._hid_module = hid
        return self._hid_module
