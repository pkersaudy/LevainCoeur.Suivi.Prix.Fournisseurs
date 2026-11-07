"""Extracteur Factur-X : Transgourmet.

Les factures Transgourmet (fichiers 'facturX_..._fx.pdf') sont des PDF hybrides
Factur-X : une facture XML (norme CII / EN16931) est embarquee dans le PDF.
On lit directement ce XML -> AUCUN OCR, aucune heuristique de mise en page.
"""

from __future__ import annotations

from pathlib import Path

from lxml import etree

from .base_extractor import Extractor, Facture, LigneFacture

# Namespaces CII (Cross Industry Invoice)
NS = {
    "rsm": "urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100",
    "ram": "urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100",
    "udt": "urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100",
}


def _txt(node, xpath):
    r = node.xpath(xpath, namespaces=NS)
    return r[0].text.strip() if r and r[0].text else None


class FacturXExtractor(Extractor):
    nom_fournisseur = "Transgourmet"

    def peut_traiter(self, pdf_path: Path, texte_apercu: str) -> bool:
        # Nom de fichier Factur-X ou presence du XML embarque + emetteur Transgourmet
        if "facturx" in pdf_path.name.lower() or "_fx" in pdf_path.name.lower():
            return True
        return "TRANSGOURMET" in texte_apercu.upper()

    def _lire_xml(self, pdf_path: Path) -> bytes:
        # Necessite la lib 'facturx' : pip install factur-x
        from facturx import get_facturx_xml_from_pdf

        _, xml_bytes = get_facturx_xml_from_pdf(str(pdf_path))
        return xml_bytes

    def extraire(self, pdf_path: Path) -> Facture:
        root = etree.fromstring(self._lire_xml(pdf_path))

        numero = _txt(root, ".//rsm:ExchangedDocument/ram:ID")
        # date au format 102 (AAAAMMJJ)
        d = _txt(root, ".//rsm:ExchangedDocument/ram:IssueDateTime/udt:DateTimeString")
        date_prix = f"{d[6:8]}/{d[4:6]}/{d[0:4]}" if d and len(d) == 8 else ""

        fac = Facture(fournisseur=self.nom_fournisseur, date_prix=date_prix, numero=numero)

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
            unite = None
            q_node = li.xpath(".//ram:SpecifiedLineTradeDelivery/ram:BilledQuantity", namespaces=NS)
            if q_node:
                unite = q_node[0].get("unitCode")  # ex: KGM, LTR, C62 (piece)
            montant = _txt(li, ".//ram:SpecifiedTradeSettlementLineMonetarySummation/ram:LineTotalAmount")

            if not designation or pu is None:
                continue
            fac.lignes.append(
                LigneFacture(
                    designation=designation,
                    prix_unitaire_ht=float(pu),
                    unite=_map_unite(unite),
                    fournisseur=self.nom_fournisseur,
                    date_prix=date_prix,
                    code_article=code,
                    quantite=float(qte) if qte else None,
                    montant_ht=float(montant) if montant else None,
                )
            )
        return fac


def _map_unite(code: str | None) -> str:
    """Codes UN/ECE -> unites lisibles."""
    return {"KGM": "kg", "LTR": "L", "C62": "pièce", "H87": "pièce", "PCE": "pièce", "GRM": "g"}.get(
        (code or "").upper(), code or "unité"
    )
