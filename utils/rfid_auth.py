"""
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
