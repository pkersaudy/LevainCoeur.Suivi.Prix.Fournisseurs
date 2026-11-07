"""Configuration centrale du pipeline factures -> base de prix."""

from pathlib import Path

# --- Chemins ---
ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
BASE_CSV = DATA / "base_prix_matieres_premieres.csv"  # base longue (historique de prix)
ALIAS_CSV = DATA / "dictionnaire_alias.csv"  # dictionnaire d'alias (éditable à la main)
REVIEW_CSV = DATA / "a_valider.csv"  # file d'attente de revue humaine
INBOX = ROOT / "factures_a_traiter"  # déposez vos PDF ici

# --- Format CSV (locale FR / OnlyOffice) ---
CSV_SEP = ";"
CSV_DECIMAL = ","
CSV_ENCODING = "utf-8-sig"

# --- Matching ---
TOP_K = 10  # nb de candidats proposés au LLM
SEUIL_CONFIANCE_LLM = 0.90  # confiance du LLM < : file de revue

# --- File de revue ---
CATEGORIE_LLM = "llm matched"  # déjà en base, le boulanger la valide ou la corrige
CATEGORIE_A_RAPPROCHER = "a rapprocher"  # pas en base tant qu'il ne l'a pas remplie

# --- LLM de secours ---
LLM_MODEL = "claude-haiku-5-5"
LLM_API_KEY_ENV = "ANTHROPIC_API_KEY"
LLM_MAX_TOKENS = 1024  # la réflexion du modèle compte dedans
LLM_TIMEOUT_S = 30  # au-delà, le service est tenu pour indisponible
LLM_MAX_RETRIES = 2  # une surcharge (503) passe souvent à la relance ; le défaut relance plus de 9 min

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
