"""
Konstanten für Shirtful WMS
Zentrale Definition aller System-Konstanten.
"""

from enum import Enum, auto
from typing import Dict, List, Tuple

# === System-Konstanten ===

# Version
SYSTEM_VERSION = "1.0.0"
SYSTEM_NAME = "Shirtful WMS"
COMPANY_NAME = "Shirtful GmbH"

# Zeitzone
TIMEZONE = "Europe/Berlin"

# Arbeitszeiten
WORK_START_TIME = "06:00"
WORK_END_TIME = "22:00"
BREAK_AFTER_HOURS = 6
BREAK_DURATION_MINUTES = 30


# === Status-Konstanten ===

class PackageStatus(Enum):
    """Paket-Status im System."""
    RECEIVED = "Wareneingang"
    IN_PROCESSING = "In Veredelung"
    IN_FABRIC = "In Betuchung"
    QUALITY_CHECK = "Qualitätskontrolle"
    QUALITY_OK = "Qualität OK"
    REWORK_NEEDED = "Nacharbeit erforderlich"
    READY_TO_SHIP = "Versandbereit"
    SHIPPED = "Versendet"
    CANCELLED = "Storniert"
    ON_HOLD = "Zurückgestellt"


class DeliveryStatus(Enum):
    """Lieferungs-Status."""
    OPEN = "Offen"
    IN_PROGRESS = "In Bearbeitung"
    COMPLETED = "Abgeschlossen"
    CANCELLED = "Abgebrochen"


class EmployeeStatus(Enum):
    """Mitarbeiter-Status."""
    ACTIVE = "Aktiv"
    INACTIVE = "Inaktiv"
    ON_BREAK = "Pause"
    OFF_DUTY = "Feierabend"


class Priority(Enum):
    """Prioritätsstufen."""
    LOW = "Niedrig"
    NORMAL = "Normal"
    HIGH = "Hoch"
    EXPRESS = "Express"
    URGENT = "Dringend"


# === Prozess-Konstanten ===

# Veredelungsarten
PROCESSING_TYPES = [
    "Siebdruck",
    "Digitaldruck",
    "Stickerei",
    "Transferdruck",
    "Flexdruck",
    "Sublimation",
    "DTG (Direct to Garment)",
    "Flockdruck",
    "Lasergravur",
    "Sonstiges"
]

# Qualitätsfehler-Kategorien
QUALITY_ERROR_TYPES = [
    "Druckfehler",
    "Farbabweichung",
    "Positionsfehler",
    "Stoffdefekt",
    "Verschmutzung",
    "Falsche Größe",
    "Nahtfehler",
    "Motivfehler",
    "Beschädigung",
    "Sonstiges"
]

# Versandarten
SHIPPING_METHODS = [
    "DHL Express",
    "DHL Standard",
    "UPS",
    "DPD",
    "GLS",
    "Hermes",
    "FedEx",
    "Deutsche Post",
    "Spedition",
    "Selbstabholung"
]

# Lieferanten
SUPPLIERS = [
    "DHL",
    "UPS",
    "DPD",
    "GLS",
    "Hermes",
    "Direktlieferung",
    "Kunde",
    "Intern",
    "Sonstige"
]

# === UI-Konstanten ===

# Mindestgrößen für Touch-UI (in Pixeln)
MIN_BUTTON_HEIGHT = 48
MIN_BUTTON_WIDTH = 120
MIN_TOUCH_TARGET = 44

# Timeouts (in Millisekunden)
NOTIFICATION_TIMEOUT = 3000
SCANNER_TIMEOUT = 30000
LOGIN_TIMEOUT = 300000  # 5 Minuten
SESSION_TIMEOUT = 3600000  # 1 Stunde

# Limits
MAX_SCAN_RETRIES = 3
MAX_LOGIN_ATTEMPTS = 3
MAX_PACKAGE_BATCH = 50
MAX_FILE_SIZE_MB = 10

# === Datenbank-Konstanten ===

# Tabellennamen
TABLE_EMPLOYEES = "Employees"
TABLE_PACKAGES = "Packages"
TABLE_DELIVERIES = "Deliveries"
TABLE_PACKAGE_HISTORY = "PackageHistory"
TABLE_TIME_TRACKING = "TimeTracking"
TABLE_QUALITY_ISSUES = "QualityIssues"
TABLE_SETTINGS = "Settings"

# Feldlängen
MAX_QR_CODE_LENGTH = 50
MAX_ORDER_ID_LENGTH = 50
MAX_CUSTOMER_NAME_LENGTH = 100
MAX_NOTES_LENGTH = 500
MAX_TRACKING_NUMBER_LENGTH = 50

# === Validierungs-Konstanten ===

# QR-Code Format
QR_CODE_PREFIX = "PKG"
QR_CODE_PATTERN = r"^PKG-\d{4}-[A-F0-9]{6}$"

# Bestellnummer Format
ORDER_ID_PATTERN = r"^[A-Z0-9\-]+$"

# RFID-Tag Format
RFID_TAG_LENGTH = 8
RFID_TAG_PATTERN = r"^[A-F0-9]{8,16}$"

# === Farb-Mappings ===

STATUS_COLORS: Dict[str, str] = {
    PackageStatus.RECEIVED.value: "#2196F3",  # Blau
    PackageStatus.IN_PROCESSING.value: "#FF9800",  # Orange
    PackageStatus.IN_FABRIC.value: "#9C27B0",  # Lila
    PackageStatus.QUALITY_CHECK.value: "#00BCD4",  # Cyan
    PackageStatus.QUALITY_OK.value: "#4CAF50",  # Grün
    PackageStatus.REWORK_NEEDED.value: "#F44336",  # Rot
    PackageStatus.READY_TO_SHIP.value: "#8BC34A",  # Hellgrün
    PackageStatus.SHIPPED.value: "#607D8B",  # Grau
    PackageStatus.CANCELLED.value: "#E91E63",  # Pink
    PackageStatus.ON_HOLD.value: "#FFC107"  # Amber
}

PRIORITY_COLORS: Dict[str, str] = {
    Priority.LOW.value: "#9E9E9E",  # Grau
    Priority.NORMAL.value: "#2196F3",  # Blau
    Priority.HIGH.value: "#FF9800",  # Orange
    Priority.EXPRESS.value: "#F44336",  # Rot
    Priority.URGENT.value: "#E91E63"  # Pink
}


# === Berechtigungen ===

class Permission(Enum):
    """System-Berechtigungen."""
    # Wareneingang
    RECEIVE_PACKAGES = auto()
    CREATE_DELIVERY = auto()

    # Veredelung
    START_PROCESSING = auto()
    UPDATE_PROCESSING = auto()

    # Betuchung
    START_FABRIC = auto()
    UPDATE_FABRIC = auto()

    # Qualitätskontrolle
    PERFORM_QC = auto()
    OVERRIDE_QC = auto()

    # Versand
    SHIP_PACKAGES = auto()
    PRINT_LABELS = auto()

    # Administration
    MANAGE_USERS = auto()
    VIEW_REPORTS = auto()
    CHANGE_SETTINGS = auto()
    DELETE_DATA = auto()


# Rollen-Berechtigungen
ROLE_PERMISSIONS: Dict[str, List[Permission]] = {
    "Lagerarbeiter": [
        Permission.RECEIVE_PACKAGES,
        Permission.CREATE_DELIVERY,
        Permission.SHIP_PACKAGES
    ],
    "Veredelung": [
        Permission.START_PROCESSING,
        Permission.UPDATE_PROCESSING
    ],
    "Betuchung": [
        Permission.START_FABRIC,
        Permission.UPDATE_FABRIC
    ],
    "Qualitätskontrolle": [
        Permission.PERFORM_QC
    ],
    "Teamleiter": [
        Permission.RECEIVE_PACKAGES,
        Permission.CREATE_DELIVERY,
        Permission.START_PROCESSING,
        Permission.UPDATE_PROCESSING,
        Permission.START_FABRIC,
        Permission.UPDATE_FABRIC,
        Permission.PERFORM_QC,
        Permission.OVERRIDE_QC,
        Permission.SHIP_PACKAGES,
        Permission.PRINT_LABELS,
        Permission.VIEW_REPORTS
    ],
    "Administrator": [
        # Alle Berechtigungen
        perm for perm in Permission
    ]
}

# === Report-Konstanten ===

# Report-Typen
REPORT_TYPES = [
    "Tagesbericht",
    "Wochenbericht",
    "Monatsbericht",
    "Mitarbeiterbericht",
    "Qualitätsbericht",
    "Lieferantenbericht",
    "Kundenbericht"
]

# Export-Formate
EXPORT_FORMATS = [
    ("CSV", "csv"),
    ("Excel", "xlsx"),
    ("PDF", "pdf"),
    ("JSON", "json")
]

# === Sprach-Konstanten ===

# Verfügbare Sprachen
LANGUAGES = {
    'de': {
        'name': 'Deutsch',
        'flag': '🇩🇪',
        'locale': 'de_DE'
    },
    'en': {
        'name': 'English',
        'flag': '🇬🇧',
        'locale': 'en_US'
    },
    'tr': {
        'name': 'Türkçe',
        'flag': '🇹🇷',
        'locale': 'tr_TR'
    },
    'pl': {
        'name': 'Polski',
        'flag': '🇵🇱',
        'locale': 'pl_PL'
    }
}

# Standard-Sprache
DEFAULT_LANGUAGE = 'de'

# === Feiertage (Berlin 2024/2025) ===

HOLIDAYS_2024 = [
    "2024-01-01",  # Neujahr
    "2024-03-29",  # Karfreitag
    "2024-04-01",  # Ostermontag
    "2024-05-01",  # Tag der Arbeit
    "2024-05-09",  # Christi Himmelfahrt
    "2024-05-20",  # Pfingstmontag
    "2024-10-03",  # Tag der Deutschen Einheit
    "2024-12-25",  # 1. Weihnachtstag
    "2024-12-26",  # 2. Weihnachtstag
]

HOLIDAYS_2025 = [
    "2025-01-01",  # Neujahr
    "2025-04-18",  # Karfreitag
    "2025-04-21",  # Ostermontag
    "2025-05-01",  # Tag der Arbeit
    "2025-05-29",  # Christi Himmelfahrt
    "2025-06-09",  # Pfingstmontag
    "2025-10-03",  # Tag der Deutschen Einheit
    "2025-12-25",  # 1. Weihnachtstag
    "2025-12-26",  # 2. Weihnachtstag
]

# === Sonstige Konstanten ===

# Währung
CURRENCY = "EUR"
CURRENCY_SYMBOL = "€"

# Temperatur-Einheit
TEMPERATURE_UNIT = "°C"

# Gewichts-Einheit
WEIGHT_UNIT = "kg"

# Größen-Einheit
SIZE_UNIT = "cm"

# Pagination
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Cache-Zeiten (Sekunden)
CACHE_TTL_SHORT = 300  # 5 Minuten
CACHE_TTL_MEDIUM = 3600  # 1 Stunde
CACHE_TTL_LONG = 86400  # 1 Tag

# === Error Messages ===

ERROR_MESSAGES = {
    'CONNECTION_FAILED': "Verbindung fehlgeschlagen",
    'LOGIN_FAILED': "Anmeldung fehlgeschlagen",
    'INVALID_CREDENTIALS': "Ungültige Anmeldedaten",
    'SESSION_EXPIRED': "Sitzung abgelaufen",
    'PERMISSION_DENIED': "Zugriff verweigert",
    'NOT_FOUND': "Nicht gefunden",
    'VALIDATION_ERROR': "Validierungsfehler",
    'DATABASE_ERROR': "Datenbankfehler",
    'NETWORK_ERROR': "Netzwerkfehler",
    'UNKNOWN_ERROR': "Unbekannter Fehler"
}

# === Success Messages ===

SUCCESS_MESSAGES = {
    'LOGIN_SUCCESS': "Erfolgreich angemeldet",
    'LOGOUT_SUCCESS': "Erfolgreich abgemeldet",
    'SAVE_SUCCESS': "Erfolgreich gespeichert",
    'DELETE_SUCCESS': "Erfolgreich gelöscht",
    'UPDATE_SUCCESS': "Erfolgreich aktualisiert",
    'SEND_SUCCESS': "Erfolgreich gesendet",
    'SCAN_SUCCESS': "Erfolgreich gescannt",
    'PRINT_SUCCESS': "Erfolgreich gedruckt"
}

# Test
if __name__ == "__main__":
    print(f"=== {SYSTEM_NAME} v{SYSTEM_VERSION} ===\n")

    print("Package Status Values:")
    for status in PackageStatus:
        color = STATUS_COLORS.get(status.value, "#000000")
        print(f"  {status.name}: {status.value} (Color: {color})")

    print(f"\nTotal Constants Defined: {len(dir())}")