"""
QR-Code Scanner für Shirtful WMS
Verwaltet das Scannen von QR-Codes über Webcam.
"""

import cv2
import numpy as np
from pyzbar import pyzbar
from pyzbar.pyzbar import ZBarSymbol
import logging
import threading
import time
from typing import Optional, Callable, List, Tuple
from datetime import datetime
import qrcode
from PIL import Image, ImageDraw, ImageFont
import io


class QRScanner:
    """Klasse für QR-Code Scanning mit Webcam."""

    def __init__(self, camera_index: int = 0):
        """
        Initialisiert den QR-Scanner.

        Args:
            camera_index: Index der Kamera (0 für Standard-Webcam)
        """
        self.logger = logging.getLogger(__name__)
        self.camera_index = camera_index
        self.capture = None
        self.is_scanning = False
        self.scan_thread = None
        self.scan_callback = None
        self.last_scanned_code = None
        self.last_scan_time = 0
        self.duplicate_timeout = 2.0  # Sekunden

        # Scanner-Einstellungen
        self.scan_interval = 0.1  # Scan alle 100ms
        self.min_qr_size = 50  # Minimale QR-Code Größe in Pixeln
        self.roi_enabled = False  # Region of Interest
        self.roi_rect = None

        # Kamera-Einstellungen
        self.resolution = (1280, 720)
        self.autofocus = True

    def start_camera(self) -> bool:
        """
        Startet die Kamera.

        Returns:
            True bei Erfolg
        """
        try:
            if self.capture and self.capture.isOpened():
                self.capture.release()

            self.capture = cv2.VideoCapture(self.camera_index)

            # Kamera-Einstellungen
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])

            # Autofokus aktivieren wenn möglich
            if self.autofocus:
                self.capture.set(cv2.CAP_PROP_AUTOFOCUS, 1)

            # Test-Frame
            ret, frame = self.capture.read()
            if ret and frame is not None:
                self.logger.info(f"Kamera {self.camera_index} gestartet")
                return True
            else:
                self.logger.error("Kamera liefert keine Bilder")
                return False

        except Exception as e:
            self.logger.error(f"Fehler beim Starten der Kamera: {e}")
            return False

    def stop_camera(self):
        """Stoppt die Kamera."""
        if self.capture and self.capture.isOpened():
            self.capture.release()
            self.logger.info("Kamera gestoppt")

    def scan_once(self) -> Optional[str]:
        """
        Führt einen einzelnen Scan durch.

        Returns:
            QR-Code Inhalt oder None
        """
        if not self.capture or not self.capture.isOpened():
            if not self.start_camera():
                return None

        try:
            ret, frame = self.capture.read()
            if not ret or frame is None:
                return None

            # QR-Codes im Frame suchen
            codes = self._detect_qr_codes(frame)

            if codes:
                # Ersten gültigen Code zurückgeben
                for code in codes:
                    if self._is_valid_code(code):
                        self.logger.info(f"QR-Code gescannt: {code}")
                        return code

        except Exception as e:
            self.logger.error(f"Fehler beim Scannen: {e}")

        return None

    def start_continuous_scan(self, callback: Callable[[str], None]):
        """
        Startet kontinuierliches Scannen.

        Args:
            callback: Funktion die bei jedem neuen Code aufgerufen wird
        """
        if self.is_scanning:
            return

        self.scan_callback = callback
        self.is_scanning = True

        # Kamera starten
        if not self.capture or not self.capture.isOpened():
            if not self.start_camera():
                self.logger.error("Kamera konnte nicht gestartet werden")
                return

        # Scan-Thread starten
        self.scan_thread = threading.Thread(target=self._scan_loop)
        self.scan_thread.daemon = True
        self.scan_thread.start()

        self.logger.info("Kontinuierliches Scannen gestartet")

    def stop_continuous_scan(self):
        """Stoppt kontinuierliches Scannen."""
        self.is_scanning = False

        if self.scan_thread and self.scan_thread.is_alive():
            self.scan_thread.join(timeout=2)

        self.logger.info("Kontinuierliches Scannen gestoppt")

    def _scan_loop(self):
        """Thread-Funktion für kontinuierliches Scannen."""
        while self.is_scanning:
            try:
                ret, frame = self.capture.read()
                if not ret or frame is None:
                    time.sleep(0.1)
                    continue

                # QR-Codes suchen
                codes = self._detect_qr_codes(frame)

                for code in codes:
                    if self._is_valid_code(code) and not self._is_duplicate(code):
                        self.last_scanned_code = code
                        self.last_scan_time = time.time()

                        # Callback aufrufen
                        if self.scan_callback:
                            self.scan_callback(code)

                time.sleep(self.scan_interval)

            except Exception as e:
                self.logger.error(f"Fehler im Scan-Loop: {e}")
                time.sleep(0.5)

    def _detect_qr_codes(self, frame: np.ndarray) -> List[str]:
        """
        Erkennt QR-Codes in einem Frame.

        Args:
            frame: Bild als numpy Array

        Returns:
            Liste von QR-Code Inhalten
        """
        codes = []

        try:
            # Graustufen für bessere Erkennung
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Kontrast erhöhen
            gray = cv2.equalizeHist(gray)

            # ROI anwenden wenn aktiviert
            if self.roi_enabled and self.roi_rect:
                x, y, w, h = self.roi_rect
                gray = gray[y:y + h, x:x + w]

            # QR-Codes dekodieren
            decoded_codes = pyzbar.decode(gray, symbols=[ZBarSymbol.QRCODE])

            for obj in decoded_codes:
                # Größe prüfen
                (x, y, w, h) = obj.rect
                if w >= self.min_qr_size and h >= self.min_qr_size:
                    code_data = obj.data.decode('utf-8')
                    codes.append(code_data)

        except Exception as e:
            self.logger.debug(f"Fehler bei QR-Erkennung: {e}")

        return codes

    def _is_valid_code(self, code: str) -> bool:
        """
        Prüft ob ein QR-Code gültig ist.

        Args:
            code: QR-Code Inhalt

        Returns:
            True wenn gültig
        """
        # Basis-Validierung
        if not code or len(code) < 5:
            return False

        # Shirtful-spezifische Validierung
        # Format: PKG-YYYY-XXXXXX
        if code.startswith("PKG-"):
            parts = code.split("-")
            if len(parts) == 3:
                try:
                    year = int(parts[1])
                    if 2020 <= year <= 2030:
                        return True
                except ValueError:
                    pass

        return False

    def _is_duplicate(self, code: str) -> bool:
        """
        Prüft ob ein Code ein Duplikat ist.

        Args:
            code: QR-Code Inhalt

        Returns:
            True wenn Duplikat
        """
        current_time = time.time()

        if (self.last_scanned_code == code and
                (current_time - self.last_scan_time) < self.duplicate_timeout):
            return True

        return False

    def get_camera_frame(self) -> Optional[np.ndarray]:
        """
        Holt das aktuelle Kamera-Bild.

        Returns:
            Frame als numpy Array oder None
        """
        if not self.capture or not self.capture.isOpened():
            return None

        ret, frame = self.capture.read()
        return frame if ret else None

    def get_camera_frame_with_overlay(self) -> Optional[np.ndarray]:
        """
        Holt Kamera-Bild mit QR-Code Overlay.

        Returns:
            Frame mit Markierungen oder None
        """
        frame = self.get_camera_frame()
        if frame is None:
            return None

        # QR-Codes erkennen und markieren
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        decoded_codes = pyzbar.decode(gray, symbols=[ZBarSymbol.QRCODE])

        for obj in decoded_codes:
            # Rechteck um QR-Code zeichnen
            (x, y, w, h) = obj.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Text hinzufügen
            text = obj.data.decode('utf-8')
            cv2.putText(frame, text, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # ROI anzeigen wenn aktiviert
        if self.roi_enabled and self.roi_rect:
            x, y, w, h = self.roi_rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.putText(frame, "Scan-Bereich", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

        return frame

    def set_roi(self, x: int, y: int, width: int, height: int):
        """
        Setzt die Region of Interest für das Scannen.

        Args:
            x, y: Startposition
            width, height: Größe der Region
        """
        self.roi_rect = (x, y, width, height)
        self.roi_enabled = True
        self.logger.info(f"ROI gesetzt: {self.roi_rect}")

    def clear_roi(self):
        """Deaktiviert die Region of Interest."""
        self.roi_enabled = False
        self.roi_rect = None
        self.logger.info("ROI deaktiviert")

    def list_available_cameras(self) -> List[Tuple[int, str]]:
        """
        Listet verfügbare Kameras auf.

        Returns:
            Liste von (Index, Name) Tupeln
        """
        cameras = []

        for i in range(10):  # Teste erste 10 Indizes
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    cameras.append((i, f"Kamera {i}"))
                cap.release()

        return cameras

    @staticmethod
    def generate_qr_code(data: str, size: int = 300) -> Image.Image:
        """
        Generiert einen QR-Code.

        Args:
            data: Daten für den QR-Code
            size: Größe des Bildes in Pixeln

        Returns:
            QR-Code als PIL Image
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        qr.add_data(data)
        qr.make(fit=True)

        # QR-Code Bild erstellen
        img = qr.make_image(fill_color="black", back_color="white")

        # Auf gewünschte Größe skalieren
        img = img.resize((size, size), Image.Resampling.NEAREST)

        # Label hinzufügen
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()

        text_bbox = draw.textbbox((0, 0), data, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        x = (size - text_width) // 2
        y = size - text_height - 10

        draw.text((x, y), data, fill="black", font=font)

        return img

    def __del__(self):
        """Destruktor - Kamera freigeben."""
        self.stop_continuous_scan()
        self.stop_camera()


# Test-Funktionen für Entwicklung
if __name__ == "__main__":
    # Logger konfigurieren
    logging.basicConfig(level=logging.DEBUG)

    # Scanner initialisieren
    scanner = QRScanner()

    # Verfügbare Kameras anzeigen
    cameras = scanner.list_available_cameras()
    print(f"Verfügbare Kameras: {cameras}")

    # QR-Code generieren
    qr_img = QRScanner.generate_qr_code("PKG-2024-001234")
    qr_img.save("test_qr.png")
    print("Test QR-Code generiert: test_qr.png")

    # Einmal-Scan testen
    print("\nStarte Einmal-Scan...")
    code = scanner.scan_once()
    if code:
        print(f"Gescannt: {code}")
    else:
        print("Kein Code gescannt")

    # Kontinuierliches Scannen testen
    print("\nStarte kontinuierliches Scannen (30 Sekunden)...")


    def on_scan(code):
        print(f"Neuer Code: {code}")


    scanner.start_continuous_scan(on_scan)

    try:
        # Preview-Fenster (optional)
        print("Drücke 'q' im Fenster zum Beenden")
        while True:
            frame = scanner.get_camera_frame_with_overlay()
            if frame is not None:
                cv2.imshow("QR Scanner", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            time.sleep(0.033)  # ~30 FPS

    except KeyboardInterrupt:
        print("\nBeende...")

    scanner.stop_continuous_scan()
    scanner.stop_camera()
    cv2.destroyAllWindows()