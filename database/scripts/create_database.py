#!/usr/bin/env python3
"""
Datenbank-Erstellungsscript für Shirtful WMS
Erstellt die Datenbank und führt initiale Migrationen aus.
"""

import os
import sys
import pyodbc
import logging
import argparse
from pathlib import Path

# Projekt-Root zum Python-Path hinzufügen
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.database_config import (
    get_connection_string, DB_CONFIG, CREATE_TABLES_SQL,
    INSERT_DEFAULT_DATA_SQL, CREATE_VIEWS_SQL, CREATE_PROCEDURES_SQL
)
from database.migrations import get_migration_files, get_migration_version
from utils.logger import setup_logger


class DatabaseCreator:
    """Klasse zum Erstellen und Initialisieren der Datenbank."""

    def __init__(self):
        """Initialisiert den Database Creator."""
        self.logger = setup_logger('database_creator')
        self.database_name = DB_CONFIG['database']
        self.server = DB_CONFIG['server']

    def database_exists(self) -> bool:
        """
        Prüft ob die Datenbank bereits existiert.

        Returns:
            True wenn Datenbank existiert
        """
        try:
            # Verbindung zu master DB
            conn_str = get_connection_string()
            conn_str = conn_str.replace(f"DATABASE={self.database_name}", "DATABASE=master")

            with pyodbc.connect(conn_str) as conn:
                cursor = conn.cursor()
                cursor.execute(f"""
                    SELECT name FROM sys.databases 
                    WHERE name = '{self.database_name}'
                """)

                return cursor.fetchone() is not None

        except Exception as e:
            self.logger.error(f"Fehler bei Datenbankprüfung: {e}")
            return False

    def create_database(self, drop_if_exists: bool = False) -> bool:
        """
        Erstellt die Datenbank.

        Args:
            drop_if_exists: Existierende DB löschen

        Returns:
            True bei Erfolg
        """
        try:
            # Verbindung zu master DB
            conn_str = get_connection_string()
            conn_str = conn_str.replace(f"DATABASE={self.database_name}", "DATABASE=master")

            with pyodbc.connect(conn_str, autocommit=True) as conn:
                cursor = conn.cursor()

                # Prüfen ob DB existiert
                if self.database_exists():
                    if drop_if_exists:
                        self.logger.warning(f"Lösche existierende Datenbank {self.database_name}")

                        # Verbindungen trennen
                        cursor.execute(f"""
                        ALTER DATABASE [{self.database_name}] 
                        SET SINGLE_USER WITH ROLLBACK IMMEDIATE
                        """)

                        # Datenbank löschen
                        cursor.execute(f"DROP DATABASE [{self.database_name}]")
                        self.logger.info("Datenbank gelöscht")
                    else:
                        self.logger.info("Datenbank existiert bereits")
                        return True

                # Datenbank erstellen
                self.logger.info(f"Erstelle Datenbank {self.database_name}")
                cursor.execute(f"CREATE DATABASE [{self.database_name}]")

                # Einstellungen
                cursor.execute(f"""
                ALTER DATABASE [{self.database_name}] SET RECOVERY SIMPLE;
                ALTER DATABASE [{self.database_name}] SET AUTO_SHRINK OFF;
                ALTER DATABASE [{self.database_name}] SET AUTO_CREATE_STATISTICS ON;
                ALTER DATABASE [{self.database_name}] SET AUTO_UPDATE_STATISTICS ON;
                """)

                self.logger.info("Datenbank erfolgreich erstellt")
                return True

        except Exception as e:
            self.logger.error(f"Fehler beim Erstellen der Datenbank: {e}")
            return False

    def create_tables(self) -> bool:
        """
        Erstellt alle Tabellen.

        Returns:
            True bei Erfolg
        """
        try:
            with pyodbc.connect(get_connection_string()) as conn:
                cursor = conn.cursor()

                self.logger.info("Erstelle Tabellen...")

                # SQL in einzelne Statements aufteilen
                statements = CREATE_TABLES_SQL.split('GO')

                for statement in statements:
                    if statement.strip():
                        try:
                            cursor.execute(statement)
                            conn.commit()
                        except pyodbc.Error as e:
                            if "already exists" not in str(e):
                                self.logger.error(f"Fehler bei Statement: {e}")
                                raise

                self.logger.info("Tabellen erfolgreich erstellt")
                return True

        except Exception as e:
            self.logger.error(f"Fehler beim Erstellen der Tabellen: {e}")
            return False

    def create_views(self) -> bool:
        """
        Erstellt alle Views.

        Returns:
            True bei Erfolg
        """
        try:
            with pyodbc.connect(get_connection_string(), autocommit=True) as conn:
                cursor = conn.cursor()

                self.logger.info("Erstelle Views...")

                # SQL in einzelne Statements aufteilen
                statements = CREATE_VIEWS_SQL.split('GO')

                for statement in statements:
                    if statement.strip():
                        try:
                            cursor.execute(statement)
                        except pyodbc.Error as e:
                            self.logger.warning(f"View-Fehler (wird ignoriert): {e}")

                self.logger.info("Views erstellt")
                return True

        except Exception as e:
            self.logger.error(f"Fehler beim Erstellen der Views: {e}")
            return False

    def create_procedures(self) -> bool:
        """
        Erstellt alle Stored Procedures.

        Returns:
            True bei Erfolg
        """
        try:
            with pyodbc.connect(get_connection_string(), autocommit=True) as conn:
                cursor = conn.cursor()

                self.logger.info("Erstelle Stored Procedures...")

                # SQL in einzelne Statements aufteilen
                statements = CREATE_PROCEDURES_SQL.split('GO')

                for statement in statements:
                    if statement.strip():
                        try:
                            cursor.execute(statement)
                        except pyodbc.Error as e:
                            self.logger.warning(f"Procedure-Fehler (wird ignoriert): {e}")

                self.logger.info("Stored Procedures erstellt")
                return True

        except Exception as e:
            self.logger.error(f"Fehler beim Erstellen der Procedures: {e}")
            return False

    def insert_default_data(self) -> bool:
        """
        Fügt Standarddaten ein.

        Returns:
            True bei Erfolg
        """
        try:
            with pyodbc.connect(get_connection_string()) as conn:
                cursor = conn.cursor()

                self.logger.info("Füge Standarddaten ein...")

                # SQL in einzelne Statements aufteilen
                statements = INSERT_DEFAULT_DATA_SQL.split('GO')

                for statement in statements:
                    if statement.strip():
                        try:
                            cursor.execute(statement)
                            conn.commit()
                        except pyodbc.Error as e:
                            if "Violation of UNIQUE KEY" not in str(e):
                                self.logger.error(f"Fehler bei Daten: {e}")

                self.logger.info("Standarddaten eingefügt")
                return True

        except Exception as e:
            self.logger.error(f"Fehler beim Einfügen der Daten: {e}")
            return False

    def run_migrations(self) -> bool:
        """
        Führt alle Migrationen aus.

        Returns:
            True bei Erfolg
        """
        try:
            migration_files = get_migration_files()

            if not migration_files:
                self.logger.info("Keine Migrationen gefunden")
                return True

            with pyodbc.connect(get_connection_string(), autocommit=True) as conn:
                cursor = conn.cursor()

                # Migration-Tracking-Tabelle prüfen
                cursor.execute("""
                    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='DatabaseMigrations' AND xtype='U')
                    BEGIN
                        CREATE TABLE DatabaseMigrations (
                            MigrationID INT IDENTITY(1,1) PRIMARY KEY,
                            Version VARCHAR(50) NOT NULL UNIQUE,
                            Description NVARCHAR(200),
                            AppliedAt DATETIME DEFAULT GETDATE(),
                            AppliedBy NVARCHAR(100) DEFAULT SYSTEM_USER
                        );
                    END
                """)

                for migration_file in migration_files:
                    version = get_migration_version(migration_file)

                    # Prüfen ob bereits angewendet
                    cursor.execute(
                        "SELECT Version FROM DatabaseMigrations WHERE Version = ?",
                        version
                    )

                    if cursor.fetchone():
                        self.logger.info(f"Migration {version} bereits angewendet")
                        continue

                    # Migration ausführen
                    self.logger.info(f"Führe Migration {version} aus...")

                    with open(migration_file, 'r', encoding='utf-8') as f:
                        migration_sql = f.read()

                    # In Statements aufteilen
                    statements = migration_sql.split('GO')

                    for statement in statements:
                        if statement.strip():
                            cursor.execute(statement)

                    self.logger.info(f"Migration {version} erfolgreich")

                return True

        except Exception as e:
            self.logger.error(f"Fehler bei Migrationen: {e}")
            return False

    def verify_database(self) -> bool:
        """
        Verifiziert die Datenbankstruktur.

        Returns:
            True wenn alles OK
        """
        required_tables = [
            'Employees', 'Deliveries', 'Packages', 'PackageHistory',
            'TimeTracking', 'QualityIssues', 'Settings', 'AuditLog'
        ]

        try:
            with pyodbc.connect(get_connection_string()) as conn:
                cursor = conn.cursor()

                self.logger.info("Verifiziere Datenbankstruktur...")

                missing_tables = []

                for table in required_tables:
                    cursor.execute(f"""
                        SELECT name FROM sysobjects 
                        WHERE name = '{table}' AND xtype = 'U'
                    """)

                    if not cursor.fetchone():
                        missing_tables.append(table)

                if missing_tables:
                    self.logger.error(f"Fehlende Tabellen: {', '.join(missing_tables)}")
                    return False

                # Prüfe ob Admin-User existiert
                cursor.execute("SELECT * FROM Employees WHERE RFIDTag = 'ADMIN001'")
                if not cursor.fetchone():
                    self.logger.warning("Admin-User fehlt")

                self.logger.info("Datenbankstruktur OK")
                return True

        except Exception as e:
            self.logger.error(f"Fehler bei Verifikation: {e}")
            return False

    def create_full_database(self, drop_if_exists: bool = False) -> bool:
        """
        Erstellt die komplette Datenbank mit allen Objekten.

        Args:
            drop_if_exists: Existierende DB löschen

        Returns:
            True bei Erfolg
        """
        self.logger.info("=== Starte Datenbank-Setup ===")

        # 1. Datenbank erstellen
        if not self.create_database(drop_if_exists):
            return False

        # 2. Tabellen erstellen
        if not self.create_tables():
            return False

        # 3. Views erstellen
        self.create_views()  # Fehler werden ignoriert

        # 4. Stored Procedures erstellen
        self.create_procedures()  # Fehler werden ignoriert

        # 5. Standarddaten einfügen
        if not self.insert_default_data():
            return False

        # 6. Migrationen ausführen
        self.run_migrations()

        # 7. Verifizieren
        if not self.verify_database():
            self.logger.warning("Verifikation fehlgeschlagen, aber Setup fortgesetzt")

        self.logger.info("=== Datenbank-Setup abgeschlossen ===")
        return True


def main():
    """Hauptfunktion für Kommandozeilen-Nutzung."""
    parser = argparse.ArgumentParser(description='Shirtful WMS Datenbank erstellen')
    parser.add_argument('--drop', action='store_true',
                        help='Existierende Datenbank löschen')
    parser.add_argument('--verify-only', action='store_true',
                        help='Nur Struktur verifizieren')
    parser.add_argument('--tables-only', action='store_true',
                        help='Nur Tabellen erstellen')
    parser.add_argument('--data-only', action='store_true',
                        help='Nur Daten einfügen')

    args = parser.parse_args()

    creator = DatabaseCreator()

    try:
        if args.verify_only:
            # Nur verifizieren
            if creator.verify_database():
                print("✓ Datenbankstruktur OK")
            else:
                print("✗ Datenbankstruktur fehlerhaft")
                sys.exit(1)

        elif args.tables_only:
            # Nur Tabellen
            if creator.create_tables():
                print("✓ Tabellen erstellt")
            else:
                print("✗ Fehler beim Erstellen der Tabellen")
                sys.exit(1)

        elif args.data_only:
            # Nur Daten
            if creator.insert_default_data():
                print("✓ Daten eingefügt")
            else:
                print("✗ Fehler beim Einfügen der Daten")
                sys.exit(1)

        else:
            # Komplettes Setup
            print(f"Erstelle Datenbank '{creator.database_name}' auf Server '{creator.server}'")

            if creator.database_exists() and not args.drop:
                print("Datenbank existiert bereits. Verwenden Sie --drop zum Überschreiben.")
                sys.exit(1)

            if creator.create_full_database(args.drop):
                print("\n✓ Datenbank erfolgreich erstellt!")
                print(f"\nVerbindungsdetails:")
                print(f"  Server: {creator.server}")
                print(f"  Datenbank: {creator.database_name}")
                print(f"  Authentifizierung: Windows")
            else:
                print("\n✗ Fehler beim Erstellen der Datenbank")
                sys.exit(1)

    except Exception as e:
        print(f"\n✗ Kritischer Fehler: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()