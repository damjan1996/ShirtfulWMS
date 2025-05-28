"""
HID-basierter RFID-Reader für Shirtful WMS
Kompatibel mit TS-HRW380 und anderen HID-RFID Readern
"""

import time
import threading
import logging
from typing import Optional, Callable
import queue

try:
    import hid
    HID_AVAILABLE = True
except ImportError:
    HID_AVAILABLE = False
    print("⚠️ HID-Library nicht verfügbar. Installieren: pip install hidapi")

class RFIDReader:
    """HID-basierter RFID-Reader für TS-HRW380"""

    def __init__(self, port: str = None, baudrate: int = 9600):
        """
        Initialisiert RFID-Reader

        Args:
            port: Ignoriert (Kompatibilität mit Serial-Version)
            baudrate: Ignoriert (Kompatibilität)
        """
        self.logger = logging.getLogger(__name__)

        # HID-Device Parameter (TS-HRW380)
        self.vendor_id = 0x25DD  # Standard für TS-HRW380
        self.product_id = 0x3000

        self.device = None
        self.is_running = False
        self.read_thread = None
        self.card_queue = queue.Queue(maxsize=10)

        # Karten-Buffer
        self.card_buffer = ""
        self.last_card = ""
        self.last_card_time = 0

        self._connected = False
        self._last_error = None

        if not HID_AVAILABLE:
            self._last_error = "HID-Library nicht verfügbar"
            self.logger.error("HID-Library fehlt. Installieren Sie: pip install hidapi")

    def connect(self) -> bool:
        """
        Verbindet mit HID-RFID Reader

        Returns:
            True bei erfolgreicher Verbindung
        """
        if not HID_AVAILABLE:
            self.logger.error("HID-Library nicht verfügbar")
            return False

        try:
            # Alle HID-Geräte scannen
            devices = hid.enumerate()

            # TS-HRW380 suchen
            target_device = None

            # Zuerst nach VID/PID suchen
            for dev in devices:
                if (dev['vendor_id'] == self.vendor_id and 
                    dev['product_id'] == self.product_id):
                    target_device = dev
                    break

            # Falls nicht gefunden, nach Produktname suchen
            if not target_device:
                for dev in devices:
                    product = str(dev.get('product_string', '')).upper()
                    if 'TS-HRW' in product or 'RFID' in product:
                        target_device = dev
                        self.vendor_id = dev['vendor_id']
                        self.product_id = dev['product_id']
                        self.logger.info(f"RFID-Reader gefunden: {dev.get('product_string')}")
                        break

            if not target_device:
                self._last_error = "TS-HRW380 RFID-Reader nicht gefunden"
                self.logger.error(self._last_error)
                self._list_hid_devices()
                return False

            # Verbindung herstellen
            self.device = hid.device()
            self.device.open(self.vendor_id, self.product_id)

            # Device-Info loggen
            manufacturer = self.device.get_manufacturer_string() or "Unknown"
            product = self.device.get_product_string() or "Unknown"

            self.logger.info(f"RFID-Reader verbunden: {manufacturer} {product}")
            self.logger.info(f"VID: 0x{self.vendor_id:04X}, PID: 0x{self.product_id:04X}")

            # Non-blocking Modus
            self.device.set_nonblocking(1)

            # Lese-Thread starten
            self._start_reading_thread()

            self._connected = True
            return True

        except Exception as e:
            self._last_error = f"Verbindungsfehler: {e}"
            self.logger.error(self._last_error)
            return False

    def _list_hid_devices(self):
        """Listet verfügbare HID-Geräte für Debugging"""
        self.logger.info("Verfügbare HID-Geräte:")
        try:
            devices = hid.enumerate()
            for dev in devices:
                vid = dev['vendor_id']
                pid = dev['product_id']
                manufacturer = dev.get('manufacturer_string', 'Unknown')
                product = dev.get('product_string', 'Unknown')
                self.logger.info(f"  VID:0x{vid:04X} PID:0x{pid:04X} - {manufacturer} {product}")
        except Exception as e:
            self.logger.error(f"Fehler beim Auflisten der HID-Geräte: {e}")

    def _start_reading_thread(self):
        """Startet den Lese-Thread"""
        self.is_running = True
        self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
        self.read_thread.start()
        self.logger.info("RFID-Lese-Thread gestartet")

    def _read_loop(self):
        """Haupt-Lese-Schleife"""
        while self.is_running and self.device:
            try:
                # HID-Daten lesen (64 Byte Buffer, 100ms Timeout)
                data = self.device.read(64, timeout_ms=100)

                if data and any(b != 0 for b in data):  # Ignoriere Null-Daten
                    self._process_hid_data(data)

                time.sleep(0.01)  # Kurze Pause

            except Exception as e:
                if self.is_running:
                    self.logger.error(f"Lesefehler: {e}")
                time.sleep(0.1)

    def _process_hid_data(self, data: list):
        """Verarbeitet empfangene HID-Daten"""
        try:
            # Filtern und in Text konvertieren
            text_chars = []
            for byte_val in data:
                if byte_val == 0:
                    continue
                if 32 <= byte_val <= 126:  # Druckbare ASCII-Zeichen
                    text_chars.append(chr(byte_val))
                elif byte_val in [10, 13]:  # LF, CR
                    text_chars.append('\n')

            if not text_chars:
                return

            text = ''.join(text_chars)
            self.card_buffer += text

            # Vollständige Karte erkannt (Enter/Return)
            if '\n' in self.card_buffer:
                lines = self.card_buffer.split('\n')
                for line in lines[:-1]:  # Alle außer der letzten (unvollständigen)
                    card_id = line.strip()
                    if card_id and len(card_id) >= 6:  # Mindestlänge
                        self._handle_new_card(card_id)

                # Letzten Teil behalten
                self.card_buffer = lines[-1]

        except Exception as e:
            self.logger.error(f"Fehler beim Verarbeiten der HID-Daten: {e}")

    def _handle_new_card(self, card_id: str):
        """Behandelt erkannte Karte"""
        current_time = time.time()

        # Duplikate innerhalb 2 Sekunden ignorieren
        if (card_id == self.last_card and 
            current_time - self.last_card_time < 2.0):
            return

        self.last_card = card_id
        self.last_card_time = current_time

        self.logger.info(f"🎯 RFID-Karte erkannt: {card_id}")

        # In Queue einreihen
        try:
            self.card_queue.put_nowait(card_id)
        except queue.Full:
            # Queue voll, älteste Karte entfernen
            try:
                self.card_queue.get_nowait()
                self.card_queue.put_nowait(card_id)
            except queue.Empty:
                pass

    def read_card(self, timeout: float = 1.0) -> Optional[str]:
        """
        Liest eine RFID-Karte

        Args:
            timeout: Timeout in Sekunden

        Returns:
            RFID-Karten-ID oder None
        """
        if not self._connected:
            return None

        try:
            return self.card_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def read_card_async(self) -> Optional[str]:
        """
        Nicht-blockierendes Lesen einer RFID-Karte

        Returns:
            RFID-Karten-ID oder None
        """
        if not self._connected:
            return None

        try:
            return self.card_queue.get_nowait()
        except queue.Empty:
            return None

    def is_connected(self) -> bool:
        """
        Prüft Verbindungsstatus

        Returns:
            True wenn verbunden
        """
        return self._connected and self.device is not None

    def disconnect(self):
        """Trennt Verbindung zum RFID-Reader"""
        self.logger.info("Trenne RFID-Reader...")

        # Lese-Thread stoppen
        self.is_running = False
        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join(timeout=2.0)

        # Device schließen
        if self.device:
            try:
                self.device.close()
            except Exception as e:
                self.logger.error(f"Fehler beim Schließen: {e}")
            finally:
                self.device = None

        self._connected = False
        self.logger.info("RFID-Reader getrennt")

    def get_last_error(self) -> Optional[str]:
        """
        Holt letzten Fehler

        Returns:
            Fehlermeldung oder None
        """
        return self._last_error

    def __del__(self):
        """Destruktor"""
        self.disconnect()


# Kompatibilitätsfunktionen für das bestehende WMS
def create_rfid_reader(port: str = None, baudrate: int = 9600) -> RFIDReader:
    """
    Factory-Funktion für RFID-Reader

    Args:
        port: Ignoriert (HID)
        baudrate: Ignoriert (HID)

    Returns:
        HID-RFID Reader Instanz
    """
    return RFIDReader(port, baudrate)


# Test-Funktion
def test_rfid_reader():
    """Testet den HID-RFID Reader"""
    print("=== HID-RFID READER TEST ===")

    if not HID_AVAILABLE:
        print("❌ HID-Library nicht verfügbar")
        print("   pip install hidapi")
        return False

    reader = RFIDReader()

    if reader.connect():
        print("✅ RFID-Reader verbunden")
        print("👋 Halten Sie eine RFID-Karte an den Reader...")
        print("   (5 Sekunden Test)")

        start_time = time.time()
        cards_read = 0

        while time.time() - start_time < 5.0:
            card = reader.read_card_async()
            if card:
                print(f"🎯 Karte: {card}")
                cards_read += 1
            time.sleep(0.1)

        reader.disconnect()

        print(f"✅ Test abgeschlossen. {cards_read} Karten gelesen.")
        return True
    else:
        print(f"❌ Verbindung fehlgeschlagen: {reader.get_last_error()}")
        return False


if __name__ == "__main__":
    test_rfid_reader()
