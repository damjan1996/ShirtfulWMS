#!/usr/bin/env python3
"""
Shirtful WMS - Login Screen
Login-Bildschirm für RFID-Authentifizierung
"""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable, Optional, Dict, Any
import sys
import os

# Projekt-Root zum Python-Path hinzufügen
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from utils.ui_components import COLORS, FONTS
from utils.rfid_auth import RFIDAuth
from utils.logger import setup_logger
from config.translations import Translations


class LoginScreen:
    """Login-Bildschirm für die Wareneingang-Anwendung."""

    def __init__(self, parent: tk.Tk, on_login_success: Callable[[Dict[str, Any]], None]):
        """
        Initialisiert den Login-Bildschirm.

        Args:
            parent: Hauptfenster
            on_login_success: Callback-Funktion bei erfolgreichem Login
        """
        self.parent = parent
        self.on_login_success = on_login_success
        self.logger = setup_logger('login_screen')

        # Komponenten
        self.rfid = RFIDAuth()
        self.translations = Translations()

        # UI-Elemente
        self.main_frame = None
        self.rfid_status_label = None
        self.waiting_label = None
        self.manual_login_button = None
        self.test_card_button = None

        # Status
        self.language = 'de'
        self.scanning_active = False
        self.scan_job_id = None

    def setup(self):
        """Erstellt den Login-Bildschirm."""
        self._clear_screen()
        self._create_main_frame()
        self._create_title()
        self._create_login_area()
        self._create_manual_login_button()
        self._create_test_button()
        self._create_language_selector()
        self._start_rfid_scanning()

    def _clear_screen(self):
        """Löscht alle Widgets vom Bildschirm."""
        for widget in self.parent.winfo_children():
            widget.destroy()

    def _create_main_frame(self):
        """Erstellt den Haupt-Container."""
        self.main_frame = tk.Frame(self.parent, bg=COLORS['background'])
        self.main_frame.pack(expand=True, fill='both', padx=50, pady=50)

    def _create_title(self):
        """Erstellt den Titel-Bereich."""
        title_label = tk.Label(
            self.main_frame,
            text="📥 WARENEINGANG",
            font=FONTS['title'],
            bg=COLORS['background'],
            fg=COLORS['primary']
        )
        title_label.pack(pady=(0, 50))

    def _create_login_area(self):
        """Erstellt den Login-Bereich."""
        # RFID-Login Container
        login_frame = tk.Frame(
            self.main_frame,
            bg=COLORS['card'],
            relief='raised',
            bd=2
        )
        login_frame.pack(expand=True, fill='both', padx=100, pady=50)

        # Anweisungstext
        instruction_text = self.translations.get('login_instruction', 'Bitte RFID-Karte an Lesegerät halten')
        instruction_label = tk.Label(
            login_frame,
            text=instruction_text,
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
        waiting_text = self.translations.get('waiting_for_card', 'Warte auf Karte...')
        self.waiting_label = tk.Label(
            login_frame,
            text=waiting_text,
            font=FONTS['normal'],
            bg=COLORS['card'],
            fg=COLORS['text_secondary']
        )
        self.waiting_label.pack(pady=(0, 50))

    def _create_manual_login_button(self):
        """Erstellt den manuellen Login-Button."""
        self.manual_login_button = tk.Button(
            self.main_frame,
            text="🔐 Manual Login",
            font=('Arial', 12, 'bold'),
            bg=COLORS['success'],
            fg='white',
            command=self._show_manual_login,
            pady=10,
            relief='raised',
            bd=2,
            cursor='hand2'
        )
        self.manual_login_button.pack(pady=20)

    def _create_test_button(self):
        """Erstellt den Test-Karten-Button."""
        self.test_card_button = tk.Button(
            self.main_frame,
            text="🎯 Test-Karte simulieren",
            font=('Arial', 10),
            bg=COLORS['primary'],
            fg='white',
            command=self._simulate_test_card,
            pady=5,
            relief='raised',
            bd=2,
            cursor='hand2'
        )
        self.test_card_button.pack(pady=10)

    def _create_language_selector(self):
        """Erstellt die Sprachauswahl."""
        language_frame = tk.Frame(self.main_frame, bg=COLORS['background'])
        language_frame.pack(side='bottom', pady=20)

        # Sprachauswahl-Label
        lang_label = tk.Label(
            language_frame,
            text="Sprache / Language:",
            font=('Arial', 10),
            bg=COLORS['background'],
            fg=COLORS['text_secondary']
        )
        lang_label.pack(pady=(0, 10))

        # Sprach-Buttons
        languages = [
            ('de', '🇩🇪 Deutsch'),
            ('en', '🇬🇧 English'),
            ('tr', '🇹🇷 Türkçe'),
            ('pl', '🇵🇱 Polski')
        ]

        button_container = tk.Frame(language_frame, bg=COLORS['background'])
        button_container.pack()

        for lang_code, lang_text in languages:
            btn = tk.Button(
                button_container,
                text=lang_text,
                font=('Arial', 9),
                command=lambda l=lang_code: self._change_language(l),
                width=12,
                height=1,
                relief='raised',
                bd=1,
                bg=COLORS['card'] if lang_code == self.language else COLORS['background'],
                cursor='hand2'
            )
            btn.pack(side='left', padx=3)

    def _start_rfid_scanning(self):
        """Startet den RFID-Scan-Prozess."""
        if self.scanning_active:
            return

        self.scanning_active = True
        self.logger.info("RFID-Scanning gestartet")
        self._scan_rfid_loop()

    def _stop_rfid_scanning(self):
        """Stoppt den RFID-Scan-Prozess."""
        self.scanning_active = False
        if self.scan_job_id:
            self.parent.after_cancel(self.scan_job_id)
            self.scan_job_id = None
        self.logger.info("RFID-Scanning gestoppt")

    def _scan_rfid_loop(self):
        """RFID-Scan-Schleife."""
        if not self.scanning_active:
            return

        try:
            # Versuche RFID-Tag zu lesen
            tag_id = self.rfid.read_tag()
            if tag_id:
                self._process_rfid_tag(tag_id)
                return

        except Exception as e:
            self.logger.error(f"Fehler beim RFID-Scan: {e}")

        # Nächsten Scan planen
        self.scan_job_id = self.parent.after(1000, self._scan_rfid_loop)

    def _process_rfid_tag(self, tag_id: str):
        """
        Verarbeitet eine gelesene RFID-Karte.

        Args:
            tag_id: ID der RFID-Karte
        """
        self.logger.info(f"RFID-Tag erkannt: {tag_id}")
        self._stop_rfid_scanning()

        # Visual Feedback
        self.rfid_status_label.config(text="⏳", fg=COLORS['warning'])
        self.waiting_label.config(
            text=self.translations.get('validating', 'Validiere Karte...'),
            fg=COLORS['warning']
        )

        # Mitarbeiter-Lookup
        employee = self.rfid.get_employee_by_rfid(tag_id)

        if employee:
            self._handle_successful_login(employee)
        else:
            self._handle_failed_login()

    def _handle_successful_login(self, employee: Dict[str, Any]):
        """
        Behandelt erfolgreichen Login.

        Args:
            employee: Mitarbeiter-Daten
        """
        self.logger.info(f"Erfolgreicher Login: {employee['first_name']} {employee['last_name']}")

        # Visual Feedback
        self.rfid_status_label.config(text="✅", fg=COLORS['success'])
        welcome_text = self.translations.get(
            'welcome_user',
            f"Willkommen {employee['first_name']} {employee['last_name']}!"
        )
        self.waiting_label.config(text=welcome_text, fg=COLORS['success'])

        # Kurz warten, dann zum Hauptbildschirm
        self.parent.after(1500, lambda: self._complete_login(employee))

    def _handle_failed_login(self):
        """Behandelt fehlgeschlagenen Login."""
        self.logger.warning("Unbekannte RFID-Karte")

        # Visual Feedback
        self.rfid_status_label.config(text="❌", fg=COLORS['error'])
        error_text = self.translations.get('unknown_card', 'Unbekannte Karte!')
        self.waiting_label.config(text=error_text, fg=COLORS['error'])

        # Nach 2 Sekunden zurücksetzen
        self.parent.after(2000, self._reset_login_status)

    def _reset_login_status(self):
        """Setzt den Login-Status zurück."""
        self.rfid_status_label.config(text="🔓", fg=COLORS['warning'])
        waiting_text = self.translations.get('waiting_for_card', 'Warte auf Karte...')
        self.waiting_label.config(text=waiting_text, fg=COLORS['text_secondary'])

        # RFID-Scanning wieder starten
        self._start_rfid_scanning()

    def _complete_login(self, employee: Dict[str, Any]):
        """
        Schließt den Login-Prozess ab.

        Args:
            employee: Mitarbeiter-Daten
        """
        try:
            # Sprache des Mitarbeiters übernehmen
            if 'language' in employee:
                self.language = employee['language']
                self.translations.set_language(self.language)

            # Login-Callback aufrufen
            self.on_login_success(employee)

        except Exception as e:
            self.logger.error(f"Fehler beim Abschließen des Logins: {e}")
            messagebox.showerror("Fehler", f"Login konnte nicht abgeschlossen werden:\n{str(e)}")
            self._reset_login_status()

    def _show_manual_login(self):
        """Zeigt den manuellen Login-Dialog."""
        self.logger.info("Manueller Login angefordert")

        # RFID-Scanning temporär stoppen
        was_scanning = self.scanning_active
        self._stop_rfid_scanning()

        # Dialog erstellen
        dialog = ManualLoginDialog(self.parent, self.translations)
        employee = dialog.show()

        if employee:
            self._complete_login(employee)
        else:
            # RFID-Scanning wieder aufnehmen falls es aktiv war
            if was_scanning:
                self._start_rfid_scanning()

    def _simulate_test_card(self):
        """Simuliert eine Test-RFID-Karte."""
        self.logger.info("Test-Karte wird simuliert")

        # Visual Feedback
        self.rfid_status_label.config(text="🎯", fg=COLORS['primary'])
        self.waiting_label.config(text="Test-Karte erkannt...", fg=COLORS['primary'])

        # Test-Mitarbeiter erstellen
        test_employee = {
            'id': 999,
            'rfid_card': 'test123',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'worker',
            'language': self.language,
            'department': 'Wareneingang'
        }

        # Nach kurzer Verzögerung Login simulieren
        self.parent.after(1000, lambda: self._handle_successful_login(test_employee))

    def _change_language(self, language: str):
        """
        Ändert die Sprache der Anwendung.

        Args:
            language: Sprachcode (de, en, tr, pl)
        """
        self.language = language
        self.translations.set_language(language)
        self.logger.info(f"Sprache geändert zu: {language}")

        # UI neu aufbauen
        self.setup()

    def destroy(self):
        """Zerstört den Login-Bildschirm und räumt auf."""
        self._stop_rfid_scanning()
        if self.main_frame:
            self.main_frame.destroy()


class ManualLoginDialog:
    """Dialog für manuellen Login."""

    def __init__(self, parent: tk.Tk, translations: Translations):
        """
        Initialisiert den manuellen Login-Dialog.

        Args:
            parent: Eltern-Fenster
            translations: Übersetzungen
        """
        self.parent = parent
        self.translations = translations
        self.logger = setup_logger('manual_login_dialog')

        self.window = None
        self.employee_var = None
        self.result = None

    def show(self) -> Optional[Dict[str, Any]]:
        """
        Zeigt den Dialog und gibt den ausgewählten Mitarbeiter zurück.

        Returns:
            Optional[Dict]: Mitarbeiter-Daten oder None bei Abbruch
        """
        self._create_dialog()
        self._setup_ui()

        # Modal anzeigen
        self.window.transient(self.parent)
        self.window.grab_set()
        self.window.focus_set()

        # Zentrieren
        self._center_dialog()

        # Warten bis Dialog geschlossen wird
        self.parent.wait_window(self.window)

        return self.result

    def _create_dialog(self):
        """Erstellt das Dialog-Fenster."""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Manueller Login")
        self.window.geometry("450x350")
        self.window.configure(bg=COLORS['background'])
        self.window.resizable(False, False)

        # Dialog-Schließung behandeln
        self.window.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def _center_dialog(self):
        """Zentriert den Dialog."""
        self.window.update_idletasks()

        x = self.parent.winfo_rootx() + (self.parent.winfo_width() // 2) - (self.window.winfo_width() // 2)
        y = self.parent.winfo_rooty() + (self.parent.winfo_height() // 2) - (self.window.winfo_height() // 2)

        x = max(0, x)
        y = max(0, y)

        self.window.geometry(f"+{x}+{y}")

    def _setup_ui(self):
        """Erstellt die Benutzeroberfläche."""
        # Header
        header = tk.Label(
            self.window,
            text="🔐 Manueller Login",
            font=('Arial', 16, 'bold'),
            bg=COLORS['background'],
            fg=COLORS['text']
        )
        header.pack(pady=30)

        # Beschreibung
        desc_label = tk.Label(
            self.window,
            text="Wählen Sie einen Mitarbeiter für den Login aus:",
            font=('Arial', 12),
            bg=COLORS['background'],
            fg=COLORS['text']
        )
        desc_label.pack(pady=10)

        # Mitarbeiter-Auswahl
        self._create_employee_selection()

        # Buttons
        self._create_buttons()

    def _create_employee_selection(self):
        """Erstellt die Mitarbeiter-Auswahl."""
        selection_frame = tk.Frame(self.window, bg=COLORS['background'])
        selection_frame.pack(pady=20, padx=40, fill='x')

        # Label
        tk.Label(
            selection_frame,
            text="Mitarbeiter:",
            font=('Arial', 12),
            bg=COLORS['background'],
            fg=COLORS['text']
        ).pack(anchor='w', pady=(0, 10))

        # Test-Mitarbeiter
        employees = [
            ("Max Mustermann", "Supervisor", "max.mustermann"),
            ("Anna Schmidt", "Sachbearbeiter", "anna.schmidt"),
            ("Test User", "Mitarbeiter", "test.user"),
            ("John Doe", "Aushilfe", "john.doe"),
            ("Demo Account", "Admin", "demo.admin")
        ]

        # Dropdown
        self.employee_var = tk.StringVar()
        employee_display = [f"{name} ({role})" for name, role, _ in employees]

        employee_combo = ttk.Combobox(
            selection_frame,
            textvariable=self.employee_var,
            values=employee_display,
            state="readonly",
            font=('Arial', 11),
            width=35
        )
        employee_combo.pack(fill='x', pady=5)
        employee_combo.set(employee_display[0])  # Default

        # Zusätzliche Info
        info_label = tk.Label(
            selection_frame,
            text="Dies ist nur für Testzwecke gedacht.\nIn der Produktion sollte RFID verwendet werden.",
            font=('Arial', 9),
            bg=COLORS['background'],
            fg=COLORS['text_secondary'],
            justify='center'
        )
        info_label.pack(pady=(15, 0))

        # Employee data für Lookup speichern
        self.employees_data = []
        for i, (name, role, username) in enumerate(employees):
            first_name, last_name = name.split(' ', 1)
            self.employees_data.append({
                'id': i + 1,
                'rfid_card': f'manual_{username}',
                'first_name': first_name,
                'last_name': last_name,
                'role': role.lower().replace(' ', '_'),
                'username': username,
                'department': 'Wareneingang',
                'language': 'de'
            })

    def _create_buttons(self):
        """Erstellt die Aktions-Buttons."""
        button_frame = tk.Frame(self.window, bg=COLORS['background'])
        button_frame.pack(pady=30)

        # Anmelden
        login_btn = tk.Button(
            button_frame,
            text="✅ Anmelden",
            font=('Arial', 12, 'bold'),
            bg=COLORS['success'],
            fg='white',
            command=self._on_login,
            relief='raised',
            bd=2,
            padx=25,
            pady=8,
            cursor='hand2'
        )
        login_btn.pack(side=tk.LEFT, padx=15)

        # Abbrechen
        cancel_btn = tk.Button(
            button_frame,
            text="❌ Abbrechen",
            font=('Arial', 12),
            bg=COLORS['error'],
            fg='white',
            command=self._on_cancel,
            relief='raised',
            bd=2,
            padx=25,
            pady=8,
            cursor='hand2'
        )
        cancel_btn.pack(side=tk.LEFT, padx=15)

    def _on_login(self):
        """Behandelt den Login."""
        selected = self.employee_var.get()
        if not selected:
            messagebox.showwarning("Warnung", "Bitte wählen Sie einen Mitarbeiter aus.")
            return

        # Mitarbeiter-Index finden
        employee_display = [f"{emp['first_name']} {emp['last_name']} ({emp['role'].replace('_', ' ').title()})"
                            for emp in self.employees_data]

        try:
            index = employee_display.index(selected)
            employee = self.employees_data[index].copy()

            self.logger.info(f"Manueller Login: {employee['first_name']} {employee['last_name']}")
            self.result = employee
            self.window.destroy()

        except (IndexError, ValueError) as e:
            self.logger.error(f"Fehler bei Mitarbeiter-Auswahl: {e}")
            messagebox.showerror("Fehler", "Ungültige Mitarbeiter-Auswahl.")

    def _on_cancel(self):
        """Behandelt das Abbrechen."""
        self.logger.info("Manueller Login abgebrochen")
        self.result = None
        self.window.destroy()