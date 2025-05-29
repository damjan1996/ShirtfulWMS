#!/usr/bin/env python3
"""
Shirtful WMS - Wareneingang Main Entry Point
Haupteinstiegspunkt für die modulare Wareneingang-Anwendung

Verwendung:
  python main.py                 # Normale Ausführung
  python main.py --debug         # Debug-Modus
  python main.py --windowed       # Fenster-Modus (nicht Vollbild)
  python main.py --help           # Hilfe anzeigen
"""

import sys
import os
import argparse
import logging
from datetime import datetime

# Projekt-Root zum Python-Path hinzufügen
current_dir = os.path.dirname(__file__)
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

# Eigene Module importieren
try:
    from app import WareneingangApp
    from utils.logger import setup_logger
    import config.settings as settings
except ImportError as e:
    print(f"KRITISCHER FEHLER: Module konnten nicht importiert werden: {e}")
    print("Stellen Sie sicher, dass Sie sich im korrekten Verzeichnis befinden.")
    print(f"Aktuelles Verzeichnis: {os.getcwd()}")
    print(f"Skript-Verzeichnis: {current_dir}")
    sys.exit(1)


def setup_logging(debug_mode: bool = False) -> logging.Logger:
    """
    Richtet das Logging für die Anwendung ein.

    Args:
        debug_mode: True für Debug-Level Logging

    Returns:
        logging.Logger: Konfigurierter Logger
    """
    # Log-Level bestimmen
    log_level = logging.DEBUG if debug_mode else logging.INFO

    # Hauptlogger einrichten
    logger = setup_logger('wareneingang_main', level=log_level)

    # Zusätzliche Konfiguration für Debug-Modus
    if debug_mode:
        # Root-Logger Level setzen
        logging.getLogger().setLevel(logging.DEBUG)

        # Debug-Informationen ausgeben
        logger.debug("Debug-Modus aktiviert")
        logger.debug(f"Python-Version: {sys.version}")
        logger.debug(f"Aktuelles Verzeichnis: {os.getcwd()}")
        logger.debug(f"Projekt-Root: {project_root}")
        logger.debug(f"Python-Path: {sys.path[:3]}...")  # Erste 3 Einträge

    return logger


def check_system_requirements() -> tuple[bool, list]:
    """
    Prüft Systemanforderungen und Abhängigkeiten.

    Returns:
        tuple: (requirements_met, issues)
    """
    issues = []

    # Python-Version prüfen
    if sys.version_info < (3, 10):
        issues.append(f"Python 3.10+ erforderlich, gefunden: {sys.version}")

    # Kritische Module prüfen
    critical_modules = {
        'tkinter': 'GUI Framework',
        'sqlite3': 'Lokale Datenbank (Fallback)',  # Meist vorhanden
    }

    for module_name, description in critical_modules.items():
        try:
            __import__(module_name)
        except ImportError:
            issues.append(f"Kritisches Modul fehlt: {module_name} ({description})")

    # Optionale Module prüfen (Warnungen)
    optional_modules = {
        'pyodbc': 'MSSQL Datenbankverbindung',
        'serial': 'RFID-Reader Support',
        'cv2': 'Kamera QR-Scanner',
        'pyzbar': 'QR-Code Dekodierung'
    }

    for module_name, description in optional_modules.items():
        try:
            __import__(module_name)
        except ImportError:
            issues.append(f"Optionales Modul fehlt: {module_name} ({description}) - Funktionalität eingeschränkt")

    # Verzeichnisstruktur prüfen
    required_dirs = [
        os.path.join(project_root, 'utils'),
        os.path.join(project_root, 'config'),
        os.path.join(current_dir, 'ui'),
        os.path.join(current_dir, 'services')
    ]

    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            issues.append(f"Erforderliches Verzeichnis fehlt: {dir_path}")

    return len(issues) == 0, issues


def print_startup_banner():
    """Zeigt Startup-Banner an."""
    banner = f"""
╔══════════════════════════════════════════════════════════════╗
║                    SHIRTFUL WMS - WARENEINGANG                 ║
║                         Version 1.0.0                          ║
╠══════════════════════════════════════════════════════════════╣
║  Modulare Wareneingang-Station für das Shirtful               ║
║  Lagerverwaltungssystem                                        ║
║                                                                ║
║  • RFID-Mitarbeiter-Authentifizierung                         ║
║  • QR-Code Paket-Scanning                                      ║
║  • Lieferungsverwaltung                                        ║
║  • Touch-optimierte Oberfläche                                ║
╚══════════════════════════════════════════════════════════════╝

Startzeit: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
Python:    {sys.version.split()[0]}
System:    {os.name}

"""
    print(banner)


def print_help():
    """Zeigt erweiterte Hilfe an."""
    help_text = """
SHIRTFUL WMS - WARENEINGANG
===========================

BESCHREIBUNG:
  Modulare Wareneingang-Station für das Shirtful Lagerverwaltungssystem.
  Ermöglicht RFID-basierte Mitarbeiter-Anmeldung, QR-Code Paket-Scanning
  und vollständige Lieferungsverwaltung.

VERWENDUNG:
  python main.py [OPTIONEN]

OPTIONEN:
  -h, --help       Zeigt diese Hilfe an
  -d, --debug      Aktiviert Debug-Modus mit detailliertem Logging
  -w, --windowed   Startet im Fenster-Modus (nicht Vollbild)
  -v, --version    Zeigt Versionsinformationen an
  --check-deps     Prüft nur Abhängigkeiten ohne Start
  --safe-mode      Startet im Sicherheitsmodus (eingeschränkte Features)

TASTENKOMBINATIONEN:
  ESC              Vollbild-Modus beenden / Anwendung beenden
  F11              Vollbild-Modus umschalten
  Strg+Q           Anwendung beenden
  Alt+F4           Anwendung beenden

KONFIGURATION:
  Konfigurationsdateien befinden sich im 'config/' Verzeichnis.
  Logging-Ausgabe erfolgt in 'logs/' (falls vorhanden).

ANFORDERUNGEN:
  - Python 3.10 oder höher
  - tkinter (normalerweise im Python enthalten)
  - Optionale Module: pyodbc, pyserial, opencv-python, pyzbar

SUPPORT:
  Bei Problemen wenden Sie sich an das Shirtful WMS Team.

EXAMPLES:
  python main.py                    # Standard-Start
  python main.py --debug            # Mit Debug-Ausgabe
  python main.py --windowed         # Im Fenster (für Entwicklung)
  python main.py --check-deps       # Nur Abhängigkeiten prüfen

"""
    print(help_text)


def parse_arguments() -> argparse.Namespace:
    """
    Parst Kommandozeilen-Argumente.

    Returns:
        argparse.Namespace: Geparste Argumente
    """
    parser = argparse.ArgumentParser(
        description='Shirtful WMS - Wareneingang Station',
        add_help=False  # Eigene Hilfe implementieren
    )

    # Haupt-Optionen
    parser.add_argument(
        '-h', '--help',
        action='store_true',
        help='Zeigt erweiterte Hilfe an'
    )

    parser.add_argument(
        '-v', '--version',
        action='store_true',
        help='Zeigt Versionsinformationen an'
    )

    parser.add_argument(
        '-d', '--debug',
        action='store_true',
        help='Aktiviert Debug-Modus'
    )

    parser.add_argument(
        '-w', '--windowed',
        action='store_true',
        help='Startet im Fenster-Modus (nicht Vollbild)'
    )

    parser.add_argument(
        '--check-deps',
        action='store_true',
        help='Prüft nur Abhängigkeiten ohne Start'
    )

    parser.add_argument(
        '--safe-mode',
        action='store_true',
        help='Startet im Sicherheitsmodus'
    )

    # Versteckte Entwickler-Optionen
    parser.add_argument(
        '--dev-mode',
        action='store_true',
        help=argparse.SUPPRESS  # Versteckt
    )

    parser.add_argument(
        '--log-file',
        type=str,
        help=argparse.SUPPRESS  # Versteckt
    )

    return parser.parse_args()


def show_version_info():
    """Zeigt detaillierte Versionsinformationen an."""
    try:
        from . import __version__, get_module_info
        module_info = get_module_info()

        version_info = f"""
SHIRTFUL WMS - WARENEINGANG
===========================

Version:        {__version__}
Modul:          Wareneingang Station
Build:          {datetime.now().strftime('%Y%m%d')}

Python:         {sys.version.split()[0]}
Platform:       {sys.platform}
Architektur:    {os.name}

Komponenten:
"""

        for component in module_info.get('components', []):
            version_info += f"  • {component}\n"

        version_info += f"""
Features:
"""

        for feature in module_info.get('features', []):
            version_info += f"  • {feature}\n"

        print(version_info)

    except ImportError:
        print(f"""
SHIRTFUL WMS - WARENEINGANG
===========================

Version:        1.0.0
Python:         {sys.version.split()[0]}
Platform:       {sys.platform}

Hinweis: Detaillierte Informationen nicht verfügbar.
        """)


def check_dependencies_only():
    """Prüft nur Abhängigkeiten und beendet."""
    print("Prüfe Systemanforderungen und Abhängigkeiten...")
    print("=" * 60)

    requirements_met, issues = check_system_requirements()

    if requirements_met:
        print("✅ Alle Systemanforderungen erfüllt!")
        print("\nSystem bereit für Wareneingang-Anwendung.")
        return 0
    else:
        print("❌ Probleme erkannt:")
        print()

        critical_issues = [issue for issue in issues if "Kritisches" in issue or "Erforderliches" in issue]
        warnings = [issue for issue in issues if issue not in critical_issues]

        if critical_issues:
            print("KRITISCHE PROBLEME:")
            for issue in critical_issues:
                print(f"  • {issue}")
            print()

        if warnings:
            print("WARNUNGEN:")
            for warning in warnings:
                print(f"  • {warning}")
            print()

        if critical_issues:
            print("❌ Anwendung kann nicht gestartet werden.")
            return 1
        else:
            print("⚠️  Anwendung kann mit eingeschränkter Funktionalität gestartet werden.")
            return 0


def configure_app_settings(args: argparse.Namespace) -> dict:
    """
    Konfiguriert App-Einstellungen basierend auf Argumenten.

    Args:
        args: Kommandozeilen-Argumente

    Returns:
        dict: App-Konfiguration
    """
    config = {
        'debug_mode': args.debug,
        'fullscreen': not args.windowed,
        'safe_mode': args.safe_mode,
        'dev_mode': args.dev_mode if hasattr(args, 'dev_mode') else False
    }

    # Entwicklermodus-Einstellungen
    if config['dev_mode']:
        config['debug_mode'] = True
        config['fullscreen'] = False
        print("🔧 Entwicklermodus aktiviert")

    # Sicherheitsmodus-Einstellungen
    if config['safe_mode']:
        print("🛡️  Sicherheitsmodus aktiviert - eingeschränkte Features")

    return config


def main():
    """Haupteinstiegspunkt der Anwendung."""
    # Argumente parsen
    args = parse_arguments()

    # Hilfe anzeigen
    if args.help:
        print_help()
        return 0

    # Version anzeigen
    if args.version:
        show_version_info()
        return 0

    # Nur Abhängigkeiten prüfen
    if args.check_deps:
        return check_dependencies_only()

    # Startup-Banner anzeigen
    if not args.debug:
        print_startup_banner()

    # Logging einrichten
    logger = setup_logging(args.debug)

    try:
        logger.info("Starte Wareneingang-Anwendung...")

        # Systemanforderungen prüfen
        logger.info("Prüfe Systemanforderungen...")
        requirements_met, issues = check_system_requirements()

        if not requirements_met:
            critical_issues = [issue for issue in issues if "Kritisches" in issue or "Erforderliches" in issue]

            if critical_issues:
                logger.error("Kritische Systemanforderungen nicht erfüllt:")
                for issue in critical_issues:
                    logger.error(f"  - {issue}")

                print("\n❌ KRITISCHER FEHLER:")
                print("Erforderliche Systemanforderungen sind nicht erfüllt.")
                print("Bitte beheben Sie die folgenden Probleme:\n")

                for issue in critical_issues:
                    print(f"  • {issue}")

                print(f"\nVerwenden Sie 'python {sys.argv[0]} --check-deps' für Details.")
                return 1

            # Nur Warnungen - fortfahren
            logger.warning("Einige optionale Abhängigkeiten fehlen:")
            for issue in issues:
                logger.warning(f"  - {issue}")

            if not args.debug:
                print("⚠️  Einige Features sind möglicherweise nicht verfügbar.")
                print("Verwenden Sie --debug für Details.\n")

        # App-Konfiguration
        app_config = configure_app_settings(args)
        logger.info(f"App-Konfiguration: {app_config}")

        # Anwendung erstellen und starten
        logger.info("Erstelle Wareneingang-Anwendung...")
        app = WareneingangApp()

        # Konfiguration anwenden
        if not app_config['fullscreen']:
            # Windowed-Modus nach Initialisierung setzen
            if hasattr(app, 'root'):
                app.root.attributes('-fullscreen', False)
                app.root.geometry("1200x800")

        logger.info("Starte Anwendung...")
        app.run()

        logger.info("Anwendung normal beendet")
        return 0

    except KeyboardInterrupt:
        logger.info("Anwendung durch Benutzer unterbrochen (Strg+C)")
        print("\n\n⏹️  Anwendung durch Benutzer unterbrochen.")
        return 0

    except Exception as e:
        logger.critical(f"Kritischer Fehler: {e}", exc_info=True)

        print(f"\n❌ KRITISCHER FEHLER:")
        print(f"   {str(e)}")

        if args.debug:
            print("\nDetaillierte Fehlerinformationen:")
            import traceback
            traceback.print_exc()
        else:
            print("\nVerwenden Sie --debug für detaillierte Fehlerinformationen.")

        print("\nWenn das Problem weiterhin besteht, wenden Sie sich an den Support.")
        return 1

    except SystemExit as e:
        # Normale Beendigung über sys.exit()
        logger.info(f"Anwendung beendet mit Code: {e.code}")
        return e.code if e.code is not None else 0


if __name__ == "__main__":
    # Direkter Aufruf des Skripts
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        # Fallback für unerwartete Fehler
        print(f"\nKRITISCHER FEHLER beim Start: {e}")
        sys.exit(1)