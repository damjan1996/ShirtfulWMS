"""
Authentifizierungs-Service für die Wareneingangsstation.
"""

from typing import Optional, Dict, Any, List
import logging
from datetime import datetime, timedelta

from ..models.employee import Employee
from ..config.constants import TEST_EMPLOYEES


class AuthService:
    """Service für Authentifizierung und Benutzerverwaltung."""

    def __init__(self):
        self.logger = logging.getLogger('wareneingang.auth')
        self.current_user: Optional[Employee] = None
        self.login_attempts: Dict[str, List[datetime]] = {}
        self.max_login_attempts = 5
        self.lockout_duration_minutes = 15
        self.session_timeout_minutes = 60
        self.last_activity: Optional[datetime] = None

        # Cache für Mitarbeiter-Daten
        self._employee_cache: Dict[str, Employee] = {}
        self._load_test_employees()

        self.logger.info("AuthService initialisiert")

    def _load_test_employees(self):
        """Lädt Test-Mitarbeiter in den Cache."""
        for emp_data in TEST_EMPLOYEES:
            try:
                employee = Employee.from_dict(emp_data)
                self._employee_cache[employee.rfid_card] = employee
                self.logger.debug(f"Test-Mitarbeiter geladen: {employee.full_name}")
            except Exception as e:
                self.logger.error(f"Fehler beim Laden von Test-Mitarbeiter: {e}")

    def _is_account_locked(self, identifier: str) -> bool:
        """
        Prüft ob ein Account gesperrt ist.

        Args:
            identifier: RFID-Karte oder Benutzername

        Returns:
            True wenn gesperrt, False sonst
        """
        if identifier not in self.login_attempts:
            return False

        attempts = self.login_attempts[identifier]

        # Alte Versuche entfernen (älter als Sperrzeit)
        cutoff_time = datetime.now() - timedelta(minutes=self.lockout_duration_minutes)
        self.login_attempts[identifier] = [
            attempt for attempt in attempts if attempt > cutoff_time
        ]

        # Prüfen ob zu viele Versuche
        return len(self.login_attempts[identifier]) >= self.max_login_attempts

    def _record_login_attempt(self, identifier: str, success: bool):
        """
        Zeichnet einen Login-Versuch auf.

        Args:
            identifier: RFID-Karte oder Benutzername
            success: True bei erfolgreichem Login, False bei Fehlschlag
        """
        if success:
            # Bei erfolgreichem Login alle Versuche löschen
            self.login_attempts.pop(identifier, None)
        else:
            # Fehlgeschlagenen Versuch aufzeichnen
            if identifier not in self.login_attempts:
                self.login_attempts[identifier] = []

            self.login_attempts[identifier].append(datetime.now())

            # Alte Versuche bereinigen
            cutoff_time = datetime.now() - timedelta(minutes=self.lockout_duration_minutes)
            self.login_attempts[identifier] = [
                attempt for attempt in self.login_attempts[identifier]
                if attempt > cutoff_time
            ]

    def authenticate_rfid(self, rfid_tag: str) -> Optional[Employee]:
        """
        Authentifiziert einen Benutzer über RFID.

        Args:
            rfid_tag: RFID-Tag ID

        Returns:
            Employee-Objekt bei erfolgreicher Authentifizierung, sonst None
        """
        self.logger.info(f"RFID-Authentifizierung für Tag: {rfid_tag}")

        # Prüfe Account-Sperrung
        if self._is_account_locked(rfid_tag):
            remaining_time = self._get_remaining_lockout_time(rfid_tag)
            self.logger.warning(f"Account gesperrt für RFID {rfid_tag}, verbleibende Zeit: {remaining_time} Minuten")
            return None

        # In echter Implementierung: Datenbankabfrage
        # Hier: Simulation mit Test-Mitarbeitern und Cache
        employee = self._employee_cache.get(rfid_tag)

        if employee and employee.is_active:
            # Erfolgreiche Authentifizierung
            self._record_login_attempt(rfid_tag, True)
            self.current_user = employee
            self.last_activity = datetime.now()
            employee.update_last_login()

            self.logger.info(f"Erfolgreiche RFID-Authentifizierung: {employee.full_name}")
            return employee
        else:
            # Fehlgeschlagene Authentifizierung
            self._record_login_attempt(rfid_tag, False)

            if employee and not employee.is_active:
                self.logger.warning(f"RFID-Tag für inaktiven Mitarbeiter: {rfid_tag}")
            else:
                self.logger.warning(f"RFID-Tag nicht gefunden: {rfid_tag}")

            return None

    def authenticate_manual(self, employee_name: str) -> Optional[Employee]:
        """
        Manuelle Authentifizierung über Namen.

        Args:
            employee_name: Name des Mitarbeiters

        Returns:
            Employee-Objekt bei erfolgreicher Authentifizierung, sonst None
        """
        self.logger.info(f"Manuelle Authentifizierung für: {employee_name}")

        # Prüfe Account-Sperrung
        if self._is_account_locked(employee_name):
            remaining_time = self._get_remaining_lockout_time(employee_name)
            self.logger.warning(f"Account gesperrt für {employee_name}, verbleibende Zeit: {remaining_time} Minuten")
            return None

        # Mapping für Test-Mitarbeiter
        name_mapping = {
            "Max Mustermann (Supervisor)": 0,
            "Anna Schmidt (Worker)": 1,
            "Test User (Worker)": 2,
            "Manual Login (Worker)": 3
        }

        if employee_name in name_mapping:
            emp_data = TEST_EMPLOYEES[name_mapping[employee_name]]
            employee = Employee.from_dict(emp_data)

            if employee.is_active:
                # Erfolgreiche Authentifizierung
                self._record_login_attempt(employee_name, True)
                self.current_user = employee
                self.last_activity = datetime.now()
                employee.update_last_login()

                self.logger.info(f"Erfolgreiche manuelle Authentifizierung: {employee.full_name}")
                return employee
            else:
                self.logger.warning(f"Manueller Login für inaktiven Mitarbeiter: {employee_name}")

        # Fehlgeschlagene Authentifizierung
        self._record_login_attempt(employee_name, False)
        self.logger.warning(f"Mitarbeiter nicht gefunden: {employee_name}")
        return None

    def _get_remaining_lockout_time(self, identifier: str) -> int:
        """
        Berechnet die verbleibende Sperrzeit in Minuten.

        Args:
            identifier: RFID-Karte oder Benutzername

        Returns:
            Verbleibende Sperrzeit in Minuten
        """
        if identifier not in self.login_attempts:
            return 0

        attempts = self.login_attempts[identifier]
        if not attempts:
            return 0

        oldest_attempt = min(attempts)
        unlock_time = oldest_attempt + timedelta(minutes=self.lockout_duration_minutes)
        remaining = unlock_time - datetime.now()

        return max(0, int(remaining.total_seconds() / 60))

    def get_current_user(self) -> Optional[Employee]:
        """Gibt den aktuell angemeldeten Benutzer zurück."""
        # Prüfe Session-Timeout
        if self.current_user and self._is_session_expired():
            self.logger.info(f"Session-Timeout für Benutzer: {self.current_user.full_name}")
            self.logout()

        return self.current_user

    def _is_session_expired(self) -> bool:
        """Prüft ob die Session abgelaufen ist."""
        if not self.last_activity:
            return False

        session_duration = datetime.now() - self.last_activity
        return session_duration.total_seconds() > (self.session_timeout_minutes * 60)

    def update_activity(self):
        """Aktualisiert die letzte Aktivitätszeit (Session-Management)."""
        if self.current_user:
            self.last_activity = datetime.now()

    def logout(self):
        """Meldet den aktuellen Benutzer ab."""
        if self.current_user:
            self.logger.info(f"Benutzer abgemeldet: {self.current_user.full_name}")

            # Session-Dauer berechnen
            if self.last_activity:
                session_duration = datetime.now() - self.last_activity
                self.logger.debug(f"Session-Dauer: {session_duration}")

            self.current_user = None
            self.last_activity = None

    def is_authenticated(self) -> bool:
        """Prüft ob ein Benutzer angemeldet ist."""
        return self.get_current_user() is not None

    def has_permission(self, permission: str) -> bool:
        """
        Prüft ob der aktuelle Benutzer eine bestimmte Berechtigung hat.

        Args:
            permission: Zu prüfende Berechtigung

        Returns:
            True wenn berechtigt, sonst False
        """
        current_user = self.get_current_user()
        if not current_user:
            return False

        # Aktivität aktualisieren
        self.update_activity()

        return current_user.has_permission(permission)

    def require_permission(self, permission: str) -> bool:
        """
        Wirft Exception wenn Berechtigung nicht vorhanden.

        Args:
            permission: Erforderliche Berechtigung

        Returns:
            True wenn berechtigt

        Raises:
            PermissionError: Wenn Berechtigung fehlt
        """
        if not self.is_authenticated():
            raise PermissionError("Nicht angemeldet")

        if not self.has_permission(permission):
            raise PermissionError(f"Berechtigung '{permission}' erforderlich")

        return True

    def get_user_permissions(self) -> List[str]:
        """
        Gibt alle Berechtigungen des aktuellen Benutzers zurück.

        Returns:
            Liste der Berechtigungen
        """
        current_user = self.get_current_user()
        if not current_user:
            return []

        return current_user.permissions.copy()

    def get_login_statistics(self) -> Dict[str, Any]:
        """
        Gibt Login-Statistiken zurück.

        Returns:
            Dictionary mit Statistiken
        """
        stats = {
            'current_user': self.current_user.full_name if self.current_user else None,
            'is_authenticated': self.is_authenticated(),
            'session_duration_minutes': 0,
            'failed_attempts_today': 0,
            'locked_accounts': 0,
            'total_employees': len(self._employee_cache)
        }

        # Session-Dauer berechnen
        if self.current_user and self.last_activity:
            # Hier sollte die Login-Zeit gespeichert werden, nicht last_activity
            # Für Demonstration verwenden wir last_activity
            session_duration = datetime.now() - self.last_activity
            stats['session_duration_minutes'] = int(session_duration.total_seconds() / 60)

        # Fehlgeschlagene Versuche heute
        today = datetime.now().date()
        for attempts in self.login_attempts.values():
            stats['failed_attempts_today'] += len([
                attempt for attempt in attempts
                if attempt.date() == today
            ])

        # Gesperrte Accounts
        for identifier in self.login_attempts.keys():
            if self._is_account_locked(identifier):
                stats['locked_accounts'] += 1

        return stats

    def unlock_account(self, identifier: str) -> bool:
        """
        Entsperrt einen Account (Admin-Funktion).

        Args:
            identifier: RFID-Karte oder Benutzername

        Returns:
            True wenn entsperrt, False wenn nicht gefunden
        """
        if not self.has_permission('manage_users'):
            raise PermissionError("Berechtigung zum Verwalten von Benutzern erforderlich")

        if identifier in self.login_attempts:
            del self.login_attempts[identifier]
            self.logger.info(f"Account entsperrt: {identifier}")
            return True

        return False

    def get_employee_by_id(self, employee_id: int) -> Optional[Employee]:
        """
        Holt einen Mitarbeiter anhand der ID.

        Args:
            employee_id: Mitarbeiter-ID

        Returns:
            Employee-Objekt oder None wenn nicht gefunden
        """
        for employee in self._employee_cache.values():
            if employee.id == employee_id:
                return employee
        return None

    def get_employee_by_rfid(self, rfid_card: str) -> Optional[Employee]:
        """
        Holt einen Mitarbeiter anhand der RFID-Karte.

        Args:
            rfid_card: RFID-Karte

        Returns:
            Employee-Objekt oder None wenn nicht gefunden
        """
        return self._employee_cache.get(rfid_card)

    def get_all_employees(self) -> List[Employee]:
        """
        Gibt alle Mitarbeiter zurück.

        Returns:
            Liste aller Mitarbeiter
        """
        if not self.has_permission('view_employees'):
            raise PermissionError("Berechtigung zum Anzeigen von Mitarbeitern erforderlich")

        return list(self._employee_cache.values())

    def add_employee(self, employee: Employee) -> bool:
        """
        Fügt einen neuen Mitarbeiter hinzu.

        Args:
            employee: Hinzuzufügender Mitarbeiter

        Returns:
            True wenn hinzugefügt, False bei Fehler
        """
        if not self.has_permission('manage_employees'):
            raise PermissionError("Berechtigung zum Verwalten von Mitarbeitern erforderlich")

        try:
            # Prüfe auf Duplikate
            if employee.rfid_card in self._employee_cache:
                self.logger.warning(f"RFID-Karte bereits vorhanden: {employee.rfid_card}")
                return False

            # Prüfe ID-Konflikte
            for existing in self._employee_cache.values():
                if existing.id == employee.id:
                    self.logger.warning(f"Mitarbeiter-ID bereits vorhanden: {employee.id}")
                    return False

            self._employee_cache[employee.rfid_card] = employee
            self.logger.info(f"Mitarbeiter hinzugefügt: {employee.full_name}")
            return True

        except Exception as e:
            self.logger.error(f"Fehler beim Hinzufügen von Mitarbeiter: {e}")
            return False

    def update_employee(self, employee: Employee) -> bool:
        """
        Aktualisiert einen Mitarbeiter.

        Args:
            employee: Zu aktualisierender Mitarbeiter

        Returns:
            True wenn aktualisiert, False bei Fehler
        """
        if not self.has_permission('manage_employees'):
            raise PermissionError("Berechtigung zum Verwalten von Mitarbeitern erforderlich")

        try:
            # Prüfe ob Mitarbeiter existiert
            if employee.rfid_card not in self._employee_cache:
                self.logger.warning(f"Mitarbeiter nicht gefunden: {employee.rfid_card}")
                return False

            self._employee_cache[employee.rfid_card] = employee
            self.logger.info(f"Mitarbeiter aktualisiert: {employee.full_name}")
            return True

        except Exception as e:
            self.logger.error(f"Fehler beim Aktualisieren von Mitarbeiter: {e}")
            return False

    def delete_employee(self, rfid_card: str) -> bool:
        """
        Löscht einen Mitarbeiter.

        Args:
            rfid_card: RFID-Karte des zu löschenden Mitarbeiters

        Returns:
            True wenn gelöscht, False bei Fehler
        """
        if not self.has_permission('manage_employees'):
            raise PermissionError("Berechtigung zum Verwalten von Mitarbeitern erforderlich")

        try:
            if rfid_card in self._employee_cache:
                employee = self._employee_cache[rfid_card]
                del self._employee_cache[rfid_card]
                self.logger.info(f"Mitarbeiter gelöscht: {employee.full_name}")
                return True
            else:
                self.logger.warning(f"Mitarbeiter nicht gefunden: {rfid_card}")
                return False

        except Exception as e:
            self.logger.error(f"Fehler beim Löschen von Mitarbeiter: {e}")
            return False