"""
Unit Tests Package für Shirtful WMS

Dieses Paket enthält Unit-Tests für einzelne Komponenten
des Systems, isoliert von externen Abhängigkeiten.
"""

from pathlib import Path
import sys

# Füge den Projektpfad zum Python-Pfad hinzu
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Mock-Objekte für häufig verwendete externe Abhängigkeiten
class MockSerial:
    """Mock für serielle Verbindungen (RFID-Reader)."""
    def __init__(self, port=None, baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.is_open = True
        self._read_data = b''
        self._in_waiting = 0

    def read(self, size=1):
        return self._read_data[:size]

    def readline(self):
        return self._read_data

    def write(self, data):
        return len(data)

    def close(self):
        self.is_open = False

    @property
    def in_waiting(self):
        return self._in_waiting

    def set_read_data(self, data):
        """Helper-Methode für Tests."""
        self._read_data = data.encode() if isinstance(data, str) else data
        self._in_waiting = len(self._read_data)


class MockDatabase:
    """Mock für Datenbankverbindungen."""
    def __init__(self):
        self.connected = True
        self._data = {}

    def execute(self, query, params=None):
        return MockCursor()

    def commit(self):
        pass

    def rollback(self):
        pass

    def close(self):
        self.connected = False


class MockCursor:
    """Mock für Datenbank-Cursor."""
    def __init__(self):
        self._results = []
        self._rowcount = 0

    def fetchone(self):
        return self._results[0] if self._results else None

    def fetchall(self):
        return self._results

    @property
    def rowcount(self):
        return self._rowcount

    def set_results(self, results):
        """Helper-Methode für Tests."""
        self._results = results
        self._rowcount = len(results)


# Gemeinsame Test-Fixtures
TEST_RFID_TAG = "1234567890"
TEST_QR_CODE = "PKG-2024-001"
TEST_EMPLOYEE_ID = 1
TEST_EMPLOYEE_NAME = "Test User"

# Export Mock-Klassen und Test-Konstanten
__all__ = [
    'MockSerial', 'MockDatabase', 'MockCursor',
    'TEST_RFID_TAG', 'TEST_QR_CODE', 'TEST_EMPLOYEE_ID', 'TEST_EMPLOYEE_NAME'
]