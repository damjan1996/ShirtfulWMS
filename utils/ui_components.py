"""
UI-Komponenten für Shirtful WMS
Gemeinsame UI-Elemente und Styling für alle Anwendungen.
"""

import tkinter as tk
from tkinter import ttk
import pygame
import os
from typing import Optional, Dict, Tuple
import logging
from pathlib import Path

# Farbschema
COLORS = {
    'primary': '#2196F3',  # Blau
    'secondary': '#FFC107',  # Amber
    'success': '#4CAF50',  # Grün
    'error': '#F44336',  # Rot
    'warning': '#FF9800',  # Orange
    'info': '#00BCD4',  # Cyan
    'background': '#F5F5F5',  # Hellgrau
    'card': '#FFFFFF',  # Weiß
    'text': '#212121',  # Dunkelgrau
    'text_secondary': '#757575'  # Mittelgrau
}

# Schriftarten
FONTS = {
    'title': ('Arial', 36, 'bold'),
    'large': ('Arial', 24, 'bold'),
    'normal': ('Arial', 16),
    'small': ('Arial', 12),
    'button': ('Arial', 18, 'bold')
}

# Icons (Unicode)
ICONS = {
    'package': '📦',
    'scan': '📷',
    'check': '✓',
    'cross': '✗',
    'warning': '⚠',
    'info': 'ℹ',
    'user': '👤',
    'clock': '🕐',
    'truck': '🚚',
    'print': '🖨️',
    'settings': '⚙️',
    'logout': '🚪',
    'edit': '✏️',
    'delete': '🗑️',
    'search': '🔍',
    'refresh': '🔄',
    'lock': '🔓',
    'quality': '🔍',
    'process': '🎨',
    'fabric': '🧵'
}


class UIComponents:
    """Klasse für wiederverwendbare UI-Komponenten."""

    def __init__(self):
        """Initialisiert UI-Komponenten."""
        self.logger = logging.getLogger(__name__)
        self._init_sounds()

    def _init_sounds(self):
        """Initialisiert Sound-System."""
        try:
            pygame.mixer.init()
            self.sounds_enabled = True
            self.sounds = {}

            # Sound-Dateien laden
            sound_dir = Path(__file__).parent.parent / 'resources' / 'sounds'
            sound_files = {
                'success': 'success.wav',
                'error': 'error.wav',
                'scan': 'scan.wav',
                'warning': 'warning.wav'
            }

            for name, filename in sound_files.items():
                filepath = sound_dir / filename
                if filepath.exists():
                    self.sounds[name] = pygame.mixer.Sound(str(filepath))
                else:
                    self.logger.warning(f"Sound-Datei nicht gefunden: {filepath}")

        except Exception as e:
            self.logger.warning(f"Sound-System konnte nicht initialisiert werden: {e}")
            self.sounds_enabled = False

    def play_sound(self, sound_name: str):
        """
        Spielt einen Sound ab.

        Args:
            sound_name: Name des Sounds
        """
        if not self.sounds_enabled:
            return

        try:
            if sound_name in self.sounds:
                self.sounds[sound_name].play()
            else:
                # Fallback: System-Beep
                self.root.bell()
        except:
            pass

    @staticmethod
    def create_large_button(parent, text: str, command,
                            color: str = COLORS['primary'],
                            icon: str = None) -> tk.Button:
        """
        Erstellt einen großen, touch-freundlichen Button.

        Args:
            parent: Eltern-Widget
            text: Button-Text
            command: Callback-Funktion
            color: Hintergrundfarbe
            icon: Optional Icon

        Returns:
            Button-Widget
        """
        if icon:
            text = f"{icon} {text}"

        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=FONTS['button'],
            bg=color,
            fg='white',
            activebackground=color,
            activeforeground='white',
            relief='raised',
            bd=2,
            padx=30,
            pady=15,
            cursor='hand2'
        )

        # Hover-Effekt
        def on_enter(e):
            btn['bg'] = _darken_color(color)

        def on_leave(e):
            btn['bg'] = color

        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)

        return btn

    @staticmethod
    def create_info_card(parent, title: str, content: str,
                         icon: str = None) -> tk.Frame:
        """
        Erstellt eine Info-Karte.

        Args:
            parent: Eltern-Widget
            title: Titel der Karte
            content: Inhalt
            icon: Optional Icon

        Returns:
            Frame-Widget
        """
        card = tk.Frame(
            parent,
            bg=COLORS['card'],
            relief='raised',
            bd=1
        )

        # Header
        header = tk.Frame(card, bg=COLORS['primary'])
        header.pack(fill='x')

        title_text = f"{icon} {title}" if icon else title
        title_label = tk.Label(
            header,
            text=title_text,
            font=FONTS['normal'],
            bg=COLORS['primary'],
            fg='white',
            pady=10,
            padx=15
        )
        title_label.pack(anchor='w')

        # Content
        content_label = tk.Label(
            card,
            text=content,
            font=FONTS['normal'],
            bg=COLORS['card'],
            fg=COLORS['text'],
            justify='left',
            pady=15,
            padx=15
        )
        content_label.pack(anchor='w')

        return card

    @staticmethod
    def create_status_indicator(parent, status: str) -> tk.Label:
        """
        Erstellt einen Status-Indikator.

        Args:
            parent: Eltern-Widget
            status: Status-Text

        Returns:
            Label-Widget
        """
        # Status-Farben
        status_colors = {
            'online': COLORS['success'],
            'offline': COLORS['error'],
            'warning': COLORS['warning'],
            'busy': COLORS['secondary'],
            'ready': COLORS['success'],
            'error': COLORS['error']
        }

        # Farbe bestimmen
        color = COLORS['info']
        for key, col in status_colors.items():
            if key.lower() in status.lower():
                color = col
                break

        indicator = tk.Label(
            parent,
            text=f"● {status}",
            font=FONTS['normal'],
            bg=parent['bg'],
            fg=color
        )

        return indicator

    @staticmethod
    def create_data_table(parent, columns: list, data: list) -> ttk.Treeview:
        """
        Erstellt eine Datentabelle.

        Args:
            parent: Eltern-Widget
            columns: Liste von Spaltennamen
            data: Liste von Datenzeilen

        Returns:
            Treeview-Widget
        """
        # Treeview erstellen
        tree = ttk.Treeview(
            parent,
            columns=columns,
            show='headings',
            height=10
        )

        # Spalten konfigurieren
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, minwidth=100)

        # Daten einfügen
        for row in data:
            tree.insert('', 'end', values=row)

        # Scrollbar
        scrollbar = ttk.Scrollbar(parent, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        # Style
        style = ttk.Style()
        style.configure('Treeview', font=FONTS['normal'], rowheight=30)
        style.configure('Treeview.Heading', font=FONTS['normal'])

        return tree

    @staticmethod
    def create_input_dialog(parent, title: str, fields: Dict[str, str]) -> Optional[Dict[str, str]]:
        """
        Erstellt einen Eingabe-Dialog.

        Args:
            parent: Eltern-Widget
            title: Dialog-Titel
            fields: Dictionary mit Feldnamen und Standardwerten

        Returns:
            Dictionary mit eingegebenen Werten oder None
        """
        dialog = tk.Toplevel(parent)
        dialog.title(title)
        dialog.geometry("400x300")
        dialog.transient(parent)
        dialog.grab_set()

        # Zentrieren
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        # Eingabefelder
        entries = {}
        for i, (field, default) in enumerate(fields.items()):
            label = tk.Label(
                dialog,
                text=field + ":",
                font=FONTS['normal']
            )
            label.grid(row=i, column=0, padx=10, pady=10, sticky='e')

            entry = tk.Entry(
                dialog,
                font=FONTS['normal'],
                width=25
            )
            entry.insert(0, default)
            entry.grid(row=i, column=1, padx=10, pady=10)

            entries[field] = entry

        # Buttons
        result = {'ok': False, 'values': {}}

        def on_ok():
            result['ok'] = True
            for field, entry in entries.items():
                result['values'][field] = entry.get()
            dialog.destroy()

        def on_cancel():
            dialog.destroy()

        button_frame = tk.Frame(dialog)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=20)

        ok_btn = tk.Button(
            button_frame,
            text="OK",
            command=on_ok,
            font=FONTS['normal'],
            bg=COLORS['success'],
            fg='white',
            width=10
        )
        ok_btn.pack(side='left', padx=5)

        cancel_btn = tk.Button(
            button_frame,
            text="Abbrechen",
            command=on_cancel,
            font=FONTS['normal'],
            bg=COLORS['error'],
            fg='white',
            width=10
        )
        cancel_btn.pack(side='left', padx=5)

        # Enter-Taste bindet OK
        dialog.bind('<Return>', lambda e: on_ok())

        # Warten bis Dialog geschlossen
        dialog.wait_window()

        return result['values'] if result['ok'] else None

    @staticmethod
    def create_progress_dialog(parent, title: str, message: str) -> Tuple[tk.Toplevel, ttk.Progressbar]:
        """
        Erstellt einen Fortschritts-Dialog.

        Args:
            parent: Eltern-Widget
            title: Dialog-Titel
            message: Nachricht

        Returns:
            Tuple von (Dialog, Progressbar)
        """
        dialog = tk.Toplevel(parent)
        dialog.title(title)
        dialog.geometry("400x150")
        dialog.transient(parent)
        dialog.grab_set()

        # Nicht schließbar
        dialog.protocol("WM_DELETE_WINDOW", lambda: None)

        # Nachricht
        msg_label = tk.Label(
            dialog,
            text=message,
            font=FONTS['normal']
        )
        msg_label.pack(pady=20)

        # Fortschrittsbalken
        progress = ttk.Progressbar(
            dialog,
            mode='indeterminate',
            length=300
        )
        progress.pack(pady=10)
        progress.start(10)

        # Zentrieren
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        return dialog, progress

    @staticmethod
    def create_notification(parent, message: str, type: str = 'info', duration: int = 3000):
        """
        Zeigt eine temporäre Benachrichtigung.

        Args:
            parent: Eltern-Widget
            message: Nachricht
            type: 'info', 'success', 'warning', 'error'
            duration: Anzeigedauer in Millisekunden
        """
        # Farben je nach Typ
        colors = {
            'info': COLORS['info'],
            'success': COLORS['success'],
            'warning': COLORS['warning'],
            'error': COLORS['error']
        }

        color = colors.get(type, COLORS['info'])

        # Notification Frame
        notif = tk.Frame(
            parent,
            bg=color,
            relief='raised',
            bd=2
        )

        # Icon
        icons = {
            'info': ICONS['info'],
            'success': ICONS['check'],
            'warning': ICONS['warning'],
            'error': ICONS['cross']
        }

        icon = icons.get(type, '')

        # Label
        label = tk.Label(
            notif,
            text=f"{icon} {message}",
            font=FONTS['normal'],
            bg=color,
            fg='white',
            padx=20,
            pady=10
        )
        label.pack()

        # Positionieren
        notif.place(relx=0.5, rely=0.1, anchor='n')

        # Nach Duration ausblenden
        def hide():
            notif.destroy()

        parent.after(duration, hide)

        # Fade-in Effekt (optional)
        notif.lift()


def _darken_color(hex_color: str, factor: float = 0.8) -> str:
    """
    Macht eine Farbe dunkler.

    Args:
        hex_color: Farbe als Hex-String
        factor: Verdunkelungsfaktor (0-1)

    Returns:
        Dunklere Farbe als Hex-String
    """
    # Hex zu RGB
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

    # Verdunkeln
    r = int(r * factor)
    g = int(g * factor)
    b = int(b * factor)

    # Zurück zu Hex
    return f'#{r:02x}{g:02x}{b:02x}'


# Test
if __name__ == "__main__":
    # Test-Fenster
    root = tk.Tk()
    root.title("UI Components Test")
    root.geometry("800x600")
    root.configure(bg=COLORS['background'])

    ui = UIComponents()

    # Test-Buttons
    btn1 = UIComponents.create_large_button(
        root, "Test Button", lambda: print("Click!"),
        COLORS['primary'], ICONS['package']
    )
    btn1.pack(pady=10)

    # Test-Card
    card = UIComponents.create_info_card(
        root, "Test Card", "Dies ist eine Test-Karte", ICONS['info']
    )
    card.pack(pady=10, padx=20, fill='x')

    # Test-Status
    status = UIComponents.create_status_indicator(root, "System Ready")
    status.pack(pady=10)


    # Test-Notification
    def show_notif():
        UIComponents.create_notification(root, "Test Notification", 'success')
        ui.play_sound('success')


    btn2 = tk.Button(root, text="Show Notification", command=show_notif)
    btn2.pack(pady=10)

    root.mainloop()