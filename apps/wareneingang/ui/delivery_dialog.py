#!/usr/bin/env python3
"""
Shirtful WMS - Delivery Dialog
Dialog für neue Lieferungen
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Dict, Any, Callable, Optional
import sys
import os

# Projekt-Root zum Python-Path hinzufügen
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from utils.ui_components import COLORS, FONTS
from utils.logger import setup_logger


class DeliveryDialog:
    """Dialog für die Erfassung einer neuen Lieferung."""

    def __init__(self, parent: tk.Tk, on_delivery_created: Callable[[Dict[str, Any]], None]):
        """
        Initialisiert den Lieferungs-Dialog.

        Args:
            parent: Eltern-Fenster
            on_delivery_created: Callback-Funktion für erfolgreiche Lieferungserstellung
        """
        self.parent = parent
        self.on_delivery_created = on_delivery_created
        self.logger = setup_logger('delivery_dialog')

        # Dialog-Fenster
        self.window = None
        self.dialog_result = None

        # Formular-Variablen
        self.supplier_var = tk.StringVar()
        self.delivery_note_entry = None
        self.package_count_entry = None
        self.notes_text = None

        # Verfügbare Lieferanten
        self.suppliers = [
            "DHL",
            "UPS",
            "DPD",
            "GLS",
            "Hermes",
            "Deutsche Post",
            "FedEx",
            "TNT",
            "Direktlieferung",
            "Abholung",
            "Sonstige"
        ]

    def show(self) -> Optional[Dict[str, Any]]:
        """
        Zeigt den Dialog und gibt die Lieferungsdaten zurück.

        Returns:
            Optional[Dict]: Lieferungsdaten oder None bei Abbruch
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

        return self.dialog_result

    def _create_dialog(self):
        """Erstellt das Dialog-Fenster."""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Neue Lieferung erfassen")
        self.window.geometry("700x650")
        self.window.configure(bg=COLORS['background'])
        self.window.resizable(False, False)

        # Dialog-Schließung behandeln
        self.window.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def _center_dialog(self):
        """Zentriert den Dialog auf dem Eltern-Fenster."""
        # Warten bis Dialog vollständig geladen ist
        self.window.update_idletasks()

        # Positionen berechnen
        x = self.parent.winfo_rootx() + (self.parent.winfo_width() // 2) - (self.window.winfo_width() // 2)
        y = self.parent.winfo_rooty() + (self.parent.winfo_height() // 2) - (self.window.winfo_height() // 2)

        # Sicherstellen, dass Dialog auf dem Bildschirm bleibt
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
        header_frame = tk.Frame(self.window, bg=COLORS['primary'], height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        # Titel mit Icon
        title_label = tk.Label(
            header_frame,
            text="🚚 Neue Lieferung erfassen",
            font=FONTS['large'],
            bg=COLORS['primary'],
            fg='white'
        )
        title_label.pack(pady=15)

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

        # Lieferant
        self._create_supplier_section(form_frame)

        # Lieferschein-Nummer
        self._create_delivery_note_section(form_frame)

        # Erwartete Pakete
        self._create_package_count_section(form_frame)

        # Notizen
        self._create_notes_section(form_frame)

    def _create_supplier_section(self, parent):
        """Erstellt die Lieferanten-Auswahl."""
        # Überschrift
        supplier_label = tk.Label(
            parent,
            text="Lieferant: *",
            font=FONTS['normal'],
            bg=COLORS['background'],
            fg=COLORS['text']
        )
        supplier_label.pack(anchor='w', pady=(15, 5))

        # Dropdown mit Suche
        self.supplier_var.set(self.suppliers[0])

        supplier_frame = tk.Frame(parent, bg=COLORS['background'])
        supplier_frame.pack(anchor='w', fill='x')

        self.supplier_combo = ttk.Combobox(
            supplier_frame,
            textvariable=self.supplier_var,
            values=self.suppliers,
            font=FONTS['normal'],
            state='readonly',
            width=35
        )
        self.supplier_combo.pack(side='left')

        # Info-Button
        info_btn = tk.Button(
            supplier_frame,
            text="ℹ️",
            font=('Arial', 10),
            command=self._show_supplier_info,
            bg=COLORS['card'],
            relief='flat',
            width=3
        )
        info_btn.pack(side='left', padx=(10, 0))

    def _create_delivery_note_section(self, parent):
        """Erstellt die Lieferschein-Nummer Eingabe."""
        # Überschrift
        delivery_note_label = tk.Label(
            parent,
            text="Lieferschein-Nr. (optional):",
            font=FONTS['normal'],
            bg=COLORS['background'],
            fg=COLORS['text']
        )
        delivery_note_label.pack(anchor='w', pady=(20, 5))

        # Eingabefeld
        delivery_note_frame = tk.Frame(parent, bg=COLORS['background'])
        delivery_note_frame.pack(anchor='w', fill='x')

        self.delivery_note_entry = tk.Entry(
            delivery_note_frame,
            font=FONTS['normal'],
            width=37
        )
        self.delivery_note_entry.pack(side='left')

        # QR-Code Scan Button für Lieferschein
        qr_scan_btn = tk.Button(
            delivery_note_frame,
            text="📷",
            font=('Arial', 10),
            command=self._scan_delivery_note,
            bg=COLORS['primary'],
            fg='white',
            relief='raised',
            width=3
        )
        qr_scan_btn.pack(side='left', padx=(10, 0))

    def _create_package_count_section(self, parent):
        """Erstellt die Eingabe für erwartete Pakete."""
        # Überschrift
        package_count_label = tk.Label(
            parent,
            text="Erwartete Anzahl Pakete:",
            font=FONTS['normal'],
            bg=COLORS['background'],
            fg=COLORS['text']
        )
        package_count_label.pack(anchor='w', pady=(20, 5))

        # Container für Eingabe und Buttons
        count_frame = tk.Frame(parent, bg=COLORS['background'])
        count_frame.pack(anchor='w')

        # Eingabefeld
        self.package_count_entry = tk.Entry(
            count_frame,
            font=FONTS['normal'],
            width=10,
            justify='right'
        )
        self.package_count_entry.pack(side='left')
        self.package_count_entry.insert(0, "1")

        # Plus/Minus Buttons
        minus_btn = tk.Button(
            count_frame,
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
            count_frame,
            text="+",
            font=('Arial', 12, 'bold'),
            command=self._increase_count,
            bg=COLORS['success'],
            fg='white',
            width=3,
            relief='raised'
        )
        plus_btn.pack(side='left', padx=(2, 0))

        # Hinweis
        hint_label = tk.Label(
            parent,
            text="Tipp: Die Anzahl kann später angepasst werden",
            font=('Arial', 9),
            bg=COLORS['background'],
            fg=COLORS['text_secondary']
        )
        hint_label.pack(anchor='w', pady=(5, 0))

    def _create_notes_section(self, parent):
        """Erstellt den Notizen-Bereich."""
        # Überschrift
        notes_label = tk.Label(
            parent,
            text="Notizen / Besonderheiten:",
            font=FONTS['normal'],
            bg=COLORS['background'],
            fg=COLORS['text']
        )
        notes_label.pack(anchor='w', pady=(20, 5))

        # Textbereich mit Scrollbar
        notes_frame = tk.Frame(parent, bg=COLORS['background'])
        notes_frame.pack(anchor='w', fill='x')

        self.notes_text = tk.Text(
            notes_frame,
            height=4,
            font=FONTS['normal'],
            wrap='word',
            width=50
        )

        notes_scrollbar = ttk.Scrollbar(notes_frame, orient="vertical", command=self.notes_text.yview)
        self.notes_text.configure(yscrollcommand=notes_scrollbar.set)

        self.notes_text.pack(side='left', fill='x', expand=True)
        notes_scrollbar.pack(side='right', fill='y')

        # Beispieltext einfügen
        example_text = "z.B. Fragile Ware, Express-Lieferung, Sonderabmessungen..."
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

    def _create_buttons(self):
        """Erstellt die Aktions-Buttons."""
        # Button-Bereich am unteren Rand
        button_frame = tk.Frame(self.window, bg=COLORS['background'], height=80)
        button_frame.pack(side='bottom', fill='x', pady=15)
        button_frame.pack_propagate(False)

        # Button-Container für zentrierte Anordnung
        button_container = tk.Frame(button_frame, bg=COLORS['background'])
        button_container.pack(expand=True)

        # Lieferung starten (Hauptaktion)
        start_btn = tk.Button(
            button_container,
            text="✅ Lieferung starten",
            font=FONTS['normal'],
            command=self._on_start_delivery,
            bg=COLORS['success'],
            fg='white',
            relief='raised',
            bd=3,
            padx=25,
            pady=12,
            cursor='hand2'
        )
        start_btn.pack(side='left', padx=15)

        # Speichern als Entwurf
        draft_btn = tk.Button(
            button_container,
            text="📝 Als Entwurf speichern",
            font=FONTS['normal'],
            command=self._on_save_draft,
            bg=COLORS['warning'],
            fg='white',
            relief='raised',
            bd=2,
            padx=20,
            pady=10,
            cursor='hand2'
        )
        draft_btn.pack(side='left', padx=10)

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

    def _show_supplier_info(self):
        """Zeigt Informationen zu Lieferanten."""
        info_text = """
Verfügbare Lieferanten:

• DHL, UPS, DPD, GLS: Paketdienste
• Deutsche Post: Standardversand
• FedEx, TNT: Express-Dienste
• Direktlieferung: Lieferant kommt selbst
• Abholung: Ware wird abgeholt
• Sonstige: Andere Transportwege

Bei 'Sonstige' bitte Details in Notizen angeben.
        """
        messagebox.showinfo("Lieferanten-Info", info_text.strip())

    def _scan_delivery_note(self):
        """Simuliert QR-Code Scan für Lieferschein."""
        # Placeholder für echten QR-Scanner
        result = messagebox.askquestion(
            "QR-Code Scanner",
            "QR-Code Scanner simulieren?\n(Fügt Beispiel-Lieferschein ein)"
        )

        if result == 'yes':
            sample_delivery_note = f"LN-{datetime.now().strftime('%Y%m%d%H%M')}"
            self.delivery_note_entry.delete(0, tk.END)
            self.delivery_note_entry.insert(0, sample_delivery_note)

    def _increase_count(self):
        """Erhöht die Paket-Anzahl."""
        try:
            current = int(self.package_count_entry.get())
            self.package_count_entry.delete(0, tk.END)
            self.package_count_entry.insert(0, str(current + 1))
        except ValueError:
            self.package_count_entry.delete(0, tk.END)
            self.package_count_entry.insert(0, "1")

    def _decrease_count(self):
        """Verringert die Paket-Anzahl."""
        try:
            current = int(self.package_count_entry.get())
            if current > 0:
                self.package_count_entry.delete(0, tk.END)
                self.package_count_entry.insert(0, str(current - 1))
        except ValueError:
            self.package_count_entry.delete(0, tk.END)
            self.package_count_entry.insert(0, "0")

    def _validate_form(self) -> tuple[bool, str]:
        """
        Validiert das Formular.

        Returns:
            tuple: (is_valid, error_message)
        """
        # Lieferant prüfen
        supplier = self.supplier_var.get().strip()
        if not supplier:
            return False, "Bitte wählen Sie einen Lieferanten aus."

        # Paket-Anzahl prüfen
        try:
            package_count = int(self.package_count_entry.get())
            if package_count < 0:
                return False, "Anzahl Pakete kann nicht negativ sein."
        except ValueError:
            return False, "Bitte geben Sie eine gültige Anzahl für Pakete ein."

        return True, ""

    def _collect_form_data(self) -> Dict[str, Any]:
        """
        Sammelt die Formular-Daten.

        Returns:
            Dict: Formulardaten
        """
        # Notizen bereinigen
        notes = self.notes_text.get("1.0", "end-1c").strip()
        example_text = "z.B. Fragile Ware, Express-Lieferung, Sonderabmessungen..."
        if notes == example_text:
            notes = ""

        return {
            'supplier': self.supplier_var.get().strip(),
            'delivery_note': self.delivery_note_entry.get().strip(),
            'expected_packages': int(self.package_count_entry.get()),
            'notes': notes,
            'created_at': datetime.now(),
            'status': 'active'
        }

    def _on_start_delivery(self):
        """Behandelt das Starten einer neuen Lieferung."""
        # Validierung
        is_valid, error_msg = self._validate_form()
        if not is_valid:
            messagebox.showerror("Eingabefehler", error_msg)
            return

        # Daten sammeln
        delivery_data = self._collect_form_data()

        # Bestätigung
        confirmation_text = f"""
Neue Lieferung starten?

Lieferant: {delivery_data['supplier']}
Lieferschein: {delivery_data['delivery_note'] or 'Nicht angegeben'}
Erwartete Pakete: {delivery_data['expected_packages']}

Die Lieferung wird sofort aktiv und kann verwendet werden.
        """

        result = messagebox.askyesno("Lieferung starten", confirmation_text.strip())
        if result:
            try:
                # Erfolg
                self.dialog_result = delivery_data
                self.logger.info(f"Neue Lieferung erstellt: {delivery_data['supplier']}")

                # Callback aufrufen
                if self.on_delivery_created:
                    self.on_delivery_created(delivery_data)

                # Dialog schließen
                self.window.destroy()

            except Exception as e:
                self.logger.error(f"Fehler beim Erstellen der Lieferung: {e}")
                messagebox.showerror("Fehler", f"Lieferung konnte nicht erstellt werden:\n{str(e)}")

    def _on_save_draft(self):
        """Behandelt das Speichern als Entwurf."""
        # Validierung (weniger streng)
        supplier = self.supplier_var.get().strip()
        if not supplier:
            messagebox.showwarning("Warnung", "Mindestens ein Lieferant muss ausgewählt werden.")
            return

        # Daten sammeln
        delivery_data = self._collect_form_data()
        delivery_data['status'] = 'draft'

        # Bestätigung
        result = messagebox.askyesno(
            "Entwurf speichern",
            "Lieferung als Entwurf speichern?\nSie kann später fortgesetzt werden."
        )

        if result:
            try:
                self.dialog_result = delivery_data
                self.logger.info(f"Lieferung als Entwurf gespeichert: {delivery_data['supplier']}")

                # Callback aufrufen
                if self.on_delivery_created:
                    self.on_delivery_created(delivery_data)

                # Dialog schließen
                self.window.destroy()

            except Exception as e:
                self.logger.error(f"Fehler beim Speichern des Entwurfs: {e}")
                messagebox.showerror("Fehler", f"Entwurf konnte nicht gespeichert werden:\n{str(e)}")

    def _on_cancel(self):
        """Behandelt das Abbrechen des Dialogs."""
        # Prüfen ob Änderungen vorhanden sind
        has_changes = (
                self.delivery_note_entry.get().strip() or
                self.package_count_entry.get() != "1" or
                (self.notes_text.get("1.0", "end-1c").strip() and
                 self.notes_text.get("1.0",
                                     "end-1c").strip() != "z.B. Fragile Ware, Express-Lieferung, Sonderabmessungen...")
        )

        if has_changes:
            result = messagebox.askyesno(
                "Abbrechen bestätigen",
                "Es gibt ungespeicherte Änderungen.\nTrotzdem abbrechen?"
            )
            if not result:
                return

        self.dialog_result = None
        self.logger.info("Lieferungs-Dialog abgebrochen")
        self.window.destroy()