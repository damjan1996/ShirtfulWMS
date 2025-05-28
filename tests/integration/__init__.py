"""
Integration Tests Package für Shirtful WMS

Dieses Paket enthält Integrationstests, die mehrere Komponenten
des Systems zusammen testen.
"""

# Gemeinsame Imports für alle Integrationstests
from pathlib import Path
import sys

# Füge den Projektpfad zum Python-Pfad hinzu
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Test-Konfiguration für Integrationstests
TEST_DATABASE = "ShirtfulWMS_Test"
TEST_RFID_PORT = "COM_TEST"
TEST_TIMEOUT = 30  # Sekunden

# Gemeinsame Test-Fixtures können hier definiert werden
__all__ = ['TEST_DATABASE', 'TEST_RFID_PORT', 'TEST_TIMEOUT']