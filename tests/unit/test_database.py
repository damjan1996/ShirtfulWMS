"""
Unit-Tests für das Database-Modul

Diese Tests prüfen die Datenbankfunktionalität isoliert,
ohne echte Datenbankverbindungen zu benötigen.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime, timedelta
import pyodbc
import pytest

from utils.database import (
    Database, PackageStatus, EmployeeRole,
    DatabaseError, ConnectionError, ValidationError
)
from . import MockDatabase, MockCursor


class TestDatabase(unittest.TestCase):
    """Tests für die Database-Klasse."""

    def setUp(self):
        """Setup für jeden Test."""
        self.db = None
        self.mock_connection = Mock()
        self.mock_cursor = Mock()

        # Mock pyodbc.connect
        self.connect_patcher = patch('pyodbc.connect')
        self.mock_connect = self.connect_patcher.start()
        self.mock_connect.return_value = self.mock_connection
        self.mock_connection.cursor.return_value = self.mock_cursor

    def tearDown(self):
        """Cleanup nach jedem Test."""
        self.connect_patcher.stop()
        if self.db:
            self.db.close()

    def test_database_connection(self):
        """Test der Datenbankverbindung."""
        # Test erfolgreiche Verbindung
        db = Database()

        self.mock_connect.assert_called_once()
        self.assertIsNotNone(db.connection)
        self.assertTrue(db.is_connected())

    def test_database_connection_failure(self):
        """Test der Fehlerbehandlung bei Verbindungsproblemen."""
        # Simuliere Verbindungsfehler
        self.mock_connect.side_effect = pyodbc.Error("Connection failed")

        with self.assertRaises(ConnectionError):
            Database()

    def test_employee_authentication(self):
        """Test der Mitarbeiter-Authentifizierung."""
        db = Database()

        # Mock erfolgreiche Authentifizierung
        self.mock_cursor.fetchone.return_value = (
            1,  # EmployeeID
            "Max Mustermann",  # Name
            "max@shirtful.de",  # Email
            "de",  # Language
            "worker"  # Role
        )

        result = db.authenticate_employee("1234567890")

        # Verifiziere SQL-Query
        self.mock_cursor.execute.assert_called_once()
        query = self.mock_cursor.execute.call_args[0][0]
        self.assertIn("SELECT", query)
        self.assertIn("FROM Employees", query)
        self.assertIn("WHERE RFIDTag", query)

        # Verifiziere Ergebnis
        self.assertEqual(result['employee_id'], 1)
        self.assertEqual(result['name'], "Max Mustermann")
        self.assertEqual(result['language'], 'de')

    def test_employee_authentication_invalid_rfid(self):
        """Test mit ungültiger RFID-Karte."""
        db = Database()

        # Mock keine Ergebnisse
        self.mock_cursor.fetchone.return_value = None

        result = db.authenticate_employee("INVALID_RFID")

        self.assertIsNone(result)

    def test_register_package(self):
        """Test der Paketregistrierung."""
        db = Database()

        # Mock erfolgreiche Registrierung
        self.mock_cursor.rowcount = 1

        qr_code = "PKG-2024-001"
        employee_id = 1

        result = db.register_package(qr_code, employee_id, PackageStatus.RECEIVED)

        # Verifiziere SQL-Query
        self.mock_cursor.execute.assert_called()
        query = self.mock_cursor.execute.call_args[0][0]
        self.assertIn("INSERT INTO Packages", query)

        # Verifiziere commit wurde aufgerufen
        self.mock_connection.commit.assert_called_once()

        self.assertTrue(result)

    def test_register_duplicate_package(self):
        """Test der Registrierung eines bereits existierenden Pakets."""
        db = Database()

        # Mock Constraint Violation
        self.mock_cursor.execute.side_effect = pyodbc.IntegrityError(
            "Violation of UNIQUE constraint"
        )

        with self.assertRaises(ValidationError) as context:
            db.register_package("PKG-2024-001", 1, PackageStatus.RECEIVED)

        self.assertIn("already exists", str(context.exception))
        self.mock_connection.rollback.assert_called_once()

    def test_update_package_status(self):
        """Test der Paket-Status-Aktualisierung."""
        db = Database()

        # Mock erfolgreiche Aktualisierung
        self.mock_cursor.rowcount = 1

        result = db.update_package_status(
            "PKG-2024-001",
            PackageStatus.IN_PROCESSING,
            1
        )

        # Verifiziere SQL-Query
        self.mock_cursor.execute.assert_called()
        query = self.mock_cursor.execute.call_args[0][0]
        self.assertIn("UPDATE Packages", query)
        self.assertIn("SET CurrentStage", query)

        self.assertTrue(result)

    def test_update_nonexistent_package(self):
        """Test der Aktualisierung eines nicht existierenden Pakets."""
        db = Database()

        # Mock keine betroffenen Zeilen
        self.mock_cursor.rowcount = 0

        result = db.update_package_status(
            "NONEXISTENT",
            PackageStatus.IN_PROCESSING,
            1
        )

        self.assertFalse(result)

    def test_clock_in(self):
        """Test der Zeiterfassung - Einstempeln."""
        db = Database()

        # Mock erfolgreiche Zeiterfassung
        self.mock_cursor.rowcount = 1
        self.mock_cursor.fetchone.return_value = (1,)  # TimeEntryID

        employee_id = 1
        result = db.clock_in(employee_id)

        # Verifiziere SQL-Queries
        calls = self.mock_cursor.execute.call_args_list

        # Erster Call: Check ob bereits eingestempelt
        self.assertIn("SELECT", calls[0][0][0])
        self.assertIn("ClockOut IS NULL", calls[0][0][0])

        # Zweiter Call: Einstempeln
        self.assertIn("INSERT INTO TimeTracking", calls[1][0][0])

        self.assertTrue(result)

    def test_clock_in_already_clocked_in(self):
        """Test Einstempeln wenn bereits eingestempelt."""
        db = Database()

        # Mock bereits eingestempelt
        self.mock_cursor.fetchone.return_value = (1,)  # Existierender Eintrag

        result = db.clock_in(1)

        # Sollte False zurückgeben, kein neuer Eintrag
        self.assertFalse(result)

        # Nur ein execute Call (der Check)
        self.assertEqual(self.mock_cursor.execute.call_count, 1)

    def test_clock_out(self):
        """Test der Zeiterfassung - Ausstempeln."""
        db = Database()

        # Mock erfolgreiches Ausstempeln
        self.mock_cursor.rowcount = 1
        self.mock_cursor.fetchone.return_value = (
            datetime.now() - timedelta(hours=8),  # ClockIn Zeit
        )

        result = db.clock_out(1)

        # Verifiziere SQL-Query
        self.mock_cursor.execute.assert_called()
        query = self.mock_cursor.execute.call_args[0][0]
        self.assertIn("UPDATE TimeTracking", query)
        self.assertIn("SET ClockOut", query)

        self.assertTrue(result)

    def test_automatic_break_calculation(self):
        """Test der automatischen Pausenberechnung."""
        db = Database()

        # Mock Arbeitszeit > 6 Stunden
        clock_in_time = datetime.now() - timedelta(hours=7)
        self.mock_cursor.fetchone.return_value = (clock_in_time,)
        self.mock_cursor.rowcount = 1

        result = db.clock_out(1)

        # Verifiziere, dass Pausenzeit berücksichtigt wurde
        calls = self.mock_cursor.execute.call_args_list
        update_query = calls[-1][0][0]

        # Query sollte BreakMinutes enthalten
        self.assertIn("BreakMinutes", update_query)

        self.assertTrue(result)

    def test_get_package_history(self):
        """Test des Abrufs der Pakethistorie."""
        db = Database()

        # Mock Pakethistorie
        mock_history = [
            ("PKG-2024-001", "RECEIVED", datetime.now(), "Max Mustermann"),
            ("PKG-2024-001", "IN_PROCESSING", datetime.now(), "Anna Schmidt"),
        ]
        self.mock_cursor.fetchall.return_value = mock_history

        history = db.get_package_history("PKG-2024-001")

        # Verifiziere SQL-Query
        self.mock_cursor.execute.assert_called_once()
        query = self.mock_cursor.execute.call_args[0][0]
        self.assertIn("SELECT", query)
        self.assertIn("FROM PackageHistory", query)

        self.assertEqual(len(history), 2)
        self.assertEqual(history[0][0], "PKG-2024-001")

    def test_get_employee_statistics(self):
        """Test des Abrufs von Mitarbeiterstatistiken."""
        db = Database()

        # Mock Statistiken
        mock_stats = {
            'packages_today': 42,
            'average_time': 15.5,
            'total_hours': 160.0
        }
        self.mock_cursor.fetchone.return_value = (42, 15.5, 160.0)

        stats = db.get_employee_statistics(1)

        self.assertEqual(stats['packages_today'], 42)
        self.assertEqual(stats['average_time'], 15.5)

    def test_transaction_rollback(self):
        """Test des Rollbacks bei Fehlern."""
        db = Database()

        # Simuliere Fehler während Transaction
        self.mock_cursor.execute.side_effect = [
            None,  # Erste Query erfolgreich
            pyodbc.Error("Database error")  # Zweite Query fehlerhaft
        ]

        with self.assertRaises(DatabaseError):
            db.complex_operation()

        # Verifiziere Rollback wurde aufgerufen
        self.mock_connection.rollback.assert_called()

    def test_connection_pool(self):
        """Test der Verbindungsverwaltung."""
        # Erstelle mehrere Datenbankinstanzen
        databases = []
        for _ in range(5):
            databases.append(Database())

        # Alle sollten eigene Verbindungen haben
        self.assertEqual(self.mock_connect.call_count, 5)

        # Schließe alle Verbindungen
        for db in databases:
            db.close()

        # Verifiziere alle wurden geschlossen
        self.assertEqual(self.mock_connection.close.call_count, 5)

    def test_sql_injection_prevention(self):
        """Test der SQL-Injection-Prävention."""
        db = Database()

        # Versuche SQL-Injection
        malicious_input = "'; DROP TABLE Employees; --"

        db.authenticate_employee(malicious_input)

        # Verifiziere, dass parametrisierte Queries verwendet werden
        call_args = self.mock_cursor.execute.call_args

        # Query sollte Platzhalter enthalten
        query = call_args[0][0]
        self.assertIn("?", query)

        # Parameter sollten separat übergeben werden
        params = call_args[0][1]
        self.assertEqual(params, (malicious_input,))

    def test_retry_mechanism(self):
        """Test des Retry-Mechanismus bei temporären Fehlern."""
        db = Database()

        # Simuliere temporären Fehler, dann Erfolg
        self.mock_cursor.execute.side_effect = [
            pyodbc.Error("Timeout"),
            pyodbc.Error("Timeout"),
            None  # Dritter Versuch erfolgreich
        ]

        with patch('time.sleep'):  # Mock sleep für schnellere Tests
            result = db.execute_with_retry("SELECT 1")

        # Verifiziere 3 Versuche
        self.assertEqual(self.mock_cursor.execute.call_count, 3)
        self.assertIsNotNone(result)


class TestPackageStatus(unittest.TestCase):
    """Tests für die PackageStatus-Enumeration."""

    def test_status_values(self):
        """Test der Status-Werte."""
        self.assertEqual(PackageStatus.RECEIVED.value, "RECEIVED")
        self.assertEqual(PackageStatus.IN_PROCESSING.value, "IN_PROCESSING")
        self.assertEqual(PackageStatus.IN_COVERING.value, "IN_COVERING")
        self.assertEqual(PackageStatus.QUALITY_CHECK.value, "QUALITY_CHECK")
        self.assertEqual(PackageStatus.READY_TO_SHIP.value, "READY_TO_SHIP")
        self.assertEqual(PackageStatus.SHIPPED.value, "SHIPPED")

    def test_status_transitions(self):
        """Test der erlaubten Status-Übergänge."""
        # Definiere erlaubte Übergänge
        allowed_transitions = {
            PackageStatus.RECEIVED: [PackageStatus.IN_PROCESSING],
            PackageStatus.IN_PROCESSING: [PackageStatus.IN_COVERING],
            PackageStatus.IN_COVERING: [PackageStatus.QUALITY_CHECK],
            PackageStatus.QUALITY_CHECK: [
                PackageStatus.READY_TO_SHIP,
                PackageStatus.IN_PROCESSING  # Bei Nacharbeit
            ],
            PackageStatus.READY_TO_SHIP: [PackageStatus.SHIPPED],
            PackageStatus.SHIPPED: []  # Endstatus
        }

        # Test alle Übergänge
        for current, allowed in allowed_transitions.items():
            for next_status in PackageStatus:
                if next_status in allowed:
                    # Sollte erlaubt sein
                    self.assertTrue(
                        self.is_valid_transition(current, next_status),
                        f"Transition {current} -> {next_status} should be allowed"
                    )
                elif next_status != current:
                    # Sollte nicht erlaubt sein
                    self.assertFalse(
                        self.is_valid_transition(current, next_status),
                        f"Transition {current} -> {next_status} should not be allowed"
                    )

    def is_valid_transition(self, current, next_status):
        """Hilfsmethode zur Überprüfung von Status-Übergängen."""
        # Diese Logik würde normalerweise in der Database-Klasse sein
        transitions = {
            PackageStatus.RECEIVED: [PackageStatus.IN_PROCESSING],
            PackageStatus.IN_PROCESSING: [PackageStatus.IN_COVERING],
            PackageStatus.IN_COVERING: [PackageStatus.QUALITY_CHECK],
            PackageStatus.QUALITY_CHECK: [
                PackageStatus.READY_TO_SHIP,
                PackageStatus.IN_PROCESSING
            ],
            PackageStatus.READY_TO_SHIP: [PackageStatus.SHIPPED],
            PackageStatus.SHIPPED: []
        }
        return next_status in transitions.get(current, [])


if __name__ == '__main__':
    unittest.main()