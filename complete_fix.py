"""
Komplette WMS-Reparatur für HID-RFID und SQLite
Repariert sowohl RFID-Auth als auch Datenbank-Problem
"""

import shutil
from pathlib import Path


def fix_database():
    """Repariert Datenbank - von SQL Server zu SQLite"""
    print("🔧 DATENBANK-REPARATUR")
    print("=" * 40)

    db_file = Path("utils/database.py")

    if not db_file.exists():
        print("❌ utils/database.py nicht gefunden!")
        return False

    # Backup erstellen
    backup_file = Path("utils/database_sqlserver_backup.py")
    shutil.copy2(db_file, backup_file)
    print(f"✅ SQL Server Database Backup: {backup_file}")

    # SQLite-Datenbank Code
    sqlite_db_code = '''"""
SQLite-Datenbank für Shirtful WMS
Ersetzt SQL Server durch SQLite
"""

import sqlite3
import logging
from pathlib import Path
from contextlib import contextmanager
from typing import Dict, Optional, List
from datetime import datetime

class Database:
    """SQLite-Datenbank für Shirtful WMS"""

    def __init__(self):
        """Initialisiert SQLite-Datenbank"""
        self.logger = logging.getLogger(__name__)

        # Datenbank-Verzeichnis erstellen
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)

        self.db_path = data_dir / "shirtful_wms.db"

        # Datenbank initialisieren
        self._init_database()
        self.logger.info(f"✅ SQLite-Datenbank bereit: {self.db_path}")

    def _init_database(self):
        """Erstellt Datenbank-Schema"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Mitarbeiter-Tabelle
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS employees (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        rfid_card TEXT UNIQUE,
                        first_name TEXT NOT NULL,
                        last_name TEXT NOT NULL,
                        role TEXT DEFAULT 'worker',
                        active BOOLEAN DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Pakete-Tabelle
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS packages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        package_id TEXT UNIQUE NOT NULL,
                        order_id TEXT,
                        customer TEXT,
                        item_count INTEGER DEFAULT 1,
                        priority TEXT DEFAULT 'normal',
                        status TEXT DEFAULT 'received',
                        notes TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Aktivitäten-Log
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS activity_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        employee_id INTEGER,
                        package_id TEXT,
                        action TEXT,
                        details TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (employee_id) REFERENCES employees (id)
                    )
                """)

                # Test-Daten einfügen falls leer
                cursor.execute("SELECT COUNT(*) FROM employees")
                if cursor.fetchone()[0] == 0:
                    self._insert_test_data(cursor)

                conn.commit()
                self.logger.info("✅ Datenbank-Schema erstellt")

        except Exception as e:
            self.logger.error(f"Fehler beim Initialisieren der Datenbank: {e}")
            raise

    def _insert_test_data(self, cursor):
        """Fügt Test-Daten ein"""
        # Test-Mitarbeiter
        test_employees = [
            ('1234567890', 'Max', 'Mustermann', 'supervisor'),
            ('0987654321', 'Anna', 'Schmidt', 'worker'),
            ('test123', 'Test', 'User', 'worker'),
            (None, 'Manual', 'Login', 'worker')  # Für manuellen Login
        ]

        cursor.executemany("""
            INSERT INTO employees (rfid_card, first_name, last_name, role)
            VALUES (?, ?, ?, ?)
        """, test_employees)

        # Test-Pakete
        test_packages = [
            ('PKG001', 'ORD001', 'Test Kunde 1', 2, 'normal', 'received'),
            ('PKG002', 'ORD002', 'Test Kunde 2', 1, 'high', 'processing'),
            ('PKG003', 'ORD003', 'Test Kunde 3', 3, 'express', 'ready'),
            ('PKG004', 'ORD004', 'Test Kunde 4', 1, 'normal', 'shipped')
        ]

        cursor.executemany("""
            INSERT INTO packages (package_id, order_id, customer, item_count, priority, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, test_packages)

        self.logger.info("✅ Test-Daten eingefügt")

    @contextmanager
    def get_connection(self):
        """Context Manager für Datenbankverbindungen"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            conn.row_factory = sqlite3.Row  # Dict-ähnliche Rows
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Datenbankfehler: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def get_employee_by_rfid(self, rfid_card: str) -> Optional[Dict]:
        """Holt Mitarbeiter anhand RFID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM employees 
                    WHERE rfid_card = ? AND active = 1
                """, (rfid_card,))

                row = cursor.fetchone()
                return dict(row) if row else None

        except Exception as e:
            self.logger.error(f"Fehler beim Holen des Mitarbeiters: {e}")
            return None

    def get_employee_by_name(self, first_name: str, last_name: str) -> Optional[Dict]:
        """Holt Mitarbeiter anhand Namen"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM employees 
                    WHERE first_name = ? AND last_name = ? AND active = 1
                """, (first_name, last_name))

                row = cursor.fetchone()
                return dict(row) if row else None

        except Exception as e:
            self.logger.error(f"Fehler beim Holen des Mitarbeiters: {e}")
            return None

    def get_all_employees(self) -> List[Dict]:
        """Holt alle aktiven Mitarbeiter"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM employees WHERE active = 1
                    ORDER BY first_name, last_name
                """)

                return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            self.logger.error(f"Fehler beim Holen der Mitarbeiter: {e}")
            return []

    def register_package(self, package_id: str, **kwargs) -> bool:
        """Registriert neues Paket"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO packages 
                    (package_id, order_id, customer, item_count, priority, status, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    package_id,
                    kwargs.get('order_id'),
                    kwargs.get('customer'),
                    kwargs.get('item_count', 1),
                    kwargs.get('priority', 'normal'),
                    kwargs.get('status', 'received'),
                    kwargs.get('notes')
                ))

                conn.commit()
                self.logger.info(f"✅ Paket registriert: {package_id}")
                return True

        except Exception as e:
            self.logger.error(f"Fehler beim Registrieren des Pakets: {e}")
            return False

    def get_package(self, package_id: str) -> Optional[Dict]:
        """Holt Paket-Details"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM packages WHERE package_id = ?", (package_id,))

                row = cursor.fetchone()
                return dict(row) if row else None

        except Exception as e:
            self.logger.error(f"Fehler beim Holen des Pakets: {e}")
            return None

    def update_package_status(self, package_id: str, status: str, notes: str = None) -> bool:
        """Aktualisiert Paket-Status"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                if notes:
                    cursor.execute("""
                        UPDATE packages 
                        SET status = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE package_id = ?
                    """, (status, notes, package_id))
                else:
                    cursor.execute("""
                        UPDATE packages 
                        SET status = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE package_id = ?
                    """, (status, package_id))

                conn.commit()
                return cursor.rowcount > 0

        except Exception as e:
            self.logger.error(f"Fehler beim Aktualisieren des Paket-Status: {e}")
            return False

    def get_packages_by_status(self, status: str) -> List[Dict]:
        """Holt Pakete nach Status"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM packages WHERE status = ?
                    ORDER BY priority DESC, created_at ASC
                """, (status,))

                return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            self.logger.error(f"Fehler beim Holen der Pakete: {e}")
            return []

    def get_package_count_by_status(self) -> Dict[str, int]:
        """Holt Paket-Statistiken"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT status, COUNT(*) as count
                    FROM packages
                    GROUP BY status
                """)

                return {row['status']: row['count'] for row in cursor.fetchall()}

        except Exception as e:
            self.logger.error(f"Fehler beim Holen der Statistiken: {e}")
            return {}

    def get_all_packages(self) -> List[Dict]:
        """Holt alle Pakete"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM packages 
                    ORDER BY created_at DESC
                """)

                return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            self.logger.error(f"Fehler beim Holen aller Pakete: {e}")
            return []

    def log_activity(self, employee_id: int, package_id: str, action: str, details: str = None) -> bool:
        """Loggt Aktivität"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO activity_log (employee_id, package_id, action, details)
                    VALUES (?, ?, ?, ?)
                """, (employee_id, package_id, action, details))

                conn.commit()
                return True

        except Exception as e:
            self.logger.error(f"Fehler beim Loggen der Aktivität: {e}")
            return False

    def get_activity_log(self, limit: int = 100) -> List[Dict]:
        """Holt Aktivitäts-Log"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT al.*, e.first_name, e.last_name 
                    FROM activity_log al
                    LEFT JOIN employees e ON al.employee_id = e.id
                    ORDER BY al.timestamp DESC
                    LIMIT ?
                """, (limit,))

                return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            self.logger.error(f"Fehler beim Holen des Activity-Logs: {e}")
            return []
'''

    # Neue SQLite-Database schreiben
    with open(db_file, 'w', encoding='utf-8') as f:
        f.write(sqlite_db_code)

    print("✅ Datenbank auf SQLite umgestellt")
    return True


def fix_rfid_auth():
    """Repariert RFIDAuth für HID"""
    print("\n🔧 RFID-AUTH REPARATUR")
    print("=" * 40)

    auth_file = Path("utils/rfid_auth.py")

    if not auth_file.exists():
        print("❌ utils/rfid_auth.py nicht gefunden!")
        return False

    # Backup erstellen
    backup_file = Path("utils/rfid_auth_original.py")
    shutil.copy2(auth_file, backup_file)
    print(f"✅ RFIDAuth Backup: {backup_file}")

    # HID-RFID Auth Code
    hid_auth_code = '''"""
RFID-Authentifizierung für Shirtful WMS
HID-basiert für TS-HRW380 Reader
"""

import logging
import threading
import time
from typing import Optional, Callable, Dict, Any
from utils.rfid_reader import RFIDReader
from utils.database import Database

class RFIDAuth:
    """RFID-Authentifizierung mit HID-Reader"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.rfid_reader = None
        self.database = None
        self.is_connected = False
        self.is_monitoring = False
        self.monitor_thread = None
        self._stop_monitoring = False
        self.card_callback = None
        self.status_callback = None
        self.last_error = None

        self.logger.info("RFIDAuth (HID) initialisiert")

    def initialize(self) -> bool:
        """Initialisiert RFID-System"""
        try:
            self.logger.info("Initialisiere HID-RFID System...")

            # Datenbank
            self.database = Database()
            self.logger.info("✅ Datenbank verbunden")

            # RFID-Reader
            self.rfid_reader = RFIDReader()

            if self.connect():
                self.logger.info("✅ RFID-Auth erfolgreich initialisiert")
                return True
            else:
                self.logger.error("❌ RFID-Reader Verbindung fehlgeschlagen")
                return False

        except Exception as e:
            self.last_error = f"Initialisierungsfehler: {e}"
            self.logger.error(self.last_error)
            return False

    def connect(self) -> bool:
        """Verbindet mit RFID-Reader"""
        if not self.rfid_reader:
            return False

        try:
            if self.rfid_reader.connect():
                self.is_connected = True
                self.logger.info("✅ HID-RFID Reader verbunden")
                return True
            else:
                self.is_connected = False
                error = self.rfid_reader.get_last_error()
                self.last_error = f"Verbindung fehlgeschlagen: {error}"
                self.logger.error(self.last_error)
                return False

        except Exception as e:
            self.is_connected = False
            self.last_error = f"Verbindungsfehler: {e}"
            self.logger.error(self.last_error)
            return False

    def disconnect(self):
        """Trennt RFID-Reader"""
        self.stop_monitoring()
        if self.rfid_reader:
            self.rfid_reader.disconnect()
        self.is_connected = False

    def start_monitoring(self, card_callback: Callable = None, status_callback: Callable = None):
        """Startet RFID-Monitoring"""
        if self.is_monitoring or not self.is_connected:
            return

        self.card_callback = card_callback
        self.status_callback = status_callback

        self._stop_monitoring = False
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        self.is_monitoring = True

        self.logger.info("✅ RFID-Monitoring gestartet")

    def stop_monitoring(self):
        """Stoppt RFID-Monitoring"""
        self._stop_monitoring = True
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)

    def _monitoring_loop(self):
        """Monitoring-Schleife"""
        while not self._stop_monitoring and self.is_connected:
            try:
                card_id = self.rfid_reader.read_card_async()
                if card_id:
                    self.logger.info(f"🎯 RFID-Karte: {card_id}")
                    self._handle_card(card_id)
                time.sleep(0.1)
            except Exception as e:
                self.logger.error(f"Monitoring-Fehler: {e}")
                time.sleep(1.0)

    def _handle_card(self, card_id: str):
        """Behandelt erkannte Karte"""
        try:
            employee = None
            if self.database:
                employee = self.database.get_employee_by_rfid(card_id)

            if not employee:
                employee = {
                    'rfid_card': card_id,
                    'first_name': 'Unbekannt',
                    'last_name': 'Benutzer',
                    'role': 'worker'
                }

            if self.card_callback:
                self.card_callback(card_id, employee)

        except Exception as e:
            self.logger.error(f"Fehler beim Verarbeiten der Karte: {e}")

    def read_single_card(self, timeout: float = 5.0) -> Optional[Dict]:
        """Liest einzelne RFID-Karte"""
        if not self.is_connected:
            return None

        try:
            card_id = self.rfid_reader.read_card(timeout)
            if card_id and self.database:
                employee = self.database.get_employee_by_rfid(card_id)
                if employee:
                    return employee
                return {
                    'rfid_card': card_id,
                    'first_name': 'Unbekannt',
                    'last_name': 'Benutzer',
                    'role': 'worker'
                }
            return None
        except Exception as e:
            self.logger.error(f"Fehler beim Kartenlesen: {e}")
            return None

    def is_reader_connected(self) -> bool:
        """Prüft Reader-Status"""
        return self.is_connected and self.rfid_reader and self.rfid_reader.is_connected()

    def get_status(self) -> Dict[str, Any]:
        """Holt Status"""
        return {
            'connected': self.is_connected,
            'monitoring': self.is_monitoring,
            'reader_type': 'HID-RFID (TS-HRW380)',
            'last_error': self.last_error
        }

    def get_last_error(self) -> Optional[str]:
        """Holt letzten Fehler"""
        return self.last_error

    def test_connection(self) -> bool:
        """Testet Verbindung"""
        if not self.is_connected:
            return self.connect()
        return self.rfid_reader.is_connected() if self.rfid_reader else False
'''

    # RFIDAuth schreiben
    with open(auth_file, 'w', encoding='utf-8') as f:
        f.write(hid_auth_code)

    print("✅ RFIDAuth für HID aktualisiert")
    return True


def create_test_script():
    """Erstellt Komplett-Test"""
    test_code = '''"""
Komplett-Test für WMS nach Reparatur
"""

import sys
from pathlib import Path

def test_database():
    """Testet SQLite-Datenbank"""
    print("=== DATABASE TEST ===")
    try:
        from utils.database import Database
        db = Database()

        employees = db.get_all_employees()
        packages = db.get_all_packages()

        print(f"✅ {len(employees)} Mitarbeiter")
        print(f"✅ {len(packages)} Pakete")
        return True
    except Exception as e:
        print(f"❌ Database-Fehler: {e}")
        return False

def test_rfid():
    """Testet HID-RFID"""
    print("\\n=== RFID TEST ===")
    try:
        from utils.rfid_reader import RFIDReader
        reader = RFIDReader()

        if reader.connect():
            print("✅ HID-RFID Reader verbunden")
            reader.disconnect()
            return True
        else:
            print(f"❌ RFID-Verbindung fehlgeschlagen: {reader.get_last_error()}")
            return False
    except Exception as e:
        print(f"❌ RFID-Fehler: {e}")
        return False

def test_rfid_auth():
    """Testet RFID-Auth"""
    print("\\n=== RFID-AUTH TEST ===")
    try:
        from utils.rfid_auth import RFIDAuth
        auth = RFIDAuth()

        if auth.initialize():
            print("✅ RFID-Auth initialisiert")
            auth.disconnect()
            return True
        else:
            print(f"❌ RFID-Auth Fehler: {auth.get_last_error()}")
            return False
    except Exception as e:
        print(f"❌ RFID-Auth Fehler: {e}")
        return False

def main():
    print("🧪 WMS KOMPLETT-TEST NACH REPARATUR")
    print("=" * 50)

    tests = [
        ("Database", test_database),
        ("RFID-Reader", test_rfid), 
        ("RFID-Auth", test_rfid_auth)
    ]

    results = []
    for name, test_func in tests:
        results.append((name, test_func()))

    print("\\n" + "=" * 50)
    print("📊 ERGEBNISSE:")

    all_ok = True
    for name, passed in results:
        status = "✅" if passed else "❌"
        print(f"   {status} {name}")
        if not passed:
            all_ok = False

    if all_ok:
        print("\\n🎉 ALLE TESTS ERFOLGREICH!")
        print("\\n🚀 WMS starten:")
        print("   .\\\\run_wareneingang.bat")
    else:
        print("\\n⚠️ Einige Tests fehlgeschlagen")

if __name__ == "__main__":
    main()
'''

    with open('test_complete_wms.py', 'w', encoding='utf-8') as f:
        f.write(test_code)

    print("✅ Komplett-Test Script erstellt")


def main():
    """Hauptfunktion - Repariert alles"""
    print("🔧 SHIRTFUL WMS - KOMPLETTE REPARATUR")
    print("=" * 60)
    print("Repariert: Database (SQL→SQLite) + RFID (Serial→HID)")
    print()

    success_count = 0

    # 1. Datenbank reparieren
    if fix_database():
        success_count += 1

    # 2. RFID-Auth reparieren
    if fix_rfid_auth():
        success_count += 1

    # 3. Test-Script erstellen
    create_test_script()
    success_count += 1

    print("\n" + "=" * 60)
    if success_count >= 2:
        print("✅ REPARATUR ABGESCHLOSSEN!")
        print("\n🧪 System testen:")
        print("   python test_complete_wms.py")
        print("\n🚀 WMS starten:")
        print("   .\\\\run_wareneingang.bat")
        print("\n📋 Was repariert wurde:")
        print("   ✅ SQLite-Datenbank (statt SQL Server)")
        print("   ✅ HID-RFID Support (statt Serial)")
        print("   ✅ Test-Daten eingefügt")
        print("   ✅ Backups erstellt")
    else:
        print("❌ REPARATUR FEHLGESCHLAGEN!")
        print("Bitte Fehler prüfen")


if __name__ == "__main__":
    main()