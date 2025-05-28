"""
Haupteinstellungen für Shirtful WMS
Zentrale Konfigurationsdatei für alle Anwendungen.
"""

import os
import json
from pathlib import Path
from typing import Any, Dict, Optional
import logging
from datetime import datetime
from typing import List, Dict



class Settings:
    """Zentrale Settings-Klasse für die Anwendung."""

    def __init__(self, config_file: str = None):
        """
        Initialisiert die Settings.

        Args:
            config_file: Pfad zur Konfigurationsdatei
        """
        self.logger = logging.getLogger(__name__)

        # Standard-Konfigurationsdatei
        if not config_file:
            config_dir = Path(__file__).parent
            config_file = config_dir / 'settings.json'

        self.config_file = Path(config_file)

        # Standard-Einstellungen
        self.defaults = self._get_defaults()

        # Einstellungen laden
        self.settings = self.defaults.copy()
        self.load()

    def _get_defaults(self) -> Dict[str, Any]:
        """
        Definiert Standard-Einstellungen.

        Returns:
            Dictionary mit Standard-Einstellungen
        """
        return {
            # === Allgemeine Einstellungen ===
            'general': {
                'company_name': 'Shirtful GmbH',
                'system_name': 'Shirtful WMS',
                'version': '1.0.0',
                'language': 'de',
                'timezone': 'Europe/Berlin',
                'debug_mode': False,
                'log_level': 'INFO'
            },

            # === Datenbank ===
            'database': {
                'server': 'localhost',
                'database': 'ShirtfulWMS',
                'trusted_connection': True,
                'username': '',
                'password': '',
                'connection_timeout': 30,
                'command_timeout': 300,
                'pool_size': 5
            },

            # === RFID ===
            'rfid': {
                'enabled': True,
                'port': 'AUTO',  # AUTO für automatische Erkennung
                'baudrate': 9600,
                'timeout': 0.5,
                'beep_on_scan': True,
                'duplicate_timeout': 2.0,
                'auto_read': True
            },

            # === QR-Scanner ===
            'scanner': {
                'enabled': True,
                'camera_index': 0,
                'resolution': [1280, 720],
                'autofocus': True,
                'scan_interval': 0.1,
                'min_qr_size': 50,
                'beep_on_scan': True,
                'show_preview': True
            },

            # === UI-Einstellungen ===
            'ui': {
                'fullscreen': True,
                'touch_mode': True,
                'show_keyboard': True,
                'theme': 'light',
                'font_size': 'normal',
                'sound_enabled': True,
                'notification_duration': 3000,
                'auto_logout_minutes': 30
            },

            # === Arbeitszeiten ===
            'working_hours': {
                'start_time': '06:00',
                'end_time': '22:00',
                'break_after_hours': 6,
                'break_duration_minutes': 30,
                'overtime_allowed': True,
                'weekend_work': True
            },

            # === Prozess-Einstellungen ===
            'process': {
                'auto_print_labels': True,
                'require_quality_check': True,
                'allow_skip_stages': False,
                'max_batch_size': 50,
                'priority_handling': True,
                'express_processing': True
            },

            # === Benachrichtigungen ===
            'notifications': {
                'email_enabled': False,
                'email_server': '',
                'email_port': 587,
                'email_user': '',
                'email_password': '',
                'email_from': 'wms@shirtful.de',
                'alert_on_errors': True,
                'daily_report': True
            },

            # === Backup ===
            'backup': {
                'enabled': True,
                'interval_hours': 24,
                'backup_path': 'C:\\Backups\\ShirtfulWMS',
                'keep_days': 30,
                'compress': True,
                'include_logs': True
            },

            # === Sicherheit ===
            'security': {
                'require_rfid': True,
                'allow_manual_login': False,
                'password_min_length': 8,
                'session_timeout_minutes': 60,
                'max_login_attempts': 3,
                'audit_logging': True
            },

            # === Performance ===
            'performance': {
                'cache_enabled': True,
                'cache_ttl_seconds': 300,
                'max_concurrent_scans': 3,
                'db_connection_pooling': True,
                'lazy_loading': True
            },

            # === Pfade ===
            'paths': {
                'data_dir': 'C:\\ProgramData\\ShirtfulWMS',
                'log_dir': 'C:\\ProgramData\\ShirtfulWMS\\logs',
                'backup_dir': 'C:\\Backups\\ShirtfulWMS',
                'temp_dir': 'C:\\Temp\\ShirtfulWMS',
                'report_dir': 'C:\\Reports\\ShirtfulWMS'
            },

            # === Integration ===
            'integration': {
                'erp_enabled': False,
                'erp_endpoint': '',
                'erp_api_key': '',
                'webhook_enabled': False,
                'webhook_url': '',
                'sync_interval_minutes': 15
            }
        }

    def load(self) -> bool:
        """
        Lädt Einstellungen aus Datei.

        Returns:
            True bei Erfolg
        """
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)

                # Merge mit Defaults
                self._deep_merge(self.settings, loaded)

                self.logger.info(f"Einstellungen geladen von {self.config_file}")
                return True
            else:
                self.logger.info("Keine Konfigurationsdatei gefunden, verwende Defaults")
                # Erstelle Datei mit Defaults
                self.save()
                return True

        except Exception as e:
            self.logger.error(f"Fehler beim Laden der Einstellungen: {e}")
            return False

    def save(self) -> bool:
        """
        Speichert Einstellungen in Datei.

        Returns:
            True bei Erfolg
        """
        try:
            # Verzeichnis erstellen
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            # Backup erstellen
            if self.config_file.exists():
                backup = self.config_file.with_suffix('.json.bak')
                self.config_file.rename(backup)

            # Speichern
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)

            self.logger.info(f"Einstellungen gespeichert nach {self.config_file}")
            return True

        except Exception as e:
            self.logger.error(f"Fehler beim Speichern der Einstellungen: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """
        Holt einen Einstellungswert.

        Args:
            key: Schlüssel (kann Punkte für Verschachtelung enthalten)
            default: Standardwert falls nicht vorhanden

        Returns:
            Einstellungswert
        """
        keys = key.split('.')
        value = self.settings

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any, save: bool = True) -> bool:
        """
        Setzt einen Einstellungswert.

        Args:
            key: Schlüssel (kann Punkte für Verschachtelung enthalten)
            value: Neuer Wert
            save: Automatisch speichern

        Returns:
            True bei Erfolg
        """
        try:
            keys = key.split('.')
            target = self.settings

            # Navigate to parent
            for k in keys[:-1]:
                if k not in target:
                    target[k] = {}
                target = target[k]

            # Set value
            target[keys[-1]] = value

            # Speichern wenn gewünscht
            if save:
                return self.save()

            return True

        except Exception as e:
            self.logger.error(f"Fehler beim Setzen von {key}: {e}")
            return False

    def reset(self, section: str = None) -> bool:
        """
        Setzt Einstellungen auf Defaults zurück.

        Args:
            section: Bestimmte Sektion oder None für alle

        Returns:
            True bei Erfolg
        """
        try:
            if section:
                if section in self.defaults:
                    self.settings[section] = self.defaults[section].copy()
                else:
                    return False
            else:
                self.settings = self.defaults.copy()

            return self.save()

        except Exception as e:
            self.logger.error(f"Fehler beim Zurücksetzen: {e}")
            return False

    def validate(self) -> Dict[str, List[str]]:
        """
        Validiert die aktuellen Einstellungen.

        Returns:
            Dictionary mit Fehlern pro Sektion
        """
        errors = {}

        # Datenbank validieren
        db_errors = []
        if not self.get('database.server'):
            db_errors.append("Server nicht angegeben")
        if not self.get('database.database'):
            db_errors.append("Datenbank nicht angegeben")

        if db_errors:
            errors['database'] = db_errors

        # Pfade validieren
        path_errors = []
        for key in ['data_dir', 'log_dir', 'backup_dir']:
            path = self.get(f'paths.{key}')
            if path and not os.path.exists(path):
                try:
                    os.makedirs(path, exist_ok=True)
                except:
                    path_errors.append(f"{key}: Pfad kann nicht erstellt werden")

        if path_errors:
            errors['paths'] = path_errors

        # RFID validieren
        rfid_errors = []
        baudrate = self.get('rfid.baudrate')
        if baudrate not in [9600, 19200, 38400, 57600, 115200]:
            rfid_errors.append("Ungültige Baudrate")

        if rfid_errors:
            errors['rfid'] = rfid_errors

        return errors

    def export_settings(self, filepath: str) -> bool:
        """
        Exportiert Einstellungen in Datei.

        Args:
            filepath: Zieldatei

        Returns:
            True bei Erfolg
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            self.logger.error(f"Export-Fehler: {e}")
            return False

    def import_settings(self, filepath: str) -> bool:
        """
        Importiert Einstellungen aus Datei.

        Args:
            filepath: Quelldatei

        Returns:
            True bei Erfolg
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                imported = json.load(f)

            # Validieren
            if not isinstance(imported, dict):
                return False

            # Backup aktueller Einstellungen
            backup = self.settings.copy()

            try:
                # Merge
                self._deep_merge(self.settings, imported)

                # Speichern
                return self.save()

            except:
                # Restore bei Fehler
                self.settings = backup
                return False

        except Exception as e:
            self.logger.error(f"Import-Fehler: {e}")
            return False

    def _deep_merge(self, target: dict, source: dict):
        """
        Deep merge von zwei Dictionaries.

        Args:
            target: Ziel-Dictionary
            source: Quell-Dictionary
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value

    def get_all_settings(self) -> Dict[str, Any]:
        """
        Gibt alle Einstellungen zurück.

        Returns:
            Kopie aller Einstellungen
        """
        return self.settings.copy()

    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Gibt eine komplette Sektion zurück.

        Args:
            section: Sektionsname

        Returns:
            Sektions-Dictionary oder leeres Dict
        """
        return self.settings.get(section, {}).copy()


# Globale Settings-Instanz
_settings = None


def get_settings() -> Settings:
    """
    Holt die globale Settings-Instanz.

    Returns:
        Settings-Instanz
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# Test
if __name__ == "__main__":
    # Test Settings
    settings = Settings()

    print("=== Shirtful WMS Settings ===\n")

    # Einige Werte anzeigen
    print(f"Company: {settings.get('general.company_name')}")
    print(f"Version: {settings.get('general.version')}")
    print(f"Database: {settings.get('database.server')}/{settings.get('database.database')}")
    print(f"RFID Port: {settings.get('rfid.port')}")

    # Validierung
    errors = settings.validate()
    if errors:
        print("\nValidierungsfehler:")
        for section, errs in errors.items():
            print(f"  {section}: {', '.join(errs)}")
    else:
        print("\nKeine Validierungsfehler")

    # Test set/get
    settings.set('test.value', 'Hello World', save=False)
    print(f"\nTest Value: {settings.get('test.value')}")