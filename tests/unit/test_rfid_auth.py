"""
Unit Tests für RFID-Authentifizierung.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import serial
from utils.rfid_auth import RFIDAuth
from config.rfid_config import RFID_COMMANDS


class TestRFIDAuth:
    """Tests für RFIDAuth Klasse."""

    @patch('serial.Serial')
    @patch('serial.tools.list_ports.comports')
    def test_init_auto_port(self, mock_comports, mock_serial):
        """Test automatische Port-Erkennung."""
        # Mock COM-Ports
        mock_port = Mock()
        mock_port.device = 'COM3'
        mock_port.description = 'USB Serial Port'
        mock_comports.return_value = [mock_port]

        # Mock Serial-Verbindung
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn
        mock_conn.read.return_value = b'\xAA\xBB\x02\x00\x02'  # Mock response

        # RFID initialisieren
        rfid = RFIDAuth()

        assert rfid.port == 'COM3'
        assert rfid.is_connected == True
        mock_serial.assert_called()

    @patch('serial.Serial')
    def test_init_specific_port(self, mock_serial):
        """Test mit spezifischem Port."""
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn
        mock_conn.read.return_value = b'\xAA\xBB\x02\x00\x02'

        rfid = RFIDAuth(port='COM5')

        assert rfid.port == 'COM5'
        assert rfid.baudrate == 9600

    @patch('serial.Serial')
    def test_connect_success(self, mock_serial):
        """Test erfolgreiche Verbindung."""
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn
        mock_conn.read.return_value = b'\xAA\xBB\x02\x00\x02'
        mock_conn.is_open = True

        rfid = RFIDAuth(port='COM3')
        result = rfid.connect()

        assert result == True
        assert rfid.is_connected == True
        mock_conn.write.assert_called_with(RFID_COMMANDS['GET_VERSION'])

    @patch('serial.Serial')
    def test_connect_failure(self, mock_serial):
        """Test fehlgeschlagene Verbindung."""
        mock_serial.side_effect = serial.SerialException("Port not found")

        rfid = RFIDAuth(port='COM99')

        assert rfid.is_connected == False

    @patch('serial.Serial')
    def test_disconnect(self, mock_serial):
        """Test Verbindung trennen."""
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn
        mock_conn.is_open = True

        rfid = RFIDAuth(port='COM3')
        rfid.disconnect()

        assert rfid.is_connected == False
        mock_conn.close.assert_called_once()

    @patch('serial.Serial')
    def test_read_tag_success(self, mock_serial):
        """Test erfolgreiches Tag-Lesen."""
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn

        # Mock RFID Response für Tag "12345678"
        mock_response = b'\xAA\xBB\x06\x00\x12\x34\x56\x78\x00\x00'
        mock_conn.read.return_value = mock_response
        mock_conn.in_waiting = len(mock_response)

        rfid = RFIDAuth(port='COM3')
        tag_id = rfid.read_tag()

        assert tag_id == "12345678"
        mock_conn.write.assert_called_with(RFID_COMMANDS['READ_TAG_ONCE'])

    @patch('serial.Serial')
    def test_read_tag_no_tag(self, mock_serial):
        """Test Lesen ohne Tag."""
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn
        mock_conn.read.return_value = b''

        rfid = RFIDAuth(port='COM3')
        tag_id = rfid.read_tag()

        assert tag_id is None

    @patch('serial.Serial')
    def test_beep(self, mock_serial):
        """Test Beep-Funktion."""
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn

        rfid = RFIDAuth(port='COM3')
        rfid.beep(100)

        mock_conn.write.assert_called_with(RFID_COMMANDS['BEEP'])

    @patch('serial.Serial')
    @patch('threading.Thread')
    def test_continuous_read_start(self, mock_thread, mock_serial):
        """Test Start kontinuierliches Lesen."""
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn

        callback = Mock()
        rfid = RFIDAuth(port='COM3')
        rfid.start_continuous_read(callback)

        assert rfid.tag_callback == callback
        mock_thread.assert_called_once()
        mock_conn.write.assert_called_with(RFID_COMMANDS['READ_TAG_CONTINUOUS'])

    @patch('serial.Serial')
    def test_continuous_read_stop(self, mock_serial):
        """Test Stop kontinuierliches Lesen."""
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn

        rfid = RFIDAuth(port='COM3')
        rfid.stop_continuous_read()

        assert rfid.stop_reading.is_set()
        mock_conn.write.assert_called_with(RFID_COMMANDS['STOP_CONTINUOUS'])

    def test_parse_tag_response_valid(self):
        """Test Parsen einer gültigen Tag-Antwort."""
        rfid = RFIDAuth(port='COM3')

        # Gültige Response mit Tag "ABCD1234"
        response = b'\xAA\xBB\x06\x00\xAB\xCD\x12\x34\x00\x00'
        tag_id = rfid._parse_tag_response(response)

        assert tag_id == "ABCD1234"

    def test_parse_tag_response_invalid(self):
        """Test Parsen einer ungültigen Antwort."""
        rfid = RFIDAuth(port='COM3')

        # Zu kurze Response
        response = b'\xAA\xBB'
        tag_id = rfid._parse_tag_response(response)

        assert tag_id is None

    def test_parse_tag_response_wrong_header(self):
        """Test Parsen mit falschem Header."""
        rfid = RFIDAuth(port='COM3')

        # Falscher Header
        response = b'\xFF\xFF\x06\x00\x12\x34\x56\x78\x00\x00'
        tag_id = rfid._parse_tag_response(response)

        assert tag_id is None

    @patch('serial.Serial')
    def test_get_reader_info(self, mock_serial):
        """Test Reader-Info abrufen."""
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn
        mock_conn.read.return_value = b'TSHRW380BZMP V1.0'

        rfid = RFIDAuth(port='COM3')
        info = rfid.get_reader_info()

        assert info['connected'] == True
        assert info['port'] == 'COM3'
        assert info['baudrate'] == 9600
        assert info['model'] == 'TSHRW380BZMP'
        assert 'version' in info

    @patch('serial.Serial')
    def test_test_connection_success(self, mock_serial):
        """Test Verbindungstest erfolgreich."""
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn
        mock_conn.read.return_value = b'\xAA\xBB\x02\x00\x02'

        rfid = RFIDAuth(port='COM3')
        result = rfid.test_connection()

        assert result == True

    @patch('serial.Serial')
    def test_test_connection_failure(self, mock_serial):
        """Test Verbindungstest fehlgeschlagen."""
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn
        mock_conn.write.side_effect = serial.SerialException("Write failed")

        rfid = RFIDAuth(port='COM3')
        result = rfid.test_connection()

        assert result == False

    @patch('serial.Serial')
    def test_continuous_read_callback(self, mock_serial):
        """Test Callback bei kontinuierlichem Lesen."""
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn

        # Mock Response
        mock_conn.in_waiting = 10
        mock_conn.read.return_value = b'\xAA\xBB\x06\x00\x12\x34\x56\x78\x00\x00'

        callback = Mock()
        rfid = RFIDAuth(port='COM3')

        # Simuliere Scan-Loop
        rfid.tag_callback = callback
        rfid.stop_reading.clear()

        # Einmal durchlaufen
        tag_id = rfid._parse_tag_response(mock_conn.read())
        if tag_id:
            callback(tag_id)

        callback.assert_called_once_with("12345678")

    def test_calculate_checksum(self):
        """Test Checksum-Berechnung."""
        from config.rfid_config import calculate_checksum

        # Test-Daten
        data = b'\xAA\xBB\x02\x20'
        checksum = calculate_checksum(data)

        assert checksum == 0x22  # 0x02 XOR 0x20

    def test_build_command(self):
        """Test Kommando-Erstellung."""
        from config.rfid_config import build_command

        # Basis-Kommando
        base = b'\xAA\xBB\x03\x50'
        cmd = build_command(base, 0x01)

        # Erwartetes Ergebnis: AA BB 03 50 01 52 (Checksum = 0x03 XOR 0x50 XOR 0x01)
        assert cmd == b'\xAA\xBB\x03\x50\x01\x52'


class TestRFIDAuthIntegration:
    """Integrationstests für RFID (mit Mock-Hardware)."""

    @pytest.mark.integration
    @patch('serial.Serial')
    def test_full_workflow(self, mock_serial):
        """Test kompletter Workflow: Connect -> Read -> Disconnect."""
        mock_conn = MagicMock()
        mock_serial.return_value = mock_conn

        # Mock Responses
        mock_conn.read.side_effect = [
            b'\xAA\xBB\x02\x00\x02',  # Version response
            b'\xAA\xBB\x06\x00\x12\x34\x56\x78\x00\x00'  # Tag response
        ]

        # Workflow
        rfid = RFIDAuth(port='COM3')
        assert rfid.is_connected == True

        tag = rfid.read_tag()
        assert tag == "12345678"

        rfid.disconnect()
        assert rfid.is_connected == False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])