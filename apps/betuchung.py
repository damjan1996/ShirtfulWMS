#!/usr/bin/env python3
"""
Shirtful WMS - Betuchung Station
Anwendung für die Betuchungsstation im Warenprozess.
"""

import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
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


class BetuchungApp:
    """Hauptanwendung für die Betuchungsstation."""

    def __init__(self):
        """Initialisiert die Betuchung-Anwendung."""
        self.root = tk.Tk()
        self.root.title("Shirtful WMS - Betuchung")
        self.root.geometry("1024x768")
        self.root.configure(bg=COLORS['background'])

        # Vollbildmodus
        self.root.attributes('-fullscreen', True)
        self.root.bind('<Escape>', lambda e: self.root.attributes('-fullscreen', False))
        self.root.bind('<F11>', lambda e: self.root.attributes('-fullscreen', True))

        # Logger einrichten
        self.logger = setup_logger('betuchung')
        self.logger.info("Betuchung-App gestartet")

        # Komponenten initialisieren
        self.rfid = RFIDAuth()
        self.db = Database()
        self.qr_scanner = QRScanner()
        self.ui = UIComponents()
        self.translations = Translations()

        # App-Status
        self.current_user = None
        self.current_package = None
        self.language = 'de'  # Standard: Deutsch

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
            text="🧵 BETUCHUNG",
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
                # Weiter scannen
                self.root.after(1000, scan)

        # Scan nach 1 Sekunde starten
        self.root.after(1000, scan)

    def process_login(self, tag_id):
        """Verarbeitet den RFID-Login."""
        self.logger.info(f"RFID-Tag erkannt: {tag_id}")

        # Mitarbeiter validieren
        employee = self.db.validate_employee_rfid(tag_id)
        if employee:
            self.current_user = employee
            self.language = employee.get('language', 'de')

            # Erfolgsmeldung
            self.rfid_status_label.config(text="✓", fg=COLORS['success'])
            self.waiting_label.config(
                text=f"Willkommen {employee['name']}!",
                fg=COLORS['success']
            )

            # Zeit erfassen
            self.db.clock_in(employee['id'])

            # Nach 1 Sekunde zum Hauptmenü
            self.root.after(1000, self.setup_main_screen)
        else:
            # Fehlermeldung
            self.rfid_status_label.config(text="✗", fg=COLORS['error'])
            self.waiting_label.config(
                text="Unbekannte Karte!",
                fg=COLORS['error']
            )

            # Nach 2 Sekunden zurücksetzen
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
            text=f"👤 {self.current_user['name']} | 🧵 Betuchung",
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

        # Aktionsbuttons
        button_frame = tk.Frame(main_frame, bg=COLORS['background'])
        button_frame.pack(expand=True)

        # Paket scannen Button
        scan_btn = self.ui.create_large_button(
            button_frame,
            text="📦 Paket scannen",
            command=self.scan_package,
            color=COLORS['primary']
        )
        scan_btn.pack(pady=20)

        # Status-Anzeige
        self.status_frame = tk.Frame(main_frame, bg=COLORS['card'], relief='raised', bd=2)
        self.status_frame.pack(fill='x', pady=20)

        self.status_label = tk.Label(
            self.status_frame,
            text="Bereit zum Scannen...",
            font=FONTS['large'],
            bg=COLORS['card'],
            fg=COLORS['text']
        )
        self.status_label.pack(pady=20)

        # Statistiken
        stats_frame = tk.Frame(main_frame, bg=COLORS['background'])
        stats_frame.pack(side='bottom', fill='x')

        self.stats_label = tk.Label(
            stats_frame,
            text="Heute bearbeitet: 0 Pakete",
            font=FONTS['normal'],
            bg=COLORS['background'],
            fg=COLORS['text_secondary']
        )
        self.stats_label.pack()

        # Statistiken aktualisieren
        self.update_statistics()

    def scan_package(self):
        """Öffnet den QR-Code Scanner."""
        self.logger.info("Starte Paket-Scan")

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

        # Abbrechen-Button
        cancel_btn = tk.Button(
            scanner_frame,
            text="Abbrechen",
            font=FONTS['normal'],
            command=scanner_window.destroy,
            bg=COLORS['error'],
            fg='white',
            width=20
        )
        cancel_btn.pack(pady=20)

        # Simuliere Scan nach 2 Sekunden
        scanner_window.after(2000, lambda: self.process_package_scan("PKG-2024-001234", scanner_window))

    def process_package_scan(self, qr_code, scanner_window):
        """Verarbeitet den gescannten QR-Code."""
        scanner_window.destroy()

        # Paket in Datenbank suchen
        package = self.db.get_package_by_qr(qr_code)

        if package:
            self.current_package = package
            self.show_package_details()
        else:
            messagebox.showerror(
                "Fehler",
                f"Paket mit QR-Code '{qr_code}' nicht gefunden!"
            )

    def show_package_details(self):
        """Zeigt Paketdetails und Aktionsoptionen."""
        # Details-Fenster
        details_window = tk.Toplevel(self.root)
        details_window.title("Paketdetails")
        details_window.geometry("900x700")
        details_window.transient(self.root)
        details_window.grab_set()

        # Header
        header_frame = tk.Frame(details_window, bg=COLORS['primary'], height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        title_label = tk.Label(
            header_frame,
            text=f"Paket: {self.current_package['qr_code']}",
            font=FONTS['large'],
            bg=COLORS['primary'],
            fg='white'
        )
        title_label.pack(pady=15)

        # Details
        details_frame = tk.Frame(details_window, bg=COLORS['background'])
        details_frame.pack(fill='both', expand=True, padx=30, pady=20)

        # Paketinfo
        info_text = f"""
        Bestellung: {self.current_package.get('order_id', 'N/A')}
        Kunde: {self.current_package.get('customer', 'N/A')}
        Artikel: {self.current_package.get('item_count', 0)} Stück
        Status: {self.current_package.get('status', 'Unbekannt')}
        Letzte Aktualisierung: {self.current_package.get('last_update', 'N/A')}
        """

        info_label = tk.Label(
            details_frame,
            text=info_text,
            font=FONTS['normal'],
            bg=COLORS['background'],
            justify='left'
        )
        info_label.pack(anchor='w', pady=20)

        # Notizen
        notes_label = tk.Label(
            details_frame,
            text="Notizen (optional):",
            font=FONTS['normal'],
            bg=COLORS['background']
        )
        notes_label.pack(anchor='w', pady=(20, 5))

        self.notes_text = tk.Text(
            details_frame,
            height=4,
            font=FONTS['normal'],
            wrap='word'
        )
        self.notes_text.pack(fill='x', padx=20)

        # Aktionsbuttons
        button_frame = tk.Frame(details_frame, bg=COLORS['background'])
        button_frame.pack(pady=30)

        # Status auf "In Betuchung" setzen
        process_btn = tk.Button(
            button_frame,
            text="✓ In Betuchung nehmen",
            font=FONTS['large'],
            command=lambda: self.update_package_status(details_window),
            bg=COLORS['success'],
            fg='white',
            width=25,
            height=2
        )
        process_btn.pack(pady=10)

        # Abbrechen
        cancel_btn = tk.Button(
            button_frame,
            text="Abbrechen",
            font=FONTS['normal'],
            command=details_window.destroy,
            bg=COLORS['error'],
            fg='white',
            width=25
        )
        cancel_btn.pack()

    def update_package_status(self, window):
        """Aktualisiert den Paketstatus auf 'In Betuchung'."""
        notes = self.notes_text.get("1.0", "end-1c").strip()

        # Status in DB aktualisieren
        success = self.db.update_package_status(
            self.current_package['id'],
            'In Betuchung',
            self.current_user['id'],
            notes
        )

        if success:
            window.destroy()
            self.status_label.config(
                text=f"✓ Paket {self.current_package['qr_code']} in Betuchung genommen",
                fg=COLORS['success']
            )

            # Sound abspielen
            self.ui.play_sound('success')

            # Statistiken aktualisieren
            self.update_statistics()

            # Nach 3 Sekunden Status zurücksetzen
            self.root.after(3000, lambda: self.status_label.config(
                text="Bereit zum Scannen...",
                fg=COLORS['text']
            ))
        else:
            messagebox.showerror("Fehler", "Status konnte nicht aktualisiert werden!")

    def update_statistics(self):
        """Aktualisiert die Statistiken."""
        stats = self.db.get_daily_statistics(self.current_user['id'], 'Betuchung')
        self.stats_label.config(
            text=f"Heute bearbeitet: {stats.get('count', 0)} Pakete"
        )

    def change_language(self, language):
        """Ändert die Sprache der Anwendung."""
        self.language = language
        self.translations.set_language(language)
        # UI neu laden
        if self.current_user:
            self.setup_main_screen()
        else:
            self.setup_login_screen()

    def logout(self):
        """Meldet den Benutzer ab."""
        if self.current_user:
            # Ausstempeln
            self.db.clock_out(self.current_user['id'])
            self.logger.info(f"Benutzer {self.current_user['name']} abgemeldet")

        self.current_user = None
        self.current_package = None
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
    app = BetuchungApp()
    app.run()


if __name__ == "__main__":
    main()