"""
Pytest Konfiguration und gemeinsame Fixtures für Shirtful WMS Tests.
"""

import pytest
import os
import sys
import tempfile
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

# Projekt-Root zum Python-Path hinzufügen
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests import TEST_CONFIG, TEST_DATA


# === Fixtures ===

@pytest.fixture
def mock_db():
    """Mock Database Objekt."""
    db = Mock()

    # Standard-Rückgabewerte
    db.validate_employee_rfid.return_value = {
        'id': 1,
        'name': 'Test User',
        'department': 'Test',
        'role': 'Tester',
        'language': 'de'
    }

    db.get_package_by_qr.return_value = {
        'id': 1,
        'qr_code': 'PKG-TEST-000001',
        'order_id': 'ORD-TEST-0001',
        'customer': 'Test Customer',
        'item_count': 5,
        'status': 'Wareneingang'
    }

    db.clock_in.return_value = True
    db.clock_out.return_value = True
    db.update_package_status.return_value = True
    db.register_package.return_value = 1
    db.get_daily_statistics.return_value = {'count': 10}

    return db


@pytest.fixture
def mock_rfid():
    """Mock RFID Reader."""
    rfid = Mock()

    rfid.is_connected = True
    rfid.read_tag.return_value = TEST_DATA['test_employee']['rfid_tag']
    rfid.connect.return_value = True
    rfid.disconnect.return_value = None
    rfid.beep.return_value = None

    return rfid


@pytest.fixture
def mock_qr_scanner():
    """Mock QR Scanner."""
    scanner = Mock()

    scanner.scan_once.return_value = TEST_DATA['test_package']['qr_code']
    scanner.start_camera.return_value = True
    scanner.stop_camera.return_value = None
    scanner.get_camera_frame.return_value = None

    return scanner


@pytest.fixture
def mock_ui_components():
    """Mock UI Components."""
    ui = Mock()

    ui.play_sound.return_value = None
    ui.create_large_button = Mock(return_value=Mock())
    ui.create_info_card = Mock(return_value=Mock())
    ui.create_notification.return_value = None

    return ui


@pytest.fixture
def temp_config_file():
    """Temporäre Konfigurationsdatei."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        import json
        config = {
            'general': {
                'language': 'de',
                'debug_mode': True
            },
            'database': {
                'server': 'localhost',
                'database': 'ShirtfulWMS_Test'
            },
            'rfid': {
                'port': 'COM99',
                'simulate_mode': True
            }
        }
        json.dump(config, f)
        temp_path = f.name

    yield temp_path

    # Cleanup
    os.unlink(temp_path)


@pytest.fixture
def mock_tkinter():
    """Mock für Tkinter GUI-Komponenten."""
    with patch('tkinter.Tk') as mock_tk:
        root = MagicMock()
        mock_tk.return_value = root

        # Standard-Widgets mocken
        root.title.return_value = None
        root.geometry.return_value = None
        root.configure.return_value = None
        root.mainloop.return_value = None
        root.after.return_value = None
        root.destroy.return_value = None

        yield root


@pytest.fixture
def test_employee_data():
    """Test-Mitarbeiterdaten."""
    return TEST_DATA['test_employee'].copy()


@pytest.fixture
def test_package_data():
    """Test-Paketdaten."""
    return TEST_DATA['test_package'].copy()


@pytest.fixture
def mock_datetime():
    """Mock für datetime mit festem Zeitpunkt."""
    fixed_time = datetime(2024, 5, 1, 10, 30, 0)
    with patch('datetime.datetime') as mock_dt:
        mock_dt.now.return_value = fixed_time
        mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
        yield fixed_time


# === Hilfsfunktionen ===

def create_test_db_connection():
    """Erstellt Test-Datenbankverbindung."""
    if TEST_CONFIG['use_test_db']:
        # Mock-Verbindung für Tests
        return Mock()
    else:
        # Echte Test-DB wenn konfiguriert
        from config.database_config import get_connection_string
        import pyodbc
        conn_str = get_connection_string('test')
        return pyodbc.connect(conn_str)


# === Pytest Konfiguration ===

def pytest_configure(config):
    """Pytest Konfiguration."""
    # Eigene Marker registrieren
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "hardware: marks tests that require hardware"
    )


def pytest_collection_modifyitems(config, items):
    """Test-Items modifizieren."""
    # Hardware-Tests überspringen wenn Mock aktiviert
    if TEST_CONFIG['mock_hardware']:
        skip_hardware = pytest.mark.skip(reason="Hardware mocking enabled")
        for item in items:
            if "hardware" in item.keywords:
                item.add_marker(skip_hardware)


# === Globale Test-Einstellungen ===

# Logging für Tests
import logging

logging.basicConfig(level=logging.DEBUG)

# Warnungen unterdrücken
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

# Umgebungsvariablen für Tests
os.environ['SHIRTFUL_TEST_MODE'] = '1'
os.environ['SHIRTFUL_DB_SERVER'] = 'localhost\\SQLEXPRESS'
os.environ['SHIRTFUL_DB_NAME'] = 'ShirtfulWMS_Test'