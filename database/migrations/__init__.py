"""
Datenbank-Migrationen für Shirtful WMS
Verwaltung von Schema-Änderungen.
"""

import os
import glob
from pathlib import Path

# Migrations-Verzeichnis
MIGRATIONS_DIR = Path(__file__).parent


def get_migration_files():
    """
    Holt alle SQL-Migrationsdateien.

    Returns:
        Liste von Migrationsdateien sortiert nach Version
    """
    sql_files = glob.glob(os.path.join(MIGRATIONS_DIR, '*.sql'))
    # Nach Versionsnummer sortieren
    sql_files.sort()
    return sql_files


def get_migration_version(filename):
    """
    Extrahiert die Versionsnummer aus dem Dateinamen.

    Args:
        filename: Dateiname der Migration

    Returns:
        Versionsnummer als String
    """
    basename = os.path.basename(filename)
    # Format: 001_migration_name.sql
    version = basename.split('_')[0]
    return version


__all__ = ['get_migration_files', 'get_migration_version']