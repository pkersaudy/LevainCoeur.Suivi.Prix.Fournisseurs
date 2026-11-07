"""Modele de donnee commun + interface d'extraction par fournisseur."""
from __future__ import annotations
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, List


@dataclass
class LigneFacture:
    """Une ligne d'article extraite d'une facture, avant rapprochement."""
    designation: str                      # libelle brut du fournisseur (= futur alias)
    prix_unitaire_ht: float               # prix unitaire HT tel que facture
    unite: str = "kg"                     # unite facturee (kg, L, piece, colis...)
    fournisseur: str = ""
    date_prix: str = ""                   # jj/mm/aaaa
    code_article: Optional[str] = None    # code fournisseur si dispo
    quantite: Optional[float] = None
    montant_ht: Optional[float] = None


@dataclass
class Facture:
    fournisseur: str
    date_prix: str
    numero: Optional[str] = None
    lignes: List[LigneFacture] = field(default_factory=list)


class Extractor(ABC):
    """Chaque fournisseur a son extracteur (Factur-X ou pdfplumber)."""
    nom_fournisseur: str = "Inconnu"

    @abstractmethod
    def peut_traiter(self, pdf_path: Path, texte_apercu: str) -> bool:
        """Retourne True si ce PDF vient bien de ce fournisseur."""

    @abstractmethod
    def extraire(self, pdf_path: Path) -> Facture:
        """Extrait les lignes d'articles (matieres premieres uniquement)."""
