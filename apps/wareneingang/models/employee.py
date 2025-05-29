"""
Mitarbeiter-Modell
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
import json


@dataclass
class Employee:
    """Datenmodell für einen Mitarbeiter."""

    id: int
    rfid_card: str
    first_name: str
    last_name: str
    role: str
    language: str = 'de'
    department: Optional[str] = None
    is_active: bool = True
    email: Optional[str] = None
    phone: Optional[str] = None
    hire_date: Optional[datetime] = None
    last_login: Optional[datetime] = None
    permissions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Wird nach der Initialisierung aufgerufen."""
        # Validierung
        self._validate()

        # Standard-Berechtigungen basierend auf Rolle setzen
        if not self.permissions:
            self.permissions = self._get_default_permissions()

    def _validate(self):
        """Validiert die Mitarbeiterdaten."""
        if not self.first_name or not self.first_name.strip():
            raise ValueError("Vorname ist erforderlich")

        if not self.last_name or not self.last_name.strip():
            raise ValueError("Nachname ist erforderlich")

        if not self.rfid_card or not self.rfid_card.strip():
            raise ValueError("RFID-Karte ist erforderlich")

        if self.role not in ['worker', 'supervisor', 'admin', 'manager']:
            raise ValueError(f"Ungültige Rolle: {self.role}")

        if self.language not in ['de', 'en', 'tr', 'pl']:
            raise ValueError(f"Ungültige Sprache: {self.language}")

        if self.id <= 0:
            raise ValueError("Mitarbeiter-ID muss positiv sein")

    def _get_default_permissions(self) -> List[str]:
        """
        Gibt Standard-Berechtigungen basierend auf der Rolle zurück.

        Returns:
            Liste der Standard-Berechtigungen
        """
        base_permissions = [
            'view_own_profile',
            'change_own_language',
            'view_deliveries'
        ]

        if self.role == 'worker':
            return base_permissions + [
                'scan_packages',
                'register_packages',
                'manual_entry',
                'view_package_list'
            ]

        elif self.role == 'supervisor':
            return base_permissions + [
                'scan_packages',
                'register_packages',
                'manual_entry',
                'view_package_list',
                'create_delivery',
                'finish_delivery',
                'cancel_delivery',
                'view_statistics',
                'edit_packages',
                'delete_packages'
            ]

        elif self.role == 'manager':
            return base_permissions + [
                'scan_packages',
                'register_packages',
                'manual_entry',
                'view_package_list',
                'create_delivery',
                'finish_delivery',
                'cancel_delivery',
                'view_statistics',
                'edit_packages',
                'delete_packages',
                'manage_employees',
                'view_reports',
                'export_data',
                'system_settings'
            ]

        elif self.role == 'admin':
            return ['*']  # Alle Berechtigungen

        return base_permissions

    @property
    def full_name(self) -> str:
        """Gibt den vollständigen Namen zurück."""
        return f"{self.first_name} {self.last_name}"

    @property
    def initials(self) -> str:
        """Gibt die Initialen zurück."""
        return f"{self.first_name[0]}{self.last_name[0]}".upper()

    @property
    def is_supervisor(self) -> bool:
        """Prüft ob der Mitarbeiter ein Supervisor ist."""
        return self.role.lower() == 'supervisor'

    @property
    def is_manager(self) -> bool:
        """Prüft ob der Mitarbeiter ein Manager ist."""
        return self.role.lower() == 'manager'

    @property
    def is_admin(self) -> bool:
        """Prüft ob der Mitarbeiter ein Administrator ist."""
        return self.role.lower() == 'admin'

    @property
    def display_name(self) -> str:
        """Gibt den Anzeigenamen zurück."""
        role_translations = {
            'worker': {'de': 'Mitarbeiter', 'en': 'Worker', 'tr': 'Çalışan', 'pl': 'Pracownik'},
            'supervisor': {'de': 'Supervisor', 'en': 'Supervisor', 'tr': 'Süpervizör', 'pl': 'Kierownik'},
            'manager': {'de': 'Manager', 'en': 'Manager', 'tr': 'Müdür', 'pl': 'Menedżer'},
            'admin': {'de': 'Administrator', 'en': 'Administrator', 'tr': 'Yönetici', 'pl': 'Administrator'}
        }

        role_text = role_translations.get(self.role, {}).get(self.language, self.role.title())
        return f"{self.full_name} ({role_text})"

    @property
    def role_level(self) -> int:
        """Gibt die Berechtigungsstufe der Rolle zurück."""
        role_levels = {
            'worker': 1,
            'supervisor': 2,
            'manager': 3,
            'admin': 4
        }
        return role_levels.get(self.role, 0)

    @property
    def days_since_hire(self) -> Optional[int]:
        """Berechnet die Tage seit Einstellung."""
        if not self.hire_date:
            return None

        delta = datetime.now() - self.hire_date
        return delta.days

    @property
    def employment_duration_text(self) -> Optional[str]:
        """Gibt die Beschäftigungsdauer als Text zurück."""
        days = self.days_since_hire
        if not days:
            return None

        years = days // 365
        months = (days % 365) // 30

        if years > 0:
            if months > 0:
                return f"{years} Jahre, {months} Monate"
            else:
                return f"{years} Jahre"
        elif months > 0:
            return f"{months} Monate"
        else:
            return f"{days} Tage"

    def has_permission(self, permission: str) -> bool:
        """
        Prüft ob der Mitarbeiter eine bestimmte Berechtigung hat.

        Args:
            permission: Zu prüfende Berechtigung

        Returns:
            True wenn berechtigt, False sonst
        """
        if not self.is_active:
            return False

        # Admin hat alle Berechtigungen
        if '*' in self.permissions:
            return True

        return permission in self.permissions

    def add_permission(self, permission: str) -> bool:
        """
        Fügt eine Berechtigung hinzu.

        Args:
            permission: Hinzuzufügende Berechtigung

        Returns:
            True wenn hinzugefügt, False wenn bereits vorhanden
        """
        if permission not in self.permissions:
            self.permissions.append(permission)
            return True
        return False

    def remove_permission(self, permission: str) -> bool:
        """
        Entfernt eine Berechtigung.

        Args:
            permission: Zu entfernende Berechtigung

        Returns:
            True wenn entfernt, False wenn nicht vorhanden
        """
        if permission in self.permissions:
            self.permissions.remove(permission)
            return True
        return False

    def update_last_login(self) -> None:
        """Aktualisiert den letzten Login-Zeitstempel."""
        self.last_login = datetime.now()
        self.metadata['login_count'] = self.metadata.get('login_count', 0) + 1

    def deactivate(self, reason: Optional[str] = None) -> None:
        """
        Deaktiviert den Mitarbeiter.

        Args:
            reason: Optional - Grund für Deaktivierung
        """
        self.is_active = False
        self.metadata['deactivation_date'] = datetime.now().isoformat()

        if reason:
            self.metadata['deactivation_reason'] = reason

    def activate(self) -> None:
        """Aktiviert den Mitarbeiter wieder."""
        self.is_active = True
        self.metadata['reactivation_date'] = datetime.now().isoformat()

        # Entferne Deaktivierungsdaten
        self.metadata.pop('deactivation_date', None)
        self.metadata.pop('deactivation_reason', None)

    def change_role(self, new_role: str, update_permissions: bool = True) -> None:
        """
        Ändert die Rolle des Mitarbeiters.

        Args:
            new_role: Neue Rolle
            update_permissions: Berechtigungen automatisch aktualisieren
        """
        old_role = self.role
        self.role = new_role

        if update_permissions:
            self.permissions = self._get_default_permissions()

        # Metadaten aktualisieren
        self.metadata['role_history'] = self.metadata.get('role_history', [])
        self.metadata['role_history'].append({
            'old_role': old_role,
            'new_role': new_role,
            'change_date': datetime.now().isoformat(),
            'permissions_updated': update_permissions
        })

    def get_profile_summary(self) -> Dict[str, Any]:
        """
        Gibt eine Profilzusammenfassung zurück.

        Returns:
            Dictionary mit Profildaten
        """
        return {
            'id': self.id,
            'name': self.full_name,
            'initials': self.initials,
            'role': self.role,
            'role_level': self.role_level,
            'department': self.department,
            'language': self.language,
            'is_active': self.is_active,
            'employment_duration': self.employment_duration_text,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'permission_count': len(self.permissions),
            'is_supervisor_or_higher': self.role_level >= 2
        }

    def can_manage_employee(self, other_employee: 'Employee') -> bool:
        """
        Prüft ob dieser Mitarbeiter einen anderen verwalten kann.

        Args:
            other_employee: Zu verwaltender Mitarbeiter

        Returns:
            True wenn verwaltbar, False sonst
        """
        # Nicht aktive Mitarbeiter können niemanden verwalten
        if not self.is_active:
            return False

        # Admin kann alle verwalten
        if self.is_admin:
            return True

        # Manager können alle außer Admins verwalten
        if self.is_manager:
            return not other_employee.is_admin

        # Supervisor können nur Worker verwalten
        if self.is_supervisor:
            return other_employee.role == 'worker'

        # Worker können niemanden verwalten
        return False

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary für Serialisierung."""
        return {
            'id': self.id,
            'rfid_card': self.rfid_card,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role,
            'language': self.language,
            'department': self.department,
            'is_active': self.is_active,
            'email': self.email,
            'phone': self.phone,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'permissions': self.permissions.copy(),
            'metadata': self.metadata.copy()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Employee':
        """
        Erstellt Employee-Objekt aus Dictionary.

        Args:
            data: Dictionary mit Mitarbeiterdaten

        Returns:
            Employee-Objekt
        """
        employee = cls(
            id=data['id'],
            rfid_card=data['rfid_card'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=data['role'],
            language=data.get('language', 'de'),
            department=data.get('department'),
            is_active=data.get('is_active', True),
            email=data.get('email'),
            phone=data.get('phone'),
            permissions=data.get('permissions', []),
            metadata=data.get('metadata', {})
        )

        # Zeitstempel parsen
        if data.get('hire_date'):
            employee.hire_date = datetime.fromisoformat(data['hire_date'])
        if data.get('last_login'):
            employee.last_login = datetime.fromisoformat(data['last_login'])

        return employee

    def to_json(self) -> str:
        """Konvertiert zu JSON-String."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'Employee':
        """
        Erstellt Employee-Objekt aus JSON-String.

        Args:
            json_str: JSON-String mit Mitarbeiterdaten

        Returns:
            Employee-Objekt
        """
        data = json.loads(json_str)
        return cls.from_dict(data)

    def __str__(self) -> str:
        """String-Repräsentation."""
        return f"Employee(id={self.id}, name='{self.full_name}', role='{self.role}')"

    def __repr__(self) -> str:
        """Debug-Repräsentation."""
        return (f"Employee(id={self.id}, rfid_card='{self.rfid_card}', "
                f"first_name='{self.first_name}', last_name='{self.last_name}', "
                f"role='{self.role}', is_active={self.is_active})")

    def __eq__(self, other) -> bool:
        """Gleichheitsvergleich."""
        if not isinstance(other, Employee):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash-Funktion für Sets/Dicts."""
        return hash(self.id)

    def __lt__(self, other) -> bool:
        """Kleiner-als-Vergleich für Sortierung."""
        if not isinstance(other, Employee):
            return NotImplemented

        # Sortiere nach Rolle (höhere Rollen zuerst), dann nach Namen
        if self.role_level != other.role_level:
            return self.role_level > other.role_level

        return self.full_name < other.full_name