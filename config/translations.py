"""
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
