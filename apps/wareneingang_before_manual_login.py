#!/usr/bin/env python3
"""
Shirtful WMS - Wareneingang Station
Anwendung für die Wareneingangsstation im Warenprozess.
"""

import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import sys
import os
import random
import string

# Projekt-Root zum Python-Path hinzufügen
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.rfid_auth import RFIDAuth
from utils.database import Database
from utils.qr_scanner import QRScanner
from utils.ui_components import UIComponents, COLORS, FONTS
from utils.logger import setup_logger
from config.translations import Translations


class WareneingangApp:
    """Hauptanwendung für die Wareneingangsstation."""

    def __init__(self):
        """Initialisiert die Wareneingang-Anwendung."""
        self.root = tk.Tk()
        self.root.title("Shirtful WMS - Wareneingang")
        self.root.geometry("1024x768")
        self.root.configure(bg=COLORS['background'])

        # Vollbildmodus
        self.root.attributes('-fullscreen', True)
        self.root.bind('<Escape>', lambda e: self.root.attributes('-fullscreen', False))
        self.root.bind('<F11>', lambda e: self.root.attributes('-fullscreen', True))

        # Logger einrichten
        self.logger = setup_logger('wareneingang')
        self.logger.info("Wareneingang-App gestartet")

        # Komponenten initialisieren
        self.rfid = RFIDAuth()
        self.db = Database()
        self.qr_scanner = QRScanner()
        self.ui = UIComponents()
        self.translations = Translations()

        # App-Status
        self.current_user = None
        self.current_delivery = None
        self.language = 'de'
        self.registered_packages = []

        # Lieferanten
        self.suppliers = [
            "DHL",
            "UPS",
            "DPD",
            "GLS",
            "Hermes",
            "Direktlieferung",
            "Sonstige"
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
            text="📥 WARENEINGANG",
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
            text=f"👤 {self.current_user['name']} | 📥 Wareneingang",
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

        # Zwei Hauptbereiche
        top_frame = tk.Frame(main_frame, bg=COLORS['background'])
        top_frame.pack(fill='x', pady=(0, 20))

        bottom_frame = tk.Frame(main_frame, bg=COLORS['background'])
        bottom_frame.pack(expand=True, fill='both')

        # Oberer Bereich - Hauptaktionen
        action_container = tk.Frame(top_frame, bg=COLORS['background'])
        action_container.pack()

        # Neue Lieferung Button
        new_delivery_btn = self.ui.create_large_button(
            action_container,
            text="🚚 Neue Lieferung",
            command=self.new_delivery,
            color=COLORS['primary']
        )
        new_delivery_btn.pack(side='left', padx=10)

        # Paket scannen Button
        scan_btn = self.ui.create_large_button(
            action_container,
            text="📷 Paket scannen",
            command=self.scan_package,
            color=COLORS['success']
        )
        scan_btn.pack(side='left', padx=10)

        # Manuelle Eingabe Button
        manual_btn = self.ui.create_large_button(
            action_container,
            text="⌨️ Manuelle Eingabe",
            command=self.manual_entry,
            color=COLORS['warning']
        )
        manual_btn.pack(side='left', padx=10)

        # Status-Anzeige
        self.status_frame = tk.Frame(top_frame, bg=COLORS['card'], relief='raised', bd=2)
        self.status_frame.pack(fill='x', pady=20)

        self.status_label = tk.Label(
            self.status_frame,
            text="Keine aktive Lieferung - Bitte neue Lieferung starten",
            font=FONTS['normal'],
            bg=COLORS['card'],
            fg=COLORS['text']
        )
        self.status_label.pack(pady=15)

        # Unterer Bereich - Zwei Spalten
        left_frame = tk.Frame(bottom_frame, bg=COLORS['background'])
        left_frame.pack(side='left', expand=True, fill='both', padx=(0, 10))

        right_frame = tk.Frame(bottom_frame, bg=COLORS['background'])
        right_frame.pack(side='right', expand=True, fill='both', padx=(10, 0))

        # Linke Spalte - Aktuelle Lieferung
        delivery_label = tk.Label(
            left_frame,
            text="Aktuelle Lieferung",
            font=FONTS['large'],
            bg=COLORS['background'],
            fg=COLORS['text']
        )
        delivery_label.pack(pady=(0, 10))

        self.delivery_info_frame = tk.Frame(left_frame, bg=COLORS['card'], relief='raised', bd=2)
        self.delivery_info_frame.pack(fill='both', expand=True)

        self.delivery_info_label = tk.Label(
            self.delivery_info_frame,
            text="Keine aktive Lieferung",
            font=FONTS['normal'],
            bg=COLORS['card'],
            fg=COLORS['text_secondary']
        )
        self.delivery_info_label.pack(pady=20)

        # Rechte Spalte - Letzte Eingänge
        recent_label = tk.Label(
            right_frame,
            text="Letzte Eingänge",
            font=FONTS['large'],
            bg=COLORS['background'],
            fg=COLORS['text']
        )
        recent_label.pack(pady=(0, 10))

        # Scrollbare Liste
        list_frame = tk.Frame(right_frame, bg=COLORS['card'], relief='raised', bd=2)
        list_frame.pack(fill='both', expand=True)

        canvas = tk.Canvas(list_frame, bg=COLORS['card'])
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        self.recent_frame = tk.Frame(canvas, bg=COLORS['card'])

        self.recent_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.recent_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Statistiken
        stats_frame = tk.Frame(main_frame, bg=COLORS['background'])
        stats_frame.pack(side='bottom', fill='x', pady=20)

        self.stats_label = tk.Label(
            stats_frame,
            text="Heute: 0 Lieferungen | 0 Pakete",
            font=FONTS['normal'],
            bg=COLORS['background'],
            fg=COLORS['text_secondary']
        )
        self.stats_label.pack()

        # Daten laden
        self.update_recent_entries()
        self.update_statistics()

    def new_delivery(self):
        """Startet eine neue Lieferung."""
        # Dialog für neue Lieferung
        delivery_window = tk.Toplevel(self.root)
        delivery_window.title("Neue Lieferung")
        delivery_window.geometry("700x500")
        delivery_window.transient(self.root)
        delivery_window.grab_set()

        # Header
        header_label = tk.Label(
            delivery_window,
            text="Neue Lieferung erfassen",
            font=FONTS['large'],
            bg=COLORS['background']
        )
        header_label.pack(pady=20)

        # Formular
        form_frame = tk.Frame(delivery_window, bg=COLORS['background'])
        form_frame.pack(expand=True, fill='both', padx=40)

        # Lieferant
        supplier_label = tk.Label(
            form_frame,
            text="Lieferant:",
            font=FONTS['normal'],
            bg=COLORS['background']
        )
        supplier_label.pack(anchor='w', pady=(10, 5))

        self.supplier_var = tk.StringVar(value=self.suppliers[0])
        supplier_combo = ttk.Combobox(
            form_frame,
            textvariable=self.supplier_var,
            values=self.suppliers,
            font=FONTS['normal'],
            state='readonly',
            width=30
        )
        supplier_combo.pack(anchor='w')

        # Lieferschein-Nummer
        delivery_note_label = tk.Label(
            form_frame,
            text="Lieferschein-Nr. (optional):",
            font=FONTS['normal'],
            bg=COLORS['background']
        )
        delivery_note_label.pack(anchor='w', pady=(20, 5))

        self.delivery_note_entry = tk.Entry(
            form_frame,
            font=FONTS['normal'],
            width=32
        )
        self.delivery_note_entry.pack(anchor='w')

        # Anzahl Pakete (geschätzt)
        package_count_label = tk.Label(
            form_frame,
            text="Erwartete Pakete:",
            font=FONTS['normal'],
            bg=COLORS['background']
        )
        package_count_label.pack(anchor='w', pady=(20, 5))

        self.package_count_entry = tk.Entry(
            form_frame,
            font=FONTS['normal'],
            width=10
        )
        self.package_count_entry.pack(anchor='w')

        # Notizen
        notes_label = tk.Label(
            form_frame,
            text="Notizen:",
            font=FONTS['normal'],
            bg=COLORS['background']
        )
        notes_label.pack(anchor='w', pady=(20, 5))

        self.notes_text = tk.Text(
            form_frame,
            height=3,
            font=FONTS['normal'],
            wrap='word',
            width=40
        )
        self.notes_text.pack(anchor='w')

        # Buttons
        button_frame = tk.Frame(delivery_window, bg=COLORS['background'])
        button_frame.pack(side='bottom', pady=20)

        # Starten
        start_btn = tk.Button(
            button_frame,
            text="✓ Lieferung starten",
            font=FONTS['normal'],
            command=lambda: self.start_delivery(delivery_window),
            bg=COLORS['success'],
            fg='white',
            width=20,
            height=2
        )
        start_btn.pack(side='left', padx=10)

        # Abbrechen
        cancel_btn = tk.Button(
            button_frame,
            text="Abbrechen",
            font=FONTS['normal'],
            command=delivery_window.destroy,
            bg=COLORS['error'],
            fg='white',
            width=20,
            height=2
        )
        cancel_btn.pack(side='right', padx=10)

    def start_delivery(self, window):
        """Startet eine neue Lieferung."""
        supplier = self.supplier_var.get()
        delivery_note = self.delivery_note_entry.get().strip()
        notes = self.notes_text.get("1.0", "end-1c").strip()

        try:
            expected_packages = int(self.package_count_entry.get())
        except ValueError:
            expected_packages = 0

        # Lieferung in DB erstellen
        delivery_id = self.db.create_delivery(
            supplier,
            self.current_user['id'],
            delivery_note,
            expected_packages,
            notes
        )

        if delivery_id:
            self.current_delivery = {
                'id': delivery_id,
                'supplier': supplier,
                'delivery_note': delivery_note,
                'expected_packages': expected_packages,
                'received_packages': 0,
                'start_time': datetime.now()
            }

            window.destroy()
            self.update_delivery_status()
            self.ui.play_sound('success')

            self.status_label.config(
                text=f"✓ Lieferung von {supplier} gestartet",
                fg=COLORS['success']
            )
        else:
            messagebox.showerror("Fehler", "Lieferung konnte nicht erstellt werden!")

    def update_delivery_status(self):
        """Aktualisiert die Anzeige der aktuellen Lieferung."""
        if self.current_delivery:
            info_text = f"""
            Lieferant: {self.current_delivery['supplier']}
            Lieferschein: {self.current_delivery.get('delivery_note', 'N/A')}
            Erwartet: {self.current_delivery['expected_packages']} Pakete
            Empfangen: {self.current_delivery['received_packages']} Pakete
            Start: {self.current_delivery['start_time'].strftime('%H:%M Uhr')}
            """

            self.delivery_info_label.config(
                text=info_text,
                fg=COLORS['text']
            )

            # Abschluss-Button hinzufügen wenn noch nicht vorhanden
            if not hasattr(self, 'finish_delivery_btn'):
                self.finish_delivery_btn = tk.Button(
                    self.delivery_info_frame,
                    text="Lieferung abschließen",
                    font=FONTS['normal'],
                    command=self.finish_delivery,
                    bg=COLORS['warning'],
                    fg='white'
                )
                self.finish_delivery_btn.pack(pady=10)
        else:
            self.delivery_info_label.config(
                text="Keine aktive Lieferung",
                fg=COLORS['text_secondary']
            )

            if hasattr(self, 'finish_delivery_btn'):
                self.finish_delivery_btn.destroy()
                delattr(self, 'finish_delivery_btn')

    def scan_package(self):
        """Öffnet den QR-Code Scanner."""
        if not self.current_delivery:
            messagebox.showwarning("Warnung", "Bitte zuerst eine Lieferung starten!")
            return

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

        # Buttons
        button_frame = tk.Frame(scanner_frame, bg=COLORS['background'])
        button_frame.pack()

        # Neuer QR-Code Button (für neue Pakete)
        new_qr_btn = tk.Button(
            button_frame,
            text="Neuer QR-Code",
            font=FONTS['normal'],
            command=lambda: self.generate_new_qr(scanner_window),
            bg=COLORS['primary'],
            fg='white',
            width=15
        )
        new_qr_btn.pack(side='left', padx=10)

        # Abbrechen-Button
        cancel_btn = tk.Button(
            button_frame,
            text="Fertig",
            font=FONTS['normal'],
            command=scanner_window.destroy,
            bg=COLORS['error'],
            fg='white',
            width=15
        )
        cancel_btn.pack(side='right', padx=10)

        # Simuliere Scan nach 2 Sekunden
        scanner_window.after(2000, lambda: self.process_package_scan("PKG-2024-001234", scanner_window))

    def generate_new_qr(self, parent_window):
        """Generiert einen neuen QR-Code für ein Paket."""
        # Neuen QR-Code generieren
        qr_code = f"PKG-{datetime.now().strftime('%Y')}-{self.generate_package_id()}"

        # Dialog für Paketdetails
        self.show_package_registration(qr_code, parent_window, is_new=True)

    def generate_package_id(self):
        """Generiert eine eindeutige Paket-ID."""
        return ''.join(random.choices(string.digits, k=6))

    def process_package_scan(self, qr_code, scanner_window):
        """Verarbeitet den gescannten QR-Code."""
        # Prüfen ob Paket bereits existiert
        package = self.db.get_package_by_qr(qr_code)

        if package:
            # Paket existiert bereits
            self.status_label.config(
                text=f"⚠ Paket {qr_code} bereits im System!",
                fg=COLORS['warning']
            )
            self.ui.play_sound('error')

            # Info anzeigen
            messagebox.showinfo(
                "Paket vorhanden",
                f"Paket {qr_code} ist bereits registriert.\nStatus: {package.get('status', 'Unbekannt')}"
            )
        else:
            # Neues Paket registrieren
            self.show_package_registration(qr_code, scanner_window, is_new=False)

    def show_package_registration(self, qr_code, parent_window, is_new):
        """Zeigt das Paket-Registrierungsformular."""
        # Registrierungs-Dialog
        reg_window = tk.Toplevel(parent_window)
        reg_window.title("Paket registrieren")
        reg_window.geometry("700x600")
        reg_window.transient(parent_window)
        reg_window.grab_set()

        # Header
        header_label = tk.Label(
            reg_window,
            text=f"{'Neues Paket' if is_new else 'Paket'} registrieren",
            font=FONTS['large'],
            bg=COLORS['background']
        )
        header_label.pack(pady=20)

        # QR-Code anzeigen
        qr_label = tk.Label(
            reg_window,
            text=f"QR-Code: {qr_code}",
            font=FONTS['normal'],
            bg=COLORS['background'],
            fg=COLORS['primary']
        )
        qr_label.pack()

        # Formular
        form_frame = tk.Frame(reg_window, bg=COLORS['background'])
        form_frame.pack(expand=True, fill='both', padx=40, pady=20)

        # Bestellnummer
        order_label = tk.Label(
            form_frame,
            text="Bestellnummer:",
            font=FONTS['normal'],
            bg=COLORS['background']
        )
        order_label.pack(anchor='w', pady=(0, 5))

        order_entry = tk.Entry(
            form_frame,
            font=FONTS['normal'],
            width=30
        )
        order_entry.pack(anchor='w')

        # Kunde
        customer_label = tk.Label(
            form_frame,
            text="Kunde:",
            font=FONTS['normal'],
            bg=COLORS['background']
        )
        customer_label.pack(anchor='w', pady=(15, 5))

        customer_entry = tk.Entry(
            form_frame,
            font=FONTS['normal'],
            width=30
        )
        customer_entry.pack(anchor='w')

        # Artikelanzahl
        item_count_label = tk.Label(
            form_frame,
            text="Anzahl Artikel:",
            font=FONTS['normal'],
            bg=COLORS['background']
        )
        item_count_label.pack(anchor='w', pady=(15, 5))

        item_count_entry = tk.Entry(
            form_frame,
            font=FONTS['normal'],
            width=10
        )
        item_count_entry.pack(anchor='w')
        item_count_entry.insert(0, "1")

        # Priorität
        priority_label = tk.Label(
            form_frame,
            text="Priorität:",
            font=FONTS['normal'],
            bg=COLORS['background']
        )
        priority_label.pack(anchor='w', pady=(15, 5))

        priority_var = tk.StringVar(value="Normal")
        priority_frame = tk.Frame(form_frame, bg=COLORS['background'])
        priority_frame.pack(anchor='w')

        for priority in ["Normal", "Hoch", "Express"]:
            rb = tk.Radiobutton(
                priority_frame,
                text=priority,
                variable=priority_var,
                value=priority,
                font=FONTS['normal'],
                bg=COLORS['background']
            )
            rb.pack(side='left', padx=10)

        # Notizen
        notes_label = tk.Label(
            form_frame,
            text="Notizen:",
            font=FONTS['normal'],
            bg=COLORS['background']
        )
        notes_label.pack(anchor='w', pady=(15, 5))

        notes_text = tk.Text(
            form_frame,
            height=3,
            font=FONTS['normal'],
            wrap='word'
        )
        notes_text.pack(fill='x')

        # Buttons
        button_frame = tk.Frame(reg_window, bg=COLORS['background'])
        button_frame.pack(side='bottom', pady=20)

        # Registrieren
        def register_package():
            # Daten sammeln
            order_id = order_entry.get().strip()
            customer = customer_entry.get().strip()

            try:
                item_count = int(item_count_entry.get())
            except ValueError:
                item_count = 1

            priority = priority_var.get()
            notes = notes_text.get("1.0", "end-1c").strip()

            # Validierung
            if not order_id or not customer:
                messagebox.showwarning("Warnung", "Bitte Bestellnummer und Kunde eingeben!")
                return

            # Paket in DB registrieren
            package_id = self.db.register_package(
                qr_code,
                order_id,
                customer,
                item_count,
                priority,
                self.current_delivery['id'],
                self.current_user['id'],
                notes
            )

            if package_id:
                # Erfolg
                self.current_delivery['received_packages'] += 1
                self.update_delivery_status()
                self.update_recent_entries()
                self.update_statistics()

                reg_window.destroy()

                self.status_label.config(
                    text=f"✓ Paket {qr_code} registriert",
                    fg=COLORS['success']
                )
                self.ui.play_sound('success')

                # Weiter scannen
                parent_window.after(1000, lambda: self.process_package_scan(
                    f"PKG-2024-{self.generate_package_id()}",
                    parent_window
                ))
            else:
                messagebox.showerror("Fehler", "Paket konnte nicht registriert werden!")

        register_btn = tk.Button(
            button_frame,
            text="✓ Registrieren",
            font=FONTS['normal'],
            command=register_package,
            bg=COLORS['success'],
            fg='white',
            width=20,
            height=2
        )
        register_btn.pack(side='left', padx=10)

        # Abbrechen
        cancel_btn = tk.Button(
            button_frame,
            text="Abbrechen",
            font=FONTS['normal'],
            command=reg_window.destroy,
            bg=COLORS['error'],
            fg='white',
            width=20,
            height=2
        )
        cancel_btn.pack(side='right', padx=10)

    def manual_entry(self):
        """Öffnet Dialog für manuelle Paketeingabe."""
        if not self.current_delivery:
            messagebox.showwarning("Warnung", "Bitte zuerst eine Lieferung starten!")
            return

        # Neuen QR-Code generieren und Registrierung zeigen
        qr_code = f"PKG-{datetime.now().strftime('%Y')}-{self.generate_package_id()}"

        # Dummy parent window
        dummy_window = tk.Toplevel(self.root)
        dummy_window.withdraw()

        self.show_package_registration(qr_code, dummy_window, is_new=True)

    def finish_delivery(self):
        """Schließt die aktuelle Lieferung ab."""
        if not self.current_delivery:
            return

        # Bestätigungsdialog
        result = messagebox.askyesno(
            "Lieferung abschließen",
            f"Lieferung von {self.current_delivery['supplier']} abschließen?\n\n"
            f"Empfangen: {self.current_delivery['received_packages']} Pakete"
        )

        if result:
            # Lieferung in DB abschließen
            self.db.finish_delivery(self.current_delivery['id'])

            self.status_label.config(
                text=f"✓ Lieferung abgeschlossen - {self.current_delivery['received_packages']} Pakete",
                fg=COLORS['success']
            )

            self.current_delivery = None
            self.update_delivery_status()
            self.update_statistics()
            self.ui.play_sound('success')

    def update_recent_entries(self):
        """Aktualisiert die Liste der letzten Eingänge."""
        # Alte Einträge löschen
        for widget in self.recent_frame.winfo_children():
            widget.destroy()

        # Letzte Eingänge abrufen
        recent_packages = self.db.get_recent_packages(10)

        if not recent_packages:
            no_entries_label = tk.Label(
                self.recent_frame,
                text="Keine Eingänge heute",
                font=FONTS['normal'],
                bg=COLORS['card'],
                fg=COLORS['text_secondary']
            )
            no_entries_label.pack(pady=20)
        else:
            for package in recent_packages:
                entry_frame = tk.Frame(
                    self.recent_frame,
                    bg=COLORS['background'],
                    relief='raised',
                    bd=1
                )
                entry_frame.pack(fill='x', padx=10, pady=5)

                # Paketinfo
                info_label = tk.Label(
                    entry_frame,
                    text=f"{package['qr_code']} - {package['customer']}",
                    font=FONTS['normal'],
                    bg=COLORS['background']
                )
                info_label.pack(anchor='w', padx=10, pady=(5, 0))

                # Zeitstempel
                time_label = tk.Label(
                    entry_frame,
                    text=package['timestamp'].strftime('%H:%M Uhr'),
                    font=('Arial', 10),
                    bg=COLORS['background'],
                    fg=COLORS['text_secondary']
                )
                time_label.pack(anchor='w', padx=10, pady=(0, 5))

    def update_statistics(self):
        """Aktualisiert die Statistiken."""
        stats = self.db.get_receiving_statistics(self.current_user['id'])
        self.stats_label.config(
            text=f"Heute: {stats.get('deliveries', 0)} Lieferungen | {stats.get('packages', 0)} Pakete"
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
            # Offene Lieferung warnen
            if self.current_delivery:
                result = messagebox.askyesno(
                    "Warnung",
                    "Es gibt eine offene Lieferung. Trotzdem abmelden?"
                )
                if not result:
                    return

            self.db.clock_out(self.current_user['id'])
            self.logger.info(f"Benutzer {self.current_user['name']} abgemeldet")

        self.current_user = None
        self.current_delivery = None
        self.registered_packages = []
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
    app = WareneingangApp()
    app.run()


if __name__ == "__main__":
    main()