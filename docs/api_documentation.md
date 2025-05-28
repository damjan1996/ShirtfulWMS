# Shirtful WMS - API Dokumentation

## Übersicht

Das Shirtful WMS ist eine Desktop-Anwendung und bietet derzeit keine REST-API. Diese Dokumentation beschreibt die internen Python-Module und deren Verwendung.

## Module

### 1. utils.rfid_auth

RFID-Authentifizierung für Mitarbeiter-Login.

```python
from utils.rfid_auth import RFIDAuth

# RFID-Reader initialisieren
rfid = RFIDAuth(port='COM3')

# Einmal-Scan
tag_id = rfid.read_tag()

# Kontinuierliches Scannen
def on_tag_scanned(tag_id):
    print(f"Tag erkannt: {tag_id}")
    
rfid.start_continuous_read(on_tag_scanned)
```

**Klasse: RFIDAuth**

| Methode | Parameter | Rückgabe | Beschreibung |
|---------|-----------|----------|--------------|
| `__init__` | `port: str = None` | - | Initialisiert RFID-Reader |
| `connect` | - | `bool` | Stellt Verbindung her |
| `disconnect` | - | - | Trennt Verbindung |
| `read_tag` | - | `str or None` | Liest einmalig Tag |
| `start_continuous_read` | `callback: Callable` | - | Startet kontinuierliches Lesen |
| `stop_continuous_read` | - | - | Stoppt kontinuierliches Lesen |
| `beep` | `duration: int = 100` | - | Lässt Reader piepen |

### 2. utils.database

Datenbank-Operationen mit MSSQL Server.

```python
from utils.database import Database

# Datenbank-Instanz
db = Database()

# Mitarbeiter validieren
employee = db.validate_employee_rfid('12345678')

# Paket-Status aktualisieren
success = db.update_package_status(
    package_id=123,
    new_status='In Veredelung',
    employee_id=1
)
```

**Klasse: Database**

| Methode | Parameter | Rückgabe | Beschreibung |
|---------|-----------|----------|--------------|
| `validate_employee_rfid` | `rfid_tag: str` | `dict or None` | Validiert Mitarbeiter |
| `clock_in` | `employee_id: int` | `bool` | Stempelt ein |
| `clock_out` | `employee_id: int` | `bool` | Stempelt aus |
| `get_package_by_qr` | `qr_code: str` | `dict or None` | Holt Paketdaten |
| `register_package` | `...` | `int or None` | Registriert neues Paket |
| `update_package_status` | `...` | `bool` | Aktualisiert Status |
| `get_daily_statistics` | `employee_id: int, stage: str` | `dict` | Holt Tagesstatistik |

### 3. utils.qr_scanner

QR-Code Scanner mit Webcam.

```python
from utils.qr_scanner import QRScanner

# Scanner initialisieren
scanner = QRScanner(camera_index=0)

# Einmal scannen
qr_code = scanner.scan_once()

# Kontinuierlich scannen
def on_qr_scanned(code):
    print(f"QR-Code: {code}")
    
scanner.start_continuous_scan(on_qr_scanned)

# QR-Code generieren
from utils.qr_scanner import QRScanner
qr_image = QRScanner.generate_qr_code("PKG-2024-001234")
qr_image.save("package_label.png")
```

**Klasse: QRScanner**

| Methode | Parameter | Rückgabe | Beschreibung |
|---------|-----------|----------|--------------|
| `start_camera` | - | `bool` | Startet Kamera |
| `stop_camera` | - | - | Stoppt Kamera |
| `scan_once` | - | `str or None` | Einmal-Scan |
| `start_continuous_scan` | `callback: Callable` | - | Kontinuierliches Scannen |
| `stop_continuous_scan` | - | - | Stoppt Scannen |
| `get_camera_frame` | - | `numpy.ndarray` | Aktuelles Kamerabild |
| `generate_qr_code` | `data: str, size: int` | `PIL.Image` | Generiert QR-Code |

### 4. utils.ui_components

Wiederverwendbare UI-Komponenten.

```python
from utils.ui_components import UIComponents, COLORS, FONTS

ui = UIComponents()

# Großer Button erstellen
button = ui.create_large_button(
    parent=root,
    text="Paket scannen",
    command=scan_package,
    color=COLORS['primary']
)

# Info-Karte
card = ui.create_info_card(
    parent=root,
    title="Paketinfo",
    content="PKG-2024-001234\nKunde: Test GmbH"
)

# Sound abspielen
ui.play_sound('success')
```

**Klasse: UIComponents**

| Methode | Parameter | Rückgabe | Beschreibung |
|---------|-----------|----------|--------------|
| `create_large_button` | `parent, text, command, color, icon` | `tk.Button` | Touch-Button |
| `create_info_card` | `parent, title, content, icon` | `tk.Frame` | Info-Karte |
| `create_status_indicator` | `parent, status` | `tk.Label` | Status-Anzeige |
| `create_data_table` | `parent, columns, data` | `ttk.Treeview` | Datentabelle |
| `create_notification` | `parent, message, type, duration` | - | Popup-Nachricht |
| `play_sound` | `sound_name: str` | - | Spielt Sound |

### 5. config.translations

Mehrsprachigkeit für die Anwendung.

```python
from config.translations import Translations, _

# Translations-Instanz
trans = Translations()

# Sprache setzen
trans.set_language('en')

# Übersetzung holen
text = trans.get('scan_package')  # "Scan package"

# Shortcut-Funktion
text = _('welcome', name='John')  # "Welcome John"
```

**Klasse: Translations**

| Methode | Parameter | Rückgabe | Beschreibung |
|---------|-----------|----------|--------------|
| `get` | `key: str, language: str` | `str` | Holt Übersetzung |
| `set_language` | `language: str` | `bool` | Setzt Sprache |
| `get_language` | - | `str` | Aktuelle Sprache |
| `get_available_languages` | - | `dict` | Verfügbare Sprachen |

## Datenbank-Schema

### Tabelle: Employees

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| EmployeeID | INT | Primary Key |
| RFIDTag | VARCHAR(50) | RFID-Tag (unique) |
| Name | NVARCHAR(100) | Mitarbeitername |
| Department | NVARCHAR(50) | Abteilung |
| Role | NVARCHAR(50) | Rolle |
| Language | CHAR(2) | Sprachcode |
| IsActive | BIT | Aktiv-Status |

### Tabelle: Packages

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| PackageID | INT | Primary Key |
| QRCode | VARCHAR(50) | QR-Code (unique) |
| OrderID | VARCHAR(50) | Bestellnummer |
| CustomerName | NVARCHAR(100) | Kunde |
| CurrentStage | NVARCHAR(50) | Aktueller Status |
| Priority | NVARCHAR(20) | Priorität |

### Tabelle: PackageHistory

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| HistoryID | INT | Primary Key |
| PackageID | INT | Foreign Key |
| Stage | NVARCHAR(50) | Status |
| EmployeeID | INT | Foreign Key |
| Timestamp | DATETIME | Zeitstempel |
| Notes | NVARCHAR(500) | Notizen |

## Stored Procedures

### sp_UpdatePackageStatus

Aktualisiert den Status eines Pakets.

```sql
EXEC sp_UpdatePackageStatus 
    @PackageID = 123,
    @NewStatus = 'In Veredelung',
    @EmployeeID = 1,
    @Notes = 'Siebdruck gestartet'
```

### sp_DailyCloseout

Erstellt Tagesabschluss-Statistiken.

```sql
EXEC sp_DailyCloseout @Date = '2024-05-01'
```

## Konstanten

### Paket-Status (CurrentStage)

- `Wareneingang`
- `In Veredelung`
- `In Betuchung`
- `Qualitätskontrolle`
- `Qualität OK`
- `Nacharbeit erforderlich`
- `Versandbereit`
- `Versendet`

### Prioritäten

- `Niedrig`
- `Normal`
- `Hoch`
- `Express`
- `Dringend`

### Veredelungsarten

- `Siebdruck`
- `Digitaldruck`
- `Stickerei`
- `Transferdruck`
- `Flexdruck`
- `Sublimation`

## Fehlerbehandlung

Alle Module verwenden strukturierte Fehlerbehandlung:

```python
try:
    result = db.update_package_status(...)
    if result:
        # Erfolg
        pass
    else:
        # Fehler behandeln
        logger.error("Update fehlgeschlagen")
except Exception as e:
    logger.exception(f"Kritischer Fehler: {e}")
```

## Logging

Alle Module verwenden das zentrale Logging-System:

```python
from utils.logger import setup_logger

logger = setup_logger('module_name')
logger.info("Info-Nachricht")
logger.error("Fehler-Nachricht")
```

Log-Dateien werden gespeichert unter: `logs/module_name.log`

## Best Practices

1. **Fehlerbehandlung**: Immer try-except verwenden
2. **Logging**: Wichtige Aktionen loggen
3. **Transaktionen**: Datenbank-Updates in Transaktionen
4. **Validierung**: Eingaben validieren
5. **Timeouts**: Bei Hardware-Zugriff Timeouts setzen
6. **Ressourcen**: Verbindungen immer schließen
7. **Threading**: UI nicht aus Background-Threads updaten