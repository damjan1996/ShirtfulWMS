#!/usr/bin/env python3
"""
Shirtful WMS - Wareneingang App
Hauptanwendungsklasse für die modulare Wareneingang-Station
"""

import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from typing import Dict, Any, Optional
import sys
import os

# Projekt-Root zum Python-Path hinzufügen
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# UI-Komponenten importieren
from .ui import LoginScreen, MainScreen, DeliveryDialog, ScannerDialog, PackageRegistrationDialog

# Services importieren
from .services.auth_service import AuthService
from .services.delivery_service import DeliveryService
from .services.package_service import PackageService

# Utils importieren
from utils.ui_components import COLORS, FONTS
from utils.logger import setup_logger
from config.translations import Translations


class WareneingangApp:
    """
    Hauptanwendungsklasse für die Wareneingang-Station.

    Diese Klasse koordiniert alle UI-Komponenten und Services für eine
    vollständige Wareneingang-Arbeitsstation.
    """

    def __init__(self):
        """Initialisiert die Wareneingang-Anwendung."""
        # Logging einrichten
        self.logger = setup_logger('wareneingang_app')
        self.logger.info("Wareneingang-App wird initialisiert...")

        # Hauptfenster erstellen
        self._create_main_window()

        # Services initialisieren
        self._initialize_services()

        # Anwendungsstatus
        self._initialize_app_state()

        # UI-Komponenten
        self.current_screen = None
        self.login_screen = None
        self.main_screen = None

        self.logger.info("Wareneingang-App erfolgreich initialisiert")

    def _create_main_window(self):
        """Erstellt das Hauptfenster."""
        self.root = tk.Tk()
        self.root.title("Shirtful WMS - Wareneingang")
        self.root.geometry("1024x768")
        self.root.configure(bg=COLORS['background'])

        # Vollbildmodus
        self.root.attributes('-fullscreen', True)

        # Tastenkombinationen
        self.root.bind('<Escape>', self._on_escape)
        self.root.bind('<F11>', self._toggle_fullscreen)
        self.root.bind('<Control-q>', self._on_quit)
        self.root.bind('<Alt-F4>', self._on_quit)

        # Fenster-Ereignisse
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)

        # Icon setzen (falls verfügbar)
        self._set_window_icon()

    def _set_window_icon(self):
        """Setzt das Fenster-Icon."""
        try:
            # Versuche Icon zu setzen (falls vorhanden)
            icon_path = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'icon.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception as e:
            self.logger.debug(f"Icon konnte nicht gesetzt werden: {e}")

    def _initialize_services(self):
        """Initialisiert alle Services."""
        try:
            self.auth_service = AuthService()
            self.delivery_service = DeliveryService()
            self.package_service = PackageService()

            self.logger.info("Services erfolgreich initialisiert")

        except Exception as e:
            self.logger.error(f"Fehler beim Initialisieren der Services: {e}")
            messagebox.showerror(
                "Initialisierungsfehler",
                f"Services konnten nicht initialisiert werden:\n{str(e)}\n\n"
                "Die Anwendung wird möglicherweise nicht korrekt funktionieren."
            )

    def _initialize_app_state(self):
        """Initialisiert den Anwendungsstatus."""
        # Aktueller Benutzer
        self.current_employee = None

        # Aktuelle Lieferung
        self.current_delivery = None

        # Anwendungseinstellungen
        self.settings = {
            'language': 'de',
            'fullscreen': True,
            'auto_logout_minutes': 30,
            'sound_enabled': True
        }

        # Statistiken
        self.session_stats = {
            'start_time': datetime.now(),
            'packages_scanned': 0,
            'deliveries_created': 0,
            'login_time': None
        }

        # Übersetzungen
        self.translations = Translations()
        self.translations.set_language(self.settings['language'])

    def run(self):
        """Startet die Anwendung."""
        try:
            self.logger.info("Starte Wareneingang-Anwendung")

            # Login-Bildschirm anzeigen
            self.show_login_screen()

            # Hauptschleife starten
            self.root.mainloop()

        except Exception as e:
            self.logger.error(f"Kritischer Fehler in Hauptschleife: {e}")
            messagebox.showerror("Kritischer Fehler", str(e))
        finally:
            self._cleanup()

    def show_login_screen(self):
        """Zeigt den Login-Bildschirm."""
        try:
            # Vorherigen Bildschirm aufräumen
            self._cleanup_current_screen()

            # Login-Bildschirm erstellen
            self.login_screen = LoginScreen(
                parent=self.root,
                on_login_success=self._on_employee_login
            )

            # Bildschirm anzeigen
            self.login_screen.setup()
            self.current_screen = 'login'

            self.logger.info("Login-Bildschirm angezeigt")

        except Exception as e:
            self.logger.error(f"Fehler beim Anzeigen des Login-Bildschirms: {e}")
            self._show_error_and_exit(f"Login-Bildschirm konnte nicht angezeigt werden:\n{str(e)}")

    def show_main_screen(self):
        """Zeigt den Hauptbildschirm."""
        try:
            if not self.current_employee:
                raise ValueError("Kein Mitarbeiter angemeldet")

            # Vorherigen Bildschirm aufräumen
            self._cleanup_current_screen()

            # Hauptbildschirm erstellen
            self.main_screen = MainScreen(
                parent=self.root,
                employee=self.current_employee,
                on_logout=self._on_employee_logout
            )

            # Callbacks für Dialoge setzen
            self.main_screen.set_callbacks(
                on_new_delivery=self._show_delivery_dialog,
                on_scan_package=self._show_scanner_dialog,
                on_manual_entry=self._show_manual_entry_dialog
            )

            # Bildschirm anzeigen
            self.main_screen.setup()
            self.current_screen = 'main'

            # Aktuelle Daten laden
            self._sync_main_screen_data()

            self.logger.info("Hauptbildschirm angezeigt")

        except Exception as e:
            self.logger.error(f"Fehler beim Anzeigen des Hauptbildschirms: {e}")
            messagebox.showerror("Fehler", f"Hauptbildschirm konnte nicht angezeigt werden:\n{str(e)}")
            self.show_login_screen()

    def _on_employee_login(self, employee: Dict[str, Any]):
        """
        Behandelt erfolgreiches Mitarbeiter-Login.

        Args:
            employee: Mitarbeiter-Daten
        """
        try:
            self.current_employee = employee
            self.session_stats['login_time'] = datetime.now()

            # Sprache des Mitarbeiters übernehmen
            if 'language' in employee:
                self.settings['language'] = employee['language']
                self.translations.set_language(employee['language'])

            self.logger.info(f"Mitarbeiter angemeldet: {employee['first_name']} {employee['last_name']}")

            # Hauptbildschirm anzeigen
            self.show_main_screen()

        except Exception as e:
            self.logger.error(f"Fehler beim Mitarbeiter-Login: {e}")
            messagebox.showerror("Login-Fehler", f"Login konnte nicht abgeschlossen werden:\n{str(e)}")

    def _on_employee_logout(self):
        """Behandelt Mitarbeiter-Logout."""
        try:
            if self.current_employee:
                user_name = f"{self.current_employee['first_name']} {self.current_employee['last_name']}"
                self.logger.info(f"Mitarbeiter abgemeldet: {user_name}")

            # Session-Daten zurücksetzen
            self._reset_session_data()

            # Login-Bildschirm anzeigen
            self.show_login_screen()

        except Exception as e:
            self.logger.error(f"Fehler beim Logout: {e}")
            messagebox.showerror("Logout-Fehler", f"Logout konnte nicht abgeschlossen werden:\n{str(e)}")

    def _show_delivery_dialog(self):
        """Zeigt den Dialog für neue Lieferungen."""
        try:
            self.logger.info("Lieferungs-Dialog angefordert")

            dialog = DeliveryDialog(
                parent=self.root,
                on_delivery_created=self._on_delivery_created
            )

            delivery_data = dialog.show()

            if delivery_data:
                self.logger.info(f"Lieferungs-Dialog abgeschlossen: {delivery_data.get('supplier', 'Unbekannt')}")
            else:
                self.logger.info("Lieferungs-Dialog abgebrochen")

        except Exception as e:
            self.logger.error(f"Fehler im Lieferungs-Dialog: {e}")
            messagebox.showerror("Dialog-Fehler", f"Lieferungs-Dialog konnte nicht angezeigt werden:\n{str(e)}")

    def _show_scanner_dialog(self):
        """Zeigt den QR-Code Scanner Dialog."""
        try:
            self.logger.info("Scanner-Dialog angefordert")

            dialog = ScannerDialog(
                parent=self.root,
                on_code_scanned=self._on_qr_code_scanned
            )

            dialog.show()

        except Exception as e:
            self.logger.error(f"Fehler im Scanner-Dialog: {e}")
            messagebox.showerror("Dialog-Fehler", f"Scanner-Dialog konnte nicht angezeigt werden:\n{str(e)}")

    def _show_manual_entry_dialog(self):
        """Zeigt den Dialog für manuelle Paketeingabe."""
        try:
            if not self.current_delivery:
                messagebox.showwarning("Warnung", "Bitte zuerst eine Lieferung starten!")
                return

            self.logger.info("Manuelle Eingabe angefordert")

            # Neuen QR-Code generieren
            qr_code = self.package_service.generate_qr_code()

            dialog = PackageRegistrationDialog(
                parent=self.root,
                qr_code=qr_code,
                on_package_registered=self._on_package_registered,
                is_new_package=True
            )

            package_data = dialog.show()

            if package_data:
                self.logger.info(f"Manueller Eintrag abgeschlossen: {qr_code}")
            else:
                self.logger.info("Manueller Eintrag abgebrochen")

        except Exception as e:
            self.logger.error(f"Fehler bei manueller Eingabe: {e}")
            messagebox.showerror("Dialog-Fehler", f"Manuelle Eingabe konnte nicht gestartet werden:\n{str(e)}")

    def _on_delivery_created(self, delivery_data: Dict[str, Any]):
        """
        Behandelt die Erstellung einer neuen Lieferung.

        Args:
            delivery_data: Lieferungs-Daten
        """
        try:
            # Lieferung im Service erstellen
            success, delivery_id, message = self.delivery_service.create_delivery(
                supplier=delivery_data['supplier'],
                delivery_note=delivery_data.get('delivery_note'),
                expected_packages=delivery_data.get('expected_packages', 0),
                notes=delivery_data.get('notes', ''),
                employee_id=self.current_employee['id']
            )

            if success:
                # Aktuelle Lieferung setzen
                delivery_data['id'] = delivery_id
                delivery_data['received_packages'] = 0
                self.current_delivery = delivery_data

                # Session-Statistiken aktualisieren
                self.session_stats['deliveries_created'] += 1

                # Hauptbildschirm aktualisieren
                if self.main_screen:
                    self.main_screen.set_current_delivery(self.current_delivery)

                self.logger.info(f"Lieferung erstellt: {delivery_id}")

            else:
                messagebox.showerror("Fehler", f"Lieferung konnte nicht erstellt werden:\n{message}")

        except Exception as e:
            self.logger.error(f"Fehler beim Erstellen der Lieferung: {e}")
            messagebox.showerror("Fehler", f"Unerwarteter Fehler bei Lieferungserstellung:\n{str(e)}")

    def _on_qr_code_scanned(self, qr_code: str):
        """
        Behandelt gescannte QR-Codes.

        Args:
            qr_code: Gescannter QR-Code
        """
        try:
            if not self.current_delivery:
                messagebox.showwarning("Warnung", "Bitte zuerst eine Lieferung starten!")
                return

            self.logger.info(f"QR-Code gescannt: {qr_code}")

            # Prüfen ob Paket bereits existiert
            existing_package = self.package_service.get_package(qr_code)

            if existing_package:
                # Paket existiert bereits
                messagebox.showinfo(
                    "Paket vorhanden",
                    f"Paket {qr_code} ist bereits registriert.\n"
                    f"Status: {existing_package.get('status', 'Unbekannt')}\n"
                    f"Kunde: {existing_package.get('customer', 'Unbekannt')}"
                )
                return

            # Neues Paket registrieren
            self._show_package_registration_dialog(qr_code, is_new=False)

        except Exception as e:
            self.logger.error(f"Fehler beim Verarbeiten des QR-Codes {qr_code}: {e}")
            messagebox.showerror("Fehler", f"QR-Code konnte nicht verarbeitet werden:\n{str(e)}")

    def _show_package_registration_dialog(self, qr_code: str, is_new: bool = False):
        """
        Zeigt den Paket-Registrierungs-Dialog.

        Args:
            qr_code: QR-Code des Pakets
            is_new: True wenn neues Paket
        """
        try:
            dialog = PackageRegistrationDialog(
                parent=self.root,
                qr_code=qr_code,
                on_package_registered=self._on_package_registered,
                is_new_package=is_new
            )

            package_data = dialog.show()

            if package_data:
                self.logger.info(f"Paket-Registrierung abgeschlossen: {qr_code}")
            else:
                self.logger.info(f"Paket-Registrierung abgebrochen: {qr_code}")

        except Exception as e:
            self.logger.error(f"Fehler im Paket-Registrierungs-Dialog: {e}")
            messagebox.showerror("Dialog-Fehler", f"Paket-Registrierung konnte nicht gestartet werden:\n{str(e)}")

    def _on_package_registered(self, package_data: Dict[str, Any]):
        """
        Behandelt die Registrierung eines Pakets.

        Args:
            package_data: Paket-Daten
        """
        try:
            if not self.current_delivery:
                raise ValueError("Keine aktive Lieferung")

            # Paket im Service registrieren
            success, message = self.package_service.register_package(
                delivery_id=self.current_delivery['id'],
                package_data=package_data
            )

            if success:
                # Lieferung aktualisieren
                self.current_delivery['received_packages'] = self.current_delivery.get('received_packages', 0) + 1

                # Session-Statistiken aktualisieren
                self.session_stats['packages_scanned'] += 1

                # Hauptbildschirm aktualisieren
                if self.main_screen:
                    self.main_screen.add_registered_package(package_data)

                self.logger.info(f"Paket registriert: {package_data['package_id']}")

            else:
                messagebox.showerror("Registrierungsfehler", message)

        except Exception as e:
            self.logger.error(f"Fehler bei Paket-Registrierung: {e}")
            messagebox.showerror("Fehler", f"Paket konnte nicht registriert werden:\n{str(e)}")

    def _sync_main_screen_data(self):
        """Synchronisiert Daten mit dem Hauptbildschirm."""
        if not self.main_screen:
            return

        try:
            # Aktuelle Lieferung setzen
            self.main_screen.set_current_delivery(self.current_delivery)

            # Statistiken aktualisieren
            self.main_screen.update_statistics()

        except Exception as e:
            self.logger.error(f"Fehler beim Synchronisieren der Hauptbildschirm-Daten: {e}")

    def _cleanup_current_screen(self):
        """Räumt den aktuellen Bildschirm auf."""
        try:
            if self.current_screen == 'login' and self.login_screen:
                self.login_screen.destroy()
                self.login_screen = None
            elif self.current_screen == 'main' and self.main_screen:
                self.main_screen.destroy()
                self.main_screen = None

            self.current_screen = None

        except Exception as e:
            self.logger.error(f"Fehler beim Aufräumen des Bildschirms: {e}")

    def _reset_session_data(self):
        """Setzt Session-Daten zurück."""
        # Mitarbeiter-Daten
        self.current_employee = None

        # Lieferungs-Daten
        self.current_delivery = None

        # Session-Statistiken (teilweise) zurücksetzen
        self.session_stats['login_time'] = None
        self.session_stats['packages_scanned'] = 0
        self.session_stats['deliveries_created'] = 0

    def _show_error_and_exit(self, error_message: str):
        """
        Zeigt einen kritischen Fehler und beendet die Anwendung.

        Args:
            error_message: Fehlermeldung
        """
        self.logger.critical(f"Kritischer Fehler: {error_message}")
        messagebox.showerror("Kritischer Fehler", f"{error_message}\n\nDie Anwendung wird beendet.")
        self._exit_application()

    def _on_escape(self, event):
        """Behandelt Escape-Taste."""
        if self.root.attributes('-fullscreen'):
            self.root.attributes('-fullscreen', False)
        else:
            self._on_quit(event)

    def _toggle_fullscreen(self, event):
        """Wechselt Vollbildmodus."""
        current_state = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not current_state)
        self.settings['fullscreen'] = not current_state

    def _on_quit(self, event):
        """Behandelt Beenden-Anfrage."""
        self._confirm_exit()

    def _on_window_close(self):
        """Behandelt Fenster-Schließen."""
        self._confirm_exit()

    def _confirm_exit(self):
        """Bestätigt das Beenden der Anwendung."""
        # Warnung bei aktiver Lieferung
        if self.current_delivery:
            result = messagebox.askyesno(
                "Anwendung beenden",
                "Es gibt eine aktive Lieferung. Trotzdem beenden?\n\n"
                "Die Lieferung bleibt gespeichert und kann später fortgesetzt werden."
            )
            if not result:
                return

        # Session-Zusammenfassung (falls angemeldet)
        if self.current_employee:
            session_duration = datetime.now() - self.session_stats['start_time']
            summary = f"""
Session-Zusammenfassung:

Mitarbeiter: {self.current_employee['first_name']} {self.current_employee['last_name']}
Dauer: {str(session_duration).split('.')[0]}
Lieferungen: {self.session_stats['deliveries_created']}
Pakete: {self.session_stats['packages_scanned']}

Anwendung wirklich beenden?
            """

            result = messagebox.askyesno("Anwendung beenden", summary.strip())
            if not result:
                return

        self._exit_application()

    def _exit_application(self):
        """Beendet die Anwendung sicher."""
        try:
            self.logger.info("Anwendung wird beendet")

            # Cleanup
            self._cleanup()

            # Fenster zerstören
            if self.root:
                self.root.quit()
                self.root.destroy()

        except Exception as e:
            self.logger.error(f"Fehler beim Beenden: {e}")

    def _cleanup(self):
        """Führt Cleanup-Operationen durch."""
        try:
            # Services cleanup
            if hasattr(self, 'auth_service'):
                # Auth-Service cleanup falls implementiert
                pass

            if hasattr(self, 'delivery_service'):
                # Delivery-Service cleanup falls implementiert
                pass

            if hasattr(self, 'package_service'):
                # Package-Service cleanup falls implementiert
                pass

            # UI cleanup
            self._cleanup_current_screen()

            self.logger.info("Cleanup abgeschlossen")

        except Exception as e:
            self.logger.error(f"Fehler beim Cleanup: {e}")

    # Utility-Methoden für externe Verwendung

    def get_current_employee(self) -> Optional[Dict[str, Any]]:
        """
        Gibt den aktuell angemeldeten Mitarbeiter zurück.

        Returns:
            Optional[Dict]: Mitarbeiter-Daten oder None
        """
        return self.current_employee

    def get_current_delivery(self) -> Optional[Dict[str, Any]]:
        """
        Gibt die aktuelle Lieferung zurück.

        Returns:
            Optional[Dict]: Lieferungs-Daten oder None
        """
        return self.current_delivery

    def get_session_statistics(self) -> Dict[str, Any]:
        """
        Gibt Session-Statistiken zurück.

        Returns:
            Dict: Session-Statistiken
        """
        stats = self.session_stats.copy()

        # Berechnete Werte hinzufügen
        if stats['start_time']:
            stats['session_duration'] = datetime.now() - stats['start_time']

        if stats['login_time']:
            stats['logged_in_duration'] = datetime.now() - stats['login_time']

        return stats

    def force_logout(self):
        """Erzwingt Logout (für externe Verwendung)."""
        self._on_employee_logout()

    def force_exit(self):
        """Erzwingt Beenden (für externe Verwendung)."""
        self._exit_application()