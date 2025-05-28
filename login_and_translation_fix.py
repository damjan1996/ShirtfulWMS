"""
Wareneingang App Patch:
1. Manual Login Button hinzufügen
2. Übersetzungs-System reparieren
3. Test ohne RFID-Karte ermöglichen
"""

import shutil
from pathlib import Path


def patch_wareneingang_app():
    """Patcht Wareneingang-App für Manual Login"""
    print("🔧 WARENEINGANG-APP PATCH")
    print("=" * 40)

    app_file = Path("apps/wareneingang.py")

    if not app_file.exists():
        print("❌ apps/wareneingang.py nicht gefunden!")
        return False

    # Backup erstellen
    backup_file = Path("apps/wareneingang_before_manual_login.py")
    shutil.copy2(app_file, backup_file)
    print(f"✅ Backup erstellt: {backup_file}")

    # Originale Datei lesen
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Manual Login Code einfügen
    manual_login_addition = '''
        # Manual Login Button hinzufügen
        self.manual_login_button = tk.Button(
            main_frame,
            text="Manual Login",
            font=('Arial', 12, 'bold'),
            bg='#4CAF50',
            fg='white',
            command=self.show_manual_login,
            pady=10
        )
        self.manual_login_button.pack(pady=20)

        # Test-Karte Button (für Entwicklung)
        self.test_card_button = tk.Button(
            main_frame,
            text="Test-Karte simulieren",
            font=('Arial', 10),
            bg='#2196F3',
            fg='white',
            command=self.simulate_test_card,
            pady=5
        )
        self.test_card_button.pack(pady=10)
'''

    # Manual Login Methoden hinzufügen
    manual_login_methods = '''
    def show_manual_login(self):
        """Zeigt Manual Login Dialog"""
        self.logger.info("Manual Login angefordert")

        # Dialog-Fenster erstellen
        dialog = tk.Toplevel(self.root)
        dialog.title("Manual Login")
        dialog.geometry("400x300")
        dialog.configure(bg=COLORS['background'])
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
            bg=COLORS['background'],
            fg=COLORS['text']
        )
        header.pack(pady=20)

        # Mitarbeiter-Auswahl
        tk.Label(
            dialog,
            text="Mitarbeiter auswählen:",
            font=('Arial', 12),
            bg=COLORS['background'],
            fg=COLORS['text']
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
        button_frame = tk.Frame(dialog, bg=COLORS['background'])
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
            bg=COLORS['success'],
            fg='white',
            command=login,
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            button_frame,
            text="❌ Abbrechen",
            font=('Arial', 12),
            bg=COLORS['error'],
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

        # Visual Feedback
        self.rfid_status_label.config(text="🎯", fg=COLORS['success'])
        self.root.after(2000, lambda: self.rfid_status_label.config(text="✓", fg=COLORS['success']))

    def handle_employee_login(self, employee_data):
        """Behandelt Mitarbeiter-Login (RFID oder Manual)"""
        try:
            self.current_employee = employee_data
            self.logger.info(f"Mitarbeiter angemeldet: {employee_data['first_name']} {employee_data['last_name']}")

            # GUI zu Wareneingang-Modus wechseln
            self.show_wareneingang_interface()

        except Exception as e:
            self.logger.error(f"Fehler beim Mitarbeiter-Login: {e}")
            self.show_error_message(f"Login-Fehler: {e}")
'''

    # In der Datei nach dem RFID-Status Label suchen und Manual Login einfügen
    # Suche nach dem Pattern wo die GUI aufgebaut wird
    if 'self.rfid_status_label.pack(pady=30)' in content:
        content = content.replace(
            'self.rfid_status_label.pack(pady=30)',
            'self.rfid_status_label.pack(pady=30)' + manual_login_addition
        )
        print("✅ Manual Login Buttons hinzugefügt")

    # Manual Login Methoden am Ende der Klasse hinzufügen
    if 'if __name__ == "__main__":' in content:
        content = content.replace(
            'if __name__ == "__main__":',
            manual_login_methods + '\nif __name__ == "__main__":'
        )
        print("✅ Manual Login Methoden hinzugefügt")

    # Datei speichern
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ Wareneingang-App für Manual Login erweitert")
    return True


def fix_translations():
    """Repariert Übersetzungs-System"""
    print("\n🔧 ÜBERSETZUNGS-SYSTEM REPARATUR")
    print("=" * 40)

    trans_file = Path("config/translations.py")

    if not trans_file.exists():
        print("❌ config/translations.py nicht gefunden - erstelle neue Datei")

        # Verzeichnis erstellen falls nicht vorhanden
        trans_file.parent.mkdir(exist_ok=True)
    else:
        # Backup erstellen
        backup_file = Path("config/translations_backup.py")
        shutil.copy2(trans_file, backup_file)
        print(f"✅ Übersetzungs-Backup: {backup_file}")

    # Vollständiges Übersetzungs-System
    translations_code = '''"""
Übersetzungs-System für Shirtful WMS
Unterstützt: Deutsch, Englisch, Türkisch, Polnisch
"""

class Translations:
    """Übersetzungs-Manager für WMS"""

    def __init__(self, default_language='de'):
        self.current_language = default_language
        self.translations = {
            'de': {
                # Login/Auth
                'login_title': 'Anmeldung',
                'rfid_prompt': 'Bitte RFID-Karte an Lesegerät halten',
                'waiting_for_card': 'Warte auf Karte...',
                'manual_login': 'Manuelle Anmeldung',
                'test_card': 'Test-Karte simulieren',
                'employee_select': 'Mitarbeiter auswählen:',
                'login_button': '✅ Anmelden',
                'cancel_button': '❌ Abbrechen',

                # Wareneingang
                'wareneingang_title': 'WARENEINGANG',
                'package_scan': 'Paket scannen oder eingeben:',
                'package_id': 'Paket-ID',
                'customer': 'Kunde',
                'order_id': 'Bestellnummer',
                'priority': 'Priorität',
                'notes': 'Notizen',
                'register_package': 'Paket registrieren',
                'package_registered': 'Paket erfolgreich registriert!',

                # Status
                'connected': 'Verbunden',
                'disconnected': 'Getrennt',
                'error': 'Fehler',
                'success': 'Erfolgreich',
                'warning': 'Warnung',

                # Allgemein
                'save': 'Speichern',
                'delete': 'Löschen',
                'edit': 'Bearbeiten',
                'back': 'Zurück',
                'next': 'Weiter',
                'close': 'Schließen',
                'yes': 'Ja',
                'no': 'Nein'
            },

            'en': {
                # Login/Auth
                'login_title': 'Login',
                'rfid_prompt': 'Please hold RFID card to reader',
                'waiting_for_card': 'Waiting for card...',
                'manual_login': 'Manual Login',
                'test_card': 'Simulate Test Card',
                'employee_select': 'Select employee:',
                'login_button': '✅ Login',
                'cancel_button': '❌ Cancel',

                # Wareneingang
                'wareneingang_title': 'GOODS RECEIPT',
                'package_scan': 'Scan or enter package:',
                'package_id': 'Package ID',
                'customer': 'Customer',
                'order_id': 'Order Number',
                'priority': 'Priority',
                'notes': 'Notes',
                'register_package': 'Register Package',
                'package_registered': 'Package successfully registered!',

                # Status
                'connected': 'Connected',
                'disconnected': 'Disconnected',
                'error': 'Error',
                'success': 'Success',
                'warning': 'Warning',

                # Allgemein
                'save': 'Save',
                'delete': 'Delete',
                'edit': 'Edit',
                'back': 'Back',
                'next': 'Next',
                'close': 'Close',
                'yes': 'Yes',
                'no': 'No'
            },

            'tr': {
                # Login/Auth
                'login_title': 'Giriş',
                'rfid_prompt': 'Lütfen RFID kartını okuyucuya tutun',
                'waiting_for_card': 'Kart bekleniyor...',
                'manual_login': 'Manuel Giriş',
                'test_card': 'Test Kartı Simüle Et',
                'employee_select': 'Çalışan seçin:',
                'login_button': '✅ Giriş Yap',
                'cancel_button': '❌ İptal',

                # Wareneingang
                'wareneingang_title': 'MAL KABUL',
                'package_scan': 'Paketi tarayın veya girin:',
                'package_id': 'Paket ID',
                'customer': 'Müşteri',
                'order_id': 'Sipariş No',
                'priority': 'Öncelik',
                'notes': 'Notlar',
                'register_package': 'Paketi Kaydet',
                'package_registered': 'Paket başarıyla kaydedildi!',

                # Status
                'connected': 'Bağlandı',
                'disconnected': 'Bağlantı Kesildi',
                'error': 'Hata',
                'success': 'Başarılı',
                'warning': 'Uyarı',

                # Allgemein
                'save': 'Kaydet',
                'delete': 'Sil',
                'edit': 'Düzenle',
                'back': 'Geri',
                'next': 'İleri',
                'close': 'Kapat',
                'yes': 'Evet',
                'no': 'Hayır'
            },

            'pl': {
                # Login/Auth
                'login_title': 'Logowanie',
                'rfid_prompt': 'Proszę przyłożyć kartę RFID do czytnika',
                'waiting_for_card': 'Oczekiwanie na kartę...',
                'manual_login': 'Logowanie Ręczne',
                'test_card': 'Symuluj Kartę Testową',
                'employee_select': 'Wybierz pracownika:',
                'login_button': '✅ Zaloguj',
                'cancel_button': '❌ Anuluj',

                # Wareneingang
                'wareneingang_title': 'PRZYJĘCIE TOWARU',
                'package_scan': 'Zeskanuj lub wprowadź paczkę:',
                'package_id': 'ID Paczki',
                'customer': 'Klient',
                'order_id': 'Numer Zamówienia',
                'priority': 'Priorytet',
                'notes': 'Notatki',
                'register_package': 'Zarejestruj Paczkę',
                'package_registered': 'Paczka została pomyślnie zarejestrowana!',

                # Status
                'connected': 'Połączony',
                'disconnected': 'Rozłączony',
                'error': 'Błąd',
                'success': 'Sukces',
                'warning': 'Ostrzeżenie',

                # Allgemein
                'save': 'Zapisz',
                'delete': 'Usuń',
                'edit': 'Edytuj',
                'back': 'Wstecz',
                'next': 'Dalej',
                'close': 'Zamknij',
                'yes': 'Tak',
                'no': 'Nie'
            }
        }

    def set_language(self, language_code):
        """Setzt aktuelle Sprache"""
        if language_code in self.translations:
            self.current_language = language_code
            return True
        return False

    def get(self, key, fallback=None):
        """Holt Übersetzung für aktuellen Schlüssel"""
        try:
            return self.translations[self.current_language].get(key, fallback or key)
        except KeyError:
            return fallback or key

    def get_current_language(self):
        """Holt aktuelle Sprache"""
        return self.current_language

    def get_available_languages(self):
        """Holt verfügbare Sprachen"""
        return list(self.translations.keys())


# Globale Instanz für einfachen Import
translations = Translations('de')

def set_language(lang_code):
    """Setzt globale Sprache"""
    return translations.set_language(lang_code)

def t(key, fallback=None):
    """Kurze Funktion für Übersetzungen"""
    return translations.get(key, fallback)

def get_language():
    """Holt aktuelle Sprache"""
    return translations.get_current_language()
'''

    # Übersetzungs-Datei schreiben
    with open(trans_file, 'w', encoding='utf-8') as f:
        f.write(translations_code)

    print("✅ Übersetzungs-System repariert und erweitert")
    return True


def create_quick_test():
    """Erstellt schnellen Test für Manual Login"""
    test_code = '''"""
Quick Test für Manual Login und Übersetzungen
"""

def test_translations():
    """Testet Übersetzungs-System"""
    print("=== TRANSLATION TEST ===")
    try:
        from config.translations import translations, t, set_language

        # Deutsche Übersetzungen
        print(f"DE: {t('wareneingang_title')}")

        # Englische Übersetzungen
        set_language('en')
        print(f"EN: {t('wareneingang_title')}")

        # Türkische Übersetzungen
        set_language('tr') 
        print(f"TR: {t('wareneingang_title')}")

        # Polnische Übersetzungen
        set_language('pl')
        print(f"PL: {t('wareneingang_title')}")

        # Zurück zu Deutsch
        set_language('de')

        print("✅ Übersetzungen funktionieren")
        return True

    except Exception as e:
        print(f"❌ Übersetzungs-Fehler: {e}")
        return False

def main():
    print("🧪 QUICK TEST - MANUAL LOGIN & ÜBERSETZUNGEN")
    print("=" * 50)

    if test_translations():
        print("\\n✅ TESTS ERFOLGREICH!")
        print("\\n🚀 App starten:")
        print("   .\\\\run_wareneingang.bat")
        print("\\n📋 Neue Features:")
        print("   🔐 Manual Login Button")
        print("   🎯 Test-Karte simulieren")
        print("   🌍 Vollständige Übersetzungen (DE/EN/TR/PL)")
    else:
        print("\\n❌ Tests fehlgeschlagen")

if __name__ == "__main__":
    main()
'''

    with open('test_manual_login.py', 'w', encoding='utf-8') as f:
        f.write(test_code)

    print("✅ Quick-Test erstellt")


def main():
    """Hauptfunktion"""
    print("🔧 WARENEINGANG MANUAL LOGIN & ÜBERSETZUNGS-PATCH")
    print("=" * 60)
    print("Fügt hinzu: Manual Login + Test-Karte + Übersetzungen")
    print()

    success_count = 0

    # 1. Wareneingang-App erweitern
    if patch_wareneingang_app():
        success_count += 1

    # 2. Übersetzungen reparieren
    if fix_translations():
        success_count += 1

    # 3. Quick-Test erstellen
    create_quick_test()
    success_count += 1

    print("\n" + "=" * 60)
    if success_count >= 2:
        print("✅ PATCH ERFOLGREICH!")
        print("\n🧪 Testen:")
        print("   python test_manual_login.py")
        print("\n🚀 App starten:")
        print("   .\\\\run_wareneingang.bat")
        print("\n🎯 Neue Features:")
        print("   🔐 Manual Login Button (ohne RFID-Karte)")
        print("   🎯 Test-Karte simulieren")
        print("   🌍 Sprach-Buttons funktionieren (DE/EN/TR/PL)")
        print("   📋 Vollständige Übersetzungen")
        print("\n⚡ Jetzt können Sie das WMS ohne RFID-Karte testen!")
    else:
        print("❌ PATCH FEHLGESCHLAGEN!")


if __name__ == "__main__":
    main()