"""Constants for ha_norkko."""

from __future__ import annotations

from datetime import timedelta
from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "ha_norkko"
ATTRIBUTION = "Data provided by norkko.fi"
DATA_URL = "https://siirto.siitepoly.fi/media/sptied.txt"
UPDATE_INTERVAL = timedelta(hours=1)

POLLEN_TYPE_NAMES = {
    "L": "Alder",
    "C": "Hazel",
    "K": "Birch",
    "H": "Grasses",
    "P": "Mugwort",
    "T": "Plantain",
}
POLLEN_TYPE_LABELS_FI = {
    "L": "Leppä",
    "C": "Pähkinäpensas",
    "K": "Koivu",
    "H": "Heinät",
    "P": "Pujo",
    "T": "Tuoksukki",
}

SEVERITY_NAMES = {
    0: "none",
    1: "mild",
    2: "moderate",
    3: "high",
}

DEFAULT_POLLEN_ORDER = ["L", "C", "K", "H", "P", "T"]
