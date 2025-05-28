#!/usr/bin/env python3
"""
Shirtful WMS - Qualitätskontrolle Station
Anwendung für die Qualitätskontrolle im Warenprozess.
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


class QualitaetskontrolleApp:
    """Hauptanwendung für die Qualitätskontrolle."""

    def __init__(self):
        """Initialisiert die Qualitätskontrolle-Anwendung."""
        self.root = tk.Tk()
        self.root.title("Shirtful WMS - Qualitätskontrolle")
        self.root.geometry("1024x768")
        self.root.configure(bg=COLORS['background'])

        # Vollbildmodus
        self.root.attributes('-fullscreen', True)
        self.root.bind('<Escape>', lambda e: self.root.attributes('-fullscreen', False))
        self.root.bind('<F11>', lambda e: self.root.attributes('-fullscreen', True))

        # Logger einrichten
        self.logger = setup_logger('qualitaetskontrolle')
        self.logger.info("Qualitätskontrolle-App gestartet")

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

        # Fehlerkategorien
        self.error_categories = [
            "Druckfehler",
            "Farbabweichung",
            "Stoffdefekt",
            "Verschmutzung",
            "Falsche Größe",
            "Nahtfehler",
            "Positionsfehler",
            "Sonstiges"
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
            text="🔍 QUALITÄTSKONTROLLE",
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
            text=f"👤 {self.current_user['name']} | 🔍 Qualitätskontrolle",
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
            text="📦 Paket prüfen",
            command=self.scan_package,
            color=COLORS['primary']
        )
        scan_btn.pack(pady=20)

        # Status-Anzeige
        self.status_frame = tk.Frame(main_frame, bg=COLORS['card'], relief='raised', bd=2)
        self.status_frame.pack(fill='x', pady=20)

        self.status_label = tk.Label(
            self.status_frame,
            text="Bereit zur Qualitätsprüfung...",
            font=FONTS['large'],
            bg=COLORS['card'],
            fg=COLORS['text']
        )
        self.status_label.pack(pady=20)

        # Statistiken
        stats_frame = tk.Frame(main_frame, bg=COLORS['background'])
        stats_frame.pack(side='bottom', fill='x')

        # Zwei Spalten für Statistiken
        stats_left = tk.Frame(stats_frame, bg=COLORS['background'])
        stats_left.pack(side='left', expand=True, fill='x')

        stats_right = tk.Frame(stats_frame, bg=COLORS['background'])
        stats_right.pack(side='right', expand=True, fill='x')

        self.ok_stats_label = tk.Label(
            stats_left,
            text="✓ OK: 0",
            font=FONTS['large'],
            bg=COLORS['background'],
            fg=COLORS['success']
        )
        self.ok_stats_label.pack()

        self.error_stats_label = tk.Label(
            stats_right,
            text="✗ Nacharbeit: 0",
            font=FONTS['large'],
            bg=COLORS['background'],
            fg=COLORS['error']
        )
        self.error_stats_label.pack()

        # Statistiken aktualisieren
        self.update_statistics()

    def scan_package(self):
        """Öffnet den QR-Code Scanner."""
        self.logger.info("Starte Paket-Scan für Qualitätsprüfung")

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
            self.show_quality_check_screen()
        else:
            messagebox.showerror(
                "Fehler",
                f"Paket mit QR-Code '{qr_code}' nicht gefunden!"
            )

    def show_quality_check_screen(self):
        """Zeigt den Qualitätsprüfungs-Bildschirm."""
        # Qualitätsprüfungs-Fenster
        qc_window = tk.Toplevel(self.root)
        qc_window.title("Qualitätsprüfung")
        qc_window.geometry("1000x800")
        qc_window.transient(self.root)
        qc_window.grab_set()

        # Header
        header_frame = tk.Frame(qc_window, bg=COLORS['primary'], height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        title_label = tk.Label(
            header_frame,
            text=f"Qualitätsprüfung: {self.current_package['qr_code']}",
            font=FONTS['large'],
            bg=COLORS['primary'],
            fg='white'
        )
        title_label.pack(pady=15)

        # Hauptbereich
        main_frame = tk.Frame(qc_window, bg=COLORS['background'])
        main_frame.pack(fill='both', expand=True, padx=30, pady=20)

        # Paketinfo
        info_frame = tk.Frame(main_frame, bg=COLORS['card'], relief='raised', bd=1)
        info_frame.pack(fill='x', pady=(0, 20))

        info_text = f"""
        Bestellung: {self.current_package.get('order_id', 'N/A')}
        Kunde: {self.current_package.get('customer', 'N/A')}
        Artikel: {self.current_package.get('item_count', 0)} Stück
        Vorheriger Status: {self.current_package.get('status', 'Unbekannt')}
        """

        info_label = tk.Label(
            info_frame,
            text=info_text,
            font=FONTS['normal'],
            bg=COLORS['card'],
            justify='left'
        )
        info_label.pack(anchor='w', padx=20, pady=15)

        # Prüfungsergebnis
        result_frame = tk.Frame(main_frame, bg=COLORS['background'])
        result_frame.pack(expand=True)

        result_label = tk.Label(
            result_frame,
            text="Prüfungsergebnis:",
            font=FONTS['large'],
            bg=COLORS['background']
        )
        result_label.pack(pady=(0, 20))

        # Große Buttons für OK/Nacharbeit
        button_container = tk.Frame(result_frame, bg=COLORS['background'])
        button_container.pack()

        # OK Button
        ok_btn = tk.Button(
            button_container,
            text="✓ Qualität OK",
            font=('Arial', 32, 'bold'),
            command=lambda: self.set_quality_status('OK', qc_window),
            bg=COLORS['success'],
            fg='white',
            width=15,
            height=3
        )
        ok_btn.pack(side='left', padx=20)

        # Nacharbeit Button
        rework_btn = tk.Button(
            button_container,
            text="✗ Nacharbeit",
            font=('Arial', 32, 'bold'),
            command=lambda: self.show_error_selection(qc_window),
            bg=COLORS['error'],
            fg='white',
            width=15,
            height=3
        )
        rework_btn.pack(side='right', padx=20)

        # Abbrechen
        cancel_frame = tk.Frame(main_frame, bg=COLORS['background'])
        cancel_frame.pack(side='bottom', pady=20)

        cancel_btn = tk.Button(
            cancel_frame,
            text="Abbrechen",
            font=FONTS['normal'],
            command=qc_window.destroy,
            bg=COLORS['warning'],
            fg='white',
            width=20
        )
        cancel_btn.pack()

    def show_error_selection(self, parent_window):
        """Zeigt Fehlerauswahl-Dialog."""
        # Fehlerauswahl-Fenster
        error_window = tk.Toplevel(parent_window)
        error_window.title("Fehler auswählen")
        error_window.geometry("800x700")
        error_window.transient(parent_window)
        error_window.grab_set()

        # Header
        header_label = tk.Label(
            error_window,
            text="Bitte Fehlerart auswählen:",
            font=FONTS['large'],
            bg=COLORS['background']
        )
        header_label.pack(pady=20)

        # Fehler-Buttons
        error_frame = tk.Frame(error_window, bg=COLORS['background'])
        error_frame.pack(expand=True, padx=40)

        self.selected_errors = []

        # Checkboxen für Fehlerarten
        for error in self.error_categories:
            var = tk.BooleanVar()
            cb = tk.Checkbutton(
                error_frame,
                text=error,
                variable=var,
                font=FONTS['large'],
                bg=COLORS['background'],
                onvalue=True,
                offvalue=False
            )
            cb.pack(anchor='w', pady=10)
            self.selected_errors.append((error, var))

        # Zusätzliche Notizen
        notes_label = tk.Label(
            error_frame,
            text="Zusätzliche Bemerkungen:",
            font=FONTS['normal'],
            bg=COLORS['background']
        )
        notes_label.pack(anchor='w', pady=(20, 5))

        self.error_notes = tk.Text(
            error_frame,
            height=3,
            font=FONTS['normal'],
            wrap='word'
        )
        self.error_notes.pack(fill='x', pady=(0, 20))

        # Buttons
        button_frame = tk.Frame(error_window, bg=COLORS['background'])
        button_frame.pack(side='bottom', pady=20)

        # Bestätigen
        confirm_btn = tk.Button(
            button_frame,
            text="Fehler bestätigen",
            font=FONTS['normal'],
            command=lambda: self.confirm_errors(parent_window, error_window),
            bg=COLORS['error'],
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
            command=error_window.destroy,
            bg=COLORS['warning'],
            fg='white',
            width=20,
            height=2
        )
        cancel_btn.pack(side='right', padx=10)

    def confirm_errors(self, parent_window, error_window):
        """Bestätigt die ausgewählten Fehler."""
        # Ausgewählte Fehler sammeln
        errors = [error for error, var in self.selected_errors if var.get()]
        notes = self.error_notes.get("1.0", "end-1c").strip()

        if not errors:
            messagebox.showwarning("Warnung", "Bitte mindestens einen Fehler auswählen!")
            return

        # Fehlerdetails zusammenstellen
        error_details = {
            'errors': errors,
            'notes': notes
        }

        error_window.destroy()
        self.set_quality_status('Nacharbeit', parent_window, error_details)

    def set_quality_status(self, status, window, error_details=None):
        """Setzt den Qualitätsstatus des Pakets."""
        # Status in DB aktualisieren
        success = self.db.update_package_quality_status(
            self.current_package['id'],
            status,
            self.current_user['id'],
            error_details
        )

        if success:
            window.destroy()

            if status == 'OK':
                self.status_label.config(
                    text=f"✓ Paket {self.current_package['qr_code']} - Qualität OK",
                    fg=COLORS['success']
                )
                self.ui.play_sound('success')
            else:
                self.status_label.config(
                    text=f"✗ Paket {self.current_package['qr_code']} - Nacharbeit erforderlich",
                    fg=COLORS['error']
                )
                self.ui.play_sound('error')

            # Statistiken aktualisieren
            self.update_statistics()

            # Nach 3 Sekunden Status zurücksetzen
            self.root.after(3000, lambda: self.status_label.config(
                text="Bereit zur Qualitätsprüfung...",
                fg=COLORS['text']
            ))
        else:
            messagebox.showerror("Fehler", "Status konnte nicht aktualisiert werden!")

    def update_statistics(self):
        """Aktualisiert die Statistiken."""
        stats = self.db.get_quality_statistics(self.current_user['id'])
        self.ok_stats_label.config(
            text=f"✓ OK: {stats.get('ok_count', 0)}"
        )
        self.error_stats_label.config(
            text=f"✗ Nacharbeit: {stats.get('rework_count', 0)}"
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
    app = QualitaetskontrolleApp()
    app.run()


if __name__ == "__main__":
    main()