"""
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
    print("\n=== RFID TEST ===")
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
    print("\n=== RFID-AUTH TEST ===")
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

    print("\n" + "=" * 50)
    print("📊 ERGEBNISSE:")

    all_ok = True
    for name, passed in results:
        status = "✅" if passed else "❌"
        print(f"   {status} {name}")
        if not passed:
            all_ok = False

    if all_ok:
        print("\n🎉 ALLE TESTS ERFOLGREICH!")
        print("\n🚀 WMS starten:")
        print("   .\\run_wareneingang.bat")
    else:
        print("\n⚠️ Einige Tests fehlgeschlagen")

if __name__ == "__main__":
    main()
