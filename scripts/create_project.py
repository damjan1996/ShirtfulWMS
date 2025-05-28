#!/usr/bin/env python3
"""
Shirtful Lagerverwaltungssystem - Projektstruktur Generator
Erstellt die komplette Verzeichnis- und Dateistruktur für das Projekt.
"""

import os
import sys
from pathlib import Path


def create_project_structure():
    """Erstellt die komplette Projektstruktur für das Shirtful WMS."""

    # Basis-Projektpfad
    base_path = Path(r"C:\Users\damja\PycharmProjects\Shirtful")

    # Verzeichnisstruktur definieren
    directories = [
        "apps",
        "utils",
        "config",
        "logs",
        "docs",
        "tests",
        "tests/unit",
        "tests/integration",
        "database",
        "database/migrations",
        "database/scripts",
        "resources",
        "resources/images",
        "resources/sounds",
        "resources/icons"
    ]

    # Dateien definieren (Pfad relativ zum base_path)
    files = [
        # Hauptverzeichnis
        "README.md",
        "requirements.txt",
        ".gitignore",
        "setup.py",
        "run_wareneingang.bat",
        "run_veredelung.bat",
        "run_betuchung.bat",
        "run_qualitaetskontrolle.bat",
        "run_warenausgang.bat",

        # Apps
        "apps/__init__.py",
        "apps/wareneingang.py",
        "apps/veredelung.py",
        "apps/betuchung.py",
        "apps/qualitaetskontrolle.py",
        "apps/warenausgang.py",

        # Utils
        "utils/__init__.py",
        "utils/rfid_auth.py",
        "utils/database.py",
        "utils/qr_scanner.py",
        "utils/ui_components.py",
        "utils/logger.py",
        "utils/helpers.py",
        "utils/constants.py",

        # Config
        "config/__init__.py",
        "config/settings.py",
        "config/translations.py",
        "config/database_config.py",
        "config/rfid_config.py",

        # Logs
        "logs/.gitkeep",

        # Docs
        "docs/installation.md",
        "docs/user_manual.md",
        "docs/api_documentation.md",
        "docs/database_schema.md",

        # Tests
        "tests/__init__.py",
        "tests/conftest.py",
        "tests/unit/__init__.py",
        "tests/unit/test_rfid_auth.py",
        "tests/unit/test_database.py",
        "tests/unit/test_qr_scanner.py",
        "tests/integration/__init__.py",
        "tests/integration/test_wareneingang.py",

        # Database
        "database/__init__.py",
        "database/schema.sql",
        "database/sample_data.sql",
        "database/migrations/__init__.py",
        "database/migrations/001_initial_schema.sql",
        "database/scripts/create_database.py",
        "database/scripts/backup_database.py",

        # Resources
        "resources/.gitkeep",
        "resources/images/.gitkeep",
        "resources/sounds/success.wav",
        "resources/sounds/error.wav",
        "resources/sounds/scan.wav",
        "resources/icons/.gitkeep"
    ]

    print("=" * 60)
    print("Shirtful WMS - Projektstruktur Generator")
    print("=" * 60)
    print(f"\nZielverzeichnis: {base_path}")
    print("\nErstelle Projektstruktur...\n")

    # Hauptverzeichnis erstellen
    try:
        base_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Hauptverzeichnis erstellt: {base_path}")
    except Exception as e:
        print(f"✗ Fehler beim Erstellen des Hauptverzeichnisses: {e}")
        return False

    # Unterverzeichnisse erstellen
    print("\nErstelle Verzeichnisse:")
    for directory in directories:
        dir_path = base_path / directory
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"  ✓ {directory}")
        except Exception as e:
            print(f"  ✗ {directory} - Fehler: {e}")

    # Dateien erstellen
    print("\nErstelle Dateien:")
    for file in files:
        file_path = base_path / file
        try:
            # Stelle sicher, dass das Verzeichnis existiert
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Erstelle die Datei nur wenn sie noch nicht existiert
            if not file_path.exists():
                file_path.touch()
                print(f"  ✓ {file}")
            else:
                print(f"  ⚠ {file} (existiert bereits)")
        except Exception as e:
            print(f"  ✗ {file} - Fehler: {e}")

    # Zusätzliche Konfigurationsdateien mit Basis-Inhalt erstellen
    print("\nErstelle Konfigurationsdateien mit Basis-Inhalt:")

    # .gitignore
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Logs
logs/*.log
*.log

# Database
*.db
*.sqlite
*.sqlite3

# Config
config/local_settings.py

# OS
.DS_Store
Thumbs.db

# Test coverage
.coverage
htmlcov/
.pytest_cache/

# Distribution
dist/
build/
*.egg-info/
"""

    try:
        gitignore_path = base_path / ".gitignore"
        gitignore_path.write_text(gitignore_content, encoding='utf-8')
        print(f"  ✓ .gitignore (mit Inhalt)")
    except Exception as e:
        print(f"  ✗ .gitignore - Fehler: {e}")

    # VS Code Workspace-Einstellungen
    vscode_dir = base_path / ".vscode"
    try:
        vscode_dir.mkdir(exist_ok=True)
        settings_path = vscode_dir / "settings.json"
        settings_content = """{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "python.testing.nosetestsEnabled": false,
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true
    }
}"""
        settings_path.write_text(settings_content, encoding='utf-8')
        print(f"  ✓ .vscode/settings.json (mit VS Code Einstellungen)")
    except Exception as e:
        print(f"  ✗ .vscode/settings.json - Fehler: {e}")

    print("\n" + "=" * 60)
    print("✓ Projektstruktur erfolgreich erstellt!")
    print("=" * 60)

    # Zusammenfassung
    print("\nNächste Schritte:")
    print("1. Öffne das Projekt in PyCharm: " + str(base_path))
    print("2. Erstelle eine virtuelle Umgebung: python -m venv venv")
    print("3. Aktiviere die virtuelle Umgebung: venv\\Scripts\\activate")
    print("4. Installiere die Abhängigkeiten: pip install -r requirements.txt")
    print("\nHinweis: Alle Dateien wurden leer erstellt.")
    print("Die Implementierung erfolgt in den nächsten Schritten.")

    return True


def main():
    """Hauptfunktion."""
    try:
        success = create_project_structure()
        if success:
            print("\n✅ Projekt-Setup abgeschlossen!")
            sys.exit(0)
        else:
            print("\n❌ Fehler beim Projekt-Setup!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠ Vorgang abgebrochen!")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unerwarteter Fehler: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()