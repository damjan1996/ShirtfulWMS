"""
Patch für utils/rfid_auth.py - HID-RFID Integration
Aktualisiert RFIDAuth für TS-HRW380 HID-Reader
"""

import shutil
from pathlib import Path


def patch_rfid_auth():
    """Patcht RFIDAuth für HID-RFID"""

    print("🔧 RFID-AUTH HID-PATCH")
    print("=" * 40)

    # Original-Datei finden
    auth_file = Path("utils/rfid_auth.py")

    if not auth_file.exists():
        print("❌ utils/rfid_auth.py nicht gefunden!")
        return False

    # Backup erstellen
    backup_file = Path("utils/rfid_auth_original.py")
    shutil.copy2(auth_file, backup_file)
    print(f"✅ Backup erstellt: {backup_file}")

    # Neue HID-basierte RFIDAuth erstellen
    hid_rfid_auth_code = '''"""
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
    """
    RFID-Authentifizierung mit HID-Reader Support
    Verwendet TS-HRW380 HID-RFID Reader
    """

    def __init__(self):
        """Initialisiert RFID-Authentifizierung"""
        self.logger = logging.getLogger(__name__)

        # RFID-Reader
        self.rfid_reader = None
        self.is_connected = False
        self.is_monitoring = False

        # Datenbank
        self.database = None

        # Callbacks
        self.card_callback = None
        self.status_callback = None

        # Threading
        self.monitor_thread = None
        self._stop_monitoring = False

        # Status
        self.last_error = None
        self.connection_attempts = 0
        self.max_reconnect_attempts = 3

        self.logger.info("RFIDAuth (HID) initialisiert")

    def initialize(self) -> bool:
        """
        Initialisiert RFID-System

        Returns:
            True bei erfolgreicher Initialisierung
        """
        try:
            self.logger.info("Initialisiere RFID-System...")

            # Datenbank verbinden
            self.database = Database()
            self.logger.info("✅ Datenbank verbunden")

            # RFID-Reader erstellen
            self.rfid_reader = RFIDReader()

            # Verbindung herstellen
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
        """
        Verbindet mit RFID-Reader

        Returns:
            True bei erfolgreicher Verbindung
        """
        if not self.rfid_reader:
            self.last_error = "RFID-Reader nicht initialisiert"
            return False

        try:
            self.logger.info("Verbinde mit HID-RFID Reader...")

            if self.rfid_reader.connect():
                self.is_connected = True
                self.connection_attempts = 0
                self.logger.info("✅ HID-RFID Reader verbunden")

                # Status-Callback informieren
                if self.status_callback:
                    self.status_callback("connected")

                return True
            else:
                self.is_connected = False
                error = self.rfid_reader.get_last_error()
                self.last_error = f"Verbindung fehlgeschlagen: {error}"
                self.logger.error(self.last_error)

                # Status-Callback informieren
                if self.status_callback:
                    self.status_callback("error")

                return False

        except Exception as e:
            self.is_connected = False
            self.last_error = f"Verbindungsfehler: {e}"
            self.logger.error(self.last_error)

            if self.status_callback:
                self.status_callback("error")

            return False

    def disconnect(self):
        """Trennt RFID-Reader Verbindung"""
        self.logger.info("Trenne RFID-Reader...")

        # Monitoring stoppen
        self.stop_monitoring()

        # Reader trennen
        if self.rfid_reader:
            self.rfid_reader.disconnect()

        self.is_connected = False

        # Status-Callback informieren
        if self.status_callback:
            self.status_callback("disconnected")

        self.logger.info("RFID-Reader getrennt")

    def start_monitoring(self, card_callback: Callable[[str, Dict], None] = None,
                        status_callback: Callable[[str], None] = None):
        """
        Startet RFID-Monitoring

        Args:
            card_callback: Funktion für erkannte Karten (card_id, employee_data)
            status_callback: Funktion für Status-Updates
        """
        if self.is_monitoring:
            self.logger.warning("RFID-Monitoring läuft bereits")
            return

        if not self.is_connected:
            self.logger.error("RFID-Reader nicht verbunden")
            return

        self.card_callback = card_callback
        self.status_callback = status_callback

        # Monitoring-Thread starten
        self._stop_monitoring = False
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()

        self.is_monitoring = True
        self.logger.info("✅ RFID-Monitoring gestartet")

    def stop_monitoring(self):
        """Stoppt RFID-Monitoring"""
        if not self.is_monitoring:
            return

        self.logger.info("Stoppe RFID-Monitoring...")

        self._stop_monitoring = True
        self.is_monitoring = False

        # Thread beenden
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2.0)

        self.logger.info("RFID-Monitoring gestoppt")

    def _monitoring_loop(self):
        """Haupt-Monitoring-Schleife"""
        self.logger.info("RFID-Monitoring-Loop gestartet")

        while not self._stop_monitoring and self.is_connected:
            try:
                # Karte lesen (non-blocking)
                card_id = self.rfid_reader.read_card_async()

                if card_id:
                    self.logger.info(f"🎯 RFID-Karte erkannt: {card_id}")
                    self._handle_card(card_id)

                time.sleep(0.1)  # Kurze Pause

            except Exception as e:
                self.logger.error(f"Monitoring-Fehler: {e}")

                # Reconnect versuchen
                if self.connection_attempts < self.max_reconnect_attempts:
                    self.connection_attempts += 1
                    self.logger.info(f"Reconnect-Versuch {self.connection_attempts}/{self.max_reconnect_attempts}")

                    if self.connect():
                        continue

                # Bei zu vielen Fehlern stoppen
                self.logger.error("Zu viele Verbindungsfehler, stoppe Monitoring")
                break

                time.sleep(1.0)

        self.logger.info("RFID-Monitoring-Loop beendet")

    def _handle_card(self, card_id: str):
        """
        Behandelt erkannte RFID-Karte

        Args:
            card_id: ID der erkannten Karte
        """
        try:
            # Mitarbeiter in Datenbank suchen
            employee = None
            if self.database:
                employee = self.database.get_employee_by_rfid(card_id)

            if employee:
                self.logger.info(f"✅ Mitarbeiter gefunden: {employee.get('first_name')} {employee.get('last_name')}")
            else:
                self.logger.warning(f"⚠️ Unbekannte RFID-Karte: {card_id}")
                # Trotzdem weiterleiten für weitere Verarbeitung
                employee = {
                    'rfid_card': card_id,
                    'first_name': 'Unbekannt',
                    'last_name': 'Benutzer',
                    'role': 'unknown'
                }

            # Callback aufrufen
            if self.card_callback:
                self.card_callback(card_id, employee)

        except Exception as e:
            self.logger.error(f"Fehler beim Verarbeiten der Karte: {e}")

    def read_single_card(self, timeout: float = 5.0) -> Optional[Dict]:
        """
        Liest eine einzelne RFID-Karte (blockierend)

        Args:
            timeout: Timeout in Sekunden

        Returns:
            Mitarbeiter-Daten oder None
        """
        if not self.is_connected:
            self.logger.error("RFID-Reader nicht verbunden")
            return None

        try:
            self.logger.info(f"Warte auf RFID-Karte ({timeout}s)...")

            card_id = self.rfid_reader.read_card(timeout)

            if card_id:
                self.logger.info(f"✅ Karte gelesen: {card_id}")

                # Mitarbeiter suchen
                if self.database:
                    employee = self.database.get_employee_by_rfid(card_id)
                    if employee:
                        return employee

                # Fallback
                return {
                    'rfid_card': card_id,
                    'first_name': 'Unbekannt',
                    'last_name': 'Benutzer',
                    'role': 'worker'
                }
            else:
                self.logger.info("⏱️ Timeout beim Kartenlesen")
                return None

        except Exception as e:
            self.logger.error(f"Fehler beim Kartenlesen: {e}")
            return None

    def is_reader_connected(self) -> bool:
        """
        Prüft RFID-Reader Status

        Returns:
            True wenn verbunden
        """
        if not self.rfid_reader:
            return False

        return self.rfid_reader.is_connected()

    def get_status(self) -> Dict[str, Any]:
        """
        Holt RFID-System Status

        Returns:
            Status-Dictionary
        """
        return {
            'connected': self.is_connected,
            'monitoring': self.is_monitoring,
            'reader_type': 'HID-RFID (TS-HRW380)',
            'connection_attempts': self.connection_attempts,
            'last_error': self.last_error
        }

    def get_last_error(self) -> Optional[str]:
        """
        Holt letzten Fehler

        Returns:
            Fehlermeldung oder None
        """
        return self.last_error

    def test_connection(self) -> bool:
        """
        Testet RFID-Reader Verbindung

        Returns:
            True wenn OK
        """
        try:
            if not self.is_connected:
                return self.connect()

            # Einfacher Status-Check
            return self.rfid_reader.is_connected() if self.rfid_reader else False

        except Exception as e:
            self.logger.error(f"Verbindungstest fehlgeschlagen: {e}")
            return False

    def __del__(self):
        """Destruktor"""
        self.disconnect()


# Kompatibilitätsfunktionen für ältere Versionen
def create_rfid_auth() -> RFIDAuth:
    """
    Factory-Funktion für RFIDAuth

    Returns:
        RFIDAuth Instanz
    """
    return RFIDAuth()
'''

    # Neue Datei schreiben
    with open(auth_file, 'w', encoding='utf-8') as f:
        f.write(hid_rfid_auth_code)

    print("✅ RFIDAuth für HID-RFID aktualisiert")
    return True


def main():
    """Hauptfunktion"""
    print("🔧 RFID-AUTH HID-INTEGRATION")
    print("=" * 50)

    # Patch anwenden
    if patch_rfid_auth():
        print("\n✅ PATCH ERFOLGREICH ANGEWENDET!")
        print("\n🧪 Zum Testen:")
        print("   python test_hid_rfid.py")
        print("\n🚀 WMS starten:")
        print("   .\\run_wareneingang.bat")
        print("\n📋 Was geändert wurde:")
        print("   - RFIDAuth verwendet jetzt HID-RFID Reader")
        print("   - Kompatibel mit TS-HRW380")
        print("   - Backup der Original-Datei erstellt")
    else:
        print("\n❌ PATCH FEHLGESCHLAGEN!")


if __name__ == "__main__":
    main()