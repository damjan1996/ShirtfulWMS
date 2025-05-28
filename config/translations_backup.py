"""
Übersetzungen für Shirtful WMS
Mehrsprachige Texte für alle Anwendungen.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional, Any, List


class Translations:
    """Klasse für mehrsprachige Übersetzungen."""

    def __init__(self, default_language: str = 'de'):
        """
        Initialisiert das Übersetzungssystem.

        Args:
            default_language: Standard-Sprache
        """
        self.logger = logging.getLogger(__name__)
        self.default_language = default_language
        self.current_language = default_language
        self.translations = self._load_translations()

    def _load_translations(self) -> Dict[str, Dict[str, str]]:
        """
        Lädt alle Übersetzungen.

        Returns:
            Dictionary mit allen Übersetzungen
        """
        return {
            # === Deutsch ===
            'de': {
                # Allgemein
                'app_title': 'Shirtful Lagerverwaltung',
                'welcome': 'Willkommen',
                'goodbye': 'Auf Wiedersehen',
                'yes': 'Ja',
                'no': 'Nein',
                'ok': 'OK',
                'cancel': 'Abbrechen',
                'save': 'Speichern',
                'delete': 'Löschen',
                'edit': 'Bearbeiten',
                'search': 'Suchen',
                'refresh': 'Aktualisieren',
                'back': 'Zurück',
                'next': 'Weiter',
                'finish': 'Fertig',
                'close': 'Schließen',
                'error': 'Fehler',
                'warning': 'Warnung',
                'info': 'Information',
                'success': 'Erfolg',
                'loading': 'Laden...',
                'please_wait': 'Bitte warten...',

                # Login
                'login': 'Anmelden',
                'logout': 'Abmelden',
                'rfid_instruction': 'Bitte RFID-Karte an Lesegerät halten',
                'waiting_for_card': 'Warte auf Karte...',
                'login_successful': 'Anmeldung erfolgreich',
                'login_failed': 'Anmeldung fehlgeschlagen',
                'unknown_card': 'Unbekannte Karte!',
                'user_inactive': 'Benutzer inaktiv',

                # Navigation
                'main_menu': 'Hauptmenü',
                'wareneingang': 'Wareneingang',
                'veredelung': 'Veredelung',
                'betuchung': 'Betuchung',
                'qualitaetskontrolle': 'Qualitätskontrolle',
                'warenausgang': 'Warenausgang',

                # Pakete
                'package': 'Paket',
                'packages': 'Pakete',
                'scan_package': 'Paket scannen',
                'package_details': 'Paketdetails',
                'package_id': 'Paket-ID',
                'order_id': 'Bestellnummer',
                'customer': 'Kunde',
                'item_count': 'Artikelanzahl',
                'priority': 'Priorität',
                'status': 'Status',
                'notes': 'Notizen',
                'last_update': 'Letzte Aktualisierung',

                # Status
                'status_received': 'Wareneingang',
                'status_processing': 'In Veredelung',
                'status_fabric': 'In Betuchung',
                'status_quality': 'Qualitätskontrolle',
                'status_ok': 'Qualität OK',
                'status_rework': 'Nacharbeit erforderlich',
                'status_ready': 'Versandbereit',
                'status_shipped': 'Versendet',

                # Aktionen
                'new_delivery': 'Neue Lieferung',
                'register_package': 'Paket registrieren',
                'start_processing': 'Veredelung starten',
                'start_fabric': 'Betuchung starten',
                'quality_check': 'Qualität prüfen',
                'mark_shipped': 'Als versendet markieren',
                'print_label': 'Label drucken',

                # Lieferungen
                'delivery': 'Lieferung',
                'deliveries': 'Lieferungen',
                'supplier': 'Lieferant',
                'delivery_note': 'Lieferschein-Nr.',
                'expected_packages': 'Erwartete Pakete',
                'received_packages': 'Empfangene Pakete',
                'delivery_complete': 'Lieferung abgeschlossen',

                # Veredelung
                'processing_type': 'Veredelungsart',
                'estimated_duration': 'Geschätzte Dauer',
                'start_time': 'Startzeit',
                'end_time': 'Endzeit',
                'in_progress': 'In Bearbeitung',

                # Qualitätskontrolle
                'quality_ok': 'Qualität OK',
                'quality_failed': 'Nacharbeit erforderlich',
                'error_type': 'Fehlerart',
                'error_description': 'Fehlerbeschreibung',
                'quality_errors': 'Qualitätsfehler',

                # Versand
                'shipping': 'Versand',
                'shipping_method': 'Versandart',
                'tracking_number': 'Tracking-Nummer',
                'ready_to_ship': 'Versandbereit',
                'ship_packages': 'Pakete versenden',
                'packages_shipped': 'Pakete versendet',

                # Statistiken
                'statistics': 'Statistiken',
                'today': 'Heute',
                'this_week': 'Diese Woche',
                'this_month': 'Dieser Monat',
                'packages_processed': 'Pakete bearbeitet',
                'average_time': 'Durchschnittliche Zeit',
                'efficiency': 'Effizienz',

                # Mitarbeiter
                'employee': 'Mitarbeiter',
                'employees': 'Mitarbeiter',
                'clock_in': 'Einstempeln',
                'clock_out': 'Ausstempeln',
                'break': 'Pause',
                'working_time': 'Arbeitszeit',

                # Fehler
                'error_general': 'Ein Fehler ist aufgetreten',
                'error_connection': 'Verbindungsfehler',
                'error_database': 'Datenbankfehler',
                'error_rfid': 'RFID-Lesefehler',
                'error_scanner': 'Scanner-Fehler',
                'error_validation': 'Validierungsfehler',
                'error_permission': 'Keine Berechtigung',

                # Bestätigungen
                'confirm_delete': 'Wirklich löschen?',
                'confirm_logout': 'Wirklich abmelden?',
                'confirm_cancel': 'Änderungen verwerfen?',
                'confirm_action': 'Aktion bestätigen?',

                # Meldungen
                'msg_saved': 'Erfolgreich gespeichert',
                'msg_deleted': 'Erfolgreich gelöscht',
                'msg_updated': 'Erfolgreich aktualisiert',
                'msg_sent': 'Erfolgreich gesendet',
                'msg_printed': 'Erfolgreich gedruckt',
                'msg_no_data': 'Keine Daten vorhanden',
                'msg_loading': 'Daten werden geladen...',
                'msg_please_select': 'Bitte auswählen',
                'msg_required_field': 'Pflichtfeld',

                # Zeit
                'minutes': 'Minuten',
                'hours': 'Stunden',
                'days': 'Tage',
                'time': 'Zeit',
                'date': 'Datum',
                'from': 'Von',
                'to': 'Bis',
                'duration': 'Dauer',

                # Prioritäten
                'priority_low': 'Niedrig',
                'priority_normal': 'Normal',
                'priority_high': 'Hoch',
                'priority_express': 'Express',
                'priority_urgent': 'Dringend',
            },

            # === English ===
            'en': {
                # General
                'app_title': 'Shirtful Warehouse Management',
                'welcome': 'Welcome',
                'goodbye': 'Goodbye',
                'yes': 'Yes',
                'no': 'No',
                'ok': 'OK',
                'cancel': 'Cancel',
                'save': 'Save',
                'delete': 'Delete',
                'edit': 'Edit',
                'search': 'Search',
                'refresh': 'Refresh',
                'back': 'Back',
                'next': 'Next',
                'finish': 'Finish',
                'close': 'Close',
                'error': 'Error',
                'warning': 'Warning',
                'info': 'Information',
                'success': 'Success',
                'loading': 'Loading...',
                'please_wait': 'Please wait...',

                # Login
                'login': 'Login',
                'logout': 'Logout',
                'rfid_instruction': 'Please hold RFID card to reader',
                'waiting_for_card': 'Waiting for card...',
                'login_successful': 'Login successful',
                'login_failed': 'Login failed',
                'unknown_card': 'Unknown card!',
                'user_inactive': 'User inactive',

                # Navigation
                'main_menu': 'Main Menu',
                'wareneingang': 'Goods Receipt',
                'veredelung': 'Processing',
                'betuchung': 'Fabric',
                'qualitaetskontrolle': 'Quality Control',
                'warenausgang': 'Goods Issue',

                # Packages
                'package': 'Package',
                'packages': 'Packages',
                'scan_package': 'Scan package',
                'package_details': 'Package details',
                'package_id': 'Package ID',
                'order_id': 'Order ID',
                'customer': 'Customer',
                'item_count': 'Item count',
                'priority': 'Priority',
                'status': 'Status',
                'notes': 'Notes',
                'last_update': 'Last update',

                # Status
                'status_received': 'Goods receipt',
                'status_processing': 'In processing',
                'status_fabric': 'In fabric',
                'status_quality': 'Quality control',
                'status_ok': 'Quality OK',
                'status_rework': 'Rework needed',
                'status_ready': 'Ready to ship',
                'status_shipped': 'Shipped',

                # Actions
                'new_delivery': 'New delivery',
                'register_package': 'Register package',
                'start_processing': 'Start processing',
                'start_fabric': 'Start fabric',
                'quality_check': 'Check quality',
                'mark_shipped': 'Mark as shipped',
                'print_label': 'Print label',

                # Deliveries
                'delivery': 'Delivery',
                'deliveries': 'Deliveries',
                'supplier': 'Supplier',
                'delivery_note': 'Delivery note no.',
                'expected_packages': 'Expected packages',
                'received_packages': 'Received packages',
                'delivery_complete': 'Delivery complete',

                # Processing
                'processing_type': 'Processing type',
                'estimated_duration': 'Estimated duration',
                'start_time': 'Start time',
                'end_time': 'End time',
                'in_progress': 'In progress',

                # Quality control
                'quality_ok': 'Quality OK',
                'quality_failed': 'Rework needed',
                'error_type': 'Error type',
                'error_description': 'Error description',
                'quality_errors': 'Quality errors',

                # Shipping
                'shipping': 'Shipping',
                'shipping_method': 'Shipping method',
                'tracking_number': 'Tracking number',
                'ready_to_ship': 'Ready to ship',
                'ship_packages': 'Ship packages',
                'packages_shipped': 'Packages shipped',

                # Statistics
                'statistics': 'Statistics',
                'today': 'Today',
                'this_week': 'This week',
                'this_month': 'This month',
                'packages_processed': 'Packages processed',
                'average_time': 'Average time',
                'efficiency': 'Efficiency',

                # Employees
                'employee': 'Employee',
                'employees': 'Employees',
                'clock_in': 'Clock in',
                'clock_out': 'Clock out',
                'break': 'Break',
                'working_time': 'Working time',

                # Errors
                'error_general': 'An error occurred',
                'error_connection': 'Connection error',
                'error_database': 'Database error',
                'error_rfid': 'RFID read error',
                'error_scanner': 'Scanner error',
                'error_validation': 'Validation error',
                'error_permission': 'No permission',

                # Confirmations
                'confirm_delete': 'Really delete?',
                'confirm_logout': 'Really logout?',
                'confirm_cancel': 'Discard changes?',
                'confirm_action': 'Confirm action?',

                # Messages
                'msg_saved': 'Successfully saved',
                'msg_deleted': 'Successfully deleted',
                'msg_updated': 'Successfully updated',
                'msg_sent': 'Successfully sent',
                'msg_printed': 'Successfully printed',
                'msg_no_data': 'No data available',
                'msg_loading': 'Loading data...',
                'msg_please_select': 'Please select',
                'msg_required_field': 'Required field',

                # Time
                'minutes': 'minutes',
                'hours': 'hours',
                'days': 'days',
                'time': 'Time',
                'date': 'Date',
                'from': 'From',
                'to': 'To',
                'duration': 'Duration',

                # Priorities
                'priority_low': 'Low',
                'priority_normal': 'Normal',
                'priority_high': 'High',
                'priority_express': 'Express',
                'priority_urgent': 'Urgent',
            },

            # === Türkçe ===
            'tr': {
                # Genel
                'app_title': 'Shirtful Depo Yönetimi',
                'welcome': 'Hoş geldiniz',
                'goodbye': 'Güle güle',
                'yes': 'Evet',
                'no': 'Hayır',
                'ok': 'Tamam',
                'cancel': 'İptal',
                'save': 'Kaydet',
                'delete': 'Sil',
                'edit': 'Düzenle',
                'search': 'Ara',
                'refresh': 'Yenile',
                'back': 'Geri',
                'next': 'İleri',
                'finish': 'Bitir',
                'close': 'Kapat',
                'error': 'Hata',
                'warning': 'Uyarı',
                'info': 'Bilgi',
                'success': 'Başarılı',
                'loading': 'Yükleniyor...',
                'please_wait': 'Lütfen bekleyin...',

                # Giriş
                'login': 'Giriş',
                'logout': 'Çıkış',
                'rfid_instruction': 'Lütfen RFID kartınızı okutun',
                'waiting_for_card': 'Kart bekleniyor...',
                'login_successful': 'Giriş başarılı',
                'login_failed': 'Giriş başarısız',
                'unknown_card': 'Bilinmeyen kart!',
                'user_inactive': 'Kullanıcı aktif değil',

                # Navigasyon
                'main_menu': 'Ana Menü',
                'wareneingang': 'Mal Girişi',
                'veredelung': 'İşleme',
                'betuchung': 'Kumaş',
                'qualitaetskontrolle': 'Kalite Kontrol',
                'warenausgang': 'Mal Çıkışı',

                # Paketler
                'package': 'Paket',
                'packages': 'Paketler',
                'scan_package': 'Paketi tara',
                'package_details': 'Paket detayları',
                'package_id': 'Paket No',
                'order_id': 'Sipariş No',
                'customer': 'Müşteri',
                'item_count': 'Ürün sayısı',
                'priority': 'Öncelik',
                'status': 'Durum',
                'notes': 'Notlar',
                'last_update': 'Son güncelleme',

                # Durum
                'status_received': 'Mal girişi',
                'status_processing': 'İşlemde',
                'status_fabric': 'Kumaşta',
                'status_quality': 'Kalite kontrolde',
                'status_ok': 'Kalite OK',
                'status_rework': 'Düzeltme gerekli',
                'status_ready': 'Gönderime hazır',
                'status_shipped': 'Gönderildi',

                # İşlemler
                'new_delivery': 'Yeni teslimat',
                'register_package': 'Paketi kaydet',
                'start_processing': 'İşlemeyi başlat',
                'start_fabric': 'Kumaşı başlat',
                'quality_check': 'Kalite kontrol',
                'mark_shipped': 'Gönderildi işaretle',
                'print_label': 'Etiket yazdır',

                # Teslimatlar
                'delivery': 'Teslimat',
                'deliveries': 'Teslimatlar',
                'supplier': 'Tedarikçi',
                'delivery_note': 'İrsaliye No',
                'expected_packages': 'Beklenen paket',
                'received_packages': 'Alınan paket',
                'delivery_complete': 'Teslimat tamamlandı',

                # İşleme
                'processing_type': 'İşlem türü',
                'estimated_duration': 'Tahmini süre',
                'start_time': 'Başlangıç',
                'end_time': 'Bitiş',
                'in_progress': 'Devam ediyor',

                # Kalite kontrol
                'quality_ok': 'Kalite OK',
                'quality_failed': 'Düzeltme gerekli',
                'error_type': 'Hata türü',
                'error_description': 'Hata açıklaması',
                'quality_errors': 'Kalite hataları',

                # Gönderim
                'shipping': 'Gönderim',
                'shipping_method': 'Gönderim şekli',
                'tracking_number': 'Takip numarası',
                'ready_to_ship': 'Gönderime hazır',
                'ship_packages': 'Paketleri gönder',
                'packages_shipped': 'Paket gönderildi',

                # İstatistikler
                'statistics': 'İstatistikler',
                'today': 'Bugün',
                'this_week': 'Bu hafta',
                'this_month': 'Bu ay',
                'packages_processed': 'İşlenen paket',
                'average_time': 'Ortalama süre',
                'efficiency': 'Verimlilik',

                # Çalışanlar
                'employee': 'Çalışan',
                'employees': 'Çalışanlar',
                'clock_in': 'Giriş',
                'clock_out': 'Çıkış',
                'break': 'Mola',
                'working_time': 'Çalışma süresi',

                # Hatalar
                'error_general': 'Bir hata oluştu',
                'error_connection': 'Bağlantı hatası',
                'error_database': 'Veritabanı hatası',
                'error_rfid': 'RFID okuma hatası',
                'error_scanner': 'Tarayıcı hatası',
                'error_validation': 'Doğrulama hatası',
                'error_permission': 'Yetki yok',

                # Onaylar
                'confirm_delete': 'Silmek istediğinize emin misiniz?',
                'confirm_logout': 'Çıkış yapmak istiyor musunuz?',
                'confirm_cancel': 'Değişiklikleri iptal et?',
                'confirm_action': 'İşlemi onayla?',

                # Mesajlar
                'msg_saved': 'Başarıyla kaydedildi',
                'msg_deleted': 'Başarıyla silindi',
                'msg_updated': 'Başarıyla güncellendi',
                'msg_sent': 'Başarıyla gönderildi',
                'msg_printed': 'Başarıyla yazdırıldı',
                'msg_no_data': 'Veri bulunamadı',
                'msg_loading': 'Veriler yükleniyor...',
                'msg_please_select': 'Lütfen seçin',
                'msg_required_field': 'Zorunlu alan',

                # Zaman
                'minutes': 'dakika',
                'hours': 'saat',
                'days': 'gün',
                'time': 'Zaman',
                'date': 'Tarih',
                'from': 'Başlangıç',
                'to': 'Bitiş',
                'duration': 'Süre',

                # Öncelikler
                'priority_low': 'Düşük',
                'priority_normal': 'Normal',
                'priority_high': 'Yüksek',
                'priority_express': 'Express',
                'priority_urgent': 'Acil',
            },

            # === Polski ===
            'pl': {
                # Ogólne
                'app_title': 'Shirtful Zarządzanie Magazynem',
                'welcome': 'Witamy',
                'goodbye': 'Do widzenia',
                'yes': 'Tak',
                'no': 'Nie',
                'ok': 'OK',
                'cancel': 'Anuluj',
                'save': 'Zapisz',
                'delete': 'Usuń',
                'edit': 'Edytuj',
                'search': 'Szukaj',
                'refresh': 'Odśwież',
                'back': 'Wstecz',
                'next': 'Dalej',
                'finish': 'Zakończ',
                'close': 'Zamknij',
                'error': 'Błąd',
                'warning': 'Ostrzeżenie',
                'info': 'Informacja',
                'success': 'Sukces',
                'loading': 'Ładowanie...',
                'please_wait': 'Proszę czekać...',

                # Logowanie
                'login': 'Zaloguj',
                'logout': 'Wyloguj',
                'rfid_instruction': 'Przyłóż kartę RFID do czytnika',
                'waiting_for_card': 'Oczekiwanie na kartę...',
                'login_successful': 'Logowanie pomyślne',
                'login_failed': 'Logowanie nieudane',
                'unknown_card': 'Nieznana karta!',
                'user_inactive': 'Użytkownik nieaktywny',

                # Nawigacja
                'main_menu': 'Menu główne',
                'wareneingang': 'Przyjęcie towaru',
                'veredelung': 'Uszlachetnianie',
                'betuchung': 'Tkanina',
                'qualitaetskontrolle': 'Kontrola jakości',
                'warenausgang': 'Wydanie towaru',

                # Paczki
                'package': 'Paczka',
                'packages': 'Paczki',
                'scan_package': 'Skanuj paczkę',
                'package_details': 'Szczegóły paczki',
                'package_id': 'ID paczki',
                'order_id': 'Nr zamówienia',
                'customer': 'Klient',
                'item_count': 'Liczba sztuk',
                'priority': 'Priorytet',
                'status': 'Status',
                'notes': 'Uwagi',
                'last_update': 'Ostatnia aktualizacja',

                # Status
                'status_received': 'Przyjęto',
                'status_processing': 'W obróbce',
                'status_fabric': 'W tkaninie',
                'status_quality': 'Kontrola jakości',
                'status_ok': 'Jakość OK',
                'status_rework': 'Wymaga poprawek',
                'status_ready': 'Gotowe do wysyłki',
                'status_shipped': 'Wysłano',

                # Akcje
                'new_delivery': 'Nowa dostawa',
                'register_package': 'Zarejestruj paczkę',
                'start_processing': 'Rozpocznij obróbkę',
                'start_fabric': 'Rozpocznij tkaninę',
                'quality_check': 'Sprawdź jakość',
                'mark_shipped': 'Oznacz jako wysłane',
                'print_label': 'Drukuj etykietę',

                # Dostawy
                'delivery': 'Dostawa',
                'deliveries': 'Dostawy',
                'supplier': 'Dostawca',
                'delivery_note': 'Nr listu przewozowego',
                'expected_packages': 'Oczekiwane paczki',
                'received_packages': 'Otrzymane paczki',
                'delivery_complete': 'Dostawa zakończona',

                # Obróbka
                'processing_type': 'Typ obróbki',
                'estimated_duration': 'Szacowany czas',
                'start_time': 'Czas rozpoczęcia',
                'end_time': 'Czas zakończenia',
                'in_progress': 'W trakcie',

                # Kontrola jakości
                'quality_ok': 'Jakość OK',
                'quality_failed': 'Wymaga poprawek',
                'error_type': 'Typ błędu',
                'error_description': 'Opis błędu',
                'quality_errors': 'Błędy jakości',

                # Wysyłka
                'shipping': 'Wysyłka',
                'shipping_method': 'Metoda wysyłki',
                'tracking_number': 'Numer śledzenia',
                'ready_to_ship': 'Gotowe do wysyłki',
                'ship_packages': 'Wyślij paczki',
                'packages_shipped': 'Paczki wysłane',

                # Statystyki
                'statistics': 'Statystyki',
                'today': 'Dzisiaj',
                'this_week': 'W tym tygodniu',
                'this_month': 'W tym miesiącu',
                'packages_processed': 'Przetworzone paczki',
                'average_time': 'Średni czas',
                'efficiency': 'Wydajność',

                # Pracownicy
                'employee': 'Pracownik',
                'employees': 'Pracownicy',
                'clock_in': 'Wejście',
                'clock_out': 'Wyjście',
                'break': 'Przerwa',
                'working_time': 'Czas pracy',

                # Błędy
                'error_general': 'Wystąpił błąd',
                'error_connection': 'Błąd połączenia',
                'error_database': 'Błąd bazy danych',
                'error_rfid': 'Błąd odczytu RFID',
                'error_scanner': 'Błąd skanera',
                'error_validation': 'Błąd walidacji',
                'error_permission': 'Brak uprawnień',

                # Potwierdzenia
                'confirm_delete': 'Na pewno usunąć?',
                'confirm_logout': 'Na pewno wylogować?',
                'confirm_cancel': 'Porzucić zmiany?',
                'confirm_action': 'Potwierdzić akcję?',

                # Komunikaty
                'msg_saved': 'Pomyślnie zapisano',
                'msg_deleted': 'Pomyślnie usunięto',
                'msg_updated': 'Pomyślnie zaktualizowano',
                'msg_sent': 'Pomyślnie wysłano',
                'msg_printed': 'Pomyślnie wydrukowano',
                'msg_no_data': 'Brak danych',
                'msg_loading': 'Ładowanie danych...',
                'msg_please_select': 'Proszę wybrać',
                'msg_required_field': 'Pole wymagane',

                # Czas
                'minutes': 'minuty',
                'hours': 'godziny',
                'days': 'dni',
                'time': 'Czas',
                'date': 'Data',
                'from': 'Od',
                'to': 'Do',
                'duration': 'Czas trwania',

                # Priorytety
                'priority_low': 'Niski',
                'priority_normal': 'Normalny',
                'priority_high': 'Wysoki',
                'priority_express': 'Express',
                'priority_urgent': 'Pilny',
            }
        }

    def get(self, key: str, language: str = None, default: str = None) -> str:
        """
        Holt eine Übersetzung.

        Args:
            key: Übersetzungsschlüssel
            language: Sprache (None für aktuelle)
            default: Standardwert falls nicht vorhanden

        Returns:
            Übersetzter Text
        """
        lang = language or self.current_language

        # Versuche Übersetzung zu finden
        if lang in self.translations:
            if key in self.translations[lang]:
                return self.translations[lang][key]

        # Fallback auf Default-Sprache
        if lang != self.default_language:
            if key in self.translations[self.default_language]:
                return self.translations[self.default_language][key]

        # Fallback auf Schlüssel oder Default
        return default or key

    def _(self, key: str, **kwargs) -> str:
        """
        Kurzform für get() mit Formatierung.

        Args:
            key: Übersetzungsschlüssel
            **kwargs: Formatierungsparameter

        Returns:
            Formatierter Text
        """
        text = self.get(key)

        # Formatierung anwenden
        if kwargs:
            try:
                text = text.format(**kwargs)
            except:
                pass

        return text

    def set_language(self, language: str) -> bool:
        """
        Setzt die aktuelle Sprache.

        Args:
            language: Sprachcode (de, en, tr, pl)

        Returns:
            True bei Erfolg
        """
        if language in self.translations:
            self.current_language = language
            self.logger.info(f"Sprache geändert auf: {language}")
            return True
        else:
            self.logger.warning(f"Unbekannte Sprache: {language}")
            return False

    def get_language(self) -> str:
        """
        Gibt die aktuelle Sprache zurück.

        Returns:
            Aktueller Sprachcode
        """
        return self.current_language

    def get_available_languages(self) -> Dict[str, str]:
        """
        Gibt verfügbare Sprachen zurück.

        Returns:
            Dictionary mit Code -> Name
        """
        languages = {}
        for code in self.translations.keys():
            # Sprachname aus app_title ableiten
            languages[code] = code.upper()

        # Bessere Namen
        language_names = {
            'de': 'Deutsch',
            'en': 'English',
            'tr': 'Türkçe',
            'pl': 'Polski'
        }

        for code, name in language_names.items():
            if code in languages:
                languages[code] = name

        return languages

    def add_translation(self, language: str, key: str, value: str):
        """
        Fügt eine Übersetzung hinzu.

        Args:
            language: Sprachcode
            key: Übersetzungsschlüssel
            value: Übersetzter Text
        """
        if language not in self.translations:
            self.translations[language] = {}

        self.translations[language][key] = value

    def load_from_file(self, filepath: str) -> bool:
        """
        Lädt Übersetzungen aus JSON-Datei.

        Args:
            filepath: Pfad zur JSON-Datei

        Returns:
            True bei Erfolg
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Übersetzungen mergen
            for lang, translations in data.items():
                if lang not in self.translations:
                    self.translations[lang] = {}
                self.translations[lang].update(translations)

            self.logger.info(f"Übersetzungen geladen von {filepath}")
            return True

        except Exception as e:
            self.logger.error(f"Fehler beim Laden der Übersetzungen: {e}")
            return False

    def save_to_file(self, filepath: str) -> bool:
        """
        Speichert Übersetzungen in JSON-Datei.

        Args:
            filepath: Pfad zur JSON-Datei

        Returns:
            True bei Erfolg
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.translations, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Übersetzungen gespeichert nach {filepath}")
            return True

        except Exception as e:
            self.logger.error(f"Fehler beim Speichern der Übersetzungen: {e}")
            return False

    def get_missing_translations(self, language: str) -> List[str]:
        """
        Findet fehlende Übersetzungen für eine Sprache.

        Args:
            language: Sprachcode

        Returns:
            Liste fehlender Schlüssel
        """
        if language not in self.translations:
            return []

        # Alle Schlüssel aus Default-Sprache
        all_keys = set(self.translations[self.default_language].keys())

        # Vorhandene Schlüssel in Zielsprache
        existing_keys = set(self.translations[language].keys())

        # Differenz
        missing = list(all_keys - existing_keys)
        missing.sort()

        return missing


# Globale Translations-Instanz
_translations = None


def get_translations() -> Translations:
    """
    Holt die globale Translations-Instanz.

    Returns:
        Translations-Instanz
    """
    global _translations
    if _translations is None:
        _translations = Translations()
    return _translations


# Shortcut-Funktion
def _(key: str, **kwargs) -> str:
    """
    Globale Übersetzungsfunktion.

    Args:
        key: Übersetzungsschlüssel
        **kwargs: Formatierungsparameter

    Returns:
        Übersetzter Text
    """
    return get_translations()._(key, **kwargs)


# Test
if __name__ == "__main__":
    # Test Translations
    trans = Translations()

    print("=== Shirtful WMS Translations ===\n")

    # Verfügbare Sprachen
    print("Verfügbare Sprachen:")
    for code, name in trans.get_available_languages().items():
        print(f"  {code}: {name}")

    print(f"\nAktuelle Sprache: {trans.get_language()}")

    # Test Übersetzungen
    print("\nTest Übersetzungen:")
    test_keys = ['welcome', 'scan_package', 'quality_ok', 'error_general']

    for lang in ['de', 'en', 'tr', 'pl']:
        trans.set_language(lang)
        print(f"\n{lang.upper()}:")
        for key in test_keys:
            print(f"  {key}: {trans.get(key)}")

    # Fehlende Übersetzungen
    print("\nFehlende Übersetzungen (PL):")
    missing = trans.get_missing_translations('pl')
    print(f"  Anzahl: {len(missing)}")
    if missing:
        print(f"  Erste 5: {missing[:5]}")