"""
Shirtful WMS - Utils Package
Gemeinsame Hilfsmodule für alle Anwendungen.
"""

# Version Info
__version__ = "1.0.0"
__author__ = "Shirtful IT Team"

# Verfügbare Module
__all__ = [
    "rfid_auth",
    "database",
    "qr_scanner",
    "ui_components",
    "logger",
    "helpers",
    "constants"
]

# Gemeinsame Imports für einfachen Zugriff
from .rfid_auth import RFIDAuth
from .database import Database
from .qr_scanner import QRScanner
from .ui_components import UIComponents, COLORS, FONTS
from .logger import setup_logger
from .helpers import *
from .constants import *