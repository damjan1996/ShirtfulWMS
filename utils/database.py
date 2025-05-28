"""
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
