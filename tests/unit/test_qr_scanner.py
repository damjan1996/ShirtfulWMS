"""
Unit-Tests für das QR-Scanner-Modul

Diese Tests prüfen die QR-Code-Scanning-Funktionalität
ohne echte Kamera-Hardware zu benötigen.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, call
import cv2
import numpy as np
from pyzbar.pyzbar import ZBarSymbol
import threading
import time
import queue

from utils.qr_scanner import (
    QRScanner, QRCodeData, ScanResult,
    CameraError, ScanTimeoutError, InvalidQRCodeError
)


class TestQRScanner(unittest.TestCase):
    """Tests für die QRScanner-Klasse."""

    def setUp(self):
        """Setup für jeden Test."""
        # Mock cv2.VideoCapture
        self.mock_capture = Mock()
        self.capture_patcher = patch('cv2.VideoCapture')
        self.mock_video_capture = self.capture_patcher.start()
        self.mock_video_capture.return_value = self.mock_capture

        # Mock pyzbar.decode
        self.decode_patcher = patch('pyzbar.pyzbar.decode')
        self.mock_decode = self.decode_patcher.start()

        # Default Mock-Verhalten
        self.mock_capture.isOpened.return_value = True
        self.mock_capture.read.return_value = (True, self.create_test_frame())

        self.scanner = None

    def tearDown(self):
        """Cleanup nach jedem Test."""
        self.capture_patcher.stop()
        self.decode_patcher.stop()

        if self.scanner:
            self.scanner.close()

    def create_test_frame(self, width=640, height=480):
        """Erstellt ein Test-Bild."""
        return np.zeros((height, width, 3), dtype=np.uint8)

    def create_mock_qr_result(self, data="PKG-2024-001", type_=ZBarSymbol.QRCODE):
        """Erstellt ein Mock QR-Code Scan-Ergebnis."""
        mock_result = Mock()
        mock_result.data = data.encode('utf-8')
        mock_result.type = type_
        mock_result.rect = Mock(left=100, top=100, width=200, height=200)
        mock_result.polygon = [(100, 100), (300, 100), (300, 300), (100, 300)]
        return mock_result

    def test_scanner_initialization(self):
        """Test der Scanner-Initialisierung."""
        scanner = QRScanner(camera_index=0)

        # Verifiziere VideoCapture wurde mit richtigem Index erstellt
        self.mock_video_capture.assert_called_once_with(0)

        # Verifiziere Kamera-Einstellungen
        expected_calls = [
            call(cv2.CAP_PROP_FRAME_WIDTH, 1280),
            call(cv2.CAP_PROP_FRAME_HEIGHT, 720),
            call(cv2.CAP_PROP_FPS, 30)
        ]

        for expected_call in expected_calls:
            self.assertIn(expected_call, self.mock_capture.set.call_args_list)

    def test_camera_not_available(self):
        """Test wenn keine Kamera verfügbar ist."""
        self.mock_capture.isOpened.return_value = False

        with self.assertRaises(CameraError) as context:
            QRScanner()

        self.assertIn("Camera not available", str(context.exception))

    def test_scan_single_qr_code(self):
        """Test des Scannens eines einzelnen QR-Codes."""
        scanner = QRScanner()

        # Mock QR-Code gefunden
        mock_qr = self.create_mock_qr_result("PKG-2024-001")
        self.mock_decode.return_value = [mock_qr]

        result = scanner.scan_single()

        # Verifiziere Ergebnis
        self.assertEqual(result.data, "PKG-2024-001")
        self.assertEqual(result.type, "QRCODE")
        self.assertTrue(result.success)

        # Verifiziere Kamera wurde gestoppt
        self.mock_capture.release.assert_called_once()

    def test_scan_timeout(self):
        """Test des Scan-Timeouts."""
        scanner = QRScanner(scan_timeout=1)  # 1 Sekunde Timeout

        # Mock keine QR-Codes gefunden
        self.mock_decode.return_value = []

        start_time = time.time()

        with self.assertRaises(ScanTimeoutError):
            scanner.scan_single()

        elapsed_time = time.time() - start_time

        # Timeout sollte nach etwa 1 Sekunde auftreten
        self.assertAlmostEqual(elapsed_time, 1.0, delta=0.2)

    def test_scan_from_webcam(self):
        """Test der interaktiven Webcam-Scan-Funktion."""
        scanner = QRScanner()

        # Mock QR-Code nach 3 Frames
        self.mock_decode.side_effect = [
            [],  # Frame 1: Kein QR-Code
            [],  # Frame 2: Kein QR-Code
            [self.create_mock_qr_result("PKG-2024-002")]  # Frame 3: QR-Code gefunden
        ]

        # Mock cv2.imshow und cv2.waitKey
        with patch('cv2.imshow'), \
                patch('cv2.waitKey', return_value=-1):
            result = scanner.scan_from_webcam()

        self.assertEqual(result, "PKG-2024-002")
        self.assertEqual(self.mock_decode.call_count, 3)

    def test_scan_multiple_qr_codes(self):
        """Test des Scannens mehrerer QR-Codes gleichzeitig."""
        scanner = QRScanner()

        # Mock mehrere QR-Codes im Bild
        mock_qrs = [
            self.create_mock_qr_result("PKG-2024-001"),
            self.create_mock_qr_result("PKG-2024-002"),
            self.create_mock_qr_result("PKG-2024-003")
        ]
        self.mock_decode.return_value = mock_qrs

        results = scanner.scan_multiple()

        # Verifiziere alle QR-Codes wurden erkannt
        self.assertEqual(len(results), 3)
        self.assertEqual([r.data for r in results],
                         ["PKG-2024-001", "PKG-2024-002", "PKG-2024-003"])

    def test_qr_code_validation(self):
        """Test der QR-Code-Validierung."""
        scanner = QRScanner()

        # Test gültige Formate
        valid_formats = [
            "PKG-2024-001",
            "PKG-2024-999",
            "ORD-2024-12345",
            "SHIP-2024-001"
        ]

        for qr_data in valid_formats:
            self.assertTrue(
                scanner.validate_qr_code(qr_data),
                f"{qr_data} should be valid"
            )

        # Test ungültige Formate
        invalid_formats = [
            "INVALID",
            "PKG2024001",  # Keine Bindestriche
            "PKG-24-001",  # Falsches Jahr-Format
            "PKG-2024",  # Fehlende Nummer
            "",  # Leer
            "PKG-2024-ABC"  # Buchstaben statt Zahlen
        ]

        for qr_data in invalid_formats:
            self.assertFalse(
                scanner.validate_qr_code(qr_data),
                f"{qr_data} should be invalid"
            )

    def test_barcode_support(self):
        """Test der Unterstützung verschiedener Barcode-Typen."""
        scanner = QRScanner()

        # Test verschiedene Barcode-Typen
        barcode_types = [
            (ZBarSymbol.QRCODE, "QRCODE"),
            (ZBarSymbol.CODE128, "CODE128"),
            (ZBarSymbol.EAN13, "EAN13"),
            (ZBarSymbol.DATAMATRIX, "DATAMATRIX")
        ]

        for symbol_type, expected_name in barcode_types:
            mock_result = self.create_mock_qr_result("TEST123", symbol_type)
            self.mock_decode.return_value = [mock_result]

            result = scanner.scan_single()

            self.assertEqual(result.type, expected_name)

    def test_frame_preprocessing(self):
        """Test der Bildvorverarbeitung für bessere Erkennung."""
        scanner = QRScanner(enable_preprocessing=True)

        # Erstelle ein Test-Frame
        test_frame = self.create_test_frame()

        # Mock decode mit Preprocessing-Check
        def decode_with_check(frame, symbols=None):
            # Verifiziere, dass Frame vorverarbeitet wurde
            # (Grayscale hat nur 2 Dimensionen)
            if len(frame.shape) == 2:
                return [self.create_mock_qr_result("PREPROCESSED")]
            return []

        self.mock_decode.side_effect = decode_with_check

        result = scanner.scan_single()

        self.assertEqual(result.data, "PREPROCESSED")

    def test_continuous_scanning(self):
        """Test des kontinuierlichen Scan-Modus."""
        scanner = QRScanner()
        results = []

        # Mock QR-Codes über Zeit
        scan_sequence = [
            [],  # Frame 1-2: Nichts
            [],
            [self.create_mock_qr_result("PKG-2024-001")],  # Frame 3: Erster QR
            [],  # Frame 4-5: Nichts
            [],
            [self.create_mock_qr_result("PKG-2024-002")],  # Frame 6: Zweiter QR
        ]
        self.mock_decode.side_effect = scan_sequence

        def callback(qr_data):
            results.append(qr_data)
            if len(results) >= 2:
                scanner.stop_continuous_scan()

        # Starte kontinuierlichen Scan
        scanner.start_continuous_scan(callback)

        # Warte kurz
        time.sleep(0.5)

        # Verifiziere beide QR-Codes wurden gescannt
        self.assertEqual(len(results), 2)
        self.assertEqual(results, ["PKG-2024-001", "PKG-2024-002"])

    def test_camera_reconnection(self):
        """Test der automatischen Kamera-Wiederverbindung."""
        scanner = QRScanner(auto_reconnect=True)

        # Simuliere Kamera-Verbindungsverlust
        self.mock_capture.read.side_effect = [
            (True, self.create_test_frame()),  # Frame 1: OK
            (False, None),  # Frame 2: Fehler
            (False, None),  # Frame 3: Fehler
            (True, self.create_test_frame()),  # Frame 4: Wieder OK
        ]

        # QR-Code nach Wiederverbindung
        self.mock_decode.side_effect = [
            [],  # Frame 1
            [],  # Frames 2-3 werden übersprungen
            [],
            [self.create_mock_qr_result("RECONNECTED")]  # Frame 4
        ]

        result = scanner.scan_single()

        self.assertEqual(result.data, "RECONNECTED")
        # Verifiziere Reconnect wurde versucht
        self.assertGreater(self.mock_capture.release.call_count, 0)

    def test_performance_metrics(self):
        """Test der Performance-Metriken."""
        scanner = QRScanner(collect_metrics=True)

        # Mock schnelle QR-Code Erkennung
        self.mock_decode.return_value = [self.create_mock_qr_result("FAST")]

        result = scanner.scan_single()
        metrics = scanner.get_metrics()

        # Verifiziere Metriken wurden gesammelt
        self.assertIn('scan_time', metrics)
        self.assertIn('frames_processed', metrics)
        self.assertIn('fps', metrics)

        self.assertGreater(metrics['frames_processed'], 0)
        self.assertGreater(metrics['fps'], 0)

    def test_error_recovery(self):
        """Test der Fehlerbehandlung und -wiederherstellung."""
        scanner = QRScanner()

        # Simuliere verschiedene Fehler
        errors = [
            cv2.error("OpenCV error"),
            ValueError("Decode error"),
            None  # Dann Erfolg
        ]

        call_count = 0

        def decode_with_errors(frame, symbols=None):
            nonlocal call_count
            if call_count < len(errors) - 1:
                error = errors[call_count]
                call_count += 1
                if error:
                    raise error
            return [self.create_mock_qr_result("RECOVERED")]

        self.mock_decode.side_effect = decode_with_errors

        # Scanner sollte Fehler behandeln und weitermachen
        result = scanner.scan_single()

        self.assertEqual(result.data, "RECOVERED")
        self.assertEqual(call_count, 2)  # Zwei Fehler vor Erfolg

    def test_custom_decoder_settings(self):
        """Test benutzerdefinierter Decoder-Einstellungen."""
        # Test mit spezifischen Barcode-Typen
        scanner = QRScanner(
            supported_formats=[ZBarSymbol.QRCODE, ZBarSymbol.CODE128]
        )

        # Verifiziere decode wird mit richtigen Symbolen aufgerufen
        scanner.scan_single()

        decode_call = self.mock_decode.call_args
        symbols_arg = decode_call[1].get('symbols', [])

        self.assertIn(ZBarSymbol.QRCODE, symbols_arg)
        self.assertIn(ZBarSymbol.CODE128, symbols_arg)

    def test_scan_region_of_interest(self):
        """Test des Scannens nur in einem bestimmten Bildbereich."""
        scanner = QRScanner()

        # Definiere Region of Interest (ROI)
        roi = (100, 100, 400, 300)  # x, y, width, height

        # Mock QR-Code in ROI
        self.mock_decode.return_value = [self.create_mock_qr_result("IN_ROI")]

        result = scanner.scan_single(roi=roi)

        # Verifiziere nur ROI wurde gescannt
        decode_call = self.mock_decode.call_args[0][0]

        # Frame sollte zugeschnitten sein
        expected_shape = (300, 400)  # height, width der ROI
        self.assertEqual(decode_call.shape[:2], expected_shape)

    def test_threading_safety(self):
        """Test der Thread-Sicherheit bei mehreren gleichzeitigen Scans."""
        scanner = QRScanner()
        results = []
        errors = []

        def scan_thread(thread_id):
            try:
                # Mock unterschiedliche QR-Codes für jeden Thread
                with patch.object(self.mock_decode, 'return_value',
                                  [self.create_mock_qr_result(f"THREAD-{thread_id}")]):
                    result = scanner.scan_single()
                    results.append((thread_id, result.data))
            except Exception as e:
                errors.append((thread_id, str(e)))

        # Starte mehrere Threads
        threads = []
        for i in range(5):
            t = threading.Thread(target=scan_thread, args=(i,))
            threads.append(t)
            t.start()

        # Warte auf alle Threads
        for t in threads:
            t.join(timeout=5)

        # Verifiziere keine Fehler und alle Threads erfolgreich
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(results), 5)


class TestQRCodeData(unittest.TestCase):
    """Tests für die QRCodeData-Klasse."""

    def test_qr_code_data_creation(self):
        """Test der QRCodeData-Erstellung."""
        data = QRCodeData(
            raw_data="PKG-2024-001",
            format="QRCODE",
            position=(100, 100, 200, 200),
            timestamp=datetime.now()
        )

        self.assertEqual(data.raw_data, "PKG-2024-001")
        self.assertEqual(data.format, "QRCODE")
        self.assertIsNotNone(data.timestamp)

    def test_qr_code_data_parsing(self):
        """Test des Parsens von QR-Code-Daten."""
        # Test Paket-QR-Code
        data = QRCodeData("PKG-2024-001")
        parsed = data.parse()

        self.assertEqual(parsed['type'], 'package')
        self.assertEqual(parsed['year'], '2024')
        self.assertEqual(parsed['number'], '001')

        # Test Bestell-QR-Code
        data = QRCodeData("ORD-2024-12345")
        parsed = data.parse()

        self.assertEqual(parsed['type'], 'order')
        self.assertEqual(parsed['number'], '12345')

    def test_qr_code_data_validation(self):
        """Test der Datenvalidierung."""
        # Gültiger QR-Code
        data = QRCodeData("PKG-2024-001")
        self.assertTrue(data.is_valid())

        # Ungültiger QR-Code
        data = QRCodeData("INVALID-DATA")
        self.assertFalse(data.is_valid())

    def test_qr_code_data_json_serialization(self):
        """Test der JSON-Serialisierung."""
        data = QRCodeData(
            raw_data="PKG-2024-001",
            format="QRCODE",
            position=(100, 100, 200, 200)
        )

        json_data = data.to_json()

        self.assertIn('raw_data', json_data)
        self.assertIn('format', json_data)
        self.assertIn('position', json_data)
        self.assertIn('timestamp', json_data)

        # Test Deserialisierung
        restored = QRCodeData.from_json(json_data)
        self.assertEqual(restored.raw_data, data.raw_data)


if __name__ == '__main__':
    unittest.main()