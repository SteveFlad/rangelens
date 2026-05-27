# RangeLens

RangeLens is a Windows-first desktop application for OptiShot 2 data capture, dispersion analytics, and coaching.

## Vision

RangeLens helps golfers practice with OptiShot hardware by capturing swing data, estimating shot outcomes, visualizing dispersion, and surfacing actionable coaching insights.

## MVP Goals

- Connect to OptiShot 2 on Windows 11
- Support mock mode when hardware is unavailable
- Capture and persist swing/shot data locally
- Compute dispersion and consistency metrics
- Show a live session view and top-down dispersion plot
- Generate deterministic rules-based coaching insights
- Export session data to CSV

## Tech Stack

- Python 3.11+
- PyQt6
- hidapi
- SQLite
- PyInstaller
- PyQtGraph

## Quick Start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m app.main --mock
```

## Planned Project Structure

```text
app/
  main.py
  config.py
  device/
  domain/
  analytics/
  storage/
  services/
  ui/
  utils/
tests/
scripts/
```

## Development Status

Initial scaffold created on a Copilot branch.
