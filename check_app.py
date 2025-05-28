"""
Prüft die Wareneingang-App und findet RFID-Import-Probleme
"""

import re
from pathlib import Path


def analyze_wareneingang_app():
    """Analysiert die Wareneingang-App"""
    print("🔍 WARENEINGANG-APP ANALYSE")
    print("=" * 40)

    app_file = Path("apps/wareneingang.py")

    if not app_file.exists():
        print("❌ apps/wareneingang.py nicht gefunden!")
        return

    try:
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()

        print("✅ Wareneingang-App gefunden")

        # RFID-Imports finden
        rfid_imports = []
        import_lines = re.findall(r'from .* import.*rfid.*|import.*rfid.*', content, re.IGNORECASE)

        for line in import_lines:
            rfid_imports.append(line.strip())

        if rfid_imports:
            print("\n📡 RFID-Imports gefunden:")
            for imp in rfid_imports:
                print(f"   - {imp}")
        else:
            print("\n⚠️ Keine RFID-Imports gefunden")

        # Serial-Usage finden
        serial_usage = re.findall(r'.*serial.*|.*Serial.*|.*COM\d.*', content)
        if serial_usage:
            print("\n📟 Serial-Verwendung gefunden:")
            for line in serial_usage[:5]:  # Nur erste 5
                print(f"   - {line.strip()}")

        # Settings-Import prüfen
        settings_usage = re.findall(r'.*settings.*|.*config.*', content, re.IGNORECASE)
        if settings_usage:
            print("\n⚙️ Settings-Verwendung:")
            for line in settings_usage[:3]:
                print(f"   - {line.strip()}")

        # RFID-Reader Erstellung suchen
        rfid_creation = re.findall(r'.*RFIDReader.*\(.*\)|.*rfid.*=.*', content, re.IGNORECASE)
        if rfid_creation:
            print("\n🔧 RFID-Reader Erstellung:")
            for line in rfid_creation:
                print(f"   - {line.strip()}")

        return content

    except Exception as e:
        print(f"❌ Fehler beim Lesen der App: {e}")
        return None


def find_all_rfid_files():
    """Findet alle RFID-bezogenen Dateien"""
    print("\n📁 ALLE RFID-DATEIEN:")

    rfid_files = []

    # Suche in verschiedenen Verzeichnissen
    search_dirs = [".", "utils", "hardware", "apps", "config"]

    for search_dir in search_dirs:
        dir_path = Path(search_dir)
        if dir_path.exists():
            for file_path in dir_path.rglob("*.py"):
                if 'rfid' in file_path.name.lower():
                    rfid_files.append(file_path)

    if rfid_files:
        for file_path in rfid_files:
            print(f"   ✅ {file_path}")
    else:
        print("   ⚠️ Keine RFID-Dateien gefunden")

    return rfid_files


def create_quick_fix():
    """Erstellt schnelle Korrektur für die Wareneingang-App"""
    print("\n🔧 SCHNELLE KORREKTUR ERSTELLEN:")

    # Backup der Original-App
    app_file = Path("apps/wareneingang.py")
    backup_file = Path("apps/wareneingang_original.py")

    if app_file.exists():
        import shutil
        shutil.copy2(app_file, backup_file)
        print(f"✅ Backup erstellt: {backup_file}")

        # Inhalt lesen
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # RFID-Import korrigieren
        if 'from utils.rfid_reader import' not in content:
            # Import hinzufügen
            if 'import' in content:
                # Nach dem letzten Import einfügen
                lines = content.split('\n')
                insert_pos = 0
                for i, line in enumerate(lines):
                    if line.strip().startswith('import ') or line.strip().startswith('from '):
                        insert_pos = i + 1

                lines.insert(insert_pos, 'from utils.rfid_reader import RFIDReader')
                content = '\n'.join(lines)
                print("✅ HID-RFID Import hinzugefügt")

        # Serial-spezifische Imports entfernen/ersetzen
        content = content.replace(
            'import serial',
            '# import serial  # Ersetzt durch HID-RFID'
        )

        # COM-Port Referenzen ersetzen
        content = re.sub(
            r"'COM\d+'",
            "'HID'  # HID-RFID (kein COM-Port)",
            content
        )

        # Speichern
        with open(app_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print("✅ Wareneingang-App für HID-RFID angepasst")
        return True

    return False


def main():
    """Hauptfunktion"""
    print("🔍 WARENEINGANG-APP DIAGNOSE")
    print("=" * 50)

    # 1. App analysieren
    content = analyze_wareneingang_app()

    # 2. Alle RFID-Dateien finden
    rfid_files = find_all_rfid_files()

    # 3. Korrektur anbieten
    if content:
        print("\n" + "=" * 50)
        print("💡 LÖSUNGSVORSCHLÄGE:")

        if 'COM3' in content or 'serial' in content.lower():
            print("⚠️ App verwendet noch Serial/COM-Ports")
            print("🔧 Automatische Korrektur verfügbar")

            response = input("\nMöchten Sie die automatische Korrektur anwenden? (j/n): ")
            if response.lower() in ['j', 'ja', 'y', 'yes']:
                if create_quick_fix():
                    print("\n✅ KORREKTUR ANGEWENDET!")
                    print("🚀 Versuchen Sie jetzt: .\\run_wareneingang.bat")
                else:
                    print("❌ Korrektur fehlgeschlagen")
        else:
            print("✅ App scheint bereits korrekt konfiguriert")

    # 4. HID-Test empfehlen
    print("\n📋 NÄCHSTE SCHRITTE:")
    print("1. pip install hidapi")
    print("2. python test_hid_rfid.py")
    print("3. .\\run_wareneingang.bat")


if __name__ == "__main__":
    main()