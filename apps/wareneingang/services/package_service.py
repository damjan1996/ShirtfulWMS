#!/usr/bin/env python3
"""
Shirtful WMS - Package Service
Service für paketbezogene Geschäftslogik
"""

import random
import string
from datetime import datetime
from typing import Dict, List, Optional, Any
import sys
import os

# Projekt-Root zum Python-Path hinzufügen
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from utils.database import Database
from utils.logger import setup_logger


class PackageService:
    """Service für alle paketbezogenen Operationen."""

    def __init__(self):
        """Initialisiert den Package Service."""
        self.db = Database()
        self.logger = setup_logger('package_service')

    def generate_package_id(self) -> str:
        """
        Generiert eine eindeutige Paket-ID.

        Returns:
            str: Eindeutige Paket-ID im Format PKG-YYYY-XXXXXX
        """
        year = datetime.now().year
        random_part = ''.join(random.choices(string.digits, k=6))
        return f"PKG-{year}-{random_part}"

    def generate_qr_code(self) -> str:
        """
        Generiert einen neuen QR-Code für ein Paket.

        Returns:
            str: Neuer QR-Code
        """
        return self.generate_package_id()

    def validate_package_data(self, package_data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validiert Paket-Daten vor der Registrierung.

        Args:
            package_data: Dictionary mit Paket-Daten

        Returns:
            tuple: (is_valid, error_message)
        """
        required_fields = ['order_id', 'customer']

        for field in required_fields:
            if not package_data.get(field, '').strip():
                return False, f"Feld '{field}' ist erforderlich"

        # Weitere Validierungen
        if package_data.get('item_count', 0) <= 0:
            return False, "Anzahl Artikel muss größer als 0 sein"

        # QR-Code eindeutig prüfen
        qr_code = package_data.get('package_id')
        if qr_code and self.package_exists(qr_code):
            return False, f"Paket mit QR-Code {qr_code} existiert bereits"

        return True, ""

    def register_package(self, delivery_id: str, package_data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Registriert ein neues Paket im System.

        Args:
            delivery_id: ID der zugehörigen Lieferung
            package_data: Dictionary mit Paket-Daten

        Returns:
            tuple: (success, message)
        """
        try:
            # Validierung
            is_valid, error_msg = self.validate_package_data(package_data)
            if not is_valid:
                return False, error_msg

            # QR-Code generieren falls nicht vorhanden
            if not package_data.get('package_id'):
                package_data['package_id'] = self.generate_qr_code()

            # Standardwerte setzen
            package_data.setdefault('status', 'incoming')
            package_data.setdefault('created_at', datetime.now())
            package_data.setdefault('updated_at', datetime.now())
            package_data['delivery_id'] = delivery_id

            # In Datenbank speichern
            success = self.db.register_package(
                package_data['package_id'],
                **package_data
            )

            if success:
                self.logger.info(f"Paket {package_data['package_id']} erfolgreich registriert")
                return True, f"Paket {package_data['package_id']} erfolgreich registriert"
            else:
                self.logger.error(f"Fehler beim Registrieren von Paket {package_data['package_id']}")
                return False, "Fehler beim Speichern in der Datenbank"

        except Exception as e:
            self.logger.error(f"Fehler bei Paket-Registrierung: {e}")
            return False, f"Unerwarteter Fehler: {str(e)}"

    def get_package(self, qr_code: str) -> Optional[Dict[str, Any]]:
        """
        Ruft Paket-Informationen anhand des QR-Codes ab.

        Args:
            qr_code: QR-Code des Pakets

        Returns:
            Optional[Dict]: Paket-Daten oder None falls nicht gefunden
        """
        try:
            package = self.db.get_package(qr_code)
            if package:
                self.logger.info(f"Paket {qr_code} gefunden")
            return package
        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen von Paket {qr_code}: {e}")
            return None

    def package_exists(self, qr_code: str) -> bool:
        """
        Prüft ob ein Paket mit dem gegebenen QR-Code existiert.

        Args:
            qr_code: QR-Code des Pakets

        Returns:
            bool: True falls Paket existiert
        """
        package = self.get_package(qr_code)
        return package is not None

    def update_package_status(self, qr_code: str, new_status: str, notes: str = '') -> bool:
        """
        Aktualisiert den Status eines Pakets.

        Args:
            qr_code: QR-Code des Pakets
            new_status: Neuer Status
            notes: Optionale Notizen

        Returns:
            bool: True bei Erfolg
        """
        try:
            success = self.db.update_package_status(qr_code, new_status, notes)
            if success:
                self.logger.info(f"Status von Paket {qr_code} auf '{new_status}' geändert")
            return success
        except Exception as e:
            self.logger.error(f"Fehler beim Aktualisieren von Paket {qr_code}: {e}")
            return False

    def get_packages_for_delivery(self, delivery_id: str) -> List[Dict[str, Any]]:
        """
        Ruft alle Pakete einer Lieferung ab.

        Args:
            delivery_id: ID der Lieferung

        Returns:
            List[Dict]: Liste der Pakete
        """
        try:
            packages = self.db.get_packages_by_delivery(delivery_id)
            return packages or []
        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen der Pakete für Lieferung {delivery_id}: {e}")
            return []

    def get_recent_packages(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Ruft die letzten registrierten Pakete ab.

        Args:
            limit: Maximale Anzahl der Pakete

        Returns:
            List[Dict]: Liste der letzten Pakete
        """
        try:
            packages = self.db.get_all_packages()
            if packages:
                # Nach Datum sortieren und limitieren
                sorted_packages = sorted(
                    packages,
                    key=lambda x: x.get('created_at', datetime.min),
                    reverse=True
                )
                return sorted_packages[:limit]
            return []
        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen der letzten Pakete: {e}")
            return []

    def get_package_statistics(self) -> Dict[str, int]:
        """
        Ruft Paket-Statistiken ab.

        Returns:
            Dict: Statistiken nach Status
        """
        try:
            stats = self.db.get_package_count_by_status()
            return stats or {}
        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen der Paket-Statistiken: {e}")
            return {}

    def get_today_package_count(self) -> int:
        """
        Ruft die Anzahl der heute registrierten Pakete ab.

        Returns:
            int: Anzahl der Pakete
        """
        try:
            # Hier könnte eine spezifische DB-Methode für heute's Pakete verwendet werden
            all_packages = self.db.get_all_packages()
            today = datetime.now().date()

            today_count = 0
            for package in all_packages or []:
                created_at = package.get('created_at')
                if isinstance(created_at, datetime) and created_at.date() == today:
                    today_count += 1
                elif isinstance(created_at, str):
                    # Fallback für String-Datumsformat
                    try:
                        created_date = datetime.fromisoformat(created_at).date()
                        if created_date == today:
                            today_count += 1
                    except:
                        pass

            return today_count
        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen der heutigen Paket-Anzahl: {e}")
            return 0

    def search_packages(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Sucht nach Paketen basierend auf verschiedenen Kriterien.

        Args:
            search_term: Suchbegriff

        Returns:
            List[Dict]: Gefundene Pakete
        """
        try:
            all_packages = self.db.get_all_packages()
            if not all_packages:
                return []

            search_term = search_term.lower().strip()
            results = []

            for package in all_packages:
                # Suche in verschiedenen Feldern
                searchable_fields = [
                    package.get('package_id', ''),
                    package.get('order_id', ''),
                    package.get('customer', ''),
                    package.get('notes', '')
                ]

                for field in searchable_fields:
                    if search_term in str(field).lower():
                        results.append(package)
                        break

            return results
        except Exception as e:
            self.logger.error(f"Fehler bei der Paket-Suche: {e}")
            return []

    def get_package_priorities(self) -> List[str]:
        """
        Ruft verfügbare Prioritätsstufen ab.

        Returns:
            List[str]: Liste der Prioritäten
        """
        return ["Normal", "Hoch", "Express", "Eilig"]

    def validate_qr_code_format(self, qr_code: str) -> bool:
        """
        Validiert das Format eines QR-Codes.

        Args:
            qr_code: Zu validierender QR-Code

        Returns:
            bool: True falls Format gültig
        """
        if not qr_code:
            return False

        # Grundlegende Format-Prüfung
        # Erwartet: PKG-YYYY-XXXXXX oder ähnlich
        parts = qr_code.split('-')
        if len(parts) >= 3 and parts[0] == 'PKG':
            return True

        # Fallback für andere Formate
        return len(qr_code) >= 5

    def get_package_history(self, qr_code: str) -> List[Dict[str, Any]]:
        """
        Ruft die Historie eines Pakets ab.

        Args:
            qr_code: QR-Code des Pakets

        Returns:
            List[Dict]: Historie-Einträge
        """
        try:
            # Hier könnte eine spezifische DB-Methode für Paket-Historie verwendet werden
            # Für jetzt einfache Implementierung
            package = self.get_package(qr_code)
            if package:
                return [{
                    'timestamp': package.get('created_at', datetime.now()),
                    'action': 'Paket registriert',
                    'status': 'incoming',
                    'user': 'System'
                }]
            return []
        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen der Paket-Historie: {e}")
            return []

    def bulk_register_packages(self, delivery_id: str, packages_data: List[Dict[str, Any]]) -> tuple[
        int, int, List[str]]:
        """
        Registriert mehrere Pakete gleichzeitig.

        Args:
            delivery_id: ID der zugehörigen Lieferung
            packages_data: Liste mit Paket-Daten

        Returns:
            tuple: (erfolgreiche_pakete, fehlgeschlagene_pakete, fehlermeldungen)
        """
        successful = 0
        failed = 0
        errors = []

        for package_data in packages_data:
            try:
                success, message = self.register_package(delivery_id, package_data)
                if success:
                    successful += 1
                else:
                    failed += 1
                    errors.append(f"Paket {package_data.get('package_id', 'Unbekannt')}: {message}")
            except Exception as e:
                failed += 1
                errors.append(f"Paket {package_data.get('package_id', 'Unbekannt')}: {str(e)}")

        self.logger.info(f"Bulk-Registrierung abgeschlossen: {successful} erfolgreich, {failed} fehlgeschlagen")
        return successful, failed, errors

    def export_packages_csv(self, delivery_id: Optional[str] = None) -> str:
        """
        Exportiert Pakete als CSV-String.

        Args:
            delivery_id: Optional - nur Pakete einer bestimmten Lieferung

        Returns:
            str: CSV-Inhalt
        """
        try:
            if delivery_id:
                packages = self.get_packages_for_delivery(delivery_id)
            else:
                packages = self.db.get_all_packages() or []

            if not packages:
                return "Keine Pakete gefunden"

            # CSV-Header
            csv_lines = ["QR-Code,Bestellnummer,Kunde,Artikel-Anzahl,Priorität,Status,Erstellt"]

            # Paket-Daten
            for package in packages:
                line = f"{package.get('package_id', '')}," \
                       f"{package.get('order_id', '')}," \
                       f"{package.get('customer', '')}," \
                       f"{package.get('item_count', 0)}," \
                       f"{package.get('priority', 'Normal')}," \
                       f"{package.get('status', 'unknown')}," \
                       f"{package.get('created_at', '')}"
                csv_lines.append(line)

            return '\n'.join(csv_lines)

        except Exception as e:
            self.logger.error(f"Fehler beim CSV-Export: {e}")
            return f"Fehler beim Export: {str(e)}"