# Shirtful WMS - Warehouse Management System

Ein einfaches, touch-optimiertes Lagerverwaltungssystem für die Textilveredelung bei Shirtful.

## 🚀 Übersicht

Das Shirtful WMS besteht aus 5 separaten Python/Tkinter-Anwendungen, die den kompletten Warenprozess abbilden:

1. **Wareneingang** - Erfassung eingehender Pakete
2. **Veredelung** - Druck- und Veredelungsprozesse
3. **Betuchung** - Stoffbearbeitung
4. **Qualitätskontrolle** - Prüfung und Freigabe
5. **Warenausgang** - Versandvorbereitung

## 📋 Features

- 🏷️ **RFID-Authentifizierung** für alle Mitarbeiter
- 📱 **QR-Code Scanning** für Paketverfolgung
- 🌍 **Mehrsprachigkeit** (DE, EN, TR, PL)
- ⏱️ **Zeiterfassung** integriert
- 📊 **Echtzeit-Statistiken**
- 🖥️ **Touch-optimierte Oberfläche**
- 🗄️ **MSSQL Datenbank-Backend**

## 🛠️ Technologie-Stack

- **Python 3.10+**
- **Tkinter** (GUI)
- **MSSQL Server** (Datenbank)
- **TSHRW380BZMP** (RFID-Reader)
- **OpenCV + pyzbar** (QR-Code Scanner)

## 📦 Installation

### 1. Voraussetzungen

- Windows 10/11
- Python 3.10 oder höher
- MSSQL Server (Express reicht)
- Webcam für QR-Code Scanning
- TSHRW380BZMP RFID-Reader

### 2. Repository klonen

```bash
git clone https://github.com/shirtful/wms.git
cd shirtful-wms
```

### 3. Virtuelle Umgebung erstellen

```bash
python -m venv venv
venv\Scripts\activate
```

### 4. Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

### 5. Datenbank einrichten

```sql
-- SQL Server Management Studio öffnen
-- Neue Datenbank erstellen: ShirtfulWMS
-- Schema-Script ausführen: database/schema.sql
```

### 6. Konfiguration anpassen

```python
# config/settings.json anpassen
{
    "database": {
        "server": "localhost",
        "database": "ShirtfulWMS"
    },
    "rfid": {
        "port": "COM3"
    }
}
```

## 🚀 Anwendungen starten

### Einzelne Anwendungen

```bash
# Wareneingang
python apps/wareneingang.py

# Veredelung
python apps/veredelung.py

# Betuchung
python apps/betuchung.py

# Qualitätskontrolle
python apps/qualitaetskontrolle.py

# Warenausgang
python apps/warenausgang.py
```

### Oder mit Batch-Dateien

Doppelklick auf:
- `run_wareneingang.bat`
- `run_veredelung.bat`
- `run_betuchung.bat`
- `run_qualitaetskontrolle.bat`
- `run_warenausgang.bat`

## 👤 Erste Anmeldung

### Test-Benutzer

| RFID-Tag | Name | Abteilung | Rolle |
|----------|------|-----------|-------|
| 12345678 | Max Mustermann | Lager | Lagerarbeiter |
| 87654321 | Erika Musterfrau | Veredelung | Teamleiter |
| ADMIN001 | Administrator | IT | Administrator |

## 📖 Bedienung

### Workflow

1. **Wareneingang**
   - RFID-Karte scannen zum Anmelden
   - "Neue Lieferung" starten
   - Pakete mit QR-Code scannen oder manuell erfassen
   - Lieferung abschließen

2. **Veredelung**
   - Anmelden mit RFID
   - Paket scannen
   - Veredelungsart wählen
   - Prozess starten

3. **Betuchung**
   - Anmelden mit RFID
   - Paket scannen
   - In Betuchung nehmen
   - Optional: Notizen hinzufügen

4. **Qualitätskontrolle**
   - Anmelden mit RFID
   - Paket scannen
   - Qualität prüfen
   - OK oder Nacharbeit markieren

5. **Warenausgang**
   - Anmelden mit RFID
   - Pakete für Versand scannen
   - Versandart wählen
   - Versand abschließen

## 🔧 Konfiguration

### RFID-Reader

```python
# config/rfid_config.py
RFID_CONFIG = {
    'port': 'COM3',  # Oder 'AUTO' für automatische Erkennung
    'baudrate': 9600,
    'beep_on_scan': True
}
```

### QR-Scanner

```python
# config/settings.json
{
    "scanner": {
        "camera_index": 0,  # 0 = Standard-Webcam
        "resolution": [1280, 720]
    }
}
```

## 📊 Datenbank-Schema

### Haupttabellen

- **Employees** - Mitarbeiterdaten
- **Packages** - Paketinformationen
- **Deliveries** - Lieferungen
- **PackageHistory** - Statusverlauf
- **TimeTracking** - Zeiterfassung
- **QualityIssues** - Qualitätsprobleme

## 🐛 Fehlerbehebung

### RFID-Reader wird nicht erkannt

1. Geräte-Manager prüfen
2. COM-Port in `rfid_config.py` anpassen
3. Treiber neu installieren

### QR-Code Scanner funktioniert nicht

1. Kamera-Zugriff prüfen
2. `camera_index` in settings.json ändern
3. OpenCV neu installieren: `pip install opencv-python --upgrade`

### Datenbankverbindung fehlgeschlagen

1. SQL Server läuft?
2. Windows-Authentifizierung aktiviert?
3. Connection String in `database_config.py` prüfen

## 📈 Performance-Tipps

- Regelmäßige Datenbank-Wartung
- Logs unter `logs/` regelmäßig leeren
- Nicht mehr als 50 Pakete pro Batch scannen
- Bei langsamer Performance: Datenbank-Indizes prüfen

## 🔐 Sicherheit

- RFID-Tags regelmäßig aktualisieren
- Mitarbeiter-Berechtigungen prüfen
- Backup-Strategie implementieren
- Audit-Logs regelmäßig prüfen

## 📝 Entwicklung

### Projekt-Struktur

```
shirtful-wms/
├── apps/              # Hauptanwendungen
├── utils/             # Gemeinsame Module
├── config/            # Konfigurationsdateien
├── database/          # SQL-Scripts
├── logs/              # Log-Dateien
├── tests/             # Unit-Tests
└── docs/              # Dokumentation
```

### Tests ausführen

```bash
pytest tests/
```

### Code-Style

```bash
# Formatierung
black .

# Linting
flake8 .

# Type Checking
mypy .
```

## 📄 Lizenz

Proprietär - Shirtful GmbH

## 👥 Support

Bei Fragen oder Problemen:
- **Email:** it@shirtful.de
- **Telefon:** +49 30 12345678
- **Intern:** Slack #wms-support

## 🔄 Updates

### Version 1.0.0 (Mai 2024)
- Erste Release
- Basis-Funktionalität für alle 5 Stationen
- RFID und QR-Code Integration
- Mehrsprachigkeit (DE, EN, TR, PL)

---

**Shirtful GmbH** - Warehouse Management System