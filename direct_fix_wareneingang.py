"""
Direkte Reparatur der wareneingang.py
Analysiert die aktuelle Datei und fügt Manual Login korrekt ein
"""

import re
import shutil
from pathlib import Path


def analyze_wareneingang_structure():
    """Analysiert die Struktur der wareneingang.py"""
    print("🔍 WARENEINGANG.PY STRUKTUR ANALYSE")
    print("=" * 50)

    app_file = Path("apps/wareneingang.py")

    if not app_file.exists():
        print("❌ apps/wareneingang.py nicht gefunden!")
        return None

    with open(app_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Analysiere die Datei
    info = {
        'total_lines': len(lines),
        'class_found': False,
        'class_start': -1,
        'setup_login_screen_found': False,
        'setup_login_screen_line': -1,
        'methods': [],
        'last_method_line': -1,
        'main_function_line': -1
    }

    # Durchsuche Zeilen
    for i, line in enumerate(lines):
        stripped = line.strip()

        # Klassenstart finden
        if stripped.startswith('class WareneingangApp'):
            info['class_found'] = True
            info['class_start'] = i
            print(f"✅ WareneingangApp Klasse gefunden: Zeile {i + 1}")

        # setup_login_screen finden
        if 'def setup_login_screen(' in stripped:
            info['setup_login_screen_found'] = True
            info['setup_login_screen_line'] = i
            print(f"✅ setup_login_screen gefunden: Zeile {i + 1}")

        # Methoden finden
        if stripped.startswith('def ') and 'self' in stripped:
            method_name = stripped.split('(')[0].replace('def ', '')
            info['methods'].append((method_name, i))
            info['last_method_line'] = i

        # main Funktion finden
        if stripped.startswith('def main('):
            info['main_function_line'] = i
            print(f"✅ main() Funktion gefunden: Zeile {i + 1}")

    print(f"📊 Struktur-Info:")
    print(f"   📄 Gesamt Zeilen: {info['total_lines']}")
    print(f"   🎯 Klasse gefunden: {info['class_found']}")
    print(f"   📝 Methoden gefunden: {len(info['methods'])}")
    print(f"   🔧 Letzte Methode: Zeile {info['last_method_line'] + 1}")

    # Prüfe ob Manual Login bereits existiert
    existing_methods = [name for name, line in info['methods']]
    manual_login_exists = 'show_manual_login' in existing_methods

    print(f"\n🔍 Manual Login Status:")
    print(f"   show_manual_login: {'✅ Vorhanden' if manual_login_exists else '❌ Fehlt'}")
    print(f"   simulate_test_card: {'✅ Vorhanden' if 'simulate_test_card' in existing_methods else '❌ Fehlt'}")
    print(f"   handle_employee_login: {'✅ Vorhanden' if 'handle_employee_login' in existing_methods else '❌ Fehlt'}")

    return info, lines


def create_manual_login_methods():
    """Erstellt die Manual Login Methoden"""
    return '''
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

    def handle_employee_login(self, employee_data):
        """Behandelt Mitarbeiter-Login (RFID oder Manual)"""
        try:
            self.current_employee = employee_data
            self.logger.info(f"Mitarbeiter angemeldet: {employee_data['first_name']} {employee_data['last_name']}")

            # Einfach Login-Screen verstecken und Success anzeigen
            self.clear_screen()
            self.show_success_screen(employee_data)

        except Exception as e:
            self.logger.error(f"Fehler beim Mitarbeiter-Login: {e}")

    def show_success_screen(self, employee_data):
        """Zeigt Erfolgs-Screen nach Login"""
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=50)

        # Success Header
        tk.Label(
            main_frame,
            text="✅ LOGIN ERFOLGREICH",
            font=('Arial', 24, 'bold'),
            bg='#f0f0f0',
            fg='#4CAF50'
        ).pack(pady=30)

        # Mitarbeiter Info
        tk.Label(
            main_frame,
            text=f"Willkommen, {employee_data['first_name']} {employee_data['last_name']}!",
            font=('Arial', 16),
            bg='#f0f0f0',
            fg='#333333'
        ).pack(pady=20)

        tk.Label(
            main_frame,
            text=f"Rolle: {employee_data['role']}",
            font=('Arial', 12),
            bg='#f0f0f0',
            fg='#666666'
        ).pack(pady=10)

        # Info Box
        info_frame = tk.Frame(main_frame, bg='#e8f5e8', relief=tk.RIDGE, bd=2)
        info_frame.pack(pady=30, padx=20, fill=tk.X)

        tk.Label(
            info_frame,
            text="🎉 WMS Manual Login funktioniert!",
            font=('Arial', 14, 'bold'),
            bg='#e8f5e8',
            fg='#2e7d32'
        ).pack(pady=15)

        tk.Label(
            info_frame,
            text="Das RFID-System wurde erfolgreich umgangen.\\nSie können jetzt das WMS ohne echte RFID-Karte nutzen.",
            font=('Arial', 11),
            bg='#e8f5e8',
            fg='#2e7d32',
            justify=tk.CENTER
        ).pack(pady=10)

        # Zurück Button
        tk.Button(
            main_frame,
            text="🔄 Zurück zum Login",
            font=('Arial', 12),
            bg='#2196F3',
            fg='white',
            command=self.setup_login_screen,
            padx=20,
            pady=10
        ).pack(pady=30)

    def clear_screen(self):
        """Leert den Bildschirm"""
        for widget in self.root.winfo_children():
            widget.destroy()
'''


def insert_manual_login_methods(lines, info):
    """Fügt Manual Login Methoden in die richtige Position ein"""
    print("\n🔧 MANUAL LOGIN METHODEN EINFÜGEN")
    print("=" * 40)

    # Finde die beste Position (vor main() Funktion oder am Ende der Klasse)
    insert_position = info['main_function_line'] if info['main_function_line'] > 0 else len(lines)

    print(f"📍 Einfügeposition: Zeile {insert_position + 1}")

    # Manual Login Methoden erstellen
    methods_code = create_manual_login_methods()
    method_lines = methods_code.split('\n')

    # An der richtigen Position einfügen
    for i, method_line in enumerate(reversed(method_lines)):
        lines.insert(insert_position, method_line + '\n')

    print("✅ Manual Login Methoden eingefügt")
    return lines


def add_manual_login_buttons_to_setup(lines):
    """Fügt Manual Login Buttons zur setup_login_screen Methode hinzu"""
    print("\n🔧 MANUAL LOGIN BUTTONS HINZUFÜGEN")
    print("=" * 40)

    # Finde setup_login_screen Methode
    setup_start = -1
    setup_end = -1

    for i, line in enumerate(lines):
        if 'def setup_login_screen(' in line:
            setup_start = i
        elif setup_start > 0 and line.strip().startswith('def ') and setup_start != i:
            setup_end = i
            break

    if setup_start < 0:
        print("❌ setup_login_screen Methode nicht gefunden")
        return lines

    if setup_end < 0:
        setup_end = len(lines)

    print(f"📍 setup_login_screen: Zeilen {setup_start + 1} bis {setup_end}")

    # Suche nach einem geeigneten Platz für die Buttons
    # Am Ende der Methode, vor der nächsten Methode
    insert_pos = setup_end - 1

    # Gehe rückwärts durch die Methode und finde das Ende
    for i in range(setup_end - 1, setup_start, -1):
        line = lines[i].strip()
        if line and not line.startswith('#') and not line.startswith('"""'):
            insert_pos = i + 1
            break

    # Button Code
    button_code = '''
        # Manual Login Button hinzufügen
        manual_button = tk.Button(
            main_frame,
            text="🔐 Manual Login",
            font=('Arial', 12, 'bold'),
            bg='#4CAF50',
            fg='white',
            command=self.show_manual_login,
            pady=10,
            padx=20
        )
        manual_button.pack(pady=15)

        # Test-Karte Button 
        test_button = tk.Button(
            main_frame,
            text="🎯 Test-Karte simulieren",
            font=('Arial', 10),
            bg='#2196F3',
            fg='white',
            command=self.simulate_test_card,
            pady=5,
            padx=15
        )
        test_button.pack(pady=10)
'''

    # Button Code einfügen
    button_lines = button_code.split('\n')
    for i, button_line in enumerate(reversed(button_lines)):
        lines.insert(insert_pos, button_line + '\n')

    print(f"✅ Manual Login Buttons eingefügt an Position {insert_pos + 1}")
    return lines


def fix_wareneingang_complete():
    """Komplette Reparatur der wareneingang.py"""
    print("🔧 WARENEINGANG.PY KOMPLETTE REPARATUR")
    print("=" * 60)

    # 1. Analysiere aktuelle Struktur
    result = analyze_wareneingang_structure()
    if not result:
        return False

    info, lines = result

    # 2. Backup erstellen
    app_file = Path("apps/wareneingang.py")
    backup_file = Path("apps/wareneingang_before_manual_fix.py")
    shutil.copy2(app_file, backup_file)
    print(f"✅ Backup erstellt: {backup_file}")

    # 3. Prüfe ob Manual Login bereits existiert
    existing_methods = [name for name, line in info['methods']]
    if 'show_manual_login' in existing_methods:
        print("✅ Manual Login Methoden bereits vorhanden")
        return True

    # 4. Manual Login Methoden einfügen
    lines = insert_manual_login_methods(lines, info)

    # 5. Manual Login Buttons hinzufügen
    lines = add_manual_login_buttons_to_setup(lines)

    # 6. Datei speichern
    with open(app_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print("\n✅ WARENEINGANG.PY ERFOLGREICH REPARIERT!")
    return True


def main():
    """Hauptfunktion"""
    print("🔧 WARENEINGANG.PY DIREKTE REPARATUR")
    print("=" * 60)
    print("Behebt: AttributeError 'show_manual_login' definitiv")
    print()

    if fix_wareneingang_complete():
        print("\n🎉 REPARATUR ABGESCHLOSSEN!")
        print("\n🚀 App testen:")
        print("   .\\\\run_wareneingang.bat")
        print("\n🎯 Was hinzugefügt wurde:")
        print("   ✅ show_manual_login() Methode")
        print("   ✅ simulate_test_card() Methode")
        print("   ✅ handle_employee_login() Methode")
        print("   ✅ show_success_screen() Methode")
        print("   ✅ clear_screen() Methode")
        print("   ✅ Manual Login Buttons in GUI")
        print("\n⚡ AttributeError sollte behoben sein!")
    else:
        print("\n❌ REPARATUR FEHLGESCHLAGEN!")


if __name__ == "__main__":
    main()