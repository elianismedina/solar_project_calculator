# Solar Project Calculator

A Django-based application for calculating solar energy project requirements, including panel arrays, inverter configurations, and battery storage solutions based on geographic location and energy consumption patterns.

## Technical Stack
- **Framework:** Django 6.0.1
- **Language:** Python 3.12
- **Database:** SQLite
- **Package Manager:** `uv`
- **Key Libraries:** `geopy`, `numpy`, `openai`, `pandas`, `pvlib`

## Project Architecture
- `design/`: Core application containing models for solar components (Panels, Inverters, Batteries) and project-specific logic.
- `manage.py`: Django management script.
- `db.sqlite3`: Local database.

## Component Models
- **Panel:** Electrical and mechanical specifications for solar modules.
- **Inverter:** Specifications for Hybrid and Off-grid inverters.
- **Battery:** Specifications for energy storage units.
- **Project:** Container for specific solar installations.
- **ProjectSettings:** Configuration for location (lat/long), tilt, and autonomy.
- **MonthlyConsumption:** Historical energy usage data.

## Active Goals
- [x] **Image Uploads:** Implement the ability for users to upload images of panels, inverters, and batteries during creation.
- [ ] **Calculation Logic:** Refine the solar calculation algorithms in `design/services.py`.

## Technical Notes
- The project settings are expected to be in a `solar_project` module (per `manage.py`), but the directory structure needs verification.
- Media configuration (`MEDIA_URL`, `MEDIA_ROOT`) needs to be set up in Django settings to handle image uploads.