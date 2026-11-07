"""Extraction sur des lignes réelles de factures : les PDF ne sont pas versionnés."""

from pathlib import Path

import pytest

from pipeline.extractors import facturx_extractor, pdf_extractors
from pipeline.extractors.facturx_extractor import DistralisExtractor, TransgourmetExtractor
from pipeline.extractors.pdf_extractors import CremerieExtractor, MinoterieExtractor, SuberyExtractor

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

XML_DISTRALIS = b"""<rsm:CrossIndustryInvoice
  xmlns:rsm="urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100"
  xmlns:ram="urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100"
  xmlns:udt="urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100">
  <rsm:ExchangedDocument><ram:ID>19693635</ram:ID>
    <ram:IssueDateTime><udt:DateTimeString format="102">20261031</udt:DateTimeString></ram:IssueDateTime>
  </rsm:ExchangedDocument>
  <ram:IncludedSupplyChainTradeLineItem>
    <ram:SpecifiedTradeProduct><ram:SellerAssignedID>71397</ram:SellerAssignedID>
      <ram:Name>FILET POULET S/OS S/P VF 2K5 VOLPIN</ram:Name></ram:SpecifiedTradeProduct>
    <ram:NetPriceProductTradePrice><ram:ChargeAmount>8.55</ram:ChargeAmount></ram:NetPriceProductTradePrice>
    <ram:SpecifiedLineTradeDelivery><ram:BilledQuantity unitCode="KGM">9.458</ram:BilledQuantity>
    </ram:SpecifiedLineTradeDelivery>
  </ram:IncludedSupplyChainTradeLineItem>
  <ram:IncludedSupplyChainTradeLineItem>
    <ram:SpecifiedTradeProduct><ram:SellerAssignedID>144177</ram:SellerAssignedID>
      <ram:Name>OEUF ECALE 43/53 SEAU X150 OVOTEAM</ram:Name></ram:SpecifiedTradeProduct>
    <ram:NetPriceProductTradePrice><ram:ChargeAmount>0.39</ram:ChargeAmount></ram:NetPriceProductTradePrice>
    <ram:SpecifiedLineTradeDelivery><ram:BilledQuantity unitCode="C62">150</ram:BilledQuantity>
    </ram:SpecifiedLineTradeDelivery>
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


def test_cremerie_reconnue_a_son_adresse_mail_et_lignes_dedoublonnees(texte_pdf):
    lignes = [
        "Email : cremeriedelarance@live.fr",
        "La Ferme de la Renaudais",
        "Facture FA00006844 du : 29/10/2026 BOULANGERIE LEVAIN COEUR",
        "Le 29/10/2026",
        "Code Description Unité Qté P.U. HT Montant HT TVA",
        "L1 LAIT ENTIERPASTEURISE Litre 40,00 0,80 32,00 5,50",
        "F1 FROMAGE BLANC EN 3-5 ou 10 KG Kg 6,00 3,40 20,40 5,50",
        "0,00 0,00 0,00 0,00",
        "L1 LAIT ENTIERPASTEURISE Litre 30,00 0,80 24,00 5,50",
    ]
    texte_pdf(lignes)

    extracteur = CremerieExtractor()
    assert extracteur.peut_traiter(PDF, "\n".join(lignes))
    facture = extracteur.extraire(PDF)

    assert facture.date_prix == "29/10/2026"
    assert [(l.designation, l.prix_unitaire_ht, l.unite) for l in facture.lignes] == [
        ("LAIT ENTIERPASTEURISE", 0.80, "L"),
        ("FROMAGE BLANC EN 3-5 ou 10 KG", 3.40, "kg"),
    ]


def test_transgourmet_prend_l_unite_dans_le_texte_du_pdf(texte_pdf, monkeypatch):
    monkeypatch.setattr(TransgourmetExtractor, "_lire_xml", lambda *_: XML_TRANSGOURMET)
    texte_pdf(
        [
            "439729 SUCRE SEMOULE PATISSIERE 25 KG BEGHIN SAY 3174660070073 3 75 KG 0,950 71,25 03",
            "221237 ORANGINA SLIM 33 CL X24 ORANGINA 3124480184344 1 1 CL 16,800 Pr 16,80 03",
        ]
    )

    lignes = TransgourmetExtractor().extraire(PDF).lignes

    assert [lg.unite for lg in lignes] == ["kg", "CL", "unité"]


def test_distralis_reconnue_a_team_ouest_et_unite_lue_dans_le_xml(texte_pdf, monkeypatch):
    monkeypatch.setattr(DistralisExtractor, "_lire_xml", lambda *_: XML_DISTRALIS)
    texte_pdf(["71397FILET POULET S/OS S/P VF 2K5 VOLPIN 9.458 KG 8.550 80.87 01"])

    assert DistralisExtractor().peut_traiter(PDF, "TEAM OUEST\nF A C T U R E")
    # un nom de fichier Factur-X ne suffit plus à faire passer la facture pour du Transgourmet
    assert not TransgourmetExtractor().peut_traiter(Path("x_fx.pdf"), "TEAM OUEST\nF A C T U R E")

    facture = DistralisExtractor().extraire(PDF)

    assert facture.fournisseur == "Distralis"
    assert [(lg.prix_unitaire_ht, lg.unite, lg.fournisseur) for lg in facture.lignes] == [
        (8.55, "kg", "Distralis"),
        (0.39, "pièce", "Distralis"),
    ]
