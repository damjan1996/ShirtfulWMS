"""
Integration Patch für HID-RFID Reader
Ersetzt die bestehende Serial-RFID Implementierung
"""

import shutil
from pathlib import Path


def patch_rfid_reader():
    """Patcht die RFID-Reader Implementierung für HID"""

    print("🔧 RFID-READER INTEGRATION PATCH")
    print("=" * 40)

    # 1. Backup der Original-RFID Datei
    rfid_files = [
        "utils/rfid_reader.py",
        "utils/rfid.py",
        "hardware/rfid_reader.py"
    ]

    backup_created = False
    for rfid_file in rfid_files:
        file_path = Path(rfid_file)
        if file_path.exists():
            backup_path = file_path.with_suffix('.backup.py')
            shutil.copy2(file_path, backup_path)
            print(f"✅ Backup erstellt: {backup_path}")
            backup_created = True
            break

    if not backup_created:
        print("ℹ️ Keine bestehende RFID-Datei gefunden (wird neu erstellt)")

    # 2. Neue HID-RFID Implementation erstellen
    rfid_code = '''"""
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
                    text_chars.append('\\n')

            if not text_chars:
                return

            text = ''.join(text_chars)
            self.card_buffer += text

            # Vollständige Karte erkannt (Enter/Return)
            if '\\n' in self.card_buffer:
                lines = self.card_buffer.split('\\n')
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
'''

    # RFID-Datei erstellen/ersetzen
    rfid_path = Path("utils/rfid_reader.py")
    rfid_path.parent.mkdir(exist_ok=True)

    with open(rfid_path, 'w', encoding='utf-8') as f:
        f.write(rfid_code)

    print(f"✅ HID-RFID Reader erstellt: {rfid_path}")

    # 3. Settings für HID anpassen
    patch_settings_for_hid()

    # 4. Test-Script erstellen
    create_hid_test_script()

    print("\n" + "=" * 40)
    print("✅ HID-RFID INTEGRATION ABGESCHLOSSEN!")
    print("\n🧪 Zum Testen:")
    print("   python test_hid_rfid.py")
    print("\n🚀 WMS starten:")
    print("   .\\run_wareneingang.bat")


def patch_settings_for_hid():
    """Passt die Einstellungen für HID-RFID an"""
    settings_file = Path("config/settings.py")

    if not settings_file.exists():
        print("⚠️ settings.py nicht gefunden - wird übersprungen")
        return

    try:
        with open(settings_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # RFID aktivieren
        content = content.replace(
            "'enabled': False,",
            "'enabled': True,  # HID-RFID aktiviert"
        )

        # Port-Einstellung für HID (wird ignoriert, aber für Kompatibilität)
        content = content.replace(
            "'port': 'COM3',",
            "'port': 'HID',  # HID-RFID Reader (kein COM-Port nötig)"
        )

        with open(settings_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print("✅ Settings für HID-RFID angepasst")

    except Exception as e:
        print(f"⚠️ Fehler beim Anpassen der Settings: {e}")


def create_hid_test_script():
    """Erstellt Test-Script für HID-RFID"""
    test_code = '''"""
Test-Script für HID-RFID Integration
Testet den TS-HRW380 Reader
"""

import sys
import time
from pathlib import Path

# Pfad zum WMS hinzufügen
sys.path.insert(0, str(Path(__file__).parent))

def test_hid_import():
    """Testet HID-Library Import"""
    print("=== HID-LIBRARY TEST ===")

    try:
        import hid
        print("✅ HID-Library erfolgreich importiert")

        # Verfügbare Geräte auflisten
        devices = hid.enumerate()
        print(f"✅ {len(devices)} HID-Geräte gefunden")

        # Nach RFID-Reader suchen
        rfid_devices = []
        for dev in devices:
            product = str(dev.get('product_string', '')).upper()
            if any(keyword in product for keyword in ['TS-HRW', 'RFID', 'CARD', 'READER']):
                rfid_devices.append(dev)

        if rfid_devices:
            print(f"🎯 {len(rfid_devices)} RFID-Reader gefunden:")
            for dev in rfid_devices:
                print(f"   - {dev.get('product_string')} (VID:0x{dev['vendor_id']:04X} PID:0x{dev['product_id']:04X})")
        else:
            print("⚠️ Keine RFID-Reader gefunden")

        return True

    except ImportError:
        print("❌ HID-Library nicht verfügbar")
        print("   Installieren Sie: pip install hidapi")
        return False
    except Exception as e:
        print(f"❌ HID-Test Fehler: {e}")
        return False

def test_rfid_reader():
    """Testet RFID-Reader Klasse"""
    print("\\n=== RFID-READER KLASSE TEST ===")

    try:
        from utils.rfid_reader import RFIDReader
        print("✅ RFID-Reader Klasse importiert")

        # Reader erstellen
        reader = RFIDReader()
        print("✅ RFID-Reader Instanz erstellt")

        # Verbinden
        if reader.connect():
            print("✅ RFID-Reader verbunden")

            # Test-Lesen
            print("\\n👋 RFID-KARTEN TEST")
            print("Halten Sie eine Karte an den Reader...")
            print("(5 Sekunden Test)")

            start_time = time.time()
            cards_found = []

            while time.time() - start_time < 5.0:
                card = reader.read_card_async()
                if card and card not in cards_found:
                    print(f"🎯 Karte erkannt: {card}")
                    cards_found.append(card)
                time.sleep(0.1)

            reader.disconnect()

            if cards_found:
                print(f"\\n✅ {len(cards_found)} verschiedene Karten erkannt")
                print("🎉 RFID-Reader funktioniert perfekt!")
            else:
                print("\\n⚠️ Keine Karten erkannt (normal wenn keine Karte angelegt)")

            return True

        else:
            error = reader.get_last_error()
            print(f"❌ Verbindung fehlgeschlagen: {error}")
            return False

    except Exception as e:
        print(f"❌ RFID-Reader Test Fehler: {e}")
        return False

def test_wms_integration():
    """Testet WMS-Integration"""
    print("\\n=== WMS-INTEGRATION TEST ===")

    try:
        # Database-Test
        from utils.database import Database
        db = Database()
        print("✅ Datenbank-Verbindung OK")

        # Test-Mitarbeiter
        employees = db.get_all_employees()
        print(f"✅ {len(employees)} Mitarbeiter in DB")

        # RFID-Test mit Datenbank
        from utils.rfid_reader import RFIDReader
        reader = RFIDReader()

        if reader.connect():
            print("✅ RFID-WMS Integration bereit")
            reader.disconnect()
            return True
        else:
            print("⚠️ RFID-Reader nicht verbunden")
            return False

    except Exception as e:
        print(f"❌ WMS-Integration Fehler: {e}")
        return False

def main():
    """Hauptfunktion"""
    print("🧪 SHIRTFUL WMS - HID-RFID TEST")
    print("=" * 50)

    # Tests durchführen
    test_results = []

    test_results.append(("HID-Library", test_hid_import()))
    test_results.append(("RFID-Reader", test_rfid_reader()))
    test_results.append(("WMS-Integration", test_wms_integration()))

    # Ergebnisse
    print("\\n" + "=" * 50)
    print("📊 TEST-ERGEBNISSE:")

    all_passed = True
    for test_name, passed in test_results:
        status = "✅" if passed else "❌"
        print(f"   {status} {test_name}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\\n🎉 ALLE TESTS ERFOLGREICH!")
        print("\\n🚀 WMS kann gestartet werden:")
        print("   .\\\\run_wareneingang.bat")
        print("\\n💡 RFID-Karten Testen:")
        print("   - Halten Sie RFID-Karten an den Reader")
        print("   - Test-RFID: 1234567890 (falls vorhanden)")
    else:
        print("\\n⚠️ Einige Tests fehlgeschlagen")
        print("Bitte Konfiguration prüfen")

if __name__ == "__main__":
    main()
'''

    with open('test_hid_rfid.py', 'w', encoding='utf-8') as f:
        f.write(test_code)

    print("✅ HID-Test Script erstellt: test_hid_rfid.py")


if __name__ == "__main__":
    patch_rfid_reader()