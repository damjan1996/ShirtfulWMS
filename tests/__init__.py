"""
Shirtful WMS - Test Package
Unit- und Integrationstests für alle Module.
"""

# Test-Konfiguration
TEST_CONFIG = {
    'use_test_db': True,
    'test_rfid_port': 'COM99',  # Simulierter Port
    'test_camera_index': -1,     # Simulierte Kamera
    'mock_hardware': True,       # Hardware simulieren
}

# Test-Daten
TEST_DATA = {
    'test_employee': {
        'rfid_tag': 'TEST1234',
        'name': 'Test User',
        'department': 'Test',
        'role': 'Tester'
    },
    'test_package': {
        'qr_code': 'PKG-TEST-000001',
        'order_id': 'ORD-TEST-0001',
        'customer': 'Test Customer',
        'item_count': 5
    }
}