"""Utvidelsespunkt for ekstern IAM-katalog (Active Directory, Entra ID, LDAP m.m.).

Backend-plugins kan deklarere capability `iam.directory_provider` i manifestet og
implementere denne ABC-en for synkronisering av personer, grupper og nestede
grupper inn i kjernens tabeller (`users`, `iam_groups`, …).

Kjernen kaller ikke AD direkte — all leverandørspesifikk logikk lever i plugin.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class IamDirectoryProviderPlugin(ABC):
    """Kontrakt for katalogsynk fra ekstern IdP (implementeres i egne plugin-pakker)."""

    @abstractmethod
    def provider_id(self) -> str:
        """Stabil id, f.eks. `freehci.iam.active_directory`."""

    @abstractmethod
    def sync_directory(self, db: Session) -> None:
        """Oppdater lokale IAM-rader ut fra ekstern katalog (implementasjonsspesifikt)."""
