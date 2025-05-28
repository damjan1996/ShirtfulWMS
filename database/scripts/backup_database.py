#!/usr/bin/env python3
"""
Datenbank-Backup Script für Shirtful WMS
Erstellt automatische Backups der SQL Server Datenbank.
"""

import os
import sys
import pyodbc
import logging
import argparse
from datetime import datetime
from pathlib import Path
import zipfile
import shutil

# Projekt-Root zum Python-Path hinzufügen
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.database_config import get_connection_string, DB_CONFIG
from utils.logger import setup_logger


class DatabaseBackup:
    """Klasse für Datenbank-Backups."""

    def __init__(self, backup_dir: str = None):
        """
        Initialisiert das Backup-System.

        Args:
            backup_dir: Backup-Verzeichnis (Standard aus Config)
        """
        self.logger = setup_logger('database_backup')
        self.backup_dir = Path(backup_dir or DB_CONFIG.get('backup_dir', 'C:\\Backups\\ShirtfulWMS'))
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self, database_name: str = None, compress: bool = True) -> str:
        """
        Erstellt ein Datenbank-Backup.

        Args:
            database_name: Name der Datenbank (Standard aus Config)
            compress: Backup komprimieren

        Returns:
            Pfad zur Backup-Datei
        """
        database_name = database_name or DB_CONFIG['database']
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Backup-Dateiname
        backup_filename = f"{database_name}_backup_{timestamp}.bak"
        backup_path = self.backup_dir / backup_filename

        self.logger.info(f"Starte Backup von {database_name}")

        try:
            # Verbindung zur master-Datenbank
            conn_str = get_connection_string()
            # master-DB verwenden für Backup-Befehle
            conn_str = conn_str.replace(f"DATABASE={database_name}", "DATABASE=master")

            with pyodbc.connect(conn_str, autocommit=True) as conn:
                cursor = conn.cursor()

                # Backup-Befehl
                backup_sql = f"""
                BACKUP DATABASE [{database_name}]
                TO DISK = N'{backup_path}'
                WITH FORMAT,
                     INIT,
                     NAME = N'{database_name}-Full Database Backup',
                     SKIP,
                     NOREWIND,
                     NOUNLOAD,
                     COMPRESSION,
                     STATS = 10
                """

                self.logger.info(f"Führe Backup aus: {backup_path}")
                cursor.execute(backup_sql)

                self.logger.info("Backup erfolgreich erstellt")

                # Optional komprimieren
                if compress:
                    zip_path = self._compress_backup(backup_path)
                    # Original löschen
                    backup_path.unlink()
                    return str(zip_path)

                return str(backup_path)

        except Exception as e:
            self.logger.error(f"Backup fehlgeschlagen: {e}")
            raise

    def _compress_backup(self, backup_path: Path) -> Path:
        """
        Komprimiert eine Backup-Datei.

        Args:
            backup_path: Pfad zur Backup-Datei

        Returns:
            Pfad zur ZIP-Datei
        """
        zip_path = backup_path.with_suffix('.zip')

        self.logger.info(f"Komprimiere Backup: {zip_path.name}")

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(backup_path, backup_path.name)

        self.logger.info(f"Komprimierung abgeschlossen")

        return zip_path

    def restore_backup(self, backup_file: str, database_name: str = None,
                       replace_existing: bool = False):
        """
        Stellt eine Datenbank aus Backup wieder her.

        Args:
            backup_file: Pfad zur Backup-Datei
            database_name: Ziel-Datenbankname
            replace_existing: Existierende DB überschreiben
        """
        backup_path = Path(backup_file)

        if not backup_path.exists():
            raise FileNotFoundError(f"Backup-Datei nicht gefunden: {backup_file}")

        # ZIP entpacken wenn nötig
        if backup_path.suffix == '.zip':
            backup_path = self._extract_backup(backup_path)

        database_name = database_name or DB_CONFIG['database']

        self.logger.info(f"Stelle Datenbank {database_name} wieder her")

        try:
            conn_str = get_connection_string()
            conn_str = conn_str.replace(f"DATABASE={database_name}", "DATABASE=master")

            with pyodbc.connect(conn_str, autocommit=True) as conn:
                cursor = conn.cursor()

                # Bestehende Verbindungen trennen wenn Replace
                if replace_existing:
                    cursor.execute(f"""
                    IF EXISTS (SELECT name FROM sys.databases WHERE name = '{database_name}')
                    BEGIN
                        ALTER DATABASE [{database_name}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
                    END
                    """)

                # Restore-Befehl
                restore_sql = f"""
                RESTORE DATABASE [{database_name}]
                FROM DISK = N'{backup_path}'
                WITH FILE = 1,
                     {"REPLACE," if replace_existing else ""}
                     NOUNLOAD,
                     STATS = 10
                """

                cursor.execute(restore_sql)

                # Multi-User wieder aktivieren
                cursor.execute(f"ALTER DATABASE [{database_name}] SET MULTI_USER;")

                self.logger.info("Wiederherstellung erfolgreich")

        except Exception as e:
            self.logger.error(f"Wiederherstellung fehlgeschlagen: {e}")
            raise

    def _extract_backup(self, zip_path: Path) -> Path:
        """
        Entpackt eine komprimierte Backup-Datei.

        Args:
            zip_path: Pfad zur ZIP-Datei

        Returns:
            Pfad zur entpackten BAK-Datei
        """
        extract_dir = zip_path.parent / 'temp'
        extract_dir.mkdir(exist_ok=True)

        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(extract_dir)

        # BAK-Datei finden
        bak_files = list(extract_dir.glob('*.bak'))
        if bak_files:
            return bak_files[0]
        else:
            raise FileNotFoundError("Keine BAK-Datei im Archiv gefunden")

    def list_backups(self) -> list:
        """
        Listet alle verfügbaren Backups auf.

        Returns:
            Liste von Backup-Dateien mit Infos
        """
        backups = []

        for file in self.backup_dir.glob('*.bak'):
            backups.append({
                'file': file.name,
                'path': str(file),
                'size': file.stat().st_size,
                'created': datetime.fromtimestamp(file.stat().st_ctime),
                'type': 'uncompressed'
            })

        for file in self.backup_dir.glob('*.zip'):
            backups.append({
                'file': file.name,
                'path': str(file),
                'size': file.stat().st_size,
                'created': datetime.fromtimestamp(file.stat().st_ctime),
                'type': 'compressed'
            })

        # Nach Datum sortieren
        backups.sort(key=lambda x: x['created'], reverse=True)

        return backups

    def cleanup_old_backups(self, keep_days: int = 30):
        """
        Löscht alte Backup-Dateien.

        Args:
            keep_days: Backups behalten für X Tage
        """
        cutoff_time = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)
        deleted_count = 0

        self.logger.info(f"Lösche Backups älter als {keep_days} Tage")

        for file in self.backup_dir.glob('*'):
            if file.suffix in ['.bak', '.zip']:
                if file.stat().st_ctime < cutoff_time:
                    try:
                        file.unlink()
                        deleted_count += 1
                        self.logger.info(f"Gelöscht: {file.name}")
                    except Exception as e:
                        self.logger.error(f"Fehler beim Löschen von {file.name}: {e}")

        self.logger.info(f"{deleted_count} alte Backups gelöscht")

    def verify_backup(self, backup_file: str) -> bool:
        """
        Verifiziert eine Backup-Datei.

        Args:
            backup_file: Pfad zur Backup-Datei

        Returns:
            True wenn Backup gültig
        """
        backup_path = Path(backup_file)

        if not backup_path.exists():
            return False

        try:
            conn_str = get_connection_string()
            conn_str = conn_str.replace(f"DATABASE={DB_CONFIG['database']}", "DATABASE=master")

            with pyodbc.connect(conn_str) as conn:
                cursor = conn.cursor()

                # VERIFYONLY prüft Backup ohne Restore
                verify_sql = f"""
                RESTORE VERIFYONLY
                FROM DISK = N'{backup_path}'
                """

                cursor.execute(verify_sql)

                self.logger.info(f"Backup {backup_path.name} ist gültig")
                return True

        except Exception as e:
            self.logger.error(f"Backup-Verifikation fehlgeschlagen: {e}")
            return False


def main():
    """Hauptfunktion für Kommandozeilen-Nutzung."""
    parser = argparse.ArgumentParser(description='Shirtful WMS Datenbank-Backup')
    parser.add_argument('action', choices=['backup', 'restore', 'list', 'cleanup', 'verify'],
                        help='Auszuführende Aktion')
    parser.add_argument('--database', help='Datenbankname')
    parser.add_argument('--file', help='Backup-Datei (für restore/verify)')
    parser.add_argument('--compress', action='store_true', help='Backup komprimieren')
    parser.add_argument('--replace', action='store_true', help='Existierende DB überschreiben')
    parser.add_argument('--keep-days', type=int, default=30, help='Tage für Cleanup')
    parser.add_argument('--backup-dir', help='Backup-Verzeichnis')

    args = parser.parse_args()

    # Backup-Manager initialisieren
    backup = DatabaseBackup(args.backup_dir)

    try:
        if args.action == 'backup':
            # Backup erstellen
            backup_file = backup.create_backup(args.database, args.compress)
            print(f"Backup erstellt: {backup_file}")

        elif args.action == 'restore':
            # Backup wiederherstellen
            if not args.file:
                print("Fehler: --file erforderlich für restore")
                sys.exit(1)

            backup.restore_backup(args.file, args.database, args.replace)
            print("Wiederherstellung erfolgreich")

        elif args.action == 'list':
            # Backups auflisten
            backups = backup.list_backups()

            if backups:
                print(f"\nVerfügbare Backups in {backup.backup_dir}:")
                print("-" * 80)
                print(f"{'Datei':<40} {'Größe':>10} {'Erstellt':<20} {'Typ':<10}")
                print("-" * 80)

                for b in backups:
                    size_mb = b['size'] / (1024 * 1024)
                    created = b['created'].strftime('%Y-%m-%d %H:%M:%S')
                    print(f"{b['file']:<40} {size_mb:>9.1f}M {created:<20} {b['type']:<10}")
            else:
                print("Keine Backups gefunden")

        elif args.action == 'cleanup':
            # Alte Backups löschen
            backup.cleanup_old_backups(args.keep_days)

        elif args.action == 'verify':
            # Backup verifizieren
            if not args.file:
                print("Fehler: --file erforderlich für verify")
                sys.exit(1)

            if backup.verify_backup(args.file):
                print(f"Backup {args.file} ist gültig")
            else:
                print(f"Backup {args.file} ist ungültig oder beschädigt")

    except Exception as e:
        print(f"Fehler: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()