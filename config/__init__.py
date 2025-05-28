"""
Shirtful WMS - Config Package
Konfigurationsdateien für alle Anwendungen.
"""

# Version Info
__version__ = "1.0.0"
__author__ = "Shirtful IT Team"

# Verfügbare Module
__all__ = [
    "settings",
    "translations",
    "database_config",
    "rfid_config"
]

# Config laden
from .settings import Settings
from .translations import Translations
from .database_config import DB_CONFIG
from .rfid_config import RFID_CONFIG

# Globale Config-Instanz
config = Settings()
translations = Translations()