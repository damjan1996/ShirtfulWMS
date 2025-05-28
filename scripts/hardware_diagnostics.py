"""
Hardware-Diagnose für Shirtful WMS
Findet verfügbare COM-Ports und prüft Systemvoraussetzungen
"""

import serial.tools.list_ports
import pyodbc
import platform
import sys


def check_com_ports():
    """Findet alle verfügbaren COM-Ports"""
    print("=== COM-PORTS DIAGNOSE ===")
    ports = serial.tools.list_ports.comports()

    if not ports:
        print("❌ Keine COM-Ports gefunden!")
        return None

    print("📡 Verfügbare COM-Ports:")
    for port in ports:
        print(f"  ✅ {port.device} - {port.description}")
        if 'USB' in port.description.upper() or 'SERIAL' in port.description.upper():
            print(f"     🎯 RFID-Reader könnte hier sein: {port.device}")

    return [port.device for port in ports]


def check_sql_drivers():
    """Prüft verfügbare SQL Server Treiber"""
    print("\n=== SQL SERVER TREIBER ===")
    drivers = pyodbc.drivers()

    sql_drivers = [d for d in drivers if 'SQL' in d.upper()]

    if sql_drivers:
        print("✅ SQL Server Treiber gefunden:")
        for driver in sql_drivers:
            print(f"  - {driver}")
    else:
        print("❌ Keine SQL Server Treiber gefunden!")
        print("💡 Installieren Sie SQL Server oder verwenden Sie SQLite")

    return sql_drivers


def suggest_solutions():
    """Schlägt Lösungen vor"""
    print("\n=== LÖSUNGSVORSCHLÄGE ===")

    print("\n🔧 RFID-Reader Problem:")
    print("1. Prüfen Sie den richtigen COM-Port oben")
    print("2. Bearbeiten Sie config/settings.py:")
    print("   'rfid': { 'port': 'COM1' }  # Richtigen Port einsetzen")
    print("3. Oder setzen Sie 'enabled': False zum Testen")

    print("\n🗄️ Datenbank Problem:")
    print("OPTION A - SQL Server installieren:")
    print("1. SQL Server Express herunterladen")
    print("2. Datenbank 'ShirtfulWMS' erstellen")
    print("3. Connection String in settings.py anpassen")

    print("\nOPTION B - SQLite verwenden (einfacher):")
    print("1. Ich kann die Database-Klasse für SQLite anpassen")
    print("2. Keine Server-Installation nötig")
    print("3. Datei-basierte Datenbank")


def test_rfid_port(port):
    """Testet einen spezifischen COM-Port"""
    try:
        ser = serial.Serial(port, 9600, timeout=1)
        ser.close()
        print(f"✅ {port} ist verfügbar und funktioniert")
        return True
    except Exception as e:
        print(f"❌ {port} Fehler: {e}")
        return False


if __name__ == "__main__":
    print("🔍 SHIRTFUL WMS - HARDWARE DIAGNOSE")
    print("=" * 50)

    # System Info
    print(f"💻 System: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {sys.version}")

    # COM-Ports prüfen
    available_ports = check_com_ports()

    # SQL Treiber prüfen
    sql_drivers = check_sql_drivers()

    # Lösungen vorschlagen
    suggest_solutions()

    # Interaktiver Test
    if available_ports:
        print(f"\n🧪 RFID-PORT TESTEN")
        print("Welchen Port möchten Sie testen?")
        for i, port in enumerate(available_ports, 1):
            print(f"{i}. {port}")

        try:
            choice = input("Port-Nummer eingeben (oder Enter zum Überspringen): ")
            if choice.strip():
                port_index = int(choice) - 1
                test_port = available_ports[port_index]
                print(f"\n🔧 Teste {test_port}...")
                test_rfid_port(test_port)
        except:
            print("Übersprungen")

    print("\n✨ Diagnose abgeschlossen!")