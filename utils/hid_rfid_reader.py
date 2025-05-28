"""
HID-RFID Adapter für TS-HRW380 Reader
Ersetzt die Serial-basierte RFID-Kommunikation durch HID-Kommunikation
"""

import time
import threading
import logging
from typing import Optional, Callable, Any
import queue

try:
    import hid

    HID_AVAILABLE = True
except ImportError:
    HID_AVAILABLE = False


class HIDRFIDReader:
    """HID-basierter RFID-Reader für TS-HRW380"""

    def __init__(self, vendor_id: int = 0x25DD, product_id: int = 0x3000):
        """
        Initialisiert HID-RFID Reader

        Args:
            vendor_id: Vendor ID des TS-HRW380 (Standard: 0x25DD)
            product_id: Product ID des TS-HRW380 (Standard: 0x3000)
        """
        self.logger = logging.getLogger(__name__)

        self.vendor_id = vendor_id
        self.product_id = product_id
        self.device = None
        self.is_running = False
        self.read_thread = None
        self.card_callback = None
        self.card_queue = queue.Queue()

        # Buffer für Karten-Daten
        self.card_buffer = ""
        self.last_card = ""
        self.last_card_time = 0

        if not HID_AVAILABLE:
            self.logger.error("HID-Bibliothek nicht verfügbar. Installieren Sie: pip install hidapi")
            raise ImportError("hidapi nicht installiert")

    def connect(self) -> bool:
        """
        Verbindet mit dem HID-RFID Reader

        Returns:
            True bei erfolgreicher Verbindung
        """
        try:
            # Alle HID-Geräte auflisten
            devices = hid.enumerate()

            # TS-HRW380 suchen
            target_device = None
            for device_info in devices:
                if (device_info['vendor_id'] == self.vendor_id and
                        device_info['product_id'] == self.product_id):
                    target_device = device_info
                    break

            if not target_device:
                # Alternative Suche nach Beschreibung
                for device_info in devices:
                    if 'TS-HRW' in str(device_info.get('product_string', '')):
                        target_device = device_info
                        self.vendor_id = device_info['vendor_id']
                        self.product_id = device_info['product_id']
                        break

            if not target_device:
                self.logger.error("TS-HRW380 RFID-Reader nicht gefunden")
                self._list_available_devices()
                return False

            # Verbindung herstellen
            self.device = hid.device()
            self.device.open(self.vendor_id, self.product_id)

            # Device-Info
            manufacturer = self.device.get_manufacturer_string()
            product = self.device.get_product_string()

            self.logger.info(f"RFID-Reader verbunden: {manufacturer} {product}")
            self.logger.info(f"VID: 0x{self.vendor_id:04X}, PID: 0x{self.product_id:04X}")

            # Non-blocking Mode
            self.device.set_nonblocking(1)

            return True

        except Exception as e:
            self.logger.error(f"Fehler beim Verbinden mit RFID-Reader: {e}")
            return False

    def _list_available_devices(self):
        """Listet alle verfügbaren HID-Geräte auf"""
        self.logger.info("Verfügbare HID-Geräte:")
        devices = hid.enumerate()

        for device in devices:
            vendor_id = device['vendor_id']
            product_id = device['product_id']
            manufacturer = device.get('manufacturer_string', 'Unknown')
            product_name = device.get('product_string', 'Unknown')

            self.logger.info(f"  VID: 0x{vendor_id:04X}, PID: 0x{product_id:04X} - {manufacturer} {product_name}")

    def start_reading(self, callback: Callable[[str], None] = None):
        """
        Startet das kontinuierliche Lesen von RFID-Karten

        Args:
            callback: Funktion die bei erkannter Karte aufgerufen wird
        """
        if not self.device:
            self.logger.error("Keine Verbindung zum RFID-Reader")
            return False

        self.card_callback = callback
        self.is_running = True

        self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
        self.read_thread.start()

        self.logger.info("RFID-Reader gestartet")
        return True

    def stop_reading(self):
        """Stoppt das Lesen von RFID-Karten"""
        self.is_running = False

        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join(timeout=2.0)

        self.logger.info("RFID-Reader gestoppt")

    def _read_loop(self):
        """Haupt-Lese-Schleife"""
        while self.is_running:
            try:
                # Daten vom HID-Device lesen
                data = self.device.read(64, timeout_ms=100)

                if data:
                    self._process_hid_data(data)

                time.sleep(0.01)  # Kurze Pause

            except Exception as e:
                if self.is_running:  # Nur loggen wenn noch aktiv
                    self.logger.error(f"Fehler beim Lesen: {e}")
                time.sleep(0.1)

    def _process_hid_data(self, data: list):
        """
        Verarbeitet HID-Daten vom RFID-Reader

        Args:
            data: Byte-Array mit HID-Daten
        """
        try:
            # Filtern von Null-Bytes
            filtered_data = [b for b in data if b != 0]

            if not filtered_data:
                return

            # In String konvertieren
            text = ''.join(chr(b) for b in filtered_data if 32 <= b <= 126)

            if not text:
                return

            # Zum Buffer hinzufügen
            self.card_buffer += text

            # Nach Zeilenendezeichen suchen (Enter/Return)
            if '\r' in self.card_buffer or '\n' in self.card_buffer:
                # Karten-ID extrahieren
                card_id = self.card_buffer.strip('\r\n\x00')

                if card_id and len(card_id) >= 8:  # Mindestlänge für RFID
                    self._handle_card_read(card_id)

                # Buffer zurücksetzen
                self.card_buffer = ""

        except Exception as e:
            self.logger.error(f"Fehler beim Verarbeiten der HID-Daten: {e}")

    def _handle_card_read(self, card_id: str):
        """
        Behandelt erkannte RFID-Karte

        Args:
            card_id: ID der erkannten Karte
        """
        current_time = time.time()

        # Duplikate innerhalb 2 Sekunden ignorieren
        if (card_id == self.last_card and
                current_time - self.last_card_time < 2.0):
            return

        self.last_card = card_id
        self.last_card_time = current_time

        self.logger.info(f"RFID-Karte erkannt: {card_id}")

        # In Queue einreihen
        try:
            self.card_queue.put_nowait(card_id)
        except queue.Full:
            self.logger.warning("RFID-Queue voll")

        # Callback aufrufen
        if self.card_callback:
            try:
                self.card_callback(card_id)
            except Exception as e:
                self.logger.error(f"Fehler im RFID-Callback: {e}")

    def get_card(self, timeout: float = None) -> Optional[str]:
        """
        Holt nächste RFID-Karte aus der Queue

        Args:
            timeout: Timeout in Sekunden (None = blockierend)

        Returns:
            RFID-Karten-ID oder None
        """
        try:
            if timeout is None:
                return self.card_queue.get_nowait()
            else:
                return self.card_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def disconnect(self):
        """Trennt Verbindung zum RFID-Reader"""
        self.stop_reading()

        if self.device:
            try:
                self.device.close()
                self.logger.info("RFID-Reader getrennt")
            except Exception as e:
                self.logger.error(f"Fehler beim Trennen: {e}")
            finally:
                self.device = None

    def __del__(self):
        """Destruktor"""
        self.disconnect()


# Kompatibilitäts-Wrapper für das bestehende WMS
class RFIDReader:
    """Kompatibilitäts-Wrapper für bestehende RFID-Implementierung"""

    def __init__(self, port: str = None, baudrate: int = 9600):
        """
        Initialisiert RFID-Reader (HID-basiert)

        Args:
            port: Ignoriert (Kompatibilität)
            baudrate: Ignoriert (Kompatibilität)
        """
        self.logger = logging.getLogger(__name__)
        self.hid_reader = None
        self.is_connected = False
        self._last_error = None

        # HID-Reader erstellen
        try:
            self.hid_reader = HIDRFIDReader()
        except ImportError as e:
            self._last_error = str(e)
            self.logger.error(f"HID-RFID Reader konnte nicht initialisiert werden: {e}")

    def connect(self) -> bool:
        """
        Verbindet mit RFID-Reader

        Returns:
            True bei Erfolg
        """
        if not self.hid_reader:
            return False

        self.is_connected = self.hid_reader.connect()

        if self.is_connected:
            self.hid_reader.start_reading()
            self.logger.info("HID-RFID Reader erfolgreich verbunden")

        return self.is_connected

    def read_card(self, timeout: float = 1.0) -> Optional[str]:
        """
        Liest RFID-Karte

        Args:
            timeout: Timeout in Sekunden

        Returns:
            RFID-Karten-ID oder None
        """
        if not self.is_connected or not self.hid_reader:
            return None

        return self.hid_reader.get_card(timeout)

    def disconnect(self):
        """Trennt Verbindung"""
        if self.hid_reader:
            self.hid_reader.disconnect()

        self.is_connected = False
        self.logger.info("RFID-Reader getrennt")

    def is_connected_status(self) -> bool:
        """
        Prüft Verbindungsstatus

        Returns:
            True wenn verbunden
        """
        return self.is_connected

    def get_last_error(self) -> Optional[str]:
        """
        Holt letzten Fehler

        Returns:
            Fehlermeldung oder None
        """
        return self._last_error


# Test-Funktion
def test_hid_rfid():
    """Testet HID-RFID Reader"""
    print("=== HID-RFID READER TEST ===")

    # Test HID-Library
    if not HID_AVAILABLE:
        print("❌ HID-Library nicht verfügbar")
        print("   Installieren Sie: pip install hidapi")
        return False

    print("✅ HID-Library verfügbar")

    # Reader erstellen
    try:
        reader = HIDRFIDReader()
        print("✅ HID-RFID Reader erstellt")
    except Exception as e:
        print(f"❌ Fehler beim Erstellen: {e}")
        return False

    # Verbinden
    if reader.connect():
        print("✅ Verbindung erfolgreich")

        # Lesen starten
        def card_callback(card_id):
            print(f"🎯 Karte erkannt: {card_id}")

        reader.start_reading(card_callback)

        print("👋 Halten Sie eine RFID-Karte an den Reader...")
        print("   (10 Sekunden Test, dann Ctrl+C zum Beenden)")

        try:
            time.sleep(10)
        except KeyboardInterrupt:
            print("\n⏹️ Test gestoppt")

        reader.disconnect()
        print("✅ Test abgeschlossen")
        return True
    else:
        print("❌ Verbindung fehlgeschlagen")
        return False


if __name__ == "__main__":
    test_hid_rfid()