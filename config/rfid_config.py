"""
RFID-Konfiguration für Shirtful WMS
Einstellungen für TSHRW380BZMP RFID-Reader.
"""

import os
from typing import Dict, Any, List

# RFID-Hauptkonfiguration
RFID_CONFIG: Dict[str, Any] = {
    # === Verbindungseinstellungen ===
    'enabled': True,
    'port': 'AUTO',  # 'AUTO' für automatische Erkennung oder 'COM3', 'COM4', etc.
    'default_port': 'COM3',  # Fallback wenn AUTO fehlschlägt
    'baudrate': 9600,  # Standard für TSHRW380BZMP
    'timeout': 0.5,  # Sekunden
    'write_timeout': 0.5,  # Sekunden

    # === Reader-Einstellungen ===
    'reader_model': 'TSHRW380BZMP',
    'frequency': '13.56MHz',  # HF RFID
    'protocol': 'ISO14443A',  # Mifare

    # === Serielle Einstellungen ===
    'bytesize': 8,
    'parity': 'N',  # None
    'stopbits': 1,
    'xonxoff': False,
    'rtscts': False,
    'dsrdtr': False,

    # === Scan-Einstellungen ===
    'beep_on_scan': True,
    'beep_duration': 100,  # Millisekunden
    'led_on_scan': True,
    'auto_read': True,  # Automatisches Lesen aktivieren
    'continuous_read': True,  # Kontinuierliches Lesen
    'duplicate_timeout': 2.0,  # Sekunden - Duplikate ignorieren

    # === Performance ===
    'scan_interval': 0.1,  # Sekunden zwischen Scans
    'max_retries': 3,  # Maximale Wiederholungen
    'retry_delay': 0.5,  # Sekunden zwischen Wiederholungen
    'buffer_size': 1024,  # Bytes

    # === Erweiterte Einstellungen ===
    'anti_collision': True,  # Anti-Kollisions-Modus
    'rf_power': 'max',  # 'min', 'medium', 'max'
    'working_mode': 'active',  # 'active' oder 'passive'

    # === Debug ===
    'debug_mode': False,
    'log_raw_data': False,
    'simulate_mode': False,  # Für Tests ohne Hardware
}

# TSHRW380BZMP Kommandos
RFID_COMMANDS = {
    # === Basis-Kommandos ===
    'GET_VERSION': bytes.fromhex('AA BB 02 20 22'),
    'RESET': bytes.fromhex('AA BB 02 10 12'),
    'BEEP': bytes.fromhex('AA BB 02 40 42'),
    'LED_ON': bytes.fromhex('AA BB 03 41 01 43'),
    'LED_OFF': bytes.fromhex('AA BB 03 41 00 42'),

    # === Lese-Kommandos ===
    'READ_TAG_ONCE': bytes.fromhex('AA BB 02 25 27'),
    'READ_TAG_CONTINUOUS': bytes.fromhex('AA BB 03 50 01 52'),
    'STOP_CONTINUOUS': bytes.fromhex('AA BB 03 50 00 51'),

    # === Karten-Kommandos ===
    'GET_CARD_TYPE': bytes.fromhex('AA BB 02 21 23'),
    'READ_BLOCK': bytes.fromhex('AA BB 04 30'),  # + Block-Nr + Checksum
    'WRITE_BLOCK': bytes.fromhex('AA BB 14 31'),  # + Block-Nr + 16 Bytes + Checksum

    # === Konfigurations-Kommandos ===
    'SET_RF_POWER_MIN': bytes.fromhex('AA BB 03 60 00 61'),
    'SET_RF_POWER_MED': bytes.fromhex('AA BB 03 60 01 62'),
    'SET_RF_POWER_MAX': bytes.fromhex('AA BB 03 60 02 63'),
    'SET_ANTI_COLLISION_ON': bytes.fromhex('AA BB 03 61 01 63'),
    'SET_ANTI_COLLISION_OFF': bytes.fromhex('AA BB 03 61 00 62'),
}

# Response Codes
RFID_RESPONSES = {
    0x00: 'SUCCESS',
    0x01: 'NO_TAG',
    0x02: 'READ_ERROR',
    0x03: 'WRITE_ERROR',
    0x04: 'INVALID_COMMAND',
    0x05: 'CHECKSUM_ERROR',
    0x06: 'AUTH_ERROR',
    0x10: 'UNKNOWN_ERROR'
}

# Unterstützte Tag-Typen
SUPPORTED_TAGS = [
    'Mifare Classic 1K',
    'Mifare Classic 4K',
    'Mifare Ultralight',
    'NTAG213',
    'NTAG215',
    'NTAG216'
]

# Test-Tags für Entwicklung
TEST_TAGS = {
    '12345678': {
        'employee_id': 1,
        'name': 'Max Mustermann',
        'department': 'Lager',
        'role': 'Lagerarbeiter'
    },
    '87654321': {
        'employee_id': 2,
        'name': 'Erika Musterfrau',
        'department': 'Veredelung',
        'role': 'Teamleiter'
    },
    'ABCD1234': {
        'employee_id': 3,
        'name': 'John Doe',
        'department': 'Qualitätskontrolle',
        'role': 'Prüfer'
    },
    'ADMIN001': {
        'employee_id': 999,
        'name': 'Administrator',
        'department': 'IT',
        'role': 'Administrator'
    }
}

# COM-Port Suchpfade
COM_PORT_SEARCH_PATHS = [
    'COM1', 'COM2', 'COM3', 'COM4', 'COM5',
    'COM6', 'COM7', 'COM8', 'COM9', 'COM10',
    '/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2',
    '/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyACM2'
]

# Fehler-Nachrichten
RFID_ERROR_MESSAGES = {
    'de': {
        'NO_READER': 'RFID-Lesegerät nicht gefunden',
        'CONNECTION_FAILED': 'Verbindung zum Lesegerät fehlgeschlagen',
        'READ_ERROR': 'Fehler beim Lesen der Karte',
        'INVALID_TAG': 'Ungültige RFID-Karte',
        'TAG_NOT_FOUND': 'Karte nicht im System registriert',
        'TIMEOUT': 'Zeitüberschreitung beim Lesen',
        'HARDWARE_ERROR': 'Hardware-Fehler am Lesegerät'
    },
    'en': {
        'NO_READER': 'RFID reader not found',
        'CONNECTION_FAILED': 'Connection to reader failed',
        'READ_ERROR': 'Error reading card',
        'INVALID_TAG': 'Invalid RFID card',
        'TAG_NOT_FOUND': 'Card not registered in system',
        'TIMEOUT': 'Read timeout',
        'HARDWARE_ERROR': 'Hardware error on reader'
    },
    'tr': {
        'NO_READER': 'RFID okuyucu bulunamadı',
        'CONNECTION_FAILED': 'Okuyucuya bağlantı başarısız',
        'READ_ERROR': 'Kart okuma hatası',
        'INVALID_TAG': 'Geçersiz RFID kartı',
        'TAG_NOT_FOUND': 'Kart sistemde kayıtlı değil',
        'TIMEOUT': 'Okuma zaman aşımı',
        'HARDWARE_ERROR': 'Okuyucu donanım hatası'
    },
    'pl': {
        'NO_READER': 'Nie znaleziono czytnika RFID',
        'CONNECTION_FAILED': 'Połączenie z czytnikiem nie powiodło się',
        'READ_ERROR': 'Błąd odczytu karty',
        'INVALID_TAG': 'Nieprawidłowa karta RFID',
        'TAG_NOT_FOUND': 'Karta nie jest zarejestrowana w systemie',
        'TIMEOUT': 'Przekroczono czas odczytu',
        'HARDWARE_ERROR': 'Błąd sprzętowy czytnika'
    }
}


def calculate_checksum(data: bytes) -> int:
    """
    Berechnet die Checksum für TSHRW380BZMP Kommandos.

    Args:
        data: Kommando-Bytes (ohne Checksum)

    Returns:
        Checksum als Integer
    """
    checksum = 0
    for byte in data[2:]:  # Skip AA BB
        checksum ^= byte
    return checksum


def build_command(cmd_base: bytes, *args) -> bytes:
    """
    Baut ein vollständiges Kommando mit Checksum.

    Args:
        cmd_base: Basis-Kommando
        *args: Zusätzliche Bytes

    Returns:
        Vollständiges Kommando mit Checksum
    """
    # Kommando zusammenbauen
    cmd = bytearray(cmd_base)

    for arg in args:
        if isinstance(arg, int):
            cmd.append(arg)
        elif isinstance(arg, bytes):
            cmd.extend(arg)

    # Länge aktualisieren (falls nötig)
    if len(cmd) > 3:
        cmd[2] = len(cmd) - 3  # Länge ohne Header und Checksum

    # Checksum berechnen und anhängen
    checksum = calculate_checksum(cmd)
    cmd.append(checksum)

    return bytes(cmd)


def parse_tag_id(response: bytes) -> str:
    """
    Extrahiert die Tag-ID aus der Reader-Antwort.

    Args:
        response: Rohdaten vom Reader

    Returns:
        Tag-ID als Hex-String oder None
    """
    if not response or len(response) < 8:
        return None

    # TSHRW380BZMP Format prüfen
    if response[0] == 0xAA and response[1] == 0xBB:
        length = response[2]

        if len(response) >= length + 4:
            # Status prüfen
            status = response[3]
            if status == 0x00:  # Success
                # Tag-ID extrahieren (4 Bytes)
                tag_data = response[4:8]
                tag_id = tag_data.hex().upper()
                return tag_id

    return None


def get_rfid_error_message(error_code: str, language: str = 'de') -> str:
    """
    Gibt lokalisierte Fehlermeldung zurück.

    Args:
        error_code: Fehlercode
        language: Sprachcode

    Returns:
        Fehlermeldung
    """
    messages = RFID_ERROR_MESSAGES.get(language, RFID_ERROR_MESSAGES['de'])
    return messages.get(error_code, f'Unbekannter Fehler: {error_code}')


# Konfiguration für verschiedene Umgebungen
RFID_CONFIG_DEV = {
    **RFID_CONFIG,
    'simulate_mode': True,
    'debug_mode': True,
    'log_raw_data': True
}

RFID_CONFIG_TEST = {
    **RFID_CONFIG,
    'simulate_mode': True,
    'beep_on_scan': False
}

RFID_CONFIG_PROD = {
    **RFID_CONFIG,
    'debug_mode': False,
    'log_raw_data': False,
    'max_retries': 5
}

# Test
if __name__ == "__main__":
    print("=== Shirtful WMS RFID Configuration ===\n")

    # Konfiguration anzeigen
    print("Main Configuration:")
    for key, value in RFID_CONFIG.items():
        if key not in ['debug_mode', 'log_raw_data']:
            print(f"  {key}: {value}")

    print(f"\nReader Model: {RFID_CONFIG['reader_model']}")
    print(f"Frequency: {RFID_CONFIG['frequency']}")
    print(f"Protocol: {RFID_CONFIG['protocol']}")

    # Kommandos testen
    print("\nSample Commands:")
    print(f"  GET_VERSION: {RFID_COMMANDS['GET_VERSION'].hex()}")
    print(f"  READ_TAG: {RFID_COMMANDS['READ_TAG_ONCE'].hex()}")

    # Checksum Test
    test_cmd = bytes.fromhex('AA BB 02 20')
    checksum = calculate_checksum(test_cmd)
    print(f"\nChecksum Test:")
    print(f"  Command: {test_cmd.hex()}")
    print(f"  Checksum: {checksum:02X}")

    # Test-Tags
    print("\nTest Tags:")
    for tag_id, info in TEST_TAGS.items():
        print(f"  {tag_id}: {info['name']} ({info['department']})")