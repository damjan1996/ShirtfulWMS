"""
Datenbank-Modul für Shirtful WMS
Verwaltet alle Datenbankoperationen mit MSSQL Server.
"""

import pyodbc
import logging
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
import json
from contextlib import contextmanager
from config.database_config import DB_CONFIG


class Database:
    """Datenbank-Klasse für alle WMS-Operationen."""

    def __init__(self):
        """Initialisiert die Datenbankverbindung."""
        self.logger = logging.getLogger(__name__)
        self.connection_string = self._build_connection_string()
        self._test_connection()

    def _build_connection_string(self) -> str:
        """Erstellt den Connection String für MSSQL."""
        config = DB_CONFIG

        if config.get('trusted_connection', True):
            return (
                f"DRIVER={{SQL Server}};"
                f"SERVER={config['server']};"
                f"DATABASE={config['database']};"
                f"Trusted_Connection=yes;"
            )
        else:
            return (
                f"DRIVER={{SQL Server}};"
                f"SERVER={config['server']};"
                f"DATABASE={config['database']};"
                f"UID={config['username']};"
                f"PWD={config['password']};"
            )

    def _test_connection(self):
        """Testet die Datenbankverbindung."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                self.logger.info("Datenbankverbindung erfolgreich")
        except Exception as e:
            self.logger.error(f"Datenbankverbindung fehlgeschlagen: {e}")
            raise

    @contextmanager
    def get_connection(self):
        """Context Manager für Datenbankverbindungen."""
        conn = None
        try:
            conn = pyodbc.connect(self.connection_string)
            yield conn
        finally:
            if conn:
                conn.close()

    # === Mitarbeiter-Funktionen ===

    def validate_employee_rfid(self, rfid_tag: str) -> Optional[Dict[str, Any]]:
        """
        Validiert einen Mitarbeiter anhand seiner RFID-Karte.

        Args:
            rfid_tag: RFID-Tag-ID

        Returns:
            Mitarbeiterdaten oder None
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                               SELECT EmployeeID as id,
                                      Name       as name,
                                      Department as department, Language as language, IsActive as is_active
                               FROM Employees
                               WHERE RFIDTag = ? AND IsActive = 1
                               """, rfid_tag)

                row = cursor.fetchone()
                if row:
                    return {
                        'id': row.id,
                        'name': row.name,
                        'department': row.department,
                        'language': row.language or 'de',
                        'is_active': row.is_active
                    }

        except Exception as e:
            self.logger.error(f"Fehler bei RFID-Validierung: {e}")

        return None

    def clock_in(self, employee_id: int) -> bool:
        """
        Stempelt einen Mitarbeiter ein.

        Args:
            employee_id: Mitarbeiter-ID

        Returns:
            True bei Erfolg
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Prüfen ob bereits eingestempelt
                cursor.execute("""
                               SELECT TOP 1 EntryID
                               FROM TimeTracking
                               WHERE EmployeeID = ?
                                 AND CAST(ClockIn AS DATE) = CAST(GETDATE() AS DATE)
                                 AND ClockOut IS NULL
                               ORDER BY ClockIn DESC
                               """, employee_id)

                if cursor.fetchone():
                    self.logger.info(f"Mitarbeiter {employee_id} bereits eingestempelt")
                    return True

                # Einstempeln
                cursor.execute("""
                               INSERT INTO TimeTracking (EmployeeID, ClockIn)
                               VALUES (?, GETDATE())
                               """, employee_id)

                conn.commit()
                self.logger.info(f"Mitarbeiter {employee_id} eingestempelt")
                return True

        except Exception as e:
            self.logger.error(f"Fehler beim Einstempeln: {e}")
            return False

    def clock_out(self, employee_id: int) -> bool:
        """
        Stempelt einen Mitarbeiter aus.

        Args:
            employee_id: Mitarbeiter-ID

        Returns:
            True bei Erfolg
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Letzte offene Stempelung finden
                cursor.execute("""
                               UPDATE TimeTracking
                               SET ClockOut = GETDATE()
                               WHERE EmployeeID = ?
                                 AND CAST(ClockIn AS DATE) = CAST(GETDATE() AS DATE)
                                 AND ClockOut IS NULL
                               """, employee_id)

                conn.commit()
                self.logger.info(f"Mitarbeiter {employee_id} ausgestempelt")
                return True

        except Exception as e:
            self.logger.error(f"Fehler beim Ausstempeln: {e}")
            return False

    # === Paket-Funktionen ===

    def get_package_by_qr(self, qr_code: str) -> Optional[Dict[str, Any]]:
        """
        Holt Paketinformationen anhand des QR-Codes.

        Args:
            qr_code: QR-Code des Pakets

        Returns:
            Paketdaten oder None
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                               SELECT p.PackageID    as id,
                                      p.QRCode       as qr_code,
                                      p.OrderID      as order_id,
                                      p.CustomerName as customer,
                                      p.ItemCount    as item_count,
                                      p.CurrentStage as status,
                                      p.Priority     as priority,
                                      p.LastUpdate   as last_update,
                                      p.Notes        as notes
                               FROM Packages p
                               WHERE p.QRCode = ?
                               """, qr_code)

                row = cursor.fetchone()
                if row:
                    return {
                        'id': row.id,
                        'qr_code': row.qr_code,
                        'order_id': row.order_id,
                        'customer': row.customer,
                        'item_count': row.item_count,
                        'status': row.status,
                        'priority': row.priority,
                        'last_update': row.last_update,
                        'notes': row.notes
                    }

        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen des Pakets: {e}")

        return None

    def register_package(self, qr_code: str, order_id: str, customer: str,
                         item_count: int, priority: str, delivery_id: int,
                         employee_id: int, notes: str = "") -> Optional[int]:
        """
        Registriert ein neues Paket im System.

        Returns:
            Package ID oder None bei Fehler
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute("""
                               INSERT INTO Packages (QRCode, OrderID, CustomerName, ItemCount,
                                                     Priority, CurrentStage, DeliveryID,
                                                     CreatedBy, CreatedAt, LastUpdate, Notes)
                               VALUES (?, ?, ?, ?, ?, 'Wareneingang', ?, ?, GETDATE(), GETDATE(), ?)
                               """, qr_code, order_id, customer, item_count, priority,
                               delivery_id, employee_id, notes)

                # ID des neuen Eintrags
                cursor.execute("SELECT @@IDENTITY")
                package_id = cursor.fetchone()[0]

                # Historie eintragen
                cursor.execute("""
                               INSERT INTO PackageHistory (PackageID, Stage, EmployeeID, Timestamp, Notes)
                               VALUES (?, 'Wareneingang', ?, GETDATE(), 'Paket registriert')
                               """, package_id, employee_id)

                conn.commit()
                self.logger.info(f"Paket {qr_code} registriert")
                return package_id

        except Exception as e:
            self.logger.error(f"Fehler beim Registrieren des Pakets: {e}")
            return None

    def update_package_status(self, package_id: int, new_status: str,
                              employee_id: int, notes: Any = None) -> bool:
        """
        Aktualisiert den Status eines Pakets.

        Args:
            package_id: Paket-ID
            new_status: Neuer Status
            employee_id: Bearbeiter-ID
            notes: Zusätzliche Notizen (String oder Dict)

        Returns:
            True bei Erfolg
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Status aktualisieren
                cursor.execute("""
                               UPDATE Packages
                               SET CurrentStage  = ?,
                                   LastUpdate    = GETDATE(),
                                   LastUpdatedBy = ?
                               WHERE PackageID = ?
                               """, new_status, employee_id, package_id)

                # Historie eintragen
                notes_str = notes if isinstance(notes, str) else json.dumps(notes)

                cursor.execute("""
                               INSERT INTO PackageHistory (PackageID, Stage, EmployeeID, Timestamp, Notes)
                               VALUES (?, ?, ?, GETDATE(), ?)
                               """, package_id, new_status, employee_id, notes_str)

                conn.commit()
                self.logger.info(f"Paket {package_id} Status auf '{new_status}' aktualisiert")
                return True

        except Exception as e:
            self.logger.error(f"Fehler beim Status-Update: {e}")
            return False

    def update_package_quality_status(self, package_id: int, status: str,
                                      employee_id: int, error_details: Dict = None) -> bool:
        """
        Aktualisiert den Qualitätsstatus eines Pakets.

        Args:
            package_id: Paket-ID
            status: 'OK' oder 'Nacharbeit'
            employee_id: Prüfer-ID
            error_details: Fehlerdetails bei Nacharbeit

        Returns:
            True bei Erfolg
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Status setzen
                new_stage = 'Qualität OK' if status == 'OK' else 'Nacharbeit erforderlich'

                cursor.execute("""
                               UPDATE Packages
                               SET CurrentStage     = ?,
                                   QualityStatus    = ?,
                                   QualityCheckedBy = ?,
                                   QualityCheckDate = GETDATE(),
                                   LastUpdate       = GETDATE(),
                                   LastUpdatedBy    = ?
                               WHERE PackageID = ?
                               """, new_stage, status, employee_id, employee_id, package_id)

                # Bei Nacharbeit: Fehler speichern
                if status == 'Nacharbeit' and error_details:
                    cursor.execute("""
                                   INSERT INTO QualityIssues (PackageID, IssueType, Description,
                                                              ReportedBy, ReportedAt)
                                   VALUES (?, ?, ?, ?, GETDATE())
                                   """, package_id,
                                   ','.join(error_details.get('errors', [])),
                                   error_details.get('notes', ''),
                                   employee_id)

                # Historie
                notes = f"Qualitätsprüfung: {status}"
                if error_details:
                    notes += f" - Fehler: {', '.join(error_details.get('errors', []))}"

                cursor.execute("""
                               INSERT INTO PackageHistory (PackageID, Stage, EmployeeID, Timestamp, Notes)
                               VALUES (?, ?, ?, GETDATE(), ?)
                               """, package_id, new_stage, employee_id, notes)

                conn.commit()
                return True

        except Exception as e:
            self.logger.error(f"Fehler beim Qualitäts-Update: {e}")
            return False

    def mark_package_shipped(self, package_id: int, employee_id: int,
                             shipping_method: str, tracking_number: str = "") -> bool:
        """
        Markiert ein Paket als versendet.

        Args:
            package_id: Paket-ID
            employee_id: Bearbeiter-ID
            shipping_method: Versandart
            tracking_number: Tracking-Nummer (optional)

        Returns:
            True bei Erfolg
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Status aktualisieren
                cursor.execute("""
                               UPDATE Packages
                               SET CurrentStage   = 'Versendet',
                                   ShippingMethod = ?,
                                   TrackingNumber = ?,
                                   ShippedBy      = ?,
                                   ShippedAt      = GETDATE(),
                                   LastUpdate     = GETDATE(),
                                   LastUpdatedBy  = ?
                               WHERE PackageID = ?
                               """, shipping_method, tracking_number, employee_id,
                               employee_id, package_id)

                # Historie
                notes = f"Versendet via {shipping_method}"
                if tracking_number:
                    notes += f" - Tracking: {tracking_number}"

                cursor.execute("""
                               INSERT INTO PackageHistory (PackageID, Stage, EmployeeID, Timestamp, Notes)
                               VALUES (?, 'Versendet', ?, GETDATE(), ?)
                               """, package_id, employee_id, notes)

                conn.commit()
                return True

        except Exception as e:
            self.logger.error(f"Fehler beim Versand-Update: {e}")
            return False

    # === Lieferungs-Funktionen ===

    def create_delivery(self, supplier: str, employee_id: int,
                        delivery_note: str = "", expected_packages: int = 0,
                        notes: str = "") -> Optional[int]:
        """
        Erstellt eine neue Lieferung.

        Returns:
            Delivery ID oder None bei Fehler
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute("""
                               INSERT INTO Deliveries (Supplier, DeliveryNote, ExpectedPackages,
                                                       ReceivedBy, ReceivedAt, Status, Notes)
                               VALUES (?, ?, ?, ?, GETDATE(), 'Offen', ?)
                               """, supplier, delivery_note, expected_packages,
                               employee_id, notes)

                cursor.execute("SELECT @@IDENTITY")
                delivery_id = cursor.fetchone()[0]

                conn.commit()
                self.logger.info(f"Lieferung {delivery_id} von {supplier} erstellt")
                return delivery_id

        except Exception as e:
            self.logger.error(f"Fehler beim Erstellen der Lieferung: {e}")
            return None

    def finish_delivery(self, delivery_id: int) -> bool:
        """
        Schließt eine Lieferung ab.

        Args:
            delivery_id: Lieferungs-ID

        Returns:
            True bei Erfolg
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Anzahl empfangener Pakete zählen
                cursor.execute("""
                               SELECT COUNT(*) as count
                               FROM Packages
                               WHERE DeliveryID = ?
                               """, delivery_id)

                received_count = cursor.fetchone().count

                # Lieferung abschließen
                cursor.execute("""
                               UPDATE Deliveries
                               SET Status           = 'Abgeschlossen',
                                   ReceivedPackages = ?,
                                   CompletedAt      = GETDATE()
                               WHERE DeliveryID = ?
                               """, received_count, delivery_id)

                conn.commit()
                self.logger.info(f"Lieferung {delivery_id} abgeschlossen")
                return True

        except Exception as e:
            self.logger.error(f"Fehler beim Abschließen der Lieferung: {e}")
            return False

    # === Statistik-Funktionen ===

    def get_daily_statistics(self, employee_id: int, stage: str) -> Dict[str, int]:
        """
        Holt Tagesstatistiken für einen Mitarbeiter und eine Station.

        Args:
            employee_id: Mitarbeiter-ID
            stage: Station (z.B. 'Veredelung')

        Returns:
            Dictionary mit Statistiken
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute("""
                               SELECT COUNT(DISTINCT PackageID) as count
                               FROM PackageHistory
                               WHERE EmployeeID = ?
                                 AND Stage LIKE ?
                                 AND CAST (Timestamp AS DATE) = CAST (GETDATE() AS DATE)
                               """, employee_id, f'%{stage}%')

                row = cursor.fetchone()
                return {'count': row.count if row else 0}

        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen der Statistiken: {e}")
            return {'count': 0}

    def get_quality_statistics(self, employee_id: int) -> Dict[str, int]:
        """
        Holt Qualitätsstatistiken für einen Mitarbeiter.

        Args:
            employee_id: Mitarbeiter-ID

        Returns:
            Dictionary mit OK und Nacharbeit Counts
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # OK-Pakete
                cursor.execute("""
                               SELECT COUNT(*) as count
                               FROM Packages
                               WHERE QualityCheckedBy = ?
                                 AND QualityStatus = 'OK'
                                 AND CAST (QualityCheckDate AS DATE) = CAST (GETDATE() AS DATE)
                               """, employee_id)

                ok_count = cursor.fetchone().count

                # Nacharbeit-Pakete
                cursor.execute("""
                               SELECT COUNT(*) as count
                               FROM Packages
                               WHERE QualityCheckedBy = ?
                                 AND QualityStatus = 'Nacharbeit'
                                 AND CAST (QualityCheckDate AS DATE) = CAST (GETDATE() AS DATE)
                               """, employee_id)

                rework_count = cursor.fetchone().count

                return {
                    'ok_count': ok_count,
                    'rework_count': rework_count
                }

        except Exception as e:
            self.logger.error(f"Fehler bei Qualitätsstatistiken: {e}")
            return {'ok_count': 0, 'rework_count': 0}

    def get_shipping_statistics(self, period: str, employee_id: int = None) -> Dict[str, int]:
        """
        Holt Versandstatistiken.

        Args:
            period: 'daily' oder 'weekly'
            employee_id: Optional für mitarbeiterspezifische Stats

        Returns:
            Dictionary mit Versandstatistiken
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Zeitraum bestimmen
                if period == 'daily':
                    date_condition = "CAST(ShippedAt AS DATE) = CAST(GETDATE() AS DATE)"
                else:  # weekly
                    date_condition = "ShippedAt >= DATEADD(day, -7, GETDATE())"

                # Query bauen
                query = f"""
                    SELECT COUNT(*) as count
                    FROM Packages
                    WHERE {date_condition}
                    AND CurrentStage = 'Versendet'
                """

                params = []
                if employee_id:
                    query += " AND ShippedBy = ?"
                    params.append(employee_id)

                cursor.execute(query, *params)
                row = cursor.fetchone()

                return {'count': row.count if row else 0}

        except Exception as e:
            self.logger.error(f"Fehler bei Versandstatistiken: {e}")
            return {'count': 0}

    def get_receiving_statistics(self, employee_id: int) -> Dict[str, int]:
        """
        Holt Wareneingangsstatistiken.

        Args:
            employee_id: Mitarbeiter-ID

        Returns:
            Dictionary mit Lieferungen und Paketen
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Lieferungen heute
                cursor.execute("""
                               SELECT COUNT(*) as count
                               FROM Deliveries
                               WHERE ReceivedBy = ?
                                 AND CAST (ReceivedAt AS DATE) = CAST (GETDATE() AS DATE)
                               """, employee_id)

                deliveries = cursor.fetchone().count

                # Pakete heute
                cursor.execute("""
                               SELECT COUNT(*) as count
                               FROM Packages p
                                   JOIN Deliveries d
                               ON p.DeliveryID = d.DeliveryID
                               WHERE p.CreatedBy = ?
                                 AND CAST (p.CreatedAt AS DATE) = CAST (GETDATE() AS DATE)
                               """, employee_id)

                packages = cursor.fetchone().count

                return {
                    'deliveries': deliveries,
                    'packages': packages
                }

        except Exception as e:
            self.logger.error(f"Fehler bei Eingangsstatistiken: {e}")
            return {'deliveries': 0, 'packages': 0}

    # === Listen-Funktionen ===

    def get_recent_packages(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Holt die letzten eingegangenen Pakete.

        Args:
            limit: Maximale Anzahl

        Returns:
            Liste von Paketdaten
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute("""
                               SELECT TOP(?) p.QRCode as qr_code, p.CustomerName as customer,
                                      p.CreatedAt as timestamp,
                        e.Name as received_by
                               FROM Packages p
                                   JOIN Employees e
                               ON p.CreatedBy = e.EmployeeID
                               WHERE CAST (p.CreatedAt AS DATE) = CAST (GETDATE() AS DATE)
                               ORDER BY p.CreatedAt DESC
                               """, limit)

                packages = []
                for row in cursor.fetchall():
                    packages.append({
                        'qr_code': row.qr_code,
                        'customer': row.customer,
                        'timestamp': row.timestamp,
                        'received_by': row.received_by
                    })

                return packages

        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen der letzten Pakete: {e}")
            return []

    def get_current_processing_orders(self) -> List[Dict[str, Any]]:
        """
        Holt aktuell in Veredelung befindliche Aufträge.

        Returns:
            Liste von Aufträgen
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute("""
                               SELECT p.QRCode     as qr_code,
                                      ph.Notes     as processing_info,
                                      ph.Timestamp as start_time
                               FROM Packages p
                                        JOIN (SELECT PackageID, MAX(Timestamp) as Timestamp, Notes
                                              FROM PackageHistory
                                              WHERE Stage = 'In Veredelung'
                                              GROUP BY PackageID, Notes) ph ON p.PackageID = ph.PackageID
                               WHERE p.CurrentStage = 'In Veredelung'
                               ORDER BY ph.Timestamp DESC
                               """)

                orders = []
                for row in cursor.fetchall():
                    try:
                        info = json.loads(row.processing_info) if row.processing_info else {}
                    except:
                        info = {}

                    orders.append({
                        'qr_code': row.qr_code,
                        'processing_type': info.get('type', 'Unbekannt'),
                        'duration': info.get('estimated_duration', 0),
                        'start_time': row.start_time.strftime('%H:%M')
                    })

                return orders

        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen der Veredelungsaufträge: {e}")
            return []


# Test-Funktionen für Entwicklung
if __name__ == "__main__":
    # Logger konfigurieren
    logging.basicConfig(level=logging.DEBUG)

    # Datenbank testen
    db = Database()

    # RFID-Validierung testen
    employee = db.validate_employee_rfid("12345678")
    if employee:
        print(f"Mitarbeiter gefunden: {employee}")

        # Ein-/Ausstempeln testen
        db.clock_in(employee['id'])
        print("Eingestempelt")

        # Statistiken abrufen
        stats = db.get_daily_statistics(employee['id'], 'Wareneingang')
        print(f"Tagesstatistik: {stats}")