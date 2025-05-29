"""
Konstanten und Konfiguration für die Wareneingangsstation.
"""

# Lieferanten
SUPPLIERS = [
    "DHL",
    "UPS",
    "DPD",
    "GLS",
    "Hermes",
    "Direktlieferung",
    "Sonstige"
]

# Prioritäten
PACKAGE_PRIORITIES = [
    "Normal",
    "Hoch",
    "Express"
]

# Test-Mitarbeiter für Manual Login
TEST_EMPLOYEES = [
    {
        'id': 1,
        'rfid_card': '1234567890',
        'first_name': 'Max',
        'last_name': 'Mustermann',
        'role': 'supervisor',
        'language': 'de',
        'department': 'Wareneingang',
        'is_active': True
    },
    {
        'id': 2,
        'rfid_card': '0987654321',
        'first_name': 'Anna',
        'last_name': 'Schmidt',
        'role': 'worker',
        'language': 'de',
        'department': 'Wareneingang',
        'is_active': True
    },
    {
        'id': 3,
        'rfid_card': 'test123',
        'first_name': 'Test',
        'last_name': 'User',
        'role': 'worker',
        'language': 'de',
        'department': 'Wareneingang',
        'is_active': True
    },
    {
        'id': 4,
        'rfid_card': 'manual',
        'first_name': 'Manual',
        'last_name': 'Login',
        'role': 'worker',
        'language': 'de',
        'department': 'Wareneingang',
        'is_active': True
    }
]

# UI-Konstanten
LANGUAGE_OPTIONS = [
    ('de', '🇩🇪'),
    ('en', '🇬🇧'),
    ('tr', '🇹🇷'),
    ('pl', '🇵🇱')
]

# Paket-Status
PACKAGE_STATUS = [
    "received",      # Empfangen
    "processing",    # In Bearbeitung
    "quality_check", # Qualitätskontrolle
    "ready",         # Bereit
    "shipped",       # Versendet
    "returned"       # Zurückgesendet
]

# Lieferungs-Status
DELIVERY_STATUS = [
    "active",        # Aktiv
    "completed",     # Abgeschlossen
    "cancelled",     # Storniert
    "partial"        # Teilweise
]

# Standard-Werte
DEFAULT_PACKAGE_PRIORITY = "Normal"
DEFAULT_PACKAGE_STATUS = "received"
DEFAULT_DELIVERY_STATUS = "active"
DEFAULT_LANGUAGE = "de"

# Validierungsregeln
VALIDATION_RULES = {
    'package_id_min_length': 5,
    'package_id_max_length': 50,
    'order_id_min_length': 3,
    'order_id_max_length': 30,
    'customer_name_min_length': 2,
    'customer_name_max_length': 100,
    'max_item_count': 9999,
    'min_item_count': 1,
    'delivery_note_max_length': 50,
    'notes_max_length': 500
}

# QR-Code-Patterns
QR_CODE_PATTERNS = {
    'shirtful_format': r'^[A-Z]+\^[A-Z0-9-]+\^[A-Z0-9]+\^[A-Z0-9-]+\^[0-9]+$',
    'order_number': r'[A-Z]{2}-\d{6,8}',
    'package_number': r'\b\d{10,20}\b',
    'tracking_number': r'[A-Z0-9]{10,25}'
}

# Zeitstempel-Formate
TIMESTAMP_FORMATS = {
    'display': '%d.%m.%Y %H:%M:%S',
    'display_short': '%H:%M:%S',
    'display_date': '%d.%m.%Y',
    'filename': '%Y%m%d_%H%M%S',
    'delivery_id': '%Y%m%d%H%M%S'
}

# Fehler-Meldungen
ERROR_MESSAGES = {
    'de': {
        'no_active_delivery': 'Keine aktive Lieferung vorhanden',
        'package_exists': 'Paket bereits registriert',
        'invalid_package_id': 'Ungültige Paket-ID',
        'invalid_order_id': 'Ungültige Bestellnummer',
        'missing_customer': 'Kundenname erforderlich',
        'invalid_item_count': 'Ungültige Artikelanzahl',
        'registration_failed': 'Registrierung fehlgeschlagen',
        'authentication_failed': 'Anmeldung fehlgeschlagen',
        'permission_denied': 'Keine Berechtigung',
        'validation_error': 'Validierungsfehler'
    },
    'en': {
        'no_active_delivery': 'No active delivery',
        'package_exists': 'Package already registered',
        'invalid_package_id': 'Invalid package ID',
        'invalid_order_id': 'Invalid order number',
        'missing_customer': 'Customer name required',
        'invalid_item_count': 'Invalid item count',
        'registration_failed': 'Registration failed',
        'authentication_failed': 'Authentication failed',
        'permission_denied': 'Permission denied',
        'validation_error': 'Validation error'
    }
}

# Success-Meldungen
SUCCESS_MESSAGES = {
    'de': {
        'delivery_created': 'Lieferung erfolgreich erstellt',
        'package_registered': 'Paket erfolgreich registriert',
        'delivery_completed': 'Lieferung erfolgreich abgeschlossen',
        'login_successful': 'Anmeldung erfolgreich',
        'logout_successful': 'Abmeldung erfolgreich'
    },
    'en': {
        'delivery_created': 'Delivery successfully created',
        'package_registered': 'Package successfully registered',
        'delivery_completed': 'Delivery successfully completed',
        'login_successful': 'Login successful',
        'logout_successful': 'Logout successful'
    }
}

# App-Konfiguration
APP_CONFIG = {
    'window_title': 'Shirtful WMS - Wareneingang',
    'window_size': '1024x768',
    'fullscreen_default': True,
    'auto_logout_minutes': 60,
    'scan_timeout_seconds': 30,
    'duplicate_scan_timeout_seconds': 3,
    'max_recent_packages': 50,
    'max_delivery_history': 100
}

# Logging-Konfiguration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S',
    'max_file_size_mb': 10,
    'backup_count': 5
}