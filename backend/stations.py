"""
stations.py — Central station configuration for the Polar Logistics System.
"""
from typing import Dict

STATIONS: Dict[str, str] = {
    "BHARATI": "Bharati",
    "MAITRI": "Maitri",
    "HIMADRI": "Himadri",
}

def is_valid_station(station_id: str) -> bool:
    """Validate if the given station_id is a supported station."""
    return station_id in STATIONS
