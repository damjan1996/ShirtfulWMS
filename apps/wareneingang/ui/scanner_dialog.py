#!/usr/bin/env python3
"""
Shirtful WMS - Scanner Dialog
Dialog für QR-Code und Barcode-Scanning
"""

import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from typing import Callable, Optional, Dict, Any, List
import random
import string
import sys
import os

# Projekt-Root zum Python-Path hinzufügen
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from utils.ui_components import COLORS, FONTS
from utils.qr_scanner import QRScanner
from utils.logger import setup_logger
from config.translations import Translations


class ScannerDialog:
    """Dialog für QR-Code und Barcode-Scanning."""

    def __init__(self, parent: tk.Tk, on_code_scanned: Callable[[str], None]):
        """
        Initialisiert den Scanner-Dialog.

        Args:
            parent: Eltern-Fenster
            on_code_scanned: Callback-Funktion für gescannte Codes
        """
        self.parent = parent
        self.on_code_scanned = on_code_scanned
        self.logger = setup_logger('scanner_dialog')

        # Komponenten
        self.qr_scanner = QRScanner()
        self.translations = Translations()

        # Dialog-Status
        self.window = None
        self.is_scanning = False
        self.scan_job_id = None
        self.camera_active = False

        # UI-Elemente
        self.camera_frame = None
        self.status_label = None
        self.scan_count_label = None
        self.last_scanned_label = None
        self.scan_button = None
        self.manual_entry = None

        # Scanner-Status
        self.scanned_codes = []
        self.last_scan_time = None
        self.scan_count = 0

        # Test-Codes für Simulation
        self.test_codes = [
            "PKG-2024-123456",
            "PKG-2024-789012",
            "PKG-2024-345678",
            "PKG-2024-901234",
            "PKG-2024-567890"
        ]

    def show(self):
        """Zeigt den Scanner-Dialog."""
        self._create_dialog()
        self._setup_ui()

        # Modal anzeigen
        self.window.transient(self.parent)
        self.window.grab_set()
        self.window.focus_set()

        # Zentrieren
        self._center_dialog()

        # Scanning starten
        self._start_scanning()

    def _create_dialog(self):
        """Erstellt das Dialog-Fenster."""
        self.window = tk.Toplevel(self.parent)
        self.window.title("QR-Code Scanner")
        self.window.geometry("900x700")
        self.window.configure(bg=COLORS['background'])
        self.window.resizable(True, True)

        # Dialog-Schließung behandeln
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)

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

        # Hauptbereich
        self._create_main_area()

        # Kamera-Bereich
        self._create_camera_area()

        # Steuerung
        self._create_controls()

        # Status und Historie
        self._create_status_area()

        # Buttons
        self._create_buttons()

    def _create_header(self):
        """Erstellt den Header-Bereich."""
        header_frame = tk.Frame(self.window, bg=COLORS['primary'], height=70)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        # Titel mit Animation
        title_label = tk.Label(
            header_frame,
            text="📷 QR-Code Scanner",
            font=FONTS['large'],
            bg=COLORS['primary'],
            fg='white'
        )
        title_label.pack(side='left', padx=20, pady=20)

        # Scan-Modus Indikator
        self.mode_label = tk.Label(
            header_frame,
            text="🔍 Bereit zum Scannen",
            font=('Arial', 12),
            bg=COLORS['primary'],
            fg='white'
        )
        self.mode_label.pack(side='right', padx=20, pady=20)

    def _create_main_area(self):
        """Erstellt den Hauptbereich."""
        # Hauptcontainer
        main_frame = tk.Frame(self.window, bg=COLORS['background'])
        main_frame.pack(expand=True, fill='both', padx=20, pady=10)

        # Oberer Bereich (Kamera + Steuerung)
        self.upper_frame = tk.Frame(main_frame, bg=COLORS['background'])
        self.upper_frame.pack(fill='both', expand=True, pady=(0, 10))

        # Unterer Bereich (Status + Buttons)
        self.lower_frame = tk.Frame(main_frame, bg=COLORS['background'])
        self.lower_frame.pack(fill='x', pady=(10, 0))

    def _create_camera_area(self):
        """Erstellt den Kamera-Bereich."""
        # Linke Seite - Kamera
        camera_container = tk.Frame(self.upper_frame, bg=COLORS['background'])
        camera_container.pack(side='left', expand=True, fill='both', padx=(0, 10))

        # Kamera-Titel
        camera_title = tk.Label(
            camera_container,
            text="📹 Kamera-Vorschau",
            font=FONTS['normal'],
            bg=COLORS['background'],
            fg=COLORS['text']
        )
        camera_title.pack(pady=(0, 10))

        # Kamera-Frame
        self.camera_frame = tk.Frame(
            camera_container,
            bg='black',
            relief='raised',
            bd=2
        )
        self.camera_frame.pack(expand=True, fill='both')

        # Kamera-Placeholder
        self.camera_placeholder = tk.Label(
            self.camera_frame,
            text="📷\n\nKamera wird initialisiert...\n\nHalten Sie den QR-Code\nvor die Kamera",
            font=('Arial', 14),
            bg='black',
            fg='white',
            justify='center'
        )
        self.camera_placeholder.pack(expand=True)

        # Scan-Overlay (wird bei erfolgreichem Scan angezeigt)
        self.scan_overlay = tk.Label(
            self.camera_frame,
            text="",
            font=('Arial', 20, 'bold'),
            bg='black',
            fg='lime'
        )

    def _create_controls(self):
        """Erstellt die Steuerungs-Elemente."""
        # Rechte Seite - Steuerung
        control_container = tk.Frame(self.upper_frame, bg=COLORS['background'])
        control_container.pack(side='right', fill='y', padx=(10, 0))

        # Steuerungs-Titel
        control_title = tk.Label(
            control_container,
            text="⚙️ Steuerung",
            font=FONTS['normal'],
            bg=COLORS['background'],
            fg=COLORS['text']
        )
        control_title.pack(pady=(0, 15))

        # Steuerungs-Frame
        controls_frame = tk.Frame(control_container, bg=COLORS['card'], relief='raised', bd=2)
        controls_frame.pack(fill='both', expand=True, padx=10)

        content_frame = tk.Frame(controls_frame, bg=COLORS['card'])
        content_frame.pack(fill='both', padx=20, pady=20)

        # Scan-Status
        self.status_label = tk.Label(
            content_frame,
            text="🔍 Warte auf QR-Code...",
            font=('Arial', 12, 'bold'),
            bg=COLORS['card'],
            fg=COLORS['primary'],
            wraplength=200
        )
        self.status_label.pack(pady=(0, 20))

        # Manueller Scan-Button
        self.scan_button = tk.Button(
            content_frame,
            text="🎯 Test-Scan",
            font=FONTS['normal'],
            command=self._simulate_scan,
            bg=COLORS['primary'],
            fg='white',
            relief='raised',
            bd=2,
            padx=15,
            pady=10,
            cursor='hand2'
        )
        self.scan_button.pack(fill='x', pady=(0, 15))

        # Neuen QR-Code generieren
        generate_btn = tk.Button(
            content_frame,
            text="🔄 Neuen QR generieren",
            font=FONTS['normal'],
            command=self._generate_new_qr,
            bg=COLORS['success'],
            fg='white',
            relief='raised',
            bd=2,
            padx=15,
            pady=10,
            cursor='hand2'
        )
        generate_btn.pack(fill='x', pady=(0, 15))

        # Manuelle Eingabe
        manual_label = tk.Label(
            content_frame,
            text="Manuelle QR-Eingabe:",
            font=('Arial', 10),
            bg=COLORS['card'],
            fg=COLORS['text']
        )
        manual_label.pack(anchor='w', pady=(10, 5))

        self.manual_entry = tk.Entry(
            content_frame,
            font=('Arial', 10),
            width=25
        )
        self.manual_entry.pack(fill='x')

        # Enter-Taste für manuelle Eingabe
        self.manual_entry.bind('<Return>', self._on_manual_enter)

        manual_btn = tk.Button(
            content_frame,
            text="✓ Eingeben",
            font=('Arial', 9),
            command=self._process_manual_entry,
            bg=COLORS['warning'],
            fg='white',
            relief='raised',
            bd=1,
            pady=5,
            cursor='hand2'
        )
        manual_btn.pack(fill='x', pady=(5, 0))

        # Separator
        tk.Frame(content_frame, height=2, bg=COLORS['text_secondary']).pack(fill='x', pady=20)

        # Scan-Einstellungen
        settings_label = tk.Label(
            content_frame,
            text="📋 Einstellungen:",
            font=('Arial', 11, 'bold'),
            bg=COLORS['card'],
            fg=COLORS['text']
        )
        settings_label.pack(anchor='w', pady=(0, 10))

        # Auto-Scan Checkbox
        self.auto_scan_var = tk.BooleanVar(value=True)
        auto_scan_cb = tk.Checkbutton(
            content_frame,
            text="Auto-Scan aktiviert",
            variable=self.auto_scan_var,
            font=('Arial', 9),
            bg=COLORS['card'],
            command=self._toggle_auto_scan
        )
        auto_scan_cb.pack(anchor='w')

        # Beep bei Scan
        self.beep_var = tk.BooleanVar(value=True)
        beep_cb = tk.Checkbutton(
            content_frame,
            text="Beep bei Scan",
            variable=self.beep_var,
            font=('Arial', 9),
            bg=COLORS['card']
        )
        beep_cb.pack(anchor='w')

    def _create_status_area(self):
        """Erstellt den Status-Bereich."""
        # Status-Container
        status_container = tk.Frame(self.lower_frame, bg=COLORS['background'])
        status_container.pack(fill='x', pady=(0, 10))

        # Linke Seite - Scan-Statistiken
        stats_frame = tk.Frame(status_container, bg=COLORS['card'], relief='raised', bd=2)
        stats_frame.pack(side='left', expand=True, fill='x', padx=(0, 10))

        stats_title = tk.Label(
            stats_frame,
            text="📊 Scan-Statistiken",
            font=('Arial', 11, 'bold'),
            bg=COLORS['card'],
            fg=COLORS['text']
        )
        stats_title.pack(pady=(10, 5))

        # Scan-Anzahl
        self.scan_count_label = tk.Label(
            stats_frame,
            text="Gescannt: 0 Codes",
            font=('Arial', 10),
            bg=COLORS['card'],
            fg=COLORS['text']
        )
        self.scan_count_label.pack(pady=2)

        # Letzter Scan
        self.last_scanned_label = tk.Label(
            stats_frame,
            text="Letzter Scan: --",
            font=('Arial', 9),
            bg=COLORS['card'],
            fg=COLORS['text_secondary']
        )
        self.last_scanned_label.pack(pady=(2, 10))

        # Rechte Seite - Scan-Historie
        history_frame = tk.Frame(status_container, bg=COLORS['card'], relief='raised', bd=2)
        history_frame.pack(side='right', expand=True, fill='x', padx=(10, 0))

        history_title = tk.Label(
            history_frame,
            text="📋 Letzte Scans",
            font=('Arial', 11, 'bold'),
            bg=COLORS['card'],
            fg=COLORS['text']
        )
        history_title.pack(pady=(10, 5))

        # Scrollbare Historie
        self.history_text = tk.Text(
            history_frame,
            height=4,
            font=('Arial', 9),
            bg=COLORS['card'],
            fg=COLORS['text'],
            state='disabled',
            wrap='word'
        )
        self.history_text.pack(fill='x', padx=10, pady=(0, 10))

    def _create_buttons(self):
        """Erstellt die Aktions-Buttons."""
        # Button-Container
        button_frame = tk.Frame(self.lower_frame, bg=COLORS['background'])
        button_frame.pack(fill='x')

        # Button-Layout
        button_container = tk.Frame(button_frame, bg=COLORS['background'])
        button_container.pack()

        # Pause/Resume Button
        self.pause_btn = tk.Button(
            button_container,
            text="⏸️ Pausieren",
            font=FONTS['normal'],
            command=self._toggle_scanning,
            bg=COLORS['warning'],
            fg='white',
            relief='raised',
            bd=2,
            padx=20,
            pady=10,
            cursor='hand2'
        )
        self.pause_btn.pack(side='left', padx=10)

        # Export-Button
        export_btn = tk.Button(
            button_container,
            text="📄 Export",
            font=FONTS['normal'],
            command=self._export_scan_history,
            bg=COLORS['info'],
            fg='white',
            relief='raised',
            bd=2,
            padx=20,
            pady=10,
            cursor='hand2'
        )
        export_btn.pack(side='left', padx=10)

        # Löschen-Button
        clear_btn = tk.Button(
            button_container,
            text="🗑️ Historie löschen",
            font=FONTS['normal'],
            command=self._clear_history,
            bg=COLORS['secondary'],
            fg='white',
            relief='raised',
            bd=2,
            padx=20,
            pady=10,
            cursor='hand2'
        )
        clear_btn.pack(side='left', padx=10)

        # Schließen-Button
        close_btn = tk.Button(
            button_container,
            text="✅ Fertig",
            font=FONTS['normal'],
            command=self._on_close,
            bg=COLORS['success'],
            fg='white',
            relief='raised',
            bd=2,
            padx=25,
            pady=10,
            cursor='hand2'
        )
        close_btn.pack(side='left', padx=15)

    def _start_scanning(self):
        """Startet den Scan-Prozess."""
        if self.is_scanning:
            return

        self.is_scanning = True
        self.logger.info("Scanner gestartet")

        # UI-Update
        self.status_label.config(text="🔍 Scanning aktiv...", fg=COLORS['success'])
        self.mode_label.config(text="🟢 Scanning aktiv")
        self.pause_btn.config(text="⏸️ Pausieren", bg=COLORS['warning'])

        # Kamera-Simulation
        self._simulate_camera_activity()

        # Scan-Loop starten (falls Auto-Scan aktiviert)
        if self.auto_scan_var.get():
            self._scan_loop()

    def _stop_scanning(self):
        """Stoppt den Scan-Prozess."""
        self.is_scanning = False

        if self.scan_job_id:
            self.window.after_cancel(self.scan_job_id)
            self.scan_job_id = None

        self.logger.info("Scanner gestoppt")

        # UI-Update
        self.status_label.config(text="⏸️ Scanning pausiert", fg=COLORS['warning'])
        self.mode_label.config(text="🟡 Pausiert")
        self.pause_btn.config(text="▶️ Fortsetzen", bg=COLORS['success'])

    def _toggle_scanning(self):
        """Wechselt zwischen Scanning und Pause."""
        if self.is_scanning:
            self._stop_scanning()
        else:
            self._start_scanning()

    def _scan_loop(self):
        """Haupt-Scan-Schleife."""
        if not self.is_scanning or not self.auto_scan_var.get():
            return

        try:
            # Simuliere echten QR-Scanner
            # In echter Implementierung: code = self.qr_scanner.scan_from_webcam()
            code = None

            # Gelegentlich simulierte Scans für Demo
            if random.randint(1, 100) <= 2:  # 2% Chance pro Schleife
                code = self._get_random_test_code()

            if code:
                self._process_scanned_code(code)

        except Exception as e:
            self.logger.error(f"Fehler beim Scannen: {e}")

        # Nächste Iteration planen
        if self.is_scanning and self.auto_scan_var.get():
            self.scan_job_id = self.window.after(500, self._scan_loop)

    def _simulate_camera_activity(self):
        """Simuliert Kamera-Aktivität."""
        if not self.camera_active:
            self.camera_active = True
            self.camera_placeholder.config(
                text="📹\n\nKamera AKTIV\n\nHalten Sie QR-Code\nvor die Kamera\n\n🔍 Scanning...",
                fg='lime'
            )

    def _simulate_scan(self):
        """Simuliert einen QR-Code Scan."""
        if not self.is_scanning:
            self._start_scanning()

        code = self._get_random_test_code()
        self._process_scanned_code(code, is_simulated=True)

    def _get_random_test_code(self) -> str:
        """
        Gibt einen zufälligen Test-QR-Code zurück.

        Returns:
            str: Test-QR-Code
        """
        # Gelegentlich neue Codes generieren
        if random.randint(1, 10) <= 3:
            return self._generate_random_code()
        else:
            return random.choice(self.test_codes)

    def _generate_random_code(self) -> str:
        """
        Generiert einen neuen zufälligen QR-Code.

        Returns:
            str: Neuer QR-Code
        """
        year = datetime.now().year
        random_part = ''.join(random.choices(string.digits, k=6))
        return f"PKG-{year}-{random_part}"

    def _generate_new_qr(self):
        """Generiert einen neuen QR-Code und simuliert Scan."""
        new_code = self._generate_random_code()
        self.manual_entry.delete(0, tk.END)
        self.manual_entry.insert(0, new_code)

        # Visual Feedback
        self.status_label.config(text="🆕 Neuer QR-Code generiert", fg=COLORS['primary'])

        # Nach kurzer Pause verarbeiten
        self.window.after(1000, lambda: self._process_scanned_code(new_code, is_simulated=True))

    def _process_manual_entry(self):
        """Verarbeitet manuelle QR-Code Eingabe."""
        code = self.manual_entry.get().strip()
        if not code:
            messagebox.showwarning("Warnung", "Bitte geben Sie einen QR-Code ein.")
            return

        self._process_scanned_code(code, is_manual=True)
        self.manual_entry.delete(0, tk.END)

    def _on_manual_enter(self, event):
        """Behandelt Enter-Taste in manueller Eingabe."""
        self._process_manual_entry()

    def _process_scanned_code(self, code: str, is_simulated: bool = False, is_manual: bool = False):
        """
        Verarbeitet einen gescannten QR-Code.

        Args:
            code: Gescannter Code
            is_simulated: True wenn simuliert
            is_manual: True wenn manuell eingegeben
        """
        self.logger.info(f"Code gescannt: {code} (simuliert: {is_simulated}, manuell: {is_manual})")

        # Duplikat-Prüfung
        if code in self.scanned_codes:
            self._show_duplicate_warning(code)
            return

        # Code zur Historie hinzufügen
        self.scanned_codes.append(code)
        self.scan_count += 1
        self.last_scan_time = datetime.now()

        # Visual Feedback
        self._show_scan_success(code, is_simulated, is_manual)

        # Beep (falls aktiviert)
        if self.beep_var.get():
            self._play_beep()

        # UI aktualisieren
        self._update_scan_statistics()
        self._add_to_history(code, is_simulated, is_manual)

        # Callback aufrufen
        try:
            if self.on_code_scanned:
                self.on_code_scanned(code)
        except Exception as e:
            self.logger.error(f"Fehler beim Callback: {e}")
            messagebox.showerror("Fehler", f"Fehler bei der Verarbeitung:\n{str(e)}")

    def _show_scan_success(self, code: str, is_simulated: bool, is_manual: bool):
        """
        Zeigt Scan-Erfolg visuell an.

        Args:
            code: Gescannter Code
            is_simulated: True wenn simuliert
            is_manual: True wenn manuell
        """
        # Status-Update
        source = "Simuliert" if is_simulated else ("Manuell" if is_manual else "Kamera")
        self.status_label.config(
            text=f"✅ Code gescannt!\n{source}",
            fg=COLORS['success']
        )

        # Kamera-Overlay
        if hasattr(self, 'scan_overlay'):
            self.scan_overlay.config(text=f"✅ SCAN OK\n{code[:15]}...")
            self.scan_overlay.place(relx=0.5, rely=0.5, anchor='center')

            # Overlay nach 2 Sekunden ausblenden
            self.window.after(2000, lambda: self.scan_overlay.place_forget())

        # Nach 3 Sekunden Status zurücksetzen
        self.window.after(3000, self._reset_status)

    def _reset_status(self):
        """Setzt den Status zurück."""
        if self.is_scanning:
            self.status_label.config(text="🔍 Warte auf QR-Code...", fg=COLORS['primary'])
        else:
            self.status_label.config(text="⏸️ Scanning pausiert", fg=COLORS['warning'])

    def _show_duplicate_warning(self, code: str):
        """
        Zeigt Warnung bei doppeltem Code.

        Args:
            code: Doppelter Code
        """
        self.status_label.config(text=f"⚠️ Code bereits gescannt!\n{code[:15]}...", fg=COLORS['error'])

        # Sound für Fehler (anders als Erfolg)
        if self.beep_var.get():
            self._play_error_beep()

        # Warnung anzeigen
        messagebox.showwarning(
            "Duplikat erkannt",
            f"QR-Code wurde bereits gescannt:\n{code}\n\nBitte verwenden Sie einen neuen Code."
        )

        # Status nach 3 Sekunden zurücksetzen
        self.window.after(3000, self._reset_status)

    def _play_beep(self):
        """Spielt Erfolgs-Beep ab."""
        try:
            # Windows
            import winsound
            winsound.Beep(1000, 200)  # 1000 Hz, 200ms
        except:
            # Fallback für andere Systeme
            print('\a')  # System beep

    def _play_error_beep(self):
        """Spielt Fehler-Beep ab."""
        try:
            # Windows
            import winsound
            winsound.Beep(500, 300)  # 500 Hz, 300ms (tiefer, länger)
        except:
            # Fallback
            print('\a\a')  # Doppelter system beep

    def _update_scan_statistics(self):
        """Aktualisiert die Scan-Statistiken."""
        self.scan_count_label.config(text=f"Gescannt: {self.scan_count} Codes")

        if self.last_scan_time:
            time_str = self.last_scan_time.strftime('%H:%M:%S')
            self.last_scanned_label.config(text=f"Letzter Scan: {time_str}")

    def _add_to_history(self, code: str, is_simulated: bool, is_manual: bool):
        """
        Fügt Code zur Scan-Historie hinzu.

        Args:
            code: Gescannter Code
            is_simulated: True wenn simuliert
            is_manual: True wenn manuell
        """
        # Historie-Text erstellen
        timestamp = datetime.now().strftime('%H:%M:%S')
        source = "SIM" if is_simulated else ("MAN" if is_manual else "CAM")
        entry = f"{timestamp} [{source}] {code}\n"

        # Text hinzufügen
        self.history_text.config(state='normal')
        self.history_text.insert('1.0', entry)  # Am Anfang einfügen

        # Auf maximal 10 Zeilen begrenzen
        lines = self.history_text.get('1.0', 'end').split('\n')
        if len(lines) > 11:  # 10 + 1 leere Zeile
            self.history_text.delete('11.0', 'end')

        self.history_text.config(state='disabled')

    def _toggle_auto_scan(self):
        """Wechselt Auto-Scan Ein/Aus."""
        if self.auto_scan_var.get() and self.is_scanning:
            # Auto-Scan aktiviert und Scanner läuft -> Loop starten
            self._scan_loop()
        elif not self.auto_scan_var.get():
            # Auto-Scan deaktiviert -> Loop stoppen
            if self.scan_job_id:
                self.window.after_cancel(self.scan_job_id)
                self.scan_job_id = None

    def _export_scan_history(self):
        """Exportiert die Scan-Historie."""
        if not self.scanned_codes:
            messagebox.showinfo("Export", "Keine Scan-Daten zum Exportieren vorhanden.")
            return

        try:
            # CSV-Inhalt erstellen
            csv_content = "Zeitstempel,QR-Code,Quelle\n"

            # Aktuelle Zeit für Export verwenden (vereinfacht)
            base_time = datetime.now()

            for i, code in enumerate(reversed(self.scanned_codes)):
                # Simuliere verschiedene Zeitstempel
                scan_time = base_time.replace(minute=base_time.minute - i)
                timestamp = scan_time.strftime('%Y-%m-%d %H:%M:%S')
                source = "Scanner"
                csv_content += f"{timestamp},{code},{source}\n"

            # Export-Dialog (vereinfacht)
            export_info = f"""
Scan-Historie Export

Anzahl Codes: {len(self.scanned_codes)}
Export-Format: CSV
Zeitraum: {datetime.now().strftime('%d.%m.%Y %H:%M')}

CSV-Vorschau:
{csv_content[:200]}...
            """

            messagebox.showinfo("Export erfolgreich", export_info.strip())

        except Exception as e:
            self.logger.error(f"Fehler beim Export: {e}")
            messagebox.showerror("Export-Fehler", f"Export fehlgeschlagen:\n{str(e)}")

    def _clear_history(self):
        """Löscht die Scan-Historie."""
        if not self.scanned_codes:
            messagebox.showinfo("Historie", "Keine Historie zum Löschen vorhanden.")
            return

        result = messagebox.askyesno(
            "Historie löschen",
            f"Möchten Sie wirklich alle {len(self.scanned_codes)} gescannten Codes löschen?\n\n"
            "Diese Aktion kann nicht rückgängig gemacht werden."
        )

        if result:
            # Historie löschen
            self.scanned_codes.clear()
            self.scan_count = 0
            self.last_scan_time = None

            # UI zurücksetzen
            self.scan_count_label.config(text="Gescannt: 0 Codes")
            self.last_scanned_label.config(text="Letzter Scan: --")

            self.history_text.config(state='normal')
            self.history_text.delete('1.0', 'end')
            self.history_text.config(state='disabled')

            self.logger.info("Scan-Historie geleert")
            messagebox.showinfo("Historie", "Scan-Historie wurde geleert.")

    def _on_close(self):
        """Behandelt das Schließen des Dialogs."""
        # Scanning stoppen
        self._stop_scanning()

        # Kamera stoppen (falls aktiv)
        self.camera_active = False

        # Zusammenfassung anzeigen (falls Codes gescannt wurden)
        if self.scanned_codes:
            summary = f"""
Scanner-Sitzung beendet

Gescannte Codes: {len(self.scanned_codes)}
Letzte Aktivität: {self.last_scan_time.strftime('%H:%M:%S') if self.last_scan_time else 'Keine'}

Möchten Sie den Scanner wirklich schließen?
            """

            result = messagebox.askyesno("Scanner schließen", summary.strip())
            if not result:
                # Nicht schließen, Scanning wieder aufnehmen
                if self.scanned_codes:  # Nur wenn bereits gescannt wurde
                    self._start_scanning()
                return

        self.logger.info(f"Scanner geschlossen. {len(self.scanned_codes)} Codes gescannt.")
        self.window.destroy()

    def destroy(self):
        """Zerstört den Dialog und räumt auf."""
        self._stop_scanning()
        if self.window:
            self.window.destroy()