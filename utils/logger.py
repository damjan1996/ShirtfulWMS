"""
Logger-Konfiguration für Shirtful WMS
Einheitliches Logging für alle Anwendungen.
"""

import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path
import sys
from typing import Optional

# Log-Verzeichnis
LOG_DIR = Path(__file__).parent.parent / 'logs'
LOG_DIR.mkdir(exist_ok=True)

# Log-Level Mapping
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}


class ColoredFormatter(logging.Formatter):
    """Formatter mit farbiger Ausgabe für Console."""

    # ANSI Color Codes
    COLORS = {
        'DEBUG': '\033[36m',  # Cyan
        'INFO': '\033[32m',  # Grün
        'WARNING': '\033[33m',  # Gelb
        'ERROR': '\033[31m',  # Rot
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'  # Reset
    }

    def format(self, record):
        """Formatiert Log-Eintrag mit Farbe."""
        # Farbe basierend auf Level
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']

        # Original-Format anwenden
        message = super().format(record)

        # Farbe nur in Console
        if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
            return f"{color}{message}{reset}"
        else:
            return message


def setup_logger(name: str = None,
                 level: str = 'INFO',
                 console: bool = True,
                 file: bool = True,
                 max_bytes: int = 10485760,  # 10MB
                 backup_count: int = 5) -> logging.Logger:
    """
    Richtet einen Logger ein.

    Args:
        name: Logger-Name (None für Root-Logger)
        level: Log-Level als String
        console: Console-Output aktivieren
        file: File-Output aktivieren
        max_bytes: Maximale Dateigröße
        backup_count: Anzahl Backup-Dateien

    Returns:
        Konfigurierter Logger
    """
    # Logger erstellen oder holen
    logger = logging.getLogger(name)

    # Nur konfigurieren wenn noch keine Handler
    if logger.handlers:
        return logger

    # Level setzen
    log_level = LOG_LEVELS.get(level.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Format definieren
    file_format = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    console_format = '%(asctime)s - %(levelname)s - %(message)s'

    # Console Handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_formatter = ColoredFormatter(console_format, datefmt='%H:%M:%S')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    # File Handler
    if file:
        # Dateiname basierend auf Logger-Name
        if name:
            filename = f"{name.replace('.', '_')}.log"
        else:
            filename = "shirtful_wms.log"

        filepath = LOG_DIR / filename

        # Rotating File Handler
        file_handler = logging.handlers.RotatingFileHandler(
            filepath,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter(file_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    # Erste Log-Nachricht
    logger.info(f"Logger '{name or 'root'}' initialisiert")

    return logger


def get_logger(name: str = None) -> logging.Logger:
    """
    Holt einen konfigurierten Logger.

    Args:
        name: Logger-Name

    Returns:
        Logger-Instanz
    """
    return logging.getLogger(name)


class LoggerContext:
    """Context Manager für temporäre Logger-Konfiguration."""

    def __init__(self, logger_name: str, level: str = None,
                 handlers: list = None):
        """
        Initialisiert den Context Manager.

        Args:
            logger_name: Name des Loggers
            level: Temporäres Log-Level
            handlers: Temporäre Handler
        """
        self.logger = logging.getLogger(logger_name)
        self.original_level = self.logger.level
        self.original_handlers = self.logger.handlers.copy()
        self.temp_level = LOG_LEVELS.get(level.upper()) if level else None
        self.temp_handlers = handlers or []

    def __enter__(self):
        """Aktiviert temporäre Konfiguration."""
        if self.temp_level:
            self.logger.setLevel(self.temp_level)

        for handler in self.temp_handlers:
            self.logger.addHandler(handler)

        return self.logger

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stellt ursprüngliche Konfiguration wieder her."""
        self.logger.setLevel(self.original_level)

        # Alle Handler entfernen
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # Original Handler wiederherstellen
        for handler in self.original_handlers:
            self.logger.addHandler(handler)


def log_exception(logger: logging.Logger, exc: Exception,
                  message: str = "Unbehandelte Ausnahme"):
    """
    Loggt eine Exception mit Traceback.

    Args:
        logger: Logger-Instanz
        exc: Exception
        message: Zusätzliche Nachricht
    """
    logger.exception(f"{message}: {type(exc).__name__}: {str(exc)}")


def setup_app_logging(app_name: str):
    """
    Richtet Logging für eine komplette App ein.

    Args:
        app_name: Name der Anwendung
    """
    # Root Logger
    root_logger = setup_logger(
        name=None,
        level='WARNING',
        file=True,
        console=False
    )

    # App Logger
    app_logger = setup_logger(
        name=app_name,
        level='INFO',
        file=True,
        console=True
    )

    # Datenbank Logger
    db_logger = setup_logger(
        name=f'{app_name}.database',
        level='DEBUG',
        file=True,
        console=False
    )

    # RFID Logger
    rfid_logger = setup_logger(
        name=f'{app_name}.rfid',
        level='INFO',
        file=True,
        console=False
    )

    # Startup-Nachricht
    app_logger.info(f"{'=' * 50}")
    app_logger.info(f"Shirtful WMS - {app_name}")
    app_logger.info(f"Gestartet: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    app_logger.info(f"{'=' * 50}")


def create_audit_logger(name: str = 'audit') -> logging.Logger:
    """
    Erstellt einen speziellen Audit-Logger.

    Args:
        name: Logger-Name

    Returns:
        Audit Logger
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # Audit-Datei (täglich rotierend)
    audit_file = LOG_DIR / f'{name}.log'
    handler = logging.handlers.TimedRotatingFileHandler(
        audit_file,
        when='midnight',
        interval=1,
        backupCount=365,  # 1 Jahr aufbewahren
        encoding='utf-8'
    )

    # Spezielles Format für Audit
    formatter = logging.Formatter(
        '%(asctime)s|%(levelname)s|%(name)s|%(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Keine Propagierung zum Root Logger
    logger.propagate = False

    return logger


def log_user_action(user_id: int, action: str, details: dict = None):
    """
    Loggt eine Benutzeraktion für Audit-Zwecke.

    Args:
        user_id: Benutzer-ID
        action: Durchgeführte Aktion
        details: Zusätzliche Details als Dictionary
    """
    audit_logger = create_audit_logger()

    # Log-Nachricht zusammenbauen
    message_parts = [
        f"USER:{user_id}",
        f"ACTION:{action}"
    ]

    if details:
        for key, value in details.items():
            message_parts.append(f"{key.upper()}:{value}")

    audit_logger.info("|".join(message_parts))


def cleanup_old_logs(days: int = 30):
    """
    Löscht alte Log-Dateien.

    Args:
        days: Logs älter als X Tage löschen
    """
    logger = setup_logger('maintenance')
    cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)

    deleted_count = 0
    for log_file in LOG_DIR.glob('*.log*'):
        if log_file.stat().st_mtime < cutoff_time:
            try:
                log_file.unlink()
                deleted_count += 1
            except Exception as e:
                logger.error(f"Fehler beim Löschen von {log_file}: {e}")

    if deleted_count > 0:
        logger.info(f"{deleted_count} alte Log-Dateien gelöscht")


# Test und Beispiele
if __name__ == "__main__":
    # Verschiedene Logger testen

    # Standard Logger
    logger = setup_logger('test_logger')

    logger.debug("Debug-Nachricht")
    logger.info("Info-Nachricht")
    logger.warning("Warnung")
    logger.error("Fehler")
    logger.critical("Kritischer Fehler")

    # Exception logging
    try:
        1 / 0
    except Exception as e:
        log_exception(logger, e, "Test-Exception")

    # Audit logging
    log_user_action(
        user_id=123,
        action='LOGIN',
        details={
            'ip': '192.168.1.100',
            'location': 'Wareneingang'
        }
    )

    # Context Manager
    with LoggerContext('test_logger', level='DEBUG') as debug_logger:
        debug_logger.debug("Diese Debug-Nachricht wird angezeigt")

    # App-Logging einrichten
    setup_app_logging('wareneingang')

    print(f"\nLog-Dateien in: {LOG_DIR}")