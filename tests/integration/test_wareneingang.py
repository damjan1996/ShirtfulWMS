"""
Integrationstests für die Wareneingang-Anwendung

Diese Tests prüfen das Zusammenspiel aller Komponenten der Wareneingang-App:
- RFID-Authentifizierung
- QR-Code Scanning
- Datenbankoperationen
- UI-Interaktionen
"""

import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock
import tkinter as tk
from datetime import datetime
import time
import sys
from pathlib import Path

# Füge Projektpfad hinzu
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from apps.wareneingang import WareneingangApp
from utils.rfid_auth import RFIDReader, authenticate_employee
from utils.database import Database, PackageStatus
from utils.qr_scanner import QRScanner
from config.settings import Settings


class TestWareneingangIntegration(unittest.TestCase):
    """Integrationstests für die komplette Wareneingang-Anwendung."""

    @classmethod
    def setUpClass(cls):
        """Einmalige Einrichtung für alle Tests."""
        cls.test_db = Database(test_mode=True)
        cls.test_db.create_test_tables()
        cls.test_db.insert_test_data()

    @classmethod
    def tearDownClass(cls):
        """Aufräumen nach allen Tests."""
        cls.test_db.cleanup_test_data()
        cls.test_db.close()

    def setUp(self):
        """Setup für jeden einzelnen Test."""
        self.app = None
        self.root = None

        # Mock für Hardware-Komponenten
        self.rfid_mock = Mock(spec=RFIDReader)
        self.qr_mock = Mock(spec=QRScanner)

        # Test-Daten
        self.test_employee_rfid = "1234567890"
        self.test_employee_id = 1
        self.test_employee_name = "Max Mustermann"
        self.test_package_qr = "PKG-2024-001"

    def tearDown(self):
        """Cleanup nach jedem Test."""
        if self.root:
            try:
                self.root.quit()
                self.root.destroy()
            except:
                pass
        if self.app:
            self.app = None

    def create_app(self):
        """Erstellt eine neue App-Instanz für Tests."""
        self.root = tk.Tk()
        self.app = WareneingangApp(test_mode=True, root=self.root)
        self.app.rfid_reader = self.rfid_mock
        self.app.qr_scanner = self.qr_mock
        return self.app

    def test_complete_workflow(self):
        """Test des kompletten Workflows von Login bis Paketregistrierung."""
        app = self.create_app()

        # Schritt 1: RFID-Login simulieren
        self.rfid_mock.read_tag.return_value = self.test_employee_rfid

        with patch('utils.rfid_auth.authenticate_employee') as auth_mock:
            auth_mock.return_value = {
                'employee_id': self.test_employee_id,
                'name': self.test_employee_name,
                'language': 'de'
            }

            # Login durchführen
            app.handle_rfid_scan()

            # Verifiziere Login-Status
            self.assertEqual(app.current_user['name'], self.test_employee_name)
            self.assertTrue(app.is_logged_in)
            auth_mock.assert_called_once_with(self.test_employee_rfid)

        # Schritt 2: Hauptbildschirm sollte angezeigt werden
        self.assertEqual(app.current_screen, 'main')

        # Schritt 3: QR-Code Scan simulieren
        self.qr_mock.scan_from_webcam.return_value = self.test_package_qr

        with patch('utils.database.Database.register_package') as register_mock:
            register_mock.return_value = True

            # Paket scannen
            app.scan_package()

            # Verifiziere Paketregistrierung
            register_mock.assert_called_once()
            call_args = register_mock.call_args[0]
            self.assertEqual(call_args[0], self.test_package_qr)
            self.assertEqual(call_args[1], self.test_employee_id)
            self.assertEqual(call_args[2], PackageStatus.RECEIVED)

    def test_rfid_authentication_failure(self):
        """Test der Fehlerbehandlung bei ungültiger RFID-Karte."""
        app = self.create_app()

        # Ungültige RFID-Karte
        self.rfid_mock.read_tag.return_value = "INVALID_RFID"

        with patch('utils.rfid_auth.authenticate_employee') as auth_mock:
            auth_mock.return_value = None

            # Login-Versuch
            app.handle_rfid_scan()

            # Verifiziere, dass Login fehlgeschlagen ist
            self.assertIsNone(app.current_user)
            self.assertFalse(app.is_logged_in)
            self.assertEqual(app.current_screen, 'login')

    def test_duplicate_package_scan(self):
        """Test der Behandlung von bereits registrierten Paketen."""
        app = self.create_app()

        # Erst einloggen
        self.login_test_user(app)

        # Paket-Scan simulieren
        self.qr_mock.scan_from_webcam.return_value = self.test_package_qr

        with patch('utils.database.Database.register_package') as register_mock:
            # Simuliere, dass Paket bereits existiert
            register_mock.side_effect = ValueError("Package already registered")

            # Paket scannen
            app.scan_package()

            # Verifiziere Fehlerbehandlung
            # TODO: Überprüfe, dass Fehlermeldung angezeigt wird

    def test_database_connection_failure(self):
        """Test der Fehlerbehandlung bei Datenbankproblemen."""
        app = self.create_app()

        with patch('utils.database.Database.__init__') as db_mock:
            db_mock.side_effect = Exception("Database connection failed")

            # App sollte trotzdem starten
            self.assertIsNotNone(app)
            # TODO: Verifiziere, dass Offline-Modus aktiviert ist

    def test_automatic_time_tracking(self):
        """Test der automatischen Zeiterfassung beim Login/Logout."""
        app = self.create_app()

        # Login
        with patch('utils.database.Database.clock_in') as clock_in_mock:
            clock_in_mock.return_value = True
            self.login_test_user(app)

            # Verifiziere Clock-In
            clock_in_mock.assert_called_once_with(self.test_employee_id)

        # Logout
        with patch('utils.database.Database.clock_out') as clock_out_mock:
            clock_out_mock.return_value = True
            app.logout()

            # Verifiziere Clock-Out
            clock_out_mock.assert_called_once_with(self.test_employee_id)

    def test_multi_language_support(self):
        """Test der Mehrsprachigkeitsunterstützung."""
        app = self.create_app()

        # Test verschiedene Sprachen
        languages = ['de', 'en', 'tr', 'pl']

        for lang in languages:
            with patch('utils.rfid_auth.authenticate_employee') as auth_mock:
                auth_mock.return_value = {
                    'employee_id': self.test_employee_id,
                    'name': self.test_employee_name,
                    'language': lang
                }

                app.handle_rfid_scan()

                # Verifiziere, dass die richtige Sprache geladen wurde
                self.assertEqual(app.current_language, lang)
                # TODO: Überprüfe UI-Texte

    def test_ui_responsiveness(self):
        """Test der UI-Reaktionsfähigkeit während langer Operationen."""
        app = self.create_app()
        self.login_test_user(app)

        # Simuliere lange Datenbankoperation
        with patch('utils.database.Database.register_package') as register_mock:
            def slow_operation(*args):
                time.sleep(2)  # 2 Sekunden Verzögerung
                return True

            register_mock.side_effect = slow_operation

            # UI sollte nicht einfrieren
            start_time = time.time()
            app.scan_package()
            elapsed_time = time.time() - start_time

            # Operation sollte in einem Thread laufen
            self.assertLess(elapsed_time, 0.5)  # UI-Reaktion sollte schnell sein

    def test_error_recovery(self):
        """Test der Fehlerwiederherstellung nach verschiedenen Fehlern."""
        app = self.create_app()
        self.login_test_user(app)

        # Test 1: RFID-Reader Fehler
        self.rfid_mock.read_tag.side_effect = Exception("RFID Reader disconnected")

        # App sollte weiterlaufen
        try:
            app.handle_rfid_scan()
        except:
            self.fail("App crashed on RFID error")

        # Test 2: QR-Scanner Fehler
        self.qr_mock.scan_from_webcam.side_effect = Exception("Camera not found")

        try:
            app.scan_package()
        except:
            self.fail("App crashed on QR scanner error")

    def test_session_timeout(self):
        """Test des automatischen Logout nach Inaktivität."""
        app = self.create_app()
        app.session_timeout = 1  # 1 Sekunde für Test

        self.login_test_user(app)

        # Warte bis Timeout
        time.sleep(1.5)

        # Trigger Timeout-Check
        app.check_session_timeout()

        # Verifiziere Logout
        self.assertFalse(app.is_logged_in)
        self.assertEqual(app.current_screen, 'login')

    # Hilfsmethoden
    def login_test_user(self, app):
        """Hilfsmethode für Test-Login."""
        self.rfid_mock.read_tag.return_value = self.test_employee_rfid

        with patch('utils.rfid_auth.authenticate_employee') as auth_mock:
            auth_mock.return_value = {
                'employee_id': self.test_employee_id,
                'name': self.test_employee_name,
                'language': 'de'
            }
            app.handle_rfid_scan()


@pytest.mark.integration
class TestWareneingangPerformance:
    """Performance-Tests für die Wareneingang-Anwendung."""

    def test_package_scan_performance(self):
        """Test der Scan-Geschwindigkeit für Pakete."""
        # TODO: Implementiere Performance-Tests
        pass

    def test_concurrent_users(self):
        """Test mit mehreren gleichzeitigen Benutzern."""
        # TODO: Implementiere Concurrent-User-Tests
        pass


if __name__ == '__main__':
    unittest.main()