"""
Lieferungs-Modell
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
import json


@dataclass
class Delivery:
    """Datenmodell für eine Lieferung."""

    id: str
    supplier: str
    delivery_note: Optional[str] = None
    expected_packages: int = 0
    received_packages: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    notes: Optional[str] = None
    status: str = "active"
    employee_id: Optional[int] = None
    package_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Wird nach der Initialisierung aufgerufen."""
        if self.start_time is None:
            self.start_time = datetime.now()

        # Validierung
        self._validate()

    def _validate(self):
        """Validiert die Lieferungsdaten."""
        if not self.id:
            raise ValueError("Lieferungs-ID ist erforderlich")

        if not self.supplier:
            raise ValueError("Lieferant ist erforderlich")

        if self.expected_packages < 0:
            raise ValueError("Erwartete Pakete können nicht negativ sein")

        if self.received_packages < 0:
            raise ValueError("Empfangene Pakete können nicht negativ sein")

        if self.status not in ["active", "completed", "cancelled", "partial"]:
            raise ValueError(f"Ungültiger Status: {self.status}")

    @property
    def is_complete(self) -> bool:
        """Prüft ob die Lieferung vollständig ist."""
        return (self.expected_packages > 0 and
                self.received_packages >= self.expected_packages)

    @property
    def is_active(self) -> bool:
        """Prüft ob die Lieferung aktiv ist."""
        return self.status == "active"

    @property
    def is_finished(self) -> bool:
        """Prüft ob die Lieferung beendet ist."""
        return self.status in ["completed", "cancelled"]

    @property
    def completion_percentage(self) -> float:
        """Berechnet den Fertigstellungsgrad."""
        if self.expected_packages == 0:
            return 0.0
        return min(100.0, (self.received_packages / self.expected_packages) * 100)

    @property
    def duration(self) -> Optional[float]:
        """Berechnet die Dauer der Lieferung in Minuten."""
        if not self.start_time:
            return None

        end_time = self.end_time or datetime.now()
        delta = end_time - self.start_time
        return delta.total_seconds() / 60.0

    @property
    def packages_per_minute(self) -> Optional[float]:
        """Berechnet die durchschnittlichen Pakete pro Minute."""
        duration = self.duration
        if not duration or duration == 0:
            return None

        return self.received_packages / duration

    @property
    def remaining_packages(self) -> int:
        """Berechnet die verbleibenden Pakete."""
        return max(0, self.expected_packages - self.received_packages)

    @property
    def is_overdelivered(self) -> bool:
        """Prüft ob mehr Pakete empfangen wurden als erwartet."""
        return (self.expected_packages > 0 and
                self.received_packages > self.expected_packages)

    def add_package(self, package_id: Optional[str] = None) -> None:
        """
        Fügt ein Paket zur Lieferung hinzu.

        Args:
            package_id: Optional - ID des hinzugefügten Pakets
        """
        self.received_packages += 1

        if package_id and package_id not in self.package_ids:
            self.package_ids.append(package_id)

        # Aktualisiere Metadaten
        self.metadata['last_package_added'] = datetime.now().isoformat()

        # Automatisches Abschließen wenn Ziel erreicht
        if self.is_complete and self.status == "active":
            self.status = "completed"
            if not self.end_time:
                self.end_time = datetime.now()

    def remove_package(self, package_id: Optional[str] = None) -> bool:
        """
        Entfernt ein Paket aus der Lieferung.

        Args:
            package_id: Optional - ID des zu entfernenden Pakets

        Returns:
            True wenn erfolgreich entfernt, False sonst
        """
        if self.received_packages > 0:
            self.received_packages -= 1

            if package_id and package_id in self.package_ids:
                self.package_ids.remove(package_id)

            # Status zurücksetzen falls nötig
            if self.status == "completed" and not self.is_complete:
                self.status = "active"
                self.end_time = None

            return True

        return False

    def finish(self, force: bool = False) -> bool:
        """
        Schließt die Lieferung ab.

        Args:
            force: Erzwingt Abschluss auch bei unvollständiger Lieferung

        Returns:
            True wenn erfolgreich abgeschlossen, False sonst
        """
        if self.status != "active":
            return False

        if not force and not self.is_complete:
            # Nur abschließen wenn vollständig oder Force-Flag gesetzt
            return False

        self.status = "completed"
        self.end_time = datetime.now()
        self.metadata['completion_type'] = 'forced' if force else 'automatic'

        return True

    def cancel(self, reason: Optional[str] = None) -> bool:
        """
        Storniert die Lieferung.

        Args:
            reason: Optional - Grund für Stornierung

        Returns:
            True wenn erfolgreich storniert, False sonst
        """
        if self.status != "active":
            return False

        self.status = "cancelled"
        self.end_time = datetime.now()

        if reason:
            self.metadata['cancellation_reason'] = reason

        return True

    def set_partial(self, reason: Optional[str] = None) -> bool:
        """
        Markiert die Lieferung als Teillieferung.

        Args:
            reason: Optional - Grund für Teillieferung

        Returns:
            True wenn erfolgreich markiert, False sonst
        """
        if self.status != "active":
            return False

        self.status = "partial"
        self.end_time = datetime.now()

        if reason:
            self.metadata['partial_reason'] = reason

        return True

    def add_note(self, note: str) -> None:
        """
        Fügt eine Notiz zur Lieferung hinzu.

        Args:
            note: Hinzuzufügende Notiz
        """
        timestamp = datetime.now().strftime('%H:%M:%S')
        new_note = f"[{timestamp}] {note}"

        if self.notes:
            self.notes += f"\n{new_note}"
        else:
            self.notes = new_note

    def get_summary(self) -> Dict[str, Any]:
        """
        Gibt eine Zusammenfassung der Lieferung zurück.

        Returns:
            Dictionary mit Zusammenfassungsdaten
        """
        return {
            'id': self.id,
            'supplier': self.supplier,
            'status': self.status,
            'progress': f"{self.received_packages}/{self.expected_packages}",
            'completion_percentage': round(self.completion_percentage, 1),
            'duration_minutes': round(self.duration, 1) if self.duration else None,
            'packages_per_minute': round(self.packages_per_minute, 2) if self.packages_per_minute else None,
            'is_complete': self.is_complete,
            'is_overdelivered': self.is_overdelivered,
            'package_count': len(self.package_ids)
        }

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary für Serialisierung."""
        return {
            'id': self.id,
            'supplier': self.supplier,
            'delivery_note': self.delivery_note,
            'expected_packages': self.expected_packages,
            'received_packages': self.received_packages,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'notes': self.notes,
            'status': self.status,
            'employee_id': self.employee_id,
            'package_ids': self.package_ids.copy(),
            'metadata': self.metadata.copy()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Delivery':
        """
        Erstellt Delivery-Objekt aus Dictionary.

        Args:
            data: Dictionary mit Lieferungsdaten

        Returns:
            Delivery-Objekt
        """
        delivery = cls(
            id=data['id'],
            supplier=data['supplier'],
            delivery_note=data.get('delivery_note'),
            expected_packages=data.get('expected_packages', 0),
            received_packages=data.get('received_packages', 0),
            notes=data.get('notes'),
            status=data.get('status', 'active'),
            employee_id=data.get('employee_id'),
            package_ids=data.get('package_ids', []),
            metadata=data.get('metadata', {})
        )

        # Zeitstempel parsen
        if data.get('start_time'):
            delivery.start_time = datetime.fromisoformat(data['start_time'])
        if data.get('end_time'):
            delivery.end_time = datetime.fromisoformat(data['end_time'])

        return delivery

    def to_json(self) -> str:
        """Konvertiert zu JSON-String."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'Delivery':
        """
        Erstellt Delivery-Objekt aus JSON-String.

        Args:
            json_str: JSON-String mit Lieferungsdaten

        Returns:
            Delivery-Objekt
        """
        data = json.loads(json_str)
        return cls.from_dict(data)

    def __str__(self) -> str:
        """String-Repräsentation."""
        return f"Delivery(id='{self.id}', supplier='{self.supplier}', status='{self.status}', progress={self.received_packages}/{self.expected_packages})"

    def __repr__(self) -> str:
        """Debug-Repräsentation."""
        return (f"Delivery(id='{self.id}', supplier='{self.supplier}', "
                f"expected_packages={self.expected_packages}, "
                f"received_packages={self.received_packages}, "
                f"status='{self.status}')")

    def __eq__(self, other) -> bool:
        """Gleichheitsvergleich."""
        if not isinstance(other, Delivery):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash-Funktion für Sets/Dicts."""
        return hash(self.id)