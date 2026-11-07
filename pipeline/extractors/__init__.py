from .base_extractor import Extractor, Facture, LigneFacture
from .facturx_extractor import DistralisExtractor, TransgourmetExtractor
from .pdf_extractors import CremerieExtractor, MinoterieExtractor, SuberyExtractor

# Ordre = priorité de détection. Ajoutez un nouveau fournisseur ici.
EXTRACTEURS = [
    TransgourmetExtractor(),  # XML embarqué
    DistralisExtractor(),  # XML embarqué
    MinoterieExtractor(),
    SuberyExtractor(),
    CremerieExtractor(),
]

__all__ = ["EXTRACTEURS", "Extractor", "Facture", "LigneFacture"]
