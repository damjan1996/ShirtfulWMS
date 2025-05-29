"""
Paket-Modell
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
import json
import re


@dataclass
class Package:
    """Datenmodell für ein Paket."""

    package_id: str
    order_id: Optional[str] = None
    customer: Optional[str] = None
    item_count: int = 1
    priority: str = "Normal"
    notes: Optional[str] = None
    status: str = "received"
    delivery_id: Optional[str] = None
    received_time: Optional[datetime] = None
    employee_id: Optional[int] = None
    tracking_number: Optional[str] = None
    weight: Optional[float] = None
    dimensions: Optional[Dict[str, float]] = None
    qr_data: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Wird nach der Initialisierung aufgerufen."""
        if self.received_time is None:
            self.received_time = datetime.now()

        if self.dimensions is None:
            self.dimensions = {}

        # Validierung
        self._validate()

        # Auto-Tags setzen
        self._set_auto_tags()

    def _validate(self):
        """Validiert die Paketdaten."""
        if not self.package_id or not self.package_id.strip():
            raise ValueError("Paket-ID ist erforderlich")

        if self.item_count <= 0:
            raise ValueError("Artikelanzahl muss positiv sein")

        if self.priority not in ["Normal", "Hoch", "Express"]:
            raise ValueError(f"Ungültige Priorität: {self.priority}")

        if self.status not in ["received", "processing", "quality_check", "ready", "shipped", "returned"]:
            raise ValueError(f"Ungültiger Status: {self.status}")

        if self.weight is not None and self.weight < 0:
            raise ValueError("Gewicht kann nicht negativ sein")

        # Validiere Paket-ID Format
        if not re.match(r'^[A-Za-z0-9\-_]+$', self.package_id):
            raise ValueError("Paket-ID enthält ungültige Zeichen")

    def _set_auto_tags(self):
        """Setzt automatische Tags basierend auf Paketattributen."""
        auto_tags = []

        # Prioritäts-Tags
        if self.is_express:
            auto_tags.append("express")
        elif self.is_high_priority:
            auto_tags.append("high_priority")

        # Größen-Tags
        if self.is_oversized:
            auto_tags.append("oversized")
        elif self.is_heavy:
            auto_tags.append("heavy")

        # Status-Tags
        if self.is_delayed:
            auto_tags.append("delayed")

        # Füge Auto-Tags hinzu (ohne Duplikate)
        for tag in auto_tags:
            if tag not in self.tags:
                self.tags.append(tag)

    @property
    def is_express(self) -> bool:
        """Prüft ob es sich um ein Express-Paket handelt."""
        return self.priority.lower() == "express"

    @property
    def is_high_priority(self) -> bool:
        """Prüft ob es sich um ein Paket mit hoher Priorität handelt."""
        return self.priority.lower() in ["hoch", "express"]

    @property
    def is_normal_priority(self) -> bool:
        """Prüft ob es sich um ein Paket mit normaler Priorität handelt."""
        return self.priority.lower() == "normal"

    @property
    def priority_level(self) -> int:
        """Gibt die Prioritätsstufe als Zahl zurück (höher = wichtiger)."""
        priority_levels = {
            "normal": 1,
            "hoch": 2,
            "express": 3
        }
        return priority_levels.get(self.priority.lower(), 1)

    @property
    def is_received(self) -> bool:
        """Prüft ob das Paket empfangen wurde."""
        return self.status == "received"

    @property
    def is_processing(self) -> bool:
        """Prüft ob das Paket in Bearbeitung ist."""
        return self.status == "processing"

    @property
    def is_ready(self) -> bool:
        """Prüft ob das Paket bereit ist."""
        return self.status == "ready"

    @property
    def is_shipped(self) -> bool:
        """Prüft ob das Paket versendet wurde."""
        return self.status == "shipped"

    @property
    def age_hours(self) -> float:
        """Berechnet das Alter des Pakets in Stunden."""
        if not self.received_time:
            return 0.0

        delta = datetime.now() - self.received_time
        return delta.total_seconds() / 3600.0

    @property
    def age_days(self) -> float:
        """Berechnet das Alter des Pakets in Tagen."""
        return self.age_hours / 24.0

    @property
    def is_delayed(self) -> bool:
        """Prüft ob das Paket verspätet ist (basierend auf Priorität)."""
        age_hours = self.age_hours

        if self.is_express:
            return age_hours > 2  # Express: max 2 Stunden
        elif self.is_high_priority:
            return age_hours > 4  # Hoch: max 4 Stunden
        else:
            return age_hours > 24  # Normal: max 24 Stunden

    @property
    def expected_completion_time(self) -> datetime:
        """Berechnet die erwartete Fertigstellungszeit."""
        if not self.received_time:
            return datetime.now()

        if self.is_express:
            return self.received_time + timedelta(hours=2)
        elif self.is_high_priority:
            return self.received_time + timedelta(hours=4)
        else:
            return self.received_time + timedelta(hours=24)

    @property
    def time_until_deadline(self) -> timedelta:
        """Berechnet die Zeit bis zur Deadline."""
        return self.expected_completion_time - datetime.now()

    @property
    def is_overdue(self) -> bool:
        """Prüft ob das Paket überfällig ist."""
        return datetime.now() > self.expected_completion_time

    @property
    def volume(self) -> Optional[float]:
        """Berechnet das Volumen des Pakets (wenn Dimensionen vorhanden)."""
        if not self.dimensions:
            return None

        length = self.dimensions.get('length')
        width = self.dimensions.get('width')
        height = self.dimensions.get('height')

        if all([length, width, height]):
            return length * width * height

        return None

    @property
    def is_heavy(self) -> bool:
        """Prüft ob das Paket schwer ist (>10kg)."""
        return self.weight is not None and self.weight > 10.0

    @property
    def is_oversized(self) -> bool:
        """Prüft ob das Paket übergroß ist."""
        volume = self.volume
        return volume is not None and volume > 100000  # >100L

    @property
    def display_size(self) -> str:
        """Gibt eine lesbare Größenangabe zurück."""
        if not self.dimensions:
            return "Unbekannt"

        length = self.dimensions.get('length')
        width = self.dimensions.get('width')
        height = self.dimensions.get('height')

        if all([length, width, height]):
            return f"{length}×{width}×{height} cm"

        parts = []
        if length:
            parts.append(f"L:{length}cm")
        if width:
            parts.append(f"B:{width}cm")
        if height:
            parts.append(f"H:{height}cm")

        return ", ".join(parts) if parts else "Unbekannt"

    @property
    def urgency_score(self) -> float:
        """Berechnet einen Dringlichkeitswert (0-100)."""
        base_score = self.priority_level * 10  # 10, 20, 30

        # Zeit-Faktor
        age_hours = self.age_hours
        expected_hours = {
            "express": 2,
            "hoch": 4,
            "normal": 24
        }.get(self.priority.lower(), 24)

        time_factor = (age_hours / expected_hours) * 50

        # Status-Faktor
        status_factor = {
            "received": 0,
            "processing": 10,
            "quality_check": 20,
            "ready": 5,
            "shipped": 0,
            "returned": 30
        }.get(self.status, 0)

        return min(100, base_score + time_factor + status_factor)

    def update_status(self, new_status: str, note: Optional[str] = None) -> None:
        """
        Aktualisiert den Status des Pakets.

        Args:
            new_status: Neuer Status
            note: Optional - Notiz zur Statusänderung
        """
        old_status = self.status
        self.status = new_status

        # Status-Historie in Metadaten speichern
        status_history = self.metadata.get('status_history', [])
        status_history.append({
            'from_status': old_status,
            'to_status': new_status,
            'timestamp': datetime.now().isoformat(),
            'note': note
        })
        self.metadata['status_history'] = status_history

        # Auto-Tags aktualisieren
        self._set_auto_tags()

    def set_dimensions(self, length: float, width: float, height: float) -> None:
        """
        Setzt die Abmessungen des Pakets.

        Args:
            length: Länge in cm
            width: Breite in cm
            height: Höhe in cm
        """
        self.dimensions = {
            'length': length,
            'width': width,
            'height': height
        }

        # Auto-Tags aktualisieren
        self._set_auto_tags()

    def add_tag(self, tag: str) -> bool:
        """
        Fügt ein Tag hinzu.

        Args:
            tag: Hinzuzufügendes Tag

        Returns:
            True wenn hinzugefügt, False wenn bereits vorhanden
        """
        tag = tag.lower().strip()
        if tag and tag not in self.tags:
            self.tags.append(tag)
            return True
        return False

    def remove_tag(self, tag: str) -> bool:
        """
        Entfernt ein Tag.

        Args:
            tag: Zu entfernendes Tag

        Returns:
            True wenn entfernt, False wenn nicht vorhanden
        """
        tag = tag.lower().strip()
        if tag in self.tags:
            self.tags.remove(tag)
            return True
        return False

    def has_tag(self, tag: str) -> bool:
        """
        Prüft ob das Paket ein bestimmtes Tag hat.

        Args:
            tag: Zu prüfendes Tag

        Returns:
            True wenn vorhanden, False sonst
        """
        return tag.lower().strip() in self.tags

    def add_note(self, note: str) -> None:
        """
        Fügt eine Notiz zum Paket hinzu.

        Args:
            note: Hinzuzufügende Notiz
        """
        timestamp = datetime.now().strftime('%H:%M:%S')
        new_note = f"[{timestamp}] {note}"

        if self.notes:
            self.notes += f"\n{new_note}"
        else:
            self.notes = new_note

    def get_status_duration(self, status: str) -> Optional[float]:
        """
        Berechnet wie lange das Paket in einem bestimmten Status war.

        Args:
            status: Status für den die Dauer berechnet werden soll

        Returns:
            Dauer in Stunden oder None wenn Status nicht gefunden
        """
        status_history = self.metadata.get('status_history', [])

        enter_time = None
        exit_time = None

        for i, entry in enumerate(status_history):
            if entry['to_status'] == status:
                enter_time = datetime.fromisoformat(entry['timestamp'])

                # Suche Exit-Zeit
                if i + 1 < len(status_history):
                    exit_time = datetime.fromisoformat(status_history[i + 1]['timestamp'])
                elif self.status == status:
                    exit_time = datetime.now()

                break

        if enter_time and exit_time:
            delta = exit_time - enter_time
            return delta.total_seconds() / 3600.0

        return None

    def get_summary(self) -> Dict[str, Any]:
        """
        Gibt eine Zusammenfassung des Pakets zurück.

        Returns:
            Dictionary mit Zusammenfassungsdaten
        """
        return {
            'package_id': self.package_id,
            'order_id': self.order_id,
            'customer': self.customer,
            'status': self.status,
            'priority': self.priority,
            'priority_level': self.priority_level,
            'age_hours': round(self.age_hours, 1),
            'is_delayed': self.is_delayed,
            'is_overdue': self.is_overdue,
            'urgency_score': round(self.urgency_score, 1),
            'item_count': self.item_count,
            'weight': self.weight,
            'display_size': self.display_size,
            'tag_count': len(self.tags),
            'has_notes': bool(self.notes)
        }

    def matches_filter(self, **filters) -> bool:
        """
        Prüft ob das Paket bestimmte Filter erfüllt.

        Args:
            **filters: Filter-Kriterien

        Returns:
            True wenn alle Filter erfüllt sind, False sonst
        """
        for key, value in filters.items():
            if key == 'priority' and self.priority != value:
                return False
            elif key == 'status' and self.status != value:
                return False
            elif key == 'customer' and value.lower() not in (self.customer or '').lower():
                return False
            elif key == 'order_id' and value.lower() not in (self.order_id or '').lower():
                return False
            elif key == 'delivery_id' and self.delivery_id != value:
                return False
            elif key == 'employee_id' and self.employee_id != value:
                return False
            elif key == 'is_delayed' and self.is_delayed != value:
                return False
            elif key == 'is_overdue' and self.is_overdue != value:
                return False
            elif key == 'has_tag' and not self.has_tag(value):
                return False
            elif key == 'min_age_hours' and self.age_hours < value:
                return False
            elif key == 'max_age_hours' and self.age_hours > value:
                return False

        return True

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary für Serialisierung."""
        return {
            'package_id': self.package_id,
            'order_id': self.order_id,
            'customer': self.customer,
            'item_count': self.item_count,
            'priority': self.priority,
            'notes': self.notes,
            'status': self.status,
            'delivery_id': self.delivery_id,
            'received_time': self.received_time.isoformat() if self.received_time else None,
            'employee_id': self.employee_id,
            'tracking_number': self.tracking_number,
            'weight': self.weight,
            'dimensions': self.dimensions.copy() if self.dimensions else None,
            'qr_data': self.qr_data,
            'tags': self.tags.copy(),
            'metadata': self.metadata.copy()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Package':
        """
        Erstellt Package-Objekt aus Dictionary.

        Args:
            data: Dictionary mit Paketdaten

        Returns:
            Package-Objekt
        """
        package = cls(
            package_id=data['package_id'],
            order_id=data.get('order_id'),
            customer=data.get('customer'),
            item_count=data.get('item_count', 1),
            priority=data.get('priority', 'Normal'),
            notes=data.get('notes'),
            status=data.get('status', 'received'),
            delivery_id=data.get('delivery_id'),
            employee_id=data.get('employee_id'),
            tracking_number=data.get('tracking_number'),
            weight=data.get('weight'),
            dimensions=data.get('dimensions'),
            qr_data=data.get('qr_data'),
            tags=data.get('tags', []),
            metadata=data.get('metadata', {})
        )

        # Zeitstempel parsen
        if data.get('received_time'):
            package.received_time = datetime.fromisoformat(data['received_time'])

        return package

    def to_json(self) -> str:
        """Konvertiert zu JSON-String."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'Package':
        """
        Erstellt Package-Objekt aus JSON-String.

        Args:
            json_str: JSON-String mit Paketdaten

        Returns:
            Package-Objekt
        """
        data = json.loads(json_str)
        return cls.from_dict(data)

    def __str__(self) -> str:
        """String-Repräsentation."""
        return f"Package(id='{self.package_id}', status='{self.status}', priority='{self.priority}')"

    def __repr__(self) -> str:
        """Debug-Repräsentation."""
        return (f"Package(package_id='{self.package_id}', order_id='{self.order_id}', "
                f"customer='{self.customer}', status='{self.status}', priority='{self.priority}')")

    def __eq__(self, other) -> bool:
        """Gleichheitsvergleich."""
        if not isinstance(other, Package):
            return False
        return self.package_id == other.package_id

    def __hash__(self) -> int:
        """Hash-Funktion für Sets/Dicts."""
        return hash(self.package_id)

    def __lt__(self, other) -> bool:
        """Kleiner-als-Vergleich für Sortierung."""
        if not isinstance(other, Package):
            return NotImplemented

        # Sortiere nach Priorität (höhere Priorität zuerst), dann nach Alter
        if self.priority_level != other.priority_level:
            return self.priority_level > other.priority_level

        return self.received_time < other.received_time