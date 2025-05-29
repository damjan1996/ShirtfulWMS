#!/usr/bin/env python3
"""
Shirtful WMS - Wareneingang Module
Modulare Wareneingang-Anwendung für das Shirtful Lagerverwaltungssystem.

Dieses Modul stellt eine vollständige Wareneingang-Station bereit mit:
- RFID-basierter Mitarbeiter-Authentifizierung
- QR-Code-Scanning für Pakete
- Lieferungsverwaltung
- Paket-Registrierung
- Benutzerfreundliche Touch-Oberfläche

Version: 1.0.0
Autor: Shirtful WMS Team
Erstellt: 2024
"""

from .app import WareneingangApp
from .main import main

# Version des Wareneingang-Moduls
__version__ = "1.0.0"

# Modul-Metadaten
__title__ = "Shirtful WMS - Wareneingang"
__description__ = "Modulare Wareneingang-Anwendung mit RFID und QR-Code Unterstützung"
__author__ = "Shirtful WMS Team"
__email__ = "support@shirtful.com"
__license__ = "Proprietary"

# Verfügbare Klassen und Funktionen exportieren
__all__ = [
    'WareneingangApp',
    'main',
    '__version__',
    '__title__',
    '__description__'
]

# Logging-Konfiguration für das Modul
import logging
import sys
import os

# Logger für das gesamte Wareneingang-Modul
module_logger = logging.getLogger(__name__)


def setup_module_logging():
    """
    Richtet das Logging für das Wareneingang-Modul ein.
    """
    try:
        # Logger-Level setzen
        module_logger.setLevel(logging.INFO)

        # Handler nur hinzufügen falls noch nicht vorhanden
        if not module_logger.handlers:
            # Console Handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)

            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)

            # Handler hinzufügen
            module_logger.addHandler(console_handler)

        module_logger.info(f"Wareneingang-Modul v{__version__} initialisiert")

    except Exception as e:
        print(f"Warnung: Logging-Setup fehlgeschlagen: {e}")


# Automatisches Logging-Setup beim Import
setup_module_logging()


# Modul-Initialisierung
def get_module_info():
    """
    Gibt Informationen über das Wareneingang-Modul zurück.

    Returns:
        dict: Modul-Informationen
    """
    return {
        'name': __title__,
        'version': __version__,
        'description': __description__,
        'author': __author__,
        'components': [
            'WareneingangApp - Hauptanwendung',
            'LoginScreen - RFID-Authentifizierung',
            'MainScreen - Hauptbildschirm',
            'DeliveryDialog - Lieferungsverwaltung',
            'ScannerDialog - QR-Code Scanner',
            'PackageRegistrationDialog - Paket-Registrierung'
        ],
        'features': [
            'RFID-Mitarbeiter-Login',
            'QR-Code Paket-Scanning',
            'Lieferungsverwaltung',
            'Paket-Registrierung',
            'Mehrsprachige Oberfläche',
            'Touch-optimierte UI',
            'Statistiken und Berichte',
            'Export-Funktionen'
        ],
        'requirements': [
            'Python 3.10+',
            'tkinter (Standard)',
            'pyodbc (MSSQL)',
            'pyserial (RFID)',
            'opencv-python (QR-Scanner)',
            'pyzbar (QR-Dekodierung)'
        ]
    }


def check_dependencies():
    """
    Prüft ob alle erforderlichen Abhängigkeiten verfügbar sind.

    Returns:
        tuple: (all_available, missing_deps, available_deps)
    """
    dependencies = {
        'tkinter': 'Standard GUI Framework',
        'pyodbc': 'MSSQL Datenbankverbindung',
        'serial': 'RFID-Reader Kommunikation',
        'cv2': 'QR-Code Kamera-Scanning',
        'pyzbar': 'QR-Code Dekodierung'
    }

    available = []
    missing = []

    for dep_name, description in dependencies.items():
        try:
            __import__(dep_name)
            available.append((dep_name, description, True))
            module_logger.debug(f"Abhängigkeit verfügbar: {dep_name}")
        except ImportError:
            missing.append((dep_name, description, False))
            module_logger.warning(f"Abhängigkeit fehlt: {dep_name} - {description}")

    all_available = len(missing) == 0

    if all_available:
        module_logger.info("Alle Abhängigkeiten verfügbar")
    else:
        module_logger.warning(f"{len(missing)} Abhängigkeiten fehlen")

    return all_available, missing, available


def validate_environment():
    """
    Validiert die Umgebung für die Wareneingang-Anwendung.

    Returns:
        tuple: (is_valid, issues, recommendations)
    """
    issues = []
    recommendations = []

    # Python-Version prüfen
    if sys.version_info < (3, 10):
        issues.append(f"Python-Version {sys.version} < 3.10")
        recommendations.append("Aktualisieren Sie auf Python 3.10 oder höher")

    # Abhängigkeiten prüfen
    all_deps_available, missing_deps, _ = check_dependencies()
    if not all_deps_available:
        for dep_name, description, _ in missing_deps:
            issues.append(f"Fehlende Abhängigkeit: {dep_name}")
            recommendations.append(f"Installieren Sie {dep_name}: pip install {dep_name}")

    # Pfad-Struktur prüfen
    current_dir = os.path.dirname(__file__)
    required_dirs = ['ui', 'models', 'services', 'config']

    for req_dir in required_dirs:
        dir_path = os.path.join(current_dir, req_dir)
        if not os.path.exists(dir_path):
            issues.append(f"Fehlender Ordner: {req_dir}")
            recommendations.append(f"Erstellen Sie den Ordner: {dir_path}")

    # Utils-Modul prüfen
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(current_dir)))
        import utils
        module_logger.debug("Utils-Modul verfügbar")
    except ImportError:
        issues.append("Utils-Modul nicht verfügbar")
        recommendations.append("Stellen Sie sicher, dass das utils/ Verzeichnis existiert")

    is_valid = len(issues) == 0

    if is_valid:
        module_logger.info("Umgebungsvalidierung erfolgreich")
    else:
        module_logger.error(f"Umgebungsvalidierung fehlgeschlagen: {len(issues)} Probleme")

    return is_valid, issues, recommendations


# Umgebung beim Import validieren
try:
    is_env_valid, env_issues, env_recommendations = validate_environment()

    if not is_env_valid:
        module_logger.warning("Umgebungsprobleme erkannt")
        for issue in env_issues[:3]:  # Nur erste 3 Probleme loggen
            module_logger.warning(f"  - {issue}")

        if len(env_issues) > 3:
            module_logger.warning(f"  - ... und {len(env_issues) - 3} weitere")

except Exception as e:
    module_logger.error(f"Fehler bei Umgebungsvalidierung: {e}")


# Utility-Funktionen für externe Verwendung
def create_app(**kwargs):
    """
    Factory-Funktion zum Erstellen einer Wareneingang-App Instanz.

    Args:
        **kwargs: Optionale Parameter für die App-Konfiguration

    Returns:
        WareneingangApp: Neue App-Instanz
    """
    try:
        module_logger.info("Erstelle neue Wareneingang-App Instanz")
        app = WareneingangApp(**kwargs)
        return app
    except Exception as e:
        module_logger.error(f"Fehler beim Erstellen der App: {e}")
        raise


def run_app(**kwargs):
    """
    Convenience-Funktion zum direkten Starten der Anwendung.

    Args:
        **kwargs: Optionale Parameter für die App-Konfiguration
    """
    try:
        module_logger.info("Starte Wareneingang-Anwendung")
        app = create_app(**kwargs)
        app.run()
    except Exception as e:
        module_logger.error(f"Fehler beim Starten der App: {e}")
        raise


def get_version():
    """
    Gibt die Version des Wareneingang-Moduls zurück.

    Returns:
        str: Version
    """
    return __version__


# Modul-Informationen beim Import anzeigen
module_logger.info(f"Wareneingang-Modul geladen: {__title__} v{__version__}")
module_logger.debug(f"Modul-Pfad: {os.path.dirname(__file__)}")

# Entwicklungsmodus erkennen
if __name__ == "__main__":
    # Direkte Ausführung des Moduls für Debugging
    print(f"=== {__title__} v{__version__} ===")
    print()

    # Modul-Informationen anzeigen
    info = get_module_info()
    print("Modul-Informationen:")
    for key, value in info.items():
        if isinstance(value, list):
            print(f"  {key}:")
            for item in value:
                print(f"    - {item}")
        else:
            print(f"  {key}: {value}")
    print()

    # Umgebung prüfen
    is_valid, issues, recommendations = validate_environment()

    print("Umgebungsvalidierung:")
    if is_valid:
        print("  ✅ Alle Prüfungen bestanden")
    else:
        print("  ❌ Probleme erkannt:")
        for issue in issues:
            print(f"    - {issue}")
        print()
        print("  Empfehlungen:")
        for rec in recommendations:
            print(f"    - {rec}")
    print()

    # Abhängigkeiten anzeigen
    all_deps, missing, available = check_dependencies()

    print("Abhängigkeiten:")
    for name, desc, is_available in available:
        print(f"  ✅ {name}: {desc}")

    for name, desc, is_available in missing:
        print(f"  ❌ {name}: {desc}")

    if missing:
        print()
        print("Fehlende Abhängigkeiten installieren:")
        for name, _, _ in missing:
            if name == 'cv2':
                print(f"  pip install opencv-python")
            elif name == 'serial':
                print(f"  pip install pyserial")
            else:
                print(f"  pip install {name}")

    print()
    print("Zum Starten der Anwendung:")
    print("  python main.py")
    print("  # oder")
    print("  python -m wareneingang")