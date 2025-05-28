@echo off
REM Shirtful WMS - Veredelung starten
REM =====================================

echo ========================================
echo Shirtful WMS - VEREDELUNG
echo ========================================
echo.

REM Zum Projektverzeichnis wechseln
cd /d "%~dp0"

REM Prüfen ob venv existiert
if not exist "venv\Scripts\activate.bat" (
    echo [FEHLER] Virtuelle Umgebung nicht gefunden!
    echo.
    echo Bitte führen Sie zuerst aus:
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Virtuelle Umgebung aktivieren
call venv\Scripts\activate.bat

REM Python-Version prüfen
python --version >nul 2>&1
if errorlevel 1 (
    echo [FEHLER] Python nicht gefunden!
    echo.
    pause
    exit /b 1
)

REM Anwendung starten
echo Starte Veredelung-Anwendung...
echo.
echo Zum Beenden: Fenster schließen oder Strg+C
echo ========================================
echo.

python apps\veredelung.py

REM Bei Fehler
if errorlevel 1 (
    echo.
    echo [FEHLER] Anwendung wurde mit Fehler beendet!
    echo.
    pause
)

REM Virtuelle Umgebung deaktivieren
deactivate