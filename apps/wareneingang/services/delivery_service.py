"""
Lieferungs-Service für die Wareneingangsstation.
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
import logging

from ..models.delivery import Delivery
from ..config.constants import SUPPLIERS, VALIDATION_RULES


class DeliveryService:
    """Service für Lieferungsverwaltung."""

    def __init__(self):
        self.logger = logging.getLogger('wareneingang.delivery')
        self.current_delivery: Optional[Delivery] = None
        self.delivery_history: List[Delivery] = []
        self.delivery_cache: Dict[str, Delivery] = {}

        # Statistiken
        self.daily_stats: Dict[str, Any] = {}
        self._initialize_daily_stats()

        self.logger.info("DeliveryService initialisiert")

    def _initialize_daily_stats(self):
        """Initialisiert die täglichen Statistiken."""
        today = datetime.now().date().isoformat()
        self.daily_stats = {
            'date': today,
            'deliveries_created': 0,
            'deliveries_completed': 0,
            'deliveries_cancelled': 0,
            'total_packages_received': 0,
            'average_packages_per_delivery': 0.0,
            'suppliers': {}
        }

    def _validate_delivery_data(self, supplier: str, delivery_note: Optional[str] = None,
                                expected_packages: int = 0, notes: Optional[str] = None) -> bool:
        """
        Validiert Lieferungsdaten.

        Args:
            supplier: Lieferant
            delivery_note: Lieferschein-Nummer
            expected_packages: Erwartete Anzahl Pakete
            notes: Notizen

        Returns:
            True wenn gültig, False sonst

        Raises:
            ValueError: Bei ungültigen Daten
        """
        if not supplier or not supplier.strip():
            raise ValueError("Lieferant ist erforderlich")

        if supplier not in SUPPLIERS:
            raise ValueError(f"Ungültiger Lieferant: {supplier}")

        if delivery_note and len(delivery_note) > VALIDATION_RULES['delivery_note_max_length']:
            raise ValueError(
                f"Lieferschein-Nummer zu lang (max. {VALIDATION_RULES['delivery_note_max_length']} Zeichen)")

        if expected_packages < 0:
            raise ValueError("Erwartete Pakete können nicht negativ sein")

        if notes and len(notes) > VALIDATION_RULES['notes_max_length']:
            raise ValueError(f"Notizen zu lang (max. {VALIDATION_RULES['notes_max_length']} Zeichen)")

        return True

    def create_delivery(self,
                        supplier: str,
                        delivery_note: Optional[str] = None,
                        expected_packages: int = 0,
                        notes: Optional[str] = None,
                        employee_id: Optional[int] = None) -> Delivery:
        """
        Erstellt eine neue Lieferung.

        Args:
            supplier: Lieferant
            delivery_note: Lieferschein-Nummer (optional)
            expected_packages: Erwartete Anzahl Pakete
            notes: Notizen (optional)
            employee_id: ID des Mitarbeiters

        Returns:
            Erstellte Lieferung

        Raises:
            ValueError: Bei ungültigen Daten
            RuntimeError: Wenn bereits eine aktive Lieferung existiert
        """
        # Prüfe ob bereits eine aktive Lieferung existiert
        if self.current_delivery and self.current_delivery.is_active:
            raise RuntimeError(f"Bereits eine aktive Lieferung vorhanden: {self.current_delivery.id}")

        # Validiere Eingabedaten
        self._validate_delivery_data(supplier, delivery_note, expected_packages, notes)

        # Lieferungs-ID generieren
        delivery_id = f"DEL-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Lieferung erstellen
        delivery = Delivery(
            id=delivery_id,
            supplier=supplier,
            delivery_note=delivery_note,
            expected_packages=expected_packages,
            notes=notes,
            employee_id=employee_id
        )

        # Als aktuelle Lieferung setzen
        self.current_delivery = delivery
        self.delivery_cache[delivery_id] = delivery

        # Statistiken aktualisieren
        self._update_daily_stats('delivery_created', supplier)

        self.logger.info(
            f"Neue Lieferung erstellt: {delivery_id} von {supplier} (erwartet: {expected_packages} Pakete)")

        return delivery

    def get_current_delivery(self) -> Optional[Delivery]:
        """Gibt die aktuelle aktive Lieferung zurück."""
        # Prüfe ob aktuelle Lieferung noch aktiv ist
        if self.current_delivery and not self.current_delivery.is_active:
            self.current_delivery = None

        return self.current_delivery

    def get_delivery_by_id(self, delivery_id: str) -> Optional[Delivery]:
        """
        Holt eine Lieferung anhand der ID.

        Args:
            delivery_id: Lieferungs-ID

        Returns:
            Delivery-Objekt oder None wenn nicht gefunden
        """
        return self.delivery_cache.get(delivery_id)

    def add_package_to_delivery(self, package_id: Optional[str] = None) -> bool:
        """
        Fügt ein Paket zur aktuellen Lieferung hinzu.

        Args:
            package_id: Optional - ID des hinzugefügten Pakets

        Returns:
            True bei Erfolg, False wenn keine aktive Lieferung
        """
        if not self.current_delivery or not self.current_delivery.is_active:
            self.logger.warning("Versuch Paket hinzuzufügen ohne aktive Lieferung")
            return False

        # Paket zur Lieferung hinzufügen
        self.current_delivery.add_package(package_id)

        # Statistiken aktualisieren
        self._update_daily_stats('package_received')

        self.logger.info(
            f"Paket zu Lieferung {self.current_delivery.id} hinzugefügt (Total: {self.current_delivery.received_packages})")

        # Prüfe automatische Vervollständigung
        if self.current_delivery.is_complete:
            self.logger.info(f"Lieferung {self.current_delivery.id} automatisch vollständig")

        return True

    def remove_package_from_delivery(self, package_id: Optional[str] = None) -> bool:
        """
        Entfernt ein Paket aus der aktuellen Lieferung.

        Args:
            package_id: Optional - ID des zu entfernenden Pakets

        Returns:
            True bei Erfolg, False wenn keine aktive Lieferung oder Fehler
        """
        if not self.current_delivery:
            self.logger.warning("Versuch Paket zu entfernen ohne aktive Lieferung")
            return False

        success = self.current_delivery.remove_package(package_id)

        if success:
            self.logger.info(
                f"Paket aus Lieferung {self.current_delivery.id} entfernt (Total: {self.current_delivery.received_packages})")

        return success

    def finish_delivery(self, force: bool = False) -> bool:
        """
        Schließt die aktuelle Lieferung ab.

        Args:
            force: Erzwingt Abschluss auch bei unvollständiger Lieferung

        Returns:
            True bei Erfolg, False wenn keine aktive Lieferung oder Fehler
        """
        if not self.current_delivery:
            self.logger.warning("Versuch Lieferung abzuschließen ohne aktive Lieferung")
            return False

        if not self.current_delivery.is_active:
            self.logger.warning(f"Lieferung {self.current_delivery.id} ist nicht aktiv")
            return False

        # Versuche Lieferung abzuschließen
        success = self.current_delivery.finish(force)

        if success:
            # Zur Historie hinzufügen
            self.delivery_history.append(self.current_delivery)

            # Statistiken aktualisieren
            completion_type = 'forced' if force else 'complete'
            self._update_daily_stats('delivery_completed', completion_type=completion_type)

            self.logger.info(
                f"Lieferung {self.current_delivery.id} abgeschlossen mit {self.current_delivery.received_packages} Paketen ({'erzwungen' if force else 'vollständig'})")

            # Aktuelle Lieferung zurücksetzen
            finished_delivery = self.current_delivery
            self.current_delivery = None

            return True
        else:
            self.logger.warning(
                f"Lieferung {self.current_delivery.id} konnte nicht abgeschlossen werden (unvollständig und force=False)")
            return False

    def cancel_delivery(self, reason: Optional[str] = None) -> bool:
        """
        Storniert die aktuelle Lieferung.

        Args:
            reason: Optional - Grund für Stornierung

        Returns:
            True bei Erfolg, False wenn keine aktive Lieferung oder Fehler
        """
        if not self.current_delivery:
            self.logger.warning("Versuch Lieferung zu stornieren ohne aktive Lieferung")
            return False

        if not self.current_delivery.is_active:
            self.logger.warning(f"Lieferung {self.current_delivery.id} ist nicht aktiv")
            return False

        # Lieferung stornieren
        success = self.current_delivery.cancel(reason)

        if success:
            # Zur Historie hinzufügen
            self.delivery_history.append(self.current_delivery)

            # Statistiken aktualisieren
            self._update_daily_stats('delivery_cancelled', reason=reason)

            self.logger.info(
                f"Lieferung {self.current_delivery.id} storniert" + (f" (Grund: {reason})" if reason else ""))

            # Aktuelle Lieferung zurücksetzen
            cancelled_delivery = self.current_delivery
            self.current_delivery = None

            return True

        return False

    def set_delivery_partial(self, reason: Optional[str] = None) -> bool:
        """
        Markiert die aktuelle Lieferung als Teillieferung.

        Args:
            reason: Optional - Grund für Teillieferung

        Returns:
            True bei Erfolg, False wenn keine aktive Lieferung oder Fehler
        """
        if not self.current_delivery:
            self.logger.warning("Versuch Lieferung als teilweise zu markieren ohne aktive Lieferung")
            return False

        if not self.current_delivery.is_active:
            self.logger.warning(f"Lieferung {self.current_delivery.id} ist nicht aktiv")
            return False

        # Als Teillieferung markieren
        success = self.current_delivery.set_partial(reason)

        if success:
            # Zur Historie hinzufügen
            self.delivery_history.append(self.current_delivery)

            # Statistiken aktualisieren
            self._update_daily_stats('delivery_partial', reason=reason)

            self.logger.info(f"Lieferung {self.current_delivery.id} als Teillieferung markiert" + (
                f" (Grund: {reason})" if reason else ""))

            # Aktuelle Lieferung zurücksetzen
            partial_delivery = self.current_delivery
            self.current_delivery = None

            return True

        return False

    def has_active_delivery(self) -> bool:
        """Prüft ob eine aktive Lieferung vorhanden ist."""
        current = self.get_current_delivery()
        return current is not None and current.is_active

    def get_delivery_progress(self) -> Dict[str, Any]:
        """
        Gibt den Fortschritt der aktuellen Lieferung zurück.

        Returns:
            Dictionary mit Fortschrittsdaten
        """
        if not self.current_delivery:
            return {
                'has_active_delivery': False,
                'progress_percentage': 0,
                'received_packages': 0,
                'expected_packages': 0,
                'remaining_packages': 0,
                'is_complete': False,
                'is_overdelivered': False
            }

        return {
            'has_active_delivery': True,
            'delivery_id': self.current_delivery.id,
            'supplier': self.current_delivery.supplier,
            'progress_percentage': self.current_delivery.completion_percentage,
            'received_packages': self.current_delivery.received_packages,
            'expected_packages': self.current_delivery.expected_packages,
            'remaining_packages': self.current_delivery.remaining_packages,
            'is_complete': self.current_delivery.is_complete,
            'is_overdelivered': self.current_delivery.is_overdelivered,
            'duration_minutes': self.current_delivery.duration,
            'packages_per_minute': self.current_delivery.packages_per_minute,
            'start_time': self.current_delivery.start_time.isoformat() if self.current_delivery.start_time else None
        }

    def get_delivery_stats(self) -> Dict[str, Any]:
        """
        Gibt Statistiken zu Lieferungen zurück.

        Returns:
            Dictionary mit Statistiken
        """
        # Aktuelle Session-Statistiken
        total_deliveries = len(self.delivery_history)
        if self.current_delivery:
            total_deliveries += 1

        total_packages = sum(d.received_packages for d in self.delivery_history)
        if self.current_delivery:
            total_packages += self.current_delivery.received_packages

        # Tagesstatistiken
        today_deliveries = self.daily_stats['deliveries_created']
        today_packages = self.daily_stats['total_packages_received']

        # Durchschnittswerte
        avg_packages_per_delivery = 0.0
        if total_deliveries > 0:
            avg_packages_per_delivery = total_packages / total_deliveries

        # Status-Verteilung
        status_distribution = {}
        for delivery in self.delivery_history:
            status = delivery.status
            status_distribution[status] = status_distribution.get(status, 0) + 1

        # Lieferanten-Statistiken
        supplier_stats = {}
        for delivery in self.delivery_history:
            supplier = delivery.supplier
            if supplier not in supplier_stats:
                supplier_stats[supplier] = {
                    'count': 0,
                    'total_packages': 0,
                    'avg_packages': 0.0
                }

            supplier_stats[supplier]['count'] += 1
            supplier_stats[supplier]['total_packages'] += delivery.received_packages
            supplier_stats[supplier]['avg_packages'] = (
                    supplier_stats[supplier]['total_packages'] / supplier_stats[supplier]['count']
            )

        return {
            # Session-Statistiken
            'total_deliveries_session': total_deliveries,
            'total_packages_session': total_packages,
            'avg_packages_per_delivery_session': round(avg_packages_per_delivery, 1),

            # Tagesstatistiken
            'total_deliveries_today': today_deliveries,
            'total_packages_today': today_packages,
            'deliveries_completed_today': self.daily_stats['deliveries_completed'],
            'deliveries_cancelled_today': self.daily_stats['deliveries_cancelled'],

            # Aktuelle Lieferung
            'active_delivery': self.current_delivery is not None,
            'current_delivery_packages': self.current_delivery.received_packages if self.current_delivery else 0,

            # Historie
            'delivery_history_count': len(self.delivery_history),
            'status_distribution': status_distribution,
            'supplier_statistics': supplier_stats,

            # Performance
            'avg_duration_minutes': self._calculate_average_duration(),
            'avg_packages_per_minute': self._calculate_average_packages_per_minute()
        }

    def _calculate_average_duration(self) -> Optional[float]:
        """Berechnet die durchschnittliche Lieferungsdauer."""
        durations = []
        for delivery in self.delivery_history:
            if delivery.duration:
                durations.append(delivery.duration)

        if durations:
            return round(sum(durations) / len(durations), 1)
        return None

    def _calculate_average_packages_per_minute(self) -> Optional[float]:
        """Berechnet die durchschnittlichen Pakete pro Minute."""
        rates = []
        for delivery in self.delivery_history:
            if delivery.packages_per_minute:
                rates.append(delivery.packages_per_minute)

        if rates:
            return round(sum(rates) / len(rates), 2)
        return None

    def _update_daily_stats(self, event_type: str, supplier: Optional[str] = None, **kwargs):
        """
        Aktualisiert die täglichen Statistiken.

        Args:
            event_type: Art des Events
            supplier: Optional - Lieferant
            **kwargs: Zusätzliche Parameter
        """
        # Prüfe ob neuer Tag
        today = datetime.now().date().isoformat()
        if self.daily_stats['date'] != today:
            self._initialize_daily_stats()

        if event_type == 'delivery_created':
            self.daily_stats['deliveries_created'] += 1
            if supplier:
                supplier_stats = self.daily_stats['suppliers'].get(supplier, {'count': 0, 'packages': 0})
                supplier_stats['count'] += 1
                self.daily_stats['suppliers'][supplier] = supplier_stats

        elif event_type == 'delivery_completed':
            self.daily_stats['deliveries_completed'] += 1

        elif event_type == 'delivery_cancelled':
            self.daily_stats['deliveries_cancelled'] += 1

        elif event_type == 'package_received':
            self.daily_stats['total_packages_received'] += 1

            # Aktualisiere Durchschnitt
            if self.daily_stats['deliveries_created'] > 0:
                self.daily_stats['average_packages_per_delivery'] = (
                        self.daily_stats['total_packages_received'] / self.daily_stats['deliveries_created']
                )

    def get_delivery_history(self, limit: Optional[int] = None) -> List[Delivery]:
        """
        Gibt die Lieferungshistorie zurück.

        Args:
            limit: Optional - Maximale Anzahl Einträge

        Returns:
            Liste der Lieferungen (neueste zuerst)
        """
        history = sorted(self.delivery_history, key=lambda d: d.start_time or datetime.min, reverse=True)

        if limit:
            return history[:limit]

        return history

    def search_deliveries(self, **filters) -> List[Delivery]:
        """
        Sucht Lieferungen basierend auf Filtern.

        Args:
            **filters: Such-Filter

        Returns:
            Liste der gefilterten Lieferungen
        """
        results = []

        # Alle Lieferungen durchsuchen (Historie + aktuelle)
        all_deliveries = self.delivery_history.copy()
        if self.current_delivery:
            all_deliveries.append(self.current_delivery)

        for delivery in all_deliveries:
            match = True

            # Filter anwenden
            for key, value in filters.items():
                if key == 'supplier' and delivery.supplier != value:
                    match = False
                    break
                elif key == 'status' and delivery.status != value:
                    match = False
                    break
                elif key == 'employee_id' and delivery.employee_id != value:
                    match = False
                    break
                elif key == 'delivery_note' and value.lower() not in (delivery.delivery_note or '').lower():
                    match = False
                    break
                elif key == 'min_packages' and delivery.received_packages < value:
                    match = False
                    break
                elif key == 'max_packages' and delivery.received_packages > value:
                    match = False
                    break
                elif key == 'date_from' and delivery.start_time and delivery.start_time.date() < value:
                    match = False
                    break
                elif key == 'date_to' and delivery.start_time and delivery.start_time.date() > value:
                    match = False
                    break

            if match:
                results.append(delivery)

        # Nach Start-Zeit sortieren (neueste zuerst)
        return sorted(results, key=lambda d: d.start_time or datetime.min, reverse=True)

    def get_supplier_performance(self) -> Dict[str, Dict[str, Any]]:
        """
        Gibt Performance-Statistiken pro Lieferant zurück.

        Returns:
            Dictionary mit Lieferanten-Performance
        """
        performance = {}

        for delivery in self.delivery_history:
            supplier = delivery.supplier

            if supplier not in performance:
                performance[supplier] = {
                    'total_deliveries': 0,
                    'completed_deliveries': 0,
                    'cancelled_deliveries': 0,
                    'total_packages': 0,
                    'avg_packages_per_delivery': 0.0,
                    'avg_duration_minutes': 0.0,
                    'completion_rate': 0.0,
                    'on_time_rate': 0.0
                }

            stats = performance[supplier]
            stats['total_deliveries'] += 1
            stats['total_packages'] += delivery.received_packages

            if delivery.status == 'completed':
                stats['completed_deliveries'] += 1
            elif delivery.status == 'cancelled':
                stats['cancelled_deliveries'] += 1

        # Durchschnittswerte berechnen
        for supplier, stats in performance.items():
            if stats['total_deliveries'] > 0:
                stats['avg_packages_per_delivery'] = round(
                    stats['total_packages'] / stats['total_deliveries'], 1
                )
                stats['completion_rate'] = round(
                    (stats['completed_deliveries'] / stats['total_deliveries']) * 100, 1
                )

        return performance

    def export_delivery_data(self, start_date: Optional[datetime] = None,
                             end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Exportiert Lieferungsdaten für einen Zeitraum.

        Args:
            start_date: Optional - Start-Datum
            end_date: Optional - End-Datum

        Returns:
            Liste mit Export-Daten
        """
        export_data = []

        # Filter nach Datum
        for delivery in self.delivery_history:
            if start_date and delivery.start_time and delivery.start_time < start_date:
                continue
            if end_date and delivery.start_time and delivery.start_time > end_date:
                continue

            # Export-Daten zusammenstellen
            export_data.append({
                'delivery_id': delivery.id,
                'supplier': delivery.supplier,
                'delivery_note': delivery.delivery_note or '',
                'expected_packages': delivery.expected_packages,
                'received_packages': delivery.received_packages,
                'completion_percentage': delivery.completion_percentage,
                'status': delivery.status,
                'start_time': delivery.start_time.isoformat() if delivery.start_time else '',
                'end_time': delivery.end_time.isoformat() if delivery.end_time else '',
                'duration_minutes': delivery.duration,
                'packages_per_minute': delivery.packages_per_minute,
                'is_complete': delivery.is_complete,
                'is_overdelivered': delivery.is_overdelivered,
                'employee_id': delivery.employee_id or '',
                'notes': delivery.notes or '',
                'package_count': len(delivery.package_ids)
            })

        return export_data