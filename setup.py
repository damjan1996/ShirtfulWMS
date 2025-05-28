"""
Setup-Script für Shirtful WMS
Installation und Konfiguration des Systems.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from setuptools import setup, find_packages

# Projekt-Informationen
PROJECT_NAME = "ShirtfulWMS"
VERSION = "1.0.0"
AUTHOR = "Shirtful IT Team"
DESCRIPTION = "Warehouse Management System für Textilveredelung"

# Python-Version prüfen
if sys.version_info < (3, 10):
    print("Fehler: Python 3.10 oder höher erforderlich!")
    sys.exit(1)


def read_requirements():
    """Liest requirements.txt."""
    with open('requirements.txt', 'r') as f:
        return [line.strip() for line in f
                if line.strip() and not line.startswith('#')]


def create_directories():
    """Erstellt notwendige Verzeichnisse."""
    directories = [
        'logs',
        'database/migrations',
        'database/scripts',
        'resources/images',
        'resources/sounds',
        'resources/icons',
        'temp',
        'backups'
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Verzeichnis erstellt: {directory}")


def create_desktop_shortcuts():
    """Erstellt Desktop-Verknüpfungen für Windows."""
    if sys.platform != 'win32':
        return

    try:
        import winshell
        from win32com.client import Dispatch

        desktop = winshell.desktop()

        apps = [
            ('Wareneingang', 'wareneingang.py', '📥'),
            ('Veredelung', 'veredelung.py', '🎨'),
            ('Betuchung', 'betuchung.py', '🧵'),
            ('Qualitätskontrolle', 'qualitaetskontrolle.py', '🔍'),
            ('Warenausgang', 'warenausgang.py', '📦')
        ]

        for name, script, icon in apps:
            path = os.path.join(desktop, f"Shirtful WMS - {name}.lnk")
            target = os.path.join(os.getcwd(), 'apps', script)
            wDir = os.getcwd()

            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(path)
            shortcut.Targetpath = sys.executable
            shortcut.Arguments = f'"{target}"'
            shortcut.WorkingDirectory = wDir
            shortcut.Description = f"Shirtful WMS - {name}"
            shortcut.save()

            print(f"✓ Desktop-Verknüpfung erstellt: {name}")

    except ImportError:
        print("⚠ pywin32 nicht installiert - keine Desktop-Verknüpfungen erstellt")
    except Exception as e:
        print(f"⚠ Fehler beim Erstellen der Verknüpfungen: {e}")


def install_system_dependencies():
    """Installiert System-Abhängigkeiten."""
    print("\n=== System-Abhängigkeiten ===")

    if sys.platform == 'win32':
        # Visual C++ Redistributable prüfen
        print("✓ Windows-System erkannt")

        # ODBC Driver prüfen
        try:
            import pyodbc
            drivers = [d for d in pyodbc.drivers() if 'SQL Server' in d]
            if drivers:
                print(f"✓ SQL Server ODBC Driver gefunden: {drivers[0]}")
            else:
                print("⚠ Kein SQL Server ODBC Driver gefunden!")
                print(
                    "  Bitte installieren: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server")
        except:
            pass


def setup_database():
    """Richtet die Datenbank ein."""
    print("\n=== Datenbank-Setup ===")

    try:
        from config.database_config import get_connection_string, CREATE_TABLES_SQL
        import pyodbc

        # Verbindung testen
        conn_str = get_connection_string()
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        print("✓ Datenbankverbindung erfolgreich")

        # Tabellen erstellen
        for statement in CREATE_TABLES_SQL.split('GO'):
            if statement.strip():
                cursor.execute(statement)

        conn.commit()
        print("✓ Datenbank-Tabellen erstellt")

        conn.close()

    except Exception as e:
        print(f"⚠ Datenbank-Setup fehlgeschlagen: {e}")
        print("  Bitte manuell ausführen: database/schema.sql")


def create_initial_config():
    """Erstellt initiale Konfigurationsdateien."""
    print("\n=== Konfiguration ===")

    # settings.json erstellen wenn nicht vorhanden
    settings_file = Path('config/settings.json')
    if not settings_file.exists():
        from config.settings import Settings
        settings = Settings()
        settings.save()
        print("✓ Standard-Konfiguration erstellt: config/settings.json")
    else:
        print("✓ Konfiguration vorhanden")


def compile_resources():
    """Kompiliert Ressourcen."""
    print("\n=== Ressourcen ===")

    # Sound-Dateien erstellen (Platzhalter)
    sounds = ['success.wav', 'error.wav', 'scan.wav', 'warning.wav']
    for sound in sounds:
        sound_file = Path(f'resources/sounds/{sound}')
        if not sound_file.exists():
            # Leere Datei als Platzhalter
            sound_file.touch()
            print(f"✓ Sound-Platzhalter erstellt: {sound}")


def run_tests():
    """Führt Tests aus."""
    print("\n=== Tests ===")

    try:
        result = subprocess.run([sys.executable, '-m', 'pytest', 'tests/', '-v'],
                                capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Alle Tests erfolgreich")
        else:
            print("⚠ Einige Tests fehlgeschlagen")
            print(result.stdout)
    except:
        print("⚠ pytest nicht installiert - Tests übersprungen")


def main():
    """Haupt-Setup-Funktion."""
    print("=" * 60)
    print(f"Shirtful WMS Setup v{VERSION}")
    print("=" * 60)

    # 1. Verzeichnisse erstellen
    print("\n1. Erstelle Verzeichnisstruktur...")
    create_directories()

    # 2. System-Abhängigkeiten
    print("\n2. Prüfe System-Abhängigkeiten...")
    install_system_dependencies()

    # 3. Python-Pakete installieren
    print("\n3. Installiere Python-Pakete...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])

    # 4. Datenbank einrichten
    print("\n4. Richte Datenbank ein...")
    setup_database()

    # 5. Konfiguration
    print("\n5. Erstelle Konfiguration...")
    create_initial_config()

    # 6. Ressourcen
    print("\n6. Kompiliere Ressourcen...")
    compile_resources()

    # 7. Desktop-Verknüpfungen
    print("\n7. Erstelle Desktop-Verknüpfungen...")
    create_desktop_shortcuts()

    # 8. Tests
    print("\n8. Führe Tests aus...")
    run_tests()

    print("\n" + "=" * 60)
    print("✓ Setup abgeschlossen!")
    print("=" * 60)
    print("\nNächste Schritte:")
    print("1. Konfiguration anpassen: config/settings.json")
    print("2. RFID-Tags in Datenbank eintragen")
    print("3. Anwendung starten: python apps/wareneingang.py")
    print("\nBei Problemen: Siehe README.md")


if __name__ == '__main__':
    # Standard setuptools setup
    if len(sys.argv) > 1 and sys.argv[1] in ['install', 'develop']:
        setup(
            name=PROJECT_NAME,
            version=VERSION,
            author=AUTHOR,
            description=DESCRIPTION,
            packages=find_packages(),
            install_requires=read_requirements(),
            python_requires='>=3.10',
            entry_points={
                'console_scripts': [
                    'shirtful-wareneingang=apps.wareneingang:main',
                    'shirtful-veredelung=apps.veredelung:main',
                    'shirtful-betuchung=apps.betuchung:main',
                    'shirtful-qualitaet=apps.qualitaetskontrolle:main',
                    'shirtful-warenausgang=apps.warenausgang:main',
                ],
            },
        )
    else:
        # Eigenes Setup ausführen
        main()