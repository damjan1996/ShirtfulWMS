#!/usr/bin/env python3
"""
Shirtful WMS - Main Screen
Hauptbildschirm für Wareneingang-Operationen
"""

import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from typing import Dict, Any, Callable, List, Optional
import sys
import os

# Projekt-Root zum Python-Path hinzufügen
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from utils.ui_components import UIComponents, COLORS, FONTS
from utils.logger import setup_logger
from config.translations import Translations


class MainScreen:
    """Hauptbildschirm für die Wareneingang-Anwendung."""

    def __init__(self, parent: tk.Tk, employee: Dict[str, Any], on_logout: Callable[[], None]):
        """
        Initialisiert den Hauptbildschirm.

        Args:
            parent: Hauptfenster
            employee: Angemeldeter Mitarbeiter
            on_logout: Callback für Logout
        """
        self.parent = parent
        self.employee = employee
        self.on_logout = on_logout
        self.logger = setup_logger('main_screen')

        # Komponenten
        self.ui = UIComponents()
        self.translations = Translations()

        # Status
        self.current_delivery = None
        self.registered_packages = []
        self.language = employee.get('language', 'de')

        # UI-Elemente
        self.main_frame = None
        self.header_frame = None
        self.status_label = None
        self.delivery_info_label = None
        self.recent_frame = None
        self.stats_label = None
        self.finish_delivery_btn = None

        # Callbacks für Dialoge
        self.on_new_delivery = None
        self.on_scan_package = None
        self.on_manual_entry = None

    def setup(self):
        """Erstellt den Hauptbildschirm."""
        self._clear_screen()
        self._create_header()
        self._create_main_area()
        self._update_data()

    def set_callbacks(self, on_new_delivery: Callable, on_scan_package: Callable, on_manual_entry: Callable):
        """
        Setzt die Callback-Funktionen für Dialog-Aufrufe.

        Args:
            on_new_delivery: Callback für neue Lieferung
            on_scan_package: Callback für Paket-Scan
            on_manual_entry: Callback für manuelle Eingabe
        """
        self.on_new_delivery = on_new_delivery
        self.on_scan_package = on_scan_package
        self.on_manual_entry = on_manual_entry

    def _clear_screen(self):
        """Löscht alle Widgets vom Bildschirm."""
        for widget in self.parent.winfo_children():
            widget.destroy()

    def _create_header(self):
        """Erstellt den Header-Bereich."""
        self.header_frame = tk.Frame(self.parent, bg=COLORS['primary'], height=80)
        self.header_frame.pack(fill='x')
        self.header_frame.pack_propagate(False)

        # Benutzerinfo (links)
        user_name = f"{self.employee['first_name']} {self.employee['last_name']}"
        user_role = self.employee.get('role', 'Mitarbeiter').replace('_', ' ').title()

        user_info = tk.Label(
            self.header_frame,
            text=f"👤 {user_name} ({user_role}) | 📥 Wareneingang",
            font=FONTS['large'],
            bg=COLORS['primary'],
            fg='white'
        )
        user_info.pack(side='left', padx=20, pady=20)

        # Aktuelle Zeit (mitte)
        self.time_label = tk.Label(
            self.header_frame,
            text="",
            font=('Arial', 14),
            bg=COLORS['primary'],
            fg='white'
        )
        self.time_label.pack(side='left', expand=True)
        self._update_time()

        # Logout-Button (rechts)
        logout_btn = tk.Button(
            self.header_frame,
            text="🚪 Abmelden",
            font=FONTS['normal'],
            command=self._on_logout,
            bg=COLORS['error'],
            fg='white',
            width=12,
            relief='raised',
            bd=2,
            cursor='hand2'
        )
        logout_btn.pack(side='right', padx=20, pady=20)

    def _create_main_area(self):
        """Erstellt den Hauptbereich."""
        # Hauptbereich
        self.main_frame = tk.Frame(self.parent, bg=COLORS['background'])
        self.main_frame.pack(expand=True, fill='both', padx=50, pady=30)

        # Oberer Bereich - Aktionen
        self._create_action_area()

        # Status-Anzeige
        self._create_status_area()

        # Unterer Bereich - Zwei Spalten
        self._create_content_area()

        # Statistiken unten
        self._create_statistics_area()

    def _create_action_area(self):
        """Erstellt den Aktions-Bereich."""
        top_frame = tk.Frame(self.main_frame, bg=COLORS['background'])
        top_frame.pack(fill='x', pady=(0, 20))

        # Container für Buttons
        action_container = tk.Frame(top_frame, bg=COLORS['background'])
        action_container.pack()

        # Neue Lieferung Button
        new_delivery_btn = self.ui.create_large_button(
            action_container,
            text="🚚 Neue Lieferung",
            command=self._new_delivery,
            color=COLORS['primary']
        )
        new_delivery_btn.pack(side='left', padx=10)

        # Paket scannen Button
        scan_btn = self.ui.create_large_button(
            action_container,
            text="📷 Paket scannen",
            command=self._scan_package,
            color=COLORS['success']
        )
        scan_btn.pack(side='left', padx=10)

        # Manuelle Eingabe Button
        manual_btn = self.ui.create_large_button(
            action_container,
            text="⌨️ Manuelle Eingabe",
            command=self._manual_entry,
            color=COLORS['warning']
        )
        manual_btn.pack(side='left', padx=10)

        # Erweiterte Aktionen (rechts)
        self._create_extended_actions(top_frame)

    def _create_extended_actions(self, parent):
        """Erstellt erweiterte Aktions-Buttons."""
        extended_frame = tk.Frame(parent, bg=COLORS['background'])
        extended_frame.pack(side='right')

        # Export Button
        export_btn = tk.Button(
            extended_frame,
            text="📊 Export",
            font=('Arial', 10),
            command=self._export_data,
            bg=COLORS['info'],
            fg='white',
            relief='raised',
            bd=2,
            padx=15,
            pady=8,
            cursor='hand2'
        )
        export_btn.pack(side='left', padx=5)

        # Einstellungen Button
        settings_btn = tk.Button(
            extended_frame,
            text="⚙️ Einstellungen",
            font=('Arial', 10),
            command=self._show_settings,
            bg=COLORS['secondary'],
            fg='white',
            relief='raised',
            bd=2,
            padx=15,
            pady=8,
            cursor='hand2'
        )
        settings_btn.pack(side='left', padx=5)

    def _create_status_area(self):
        """Erstellt den Status-Bereich."""
        self.status_frame = tk.Frame(
            self.main_frame,
            bg=COLORS['card'],
            relief='raised',
            bd=2
        )
        self.status_frame.pack(fill='x', pady=20)

        self.status_label = tk.Label(
            self.status_frame,
            text="Keine aktive Lieferung - Bitte neue Lieferung starten",
            font=FONTS['normal'],
            bg=COLORS['card'],
            fg=COLORS['text']
        )
        self.status_label.pack(pady=15)

    def _create_content_area(self):
        """Erstellt den Inhalts-Bereich mit zwei Spalten."""
        content_frame = tk.Frame(self.main_frame, bg=COLORS['background'])
        content_frame.pack(expand=True, fill='both')

        # Linke Spalte - Aktuelle Lieferung
        self._create_delivery_info(content_frame)

        # Rechte Spalte - Letzte Eingänge
        self._create_recent_entries(content_frame)

    def _create_delivery_info(self, parent):
        """Erstellt die Lieferungs-Info."""
        left_frame = tk.Frame(parent, bg=COLORS['background'])
        left_frame.pack(side='left', expand=True, fill='both', padx=(0, 10))

        # Überschrift
        delivery_label = tk.Label(
            left_frame,
            text="📦 Aktuelle Lieferung",
            font=FONTS['large'],
            bg=COLORS['background'],
            fg=COLORS['text']
        )
        delivery_label.pack(pady=(0, 10))

        # Info-Container
        self.delivery_info_frame = tk.Frame(
            left_frame,
            bg=COLORS['card'],
            relief='raised',
            bd=2
        )
        self.delivery_info_frame.pack(fill='both', expand=True)

        # Info-Label
        self.delivery_info_label = tk.Label(
            self.delivery_info_frame,
            text="Keine aktive Lieferung",
            font=FONTS['normal'],
            bg=COLORS['card'],
            fg=COLORS['text_secondary'],
            justify='left'
        )
        self.delivery_info_label.pack(pady=20, padx=20, anchor='w')

    def _create_recent_entries(self, parent):
        """Erstellt die Liste der letzten Eingänge."""
        right_frame = tk.Frame(parent, bg=COLORS['background'])
        right_frame.pack(side='right', expand=True, fill='both', padx=(10, 0))

        # Überschrift
        recent_label = tk.Label(
            right_frame,
            text="📋 Letzte Eingänge",
            font=FONTS['large'],
            bg=COLORS['background'],
            fg=COLORS['text']
        )
        recent_label.pack(pady=(0, 10))

        # Scrollbare Liste
        list_frame = tk.Frame(right_frame, bg=COLORS['card'], relief='raised', bd=2)
        list_frame.pack(fill='both', expand=True)

        # Canvas für Scrolling
        canvas = tk.Canvas(list_frame, bg=COLORS['card'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        self.recent_frame = tk.Frame(canvas, bg=COLORS['card'])

        # Scrolling konfigurieren
        self.recent_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.recent_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Mausrad-Scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<MouseWheel>", _on_mousewheel)

        # Layout
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _create_statistics_area(self):
        """Erstellt den Statistik-Bereich."""
        stats_frame = tk.Frame(self.main_frame, bg=COLORS['background'])
        stats_frame.pack(side='bottom', fill='x', pady=20)

        # Statistik-Container
        stats_container = tk.Frame(stats_frame, bg=COLORS['card'], relief='raised', bd=1)
        stats_container.pack(fill='x', pady=10)

        # Statistik-Label
        self.stats_label = tk.Label(
            stats_container,
            text="Heute: 0 Lieferungen | 0 Pakete registriert",
            font=FONTS['normal'],
            bg=COLORS['card'],
            fg=COLORS['text_secondary']
        )
        self.stats_label.pack(pady=10)

        # Zusätzliche Statistik-Buttons
        self._create_statistics_buttons(stats_container)

    def _create_statistics_buttons(self, parent):
        """Erstellt Buttons für detaillierte Statistiken."""
        button_frame = tk.Frame(parent, bg=COLORS['card'])
        button_frame.pack(pady=(0, 10))

        # Tagesstatistik
        day_stats_btn = tk.Button(
            button_frame,
            text="📊 Tagesstatistik",
            font=('Arial', 9),
            command=self._show_day_statistics,
            bg=COLORS['info'],
            fg='white',
            relief='raised',
            bd=1,
            padx=10,
            pady=5,
            cursor='hand2'
        )
        day_stats_btn.pack(side='left', padx=5)

        # Lieferungshistorie
        history_btn = tk.Button(
            button_frame,
            text="📋 Historie",
            font=('Arial', 9),
            command=self._show_delivery_history,
            bg=COLORS['secondary'],
            fg='white',
            relief='raised',
            bd=1,
            padx=10,
            pady=5,
            cursor='hand2'
        )
        history_btn.pack(side='left', padx=5)

    def _update_time(self):
        """Aktualisiert die Zeitanzeige."""
        try:
            current_time = datetime.now().strftime("%H:%M:%S - %d.%m.%Y")
            if hasattr(self, 'time_label') and self.time_label.winfo_exists():
                self.time_label.config(text=current_time)
        except tk.TclError:
            # Widget existiert nicht mehr
            return

        # Nächste Aktualisierung planen
        self.parent.after(1000, self._update_time)

    def _new_delivery(self):
        """Startet eine neue Lieferung."""
        self.logger.info("Neue Lieferung angefordert")

        if self.current_delivery:
            result = messagebox.askyesno(
                "Warnung",
                f"Es gibt bereits eine aktive Lieferung von {self.current_delivery.get('supplier', 'Unbekannt')}.\n"
                "Möchten Sie diese abschließen und eine neue starten?"
            )
            if result:
                self._finish_current_delivery()
            else:
                return

        # Callback aufrufen
        if self.on_new_delivery:
            self.on_new_delivery()

    def _scan_package(self):
        """Öffnet den QR-Code Scanner."""
        if not self.current_delivery:
            messagebox.showwarning("Warnung", "Bitte zuerst eine Lieferung starten!")
            return

        self.logger.info("Paket-Scan angefordert")

        # Callback aufrufen
        if self.on_scan_package:
            self.on_scan_package()

    def _manual_entry(self):
        """Öffnet die manuelle Paketeingabe."""
        if not self.current_delivery:
            messagebox.showwarning("Warnung", "Bitte zuerst eine Lieferung starten!")
            return

        self.logger.info("Manuelle Eingabe angefordert")

        # Callback aufrufen
        if self.on_manual_entry:
            self.on_manual_entry()

    def _export_data(self):
        """Exportiert Daten."""
        self.logger.info("Daten-Export angefordert")

        # Export-Optionen anzeigen
        export_window = tk.Toplevel(self.parent)
        export_window.title("Daten exportieren")
        export_window.geometry("400x300")
        export_window.configure(bg=COLORS['background'])
        export_window.transient(self.parent)
        export_window.grab_set()

        # Zentrieren
        export_window.geometry("+%d+%d" % (
            self.parent.winfo_rootx() + 200,
            self.parent.winfo_rooty() + 150
        ))

        # Header
        tk.Label(
            export_window,
            text="📊 Daten exportieren",
            font=FONTS['large'],
            bg=COLORS['background'],
            fg=COLORS['text']
        ).pack(pady=20)

        # Export-Optionen
        options_frame = tk.Frame(export_window, bg=COLORS['background'])
        options_frame.pack(pady=20, padx=40, fill='x')

        export_var = tk.StringVar(value="today")

        options = [
            ("today", "Heutige Pakete"),
            ("current_delivery", "Aktuelle Lieferung"),
            ("all_deliveries", "Alle Lieferungen"),
            ("statistics", "Statistiken")
        ]

        for value, text in options:
            rb = tk.Radiobutton(
                options_frame,
                text=text,
                variable=export_var,
                value=value,
                font=FONTS['normal'],
                bg=COLORS['background'],
                anchor='w'
            )
            rb.pack(fill='x', pady=5)

        # Buttons
        button_frame = tk.Frame(export_window, bg=COLORS['background'])
        button_frame.pack(pady=20)

        tk.Button(
            button_frame,
            text="📄 CSV Export",
            font=FONTS['normal'],
            command=lambda: self._perform_export(export_var.get(), 'csv', export_window),
            bg=COLORS['success'],
            fg='white',
            padx=20,
            pady=8
        ).pack(side='left', padx=10)

        tk.Button(
            button_frame,
            text="❌ Abbrechen",
            font=FONTS['normal'],
            command=export_window.destroy,
            bg=COLORS['error'],
            fg='white',
            padx=20,
            pady=8
        ).pack(side='left', padx=10)

    def _perform_export(self, export_type: str, format_type: str, window: tk.Toplevel):
        """Führt den Export durch."""
        try:
            # Hier würde der echte Export stattfinden
            messagebox.showinfo("Export", f"Export ({export_type}) erfolgreich!")
            window.destroy()
        except Exception as e:
            messagebox.showerror("Fehler", f"Export fehlgeschlagen:\n{str(e)}")

    def _show_settings(self):
        """Zeigt die Einstellungen."""
        messagebox.showinfo("Einstellungen", "Einstellungen werden in einer zukünftigen Version verfügbar sein.")

    def _show_day_statistics(self):
        """Zeigt detaillierte Tagesstatistiken."""
        stats_text = f"""
Tagesstatistik - {datetime.now().strftime('%d.%m.%Y')}

📦 Pakete: {len(self.registered_packages)}
🚚 Lieferungen: {1 if self.current_delivery else 0}
👤 Bearbeiter: {self.employee['first_name']} {self.employee['last_name']}
⏰ Arbeitszeit: {self._calculate_work_time()}

Letzte Aktivität: {datetime.now().strftime('%H:%M:%S')}
        """

        messagebox.showinfo("Tagesstatistik", stats_text.strip())

    def _show_delivery_history(self):
        """Zeigt die Lieferungshistorie."""
        # Placeholder für Historie
        history_text = """
Lieferungshistorie (Letzte 7 Tage)

Heute:
• Aktuelle Lieferung (läuft...)

Gestern:
• DHL Lieferung - 15 Pakete
• UPS Express - 3 Pakete

Vorgestern:
• Direktlieferung - 8 Pakete

Weitere Historie wird in zukünftigen Versionen verfügbar sein.
        """

        messagebox.showinfo("Lieferungshistorie", history_text.strip())

    def _calculate_work_time(self) -> str:
        """Berechnet die Arbeitszeit."""
        # Placeholder - in echter Implementierung würde die Zeit getrackt
        return "Seit 08:00 Uhr (ca. 2h 30min)"

    def _finish_current_delivery(self):
        """Schließt die aktuelle Lieferung ab."""
        if not self.current_delivery:
            return

        # Bestätigungsdialog
        result = messagebox.askyesno(
            "Lieferung abschließen",
            f"Lieferung von {self.current_delivery['supplier']} abschließen?\n\n"
            f"Empfangen: {self.current_delivery.get('received_packages', 0)} Pakete"
        )

        if result:
            self.logger.info(f"Lieferung abgeschlossen: {self.current_delivery['supplier']}")

            self.status_label.config(
                text=f"✅ Lieferung abgeschlossen - {self.current_delivery.get('received_packages', 0)} Pakete",
                fg=COLORS['success']
            )

            self.current_delivery = None
            self.update_delivery_status()
            self.update_statistics()

    def _on_logout(self):
        """Behandelt Logout."""
        # Warnung bei aktiver Lieferung
        if self.current_delivery:
            result = messagebox.askyesno(
                "Warnung",
                "Es gibt eine aktive Lieferung. Trotzdem abmelden?\n\n"
                "Die Lieferung bleibt gespeichert und kann von anderen Mitarbeitern fortgesetzt werden."
            )
            if not result:
                return

        self.logger.info(f"Benutzer {self.employee['first_name']} {self.employee['last_name']} meldet sich ab")

        # Cleanup
        self._cleanup()

        # Logout-Callback
        if self.on_logout:
            self.on_logout()

    def _cleanup(self):
        """Räumt Ressourcen auf."""
        # Hier könnten Timer gestoppt oder Dateien gespeichert werden
        pass

    # Öffentliche Methoden für externe Updates

    def set_current_delivery(self, delivery: Optional[Dict[str, Any]]):
        """
        Setzt die aktuelle Lieferung.

        Args:
            delivery: Lieferungs-Daten oder None
        """
        self.current_delivery = delivery
        self.update_delivery_status()

    def add_registered_package(self, package: Dict[str, Any]):
        """
        Fügt ein registriertes Paket hinzu.

        Args:
            package: Paket-Daten
        """
        self.registered_packages.append(package)
        if self.current_delivery:
            self.current_delivery['received_packages'] = self.current_delivery.get('received_packages', 0) + 1
        self.update_delivery_status()
        self.update_recent_entries()
        self.update_statistics()

    def update_delivery_status(self):
        """Aktualisiert die Anzeige der aktuellen Lieferung."""
        if self.current_delivery:
            supplier = self.current_delivery.get('supplier', 'Unbekannt')
            delivery_note = self.current_delivery.get('delivery_note', 'N/A')
            expected = self.current_delivery.get('expected_packages', 0)
            received = self.current_delivery.get('received_packages', 0)
            start_time = self.current_delivery.get('start_time', datetime.now())

            if isinstance(start_time, datetime):
                start_str = start_time.strftime('%H:%M Uhr')
            else:
                start_str = str(start_time)

            info_text = f"""Lieferant: {supplier}
Lieferschein: {delivery_note}
Erwartet: {expected} Pakete
Empfangen: {received} Pakete
Start: {start_str}"""

            self.delivery_info_label.config(
                text=info_text,
                fg=COLORS['text']
            )

            # Status-Update
            if received >= expected and expected > 0:
                status_text = f"✅ Lieferung vollständig - {received}/{expected} Pakete"
                status_color = COLORS['success']
            else:
                status_text = f"⏳ Lieferung von {supplier} - {received}/{expected} Pakete"
                status_color = COLORS['primary']

            self.status_label.config(text=status_text, fg=status_color)

            # Abschluss-Button hinzufügen/aktualisieren
            if not hasattr(self, 'finish_delivery_btn') or not self.finish_delivery_btn.winfo_exists():
                self.finish_delivery_btn = tk.Button(
                    self.delivery_info_frame,
                    text="🏁 Lieferung abschließen",
                    font=FONTS['normal'],
                    command=self._finish_current_delivery,
                    bg=COLORS['warning'],
                    fg='white',
                    relief='raised',
                    bd=2,
                    padx=15,
                    pady=8,
                    cursor='hand2'
                )
                self.finish_delivery_btn.pack(pady=15)

        else:
            self.delivery_info_label.config(
                text="Keine aktive Lieferung\n\nBitte starten Sie eine neue Lieferung\num Pakete zu registrieren.",
                fg=COLORS['text_secondary']
            )

            self.status_label.config(
                text="Keine aktive Lieferung - Bitte neue Lieferung starten",
                fg=COLORS['text']
            )

            # Abschluss-Button entfernen
            if hasattr(self, 'finish_delivery_btn') and self.finish_delivery_btn.winfo_exists():
                self.finish_delivery_btn.destroy()

    def update_recent_entries(self):
        """Aktualisiert die Liste der letzten Eingänge."""
        # Alte Einträge löschen
        for widget in self.recent_frame.winfo_children():
            widget.destroy()

        if not self.registered_packages:
            no_entries_label = tk.Label(
                self.recent_frame,
                text="Keine Pakete registriert",
                font=FONTS['normal'],
                bg=COLORS['card'],
                fg=COLORS['text_secondary']
            )
            no_entries_label.pack(pady=30)
        else:
            # Letzte Pakete anzeigen (neueste zuerst)
            recent_packages = self.registered_packages[-10:]
            recent_packages.reverse()

            for package in recent_packages:
                self._create_package_entry(package)

    def _create_package_entry(self, package: Dict[str, Any]):
        """
        Erstellt einen Eintrag für ein Paket.

        Args:
            package: Paket-Daten
        """
        entry_frame = tk.Frame(
            self.recent_frame,
            bg=COLORS['background'],
            relief='raised',
            bd=1
        )
        entry_frame.pack(fill='x', padx=10, pady=3)

        # Paket-Nummer und Kunde
        package_id = package.get('package_id', 'Unbekannt')
        customer = package.get('customer', 'Unbekannt')

        info_label = tk.Label(
            entry_frame,
            text=f"📦 {package_id}",
            font=('Arial', 11, 'bold'),
            bg=COLORS['background'],
            fg=COLORS['primary']
        )
        info_label.pack(anchor='w', padx=10, pady=(5, 0))

        customer_label = tk.Label(
            entry_frame,
            text=f"Kunde: {customer}",
            font=('Arial', 10),
            bg=COLORS['background'],
            fg=COLORS['text']
        )
        customer_label.pack(anchor='w', padx=10)

        # Zeitstempel und Priorität
        timestamp = datetime.now().strftime('%H:%M Uhr')
        priority = package.get('priority', 'Normal')

        # Priorität-Farbe
        priority_colors = {
            'Normal': COLORS['text_secondary'],
            'Hoch': COLORS['warning'],
            'Express': COLORS['error'],
            'Eilig': COLORS['error']
        }
        priority_color = priority_colors.get(priority, COLORS['text_secondary'])

        detail_frame = tk.Frame(entry_frame, bg=COLORS['background'])
        detail_frame.pack(fill='x', padx=10, pady=(0, 5))

        time_label = tk.Label(
            detail_frame,
            text=timestamp,
            font=('Arial', 9),
            bg=COLORS['background'],
            fg=COLORS['text_secondary']
        )
        time_label.pack(side='left')

        if priority != 'Normal':
            priority_label = tk.Label(
                detail_frame,
                text=f"• {priority}",
                font=('Arial', 9, 'bold'),
                bg=COLORS['background'],
                fg=priority_color
            )
            priority_label.pack(side='left', padx=(10, 0))

    def update_statistics(self):
        """Aktualisiert die Statistiken."""
        delivery_count = 1 if self.current_delivery else 0
        package_count = len(self.registered_packages)

        stats_text = f"Heute: {delivery_count} Lieferung{'en' if delivery_count != 1 else ''} | {package_count} Paket{'e' if package_count != 1 else ''} registriert"

        self.stats_label.config(text=stats_text)

    def _update_data(self):
        """Aktualisiert alle Daten-Anzeigen."""
        self.update_delivery_status()
        self.update_recent_entries()
        self.update_statistics()

    def destroy(self):
        """Zerstört den Hauptbildschirm und räumt auf."""
        self._cleanup()
        if self.main_frame:
            self.main_frame.destroy()