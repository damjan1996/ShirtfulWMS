#!/usr/bin/env python3
"""
Shirtful WMS - Package Registration Dialog
Dialog für die Registrierung von Paketen
"""

import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from typing import Dict, Any, Callable, Optional, List
import sys
import os

# Projekt-Root zum Python-Path hinzufügen
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from utils.ui_components import COLORS, FONTS
from utils.logger import setup_logger
from config.translations import Translations


class PackageRegistrationDialog:
    """Dialog für die Registrierung von Paketen."""

    def __init__(self, parent: tk.Tk, qr_code: str, on_package_registered: Callable[[Dict[str, Any]], None],
                 is_new_package: bool = False):
        """
        Initialisiert den Paket-Registrierungs-Dialog.

        Args:
            parent: Eltern-Fenster
            qr_code: QR-Code des Pakets
            on_package_registered: Callback bei erfolgreicher Registrierung
            is_new_package: True wenn neues Paket erstellt wird
        """
        self.parent = parent
        self.qr_code = qr_code
        self.on_package_registered = on_package_registered
        self.is_new_package = is_new_package
        self.logger = setup_logger('package_registration')

        # Komponenten
        self.translations = Translations()

        # Dialog-Fenster
        self.window = None
        self.dialog_result = None

        # Formular-Elemente
        self.order_entry = None
        self.customer_entry = None
        self.item_count_entry = None
        self.priority_var = tk.StringVar()
        self.notes_text = None
        self.weight_entry = None
        self.dimensions_entries = {}
        self.special_handling_vars = {}

        # Prioritäten
        self.priorities = ["Normal", "Hoch", "Express", "Eilig", "Kritisch"]

        # Spezial-Behandlungen
        self.special_handlings = [
            ("fragile", "Zerbrechlich"),
            ("heavy", "Schwer (>20kg)"),
            ("oversized", "Übergroß"),
            ("hazardous", "Gefahrgut"),
            ("temperature", "Temperaturkritisch"),
            ("express", "Express-Zustellung")
        ]

    def show(self) -> Optional[Dict[str, Any]]:
        """
        Zeigt den Dialog und gibt die Paket-Daten zurück.

        Returns:
            Optional[Dict]: Paket-Daten oder None bei Abbruch
        """
        self._create_dialog()
        self._setup_ui()

        # Modal anzeigen
        self.window.transient(self.parent)
        self.window.grab_set()
        self.window.focus_set()

        # Zentrieren
        self._center_dialog()

        # Focus auf erstes Eingabefeld
        if self.order_entry:
            self.order_entry.focus_set()

        # Warten bis Dialog geschlossen wird
        self.parent.wait_window(self.window)

        return self.dialog_result

    def _create_dialog(self):
        """Erstellt das Dialog-Fenster."""
        title = "Neues Paket registrieren" if self.is_new_package else "Paket registrieren"

        self.window = tk.Toplevel(self.parent)
        self.window.title(title)
        self.window.geometry("800x700")
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
        self._create_header()

        # Hauptbereich mit Scrollbar
        self._create_main_area()

        # Formular
        self._create_form()

        # Buttons
        self._create_buttons()

    def _create_header(self):
        """Erstellt den Header-Bereich."""
        header_frame = tk.Frame(self.window, bg=COLORS['primary'], height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        # Titel und QR-Code
        icon = "📦" if self.is_new_package else "📋"
        title = f"{icon} Paket registrieren"

        title_label = tk.Label(
            header_frame,
            text=title,
            font=FONTS['large'],
            bg=COLORS['primary'],
            fg='white'
        )
        title_label.pack(side='left', padx=20, pady=20)

        # QR-Code anzeigen
        qr_label = tk.Label(
            header_frame,
            text=f"QR: {self.qr_code}",
            font=('Arial', 14, 'bold'),
            bg=COLORS['primary'],
            fg='white'
        )
        qr_label.pack(side='right', padx=20, pady=20)

    def _create_main_area(self):
        """Erstellt den Hauptbereich mit Scrollbar."""
        # Container für Scrollbereich
        container = tk.Frame(self.window, bg=COLORS['background'])
        container.pack(expand=True, fill='both', padx=20, pady=10)

        # Canvas für Scrolling
        canvas = tk.Canvas(container, bg=COLORS['background'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)

        self.scrollable_frame = tk.Frame(canvas, bg=COLORS['background'])

        # Scrolling konfigurieren
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Mausrad-Scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<MouseWheel>", _on_mousewheel)

        # Layout
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _create_form(self):
        """Erstellt das Eingabeformular."""
        # Formular-Container
        form_frame = tk.Frame(self.scrollable_frame, bg=COLORS['background'])
        form_frame.pack(expand=True, fill='both', padx=20, pady=10)

        # Grunddaten
        self._create_basic_info_section(form_frame)

        # Paket-Details
        self._create_package_details_section(form_frame)

        # Spezial-Behandlung
        self._create_special_handling_section(form_frame)

        # Notizen
        self._create_notes_section(form_frame)

    def _create_basic_info_section(self, parent):
        """Erstellt die Grunddaten-Sektion."""
        # Überschrift
        basic_label = tk.Label(
            parent,
            text="📋 Grunddaten",
            font=('Arial', 14, 'bold'),
            bg=COLORS['background'],
            fg=COLORS['text']
        )
        basic_label.pack(anchor='w', pady=(10, 15))

        # Container
        basic_frame = tk.Frame(parent, bg=COLORS['card'], relief='raised', bd=2)
        basic_frame.pack(fill='x', pady=(0, 20), padx=10)

        content_frame = tk.Frame(basic_frame, bg=COLORS['card'])
        content_frame.pack(fill='x', padx=20, pady=15)

        # Bestellnummer
        self._create_field(
            content_frame,
            "Bestellnummer: *",
            "order_entry",
            placeholder="z.B. ORD-2024-123456",
            required=True
        )

        # Kunde
        self._create_field(
            content_frame,
            "Kunde: *",
            "customer_entry",
            placeholder="Name oder Firma des Kunden",
            required=True,
            pady_top=15
        )

        # Artikel-Anzahl
        count_frame = tk.Frame(content_frame, bg=COLORS['card'])
        count_frame.pack(anchor='w', fill='x', pady=(15, 0))

        tk.Label(
            count_frame,
            text="Anzahl Artikel: *",
            font=FONTS['normal'],
            bg=COLORS['card'],
            fg=COLORS['text']
        ).pack(anchor='w', pady=(0, 5))

        count_input_frame = tk.Frame(count_frame, bg=COLORS['card'])
        count_input_frame.pack(anchor='w')

        self.item_count_entry = tk.Entry(
            count_input_frame,
            font=FONTS['normal'],
            width=10,
            justify='right'
        )
        self.item_count_entry.pack(side='left')
        self.item_count_entry.insert(0, "1")

        # Plus/Minus Buttons
        minus_btn = tk.Button(
            count_input_frame,
            text="−",
            font=('Arial', 12, 'bold'),
            command=self._decrease_count,
            bg=COLORS['error'],
            fg='white',
            width=3,
            relief='raised'
        )
        minus_btn.pack(side='left', padx=(10, 2))

        plus_btn = tk.Button(
            count_input_frame,
            text="+",
            font=('Arial', 12, 'bold'),
            command=self._increase_count,
            bg=COLORS['success'],
            fg='white',
            width=3,
            relief='raised'
        )
        plus_btn.pack(side='left', padx=(2, 0))

    def _create_package_details_section(self, parent):
        """Erstellt die Paket-Details-Sektion."""
        # Überschrift
        details_label = tk.Label(
            parent,
            text="📏 Paket-Details",
            font=('Arial', 14, 'bold'),
            bg=COLORS['background'],
            fg=COLORS['text']
        )
        details_label.pack(anchor='w', pady=(10, 15))

        # Container
        details_frame = tk.Frame(parent, bg=COLORS['card'], relief='raised', bd=2)
        details_frame.pack(fill='x', pady=(0, 20), padx=10)

        content_frame = tk.Frame(details_frame, bg=COLORS['card'])
        content_frame.pack(fill='x', padx=20, pady=15)

        # Priorität
        self._create_priority_section(content_frame)

        # Gewicht
        self._create_field(
            content_frame,
            "Gewicht (kg):",
            "weight_entry",
            placeholder="z.B. 2.5",
            width=10,
            pady_top=15
        )

        # Abmessungen
        self._create_dimensions_section(content_frame)

    def _create_priority_section(self, parent):
        """Erstellt die Prioritäts-Auswahl."""
        priority_frame = tk.Frame(parent, bg=COLORS['card'])
        priority_frame.pack(anchor='w', fill='x', pady=(0, 15))

        tk.Label(
            priority_frame,
            text="Priorität:",
            font=FONTS['normal'],
            bg=COLORS['card'],
            fg=COLORS['text']
        ).pack(anchor='w', pady=(0, 10))

        self.priority_var.set("Normal")

        # Horizontale Anordnung der Prioritäten
        priority_buttons_frame = tk.Frame(priority_frame, bg=COLORS['card'])
        priority_buttons_frame.pack(anchor='w')

        for priority in self.priorities:
            # Farbe basierend auf Priorität
            color = COLORS['text_secondary']
            if priority == "Hoch":
                color = COLORS['warning']
            elif priority in ["Express", "Eilig", "Kritisch"]:
                color = COLORS['error']

            rb = tk.Radiobutton(
                priority_buttons_frame,
                text=priority,
                variable=self.priority_var,
                value=priority,
                font=FONTS['normal'],
                bg=COLORS['card'],
                fg=color,
                selectcolor=COLORS['background'],
                command=self._on_priority_changed
            )
            rb.pack(side='left', padx=10)

    def _create_dimensions_section(self, parent):
        """Erstellt die Abmessungs-Eingabe."""
        dim_frame = tk.Frame(parent, bg=COLORS['card'])
        dim_frame.pack(anchor='w', fill='x', pady=(15, 0))

        tk.Label(
            dim_frame,
            text="Abmessungen (cm):",
            font=FONTS['normal'],
            bg=COLORS['card'],
            fg=COLORS['text']
        ).pack(anchor='w', pady=(0, 10))

        dim_input_frame = tk.Frame(dim_frame, bg=COLORS['card'])
        dim_input_frame.pack(anchor='w')

        # Länge, Breite, Höhe
        dimensions = [("length", "Länge"), ("width", "Breite"), ("height", "Höhe")]

        for i, (key, label) in enumerate(dimensions):
            if i > 0:
                tk.Label(
                    dim_input_frame,
                    text=" × ",
                    font=FONTS['normal'],
                    bg=COLORS['card'],
                    fg=COLORS['text']
                ).pack(side='left')

            tk.Label(
                dim_input_frame,
                text=f"{label}:",
                font=('Arial', 9),
                bg=COLORS['card'],
                fg=COLORS['text_secondary']
            ).pack(side='left')

            entry = tk.Entry(
                dim_input_frame,
                font=FONTS['normal'],
                width=8,
                justify='right'
            )
            entry.pack(side='left', padx=(5, 10))
            self.dimensions_entries[key] = entry

    def _create_special_handling_section(self, parent):
        """Erstellt die Spezial-Behandlungs-Sektion."""
        # Überschrift
        special_label = tk.Label(
            parent,
            text="⚠️ Spezial-Behandlung",
            font=('Arial', 14, 'bold'),
            bg=COLORS['background'],
            fg=COLORS['text']
        )
        special_label.pack(anchor='w', pady=(10, 15))

        # Container
        special_frame = tk.Frame(parent, bg=COLORS['card'], relief='raised', bd=2)
        special_frame.pack(fill='x', pady=(0, 20), padx=10)

        content_frame = tk.Frame(special_frame, bg=COLORS['card'])
        content_frame.pack(fill='x', padx=20, pady=15)

        # Checkboxes für spezielle Behandlungen
        special_grid = tk.Frame(content_frame, bg=COLORS['card'])
        special_grid.pack(anchor='w', fill='x')

        for i, (key, label) in enumerate(self.special_handlings):
            row = i // 2
            col = i % 2

            var = tk.BooleanVar()
            self.special_handling_vars[key] = var

            cb = tk.Checkbutton(
                special_grid,
                text=label,
                variable=var,
                font=FONTS['normal'],
                bg=COLORS['card'],
                fg=COLORS['text'],
                selectcolor=COLORS['background'],
                command=lambda k=key: self._on_special_handling_changed(k)
            )
            cb.grid(row=row, column=col, sticky='w', padx=(0, 20), pady=5)

    def _create_notes_section(self, parent):
        """Erstellt die Notizen-Sektion."""
        # Überschrift
        notes_label = tk.Label(
            parent,
            text="📝 Notizen",
            font=('Arial', 14, 'bold'),
            bg=COLORS['background'],
            fg=COLORS['text']
        )
        notes_label.pack(anchor='w', pady=(10, 15))

        # Container
        notes_frame = tk.Frame(parent, bg=COLORS['card'], relief='raised', bd=2)
        notes_frame.pack(fill='x', pady=(0, 20), padx=10)

        content_frame = tk.Frame(notes_frame, bg=COLORS['card'])
        content_frame.pack(fill='x', padx=20, pady=15)

        # Textbereich
        notes_container = tk.Frame(content_frame, bg=COLORS['card'])
        notes_container.pack(fill='x')

        self.notes_text = tk.Text(
            notes_container,
            height=4,
            font=FONTS['normal'],
            wrap='word',
            bg='white',
            relief='sunken',
            bd=1
        )

        notes_scrollbar = ttk.Scrollbar(notes_container, orient="vertical", command=self.notes_text.yview)
        self.notes_text.configure(yscrollcommand=notes_scrollbar.set)

        self.notes_text.pack(side='left', fill='both', expand=True)
        notes_scrollbar.pack(side='right', fill='y')

        # Beispieltext einfügen
        example_text = "Zusätzliche Informationen zum Paket..."
        self.notes_text.insert("1.0", example_text)
        self.notes_text.config(fg=COLORS['text_secondary'])

        # Event-Handler für Platzhalter-Text
        def on_focus_in(event):
            if self.notes_text.get("1.0", "end-1c") == example_text:
                self.notes_text.delete("1.0", "end")
                self.notes_text.config(fg=COLORS['text'])

        def on_focus_out(event):
            if not self.notes_text.get("1.0", "end-1c").strip():
                self.notes_text.insert("1.0", example_text)
                self.notes_text.config(fg=COLORS['text_secondary'])

        self.notes_text.bind("<FocusIn>", on_focus_in)
        self.notes_text.bind("<FocusOut>", on_focus_out)

    def _create_field(self, parent, label_text, field_name, placeholder="", width=30, required=False, pady_top=0):
        """
        Erstellt ein Eingabefeld.

        Args:
            parent: Eltern-Widget
            label_text: Label-Text
            field_name: Name des Attributs für das Entry-Widget
            placeholder: Platzhalter-Text
            width: Breite des Eingabefelds
            required: Ob das Feld erforderlich ist
            pady_top: Zusätzlicher Abstand oben
        """
        field_frame = tk.Frame(parent, bg=COLORS['card'])
        field_frame.pack(anchor='w', fill='x', pady=(pady_top, 0))

        # Label
        label = tk.Label(
            field_frame,
            text=label_text,
            font=FONTS['normal'],
            bg=COLORS['card'],
            fg=COLORS['error'] if required else COLORS['text']
        )
        label.pack(anchor='w', pady=(0, 5))

        # Entry
        entry = tk.Entry(
            field_frame,
            font=FONTS['normal'],
            width=width
        )
        entry.pack(anchor='w')

        # Platzhalter
        if placeholder:
            entry.insert(0, placeholder)
            entry.config(fg=COLORS['text_secondary'])

            def on_focus_in(event):
                if entry.get() == placeholder:
                    entry.delete(0, tk.END)
                    entry.config(fg=COLORS['text'])

            def on_focus_out(event):
                if not entry.get().strip():
                    entry.insert(0, placeholder)
                    entry.config(fg=COLORS['text_secondary'])

            entry.bind("<FocusIn>", on_focus_in)
            entry.bind("<FocusOut>", on_focus_out)

        # Widget speichern
        setattr(self, field_name, entry)

    def _create_buttons(self):
        """Erstellt die Aktions-Buttons."""
        # Button-Bereich am unteren Rand
        button_frame = tk.Frame(self.window, bg=COLORS['background'], height=80)
        button_frame.pack(side='bottom', fill='x', pady=15)
        button_frame.pack_propagate(False)

        # Button-Container für zentrierte Anordnung
        button_container = tk.Frame(button_frame, bg=COLORS['background'])
        button_container.pack(expand=True)

        # Registrieren (Hauptaktion)
        register_btn = tk.Button(
            button_container,
            text="✅ Paket registrieren",
            font=FONTS['normal'],
            command=self._on_register,
            bg=COLORS['success'],
            fg='white',
            relief='raised',
            bd=3,
            padx=25,
            pady=12,
            cursor='hand2'
        )
        register_btn.pack(side='left', padx=15)

        # Speichern und weiter
        save_continue_btn = tk.Button(
            button_container,
            text="💾 Speichern & Weiter",
            font=FONTS['normal'],
            command=self._on_save_and_continue,
            bg=COLORS['primary'],
            fg='white',
            relief='raised',
            bd=2,
            padx=20,
            pady=10,
            cursor='hand2'
        )
        save_continue_btn.pack(side='left', padx=10)

        # Abbrechen
        cancel_btn = tk.Button(
            button_container,
            text="❌ Abbrechen",
            font=FONTS['normal'],
            command=self._on_cancel,
            bg=COLORS['error'],
            fg='white',
            relief='raised',
            bd=2,
            padx=20,
            pady=10,
            cursor='hand2'
        )
        cancel_btn.pack(side='left', padx=15)

    def _increase_count(self):
        """Erhöht die Artikel-Anzahl."""
        try:
            current = int(self.item_count_entry.get())
            self.item_count_entry.delete(0, tk.END)
            self.item_count_entry.insert(0, str(current + 1))
        except ValueError:
            self.item_count_entry.delete(0, tk.END)
            self.item_count_entry.insert(0, "1")

    def _decrease_count(self):
        """Verringert die Artikel-Anzahl."""
        try:
            current = int(self.item_count_entry.get())
            if current > 1:
                self.item_count_entry.delete(0, tk.END)
                self.item_count_entry.insert(0, str(current - 1))
        except ValueError:
            self.item_count_entry.delete(0, tk.END)
            self.item_count_entry.insert(0, "1")

    def _on_priority_changed(self):
        """Behandelt Prioritäts-Änderungen."""
        priority = self.priority_var.get()

        # Automatische Spezial-Behandlung bei hoher Priorität
        if priority in ["Express", "Eilig", "Kritisch"]:
            self.special_handling_vars["express"].set(True)
        elif priority == "Normal":
            self.special_handling_vars["express"].set(False)

    def _on_special_handling_changed(self, handling_type: str):
        """
        Behandelt Änderungen bei Spezial-Behandlungen.

        Args:
            handling_type: Typ der Spezial-Behandlung
        """
        # Logik für abhängige Behandlungen
        if handling_type == "express" and self.special_handling_vars["express"].get():
            if self.priority_var.get() == "Normal":
                self.priority_var.set("Hoch")

        if handling_type == "hazardous" and self.special_handling_vars["hazardous"].get():
            # Warnung anzeigen
            messagebox.showwarning(
                "Gefahrgut",
                "Gefahrgut erfordert spezielle Dokumentation und Behandlung!\n\n"
                "Bitte stellen Sie sicher, dass alle Vorschriften eingehalten werden."
            )

    def _validate_form(self) -> tuple[bool, str]:
        """
        Validiert das Formular.

        Returns:
            tuple: (is_valid, error_message)
        """
        # Bestellnummer prüfen
        order_id = self._get_field_value(self.order_entry, "z.B. ORD-2024-123456")
        if not order_id:
            return False, "Bestellnummer ist erforderlich."

        # Kunde prüfen
        customer = self._get_field_value(self.customer_entry, "Name oder Firma des Kunden")
        if not customer:
            return False, "Kunde ist erforderlich."

        # Artikel-Anzahl prüfen
        try:
            item_count = int(self.item_count_entry.get())
            if item_count <= 0:
                return False, "Anzahl Artikel muss größer als 0 sein."
        except ValueError:
            return False, "Bitte geben Sie eine gültige Anzahl für Artikel ein."

        # Gewicht prüfen (optional)
        weight_str = self._get_field_value(self.weight_entry, "z.B. 2.5")
        if weight_str:
            try:
                weight = float(weight_str)
                if weight <= 0:
                    return False, "Gewicht muss größer als 0 sein."
                if weight > 1000:  # 1 Tonne
                    return False, "Gewicht scheint unrealistisch hoch zu sein."
            except ValueError:
                return False, "Bitte geben Sie ein gültiges Gewicht ein (Dezimalzahl)."

        # Abmessungen prüfen (optional)
        for dim_name, entry in self.dimensions_entries.items():
            value = entry.get().strip()
            if value:
                try:
                    dim_value = float(value)
                    if dim_value <= 0:
                        return False, f"Abmessung ({dim_name}) muss größer als 0 sein."
                    if dim_value > 1000:  # 10 Meter
                        return False, f"Abmessung ({dim_name}) scheint unrealistisch groß zu sein."
                except ValueError:
                    return False, f"Bitte geben Sie eine gültige {dim_name} ein (Dezimalzahl)."

        return True, ""

    def _get_field_value(self, entry: tk.Entry, placeholder: str) -> str:
        """
        Ruft den Wert eines Eingabefelds ab, berücksichtigt Platzhalter.

        Args:
            entry: Eingabefeld
            placeholder: Platzhalter-Text

        Returns:
            str: Bereinigter Wert
        """
        value = entry.get().strip()
        if value == placeholder:
            return ""
        return value

    def _collect_form_data(self) -> Dict[str, Any]:
        """
        Sammelt die Formular-Daten.

        Returns:
            Dict: Formulardaten
        """
        # Grunddaten
        order_id = self._get_field_value(self.order_entry, "z.B. ORD-2024-123456")
        customer = self._get_field_value(self.customer_entry, "Name oder Firma des Kunden")
        item_count = int(self.item_count_entry.get())
        priority = self.priority_var.get()

        # Notizen bereinigen
        notes = self.notes_text.get("1.0", "end-1c").strip()
        if notes == "Zusätzliche Informationen zum Paket...":
            notes = ""

        # Gewicht
        weight_str = self._get_field_value(self.weight_entry, "z.B. 2.5")
        weight = float(weight_str) if weight_str else None

        # Abmessungen
        dimensions = {}
        for dim_name, entry in self.dimensions_entries.items():
            value = entry.get().strip()
            if value:
                try:
                    dimensions[dim_name] = float(value)
                except ValueError:
                    pass

        # Spezial-Behandlungen
        special_handlings = []
        for key, var in self.special_handling_vars.items():
            if var.get():
                special_handlings.append(key)

        return {
            'package_id': self.qr_code,
            'order_id': order_id,
            'customer': customer,
            'item_count': item_count,
            'priority': priority,
            'notes': notes,
            'weight': weight,
            'dimensions': dimensions,
            'special_handlings': special_handlings,
            'created_at': datetime.now(),
            'is_new_package': self.is_new_package
        }

    def _on_register(self):
        """Behandelt die Paket-Registrierung."""
        # Validierung
        is_valid, error_msg = self._validate_form()
        if not is_valid:
            messagebox.showerror("Eingabefehler", error_msg)
            return

        # Daten sammeln
        package_data = self._collect_form_data()

        # Bestätigung (bei kritischen Paketen)
        if self._needs_confirmation(package_data):
            if not self._show_confirmation(package_data):
                return

        try:
            # Erfolg
            self.dialog_result = package_data
            self.logger.info(f"Paket {self.qr_code} registriert")

            # Callback aufrufen
            if self.on_package_registered:
                self.on_package_registered(package_data)

            # Dialog schließen
            self.window.destroy()

        except Exception as e:
            self.logger.error(f"Fehler beim Registrieren des Pakets: {e}")
            messagebox.showerror("Fehler", f"Paket konnte nicht registriert werden:\n{str(e)}")

    def _on_save_and_continue(self):
        """Behandelt Speichern und weiter zum nächsten Paket."""
        # Gleiche Validierung und Speicherung wie bei Registrierung
        self._on_register()

        # Falls erfolgreich, wurde der Dialog bereits geschlossen
        # Hier könnte zusätzliche Logik für "weiter" stehen

    def _needs_confirmation(self, package_data: Dict[str, Any]) -> bool:
        """
        Prüft ob eine Bestätigung benötigt wird.

        Args:
            package_data: Paket-Daten

        Returns:
            bool: True wenn Bestätigung nötig
        """
        # Bestätigung bei kritischen Eigenschaften
        if package_data['priority'] in ["Express", "Eilig", "Kritisch"]:
            return True

        if "hazardous" in package_data['special_handlings']:
            return True

        if package_data.get('weight', 0) > 50:  # Schwere Pakete
            return True

        return False

    def _show_confirmation(self, package_data: Dict[str, Any]) -> bool:
        """
        Zeigt Bestätigungsdialog für kritische Pakete.

        Args:
            package_data: Paket-Daten

        Returns:
            bool: True wenn bestätigt
        """
        # Bestätigungstext erstellen
        warnings = []

        if package_data['priority'] in ["Express", "Eilig", "Kritisch"]:
            warnings.append(f"🚨 Hohe Priorität: {package_data['priority']}")

        if "hazardous" in package_data['special_handlings']:
            warnings.append("☢️ Gefahrgut - Spezielle Behandlung erforderlich")

        if package_data.get('weight', 0) > 50:
            warnings.append(f"⚠️ Schweres Paket: {package_data['weight']} kg")

        confirmation_text = f"""
Paket registrieren?

QR-Code: {package_data['package_id']}
Kunde: {package_data['customer']}
Bestellung: {package_data['order_id']}

WARNUNGEN:
{chr(10).join(warnings)}

Möchten Sie fortfahren?
        """

        return messagebox.askyesno("Bestätigung erforderlich", confirmation_text.strip())

    def _on_cancel(self):
        """Behandelt das Abbrechen des Dialogs."""
        # Prüfen ob Änderungen vorhanden sind
        has_changes = self._has_form_changes()

        if has_changes:
            result = messagebox.askyesno(
                "Abbrechen bestätigen",
                "Es gibt ungespeicherte Änderungen.\nTrotzdem abbrechen?"
            )
            if not result:
                return

        self.dialog_result = None
        self.logger.info("Paket-Registrierung abgebrochen")
        self.window.destroy()

    def _has_form_changes(self) -> bool:
        """
        Prüft ob das Formular Änderungen enthält.

        Returns:
            bool: True wenn Änderungen vorhanden
        """
        # Einfache Prüfung auf nicht-leere Felder
        order_value = self._get_field_value(self.order_entry, "z.B. ORD-2024-123456")
        customer_value = self._get_field_value(self.customer_entry, "Name oder Firma des Kunden")

        if order_value or customer_value:
            return True

        if self.item_count_entry.get() != "1":
            return True

        if self.priority_var.get() != "Normal":
            return True

        # Spezial-Behandlungen prüfen
        for var in self.special_handling_vars.values():
            if var.get():
                return True

        return False