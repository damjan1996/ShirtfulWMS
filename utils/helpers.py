"""
Hilfsfunktionen für Shirtful WMS
Allgemeine Utility-Funktionen für alle Anwendungen.
"""

import os
import json
import csv
import hashlib
import secrets
from datetime import datetime, date, timedelta
from typing import Any, Dict, List, Optional, Union, Tuple
import re
import unicodedata
from pathlib import Path
import zipfile
import shutil
import platform
import subprocess


def generate_package_id(prefix: str = "PKG") -> str:
    """
    Generiert eine eindeutige Paket-ID.

    Args:
        prefix: Präfix für die ID

    Returns:
        Eindeutige ID im Format PREFIX-YYYY-XXXXXX
    """
    year = datetime.now().year
    random_part = secrets.token_hex(3).upper()
    return f"{prefix}-{year}-{random_part}"


def generate_qr_data(package_id: str, order_id: str,
                     customer: str, metadata: Dict = None) -> str:
    """
    Generiert QR-Code Daten für ein Paket.

    Args:
        package_id: Paket-ID
        order_id: Bestell-ID
        customer: Kundenname
        metadata: Zusätzliche Metadaten

    Returns:
        JSON-String für QR-Code
    """
    data = {
        'id': package_id,
        'order': order_id,
        'customer': customer,
        'timestamp': datetime.now().isoformat(),
        'version': '1.0'
    }

    if metadata:
        data['metadata'] = metadata

    return json.dumps(data, separators=(',', ':'))


def parse_qr_data(qr_string: str) -> Optional[Dict[str, Any]]:
    """
    Parst QR-Code Daten.

    Args:
        qr_string: QR-Code String

    Returns:
        Dictionary mit Daten oder None
    """
    try:
        # Versuche JSON zu parsen
        data = json.loads(qr_string)
        return data
    except json.JSONDecodeError:
        # Fallback: Einfache Paket-ID
        if qr_string.startswith("PKG-"):
            return {'id': qr_string}
    except Exception:
        pass

    return None


def validate_email(email: str) -> bool:
    """
    Validiert eine E-Mail-Adresse.

    Args:
        email: E-Mail-Adresse

    Returns:
        True wenn gültig
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """
    Validiert eine Telefonnummer (deutsch).

    Args:
        phone: Telefonnummer

    Returns:
        True wenn gültig
    """
    # Entferne alle Nicht-Ziffern
    digits = re.sub(r'\D', '', phone)

    # Deutsche Nummern: 10-12 Ziffern
    return 10 <= len(digits) <= 12


def sanitize_string(text: str, max_length: int = None,
                    allowed_chars: str = None) -> str:
    """
    Bereinigt einen String für sichere Verwendung.

    Args:
        text: Eingabetext
        max_length: Maximale Länge
        allowed_chars: Erlaubte Zeichen (Regex)

    Returns:
        Bereinigter String
    """
    if not text:
        return ""

    # Unicode normalisieren
    text = unicodedata.normalize('NFKC', text)

    # Whitespace trimmen
    text = text.strip()

    # Erlaubte Zeichen filtern
    if allowed_chars:
        text = re.sub(f'[^{allowed_chars}]', '', text)
    else:
        # Standard: Alphanumerisch + Basis-Sonderzeichen
        text = re.sub(r'[^\w\s\-.,!?@#äöüÄÖÜß]', '', text)

    # Länge begrenzen
    if max_length:
        text = text[:max_length]

    return text


def format_datetime(dt: datetime, format: str = "full") -> str:
    """
    Formatiert ein Datetime-Objekt.

    Args:
        dt: Datetime-Objekt
        format: Format-Typ ('full', 'date', 'time', 'short')

    Returns:
        Formatierter String
    """
    if not dt:
        return ""

    formats = {
        'full': '%d.%m.%Y %H:%M:%S',
        'date': '%d.%m.%Y',
        'time': '%H:%M:%S',
        'short': '%d.%m. %H:%M',
        'iso': '%Y-%m-%d %H:%M:%S'
    }

    fmt = formats.get(format, formats['full'])
    return dt.strftime(fmt)


def parse_datetime(date_string: str) -> Optional[datetime]:
    """
    Parst verschiedene Datetime-Formate.

    Args:
        date_string: Datum als String

    Returns:
        Datetime-Objekt oder None
    """
    formats = [
        '%Y-%m-%d %H:%M:%S',
        '%d.%m.%Y %H:%M:%S',
        '%Y-%m-%d',
        '%d.%m.%Y',
        '%d/%m/%Y',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%SZ'
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue

    return None


def calculate_working_days(start_date: date, end_date: date,
                           exclude_weekends: bool = True,
                           holidays: List[date] = None) -> int:
    """
    Berechnet Arbeitstage zwischen zwei Daten.

    Args:
        start_date: Startdatum
        end_date: Enddatum
        exclude_weekends: Wochenenden ausschließen
        holidays: Liste von Feiertagen

    Returns:
        Anzahl Arbeitstage
    """
    if start_date > end_date:
        return 0

    days = 0
    current = start_date
    holidays = holidays or []

    while current <= end_date:
        is_workday = True

        # Wochenende prüfen
        if exclude_weekends and current.weekday() in (5, 6):
            is_workday = False

        # Feiertag prüfen
        if current in holidays:
            is_workday = False

        if is_workday:
            days += 1

        current += timedelta(days=1)

    return days


def hash_password(password: str, salt: str = None) -> Tuple[str, str]:
    """
    Hasht ein Passwort mit Salt.

    Args:
        password: Klartext-Passwort
        salt: Salt (optional, wird generiert wenn None)

    Returns:
        Tuple von (Hash, Salt)
    """
    if not salt:
        salt = secrets.token_hex(32)

    # PBKDF2 mit SHA256
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000  # Iterationen
    )

    return key.hex(), salt


def verify_password(password: str, hash: str, salt: str) -> bool:
    """
    Verifiziert ein Passwort gegen Hash.

    Args:
        password: Eingegebenes Passwort
        hash: Gespeicherter Hash
        salt: Gespeicherter Salt

    Returns:
        True wenn Passwort korrekt
    """
    computed_hash, _ = hash_password(password, salt)
    return computed_hash == hash


def export_to_csv(data: List[Dict], filename: str,
                  columns: List[str] = None) -> bool:
    """
    Exportiert Daten in CSV-Datei.

    Args:
        data: Liste von Dictionaries
        filename: Zieldatei
        columns: Spalten (optional, sonst alle)

    Returns:
        True bei Erfolg
    """
    try:
        if not data:
            return False

        # Spalten bestimmen
        if not columns:
            columns = list(data[0].keys())

        # CSV schreiben
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=columns, delimiter=';')
            writer.writeheader()

            for row in data:
                # Nur definierte Spalten
                filtered_row = {k: row.get(k, '') for k in columns}
                writer.writerow(filtered_row)

        return True

    except Exception as e:
        print(f"CSV-Export Fehler: {e}")
        return False


def import_from_csv(filename: str, encoding: str = 'utf-8-sig') -> List[Dict]:
    """
    Importiert Daten aus CSV-Datei.

    Args:
        filename: Quelldatei
        encoding: Datei-Encoding

    Returns:
        Liste von Dictionaries
    """
    data = []

    try:
        with open(filename, 'r', encoding=encoding) as f:
            # Delimiter erkennen
            sample = f.read(1024)
            f.seek(0)

            delimiter = ';' if ';' in sample else ','

            reader = csv.DictReader(f, delimiter=delimiter)
            data = list(reader)

    except Exception as e:
        print(f"CSV-Import Fehler: {e}")

    return data


def create_backup(source_dir: str, backup_dir: str,
                  prefix: str = "backup") -> Optional[str]:
    """
    Erstellt ein Backup eines Verzeichnisses.

    Args:
        source_dir: Quellverzeichnis
        backup_dir: Backup-Verzeichnis
        prefix: Dateinamen-Präfix

    Returns:
        Pfad zur Backup-Datei oder None
    """
    try:
        # Backup-Verzeichnis erstellen
        Path(backup_dir).mkdir(parents=True, exist_ok=True)

        # Backup-Dateiname
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(
            backup_dir,
            f"{prefix}_{timestamp}.zip"
        )

        # ZIP erstellen
        with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_name = os.path.relpath(file_path, source_dir)
                    zf.write(file_path, arc_name)

        return backup_file

    except Exception as e:
        print(f"Backup-Fehler: {e}")
        return None


def get_system_info() -> Dict[str, Any]:
    """
    Sammelt System-Informationen.

    Returns:
        Dictionary mit System-Info
    """
    info = {
        'platform': platform.system(),
        'platform_version': platform.version(),
        'platform_release': platform.release(),
        'architecture': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version(),
        'hostname': platform.node()
    }

    # Windows-spezifisch
    if platform.system() == 'Windows':
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
            )
            info['windows_product'] = winreg.QueryValueEx(key, "ProductName")[0]
            info['windows_build'] = winreg.QueryValueEx(key, "CurrentBuild")[0]
            winreg.CloseKey(key)
        except:
            pass

    return info


def open_file_explorer(path: str):
    """
    Öffnet den Datei-Explorer mit einem bestimmten Pfad.

    Args:
        path: Zu öffnender Pfad
    """
    path = os.path.abspath(path)

    if platform.system() == 'Windows':
        os.startfile(path)
    elif platform.system() == 'Darwin':  # macOS
        subprocess.Popen(['open', path])
    else:  # Linux
        subprocess.Popen(['xdg-open', path])


def format_file_size(size_bytes: int) -> str:
    """
    Formatiert Dateigröße human-readable.

    Args:
        size_bytes: Größe in Bytes

    Returns:
        Formatierte Größe
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def get_app_data_dir(app_name: str = "ShirtfulWMS") -> Path:
    """
    Ermittelt das App-Data Verzeichnis.

    Args:
        app_name: Name der Anwendung

    Returns:
        Pfad zum App-Data Verzeichnis
    """
    if platform.system() == 'Windows':
        base = os.environ.get('APPDATA', '')
    elif platform.system() == 'Darwin':  # macOS
        base = os.path.expanduser('~/Library/Application Support')
    else:  # Linux
        base = os.path.expanduser('~/.config')

    app_dir = Path(base) / app_name
    app_dir.mkdir(parents=True, exist_ok=True)

    return app_dir


def cleanup_temp_files(temp_dir: str, age_hours: int = 24):
    """
    Löscht alte temporäre Dateien.

    Args:
        temp_dir: Temporäres Verzeichnis
        age_hours: Dateien älter als X Stunden löschen
    """
    if not os.path.exists(temp_dir):
        return

    cutoff_time = datetime.now().timestamp() - (age_hours * 3600)

    for file in Path(temp_dir).iterdir():
        if file.is_file() and file.stat().st_mtime < cutoff_time:
            try:
                file.unlink()
            except:
                pass


# Test
if __name__ == "__main__":
    # Tests
    print("=== Helper Functions Test ===\n")

    # Package ID
    pkg_id = generate_package_id()
    print(f"Package ID: {pkg_id}")

    # QR Data
    qr_data = generate_qr_data(pkg_id, "ORDER-123", "Test GmbH")
    print(f"QR Data: {qr_data}")

    # Email Validation
    print(f"Email valid: {validate_email('test@example.com')}")

    # String Sanitization
    dirty = "Test <script>alert('XSS')</script> String!"
    clean = sanitize_string(dirty)
    print(f"Sanitized: {clean}")

    # DateTime Formatting
    now = datetime.now()
    print(f"Formatted: {format_datetime(now, 'short')}")

    # System Info
    info = get_system_info()
    print(f"\nSystem: {info['platform']} {info['platform_version']}")

    # File Size
    size = format_file_size(1536789)
    print(f"File Size: {size}")