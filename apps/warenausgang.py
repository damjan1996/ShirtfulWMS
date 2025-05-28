#!/usr/bin/env python3
"""
Shirtful WMS - Warenausgang Station
Anwendung für die Warenausgangsstation im Warenprozess.
"""

import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime, date
import sys
import os

# Projekt-Root zum Python-Path hinzufügen
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.rfid_auth import RFIDAuth
from utils.database import Database
from utils.qr_scanner import QRScanner
from utils.ui_components import UIComponents, COLORS, FONTS
from utils.logger import setup_logger
from config.translations import Translations


class WarenausgangApp:
    """Hauptanwendung für die Warenausgangsstation."""

    def __init__(self):
        """Initialisiert die Warenausgang-Anwendung."""
        self.root = tk.Tk()
        self.root.title("Shirtful WMS - Warenausgang")
        self.root.geometry("1024x768")
        self.root.configure(bg=COLORS['background'])

        # Vollbildmodus
        self.root.attributes('-fullscreen', True)
        self.root.bind('<Escape>', lambda e: self.root.attributes('-fullscreen', False))
        self.root.bind('<F11>', lambda e: self.root.attributes('-fullscreen', True))

        # Logger einrichten
        self.logger = setup_logger('warenausgang')
        self.logger.info("Warenausgang-App gestartet")

        # Komponenten initialisieren
        self.rfid = RFIDAuth()
        self.db = Database()
        self.qr_scanner = QRScanner()
        self.ui = UIComponents()
        self.translations = Translations()

        # App-Status
        self.current_user = None
        self.current_package = None
        self.language = 'de'
        self.scanned_packages = []  # Liste für Batch-Versand

        # Versandarten
        self.shipping_methods = [
            "DHL Express",
            "DHL Standard",
            "UPS",
            "DPD",
            "GLS",
            "Hermes",
            "Selbstabholung"
        ]

        # UI erstellen
        self.setup_login_screen()

    def setup_login_screen(self):
        """Erstellt den Login-Bildschirm."""
        self.clear_screen()

        # Hauptcontainer
        main_frame = tk.Frame(self.root, bg=COLORS['background'])
        main_frame.pack(expand=True, fill='both', padx=50, pady=50)

        # Logo/Titel
        title_label = tk.Label(
            main_frame,
            text="📦 WARENAUSGANG",
            font=FONTS['title'],
            bg=COLORS['background'],
            fg=COLORS['primary']
        )
        title_label.pack(pady=(0, 50))

        # RFID-Login Container
        login_frame = tk.Frame(main_frame, bg=COLORS['card'], relief='raised', bd=2)
        login_frame.pack(expand=True, fill='both', padx=100, pady=50)

        # Anweisungstext
        instruction_label = tk.Label(
            login_frame,
            text="Bitte RFID-Karte an Lesegerät halten",
            font=FONTS['large'],
            bg=COLORS['card'],
            fg=COLORS['text']
        )
        instruction_label.pack(pady=(50, 30))

        # RFID-Icon und Status
        self.rfid_status_label = tk.Label(
            login_frame,
            text="🔓",
            font=('Arial', 80),
            bg=COLORS['card'],
            fg=COLORS['warning']
        )
        self.rfid_status_label.pack(pady=30)

        # Warte-Animation
        self.waiting_label = tk.Label(
            login_frame,
            text="Warte auf Karte...",
            font=FONTS['normal'],
            bg=COLORS['card'],
            fg=COLORS['text_secondary']
        )
        self.waiting_label.pack(pady=(0, 50))

        # Sprache wechseln
        language_frame = tk.Frame(main_frame, bg=COLORS['background'])
        language_frame.pack(side='bottom', pady=20)

        for lang, flag in [('de', '🇩🇪'), ('en', '🇬🇧'), ('tr', '🇹🇷'), ('pl', '🇵🇱')]:
            btn = tk.Button(
                language_frame,
                text=flag,
                font=FONTS['normal'],
                command=lambda l=lang: self.change_language(l),
                width=3,
                height=1
            )
            btn.pack(side='left', padx=5)

        # RFID-Scan starten
        self.start_rfid_scan()

    def start_rfid_scan(self):
        """Startet den RFID-Scan-Prozess."""

        def scan():
            tag_id = self.rfid.read_tag()
            if tag_id:
                self.process_login(tag_id)
            else:
                self.root.after(1000, scan)

        self.root.after(1000, scan)

    def process_login(self, tag_id):
        """Verarbeitet den RFID-Login."""
        self.logger.info(f"RFID-Tag erkannt: {tag_id}")

        employee = self.db.validate_employee_rfid(tag_id)
        if employee:
            self.current_user = employee
            self.language = employee.get('language', 'de')

            self.rfid_status_label.config(text="✓", fg=COLORS['success'])
            self.waiting_label.config(
                text=f"Willkommen {employee['name']}!",
                fg=COLORS['success']
            )

            self.db.clock_in(employee['id'])
            self.root.after(1000, self.setup_main_screen)
        else:
            self.rfid_status_label.config(text="✗", fg=COLORS['error'])
            self.waiting_label.config(
                text="Unbekannte Karte!",
                fg=COLORS['error']
            )
            self.root.after(2000, self.reset_login_status)

    def reset_login_status(self):
        """Setzt den Login-Status zurück."""
        self.rfid_status_label.config(text="🔓", fg=COLORS['warning'])
        self.waiting_label.config(
            text="Warte auf Karte...",
            fg=COLORS['text_secondary']
        )
        self.start_rfid_scan()

    def setup_main_screen(self):
        """Erstellt den Hauptbildschirm."""
        self.clear_screen()

        # Header
        header_frame = tk.Frame(self.root, bg=COLORS['primary'], height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        # Benutzerinfo
        user_info = tk.Label(
            header_frame,
            text=f"👤 {self.current_user['name']} | 📦 Warenausgang",
            font=FONTS['large'],
            bg=COLORS['primary'],
            fg='white'
        )
        user_info.pack(side='left', padx=20, pady=20)

        # Logout-Button
        logout_btn = tk.Button(
            header_frame,
            text="Abmelden",
            font=FONTS['normal'],
            command=self.logout,
            bg=COLORS['error'],
            fg='white',
            width=12
        )
        logout_btn.pack(side='right', padx=20, pady=20)

        # Hauptbereich
        main_frame = tk.Frame(self.root, bg=COLORS['background'])
        main_frame.pack(expand=True, fill='both', padx=50, pady=30)

        # Zwei Spalten Layout
        left_frame = tk.Frame(main_frame, bg=COLORS['background'])
        left_frame.pack(side='left', expand=True, fill='both', padx=(0, 20))

        right_frame = tk.Frame(main_frame, bg=COLORS['background'])
        right_frame.pack(side='right', expand=True, fill='both', padx=(20, 0))

        # Linke Spalte - Hauptaktionen
        action_label = tk.Label(
            left_frame,
            text="Versandvorbereitung",
            font=FONTS['large'],
            bg=COLORS['background'],
            fg=COLORS['text']
        )
        action_label.pack(pady=(0, 20))

        # Paket scannen Button
        scan_btn = self.ui.create_large_button(
            left_frame,
            text="📷 Paket scannen",
            command=self.scan_package,
            color=COLORS['primary']
        )
        scan_btn.pack(pady=10)

        # Batch-Versand Button
        batch_btn = self.ui.create_large_button(
            left_frame,
            text="🚚 Versand abschließen",
            command=self.complete_shipment,
            color=COLORS['success']
        )
        batch_btn.pack(pady=10)

        # Status-Anzeige
        self.status_frame = tk.Frame(left_frame, bg=COLORS['card'], relief='raised', bd=2)
        self.status_frame.pack(fill='x', pady=20)

        self.status_label = tk.Label(
            self.status_frame,
            text="Bereit zum Scannen...",
            font=FONTS['normal'],
            bg=COLORS['card'],
            fg=COLORS['text']
        )
        self.status_label.pack(pady=15)

        # Rechte Spalte - Gescannte Pakete
        scanned_label = tk.Label(
            right_frame,
            text="Gescannte Pakete",
            font=FONTS['large'],
            bg=COLORS['background'],
            fg=COLORS['text']
        )
        scanned_label.pack(pady=(0, 20))

        # Paketliste
        self.package_frame = tk.Frame(right_frame, bg=COLORS['card'], relief='raised', bd=2)
        self.package_frame.pack(fill='both', expand=True)

        # Scrollbare Liste
        canvas = tk.Canvas(self.package_frame, bg=COLORS['card'])
        scrollbar = ttk.Scrollbar(self.package_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg=COLORS['card'])

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Paketanzahl
        self.package_count_label = tk.Label(
            right_frame,
            text="Anzahl: 0 Pakete",
            font=FONTS['normal'],
            bg=COLORS['background'],
            fg=COLORS['text_secondary']
        )
        self.package_count_label.pack(pady=10)

        # Statistiken
        stats_frame = tk.Frame(main_frame, bg=COLORS['background'])
        stats_frame.pack(side='bottom', fill='x', pady=20)

        # Tagesstatistik
        self.daily_stats_label = tk.Label(
            stats_frame,
            text="Heute versendet: 0 Pakete",
            font=FONTS['normal'],
            bg=COLORS['background'],
            fg=COLORS['text_secondary']
        )
        self.daily_stats_label.pack(side='left', padx=20)

        # Wochenstatistik
        self.weekly_stats_label = tk.Label(
            stats_frame,
            text="Diese Woche: 0 Pakete",
            font=FONTS['normal'],
            bg=COLORS['background'],
            fg=COLORS['text_secondary']
        )
        self.weekly_stats_label.pack(side='right', padx=20)

        # Statistiken aktualisieren
        self.update_statistics()

    def scan_package(self):
        """Öffnet den QR-Code Scanner."""
        self.logger.info("Starte Paket-Scan für Versand")

        # Scanner-Fenster erstellen
        scanner_window = tk.Toplevel(self.root)
        scanner_window.title("QR-Code Scanner")
        scanner_window.geometry("800x600")
        scanner_window.transient(self.root)
        scanner_window.grab_set()

        # Scanner-UI
        scanner_frame = tk.Frame(scanner_window, bg=COLORS['background'])
        scanner_frame.pack(expand=True, fill='both')

        info_label = tk.Label(
            scanner_frame,
            text="Halten Sie den QR-Code vor die Kamera",
            font=FONTS['large'],
            bg=COLORS['background']
        )
        info_label.pack(pady=20)

        # Kamera-Vorschau (Platzhalter)
        camera_frame = tk.Frame(
            scanner_frame,
            bg='black',
            width=640,
            height=480
        )
        camera_frame.pack(pady=20)

        # Mehrfach-Scan Info
        multi_info = tk.Label(
            scanner_frame,
            text="Tipp: Scannen Sie mehrere Pakete nacheinander",
            font=FONTS['normal'],
            bg=COLORS['background'],
            fg=COLORS['text_secondary']
        )
        multi_info.pack(pady=10)

        # Abbrechen-Button
        cancel_btn = tk.Button(
            scanner_frame,
            text="Fertig",
            font=FONTS['normal'],
            command=scanner_window.destroy,
            bg=COLORS['warning'],
            fg='white',
            width=20
        )
        cancel_btn.pack(pady=20)

        # Simuliere Scan nach 2 Sekunden
        scanner_window.after(2000, lambda: self.process_package_scan("PKG-2024-001234", scanner_window))

    def process_package_scan(self, qr_code, scanner_window=None):
        """Verarbeitet den gescannten QR-Code."""
        # Paket in Datenbank suchen
        package = self.db.get_package_by_qr(qr_code)

        if package:
            # Prüfen ob Paket bereits gescannt wurde
            if any(p['qr_code'] == qr_code for p in self.scanned_packages):
                self.status_label.config(
                    text=f"⚠ Paket {qr_code} bereits gescannt!",
                    fg=COLORS['warning']
                )
                self.ui.play_sound('error')
            else:
                # Prüfen ob Paket versandbereit ist
                if package.get('status') == 'Qualität OK':
                    self.scanned_packages.append(package)
                    self.update_package_list()
                    self.status_label.config(
                        text=f"✓ Paket {qr_code} hinzugefügt",
                        fg=COLORS['success']
                    )
                    self.ui.play_sound('scan')

                    # Weiter scannen nach kurzer Pause
                    if scanner_window:
                        scanner_window.after(1500, lambda: self.process_package_scan(
                            f"PKG-2024-{str(len(self.scanned_packages) + 1000).zfill(6)}",
                            scanner_window
                        ))
                else:
                    self.status_label.config(
                        text=f"✗ Paket {qr_code} nicht versandbereit!",
                        fg=COLORS['error']
                    )
                    self.ui.play_sound('error')
        else:
            self.status_label.config(
                text=f"✗ Paket {qr_code} nicht gefunden!",
                fg=COLORS['error']
            )
            self.ui.play_sound('error')

    def update_package_list(self):
        """Aktualisiert die Liste der gescannten Pakete."""
        # Alte Einträge löschen
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Pakete anzeigen
        for idx, package in enumerate(self.scanned_packages):
            package_frame = tk.Frame(
                self.scrollable_frame,
                bg=COLORS['background'],
                relief='raised',
                bd=1
            )
            package_frame.pack(fill='x', padx=10, pady=5)

            # Paketinfo
            info_frame = tk.Frame(package_frame, bg=COLORS['background'])
            info_frame.pack(side='left', fill='x', expand=True)

            package_label = tk.Label(
                info_frame,
                text=f"{idx + 1}. {package['qr_code']}",
                font=FONTS['normal'],
                bg=COLORS['background']
            )
            package_label.pack(anchor='w', padx=10, pady=(5, 0))

            customer_label = tk.Label(
                info_frame,
                text=f"Kunde: {package.get('customer', 'N/A')}",
                font=('Arial', 10),
                bg=COLORS['background'],
                fg=COLORS['text_secondary']
            )
            customer_label.pack(anchor='w', padx=10, pady=(0, 5))

            # Entfernen-Button
            remove_btn = tk.Button(
                package_frame,
                text="✗",
                font=FONTS['normal'],
                command=lambda p=package: self.remove_package(p),
                bg=COLORS['error'],
                fg='white',
                width=3
            )
            remove_btn.pack(side='right', padx=10, pady=5)

        # Anzahl aktualisieren
        self.package_count_label.config(
            text=f"Anzahl: {len(self.scanned_packages)} Pakete"
        )

    def remove_package(self, package):
        """Entfernt ein Paket aus der Liste."""
        self.scanned_packages.remove(package)
        self.update_package_list()
        self.status_label.config(
            text=f"Paket {package['qr_code']} entfernt",
            fg=COLORS['warning']
        )

    def complete_shipment(self):
        """Schließt den Versand ab."""
        if not self.scanned_packages:
            messagebox.showwarning("Warnung", "Keine Pakete zum Versenden gescannt!")
            return

        # Versand-Dialog
        shipment_window = tk.Toplevel(self.root)
        shipment_window.title("Versand abschließen")
        shipment_window.geometry("800x600")
        shipment_window.transient(self.root)
        shipment_window.grab_set()

        # Header
        header_frame = tk.Frame(shipment_window, bg=COLORS['primary'], height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        title_label = tk.Label(
            header_frame,
            text=f"Versand von {len(self.scanned_packages)} Paketen",
            font=FONTS['large'],
            bg=COLORS['primary'],
            fg='white'
        )
        title_label.pack(pady=15)

        # Hauptbereich
        main_frame = tk.Frame(shipment_window, bg=COLORS['background'])
        main_frame.pack(fill='both', expand=True, padx=30, pady=20)

        # Versandart auswählen
        method_label = tk.Label(
            main_frame,
            text="Versandart wählen:",
            font=FONTS['large'],
            bg=COLORS['background']
        )
        method_label.pack(anchor='w', pady=(0, 10))

        # Radio Buttons für Versandarten
        self.selected_method = tk.StringVar(value=self.shipping_methods[0])

        method_frame = tk.Frame(main_frame, bg=COLORS['background'])
        method_frame.pack(anchor='w', padx=20, pady=10)

        for method in self.shipping_methods:
            rb = tk.Radiobutton(
                method_frame,
                text=method,
                variable=self.selected_method,
                value=method,
                font=FONTS['normal'],
                bg=COLORS['background']
            )
            rb.pack(anchor='w', pady=5)

        # Tracking-Nummer (optional)
        tracking_label = tk.Label(
            main_frame,
            text="Tracking-Nummer (optional):",
            font=FONTS['normal'],
            bg=COLORS['background']
        )
        tracking_label.pack(anchor='w', pady=(20, 5))

        self.tracking_entry = tk.Entry(
            main_frame,
            font=FONTS['normal'],
            width=30
        )
        self.tracking_entry.pack(anchor='w', padx=20)

        # Zusammenfassung
        summary_frame = tk.Frame(main_frame, bg=COLORS['card'], relief='raised', bd=1)
        summary_frame.pack(fill='x', pady=20)

        summary_text = f"""
        Anzahl Pakete: {len(self.scanned_packages)}
        Versanddatum: {date.today().strftime('%d.%m.%Y')}
        Bearbeiter: {self.current_user['name']}
        """

        summary_label = tk.Label(
            summary_frame,
            text=summary_text,
            font=FONTS['normal'],
            bg=COLORS['card'],
            justify='left'
        )
        summary_label.pack(padx=20, pady=15)

        # Buttons
        button_frame = tk.Frame(main_frame, bg=COLORS['background'])
        button_frame.pack(side='bottom', pady=20)

        # Versand bestätigen
        confirm_btn = tk.Button(
            button_frame,
            text="✓ Versand bestätigen",
            font=FONTS['large'],
            command=lambda: self.confirm_shipment(shipment_window),
            bg=COLORS['success'],
            fg='white',
            width=20,
            height=2
        )
        confirm_btn.pack(side='left', padx=10)

        # Abbrechen
        cancel_btn = tk.Button(
            button_frame,
            text="Abbrechen",
            font=FONTS['normal'],
            command=shipment_window.destroy,
            bg=COLORS['error'],
            fg='white',
            width=20,
            height=2
        )
        cancel_btn.pack(side='right', padx=10)

    def confirm_shipment(self, window):
        """Bestätigt den Versand."""
        shipping_method = self.selected_method.get()
        tracking_number = self.tracking_entry.get().strip()

        # Alle Pakete als versendet markieren
        success_count = 0
        for package in self.scanned_packages:
            success = self.db.mark_package_shipped(
                package['id'],
                self.current_user['id'],
                shipping_method,
                tracking_number
            )
            if success:
                success_count += 1

        if success_count == len(self.scanned_packages):
            window.destroy()

            # Erfolgsmeldung
            self.status_label.config(
                text=f"✓ {success_count} Pakete erfolgreich versendet!",
                fg=COLORS['success']
            )
            self.ui.play_sound('success')

            # Liste leeren
            self.scanned_packages = []
            self.update_package_list()

            # Statistiken aktualisieren
            self.update_statistics()

            # Versandlabel drucken (simuliert)
            self.print_shipping_labels()
        else:
            messagebox.showerror(
                "Fehler",
                f"Nur {success_count} von {len(self.scanned_packages)} Paketen konnten versendet werden!"
            )

    def print_shipping_labels(self):
        """Simuliert das Drucken von Versandlabels."""
        # Info-Dialog
        info_window = tk.Toplevel(self.root)
        info_window.title("Versandlabels")
        info_window.geometry("400x200")
        info_window.transient(self.root)

        info_label = tk.Label(
            info_window,
            text="🖨️ Versandlabels werden gedruckt...",
            font=FONTS['large'],
            bg=COLORS['background']
        )
        info_label.pack(expand=True)

        # Nach 2 Sekunden schließen
        info_window.after(2000, info_window.destroy)

    def update_statistics(self):
        """Aktualisiert die Statistiken."""
        # Tagesstatistik
        daily_stats = self.db.get_shipping_statistics('daily', self.current_user['id'])
        self.daily_stats_label.config(
            text=f"Heute versendet: {daily_stats.get('count', 0)} Pakete"
        )

        # Wochenstatistik
        weekly_stats = self.db.get_shipping_statistics('weekly', self.current_user['id'])
        self.weekly_stats_label.config(
            text=f"Diese Woche: {weekly_stats.get('count', 0)} Pakete"
        )

    def change_language(self, language):
        """Ändert die Sprache der Anwendung."""
        self.language = language
        self.translations.set_language(language)
        if self.current_user:
            self.setup_main_screen()
        else:
            self.setup_login_screen()

    def logout(self):
        """Meldet den Benutzer ab."""
        if self.current_user:
            self.db.clock_out(self.current_user['id'])
            self.logger.info(f"Benutzer {self.current_user['name']} abgemeldet")

        self.current_user = None
        self.current_package = None
        self.scanned_packages = []
        self.setup_login_screen()

    def clear_screen(self):
        """Löscht alle Widgets vom Bildschirm."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def run(self):
        """Startet die Anwendung."""
        try:
            self.root.mainloop()
        except Exception as e:
            self.logger.error(f"Fehler in Hauptschleife: {e}")
            messagebox.showerror("Kritischer Fehler", str(e))


def main():
    """Haupteinstiegspunkt."""
    app = WarenausgangApp()
    app.run()


if __name__ == "__main__":
    main()