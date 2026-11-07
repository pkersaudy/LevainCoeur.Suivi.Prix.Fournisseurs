"""Extraction sur des lignes réelles de factures : les PDF ne sont pas versionnés."""

from pathlib import Path

import pytest

from pipeline.extractors import facturx_extractor, pdf_extractors
from pipeline.extractors.facturx_extractor import FacturXExtractor
from pipeline.extractors.pdf_extractors import MinoterieExtractor, SuberyExtractor

PDF = Path("facture.pdf")

XML_TRANSGOURMET = b"""<rsm:CrossIndustryInvoice
  xmlns:rsm="urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100"
  xmlns:ram="urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100"
  xmlns:udt="urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100">
  <rsm:ExchangedDocument><ram:ID>5161026291</ram:ID>
    <ram:IssueDateTime><udt:DateTimeString format="102">20261016</udt:DateTimeString></ram:IssueDateTime>
  </rsm:ExchangedDocument>
  <ram:IncludedSupplyChainTradeLineItem>
    <ram:SpecifiedTradeProduct><ram:SellerAssignedID>439729</ram:SellerAssignedID>
      <ram:Name>SUCRE SEMOULE PATISSIERE 25 KG</ram:Name></ram:SpecifiedTradeProduct>
    <ram:NetPriceProductTradePrice><ram:ChargeAmount>0.95</ram:ChargeAmount></ram:NetPriceProductTradePrice>
    <ram:SpecifiedLineTradeDelivery><ram:BilledQuantity unitCode="">75</ram:BilledQuantity>
    </ram:SpecifiedLineTradeDelivery>
  </ram:IncludedSupplyChainTradeLineItem>
  <ram:IncludedSupplyChainTradeLineItem>
    <ram:SpecifiedTradeProduct><ram:SellerAssignedID>221237</ram:SellerAssignedID>
      <ram:Name>ORANGINA SLIM 33 CL X24</ram:Name></ram:SpecifiedTradeProduct>
    <ram:NetPriceProductTradePrice><ram:ChargeAmount>16.8</ram:ChargeAmount></ram:NetPriceProductTradePrice>
    <ram:SpecifiedLineTradeDelivery><ram:BilledQuantity unitCode="">1</ram:BilledQuantity>
    </ram:SpecifiedLineTradeDelivery>
  </ram:IncludedSupplyChainTradeLineItem>
  <ram:IncludedSupplyChainTradeLineItem>
    <ram:SpecifiedTradeProduct><ram:SellerAssignedID>999037</ram:SellerAssignedID>
      <ram:Name>FRAIS DE FACTURATION</ram:Name></ram:SpecifiedTradeProduct>
    <ram:NetPriceProductTradePrice><ram:ChargeAmount>3</ram:ChargeAmount></ram:NetPriceProductTradePrice>
  </ram:IncludedSupplyChainTradeLineItem>
</rsm:CrossIndustryInvoice>"""


@pytest.fixture
def texte_pdf(monkeypatch):
    """Remplace la lecture du PDF par les lignes données."""

    def poser(lignes):
        monkeypatch.setattr(pdf_extractors, "_lignes_texte", lambda _: lignes)
        monkeypatch.setattr(facturx_extractor, "_lignes_texte", lambda _: lignes)

    return poser


def test_subery_lit_les_lignes_et_date_chaque_facture_du_pdf(texte_pdf):
    texte_pdf(
        [
            "DATE FACTURE N° CLIENT TELEVENDEUR PREPARATEUR",
            "21/10/2026 202703744 1005972",
            "4 0,10 Carotte Lavée Sac Cal.35+ 10 kg Cat.1 France 1,000 0 1,38 1,38K 1,38",
            "Règlement par : PRELEVEMENT au : 10/11/2026",
            "DATE FACTURE N° CLIENT TELEVENDEUR PREPARATEUR",
            "26/10/2026 202704420 1005972",
            "4 1,00 Salade Roquette 2 x 500 g Cat.1 France 1,000 2 3,85 3,85P 7,70",
        ]
    )

    lignes = SuberyExtractor().extraire(PDF).lignes

    assert [(lg.date_prix, lg.prix_unitaire_ht, lg.unite) for lg in lignes] == [
        ("21/10/2026", 1.38, "kg"),
        ("26/10/2026", 3.85, "pièce"),
    ]
    assert lignes[0].designation == "Carotte Lavée Sac Cal.35+ 10 kg Cat.1 France"


def test_minoterie_prend_la_date_de_facture_et_non_l_echeance(texte_pdf):
    texte_pdf(
        [
            "Date échéance : 20/11/2026",
            "N° Pièce Date Code Client",
            "CHA26100438 21/10/2026 07620",
            "PF010025 TRADITION FRANCAISE T65 25 KG 10 SAC(S) 250 0,84000 -0,04500 0,79500 198,75 1",
        ]
    )

    facture = MinoterieExtractor().extraire(PDF)

    assert facture.date_prix == "21/10/2026"
    assert facture.lignes[0].prix_unitaire_ht == 0.795


def test_transgourmet_prend_l_unite_dans_le_texte_du_pdf(texte_pdf, monkeypatch):
    monkeypatch.setattr(FacturXExtractor, "_lire_xml", lambda *_: XML_TRANSGOURMET)
    texte_pdf(
        [
            "439729 SUCRE SEMOULE PATISSIERE 25 KG BEGHIN SAY 3174660070073 3 75 KG 0,950 71,25 03",
            "221237 ORANGINA SLIM 33 CL X24 ORANGINA 3124480184344 1 1 CL 16,800 Pr 16,80 03",
        ]
    )

    lignes = FacturXExtractor().extraire(PDF).lignes

    assert [lg.unite for lg in lignes] == ["kg", "CL", "unité"]
