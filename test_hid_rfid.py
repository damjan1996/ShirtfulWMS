"""
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
    print("\n=== RFID-READER KLASSE TEST ===")

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
            print("\n👋 RFID-KARTEN TEST")
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
                print(f"\n✅ {len(cards_found)} verschiedene Karten erkannt")
                print("🎉 RFID-Reader funktioniert perfekt!")
            else:
                print("\n⚠️ Keine Karten erkannt (normal wenn keine Karte angelegt)")

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
    print("\n=== WMS-INTEGRATION TEST ===")

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
    print("\n" + "=" * 50)
    print("📊 TEST-ERGEBNISSE:")

    all_passed = True
    for test_name, passed in test_results:
        status = "✅" if passed else "❌"
        print(f"   {status} {test_name}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n🎉 ALLE TESTS ERFOLGREICH!")
        print("\n🚀 WMS kann gestartet werden:")
        print("   .\\run_wareneingang.bat")
        print("\n💡 RFID-Karten Testen:")
        print("   - Halten Sie RFID-Karten an den Reader")
        print("   - Test-RFID: 1234567890 (falls vorhanden)")
    else:
        print("\n⚠️ Einige Tests fehlgeschlagen")
        print("Bitte Konfiguration prüfen")

if __name__ == "__main__":
    main()
