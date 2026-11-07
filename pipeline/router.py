"""Détecte le fournisseur d'un PDF et délègue au bon extracteur."""

from __future__ import annotations

from pathlib import Path

import pdfplumber

from .extractors import EXTRACTEURS, Facture


def _apercu(pdf_path: Path, n_pages: int = 1) -> str:
    try:
        with pdfplumber.open(str(pdf_path)) as pdf:
            return "\n".join((p.extract_text() or "") for p in pdf.pages[:n_pages])
    except Exception:  # noqa: BLE001 : sans aperçu, le nom du fichier peut encore suffire
        return ""


def router_facture(pdf_path: Path) -> Facture:
    apercu = _apercu(pdf_path)
    for ext in EXTRACTEURS:
        try:
            if ext.peut_traiter(pdf_path, apercu):
                return ext.extraire(pdf_path)
        except Exception as e:  # noqa: BLE001 : une facture illisible n'arrête pas le lot
            print(f"  [!] {ext.nom_fournisseur} a echoue sur {pdf_path.name}: {e}")
    raise ValueError(
        f"Aucun extracteur ne reconnait {pdf_path.name} (ajoutez un extracteur dans pipeline/extractors/)."
    )
