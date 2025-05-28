# Shirtful WMS - Installationsanleitung

Diese Anleitung führt Sie Schritt für Schritt durch die Installation des Shirtful Warehouse Management Systems.

## 📋 Systemanforderungen

### Hardware
- **Prozessor:** Intel Core i3 oder besser
- **RAM:** Mindestens 4 GB (8 GB empfohlen)
- **Festplatte:** 2 GB freier Speicherplatz
- **Bildschirm:** 1024x768 oder höher (Touch-Screen empfohlen)
- **Webcam:** Für QR-Code Scanning
- **RFID-Reader:** TSHRW380BZMP (USB)

### Software
- **Betriebssystem:** Windows 10/11 (64-bit)
- **Python:** 3.10 oder höher
- **SQL Server:** Microsoft SQL Server 2019 Express oder höher
- **Browser:** Chrome/Firefox (für Dokumentation)

## 🚀 Installation

### 1. Python installieren

1. Python von https://www.python.org/downloads/ herunterladen
2. **Wichtig:** Bei Installation "Add Python to PATH" aktivieren
3. Installation durchführen
4. Terminal öffnen und prüfen:
   ```cmd
   python --version
   ```
   Sollte "Python 3.10.x" oder höher anzeigen

### 2. SQL Server installieren

1. SQL Server Express herunterladen:
   https://www.microsoft.com/en-us/sql-server/sql-server-downloads

2. Installation durchführen:
   - Installationstyp: "Basic"
   - Lizenz akzeptieren
   - Standardpfad verwenden

3. SQL Server Management Studio (SSMS) installieren:
   - Im Installer auf "Install SSMS" klicken
   - SSMS herunterladen und installieren

4. Windows-Authentifizierung aktivieren:
   - SSMS öffnen
   - Mit Server verbinden (Windows Authentication)
   - Sicherstellen dass Verbindung funktioniert

### 3. ODBC Driver installieren

1. Microsoft ODBC Driver 17 for SQL Server herunterladen:
   https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

2. Installer ausführen und Installation durchführen

### 4. Projekt einrichten

1. **Projektordner erstellen:**
   ```cmd
   cd C:\Users\damja\PycharmProjects
   mkdir Shirtful
   cd Shirtful
   ```

2. **Projekt-Dateien kopieren:**
   - Alle bereitgestellten Dateien in den Ordner kopieren
   - Oder Git Repository klonen (falls vorhanden)

3. **Python create_shirtful_project.py ausführen:**
   ```cmd
   python create_shirtful_project.py
   ```
   Dies erstellt die komplette Verzeichnisstruktur

4. **Virtuelle Umgebung erstellen:**
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

5. **Abhängigkeiten installieren:**
   ```cmd
   pip install -r requirements.txt
   ```

### 5. Datenbank einrichten

1. **SSMS öffnen** und mit Server verbinden

2. **Neue Datenbank erstellen:**
   ```sql
   CREATE DATABASE ShirtfulWMS;
   GO
   ```

3. **Schema erstellen:**
   - In SSMS: File > Open > File
   - `database\schema.sql` öffnen
   - Ausführen (F5)

4. **Testdaten laden (optional):**
   ```sql
   USE ShirtfulWMS;
   GO
   -- database\sample_data.sql ausführen
   ```

### 6. Konfiguration anpassen

1. **Datei öffnen:** `config\settings.json`

2. **Datenbank-Verbindung anpassen:**
   ```json
   "database": {
       "server": "localhost",  // oder ".\SQLEXPRESS"
       "database": "ShirtfulWMS",
       "trusted_connection": true
   }
   ```

3. **RFID-Port ermitteln:**
   - Geräte-Manager öffnen (Win+X, dann M)
   - Unter "Anschlüsse (COM & LPT)" nachsehen
   - COM-Port des RFID-Readers notieren

4. **RFID konfigurieren:**
   ```json
   "rfid": {
       "port": "COM3",  // Ihren Port eintragen
       "baudrate": 9600
   }
   ```

### 7. RFID-Reader einrichten

1. **Treiber installieren:**
   - Falls mitgelieferte CD: Treiber von CD installieren
   - Sonst: Windows sollte automatisch Treiber finden

2. **Reader testen:**
   ```cmd
   python -c "import serial.tools.list_ports; print([p.device for p in serial.tools.list_ports.comports()])"
   ```
   Sollte alle COM-Ports anzeigen

3. **Verbindung prüfen:**
   ```cmd
   python utils\rfid_auth.py
   ```

### 8. Erste Anwendung starten

1. **Test mit Wareneingang:**
   ```cmd
   python apps\wareneingang.py
   ```

2. **Oder mit Batch-Datei:**
   Doppelklick auf `run_wareneingang.bat`

3. **Login testen:**
   - RFID-Karte: Verwenden Sie eine der Test-Karten
   - Oder temporär in Code: Simulierten Login aktivieren

## 🔧 Problembehandlung

### Python wird nicht gefunden
- PATH-Variable prüfen
- Python neu installieren mit "Add to PATH"
- Computer neu starten

### Datenbankverbindung fehlgeschlagen
1. SQL Server Dienst läuft?
   ```cmd
   services.msc
   ```
   "SQL Server (SQLEXPRESS)" sollte "Gestartet" sein

2. Connection String prüfen:
   - Bei Named Instance: `server: ".\SQLEXPRESS"`
   - Bei Default Instance: `server: "localhost"`

3. Firewall-Ausnahme hinzufügen

### RFID-Reader wird nicht erkannt
1. Anderen USB-Port versuchen
2. Geräte-Manager > COM-Port prüfen
3. In `rfid_config.py` Port manuell setzen:
   ```python
   'port': 'COM4',  # Statt 'AUTO'
   ```

### QR-Scanner funktioniert nicht
1. Kamera-Berechtigung prüfen:
   - Windows-Einstellungen > Datenschutz > Kamera
   - App-Zugriff erlauben

2. Andere Kamera-Index versuchen:
   ```json
   "camera_index": 1,  // statt 0
   ```

### Fehlende Module
```cmd
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

## 📱 Touch-Screen Konfiguration

Für optimale Touch-Bedienung:

1. **Windows Touch-Tastatur aktivieren:**
   - Taskleiste Rechtsklick > Taskleisteneinstellungen
   - "Touch-Tastatur-Schaltfläche anzeigen" aktivieren

2. **Bildschirm kalibrieren:**
   - Systemsteuerung > Tablet PC-Einstellungen
   - "Kalibrieren" ausführen

## 🚦 Nächste Schritte

1. **Mitarbeiter anlegen:**
   - In SSMS Employees-Tabelle bearbeiten
   - RFID-Tags zuweisen

2. **Drucker einrichten:**
   - Zebra-Drucker installieren
   - In Settings Drucker-Port eintragen

3. **Backup einrichten:**
   - Windows Task Scheduler öffnen
   - Tägliches Backup planen

4. **Schulung durchführen:**
   - Testlauf mit allen Stationen
   - Mitarbeiter einweisen

## 📞 Support

Bei Problemen:
- Logs prüfen: `logs\` Verzeichnis
- Screenshots von Fehlermeldungen
- Kontakt: it@shirtful.de

---

**Viel Erfolg mit dem Shirtful WMS!**