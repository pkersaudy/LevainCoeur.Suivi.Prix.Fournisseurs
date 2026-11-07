"""Configuration centrale du pipeline factures -> base de prix."""

from pathlib import Path

# --- Chemins ---
ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
BASE_CSV = DATA / "base_prix_matieres_premieres.csv"  # base longue (historique de prix)
ALIAS_CSV = DATA / "dictionnaire_alias.csv"  # dictionnaire d'alias (éditable à la main)
EMB_CACHE = DATA / "embeddings_cache.parquet"  # cache des vecteurs (incrémentale)
REVIEW_CSV = DATA / "a_valider.csv"  # file d'attente de revue humaine
INBOX = ROOT / "factures_a_traiter"  # déposez vos PDF ici

# --- Format CSV (locale FR / OnlyOffice) ---
CSV_SEP = ";"
CSV_DECIMAL = ","
CSV_ENCODING = "utf-8-sig"

# --- Matching ---
# Modèle d'embeddings multilingue (bon en français, tourne en local, gratuit)
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
TOP_K = 5  # nb de candidats proposés au LLM
SEUIL_AUTO = 0.82  # cosinus >= : on accepte sans LLM
SEUIL_LLM = 0.55  # cosinus entre SEUIL_LLM et SEUIL_AUTO : on demande au LLM
# cosinus < SEUIL_LLM : direct file de revue (probablement "new")

# --- LLM de secours ---
LLM_MODEL = "gemini-3.8-flash"
LLM_API_KEY_ENV = ("GEMINI_API_KEY", "GOOGLE_API_KEY")  # on essaie ces variables dans l'ordre

# --- Colonnes de la base ---
COLS_BASE = [
    "Catégorie Matière première",
    "Matière première",
    "Cout à l'unité",
    "Unité de mesure",
    "Fournisseur",
    "Date du prix",
    "Matière d'origine",
    "Statut correspondance",
]
