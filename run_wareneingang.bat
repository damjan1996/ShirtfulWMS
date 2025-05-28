@echo off
REM Shirtful WMS - Wareneingang starten
REM =====================================

echo ========================================
echo Shirtful WMS - WARENEINGANG
echo ========================================
echo.

REM Zum Projektverzeichnis wechseln
cd /d "%~dp0"

REM Prüfen ob venv existiert und verwenden, sonst globales Python
if exist "venv\Scripts\activate.bat" (
    echo [INFO] Verwende virtuelle Umgebung
    call venv\Scripts\activate.bat
    set USING_VENV=1
) else (
    echo [INFO] Verwende globales Python ^(keine venv gefunden^)
    set USING_VENV=0
)

REM Python-Version prüfen
python --version >nul 2>&1
if errorlevel 1 (
    echo [FEHLER] Python nicht gefunden!
    echo.
    pause
    exit /b 1
)

REM PySerial verfügbarkeit prüfen
python -c "import serial; print('[INFO] PySerial verfuegbar, Version:', serial.VERSION)" 2>nul
if errorlevel 1 (
    echo [WARNUNG] PySerial nicht gefunden! Installiere Abhaengigkeiten
    pip install -r requirements.txt
)

REM Anwendung starten
echo Starte Wareneingang-Anwendung
echo.
echo Zum Beenden: Fenster schliessen oder Strg+C
echo ========================================
echo.

python apps\wareneingang.py

REM Bei Fehler
if errorlevel 1 (
    echo.
    echo [FEHLER] Anwendung wurde mit Fehler beendet!
    echo.
)

REM Virtuelle Umgebung deaktivieren falls verwendet
if "%USING_VENV%"=="1" (
    deactivate
)

pause