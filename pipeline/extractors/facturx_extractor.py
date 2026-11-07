"""Extracteur Factur-X : Transgourmet.

Les factures Transgourmet (fichiers 'facturX_..._fx.pdf') sont des PDF hybrides
Factur-X : une facture XML (norme CII / EN16931) est embarquée dans le PDF.
On lit directement ce XML -> AUCUN OCR, aucune heuristique de mise en page.
"""

from __future__ import annotations

import re
from pathlib import Path

from lxml import etree

from .base_extractor import Extractor, Facture, LigneFacture
from .pdf_extractors import _lignes_texte

# Namespaces CII (Cross Industry Invoice)
NS = {
    "rsm": "urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100",
    "ram": "urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100",
    "udt": "urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100",
}

# Ligne d'article du PDF : le code en tête, l'unité facturée juste avant le prix (3 décimales) et le montant.
RE_LIGNE_PDF = re.compile(r"^(?P<code>\d{6})\s.*\s(?P<unite>[A-Z]+)\s+\d+,\d{3}(?:\s+Pr)?\s+-?\d[\d ]*,\d{2}\s+\d{2}$")


def _txt(node, xpath):
    r = node.xpath(xpath, namespaces=NS)
    return r[0].text.strip() if r and r[0].text else None


class FacturXExtractor(Extractor):
    nom_fournisseur = "Transgourmet"

    def peut_traiter(self, pdf_path: Path, texte_apercu: str) -> bool:
        # Nom de fichier Factur-X ou présence du XML embarqué + émetteur Transgourmet
        if "facturx" in pdf_path.name.lower() or "_fx" in pdf_path.name.lower():
            return True
        return "TRANSGOURMET" in texte_apercu.upper()

    def _lire_xml(self, pdf_path: Path) -> bytes:
        # Nécessite la lib 'facturx' : pip install factur-x
        from facturx import get_xml_from_pdf

        # avec check_xsd, la version 7.9 renvoie un booléen à la place du XML
        _, xml_bytes = get_xml_from_pdf(pdf_path.read_bytes(), check_xsd=False)
        return xml_bytes

    def extraire(self, pdf_path: Path) -> Facture:
        root = etree.fromstring(self._lire_xml(pdf_path))

        numero = _txt(root, ".//rsm:ExchangedDocument/ram:ID")
        # date au format 102 (AAAAMMJJ)
        d = _txt(root, ".//rsm:ExchangedDocument/ram:IssueDateTime/udt:DateTimeString")
        date_prix = f"{d[6:8]}/{d[4:6]}/{d[0:4]}" if d and len(d) == 8 else ""

        fac = Facture(fournisseur=self.nom_fournisseur, date_prix=date_prix, numero=numero)
        # le XML porte unitCode="" sur toutes ses lignes : l'unité ne se lit que dans le texte du PDF
        unites_par_code = _unites_par_code(pdf_path)

        for li in root.xpath(".//ram:IncludedSupplyChainTradeLineItem", namespaces=NS):
            designation = _txt(li, ".//ram:SpecifiedTradeProduct/ram:Name")
            code = _txt(li, ".//ram:SpecifiedTradeProduct/ram:SellerAssignedID") or _txt(
                li, ".//ram:SpecifiedTradeProduct/ram:GlobalID"
            )
            # Prix unitaire net HT
            pu = _txt(li, ".//ram:NetPriceProductTradePrice/ram:ChargeAmount") or _txt(
                li, ".//ram:GrossPriceProductTradePrice/ram:ChargeAmount"
            )
            qte = _txt(li, ".//ram:SpecifiedLineTradeDelivery/ram:BilledQuantity")
            montant = _txt(li, ".//ram:SpecifiedTradeSettlementLineMonetarySummation/ram:LineTotalAmount")

            if not designation or pu is None:
                continue
            fac.lignes.append(
                LigneFacture(
                    designation=designation,
                    prix_unitaire_ht=float(pu),
                    unite=unites_par_code.get(code, "unité"),
                    fournisseur=self.nom_fournisseur,
                    date_prix=date_prix,
                    code_article=code,
                    quantite=float(qte) if qte else None,
                    montant_ht=float(montant) if montant else None,
                )
            )
        return fac


def _unites_par_code(pdf_path: Path) -> dict[str, str]:
    """Lit l'unité facturée de chaque article dans le texte du PDF, indexée par code article."""
    unites_par_code = {}
    for ligne in _lignes_texte(pdf_path):
        m = RE_LIGNE_PDF.match(ligne)
        if m:
            unites_par_code[m.group("code")] = {"KG": "kg", "L": "L"}.get(m.group("unite"), m.group("unite"))
    return unites_par_code
