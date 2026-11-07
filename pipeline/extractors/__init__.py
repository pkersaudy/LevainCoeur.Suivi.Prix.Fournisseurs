from .base_extractor import Extractor, Facture, LigneFacture
from .facturx_extractor import FacturXExtractor
from .pdf_extractors import CremerieExtractor, MinoterieExtractor, SuberyExtractor

# Ordre = priorite de detection. Ajoutez un nouveau fournisseur ici.
EXTRACTEURS = [
    FacturXExtractor(),  # Transgourmet (XML embarque)
    MinoterieExtractor(),
    SuberyExtractor(),
    CremerieExtractor(),
]

__all__ = ["EXTRACTEURS", "Extractor", "Facture", "LigneFacture"]
