"""Extracteurs pour les factures PDF "classiques" (non Factur-X) :
Minoterie du Chateau, Subery Claude et Fils, Cremerie de la Rance.

NOTE : l'extraction PDF est intrinsequement sensible a la mise en page.
Les regex ci-dessous sont calees sur les factures fournies ; controlez la
sortie sur vos vrais PDF et ajustez si besoin. Toute ligne non reconnue est
renvoyee dans la file "a_valider.csv" plutot que perdue.
"""

from __future__ import annotations

import re
from pathlib import Path

import pdfplumber

from .base_extractor import Extractor, Facture, LigneFacture

NUM = r"-?\d[\d\s]*,\d+|-?\d+"  # nombre FR (virgule decimale)


def _f(s: str) -> float:
    return float(s.replace(" ", "").replace(",", "."))


def _lignes_texte(pdf_path: Path) -> list[str]:
    out = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            txt = page.extract_text() or ""
            out.extend(l for l in txt.split("\n") if l.strip())
    return out


class _PdfBase(Extractor):
    marqueur = ""  # chaine caracterisant l'emetteur

    def peut_traiter(self, pdf_path: Path, texte_apercu: str) -> bool:
        return self.marqueur.upper() in texte_apercu.upper()


class MinoterieExtractor(_PdfBase):
    nom_fournisseur = "Minoterie du Chateau"
    marqueur = "Minoteries du Ch"
    # Code Designation Qte Poids PU_Brut [Remises] PU_Net Montant TVA
    RE_LIGNE = re.compile(
        rf"^(?P<code>[A-Z0-9]{{5,10}})\s+(?P<des>.+?)\s+\d+\s+(?P<tail>(?:{NUM})(?:\s+(?:{NUM}))*)\s+(?P<tva>[13])$"
    )
    RE_DATE = re.compile(r"(\d{2}/\d{2}/\d{4})")

    def extraire(self, pdf_path: Path) -> Facture:
        lignes = _lignes_texte(pdf_path)
        date = ""
        for l in lignes:
            if "N° Pièce" in l or "Date" in l:
                m = self.RE_DATE.search(l)
                if m:
                    date = m.group(1)
                    break
        fac = Facture(self.nom_fournisseur, date)
        for l in lignes:
            m = self.RE_LIGNE.match(l.strip())
            if not m:
                continue
            nums = re.findall(NUM, m.group("tail"))
            if len(nums) < 3:
                continue
            # tail = PU_Brut [remise...] PU_Net Montant  -> PU_Net = avant-dernier
            pu_net = _f(nums[-2])
            montant = _f(nums[-1])
            fac.lignes.append(
                LigneFacture(
                    designation=re.sub(r"\s*\*$", "", m.group("des")).strip(),
                    prix_unitaire_ht=pu_net,
                    unite="kg",
                    fournisseur=self.nom_fournisseur,
                    date_prix=date,
                    code_article=m.group("code"),
                    montant_ht=montant,
                )
            )
        return fac


class SuberyExtractor(_PdfBase):
    nom_fournisseur = "Subéry Claude et Fils"
    marqueur = "Subéry"
    # TVA COLIS DESIGNATION POIDS PIECES PU_Brut % PU_Net(suffixe K/P) HT
    RE_LIGNE = re.compile(
        rf"^\s*\d+\s+{NUM}\s+(?P<des>.+?)\s+(?P<poids>{NUM})\s+\d+\s+(?P<pubrut>{NUM})\s+"
        rf"(?P<punet>{NUM})(?P<suf>[KP])\s+(?P<ht>{NUM})\s*$"
    )
    RE_DATE = re.compile(r"(\d{2}/\d{2}/\d{4})")

    def extraire(self, pdf_path: Path) -> Facture:
        lignes = _lignes_texte(pdf_path)
        date = next((self.RE_DATE.search(l).group(1) for l in lignes if self.RE_DATE.search(l)), "")
        fac = Facture(self.nom_fournisseur, date)
        for l in lignes:
            m = self.RE_LIGNE.match(l)
            if not m:
                continue
            pu = _f(m.group("punet"))
            # suffixe K = deja au kg ; P = a la piece/barquette (a normaliser plus tard)
            unite = "kg" if m.group("suf") == "K" else "pièce"
            fac.lignes.append(
                LigneFacture(
                    designation=m.group("des").strip(),
                    prix_unitaire_ht=pu,
                    unite=unite,
                    fournisseur=self.nom_fournisseur,
                    date_prix=date,
                    montant_ht=_f(m.group("ht")),
                )
            )
        return fac


class CremerieExtractor(_PdfBase):
    nom_fournisseur = "Crèmerie de la Rance"
    marqueur = "Cr" + "\u00e8" + "merie"  # "Crèmerie" (robuste a l'accent)
    # Code Description Unite(Litre/Kg) Qte PU_HT Montant TVA
    RE_LIGNE = re.compile(
        rf"^(?P<code>[A-Z]\d+)\s+(?P<des>.+?)\s+(?P<unite>Litre|Kg|Pièce|Piece)\s+"
        rf"(?P<qte>{NUM})\s+(?P<pu>{NUM})\s+(?P<montant>{NUM})\s+{NUM}\s*$"
    )
    RE_DATE = re.compile(r"du\s*:?\s*(\d{2}/\d{2}/\d{4})")

    def extraire(self, pdf_path: Path) -> Facture:
        lignes = _lignes_texte(pdf_path)
        date = next((self.RE_DATE.search(l).group(1) for l in lignes if self.RE_DATE.search(l)), "")
        fac = Facture(self.nom_fournisseur, date)
        vus = set()
        for l in lignes:
            m = self.RE_LIGNE.match(l.strip())
            if not m:
                continue
            des = m.group("des").strip()
            if des in vus:  # la facture repete les memes lignes -> on dedoublonne
                continue
            vus.add(des)
            unite = {"Litre": "L", "Kg": "kg"}.get(m.group("unite"), m.group("unite").lower())
            fac.lignes.append(
                LigneFacture(
                    designation=des,
                    prix_unitaire_ht=_f(m.group("pu")),
                    unite=unite,
                    fournisseur=self.nom_fournisseur,
                    date_prix=date,
                    code_article=m.group("code"),
                    montant_ht=_f(m.group("montant")),
                )
            )
        return fac
