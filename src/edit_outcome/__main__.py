"""Calibrate designed editor calls on years at or after 2022."""

from __future__ import annotations

from .engine import calibrate, format_report

ROWS = [
    {"id": "a", "year": 2019, "observed": "intended", "predicted": {"intended": 0.82, "bystander": 0.08, "indel": 0.05, "unchanged": 0.05}},
    {"id": "b", "year": 2020, "observed": "intended", "predicted": {"intended": 0.78, "bystander": 0.12, "indel": 0.05, "unchanged": 0.05}},
    {"id": "c", "year": 2021, "observed": "bystander", "predicted": {"intended": 0.55, "bystander": 0.25, "indel": 0.10, "unchanged": 0.10}},
    {"id": "d", "year": 2023, "observed": "unchanged", "predicted": {"intended": 0.80, "bystander": 0.10, "indel": 0.05, "unchanged": 0.05}},
    {"id": "e", "year": 2024, "observed": "indel", "predicted": {"intended": 0.74, "bystander": 0.10, "indel": 0.11, "unchanged": 0.05}},
    {"id": "f", "year": 2024, "observed": "bystander", "predicted": {"intended": 0.30, "bystander": 0.30, "indel": 0.20, "unchanged": 0.20}},
]


def main() -> int:
    print(format_report(calibrate(ROWS, 2022)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
