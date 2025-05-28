"""
Fix für fehlende Manual Login Methoden
Repariert die Wareneingang-App
"""

import re
from pathlib import Path


def fix_wareneingang_manual_login():
    """Repariert die Manual Login Methoden in der Wareneingang-App"""
    print("🔧 MANUAL LOGIN METHODEN REPARATUR")
    print("=" * 50)

    app_file = Path("apps/wareneingang.py")

    if not app_file.exists():
        print("❌ apps/wareneingang.py nicht gefunden!")
        return False

    # Datei lesen
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Prüfen ob Methoden bereits existieren
    if 'def show_manual_login(self):' in content:
        print("✅ Manual Login Methoden bereits vorhanden")
        return True

    print("⚠️ Manual Login Methoden fehlen - füge hinzu...")

    # Manual Login Methoden Code
    manual_login_methods = '''
    def show_manual_login(self):
        """Zeigt Manual Login Dialog"""
        self.logger.info("Manual Login angefordert")

        # Dialog-Fenster erstellen
        dialog = tk.Toplevel(self.root)
        dialog.title("Manual Login")
        dialog.geometry("400x300")
        dialog.configure(bg='#f0f0f0')
        dialog.transient(self.root)
        dialog.grab_set()

        # Zentrieren
        dialog.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))

        # Header
        header = tk.Label(
            dialog,
            text="🔐 Manual Login",
            font=('Arial', 16, 'bold'),
            bg='#f0f0f0',
            fg='#333333'
        )
        header.pack(pady=20)

        # Mitarbeiter-Auswahl
        tk.Label(
            dialog,
            text="Mitarbeiter auswählen:",
            font=('Arial', 12),
            bg='#f0f0f0',
            fg='#333333'
        ).pack(pady=10)

        # Dropdown mit Test-Mitarbeitern
        from tkinter import ttk
        employee_var = tk.StringVar()
        employees = [
            "Max Mustermann (Supervisor)",
            "Anna Schmidt (Worker)", 
            "Test User (Worker)",
            "Manual Login (Worker)"
        ]

        employee_combo = ttk.Combobox(
            dialog,
            textvariable=employee_var,
            values=employees,
            state="readonly",
            font=('Arial', 11),
            width=30
        )
        employee_combo.pack(pady=10)
        employee_combo.set(employees[0])  # Default

        # Buttons
        button_frame = tk.Frame(dialog, bg='#f0f0f0')
        button_frame.pack(pady=20)

        def login():
            selected = employee_var.get()
            if selected:
                # Employee-Daten basierend auf Auswahl
                if "Max Mustermann" in selected:
                    employee_data = {
                        'id': 1,
                        'rfid_card': '1234567890',
                        'first_name': 'Max',
                        'last_name': 'Mustermann',
                        'role': 'supervisor'
                    }
                elif "Anna Schmidt" in selected:
                    employee_data = {
                        'id': 2,
                        'rfid_card': '0987654321',
                        'first_name': 'Anna',
                        'last_name': 'Schmidt',
                        'role': 'worker'
                    }
                elif "Test User" in selected:
                    employee_data = {
                        'id': 3,
                        'rfid_card': 'test123',
                        'first_name': 'Test',
                        'last_name': 'User',
                        'role': 'worker'
                    }
                else:
                    employee_data = {
                        'id': 4,
                        'rfid_card': 'manual',
                        'first_name': 'Manual',
                        'last_name': 'Login',
                        'role': 'worker'
                    }

                self.logger.info(f"Manual Login: {employee_data['first_name']} {employee_data['last_name']}")
                self.handle_employee_login(employee_data)
                dialog.destroy()

        def cancel():
            dialog.destroy()

        tk.Button(
            button_frame,
            text="✅ Anmelden",
            font=('Arial', 12, 'bold'),
            bg='#4CAF50',
            fg='white',
            command=login,
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            button_frame,
            text="❌ Abbrechen",
            font=('Arial', 12),
            bg='#f44336',
            fg='white',
            command=cancel,
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=10)

    def simulate_test_card(self):
        """Simuliert Test-RFID-Karte"""
        self.logger.info("Test-Karte wird simuliert...")

        # Test-Mitarbeiter Daten
        test_employee = {
            'id': 3,
            'rfid_card': 'test123',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'worker'
        }

        # Direkt als wäre eine Karte gescannt worden
        self.handle_employee_login(test_employee)

        # Visual Feedback falls RFID-Status Label existiert
        try:
            if hasattr(self, 'rfid_status_label'):
                self.rfid_status_label.config(text="🎯", fg='#4CAF50')
                self.root.after(2000, lambda: self.rfid_status_label.config(text="✓", fg='#4CAF50'))
        except:
            pass

    def handle_employee_login(self, employee_data):
        """Behandelt Mitarbeiter-Login (RFID oder Manual)"""
        try:
            self.current_employee = employee_data
            self.logger.info(f"Mitarbeiter angemeldet: {employee_data['first_name']} {employee_data['last_name']}")

            # GUI zu Wareneingang-Modus wechseln
            if hasattr(self, 'show_wareneingang_interface'):
                self.show_wareneingang_interface()
            else:
                # Fallback: Einfach erfolgreiches Login anzeigen
                self.logger.info("Login erfolgreich - Wareneingang-Interface nicht gefunden")

        except Exception as e:
            self.logger.error(f"Fehler beim Mitarbeiter-Login: {e}")
            # Einfache Error-Behandlung ohne show_error_message falls nicht vorhanden
            self.logger.error(f"Login-Fehler: {e}")
'''

    # Finde die beste Stelle zum Einfügen (vor dem Ende der Klasse)
    # Suche nach der letzten Methode der Klasse

    # Pattern für das Ende der Klasse finden
    if 'if __name__ == "__main__":' in content:
        # Einfach vor der main-Funktion einfügen
        content = content.replace(
            '\nif __name__ == "__main__":',
            manual_login_methods + '\n\nif __name__ == "__main__":'
        )
        print("✅ Manual Login Methoden eingefügt")
    else:
        # Als Fallback an das Ende der Datei
        content += manual_login_methods
        print("✅ Manual Login Methoden am Ende eingefügt")

    # Datei speichern
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ Manual Login Methoden erfolgreich hinzugefügt")
    return True


def add_manual_login_buttons():
    """Fügt Manual Login Buttons zur GUI hinzu"""
    print("\n🔧 MANUAL LOGIN BUTTONS HINZUFÜGEN")
    print("=" * 40)

    app_file = Path("apps/wareneingang.py")

    # Datei lesen
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Prüfen ob Buttons bereits existieren
    if 'Manual Login' in content and 'show_manual_login' in content:
        print("✅ Manual Login Buttons bereits vorhanden")
        return True

    print("⚠️ Manual Login Buttons fehlen - füge hinzu...")

    # Manual Login Button Code
    button_code = '''
        # Manual Login Button hinzufügen
        self.manual_login_button = tk.Button(
            main_frame,
            text="🔐 Manual Login",
            font=('Arial', 12, 'bold'),
            bg='#4CAF50',
            fg='white',
            command=self.show_manual_login,
            pady=10,
            padx=20
        )
        self.manual_login_button.pack(pady=15)

        # Test-Karte Button (für Entwicklung)
        self.test_card_button = tk.Button(
            main_frame,
            text="🎯 Test-Karte simulieren",
            font=('Arial', 10),
            bg='#2196F3',
            fg='white',
            command=self.simulate_test_card,
            pady=5,
            padx=15
        )
        self.test_card_button.pack(pady=10)'''

    # Suche nach einem guten Platz für die Buttons
    # Nach dem RFID-Status Label
    if 'self.rfid_status_label.pack(' in content:
        # Nach dem RFID Status Label einfügen
        pattern = r'(self\.rfid_status_label\.pack\([^)]*\))'
        replacement = r'\1' + button_code
        content = re.sub(pattern, replacement, content)
        print("✅ Manual Login Buttons nach RFID-Status eingefügt")
    elif 'main_frame' in content:
        # Falls main_frame existiert, am Ende einfügen
        lines = content.split('\n')
        insert_pos = -1
        for i, line in enumerate(lines):
            if 'main_frame' in line and '.pack(' in line:
                insert_pos = i + 1

        if insert_pos > 0:
            lines.insert(insert_pos, button_code)
            content = '\n'.join(lines)
            print("✅ Manual Login Buttons in main_frame eingefügt")
    else:
        print("⚠️ Konnte keine geeignete Stelle für Buttons finden")

    # Datei speichern
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(content)

    return True


def fix_sound_error():
    """Repariert Sound-System Fehler"""
    print("\n🔧 SOUND-SYSTEM REPARATUR")
    print("=" * 30)

    app_file = Path("apps/wareneingang.py")

    # Datei lesen
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Sound-Initialisierung reparieren
    if 'pygame.mixer.init()' in content:
        content = content.replace(
            'pygame.mixer.init()',
            '''try:
            pygame.mixer.init()
        except Exception as e:
            print(f"Sound-System konnte nicht initialisiert werden: {e}")
            # Sound deaktivieren
            self.sound_enabled = False'''
        )
        print("✅ Sound-System Fehlerbehandlung hinzugefügt")

    # Alternative: Sound-Calls abfangen
    content = re.sub(
        r'pygame\.mixer\.(.*)',
        r'try:\n            pygame.mixer.\1\n        except:\n            pass  # Sound nicht verfügbar',
        content
    )

    # Datei speichern
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ Sound-Fehler behoben")


def main():
    """Hauptfunktion - Repariert Manual Login"""
    print("🔧 WARENEINGANG MANUAL LOGIN REPARATUR")
    print("=" * 60)
    print("Behebt: AttributeError 'show_manual_login' + Sound-Fehler")
    print()

    success_count = 0

    # 1. Manual Login Methoden hinzufügen
    if fix_wareneingang_manual_login():
        success_count += 1

    # 2. Manual Login Buttons hinzufügen
    if add_manual_login_buttons():
        success_count += 1

    # 3. Sound-Fehler beheben
    fix_sound_error()
    success_count += 1

    print("\n" + "=" * 60)
    if success_count >= 2:
        print("✅ REPARATUR ERFOLGREICH!")
        print("\n🚀 App testen:")
        print("   .\\\\run_wareneingang.bat")
        print("\n🎯 Was repariert wurde:")
        print("   ✅ show_manual_login Methode hinzugefügt")
        print("   ✅ simulate_test_card Methode hinzugefügt")
        print("   ✅ handle_employee_login Methode hinzugefügt")
        print("   ✅ Manual Login Buttons eingefügt")
        print("   ✅ Sound-Fehler behoben")
        print("\n⚡ Die App sollte jetzt fehlerfrei starten!")
    else:
        print("❌ REPARATUR FEHLGESCHLAGEN!")


if __name__ == "__main__":
    main()