# =============================================================================
# APPLICATION STREAMLIT — DÉMOGRAPHIE DES MÉTROPOLES FRANÇAISES
# Grenoble · Rennes · Saint-Étienne · Rouen · Montpellier
# Sources : INSEE — Recensements de la Population 2011, 2016, 2022
# Filtres déplacés en haut de chaque onglet (plus de sidebar surchargée)
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
from pathlib import Path
import unicodedata

# ──────────────────────────────────────────────────────────────────────────────
# 1. CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Démographie · Métropoles françaises",
    page_icon="🏙️",
    layout="wide",
)

if "page" not in st.session_state:
    st.session_state.page = "home"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Sora', sans-serif; }

div[data-testid="metric-container"] {
    background: #F7FBF8; border: 1px solid #C8E6D4;
    border-radius: 10px; padding: 14px 18px;
}
div[data-testid="metric-container"] label {
    color: #4A7C59 !important; font-size: 0.75rem;
    font-weight: 600; text-transform: uppercase; letter-spacing:.05em;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 1.5rem; color: #1C3A27; font-weight: 700;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 6px; background: #EEF4F0; border-radius: 10px; padding: 5px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 7px; padding: 8px 20px;
    font-size: 0.87rem; font-weight: 600; color: #4A7C59;
}
.stTabs [aria-selected="true"] { background: #2D6A4F !important; color: white !important; }
.section-header {
    font-size: 1.15rem; font-weight: 700; color: #1C3A27;
    border-bottom: 2px solid #2D6A4F; padding-bottom: 5px; margin-bottom: 16px;
}
.source-note { font-size: 0.72rem; color: #88A898; margin-top: -12px; margin-bottom: 18px; }

/* ── Bandeau filtres haut de page ── */
.filter-bar {
    background: #F0F7F3;
    border: 1px solid #C8E6D4;
    border-radius: 12px;
    padding: 16px 20px 12px 20px;
    margin-bottom: 20px;
}
.filter-bar-title {
    font-size: 0.72rem; font-weight: 700; color: #4A7C59;
    text-transform: uppercase; letter-spacing: 0.07em;
    margin-bottom: 10px;
}

/* Cartes KPI CSP */
.kpi-card {
    background-color: white; padding: 20px 25px; border-radius: 12px;
    border-left: 6px solid #2D6A4F; box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    text-align: center; margin-bottom: 10px;
}
.kpi-label { font-size: 12px; font-weight: 700; color: #7f8c8d; text-transform: uppercase; letter-spacing: 0.5px; }
.kpi-value { font-size: 28px; font-weight: 800; color: #1C3A27; margin: 5px 0; }
.kpi-subtitle { font-size: 11px; color: #95a5a6; }

/* Cartes KPI mobilités */
.kpi-card-mob {
    background-color: white; padding: 20px; border-radius: 12px;
    border-top: 5px solid #2D6A4F; box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    text-align: center; margin-bottom: 10px;
}

/* ── Boutons de navigation sidebar (même style que le bouton Accueil) ── */
section[data-testid="stSidebar"] div[data-testid="stRadio"] > label {
    display: none;
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] {
    display: flex; flex-direction: column; gap: 6px;
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] label[data-baseweb="radio"] {
    background: #F0F7F3;
    border: 1px solid #C8E6D4;
    border-radius: 8px;
    padding: 10px 16px;
    cursor: pointer;
    transition: background 0.15s, border-color 0.15s, box-shadow 0.15s;
    font-weight: 600;
    font-size: 0.88rem;
    color: #2D6A4F;
    width: 100%;
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] label[data-baseweb="radio"]:hover {
    background: #DDF0E8;
    border-color: #2D6A4F;
    box-shadow: 0 2px 8px rgba(45,106,79,0.15);
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] label[data-baseweb="radio"][aria-checked="true"] {
    background: #2D6A4F !important;
    border-color: #2D6A4F !important;
    color: white !important;
    box-shadow: 0 2px 8px rgba(45,106,79,0.25);
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] span[data-testid="stMarkdownContainer"] p {
    margin: 0; font-weight: 600;
}
/* Masquer le rond radio natif */
section[data-testid="stSidebar"] div[data-testid="stRadio"] div[data-testid="stWidgetLabel"],
section[data-testid="stSidebar"] div[data-testid="stRadio"] input[type="radio"] {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# 2. CONSTANTES
# ──────────────────────────────────────────────────────────────────────────────
COMMUNES = {
    "Grenoble": [
        "Bresson","Brié-et-Angonnes","Champ-sur-Drac","Champagnier","Claix","Corenc",
        "Domène","Échirolles","Eybens","Fontaine","Fontanil-Cornillon","Gières","Grenoble",
        "Herbeys","Jarrie","La Tronche","Le Gua","Le Pont-de-Claix","Le Sappey-en-Chartreuse",
        "Meylan","Miribel-Lanchâtre","Mont-Saint-Martin","Montchaboud","Murianette",
        "Notre-Dame-de-Commiers","Notre-Dame-de-Mésage","Noyarey","Poisat","Proveysieux",
        "Quaix-en-Chartreuse","Saint-Barthélemy-de-Séchilienne","Saint-Égrève",
        "Saint-Georges-de-Commiers","Saint-Martin-d'Hères","Saint-Martin-le-Vinoux",
        "Saint-Paul-de-Varces","Saint-Pierre-de-Mésage","Sarcenas","Sassenage","Séchilienne",
        "Seyssinet-Pariset","Seyssins","Varces-Allières-et-Risset","Vaulnaveys-le-Bas",
        "Vaulnaveys-le-Haut","Venon","Veurey-Voroize","Vif","Vizille",
    ],
    "Rennes": [
        "Acigné","Bécherel","Betton","Bourgbarré","Brécé","Bruz","Cesson-Sévigné","Chantepie",
        "Chartres-de-Bretagne","Chavagne","Chevaigné","Cintré","Corps-Nuds","Gévezé",
        "La Chapelle-des-Fougeretz","La Chapelle-Thouarault","L'Hermitage","Le Rheu","Le Verger",
        "Montgermont","Mordelles","Noyal-Châtillon-sur-Seiche","Nouvoitou","Orgères","Pacé",
        "Parthenay-de-Bretagne","Pont-Péan","Rennes","Romillé","Saint-Armel","Saint-Erblon",
        "Saint-Gilles","Saint-Grégoire","Saint-Jacques-de-la-Lande","Saint-Sulpice-la-Forêt",
        "Thorigné-Fouillard","Vern-sur-Seiche","Vezin-le-Coquet","Clayes",
        "La Chapelle-Chaussée","Laillé","Langan","Miniac-sous-Bécherel",
    ],
    "Rouen": [
        "Amfreville-la-Mi-Voie","Anneville-Ambourville","Bardouville","Belbeuf","Berville-sur-Seine",
        "Bihorel","Bois-Guillaume","Bonsecours","Boos","Canteleu","Caudebec-lès-Elbeuf","Cléon",
        "Darnétal","Déville-lès-Rouen","Duclair","Elbeuf","Épinay-sur-Duclair",
        "Fontaine-sous-Préaux","Franqueville-Saint-Pierre","Freneuse","Gouy","Grand-Couronne",
        "Hautot-sur-Seine","Hénouville","Houppeville","Isneauville","Jumièges","La Bouille",
        "La Londe","La Neuville-Chant-d'Oisel","Le Grand-Quevilly","Le Houlme","Le Mesnil-Esnard",
        "Le Mesnil-sous-Jumièges","Le Petit-Quevilly","Le Trait",
        "Les Authieux-sur-le-Port-Saint-Ouen","Malaunay","Maromme","Mont-Saint-Aignan","Montmain",
        "Moulineaux","Notre-Dame-de-Bondeville","Oissel-sur-Seine","Orival","Petit-Couronne",
        "Quevillon","Quévreville-la-Poterie","Roncherolles-sur-le-Vivier","Rouen","Sahurs",
        "Saint-Aubin-Celloville","Saint-Aubin-Épinay","Saint-Aubin-lès-Elbeuf",
        "Saint-Étienne-du-Rouvray","Saint-Jacques-sur-Darnétal","Saint-Léger-du-Bourg-Denis",
        "Saint-Martin-de-Boscherville","Saint-Martin-du-Vivier","Saint-Paër",
        "Saint-Pierre-de-Manneville","Saint-Pierre-de-Varengeville","Saint-Pierre-lès-Elbeuf",
        "Sainte-Marguerite-sur-Duclair","Sotteville-lès-Rouen","Sotteville-sous-le-Val",
        "Tourville-la-Rivière","Val-de-la-Haye","Yainville","Ymare","Yville-sur-Seine",
    ],
    "Saint-Étienne": [
        "Aboën","Andrézieux-Bouthéon","Caloire","Cellieu","Chagnon","Chambœuf","Châteauneuf",
        "Dargoire","Doizieux","Farnay","Firminy","Fontanès","Fraisses","Genilac","L'Étrat",
        "L'Horme","La Fouillouse","La Gimond","La Grand-Croix","La Ricamarie","La Talaudière",
        "La Terrasse-sur-Dorlay","La Tour-en-Jarez","La Valla-en-Gier","Le Chambon-Feugerolles",
        "Lorette","Marcenod","Pavezin","Rive-de-Gier","Roche-la-Molière","Rozier-Côtes-d'Aurec",
        "Saint-Bonnet-les-Oules","Saint-Chamond","Saint-Christo-en-Jarez","Saint-Étienne",
        "Saint-Galmier","Saint-Genest-Lerpt","Saint-Héand","Saint-Jean-Bonnefonds","Saint-Joseph",
        "Saint-Martin-la-Plaine","Saint-Maurice-en-Gourgois","Saint-Nizier-de-Fornas",
        "Saint-Paul-en-Cornillon","Saint-Paul-en-Jarez","Saint-Priest-en-Jarez",
        "Saint-Romain-en-Jarez","Sainte-Croix-en-Jarez","Sorbiers","Tartaras",
        "Unieux","Valfleury","Villars",
    ],
    "Montpellier": [
        "Baillargues","Beaulieu","Castelnau-le-Lez","Castries","Clapiers","Cournonsec",
        "Cournonterral","Fabrègues","Grabels","Jacou","Juvignac","Lattes","Lavérune","Le Crès",
        "Montaud","Montferrier-sur-Lez","Montpellier","Murviel-lès-Montpellier","Pérols","Pignan",
        "Prades-le-Lez","Restinclières","Saint-Brès","Saint-Drézéry","Saint-Geniès-des-Mourgues",
        "Saint-Georges-d'Orques","Saint-Jean-de-Védas","Saussan","Sussargues","Vendargues",
        "Villeneuve-lès-Maguelone",
    ],
}

COMMUNE_VERS_METRO = {c: m for m, lst in COMMUNES.items() for c in lst}

NOM_EPCI = {
    "Grenoble":      "EPCI : Grenoble-Alpes-Métropole (200040715)",
    "Rennes":        "EPCI : Rennes Métropole (243500139)",
    "Rouen":         "EPCI : Rouen Normandie (200023414)",
    "Saint-Étienne": "EPCI : Saint-Etienne Métropole (244200770)",
    "Montpellier":   "EPCI : Montpellier Méditerranée Métropole (243400017)",
}
DR24_MAP = {"Grenoble": 38, "Rennes": 35, "Rouen": 76, "Saint-Étienne": 42, "Montpellier": 34}

COULEURS = {
    "Grenoble": "#2D6A4F", "Rennes": "#1A6FA3",
    "Saint-Étienne": "#C45B2A", "Rouen": "#7B3FA0", "Montpellier": "#D4A017",
}
TOUTES = list(COMMUNES.keys())

DEP_MAP = {
    "Grenoble": "38", "Rennes": "35", "Rouen": "76",
    "Saint-Étienne": "42", "Montpellier": "34",
}

CSP_MAP_NEW = {
    "Agriculteurs": "Agriculteurs", "Artisans": "Artisans & Chefs",
    "Cadres": "Cadres & Prof. Sup.", "Professions intermédiaires": "Prof. Intermédiaires",
    "Employés": "Employés", "Ouvriers": "Ouvriers",
}

DIP_MAP = {
    "Aucun diplôme": "Sans diplôme", "niveau CEP": "CEP", "niveau BEPC": "BEPC",
    "niveau CAP-BEP": "CAP-BEP", "bac général ou technique": "Baccalauréat",
    "universitaire de 1er cycle": "Bac + 2", "universitaire de 2ème": "Bac + 3/4",
    "universitaire de 3ème": "Supérieur (Bac+5+)",
}

LABEL_TRANCHE = {
    "01":"0–4","02":"5–9","03":"10–14","04":"15–19","05":"20–24",
    "06":"25–29","07":"30–34","08":"35–39","09":"40–44","10":"45–49",
    "11":"50–54","12":"55–59","13":"60–64","14":"65–69","15":"70–74",
    "16":"75–79","17":"80–84","18":"85–89","19":"90–94","20":"95+",
}
TRANCHES_JEUNES  = ["01","02","03","04"]
TRANCHES_ACTIFS  = ["05","06","07","08","09","10","11","12","13"]
TRANCHES_SENIORS = ["14","15","16","17","18","19","20"]

# ──────────────────────────────────────────────────────────────────────────────
# 3. CHARGEMENT
# ──────────────────────────────────────────────────────────────────────────────
DATA_DIR = Path("demographie/data_clean")

@st.cache_data
def charger_generales():
    p = DATA_DIR / "population" / "Donnees_generales_comparatives_clean.csv"
    return pd.read_csv(p) if p.exists() else None

@st.cache_data
def charger_pop_age():
    p = DATA_DIR / "population" / "Population_tranche_age_clean.csv"
    if not p.exists():
        return None
    df = pd.read_csv(p)
    df["metropole"] = df["LIBELLE"].map(COMMUNE_VERS_METRO)
    return df

@st.cache_data
def charger_men_age():
    p = DATA_DIR / "menages" / "Menage_age_situation_clean.csv"
    if not p.exists():
        return None
    df = pd.read_csv(p)
    df["metropole"] = df["LIBGEO"].map(COMMUNE_VERS_METRO)
    return df

@st.cache_data
def charger_men_csp():
    p = DATA_DIR / "menages" / "Menages_csp_nbpers_clean.csv"
    if not p.exists():
        return None
    df = pd.read_csv(p)
    df["metropole"] = df["LIBGEO"].map(COMMUNE_VERS_METRO)
    return df

@st.cache_data
def charger_mobilites():
    p_res  = DATA_DIR / "mobilite" / "Migrations_resid_clean.csv"
    p_prof = DATA_DIR / "mobilite" / "Mobilite_profess_clean.csv"
    p_scol = DATA_DIR / "mobilite" / "Mobilite_scolaire_clean.csv"

    def safe_load(p):
        if not p.exists():
            return None
        df = pd.read_csv(p)
        df["flux"] = pd.to_numeric(df.get("flux", 0), errors="coerce").fillna(0)
        return df

    return safe_load(p_res), safe_load(p_prof), safe_load(p_scol)

@st.cache_data
def charger_caf():
    paths = [
        Path("solidarite&citoyennete/data_clean/solidarite/CAF_5_Metropoles.csv"),
        Path("CAF_5_Metropoles.csv"),
    ]
    df = None
    for p in paths:
        if p.exists():
            df = pd.read_csv(p, sep=";", low_memory=False)
            break
    if df is None:
        return None
    if "Date_Ref" in df.columns and "Annee" not in df.columns:
        df["Annee"] = pd.to_datetime(df["Date_Ref"], errors="coerce").dt.year
    return df

@st.cache_data
def charger_effectifs():
    paths = [
        Path("solidarite&citoyennete/data_clean/education/effectifs_5_villes.csv"),
        Path("effectifs_5_villes.csv"),
    ]
    df = None
    for p in paths:
        if p.exists():
            df = pd.read_csv(p, low_memory=False)
            break
    if df is None:
        return None
    DEP_METRO = {"D038": "Grenoble", "D035": "Rennes", "D076": "Rouen",
                 "D042": "Saint-Étienne", "D034": "Montpellier"}
    df["metropole"] = df["dep_id"].map(DEP_METRO)
    df["effectif"] = pd.to_numeric(df["effectif"], errors="coerce").fillna(0)
    return df

@st.cache_data
def charger_filo():
    paths = [
        Path("solidarite&citoyennete/data_clean/revenus&pauvrete/BASE_TD_FILO_IRIS_2021_DEC.xlsx"),
        Path("BASE_TD_FILO_IRIS_2021_DEC.xlsx"),
    ]
    df = None
    for p in paths:
        if p.exists():
            df = pd.read_excel(p, sheet_name="IRIS_DEC", header=5)
            break
    if df is None:
        return None
    # Nettoyage : virgules décimales → points, conversion numérique
    num_cols = [c for c in df.columns if c.startswith("DEC_")]
    for c in num_cols:
        df[c] = pd.to_numeric(df[c].astype(str).str.replace(",", "."), errors="coerce")
    df["DEP"] = df["COM"].astype(str).str.zfill(5).str[:2]
    DEP_METRO = {"38": "Grenoble", "35": "Rennes", "76": "Rouen",
                 "42": "Saint-Étienne", "34": "Montpellier"}
    df["metropole"] = df["DEP"].map(DEP_METRO)
    df = df[df["metropole"].notna()].copy()
    return df

def normalize_name(text):
    if pd.isna(text):
        return ""
    return (unicodedata.normalize("NFKD", str(text))
            .encode("ascii", "ignore").decode("utf-8").lower().strip())

normalize_csp_name = normalize_name

@st.cache_data
def load_generic_data(file_paths_dict, mapping_dict):
    all_data = []
    for year, path in file_paths_dict.items():
        p = Path(path)
        if not p.exists():
            continue
        try:
            df = pd.read_excel(p) if p.suffix.lower() in [".xlsx", ".xls"] else pd.read_csv(p, sep=None, engine="python", low_memory=False)
            if not df.empty and "RR" in str(df.iloc[0, 0]):
                df = df.drop(0).reset_index(drop=True)
            c_dep = [c for c in df.columns if any(x in str(c).upper() for x in ["DÉPARTEMENT", "DR24", "DEP"])][0]
            c_lib = [c for c in df.columns if any(x in str(c).upper() for x in ["LIBELLÉ", "LIBELLE"])][0]
            res = pd.DataFrame({
                "DEP": df[c_dep].astype(str).str.zfill(2),
                "NOM": df[c_lib].astype(str),
                "ANNEE": int(year),
                "LIB_NORM": df[c_lib].apply(normalize_name),
            })
            for raw, clean in mapping_dict.items():
                cols = [c for c in df.columns if raw.lower() in str(c).lower()]
                res[clean] = df[cols].apply(pd.to_numeric, errors="coerce").fillna(0).sum(axis=1)
            all_data.append(res)
        except Exception:
            continue
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

# ── Chargement ───────────────────────────────────────────────────────────────
df_gen     = charger_generales()
df_pop     = charger_pop_age()
df_men_age = charger_men_age()
df_men_csp = charger_men_csp()
df_caf     = charger_caf()
df_eff     = charger_effectifs()
df_filo    = charger_filo()
df_res, df_prof, df_scol = charger_mobilites()

FILES_CSP = {
    2011: "demographie/data_clean/population_2554/Commune_2011_2554_sect_activite.xlsx",
    2016: "demographie/data_clean/population_2554/Commune_2016_2554_sect_activite.xlsx",
    2022: "demographie/data_clean/population_2554/Commune_2022_2554_sect_activite.xlsx",
}
FILES_DIP = {
    2011: "demographie/data_clean/population_2554/Commune_2011_2554_niveau_diplome.xlsx",
    2022: "demographie/data_clean/population_2554/Commune_2022_2554_niveau_diplome.xlsx",
}
df_csp_new = load_generic_data(FILES_CSP, CSP_MAP_NEW)
df_dip_new = load_generic_data(FILES_DIP, DIP_MAP)

# ──────────────────────────────────────────────────────────────────────────────
# 4. UTILITAIRES
# ──────────────────────────────────────────────────────────────────────────────
def fmt(v, suffix="", dec=0):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "N/D"
    if abs(v) >= 1_000_000:
        return f"{v/1_000_000:.2f} M{suffix}"
    if abs(v) >= 1_000:
        return f"{int(round(v)):,}{suffix}".replace(",", "\u202f")
    return f"{v:.{dec}f}{suffix}"

def get_epci_row(metro):
    if df_gen is None or metro not in NOM_EPCI:
        return None
    rows = df_gen[df_gen["territoire"] == NOM_EPCI[metro]]
    return rows.iloc[0] if not rows.empty else None

def epci_val(metro, col):
    if df_gen is None:
        return np.nan
    nom = NOM_EPCI.get(metro)
    if not nom:
        return np.nan
    rows = df_gen[df_gen["territoire"] == nom]
    if rows.empty:
        return np.nan
    v = rows.iloc[0].get(col, np.nan)
    return float(v) if pd.notna(v) else np.nan

def pop_from_age(metro, annee):
    if df_pop is None:
        return np.nan
    dr = DR24_MAP.get(metro)
    sub = df_pop[(df_pop["DR24"] == dr) & (df_pop["annee"] == annee)]
    age_cols = [c for c in sub.columns if "ageq_rec" in c]
    if sub.empty or not age_cols:
        return np.nan
    return float(sub[age_cols].sum().sum())

def cols_h(df):
    return sorted([c for c in df.columns if "ageq_rec" in c and "s1" in c])

def cols_f(df):
    return sorted([c for c in df.columns if "ageq_rec" in c and "s2" in c])

def label_col(col):
    import re
    m = re.search(r"ageq_rec(\d{2})", col)
    return LABEL_TRANCHE.get(m.group(1), col) if m else col

def somme_tranches(df_src, tranches, annee=None):
    if annee is not None:
        df_src = df_src[df_src["annee"] == annee]
    total = 0
    for t in tranches:
        for sx in ["s1", "s2"]:
            col = f"ageq_rec{t}{sx}rpop2016"
            if col in df_src.columns:
                total += df_src[col].sum()
    return total

def style(fig, marge_t=20):
    fig.update_layout(template="plotly_white", plot_bgcolor="rgba(0,0,0,0)",
                      paper_bgcolor="rgba(0,0,0,0)", font_family="Sora",
                      margin=dict(t=marge_t, b=20, l=10, r=10))
    return fig

def filter_bar(label="🔧 Filtres"):
    """Ouvre un conteneur visuellement encadré pour les filtres en haut de page."""
    st.markdown(f'<div class="filter-bar-title">{label}</div>', unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# 5. EN-TÊTE
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(
    "<h1 style='color:#1C3A27;font-size:2rem;margin-bottom:2px'> Tableau de bord concernant la métropole de Grenoble</h1>"
    "<p style='color:#5A8A6A;margin-bottom:20px'>Analyse intercommunal et intermétropole</p>",
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────────────────────
# 6. PAGE D'ACCUEIL (nouvelle version)
# ──────────────────────────────────────────────────────────────────────────────
if st.session_state.page == "home":
    st.markdown("""
    <style>
    .hero-accueil {
        background: linear-gradient(135deg, #1C3A27 0%, #2D6A4F 60%, #40916C 100%);
        border-radius: 16px; padding: 0; overflow: hidden;
        margin-bottom: 28px; position: relative;
    }
    .hero-inner {
        display: flex; align-items: stretch; min-height: 220px;
    }
    .hero-img-col {
        flex: 1; min-width: 0; position: relative; overflow: hidden;
    }
    .hero-img-col img {
        width: 100%; height: 100%; object-fit: cover;
        object-position: center; filter: saturate(0.75) brightness(0.85);
        display: block;
    }
    .hero-img-overlay {
        position: absolute; inset: 0;
        background: linear-gradient(to right, #1C3A27 0%, rgba(28,58,39,0) 100%);
    }
    .hero-text-col {
        flex: 0 0 420px; padding: 36px 36px 36px 40px;
        display: flex; flex-direction: column; justify-content: center;
        position: relative; z-index: 2;
    }
    .hero-badge {
        display: inline-block; background: rgba(149,213,178,0.2);
        color: #95D5B2; font-size: 11px; font-weight: 700;
        letter-spacing: 0.1em; text-transform: uppercase;
        padding: 4px 14px; border-radius: 20px;
        border: 1px solid rgba(149,213,178,0.35); margin-bottom: 14px; width: fit-content;
    }
    .hero-title {
        font-size: 28px; font-weight: 700; color: #fff; line-height: 1.25; margin-bottom: 10px;
    }
    .hero-subtitle { font-size: 13px; color: #95D5B2; font-weight: 400; line-height: 1.6; }

    .stats-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 20px; }
    .stat-box {
        background: #F0F7F3; border: 1px solid #C8E6D4; border-radius: 10px;
        padding: 14px 10px; text-align: center;
    }
    .stat-num { font-size: 24px; font-weight: 700; color: #1C3A27; }
    .stat-lbl { font-size: 11px; color: #4A7C59; font-weight: 700;
        text-transform: uppercase; letter-spacing: 0.07em; margin-top: 2px; }

    .cards-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }
    .info-card {
        background: white; border: 1px solid #C8E6D4; border-radius: 12px;
        padding: 20px 22px; border-left: 5px solid #2D6A4F;
    }
    .info-card.orange { border-left-color: #C45B2A; }
    .info-card-title {
        font-size: 12px; font-weight: 700; color: #2D6A4F; text-transform: uppercase;
        letter-spacing: 0.08em; margin-bottom: 10px;
    }
    .info-card.orange .info-card-title { color: #C45B2A; }
    .info-card-body { font-size: 13px; color: #2c2c2c; line-height: 1.7; text-align: justify; }
    .tag-row { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 12px; }
    .tag-green {
        font-size: 11px; font-weight: 600; padding: 3px 11px; border-radius: 20px;
        background: #EEF4F0; color: #2D6A4F; border: 1px solid #C8E6D4;
    }
    .tag-orange {
        font-size: 11px; font-weight: 600; padding: 3px 11px; border-radius: 20px;
        background: #FEF3ED; color: #C45B2A; border: 1px solid #F5C4B3;
    }
    .cta-wrapper { margin-top: 8px; }
    div[data-testid="stButton"] > button[kind="primary"] {
        background: #2D6A4F !important; color: white !important;
        border: none !important; border-radius: 12px !important;
        padding: 14px 28px !important; font-size: 15px !important;
        font-weight: 700 !important; width: 100% !important;
        letter-spacing: 0.03em !important; transition: background 0.2s !important;
    }
    div[data-testid="stButton"] > button[kind="primary"]:hover {
        background: #1C3A27 !important;
    }
    .footer-note { font-size: 11px; color: #88A898; text-align: center; margin-top: 12px; }
    </style>
    """, unsafe_allow_html=True)

    # ── Hero banner ────────────────────────────────────────────────────────
    img_path = Path("grenoble-1600x900.jpg")
    if img_path.exists():
        import base64
        with open(img_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()
        img_tag = f'<img src="data:image/jpeg;base64,{img_b64}" alt="Grenoble"/>'
        img_col_html = f'<div class="hero-img-col">{img_tag}<div class="hero-img-overlay"></div></div>'
    else:
        img_col_html = ""

    st.markdown(f"""
    <div class="hero-accueil">
        <div class="hero-inner">
            <div class="hero-text-col">
                <div class="hero-badge">Outil d'aide à la décision</div>
                <div class="hero-title">Différentes dynamiques<br>et enjeux territoriales</div>
                <div class="hero-subtitle">
                    Grenoble · Rennes · Rouen<br>Saint-Étienne · Montpellier
                </div>
            </div>
            {img_col_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Stats ──────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="stats-row">
        <div class="stat-box"><div class="stat-num">5</div><div class="stat-lbl">Métropoles</div></div>
        <div class="stat-box"><div class="stat-num">49</div><div class="stat-lbl">Communes (Grenoble)</div></div>
        <div class="stat-box"><div class="stat-num">2</div><div class="stat-lbl">Thématiques</div></div>
    </div>
    """, unsafe_allow_html=True)

    # ── Cartes objectif + sources ──────────────────────────────────────────
    st.markdown("""
    <div class="cards-row">
        <div class="info-card">
            <div class="info-card-title">Objectif</div>
            <div class="info-card-body">
                Analyser les données de démographie et de solidarité & citoyenneté afin de produire une analyse complète pour chaque commune de la métropole de Grenoble. 
                Cette étude vise à permettre la comparaison des communes entre elles, ainsi qu’à situer la métropole de Grenoble par rapport à celles de Rouen, Saint-Étienne, Rennes et Montpellier. 
                Elle est également destinée à accompagner les nouveaux élus dans la compréhension des dynamiques territoriales.
            </div>
        </div>
        <div class="info-card" style="border-left-color:#1A6FA3;">
            <div class="info-card-title" style="color:#1A6FA3;">Sources</div>
            <div class="info-card-body">
                Données INSEE — Recensements de la Population 2011, 2016 et 2022.
                Données CAF et indicateurs de solidarité pour la période 2019–2022.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Cartes thématiques ─────────────────────────────────────────────────
    st.markdown("""
    <div class="cards-row">
        <div class="info-card">
            <div class="info-card-title">📊 Démographie</div>
            <div class="info-card-body">
                Analyse de la population, de la structure par âge, des mobilités, des ménages, des mobilités résidentielles, professionnelles et scolaires
                à l'échelle des communes et des EPCI.
            </div>
            <div class="tag-row">
                <span class="tag-green">Population</span>
                <span class="tag-green">Structure des âges</span>
                <span class="tag-green">Mobilités</span>
                <span class="tag-green">Ménages</span>
                <span class="tag-green">Population active 25-54 ans</span>
            </div>
        </div>
        <div class="info-card orange">
            <div class="info-card-title">🤝 Solidarité & citoyenneté</div>
            <div class="info-card-body">
                Étude des allocations CAF, des indicateurs éducatifs et de santé,
                ainsi que de la participation citoyenne sur l'ensemble
                des territoires métropolitains.
            </div>
            <div class="tag-row">
                <span class="tag-orange">Solidarité</span>
                <span class="tag-orange">Éducation</span>
                <span class="tag-orange">Santé</span>
                <span class="tag-orange">Participation citoyenne</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Bouton CTA ─────────────────────────────────────────────────────────
    st.markdown('<div class="cta-wrapper">', unsafe_allow_html=True)
    if st.button("→  Accéder à l'application", type="primary"):
        st.session_state.page = "app"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="footer-note">Données INSEE · Recensements de la Population 2011, 2016, 2022</p>',
        unsafe_allow_html=True,
    )
    st.stop()

# ──────────────────────────────────────────────────────────────────────────────
# 7. SIDEBAR + NAVIGATION (sidebar minimale : navigation seule)
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    # ── 1. STYLE AMÉLIORÉ (Effets Hover + Design moderne) ────────────────────
    st.markdown("""
        <style>
        /* Force le fond de la sidebar en vert foncé */
        [data-testid="stSidebar"] {
            background-color: #1B4332 !important;
        }

        /* Conteneur global de la radio pour enlever les marges par défaut */
        div[data-testid="stRadio"] > div {
            gap: 8px;
        }

        /* Style de base des boutons (labels) */
        div[data-testid="stRadio"] label {
            background-color: rgba(255, 255, 255, 0.9) !important;
            padding: 12px 16px !important;
            border-radius: 12px !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            transition: all 0.3s ease-in-out !important; /* Animation fluide */
            cursor: pointer !important;
        }

        /* EFFET AU SURVOL (HOVER) */
        div[data-testid="stRadio"] label:hover {
            background-color: #FFFFFF !important; /* Blanc pur au survol */
            transform: translateX(5px) !important; /* Petit décalage à droite */
            box-shadow: 0px 4px 12px rgba(0,0,0,0.2) !important; /* Ombre portée */
            border: 1px solid #95D5B2 !important;
        }

        /* Style du texte (Noir) */
        div[data-testid="stRadio"] label p {
            color: #1B4332 !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            margin: 0 !important;
        }

        /* Style quand l'option est sélectionnée (Active) */
        div[data-testid="stRadio"] input:checked + div label {
            background-color: #95D5B2 !important; /* Vert clair quand sélectionné */
            border: 1px solid #FFFFFF !important;
        }
        
        /* Titre de section "Navigation" */
        .nav-header {
            font-size: 11px;
            font-weight: 800;
            color: #95D5B2;
            text-transform: uppercase;
            letter-spacing: 0.15em;
            padding: 20px 0 10px 5px;
            font-family: 'Sora', sans-serif;
        }
        </style>
    """, unsafe_allow_html=True)

    # ── 2. LOGO DU HAUT ──────────────────────────────────────────────────────
    st.markdown("""
    <div style="display:flex;align-items:center;gap:12px;padding:10px 8px 20px 8px;border-bottom:1px solid rgba(149,213,178,0.2);">
        <div style="width:38px;height:38px;background:#2D6A4F;border-radius:10px;display:flex;align-items:center;justify-content:center;box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z" stroke="#95D5B2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M9 22V12h6v10" stroke="#95D5B2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </div>
        <div>
            <div style="font-size:14px;font-weight:700;color:#FFFFFF;line-height:1.2;">Métropole Grenoble</div>
            <div style="font-size:10px;color:#95D5B2;opacity:0.8;">Tableau de bord interactif</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 3. BOUTON ACCUEIL (Avec style assorti) ────────────────────────────────
    st.write("") # Petit espace
    if st.button("Retour à l'Accueil", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()

    # ── 4. RADIO NAVIGATION AMÉLIORÉE ────────────────────────────────────────
    st.markdown('<div class="nav-header">Menu Principal</div>', unsafe_allow_html=True)
    
    vue = st.radio(
        "Navigation",
        ["Description", "Démographie", "Solidarité et citoyenneté"],
        index=0,
        label_visibility="collapsed",
    )

    # ── 5. PIED DE PAGE ──────────────────────────────────────────────────────
    st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True) # Espaceur
    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; padding:10px;">
        <div style="font-size:12px; font-weight:600; color:#95D5B2;">Grenoble-Alpes Métropole</div>
        <div style="font-size:10px; color:rgba(255,255,255,0.4); margin-top:10px;">
            Équipe Projet :<br>
            S. Dufaud • H. Unaldi • J. Ben-Hadj-Salem
        </div>
    </div>
    """, unsafe_allow_html=True)
# ──────────────────────────────────────────────────────────────────────────────
# 8. PAGES
# ──────────────────────────────────────────────────────────────────────────────
if vue == "Description":
    st.markdown('<p class="section-header">Description</p>', unsafe_allow_html=True)

    st.markdown("""
    Cette application présente des analyses comparatives sur **5 métropoles françaises** à partir des recensements INSEE 2011, 2016 et 2022.
    Chaque page dispose de ses propres filtres en haut de page, adaptés aux données présentées.
    Selon les onglets, il est possible de filtrer par métropole, par année ou par thématique.
    """)

    st.markdown("---")

    st.markdown("### 🏙️ Périmètre géographique")
    communes_data = {
        "Métropole": list(COMMUNES.keys()),
        "Nombre de communes": [len(v) for v in COMMUNES.values()],
        "Département": ["Isère (38)", "Ille-et-Vilaine (35)", "Seine-Maritime (76)", "Loire (42)", "Hérault (34)"],
    }
    st.dataframe(pd.DataFrame(communes_data).set_index("Métropole"), use_container_width=True)

    st.markdown("---")

    st.markdown("### 🏙️ Volet 1 — Démographie")

    demo_onglets = [
        {
            "titre": "🏙️ Population globale",
            "description": "Évolution et comparaison des populations totales entre métropoles.",
            "source": "INSEE — Données générales comparatives (RP 2011–2022)",
            "lien": "https://www.insee.fr/fr/statistiques/1405599?geo=EPCI-200040715+EPCI-243500139",
        },
        {
            "titre": "👥 Structure par âge",
            "description": "Pyramides des âges, part des jeunes, actifs et seniors.",
            "source": "INSEE — Population par tranche d'âge (RP 2011–2022)",
            "lien": "https://www.insee.fr/fr/statistiques/1893204",
        },
        {
            "titre": "🚌 Mobilités résidentielles",
            "description": "Flux de migrations résidentielles entre communes et métropoles.",
            "source": "INSEE — Migrations résidentielles 2019–2022",
            "lien": "https://www.insee.fr/fr/statistiques/8582988",
        },
        {
            "titre": "🚌 Mobilités professionnelles",
            "description": "Déplacements domicile-travail à l'échelle des métropoles.",
            "source": "INSEE — Mobilité professionnelle 2019–2022",
            "lien": "https://www.insee.fr/fr/statistiques/8582949",
        },
        {
            "titre": "🚌 Mobilités scolaires",
            "description": "Flux de déplacements vers les établissements scolaires.",
            "source": "INSEE — Mobilité scolaire 2019–2022",
            "lien": "https://www.insee.fr/fr/statistiques/8582969",
        },
        {
            "titre": "🏠 Ménages",
            "description": "Taille et composition des ménages selon l'âge et la CSP.",
            "source": "INSEE — Ménages par âge et situation (RP 2011–2022)",
            "lien": "https://www.insee.fr/fr/statistiques/8582448",
        },
        {
            "titre": "📊 CSP comparatif",
            "description": "Structure socioprofessionnelle et indice de spécialisation entre métropoles.",
            "source": "INSEE — Population 25-54 ans par CSP et diplôme (RP 2011–2022)",
            "lien": "https://www.insee.fr/fr/statistiques/1893185",
        },
    ]

    for onglet in demo_onglets:
        with st.expander(onglet["titre"]):
            st.markdown(onglet["description"])
            st.markdown(f"📂 **Source :** {onglet['source']} · [🔗 Accéder]({onglet['lien']})")

    st.markdown("---")

    st.markdown("### 🤝 Volet 2 — Solidarité & citoyenneté")

    solid_onglets = [
        {
            "titre": "🤝 Solidarité",
            "description": "Analyse des données CAF : foyers bénéficiaires, montants versés, évolution temporelle.",
            "sources": [
                ("INSEE — Filosofi : âge, type de ménage, niveau de vie", "https://catalogue-donnees.insee.fr/fr/catalogue/recherche/DS_FILOSOFI_AGE_TP_NIVVIE"),
                ("CAF — Allocataires par commune (NDUR)", "https://data.caf.fr/explore/dataset/ndur_s_qf_400_com_f/table/"),
                ("CAF — Bénéficiaires par commune (complément)", "https://data.caf.fr/explore/dataset/s_ben_com_f/table/"),
                ("INSEE — Données générales comparatives EPCI", "https://www.insee.fr/fr/statistiques/1405599?geo=EPCI-200040715+EPCI-243500139"),
            ],
        },
        {
            "titre": "🎓 Éducation",
            "description": "Analyse des niveaux de diplôme et de la scolarisation par métropole. *(à venir)*",
            "sources": [
                ("INSEE — Statistiques locales (diplômes, scolarisation)", "https://www.insee.fr/fr/statistiques/8307327?sommaire=2500477"),
            ],
        },
        {
            "titre": "🏥 Santé",
            "description": "Cartographie et analyse des équipements de santé. *(à venir)*",
            "sources": [
                ("OpenData — Équipements de santé OSM France", "https://smartregionidf.opendatasoft.com/explore/dataset/osm-france-healthcare/table/"),
            ],
        },
        {
            "titre": "🗳️ Participation citoyenne",
            "description": "Taux de participation et résultats des élections municipales 2020. *(à venir)*",
            "sources": [
                ("Data.gouv — Élections municipales 2020 (1er tour)", "https://www.data.gouv.fr/datasets/elections-municipales-2020-resultats-1er-tour/"),
            ],
        },
        {
            "titre": "🗄️ Base de données",
            "description": "Accès aux données brutes consolidées. *(à venir)*",
            "sources": [
                ("INSEE — Statistiques complémentaires", "https://www.insee.fr/fr/statistiques/8582448?sommaire=8582455"),
            ],
        },
    ]

    for onglet in solid_onglets:
        with st.expander(onglet["titre"]):
            st.markdown(onglet["description"])
            for source, lien in onglet["sources"]:
                st.markdown(f"📂 **Source :** {source} · [🔗 Accéder]({lien})")

    st.markdown("---")

    st.markdown("""
    <p class="source-note">Sources : INSEE — Recensements de la Population 2011, 2016, 2022 ·
    Mobilités résidentielles, professionnelles et scolaires 2019–2022 · CAF — 5 métropoles · Data.gouv · OpenData IDF</p>
    """, unsafe_allow_html=True)

    st.stop()

if vue == "Démographie":
    tab1, tab2, tab3, tab4, tab6 = st.tabs([
        "🏙️  Population globale",
        "👥  Structure par âge",
        "🚌  Mobilités",
        "🏠  Ménages",
        "📊  CSP comparatif",
    ])

# ==============================================================================
# ONGLET 1 — POPULATION GLOBALE
# ==============================================================================
if vue == "Démographie":
    with tab1:
        st.markdown(
            '<p class="source-note">Source : '
            '<a href="https://www.insee.fr/fr/statistiques/1405599" target="_blank">'
            'INSEE — Données générales comparatives (RP 2022)</a></p>',
            unsafe_allow_html=True,
        )

        # ── Helper commune (Grenoble uniquement dans df_gen) ─────────────────
        def commune_val(commune, col):
            if df_gen is None:
                return np.nan
            comm_norm = normalize_name(commune)
            geo = df_gen["territoire"].astype(str).str.extract(
                r"^(Commune|EPCI)\s*:\s*(.*?)\s*\(\d+\)\s*$"
            )
            mask = (geo[0] == "Commune") & (geo[1].apply(normalize_name) == comm_norm)
            rows = df_gen[mask]
            if rows.empty:
                return np.nan
            v = rows.iloc[0].get(col, np.nan)
            return float(v) if pd.notna(v) else np.nan

        # ── Bandeau filtres ──────────────────────────────────────────────────
        with st.container():
            st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
            filter_bar("🔧 Filtres — Population globale")
            pg_c1, pg_c2 = st.columns(2)
            with pg_c1:
                mode_pop = st.radio(
                    "Niveau géographique",
                    ["Comparaison Métropoles", "Détail Communal (Grenoble)"],
                    key="pop_mode", horizontal=True,
                )
            if mode_pop == "Comparaison Métropoles":
                sel = st.multiselect("Métropoles à comparer", TOUTES, default=TOUTES, key="sel_t1")
            else:
                with pg_c2:
                    pass  # pas de filtre métropole parente : c'est toujours Grenoble
                sel_communes_pop = st.multiselect(
                    "Communes de Grenoble", sorted(COMMUNES["Grenoble"]),
                    default=sorted(COMMUNES["Grenoble"])[:2], key="pop_communes",
                )
            st.markdown('</div>', unsafe_allow_html=True)

        # ════════════════════════════════════════════════════════════════════
        # VUE DÉTAIL COMMUNAL (Grenoble)
        # ════════════════════════════════════════════════════════════════════
        if mode_pop == "Détail Communal (Grenoble)":
            if not sel_communes_pop:
                st.warning("Sélectionnez au moins une commune.")
                st.stop()

            COLORS_COMM = ["#2D6A4F", "#95D5B2", "#1A6FA3", "#C45B2A", "#D4A017",
                           "#7B3FA0", "#74C69D", "#F4A261", "#264653", "#E9C46A"]

            st.markdown(
                "<h2 style='color:#1C3A27;font-size:1.4rem;margin:0 0 4px'>🏘️ Population — Communes de Grenoble</h2>"
                f"<p style='color:#5A8A6A;font-size:0.82rem;margin-bottom:18px'>"
                f"Communes sélectionnées : {', '.join(sel_communes_pop)}</p>",
                unsafe_allow_html=True,
            )

            # ── KPIs ─────────────────────────────────────────────────────────
            kpi_cols = st.columns(len(sel_communes_pop))
            for i, comm in enumerate(sel_communes_pop):
                pop22 = commune_val(comm, "population_2022")
                with kpi_cols[i]:
                    st.metric(label=f"🏘️ {comm}", value=fmt(pop22))

            st.markdown("---")

            # ── Graphique 1 : Population 2022 ────────────────────────────────
            st.markdown("#### 📊 Population et indicateurs")
            r1c1, r1c2 = st.columns(2)
            with r1c1:
                st.markdown("##### Population totale 2022 (habitants)")
                data_comm = [{"Commune": c, "Population": commune_val(c, "population_2022"),
                              "Couleur": COLORS_COMM[i % len(COLORS_COMM)]}
                             for i, c in enumerate(sel_communes_pop)]
                df_comm22 = pd.DataFrame(data_comm).dropna(subset=["Population"]).sort_values("Population", ascending=False)
                if not df_comm22.empty:
                    fig_pop_c = go.Figure()
                    for _, row_c in df_comm22.iterrows():
                        fig_pop_c.add_trace(go.Bar(
                            x=[row_c["Commune"]], y=[row_c["Population"]],
                            name=row_c["Commune"], marker_color=row_c["Couleur"],
                            text=[f"{int(row_c['Population']):,}".replace(",", "\u202f")],
                            textposition="outside", showlegend=False,
                        ))
                    fig_pop_c.update_layout(showlegend=False, yaxis_title="Habitants",
                                            yaxis=dict(tickformat=",d"), height=370)
                    st.plotly_chart(style(fig_pop_c), use_container_width=True)

            with r1c2:
                st.markdown("##### Densité (hab/km²)")
                data_dens_c = []
                for i, c in enumerate(sel_communes_pop):
                    d = commune_val(c, "densite_2022")
                    s = commune_val(c, "superficie_km2_2022")
                    p = commune_val(c, "population_2022")
                    if not any(np.isnan(v) for v in [d, s, p]):
                        data_dens_c.append({"Commune": c, "Densité (hab/km²)": d,
                                            "Superficie (km²)": s, "Population": p,
                                            "Couleur": COLORS_COMM[i % len(COLORS_COMM)]})
                df_dens_c = pd.DataFrame(data_dens_c)
                if not df_dens_c.empty:
                    fig_dens_c = px.scatter(df_dens_c, x="Superficie (km²)", y="Densité (hab/km²)",
                                            size="Population", color="Commune", text="Commune",
                                            color_discrete_sequence=COLORS_COMM, size_max=55, height=370)
                    fig_dens_c.update_traces(textposition="top center", textfont_size=10)
                    fig_dens_c.update_layout(showlegend=False)
                    st.plotly_chart(style(fig_dens_c), use_container_width=True)

            st.markdown("---")

            # ── Graphique 2 : Revenus, pauvreté, chômage ────────────────────
            st.markdown("#### 💶 Revenus, pauvreté & chômage")
            r3c1, r3c2, r3c3 = st.columns(3)
            with r3c1:
                st.markdown("##### Revenu médian 2021 (€/an)")
                data_rev_c = [{"Commune": c, "Revenu médian (€)": commune_val(c, "revenu_median_2021")}
                              for c in sel_communes_pop]
                df_rev_c = pd.DataFrame(data_rev_c).dropna().sort_values("Revenu médian (€)")
                if not df_rev_c.empty:
                    fig_rev_c = px.bar(df_rev_c, x="Revenu médian (€)", y="Commune", orientation="h",
                                       color_discrete_sequence=["#2D6A4F"], text_auto=".0f", height=370)
                    fig_rev_c.update_layout(showlegend=False, xaxis_title="€/an")
                    st.plotly_chart(style(fig_rev_c), use_container_width=True)

            with r3c2:
                st.markdown("##### Taux de pauvreté 2021 (%)")
                data_pauv_c = [{"Commune": c, "Taux de pauvreté (%)": commune_val(c, "tx_pauvrete_2021")}
                               for c in sel_communes_pop]
                df_pauv_c = pd.DataFrame(data_pauv_c).dropna().sort_values("Taux de pauvreté (%)", ascending=False)
                if not df_pauv_c.empty:
                    colors_pauv_c = ["#C45B2A" if v > 15 else "#D4A017" if v > 12 else "#2D6A4F"
                                     for v in df_pauv_c["Taux de pauvreté (%)"]]
                    fig_pauv_c = go.Figure(go.Bar(
                        y=df_pauv_c["Commune"], x=df_pauv_c["Taux de pauvreté (%)"], orientation="h",
                        marker_color=colors_pauv_c,
                        text=[f"{v:.1f}%" for v in df_pauv_c["Taux de pauvreté (%)"]],
                        textposition="inside",
                    ))
                    fig_pauv_c.update_layout(xaxis_title="%", showlegend=False, height=370)
                    st.plotly_chart(style(fig_pauv_c), use_container_width=True)

            with r3c3:
                st.markdown("##### Taux de chômage (%)")
                data_chom_c = [{"Commune": c, "Taux de chômage (%)": commune_val(c, "tx_chomage_15_64")}
                               for c in sel_communes_pop]
                df_chom_c = pd.DataFrame(data_chom_c).dropna().sort_values("Taux de chômage (%)", ascending=False)
                if not df_chom_c.empty:
                    fig_chom_c = px.bar(df_chom_c, x="Commune", y="Taux de chômage (%)",
                                        color="Taux de chômage (%)",
                                        color_continuous_scale="RdYlGn_r",
                                        text=[f"{v:.1f}%" for v in df_chom_c["Taux de chômage (%)"]],
                                        height=370)
                    fig_chom_c.update_traces(textposition="outside")
                    fig_chom_c.update_layout(coloraxis_showscale=False, xaxis_tickangle=-30,
                                             yaxis_title="Taux de chômage (%)")
                    st.plotly_chart(style(fig_chom_c), use_container_width=True)

            st.markdown("---")
            st.markdown("#### 📋 Tableau récapitulatif")
            lignes_tab_c = []
            for comm in sel_communes_pop:
                pop22 = commune_val(comm, "population_2022")
                dens  = commune_val(comm, "densite_2022")
                rev   = commune_val(comm, "revenu_median_2021")
                pauv  = commune_val(comm, "tx_pauvrete_2021")
                tc    = commune_val(comm, "tx_chomage_15_64")
                lignes_tab_c.append({
                    "Commune": comm,
                    "Population 2022": fmt(pop22),
                    "Densité (hab/km²)": fmt(dens),
                    "Revenu médian": fmt(rev, " €"),
                    "Taux pauvreté": f"{pauv:.1f}%" if not np.isnan(pauv) else "N/D",
                    "Taux chômage": f"{tc:.1f}%" if not np.isnan(tc) else "N/D",
                })
            st.dataframe(pd.DataFrame(lignes_tab_c).set_index("Commune"), use_container_width=True)
            st.caption("Sources : INSEE — Données générales comparatives (RP 2022).")

        # ════════════════════════════════════════════════════════════════════
        # VUE COMPARAISON MÉTROPOLES
        # ════════════════════════════════════════════════════════════════════
        else:
            if not sel:
                st.warning("Sélectionnez au moins une métropole.")
                st.stop()

            st.markdown(
                "<h2 style='color:#1C3A27;font-size:1.4rem;margin:0 0 4px'>🏙️ Population globale</h2>"
                "<p style='color:#5A8A6A;font-size:0.82rem;margin-bottom:18px'>"
                "Vue d'ensemble comparative des 5 métropoles — Données INSEE RP 2022</p>",
                unsafe_allow_html=True,
            )
            kpi_cols = st.columns(len(sel))
            for i, m in enumerate(sel):
                pop22  = epci_val(m, "population_2022")
                tx_var = epci_val(m, "tx_var_population_2016_2022")
                nais   = epci_val(m, "naissances_2024")
                deces  = epci_val(m, "deces_2024")
                with kpi_cols[i]:
                    delta_str = f"{tx_var:+.2f} %/an" if not np.isnan(tx_var) else None
                    st.metric(label=f"🌿 {m}", value=fmt(pop22), delta=delta_str,
                              help=f"Naissances 2024 : {fmt(nais)} · Décès 2024 : {fmt(deces)}")

            st.markdown("---")
            st.markdown("#### 📊 Population et densité territoriale")
            r1c1, r1c2 = st.columns(2)
            with r1c1:
                st.markdown("##### Population totale 2022 (habitants)")
                data_pop_df = [{"Métropole": m, "Population": epci_val(m, "population_2022")} for m in sel]
                df_pop22 = pd.DataFrame(data_pop_df).dropna().sort_values("Population", ascending=False)
                if not df_pop22.empty:
                    fig_pop = go.Figure()
                    for _, row_p in df_pop22.iterrows():
                        fig_pop.add_trace(go.Bar(
                            x=[row_p["Métropole"]], y=[row_p["Population"]],
                            name=row_p["Métropole"], marker_color=COULEURS.get(row_p["Métropole"], "#888"),
                            text=[f"{int(row_p['Population']):,}".replace(",", "\u202f")],
                            textposition="outside", showlegend=False,
                        ))
                    fig_pop.update_layout(showlegend=False, yaxis_title="Habitants",
                                          yaxis=dict(tickformat=",d"), height=370)
                    st.plotly_chart(style(fig_pop), use_container_width=True)
            with r1c2:
                st.markdown("##### Densité (hab/km²) vs Superficie (km²)")
                data_dens = []
                for m in sel:
                    d = epci_val(m, "densite_2022")
                    s = epci_val(m, "superficie_km2_2022")
                    p = epci_val(m, "population_2022")
                    if not any(np.isnan(v) for v in [d, s, p]):
                        data_dens.append({"Métropole": m, "Densité (hab/km²)": d,
                                          "Superficie (km²)": s, "Population": p})
                df_dens = pd.DataFrame(data_dens)
                if not df_dens.empty:
                    fig_dens = px.scatter(df_dens, x="Superficie (km²)", y="Densité (hab/km²)",
                                          size="Population", color="Métropole",
                                          color_discrete_map=COULEURS, text="Métropole",
                                          size_max=55, height=370)
                    fig_dens.update_traces(textposition="top center", textfont_size=11)
                    fig_dens.update_layout(showlegend=False)
                    st.plotly_chart(style(fig_dens), use_container_width=True)

            st.markdown("---")
            st.markdown("#### ⚖️ Composantes de la variation démographique")
            r2c1, r2c2 = st.columns(2)
            with r2c1:
                st.markdown("##### Soldes naturel et migratoire (%/an, 2016–2022)")
                rows_comp = []
                for m in sel:
                    sn  = epci_val(m, "tx_solde_naturel")
                    sm  = epci_val(m, "tx_solde_migratoire")
                    tot = epci_val(m, "tx_var_population_2016_2022")
                    if not all(np.isnan(v) for v in [sn, sm, tot]):
                        rows_comp.append({"Métropole": m, "Solde naturel": sn,
                                          "Solde migratoire": sm, "Variation totale": tot})
                if rows_comp:
                    df_comp = pd.DataFrame(rows_comp).melt(
                        id_vars="Métropole", var_name="Composante", value_name="Taux (%/an)").dropna()
                    COLOR_COMP = {"Solde naturel": "#74C69D", "Solde migratoire": "#1A6FA3",
                                  "Variation totale": "#2D6A4F"}
                    fig_comp = px.bar(df_comp, x="Métropole", y="Taux (%/an)", color="Composante",
                                      barmode="group", color_discrete_map=COLOR_COMP, height=360)
                    fig_comp.add_hline(y=0, line_dash="dot", line_color="#AAAAAA")
                    fig_comp.update_layout(legend=dict(orientation="h", y=1.12))
                    st.plotly_chart(style(fig_comp), use_container_width=True)
            with r2c2:
                st.markdown("##### Naissances & Décès 2024 (radar comparatif)")
                rows_vit = []
                for m in sel:
                    nais = epci_val(m, "naissances_2024")
                    decs = epci_val(m, "deces_2024")
                    pop  = epci_val(m, "population_2022")
                    if not any(np.isnan(v) for v in [nais, decs, pop]):
                        rows_vit.append({"Métropole": m,
                                         "Naissances/1 000 hab": nais / pop * 1000,
                                         "Décès/1 000 hab": decs / pop * 1000,
                                         "Accroissement naturel": (nais - decs) / pop * 1000})
                df_vit = pd.DataFrame(rows_vit)
                if not df_vit.empty:
                    fig_vit = go.Figure()
                    categories = ["Naissances/1 000 hab", "Décès/1 000 hab", "Accroissement naturel"]
                    for _, row_v in df_vit.iterrows():
                        fig_vit.add_trace(go.Scatterpolar(
                            r=[row_v[c] for c in categories] + [row_v[categories[0]]],
                            theta=categories + [categories[0]],
                            fill="toself", name=row_v["Métropole"],
                            line_color=COULEURS.get(row_v["Métropole"], "#888"), opacity=0.75,
                        ))
                    fig_vit.update_layout(polar=dict(radialaxis=dict(visible=True)),
                                          legend=dict(orientation="h", y=-0.15), height=360)
                    st.plotly_chart(style(fig_vit), use_container_width=True)

            st.markdown("---")
            st.markdown("#### 💶 Revenus, pauvreté & chômage")
            r4c1, r4c2, r4c3 = st.columns(3)
            with r4c1:
                st.markdown("##### Revenu médian 2021 (€/an)")
                data_rev = [{"Métropole": m, "Revenu médian (€)": epci_val(m, "revenu_median_2021")} for m in sel]
                df_rev = pd.DataFrame(data_rev).dropna().sort_values("Revenu médian (€)")
                if not df_rev.empty:
                    fig_rev = px.bar(df_rev, x="Revenu médian (€)", y="Métropole", orientation="h",
                                     color="Métropole", color_discrete_map=COULEURS,
                                     text_auto=".0f", height=300)
                    fig_rev.update_layout(showlegend=False, xaxis_title="€/an")
                    st.plotly_chart(style(fig_rev), use_container_width=True)
            with r4c2:
                st.markdown("##### Taux de pauvreté 2021 (%)")
                data_pauv = [{"Métropole": m, "Taux de pauvreté (%)": epci_val(m, "tx_pauvrete_2021")} for m in sel]
                df_pauv = pd.DataFrame(data_pauv).dropna().sort_values("Taux de pauvreté (%)", ascending=False)
                if not df_pauv.empty:
                    colors_pauv = ["#C45B2A" if v > 15 else "#D4A017" if v > 12 else "#2D6A4F"
                                   for v in df_pauv["Taux de pauvreté (%)"]]
                    fig_pauv = go.Figure(go.Bar(
                        y=df_pauv["Métropole"], x=df_pauv["Taux de pauvreté (%)"], orientation="h",
                        marker_color=colors_pauv,
                        text=[f"{v:.1f}%" for v in df_pauv["Taux de pauvreté (%)"]],
                        textposition="inside",
                    ))
                    fig_pauv.update_layout(xaxis_title="%", showlegend=False, height=300)
                    st.plotly_chart(style(fig_pauv), use_container_width=True)
            with r4c3:
                st.markdown("##### Taux de chômage 15–64 ans (%)")
                data_chom = [{"Métropole": m, "Taux de chômage (%)": epci_val(m, "tx_chomage_15_64")} for m in sel]
                df_chom = pd.DataFrame(data_chom).dropna().sort_values("Taux de chômage (%)", ascending=False)
                if not df_chom.empty:
                    fig_chom = px.bar(df_chom, x="Métropole", y="Taux de chômage (%)",
                                      color="Taux de chômage (%)",
                                      color_continuous_scale="RdYlGn_r",
                                      text=[f"{v:.1f}%" for v in df_chom["Taux de chômage (%)"]],
                                      height=300)
                    fig_chom.update_traces(textposition="outside")
                    fig_chom.update_layout(coloraxis_showscale=False,
                                           yaxis_title="Taux de chômage (%)")
                    st.plotly_chart(style(fig_chom), use_container_width=True)

            st.markdown("---")
            st.markdown("#### 📋 Tableau récapitulatif — indicateurs clés")
            lignes_tab = []
            for m in sel:
                tx_v  = epci_val(m, "tx_var_population_2016_2022")
                tc    = epci_val(m, "tx_chomage_15_64")
                rev   = epci_val(m, "revenu_median_2021")
                pauv  = epci_val(m, "tx_pauvrete_2021")
                dens  = epci_val(m, "densite_2022")
                lignes_tab.append({
                    "Métropole": m,
                    "Population 2022": fmt(epci_val(m, "population_2022")),
                    "Densité (hab/km²)": fmt(dens),
                    "Var. pop./an": f"{tx_v:+.2f}%" if not np.isnan(tx_v) else "N/D",
                    "Solde naturel/an": f"{epci_val(m,'tx_solde_naturel'):+.2f}%" if not np.isnan(epci_val(m,'tx_solde_naturel')) else "N/D",
                    "Solde migrat./an": f"{epci_val(m,'tx_solde_migratoire'):+.2f}%" if not np.isnan(epci_val(m,'tx_solde_migratoire')) else "N/D",
                    "Taux chômage": f"{tc:.1f}%" if not np.isnan(tc) else "N/D",
                    "Revenu médian": fmt(rev, " €"),
                    "Taux pauvreté": f"{pauv:.1f}%" if not np.isnan(pauv) else "N/D",
                    "Nb. ménages": fmt(epci_val(m, "nb_menages_2022")),
                    "Emploi total": fmt(epci_val(m, "emploi_total_2022")),
                })
            df_tab = pd.DataFrame(lignes_tab).set_index("Métropole")
            st.dataframe(df_tab, use_container_width=True)

            st.markdown("---")
            st.markdown("#### 🗺️ Carte des communes — Grenoble-Alpes-Métropole")
            st.caption("Carte statique · Population 2022 par commune · Source : geo.api.gouv.fr & INSEE")

            @st.cache_data(show_spinner="Chargement de la carte...")
            def charger_geojson_grenoble():
                import requests
                url = "https://geo.api.gouv.fr/communes?codeEpci=200040715&format=geojson&geometry=contour"
                try:
                    r = requests.get(url, timeout=10)
                    return r.json()
                except Exception:
                    return None

            geojson = charger_geojson_grenoble()

            if geojson is None:
                st.warning("Impossible de charger la carte (vérifiez la connexion internet).")
            elif df_gen is None:
                st.warning("Données df_gen non chargées.")
            else:
                # Construire le DataFrame des communes Grenoble avec population 2022
                rows_carte = []
                for feat in geojson["features"]:
                    nom = feat["properties"].get("nom", "")
                    code = feat["properties"].get("code", "")
                    pop = np.nan
                    # Cherche dans df_gen par nom de commune
                    match = df_gen[df_gen["territoire"] == nom]
                    if not match.empty:
                        pop = match.iloc[0].get("population_2022", np.nan)
                        try:
                            pop = float(pop)
                        except Exception:
                            pop = np.nan
                    rows_carte.append({"nom": nom, "code": code, "population_2022": pop})

                df_carte = pd.DataFrame(rows_carte)

                fig_carte = px.choropleth_mapbox(
                    df_carte,
                    geojson=geojson,
                    locations="nom",
                    featureidkey="properties.nom",
                    color="population_2022",
                    color_continuous_scale="Greens",
                    mapbox_style="carto-positron",
                    zoom=9.5,
                    center={"lat": 45.18, "lon": 5.72},
                    opacity=0.75,
                    labels={"population_2022": "Population 2022", "nom": "Commune"},
                    hover_name="nom",
                    hover_data={"population_2022": ":,.0f", "nom": False},
                    height=550,
                )
                fig_carte.update_layout(
                    margin=dict(t=0, b=0, l=0, r=0),
                    coloraxis_colorbar=dict(
                        title="Population<br>2022",
                        thickness=14,
                        len=0.6,
                    ),
                )
                st.plotly_chart(style(fig_carte, 0), use_container_width=True)
                
            st.caption("Sources : INSEE — Données générales comparatives (RP 2022).")
            
# ==============================================================================
# ONGLET 2 — STRUCTURE PAR ÂGE
# ==============================================================================
if vue == "Démographie":
    with tab2:
        st.markdown('<p class="section-header">Structure par âge et par sexe</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="source-note">Source : <a href="https://www.insee.fr/fr/statistiques/1893204" target="_blank">'
            'INSEE — Population par tranche d\'âge quinquennal (RP 2011, 2016, 2022)</a></p>',
            unsafe_allow_html=True,
        )
        if df_pop is None:
            st.info("📂 Fichier `Population_tranche_age_clean.csv` introuvable.")
        else:
            annees = sorted(df_pop["annee"].dropna().unique().astype(int).tolist())
            ch = cols_h(df_pop)
            cf = cols_f(df_pop)

            # ── Bandeau filtres ──────────────────────────────────────────────
            with st.container():
                st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
                filter_bar("🔧 Filtres — Structure par âge")
                fa1, fa2, fa3 = st.columns(3)
                with fa1:
                    mode_age = st.radio(
                        "Niveau géographique",
                        ["Comparaison Métropoles", "Détail Communal"],
                        key="age_mode", horizontal=True,
                    )
                with fa2:
                    metro_age = st.selectbox("Métropole parente", TOUTES, key="metro_age")
                with fa3:
                    annee_age = st.selectbox("Année", annees, index=len(annees)-1, key="an_age")
                if mode_age == "Détail Communal":
                    cmns = sorted(COMMUNES.get(metro_age, []))
                    sel_communes_age = st.multiselect(
                        "Communes", cmns, default=cmns[:2], key="age_communes",
                    )
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("---")

            if mode_age == "Détail Communal":
                communes_age = sel_communes_age if sel_communes_age else []
                if not communes_age:
                    st.info("Sélectionnez au moins une commune.")
                elif len(communes_age) == 1:
                    comm = communes_age[0]
                    st.markdown(f"##### Pyramide des âges — {comm} ({annee_age})")
                    df_c = df_pop[(df_pop["LIBELLE"] == comm) & (df_pop["annee"] == annee_age)]
                    if not df_c.empty and ch and cf:
                        labels = [label_col(c) for c in ch]
                        fig_p = go.Figure()
                        fig_p.add_trace(go.Bar(y=labels, x=[-df_c[c].sum() for c in ch],
                                               name="Hommes", orientation="h", marker_color="#2D6A4F"))
                        fig_p.add_trace(go.Bar(y=labels, x=[df_c[c].sum() for c in cf],
                                               name="Femmes", orientation="h", marker_color="#95D5B2"))
                        fig_p.update_layout(barmode="relative", bargap=0.06,
                                            legend=dict(orientation="h", y=1.08),
                                            yaxis_title="Tranche d'âge (ans)", xaxis_title="Population")
                        st.plotly_chart(style(fig_p, 40), use_container_width=True)
                    else:
                        st.info("Données insuffisantes pour cette commune.")
                else:
                    st.markdown(f"##### Comparaison — {' · '.join(communes_age)} ({annee_age})")
                    rows_c = []
                    for comm in communes_age:
                        df_c = df_pop[(df_pop["LIBELLE"] == comm) & (df_pop["annee"] == annee_age)]
                        if not df_c.empty and ch and cf:
                            for h, f in zip(ch, cf):
                                rows_c.append({"Tranche": label_col(h), "Commune": comm,
                                               "Population": df_c[h].sum() + df_c[f].sum()})
                    if rows_c:
                        fig_cc = px.bar(pd.DataFrame(rows_c), x="Tranche", y="Population", color="Commune",
                                        barmode="group",
                                        color_discrete_sequence=["#2D6A4F", "#95D5B2", "#1A6FA3",
                                                                  "#C45B2A", "#D4A017"])
                        fig_cc.update_layout(xaxis_tickangle=-40, legend=dict(orientation="h", y=1.08))
                        st.plotly_chart(style(fig_cc), use_container_width=True)
                    else:
                        st.info("Données insuffisantes pour ces communes.")

            else:
                # ── Vue métropole ────────────────────────────────────────────
                df_m = df_pop[(df_pop["metropole"] == metro_age) & (df_pop["annee"] == annee_age)]
                st.markdown(f"##### Pyramide des âges — {metro_age} ({annee_age})")
                if ch and cf and not df_m.empty:
                    labels = [label_col(c) for c in ch]
                    fig_p = go.Figure()
                    fig_p.add_trace(go.Bar(y=labels, x=[-df_m[c].sum() for c in ch],
                                           name="Hommes", orientation="h", marker_color="#2D6A4F"))
                    fig_p.add_trace(go.Bar(y=labels, x=[df_m[c].sum() for c in cf],
                                           name="Femmes", orientation="h", marker_color="#95D5B2"))
                    fig_p.update_layout(barmode="relative", bargap=0.06,
                                        legend=dict(orientation="h", y=1.08),
                                        yaxis_title="Tranche d'âge (ans)", xaxis_title="Population")
                    st.plotly_chart(style(fig_p, 40), use_container_width=True)
                else:
                    st.info("Données insuffisantes pour la pyramide.")

            # ── Indices démographiques (toujours affichés) ───────────────────
            st.markdown("---")
            st.markdown("##### Indices démographiques par métropole")
            idx_c = st.columns(len(TOUTES))
            for i, m in enumerate(TOUTES):
                dm = df_pop[(df_pop["metropole"] == m) & (df_pop["annee"] == annee_age)]
                pj = somme_tranches(dm, TRANCHES_JEUNES)
                pa = somme_tranches(dm, TRANCHES_ACTIFS)
                ps = somme_tranches(dm, TRANCHES_SENIORS)
                iv = (ps / pj * 100) if pj > 0 else np.nan
                rd = ((pj + ps) / pa * 100) if pa > 0 else np.nan
                with idx_c[i]:
                    st.metric(f"Vieillissement\n{m}", f"{iv:.0f}" if not np.isnan(iv) else "N/D",
                              help="65+ / <20 ans × 100")
                    st.metric(f"Dépendance\n{m}", f"{rd:.0f}%" if not np.isnan(rd) else "N/D",
                              help="(Jeunes + Seniors) / Actifs")

            st.markdown("---")
            st.markdown("##### Évolution de la population totale (2011 → 2022)")
            sel_evol = st.multiselect("Métropoles", TOUTES, default=["Grenoble", "Rennes"], key="evol")
            if sel_evol and ch and cf:
                df_e = df_pop[df_pop["metropole"].isin(sel_evol)].copy()
                df_e["pop_totale"] = df_e[[c for c in ch + cf if c in df_e.columns]].sum(axis=1)
                df_g = df_e.groupby(["metropole", "annee"])["pop_totale"].sum().reset_index()
                fig_ev = px.line(df_g, x="annee", y="pop_totale", color="metropole",
                                 color_discrete_map=COULEURS, markers=True)
                fig_ev.update_layout(yaxis_title="Population totale", xaxis_title="Année",
                                     legend_title="Métropole")
                st.plotly_chart(style(fig_ev), use_container_width=True)

# ==============================================================================
# ONGLET 3 — MOBILITÉS
# ==============================================================================
if vue == "Démographie":
    with tab3:
        st.markdown('<p class="section-header">Observatoire des mobilités</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="source-note">Source : INSEE — Migrations résidentielles, '
            'Mobilités professionnelles & scolaires (RP 2019–2022) · '
            'Les flux internes à une même commune sont exclus.</p>',
            unsafe_allow_html=True,
        )

        data_ok = any(df is not None for df in [df_res, df_prof, df_scol])
        if not data_ok:
            st.info(
                "📂 Aucun fichier de mobilité trouvé dans `demographie/data_clean/mobilite/`. "
                "Fichiers attendus : `Migrations_resid_clean.csv`, `Mobilite_profess_clean.csv`, "
                "`Mobilite_scolaire_clean.csv`."
            )
        else:
            # ── Bandeau filtres ──────────────────────────────────────────────
            with st.container():
                st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
                filter_bar("🔧 Filtres — Mobilités")

                mob_col1, mob_col2, mob_col3 = st.columns(3)
                with mob_col1:
                    theme_mob = st.selectbox(
                        "Thématique d'analyse",
                        ["🏠 Migrations Résidentielles",
                         "💼 Mobilité Professionnelle",
                         "🎓 Mobilité Scolaire"],
                        key="mob_theme",
                        label_visibility="visible",
                    )
                with mob_col2:
                    mode_mob = st.radio(
                        "Niveau géographique",
                        ["Détail Communal", "Comparaison Métropoles"],
                        key="mob_mode",
                        horizontal=True,
                    )

                # Sélection du DataFrame selon la thématique
                if "Migrations" in theme_mob:
                    current_mob_df = df_res
                    col_orig, col_dest = "commune_origine", "commune_destination"
                    label_in, label_out = "Nouveaux Arrivants", "Départs"
                    color_in, color_out = "#2D6A4F", "#B7E4C7"
                elif "Professionnelle" in theme_mob:
                    current_mob_df = df_prof
                    col_orig, col_dest = "commune_residence", "commune_travail"
                    label_in, label_out = "Travailleurs Entrants", "Résidents Sortants"
                    color_in, color_out = "#1A6FA3", "#AED4F0"
                else:
                    current_mob_df = df_scol
                    col_orig, col_dest = "commune_origine", "commune_destination"
                    label_in, label_out = "Élèves/Étudiants Entrants", "Élèves/Étudiants Sortants"
                    color_in, color_out = "#7B3FA0", "#D5B8F0"

                if current_mob_df is not None:
                    annees_mob = sorted(current_mob_df["annee"].dropna().unique().astype(int), reverse=True)
                    with mob_col3:
                        sel_annee_mob = st.selectbox("Année", annees_mob, key="mob_annee")

                # Sélection entités (communes ou métropoles) — dans le même bandeau
                if current_mob_df is not None:
                    if mode_mob == "Détail Communal":
                        geo_col1, geo_col2 = st.columns(2)
                        with geo_col1:
                            met_choice = st.selectbox("Métropole parente", TOUTES, key="mob_met")
                        with geo_col2:
                            sel_communes_mob = st.multiselect(
                                "Communes", sorted(COMMUNES[met_choice]),
                                default=sorted(COMMUNES[met_choice])[:2], key="mob_communes",
                            )
                    else:
                        sel_metros_mob = st.multiselect(
                            "Métropoles à comparer", TOUTES, default=TOUTES[:3], key="mob_metros",
                        )

                st.markdown('</div>', unsafe_allow_html=True)

            if current_mob_df is None:
                st.warning(f"📂 Données non disponibles pour '{theme_mob}'.")
            else:
                df_mob_filtered = current_mob_df[
                    (current_mob_df[col_orig] != current_mob_df[col_dest]) &
                    (current_mob_df["annee"] == sel_annee_mob)
                ]

                entities_mob = []
                if mode_mob == "Détail Communal":
                    for ent in sel_communes_mob:
                        f_in  = df_mob_filtered[df_mob_filtered[col_dest] == ent]["flux"].sum()
                        f_out = df_mob_filtered[df_mob_filtered[col_orig] == ent]["flux"].sum()
                        entities_mob.append({"name": ent, "in": f_in, "out": f_out, "solde": f_in - f_out})
                    coms_selection = sel_communes_mob
                else:
                    for m_name in sel_metros_mob:
                        coms = COMMUNES[m_name]
                        f_in  = df_mob_filtered[df_mob_filtered[col_dest].isin(coms)]["flux"].sum()
                        f_out = df_mob_filtered[df_mob_filtered[col_orig].isin(coms)]["flux"].sum()
                        entities_mob.append({"name": m_name, "in": f_in, "out": f_out, "solde": f_in - f_out})
                    coms_selection = [c for m in sel_metros_mob for c in COMMUNES[m]]

                df_plot_mob = pd.DataFrame(entities_mob)

                tab_dash_mob, tab_method_mob = st.tabs(["📊 Tableau de Bord", "📘 Guide & Méthodologie"])

                with tab_dash_mob:
                    if df_plot_mob.empty:
                        st.warning("⚠️ Sélectionnez des éléments dans les filtres ci-dessus.")
                    else:
                        st.markdown(f"#### 📌 Bilan net — {theme_mob} · {sel_annee_mob}")
                        kpi_mob_cols = st.columns(len(df_plot_mob))
                        for i, row in df_plot_mob.iterrows():
                            color_solde = "#2ecc71" if row["solde"] >= 0 else "#e74c3c"
                            with kpi_mob_cols[i]:
                                st.markdown(f"""
                                <div class='kpi-card-mob'>
                                    <div class='kpi-label'>{row['name']}</div>
                                    <div class='kpi-value'>{int(row['solde']):+,d}</div>
                                    <div style='color:{color_solde}; font-size:12px; font-weight:bold;'>BILAN NET</div>
                                </div>
                                """, unsafe_allow_html=True)

                        st.markdown("---")
                        c1, c2 = st.columns(2)
                        with c1:
                            st.markdown("##### ⚖️ Volume des échanges")
                            fig_vol = go.Figure()
                            fig_vol.add_trace(go.Bar(x=df_plot_mob["name"], y=df_plot_mob["in"],
                                                     name=label_in, marker_color=color_in))
                            fig_vol.add_trace(go.Bar(x=df_plot_mob["name"], y=df_plot_mob["out"],
                                                     name=label_out, marker_color=color_out))
                            fig_vol.update_layout(barmode="group", height=380,
                                                  legend=dict(orientation="h", y=1.1))
                            st.plotly_chart(style(fig_vol, 40), use_container_width=True)
                        with c2:
                            st.markdown("##### 🎯 Performance nette (solde)")
                            fig_net = px.bar(df_plot_mob, x="name", y="solde", color="solde",
                                             color_continuous_scale="RdYlGn",
                                             labels={"name": "", "solde": "Solde net"}, height=380)
                            fig_net.add_hline(y=0, line_dash="dash", line_color="black")
                            fig_net.update_layout(coloraxis_showscale=False,
                                                  xaxis_title="", yaxis_title="Solde net")
                            st.plotly_chart(style(fig_net, 40), use_container_width=True)

                        st.markdown("---")
                        st.markdown("#### 🔍 Analyse géographique des partenaires")
                        col_left, col_right = st.columns(2)
                        with col_left:
                            st.markdown(f"##### 📍 Top 10 origines ({label_in})")
                            top_in = df_mob_filtered[df_mob_filtered[col_dest].isin(coms_selection)].nlargest(10, "flux")
                            if not top_in.empty:
                                fig_in = px.bar(top_in, x="flux", y=col_orig, orientation="h",
                                                color_discrete_sequence=[color_in], text_auto=".0f")
                                fig_in.update_layout(yaxis={"categoryorder": "total ascending"},
                                                     height=400, yaxis_title="", xaxis_title="Flux")
                                st.plotly_chart(style(fig_in), use_container_width=True)
                            else:
                                st.info("Pas de données d'entrée disponibles.")
                        with col_right:
                            st.markdown(f"##### 🚩 Top 10 destinations ({label_out})")
                            top_out = df_mob_filtered[df_mob_filtered[col_orig].isin(coms_selection)].nlargest(10, "flux")
                            if not top_out.empty:
                                fig_out = px.bar(top_out, x="flux", y=col_dest, orientation="h",
                                                 color_discrete_sequence=[color_out], text_auto=".0f")
                                fig_out.update_layout(yaxis={"categoryorder": "total ascending"},
                                                      height=400, yaxis_title="", xaxis_title="Flux")
                                st.plotly_chart(style(fig_out), use_container_width=True)
                            else:
                                st.info("Pas de données de sortie disponibles.")

                with tab_method_mob:
                    st.header("📖 Guide d'interprétation")
                    st.markdown("""
### 1. Les trois thématiques
- **🏠 Migrations Résidentielles :** *"Où les gens ont-ils choisi de déménager ?"* — indicateur de la qualité de vie et du logement.
- **💼 Mobilité Professionnelle :** *"Où les gens travaillent-ils par rapport à leur domicile ?"* — indicateur de la force économique du territoire.
- **🎓 Mobilité Scolaire :** *"Où les élèves et étudiants vont-ils apprendre ?"* — indicateur du rayonnement éducatif.

### 2. Comprendre les graphiques
- **Barres groupées (Volume)** : vitalité globale du territoire.
- **Barres de solde (Rouge/Vert)** : attractivité nette.
- **Top 10 (horizontal)** : partenaires géographiques principaux.

### 3. Niveaux géographiques
- **Détail communal** : analyse fine d'une ou plusieurs communes d'une même métropole.
- **Comparaison métropoles** : vue macro agrégée.

### 4. Source des données
Données INSEE issues des Recensements de la Population. Les flux internes sont exclus.
                    """)

# ==============================================================================
# ONGLET 4 — MÉNAGES
# ==============================================================================
if vue == "Démographie":
    with tab4:
        st.markdown('<p class="section-header">Structure des ménages</p>', unsafe_allow_html=True)
        st.markdown('<p class="source-note">Source : <a href="https://www.insee.fr/fr/statistiques/8582448" target="_blank">INSEE — Ménages par âge, situation familiale et CSP (RP 2022)</a></p>', unsafe_allow_html=True)
        sous1, sous2 = st.tabs(["👨‍👩‍👧 Type & taille de ménage", "🧑‍💼 CSP des ménages"])

        with sous1:
            if df_men_age is None:
                st.info("📂 Fichier `Menage_age_situation_clean.csv` introuvable.")
            else:
                # ── Bandeau filtres ──────────────────────────────────────────
                with st.container():
                    st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
                    filter_bar("🔧 Filtres — Type & taille de ménage")
                    fm1, fm2 = st.columns(2)
                    with fm1:
                        mode_men = st.radio(
                            "Niveau géographique",
                            ["Comparaison Métropoles", "Détail Communal"],
                            key="men_mode", horizontal=True,
                        )
                    with fm2:
                        metro_men = st.selectbox("Métropole parente", TOUTES, key="m_men")
                    if mode_men == "Détail Communal":
                        cmns_men = sorted(COMMUNES.get(metro_men, []))
                        sel_communes_men = st.multiselect(
                            "Communes", cmns_men, default=cmns_men[:2], key="men_communes",
                        )
                    st.markdown('</div>', unsafe_allow_html=True)

                st.markdown("---")

                cols_m = [c for c in df_men_age.columns if c.startswith("Menages_")]
                TYPE_GROUPES = {
                    "Personne seule":     [c for c in cols_m if "pers_seule" in c],
                    "Couple sans enfant": [c for c in cols_m if "cpl_sans_enf" in c],
                    "Couple avec enfant": [c for c in cols_m if "cpl_avec_enfant" in c or "cpl_1enf" in c],
                    "Fam. mono. (mère)":  [c for c in cols_m if "mere_enf" in c],
                    "Fam. mono. (père)":  [c for c in cols_m if "pere_enf" in c],
                    "Autre ménage":       [c for c in cols_m if "autre_menage" in c],
                }
                AGE_LABELS = {
                    "< 20 ans": "moins20ans", "20–24 ans": "20_24ans", "25–39 ans": "25_39ans",
                    "40–54 ans": "40_54ans", "55–64 ans": "55_64ans",
                    "65–79 ans": "65_79ans", "80 ans +": "plus80ans",
                }

                if mode_men == "Comparaison Métropoles":
                    df_men_m = df_men_age[df_men_age["metropole"] == metro_men]
                    nb_men = df_men_m[cols_m].sum().sum() if not df_men_m.empty else np.nan
                    pop_m  = np.nan
                    if df_pop is not None:
                        dm2 = df_pop[(df_pop["metropole"] == metro_men) & (df_pop["annee"] == 2022)]
                        if not dm2.empty:
                            pop_m = dm2[[c for c in dm2.columns if "ageq_rec" in c]].sum().sum()
                    taille = (pop_m / nb_men) if (not np.isnan(nb_men) and nb_men > 0) else np.nan
                    k1, k2 = st.columns(2)
                    k1.metric(f"Nombre de ménages — {metro_men}", fmt(nb_men))
                    k2.metric("Taille moyenne du ménage", f"{taille:.2f} pers." if not np.isnan(taille) else "N/D")
                    st.markdown("---")
                    totaux = {lbl: df_men_m[[c for c in cols if c in df_men_m.columns]].sum().sum()
                              for lbl, cols in TYPE_GROUPES.items()}
                    df_t = pd.DataFrame(list(totaux.items()), columns=["Type", "Ménages"])
                    df_t = df_t[df_t["Ménages"] > 0].sort_values("Ménages", ascending=False)
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"##### Types de ménages — {metro_men}")
                        fig_t = px.bar(df_t, x="Ménages", y="Type", orientation="h",
                                       color_discrete_sequence=[COULEURS[metro_men]], text_auto=".0f")
                        fig_t.update_layout(yaxis={"autorange": "reversed"}, yaxis_title="",
                                            xaxis_title="Ménages")
                        st.plotly_chart(style(fig_t), use_container_width=True)
                    with c2:
                        st.markdown("##### Répartition")
                        fig_pie = px.pie(df_t, names="Type", values="Ménages", hole=0.42,
                                         color_discrete_sequence=px.colors.sequential.Greens_r)
                        st.plotly_chart(style(fig_pie), use_container_width=True)
                    st.markdown("---")
                    st.markdown("##### Composition par âge du référent du ménage")
                    rows_a = []
                    for age_l, age_k in AGE_LABELS.items():
                        for type_l, tcols in TYPE_GROUPES.items():
                            inter = [c for c in tcols if age_k in c and c in df_men_m.columns]
                            val = df_men_m[inter].sum().sum() if inter else 0
                            if val > 0:
                                rows_a.append({"Âge référent": age_l, "Type": type_l, "Ménages": val})
                    if rows_a:
                        fig_a = px.bar(pd.DataFrame(rows_a), x="Âge référent", y="Ménages",
                                       color="Type", barmode="stack",
                                       color_discrete_sequence=px.colors.sequential.Greens_r)
                        fig_a.update_layout(legend=dict(orientation="h", y=1.1, font_size=10))
                        st.plotly_chart(style(fig_a, 50), use_container_width=True)

                else:
                    # ── Vue Détail Communal ──────────────────────────────────
                    communes_men = sel_communes_men if sel_communes_men else []
                    if not communes_men:
                        st.info("Sélectionnez au moins une commune.")
                    else:
                        rows_cc = []
                        for comm in communes_men:
                            df_cc = df_men_age[df_men_age["LIBGEO"] == comm]
                            for lbl, cols in TYPE_GROUPES.items():
                                valid = [c for c in cols if c in df_cc.columns]
                                rows_cc.append({"Commune": comm, "Type": lbl,
                                                "Ménages": df_cc[valid].sum().sum() if valid else 0})
                        df_ccp = pd.DataFrame(rows_cc)
                        if len(communes_men) == 1:
                            comm = communes_men[0]
                            df_single = df_ccp[df_ccp["Ménages"] > 0].sort_values("Ménages", ascending=False)
                            c1, c2 = st.columns(2)
                            with c1:
                                st.markdown(f"##### Types de ménages — {comm}")
                                fig_t = px.bar(df_single, x="Ménages", y="Type", orientation="h",
                                               color_discrete_sequence=[COULEURS.get(metro_men, "#2D6A4F")],
                                               text_auto=".0f")
                                fig_t.update_layout(yaxis={"autorange": "reversed"}, yaxis_title="")
                                st.plotly_chart(style(fig_t), use_container_width=True)
                            with c2:
                                st.markdown("##### Répartition")
                                fig_pie = px.pie(df_single, names="Type", values="Ménages", hole=0.42,
                                                 color_discrete_sequence=px.colors.sequential.Greens_r)
                                st.plotly_chart(style(fig_pie), use_container_width=True)
                        elif df_ccp["Ménages"].sum() > 0:
                            st.markdown(f"##### Comparaison — {' · '.join(communes_men)}")
                            fig_ccp = px.bar(df_ccp, x="Type", y="Ménages", color="Commune",
                                             barmode="group",
                                             color_discrete_sequence=["#2D6A4F", "#95D5B2", "#1A6FA3",
                                                                       "#C45B2A", "#D4A017"])
                            fig_ccp.update_layout(xaxis_tickangle=-20, legend=dict(orientation="h"))
                            st.plotly_chart(style(fig_ccp), use_container_width=True)
                        else:
                            st.info("Données non disponibles pour ces communes.")

        with sous2:
            if df_men_csp is None:
                st.info("📂 Fichier `Menages_csp_nbpers_clean.csv` introuvable.")
            else:
                # ── Bandeau filtres ──────────────────────────────────────────
                with st.container():
                    st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
                    filter_bar("🔧 Filtres — CSP des ménages")
                    fc1, fc2 = st.columns(2)
                    with fc1:
                        metro_csp_m = st.selectbox("Métropole", TOUTES, key="m_csp")
                    with fc2:
                        comp_csp = st.checkbox("Comparer toutes les métropoles (%)", key="comp_csp")
                    st.markdown('</div>', unsafe_allow_html=True)

                st.markdown("---")

                cols_csp_m = [c for c in df_men_csp.columns if c.startswith("Menages_")]
                CSP_GROUPES = {
                    "Agriculteurs":           ["agriculteurs"],
                    "Artisans / Commerçants": ["artisans", "commercants", "chef_entreprise"],
                    "Cadres & Prof. sup.":    ["professions_liberales", "cadre_admin", "prof_scientifique",
                                               "ingenieur", "info_art", "cadre_commercial"],
                    "Prof. intermédiaires":   ["prof_enseignement", "prof_inter", "technicien", "agent_maitrise"],
                    "Employés":               ["emp_fonction", "emp_admin", "emp_commerce",
                                               "service_particulier", "securite"],
                    "Ouvriers":               ["ouvrier", "conducteur", "cariste"],
                    "Inactifs / Retraités":   ["retraites_inactifs", "chomeur"],
                }

                def agg_csp_men(df_src):
                    return {grp: df_src[[c for c in cols_csp_m if any(kw in c for kw in kws) and c in df_src.columns]].sum().sum()
                            for grp, kws in CSP_GROUPES.items()}

                if not comp_csp:
                    df_csp_men = df_men_csp[df_men_csp["metropole"] == metro_csp_m]
                    if df_csp_men.empty:
                        st.warning(f"Aucune donnée CSP pour {metro_csp_m}.")
                    else:
                        tot_csp = agg_csp_men(df_csp_men)
                        df_cp = pd.DataFrame(list(tot_csp.items()), columns=["CSP", "Ménages"])
                        df_cp = df_cp[df_cp["Ménages"] > 0].sort_values("Ménages", ascending=False)
                        c1, c2 = st.columns(2)
                        with c1:
                            st.markdown(f"##### Ménages par CSP — {metro_csp_m}")
                            fig_cp = px.bar(df_cp, x="Ménages", y="CSP", orientation="h",
                                            color="Ménages", color_continuous_scale="Greens", text_auto=".0f")
                            fig_cp.update_layout(yaxis={"autorange": "reversed"},
                                                 coloraxis_showscale=False, yaxis_title="")
                            st.plotly_chart(style(fig_cp), use_container_width=True)
                        with c2:
                            st.markdown("##### Répartition")
                            fig_cp2 = px.pie(df_cp, names="CSP", values="Ménages", hole=0.42,
                                              color_discrete_sequence=px.colors.sequential.Greens_r)
                            st.plotly_chart(style(fig_cp2), use_container_width=True)
                else:
                    st.markdown("##### Part des grandes CSP — toutes métropoles (%)")
                    rows_c = []
                    for m in TOUTES:
                        df_m_csp = df_men_csp[df_men_csp["metropole"] == m]
                        tot = agg_csp_men(df_m_csp)
                        total_m = sum(tot.values())
                        for grp, val in tot.items():
                            rows_c.append({"Métropole": m, "CSP": grp,
                                           "Part (%)": (val / total_m * 100) if total_m > 0 else 0})
                    fig_comp_csp = px.bar(pd.DataFrame(rows_c), x="Métropole", y="Part (%)",
                                          color="CSP", barmode="stack",
                                          color_discrete_sequence=px.colors.sequential.Greens_r)
                    fig_comp_csp.update_layout(yaxis_title="Part des ménages (%)",
                                               legend=dict(orientation="h", y=1.1, font_size=10))
                    st.plotly_chart(style(fig_comp_csp, 50), use_container_width=True)
                    
# ==============================================================================
# ONGLET 5 — CSP COMPARATIF
# ==============================================================================
if vue == "Démographie":
    with tab6:
        st.markdown('<p class="section-header">CSP comparatif — Secteurs d\'activité & Niveau de diplôme</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="source-note">Source : INSEE — Recensements de la Population 2011, 2016, 2022 '
            '· Population active de 25 à 54 ans · Fichiers Commune_AAAA_2554</p>',
            unsafe_allow_html=True,
        )

        if df_csp_new.empty or "ANNEE" not in df_csp_new.columns:
            st.info("📂 Données CSP/Diplôme non trouvées. Vérifiez les chemins FILES_CSP / FILES_DIP.")
        else:
            # ── Bandeau filtres ──────────────────────────────────────────────
            with st.container():
                st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
                filter_bar("🔧 Filtres — CSP comparatif")

                csp_row1_c1, csp_row1_c2, csp_row1_c3 = st.columns(3)
                with csp_row1_c1:
                    theme_analyse = st.selectbox(
                        "Thématique",
                        ["Secteurs d'activité (CSP)", "Niveau de diplôme"],
                        key="csp_theme",
                    )
                current_df_csp  = df_csp_new if theme_analyse == "Secteurs d'activité (CSP)" else df_dip_new
                current_map_csp = CSP_MAP_NEW if theme_analyse == "Secteurs d'activité (CSP)" else DIP_MAP

                annees_csp = sorted(current_df_csp["ANNEE"].dropna().unique(), reverse=True) if not current_df_csp.empty else []
                with csp_row1_c2:
                    sel_annee_csp = st.selectbox("📅 Année", annees_csp, key="csp_annee") if annees_csp else None
                with csp_row1_c3:
                    mode_analyse = st.radio("🎯 Niveau d'analyse",
                                            ["Par Communes (Grenoble)", "Par Métropoles"],
                                            key="csp_mode", horizontal=True)

                if mode_analyse == "Par Communes (Grenoble)":
                    clist = sorted(COMMUNES["Grenoble"])
                    sel_communes_csp = st.multiselect("Communes (Grenoble)", clist,
                                                      default=["Grenoble"], key="csp_communes")
                else:
                    sel_metros_csp = st.multiselect("Métropoles", TOUTES,
                                                    default=["Grenoble", "Rouen"], key="csp_metros")

                sel_cats = st.multiselect("📂 Catégories à afficher",
                                          options=list(current_map_csp.values()),
                                          default=list(current_map_csp.values()),
                                          key="csp_cats")

                st.markdown('</div>', unsafe_allow_html=True)

            if sel_annee_csp is None:
                st.info("Données non disponibles.")
            else:
                df_year_csp = current_df_csp[current_df_csp["ANNEE"] == sel_annee_csp]
                entities_csp = []

                if mode_analyse == "Par Communes (Grenoble)":
                    for name in sel_communes_csp:
                        subset = df_year_csp[(df_year_csp["LIB_NORM"] == normalize_name(name)) & (df_year_csp["DEP"] == "38")]
                        if not subset.empty:
                            entities_csp.append({"name": name, "data": subset.iloc[0]})
                else:
                    for m_name in sel_metros_csp:
                        dep   = DEP_MAP[m_name]
                        norms = [normalize_name(c) for c in COMMUNES[m_name]]
                        subset = df_year_csp[(df_year_csp["DEP"] == dep) & (df_year_csp["LIB_NORM"].isin(norms))]
                        if not subset.empty:
                            agg = subset[list(current_map_csp.values())].sum()
                            entities_csp.append({"name": m_name, "data": agg})

                if not entities_csp or not sel_cats:
                    st.warning("Sélectionnez au moins une entité et une catégorie dans les filtres ci-dessus.")
                else:
                    noms = " · ".join(e["name"] for e in entities_csp)
                    st.markdown(
                        f"<h2 style='color:#1C3A27;font-size:1.3rem;margin-bottom:4px'>"
                        f"🔍 {theme_analyse} — {noms} · {sel_annee_csp}</h2>",
                        unsafe_allow_html=True,
                    )

                    kpi_cols_csp = st.columns(len(entities_csp))
                    for i, entity in enumerate(entities_csp):
                        total = entity["data"][sel_cats].sum()
                        with kpi_cols_csp[i]:
                            st.markdown(f"""
                            <div class='kpi-card'>
                                <div class='kpi-label'>{entity['name']}</div>
                                <div class='kpi-value'>{int(total):,}</div>
                                <div class='kpi-subtitle'>Actifs 25–54 ans</div>
                            </div>
                            """, unsafe_allow_html=True)

                    st.markdown("---")
                    c1, c2 = st.columns(2)
                    with c1:
                        fig_bar_csp = go.Figure()
                        for ent in entities_csp:
                            fig_bar_csp.add_trace(go.Bar(
                                x=sel_cats, y=ent["data"][sel_cats],
                                name=ent["name"], marker_color=COULEURS.get(ent["name"], "#3498db"),
                            ))
                        fig_bar_csp.update_layout(title="Répartition en volume", barmode="group",
                                                  height=420, legend=dict(orientation="h", y=1.12),
                                                  xaxis_tickangle=-30)
                        st.plotly_chart(style(fig_bar_csp, 50), use_container_width=True)
                    with c2:
                        fig_radar_csp = go.Figure()
                        max_pct = 0
                        for ent in entities_csp:
                            v   = ent["data"][sel_cats]
                            tot = v.sum()
                            pct = (v / tot * 100).fillna(0) if tot > 0 else v * 0
                            max_pct = max(max_pct, pct.max())
                            fig_radar_csp.add_trace(go.Scatterpolar(
                                r=list(pct) + [pct.iloc[0]],
                                theta=sel_cats + [sel_cats[0]],
                                fill="toself", name=ent["name"],
                                line_color=COULEURS.get(ent["name"], "#3498db"), opacity=0.75,
                            ))
                        fig_radar_csp.update_layout(
                            title="Profil structurel (%)",
                            polar=dict(radialaxis=dict(visible=True, range=[0, max(max_pct * 1.2, 10)])),
                            legend=dict(orientation="h", y=-0.15), height=420,
                        )
                        st.plotly_chart(style(fig_radar_csp, 50), use_container_width=True)

                    if len(entities_csp) == 2:
                        st.markdown("---")
                        st.markdown("### 🎯 Analyse comparative")
                        with st.expander("ℹ️ Comment lire l'indice de spécialisation ?"):
                            st.write(
                                f"L'indice compare la structure de **{entities_csp[0]['name']}** "
                                f"par rapport à **{entities_csp[1]['name']}**.\n\n"
                                "- **100** : même poids relatif dans les deux zones.\n"
                                "- **> 100** : sur-représenté dans la première zone.\n"
                                "- **< 100** : sous-représenté dans la première zone."
                            )
                        v1 = entities_csp[0]["data"][sel_cats]
                        v2 = entities_csp[1]["data"][sel_cats]
                        t1, t2 = v1.sum(), v2.sum()
                        spec = ((v1 / t1) / (v2 / t2) * 100).fillna(100) if t1 > 0 and t2 > 0 else pd.Series([100] * len(sel_cats), index=sel_cats)

                        k1, k2, k3, k4 = st.columns(4)
                        k1.metric(f"Actifs — {entities_csp[0]['name']}", f"{int(t1):,}".replace(",", "\u202f"))
                        k2.metric(f"Actifs — {entities_csp[1]['name']}", f"{int(t2):,}".replace(",", "\u202f"))
                        k3.metric("Écart brut", f"{int(t1 - t2):+,}".replace(",", "\u202f"))
                        k4.metric("Indice de masse", f"{(t1 / t2):.2f}x" if t2 > 0 else "N/D")

                        st.markdown("---")
                        fig_spec = px.bar(
                            x=sel_cats, y=spec, color=spec,
                            color_continuous_scale="RdYlGn", range_color=[50, 150],
                            labels={"x": "Catégorie", "y": "Indice (base 100)", "color": "Indice"},
                            title=f"Spécialisation : {entities_csp[0]['name']} / {entities_csp[1]['name']}",
                            height=380,
                        )
                        fig_spec.add_hline(y=100, line_dash="dash", line_color="black",
                                           annotation_text="Parité (100)", annotation_position="top left")
                        fig_spec.update_layout(xaxis_tickangle=-30)
                        st.plotly_chart(style(fig_spec, 50), use_container_width=True)

                        with st.expander("📄 Voir le tableau de données complet"):
                            table_df = pd.DataFrame({
                                "Catégorie": sel_cats,
                                f"{entities_csp[0]['name']} — Effectif": [int(v1[c]) for c in sel_cats],
                                f"{entities_csp[1]['name']} — Effectif": [int(v2[c]) for c in sel_cats],
                                "Différence": [int(v1[c] - v2[c]) for c in sel_cats],
                                "Indice spécialisation": [round(spec[c], 1) for c in sel_cats],
                            })
                            st.dataframe(table_df, use_container_width=True)

                    elif len(entities_csp) > 2:
                        st.markdown("---")
                        st.markdown("#### 📋 Tableau récapitulatif")
                        rows_tab = []
                        for ent in entities_csp:
                            row = {"Entité": ent["name"]}
                            row.update({c: int(ent["data"][c]) for c in sel_cats})
                            row["Total"] = int(ent["data"][sel_cats].sum())
                            rows_tab.append(row)
                        st.dataframe(pd.DataFrame(rows_tab).set_index("Entité"), use_container_width=True)

                    st.markdown("---")
                    with st.expander("📖 Note méthodologique"):
                        st.write(
                            "**Population étudiée** : actifs de 25 à 54 ans.\n\n"
                            "**Sources** : Recensements INSEE 2011, 2016, 2022.\n\n"
                            "**Indice de spécialisation** : rapport des parts relatives de chaque catégorie "
                            "entre les deux zones, multiplié par 100."
                        )

# ==============================================================================
# SOLIDARITÉ & CITOYENNETÉ
# ==============================================================================
if vue == "Solidarité et citoyenneté":
    st.markdown('<p class="section-header">Solidarité & citoyenneté</p>', unsafe_allow_html=True)
    s1, s2, s3, s4, s5 = st.tabs(["🤝 Solidarité", "🎓 Éducation", "🏥 Santé", "🗳️ Participation", "💶 Revenus & pauvreté"])

    # ──────────────────────────────────────────────────────────────────────────
    # ONGLET SOLIDARITÉ — CAF
    # ──────────────────────────────────────────────────────────────────────────
    with s1:
        st.markdown('<p class="section-header">🤝 Solidarité — Données CAF</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="source-note">Source : <a href="https://data.caf.fr" target="_blank">' +
            "Caisse d\'Allocations Familiales — CAF 5 Métropoles 2020–2023</a></p>",
            unsafe_allow_html=True,
        )
        if df_caf is None or df_caf.empty:
            st.info("📂 Fichier `CAF_5_Metropoles.csv` introuvable.")
        else:
            required_cols = {"Annee", "Agglomeration"}
            if not required_cols.issubset(set(df_caf.columns)):
                st.error("Colonnes Annee / Agglomeration manquantes.")
            else:
                ALL_METRIC_LABELS = {
                    "Nombre foyers NDUR":        "Foyers — Toutes aides",
                    "Nombre personnes NDUR":     "Personnes — Toutes aides",
                    "Montant total NDUR":        "Montant total (€) — Toutes aides",
                    "Nombre foyers NDURPAJE":    "Foyers — PAJE",
                    "Nombre personnes NDURPAJE": "Personnes — PAJE",
                    "Montant total NDURPAJE":    "Montant (€) — PAJE",
                    "Nombre foyers NDUREJ":      "Foyers — Aide jeunes enfants",
                    "Nombre personnes NDUREJ":   "Personnes — Aide jeunes enfants",
                    "Montant total NDUREJ":      "Montant (€) — Aide jeunes enfants",
                    "Nombre foyers NDURAL":      "Foyers — Allocation logement",
                    "Nombre personnes NDURAL":   "Personnes — Allocation logement",
                    "Montant total NDURAL":      "Montant (€) — Allocation logement",
                    "Nombre foyers NDURINS":     "Foyers — Insertion sociale",
                    "Nombre personnes NDURINS":  "Personnes — Insertion sociale",
                    "Montant total NDURINS":     "Montant (€) — Insertion sociale",
                }
                available_metrics = {k: v for k, v in ALL_METRIC_LABELS.items() if k in df_caf.columns}
                if not available_metrics:
                    st.warning("Aucune mesure CAF trouvée.")
                else:
                    for col in available_metrics:
                        df_caf[col] = pd.to_numeric(df_caf[col], errors="coerce").fillna(0)
                    years_caf  = sorted(df_caf["Annee"].dropna().unique())
                    agglos_caf = sorted(df_caf["Agglomeration"].dropna().unique())

                    caf_vue, caf_comp = st.tabs(["📊 Vue d'ensemble", "🔍 Comparateur de communes"])

                    # ── Vue d'ensemble ──────────────────────────────────────────────────────────
                    with caf_vue:
                        with st.container():
                            st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
                            filter_bar("🔧 Filtres — Solidarité CAF")
                            caf_f1, caf_f2, caf_f3 = st.columns([2, 1, 2])
                            
                            with caf_f1:
                                metric_key = st.selectbox("Indicateur", list(available_metrics.keys()),
                                                        format_func=lambda k: available_metrics[k], index=0, key="caf_metric")
                            with caf_f2:
                                year_caf = st.selectbox("Année", years_caf, index=len(years_caf)-1, key="caf_year")
                            with caf_f3:
                                sel_agglos_caf = st.multiselect("Agglomérations", agglos_caf, default=agglos_caf, key="caf_agglos")
                            st.markdown('</div>', unsafe_allow_html=True)

                        if not sel_agglos_caf:
                            st.warning("⚠️ Sélectionnez au moins une agglomération.")
                        else:
                            # Préparation des données
                            metric       = metric_key
                            label_metric = available_metrics[metric]
                            df_fil = df_caf[df_caf["Agglomeration"].isin(sel_agglos_caf)]
                            df_yr  = df_fil[df_fil["Annee"] == year_caf]

                            st.markdown("---")
                            
                            # Calculs des valeurs
                            total_val = df_yr[metric].sum()
                            nb_agglo  = int(df_yr["Agglomeration"].nunique())
                            nb_com    = int(df_yr["Nom_Commune"].nunique()) if "Nom_Commune" in df_yr.columns else 0
                            max_agglo = df_yr.groupby("Agglomeration")[metric].sum().idxmax() if not df_yr.empty else "—"

                            # Affichage des 4 colonnes KPI harmonisées
                            k1, k2, k3, k4 = st.columns(4)
                            
                            # Liste de configuration pour automatiser le tracé des cartes
                            caf_cards = [
                                (k1, f"Total {year_caf}", fmt(total_val), label_metric),
                                (k2, "Agglomérations", nb_agglo, "Unités sélectionnées"),
                                (k3, "Communes", nb_com, "Territoires couverts"),
                                (k4, "Top Agglo", max_agglo, "Volume le plus élevé")
                            ]

                            for col, title, value, subtitle in caf_cards:
                                with col:
                                    st.markdown(f"""
                                    <div class='kpi-card-mob' style='border-top: none; border-left: 5px solid #1e5631; padding: 10px 15px; text-align: left; background-color: #f9f9f9; border-radius: 4px;'>
                                        <div class='kpi-label' style='font-size: 11px; color: #666; font-weight: bold; text-transform: uppercase;'>{title}</div>
                                        <div class='kpi-value' style='font-size: 22px; font-weight: bold; color: #1e5631; margin: 5px 0;'>{value}</div>
                                        <div style='font-size:10px; color:#888;'>{subtitle}</div>
                                    </div>
                                    """, unsafe_allow_html=True)

                            st.markdown("---")

                            c3, c4 = st.columns(2)
                            with c3:
                                st.markdown(f"##### 👨‍👩‍👧 Quotient familial ({year_caf})")
                                if "Quotient familial" in df_yr.columns:
                                    qf_order = ["Moins de 400 euros","Entre 400 et 799 euros",
                                        "Entre 800 et 1199 euros","Entre 1200 et 1599 euros",
                                        "Entre 1600 et 1999 euros","Entre 2000 et 3999 euros",
                                        "4000 euros ou plus","Inconnu"]
                                    qf_data = df_yr.groupby(["Agglomeration","Quotient familial"], as_index=False)[metric].sum()
                                    qf_data["QF_ord"] = pd.Categorical(qf_data["Quotient familial"], categories=qf_order, ordered=True)
                                    fig_qf = px.bar(qf_data.sort_values("QF_ord"), x="Agglomeration", y=metric,
                                        color="Quotient familial", barmode="stack",
                                        labels={"Agglomeration": "", metric: label_metric},
                                        title="Composition par quotient familial", height=380)
                                    st.plotly_chart(style(fig_qf, 40), use_container_width=True)
                            with c4:
                                st.markdown(f"##### 🏆 Top 15 communes — {year_caf}")
                                if "Nom_Commune" in df_yr.columns:
                                    top15 = df_yr.groupby(["Nom_Commune","Agglomeration"], as_index=False)[metric].sum().nlargest(15, metric)
                                    fig_top = px.bar(top15, x=metric, y="Nom_Commune", orientation="h",
                                        color="Agglomeration", color_discrete_map=COULEURS, text_auto=".3s",
                                        labels={"Nom_Commune": "", metric: label_metric},
                                        title=f"Top 15 communes — {label_metric}", height=420)
                                    fig_top.update_layout(yaxis={"categoryorder": "total ascending"})
                                    st.plotly_chart(style(fig_top, 40), use_container_width=True)
                            st.markdown("---")

                            # Radar
                            st.markdown("##### 🕸️ Profil comparatif des aides — radar")
                            aides_f = {"Foyers PAJE":"Nombre foyers NDURPAJE","Foyers aj. enf.":"Nombre foyers NDUREJ",
                                "Foyers alloc. log.":"Nombre foyers NDURAL","Foyers insertion":"Nombre foyers NDURINS",
                                "Foyers total":"Nombre foyers NDUR"}
                            aides_d = {k: v for k, v in aides_f.items() if v in df_yr.columns}
                            if len(aides_d) >= 3:
                                rdata = df_yr.groupby("Agglomeration")[list(aides_d.values())].sum().reset_index()
                                rdata.columns = ["Agglomeration"] + list(aides_d.keys())
                                fig_radar = go.Figure()
                                cats_r = list(aides_d.keys())
                                for _, rr in rdata.iterrows():
                                    vv = [rr[c] for c in cats_r] + [rr[cats_r[0]]]
                                    fig_radar.add_trace(go.Scatterpolar(r=vv, theta=cats_r+[cats_r[0]],
                                        fill="toself", name=rr["Agglomeration"],
                                        line_color=COULEURS.get(rr["Agglomeration"], "#999")))
                                fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True)), height=420,
                                    title=f"Profil des aides — {year_caf}", font_family="Sora",
                                    paper_bgcolor="rgba(0,0,0,0)")
                                st.plotly_chart(fig_radar, use_container_width=True)
                            st.markdown("---")
                            with st.expander("📄 Données détaillées"):
                                st.dataframe(df_yr.groupby(
                                    ["Agglomeration","Quotient familial"] if "Quotient familial" in df_yr.columns else ["Agglomeration"],
                                    as_index=False)[list(available_metrics.keys())].sum(), use_container_width=True)
                            with st.expander("📖 Note méthodologique"):
                                st.write("**Sources** : CAF — données communales 2020–2023.\n\n"
                                    "**NDUR** : dossiers unifiés réels. **NDURPAJE** : prestation jeune enfant. "
                                    "**NDURAL** : allocation logement. **NDURINS** : insertion sociale (RSA...).")

                    # ── Comparateur de communes CAF ──────────────────────────────────────────────
                    with caf_comp:
                        st.markdown('<p class="section-header">🔍 Comparateur de communes — CAF</p>', unsafe_allow_html=True)
                        with st.container():
                            st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
                            filter_bar("🔧 Filtres — Comparateur CAF")
                            cc1, cc2, cc3, cc4 = st.columns([1, 1, 1, 1])
                            with cc1:
                                metro_cc_caf = st.selectbox("Métropole", agglos_caf, key="caf_cc_metro")
                            communes_cc = sorted(df_caf[df_caf["Agglomeration"]==metro_cc_caf]["Nom_Commune"].dropna().unique()) if "Nom_Commune" in df_caf.columns else []
                            with cc2:
                                year_cc_caf = st.selectbox("Année", years_caf, index=len(years_caf)-1, key="caf_cc_year")
                            with cc3:
                                com_a_caf = st.selectbox("Commune A", communes_cc, index=0, key="caf_cc_a")
                            with cc4:
                                com_b_caf = st.selectbox("Commune B", communes_cc, index=min(1,len(communes_cc)-1), key="caf_cc_b")
                            st.markdown('</div>', unsafe_allow_html=True)

                        df_cc  = df_caf[(df_caf["Agglomeration"]==metro_cc_caf) & (df_caf["Annee"]==year_cc_caf)]
                        df_cca = df_cc[df_cc["Nom_Commune"]==com_a_caf] if "Nom_Commune" in df_caf.columns else pd.DataFrame()
                        df_ccb = df_cc[df_cc["Nom_Commune"]==com_b_caf] if "Nom_Commune" in df_caf.columns else pd.DataFrame()
                        st.markdown("---")

                        kpi_cc_list = ["Nombre foyers NDUR","Montant total NDUR","Nombre foyers NDURAL","Nombre foyers NDURINS"]
                        kpi_cc_d = [c for c in kpi_cc_list if c in df_caf.columns]
                        kcols = st.columns(len(kpi_cc_d))
                        for i, col in enumerate(kpi_cc_d):
                            va = df_cca[col].sum() if not df_cca.empty else np.nan
                            vb = df_ccb[col].sum() if not df_ccb.empty else np.nan
                            delta = va - vb if pd.notna(va) and pd.notna(vb) else None
                            with kcols[i]:
                                st.metric(label=available_metrics.get(col, col),
                                    value=fmt(va) if pd.notna(va) else "N/D",
                                    delta=f"{int(delta):+,d} vs {com_b_caf}".replace(",","\u202f") if delta is not None else None)
                        st.markdown("---")

                        c1, c2 = st.columns(2)
                        with c1:
                            st.markdown("##### 📊 Toutes les aides — comparaison directe")
                            rows_cc = []
                            for col, lbl in available_metrics.items():
                                va = df_cca[col].sum() if not df_cca.empty else 0
                                vb = df_ccb[col].sum() if not df_ccb.empty else 0
                                rows_cc.append({"Indicateur": lbl, com_a_caf: va, com_b_caf: vb})
                            df_ccm = pd.DataFrame(rows_cc).melt(id_vars="Indicateur", var_name="Commune", value_name="Valeur")
                            fig_ccb = px.bar(df_ccm, x="Valeur", y="Indicateur", color="Commune",
                                orientation="h", barmode="group",
                                color_discrete_map={com_a_caf:"#2D6A4F", com_b_caf:"#D4A017"},
                                labels={"Indicateur":"","Valeur":""},
                                title=f"{com_a_caf} vs {com_b_caf} ({year_cc_caf})", height=500)
                            fig_ccb.update_layout(yaxis={"categoryorder":"total ascending"})
                            st.plotly_chart(style(fig_ccb, 40), use_container_width=True)
                        with c2:
                            st.markdown("##### 📈 Évolution — comparaison temporelle")
                            metric_evo_cc = st.selectbox("Indicateur", list(available_metrics.keys()),
                                format_func=lambda k: available_metrics[k], key="caf_cc_evo")
                            if "Nom_Commune" in df_caf.columns:
                                df_ea = df_caf[df_caf["Nom_Commune"]==com_a_caf].groupby("Annee", as_index=False)[metric_evo_cc].sum().assign(Commune=com_a_caf)
                                df_eb = df_caf[df_caf["Nom_Commune"]==com_b_caf].groupby("Annee", as_index=False)[metric_evo_cc].sum().assign(Commune=com_b_caf)
                                df_ecc = pd.concat([df_ea, df_eb])
                                fig_ecc = px.line(df_ecc, x="Annee", y=metric_evo_cc, color="Commune",
                                    color_discrete_map={com_a_caf:"#2D6A4F", com_b_caf:"#D4A017"},
                                    markers=True, title=f"Évolution — {com_a_caf} vs {com_b_caf}", height=420)
                                fig_ecc.update_traces(line_width=2.5, marker_size=8)
                                st.plotly_chart(style(fig_ecc, 40), use_container_width=True)
                        st.markdown("---")
                        if "Quotient familial" in df_caf.columns and "Nombre foyers NDUR" in df_caf.columns:
                            st.markdown("##### 👨‍👩‍👧 Structure par quotient familial")
                            qfa = df_cca.groupby("Quotient familial", as_index=False)["Nombre foyers NDUR"].sum().assign(Commune=com_a_caf) if not df_cca.empty else pd.DataFrame()
                            qfb = df_ccb.groupby("Quotient familial", as_index=False)["Nombre foyers NDUR"].sum().assign(Commune=com_b_caf) if not df_ccb.empty else pd.DataFrame()
                            qfcc = pd.concat([qfa, qfb])
                            if not qfcc.empty:
                                fig_qfcc = px.bar(qfcc, x="Quotient familial", y="Nombre foyers NDUR",
                                    color="Commune", barmode="group",
                                    color_discrete_map={com_a_caf:"#2D6A4F", com_b_caf:"#D4A017"},
                                    labels={"Nombre foyers NDUR":"Foyers"},
                                    title="Répartition par quotient familial", height=380)
                                fig_qfcc.update_layout(xaxis_tickangle=-30)
                                st.plotly_chart(style(fig_qfcc, 40), use_container_width=True)

    # ──────────────────────────────────────────────────────────────────────────
    # ONGLET ÉDUCATION — Effectifs étudiants
    # ──────────────────────────────────────────────────────────────────────────
    with s2:
        st.markdown('<p class="section-header">🎓 Éducation — Effectifs dans l\'enseignement supérieur</p>', unsafe_allow_html=True)
        st.markdown('<p class="source-note">Source : <a href="https://data.enseignementsup-recherche.gouv.fr" target="_blank">' +
            "MESRI — Effectifs dans l\'enseignement supérieur · Communes des 5 métropoles</a></p>",
            unsafe_allow_html=True)
        if df_eff is None or df_eff.empty:
            st.info("📂 Fichier `effectifs_5_villes.csv` introuvable.")
        else:
            df_eff_w      = df_eff.copy()
            annees_eff    = sorted(df_eff_w["annee"].dropna().unique().astype(int))
            metros_eff    = sorted(df_eff_w["metropole"].dropna().unique())
            LABEL_REGROUPEMENT = {
                "TOTAL":"Tous types confondus","UNIV":"Universités","STS":"STS & assimilés",
                "CPGE":"CPGE","GE":"Grandes Écoles","ING_autres":"Écoles d'ingénieurs",
                "EC_COM":"Écoles de commerce","EC_ART":"Écoles d'art","EC_JUR":"Écoles juridiques",
                "EC_PARAM":"Écoles paramédicales","EC_autres":"Autres écoles",
                "INP":"INP","EPEU":"EPEU","ENS":"ENS","IUFM":"IUFM / INSPE",
            }
            regroupements_dispo = sorted(df_eff_w["regroupement"].dropna().unique())

            eff_vue, eff_comp = st.tabs(["📊 Vue d'ensemble", "🔍 Comparateur de communes"])

            # ── Vue d'ensemble Éducation ─────────────────────────────────────────────
            with eff_vue:
                with st.container():
                    st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
                    filter_bar("🔧 Filtres — Effectifs enseignement supérieur")
                    ef1, ef2, ef3, ef4 = st.columns([1, 1, 1, 1])
                    with ef1:
                        sel_metros_eff = st.multiselect("Métropoles", metros_eff, default=metros_eff, key="eff_metros")
                    with ef2:
                        annee_eff = st.selectbox("Année", annees_eff, index=len(annees_eff)-1, key="eff_annee")
                    with ef3:
                        regr_choices = ["TOTAL"] + [r for r in regroupements_dispo if r != "TOTAL"]
                        sel_regr = st.selectbox("Type d'établissement", regr_choices,
                            format_func=lambda r: LABEL_REGROUPEMENT.get(r, r), index=0, key="eff_regr")
                    with ef4:
                        sel_secteur = st.selectbox("Secteur",
                            ["Tous","Établissements publics","Établissements privés"], key="eff_secteur")
                    st.markdown('</div>', unsafe_allow_html=True)

                if not sel_metros_eff:
                    st.warning("⚠️ Sélectionnez au moins une métropole.")
                else:
                    df_e = df_eff_w[df_eff_w["metropole"].isin(sel_metros_eff) & (df_eff_w["regroupement"]==sel_regr)]
                    if sel_secteur != "Tous":
                        df_e = df_e[df_e["secteur_de_l_etablissement"]==sel_secteur]
                    df_e_yr = df_e[df_e["annee"]==annee_eff]
                    st.markdown("---")

                    total_eff   = int(df_e_yr["effectif"].sum())
                    best_metro  = df_e_yr.groupby("metropole")["effectif"].sum().idxmax() if not df_e_yr.empty else "—"
                    k1, k2, k3, k4 = st.columns(4)
                    k1.metric(f"Effectif total ({annee_eff})", fmt(total_eff))
                    k2.metric("Métropoles", int(df_e_yr["metropole"].nunique()))
                    k3.metric("Communes couvertes", int(df_e_yr["geo_nom"].nunique()))
                    k4.metric("1ère métropole", best_metro)
                    st.markdown("---")

                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"##### 📊 Effectifs par métropole — {annee_eff}")
                        by_metro = df_e_yr.groupby("metropole", as_index=False)["effectif"].sum().sort_values("effectif", ascending=False)
                        fig_em = px.bar(by_metro, x="metropole", y="effectif", color="metropole",
                            color_discrete_map=COULEURS, text_auto=".3s",
                            labels={"metropole":"","effectif":"Étudiants"},
                            title=f"Effectif — {LABEL_REGROUPEMENT.get(sel_regr, sel_regr)} · {annee_eff}", height=380)
                        fig_em.update_traces(textposition="outside")
                        fig_em.update_layout(showlegend=False)
                        st.plotly_chart(style(fig_em, 40), use_container_width=True)
                    with c2:
                        st.markdown("##### 📈 Évolution des effectifs")
                        df_e_all = df_eff_w[df_eff_w["metropole"].isin(sel_metros_eff) & (df_eff_w["regroupement"]==sel_regr)]
                        if sel_secteur != "Tous":
                            df_e_all = df_e_all[df_e_all["secteur_de_l_etablissement"]==sel_secteur]
                        evo_e = df_e_all.groupby(["annee","metropole"], as_index=False)["effectif"].sum().sort_values("annee")
                        fig_eve = px.line(evo_e, x="annee", y="effectif", color="metropole",
                            color_discrete_map=COULEURS, markers=True,
                            labels={"annee":"Année","effectif":"Étudiants","metropole":"Métropole"},
                            title="Évolution des effectifs étudiants", height=380)
                        fig_eve.update_traces(line_width=2.5, marker_size=7)
                        st.plotly_chart(style(fig_eve, 40), use_container_width=True)
                    st.markdown("---")

                    c3, c4 = st.columns(2)
                    with c3:
                        st.markdown(f"##### 🏛️ Répartition par filière ({annee_eff})")
                        df_type = df_eff_w[df_eff_w["metropole"].isin(sel_metros_eff) & (df_eff_w["annee"]==annee_eff) & (df_eff_w["regroupement"]!="TOTAL")]
                        if sel_secteur != "Tous":
                            df_type = df_type[df_type["secteur_de_l_etablissement"]==sel_secteur]
                        type_agg = df_type.groupby("regroupement", as_index=False)["effectif"].sum().sort_values("effectif", ascending=False).head(10)
                        type_agg["label"] = type_agg["regroupement"].map(lambda r: LABEL_REGROUPEMENT.get(r, r))
                        fig_pie = px.pie(type_agg, names="label", values="effectif",
                            title=f"Répartition par filière — {annee_eff}", hole=0.4, height=400)
                        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
                        st.plotly_chart(style(fig_pie, 40), use_container_width=True)
                    with c4:
                        st.markdown(f"##### ⚖️ Parité femmes / hommes ({annee_eff})")
                        if "sexe_de_l_etudiant" in df_e_yr.columns:
                            sex_agg = df_e_yr.groupby(["metropole","sexe_de_l_etudiant"], as_index=False)["effectif"].sum()
                            fig_sex = px.bar(sex_agg, x="metropole", y="effectif", color="sexe_de_l_etudiant",
                                barmode="group",
                                color_discrete_map={"Masculin":"#2D6A4F","Feminin":"#D4A017"},
                                labels={"metropole":"","effectif":"Étudiants","sexe_de_l_etudiant":"Genre"},
                                title=f"Parité H/F — {LABEL_REGROUPEMENT.get(sel_regr, sel_regr)}", height=400)
                            fig_sex.update_layout(legend=dict(orientation="h", y=1.1))
                            st.plotly_chart(style(fig_sex, 40), use_container_width=True)
                    st.markdown("---")

                    c5, c6 = st.columns(2)
                    with c5:
                        st.markdown(f"##### 🏆 Top 15 communes — {annee_eff}")
                        top_com = df_e_yr.groupby(["geo_nom","metropole"], as_index=False)["effectif"].sum().nlargest(15,"effectif")
                        fig_tc = px.bar(top_com, x="effectif", y="geo_nom", orientation="h",
                            color="metropole", color_discrete_map=COULEURS, text_auto=".3s",
                            labels={"geo_nom":"","effectif":"Étudiants"},
                            title=f"Top communes — {annee_eff}", height=430)
                        fig_tc.update_layout(yaxis={"categoryorder":"total ascending"})
                        st.plotly_chart(style(fig_tc, 40), use_container_width=True)
                    with c6:
                        st.markdown(f"##### 🏫 Public vs Privé ({annee_eff})")
                        if "secteur_de_l_etablissement" in df_e_yr.columns:
                            sec_agg = df_e_yr.groupby(["metropole","secteur_de_l_etablissement"], as_index=False)["effectif"].sum()
                            fig_sec = px.bar(sec_agg, x="metropole", y="effectif",
                                color="secteur_de_l_etablissement", barmode="stack",
                                color_discrete_map={"Établissements publics":"#2D6A4F","Établissements privés":"#D4A017"},
                                labels={"metropole":"","effectif":"Étudiants","secteur_de_l_etablissement":"Secteur"},
                                title=f"Répartition public / privé — {annee_eff}", height=430)
                            fig_sec.update_layout(legend=dict(orientation="h", y=1.1))
                            st.plotly_chart(style(fig_sec, 40), use_container_width=True)
                    st.markdown("---")
                    with st.expander("📄 Tableau de données"):
                        st.dataframe(df_e_yr.groupby(["metropole","geo_nom","regroupement","secteur_de_l_etablissement"],
                            as_index=False)["effectif"].sum().sort_values("effectif", ascending=False),
                            use_container_width=True)
                    with st.expander("📖 Note méthodologique"):
                        st.write("**Source** : MESRI. Communes des 5 dép. (38, 35, 76, 42, 34). "
                            "**TOTAL** agrège toutes filières. Effectif = inscrits en formation initiale.")

            # ── Comparateur de communes Éducation ──────────────────────────────────────
            with eff_comp:
                st.markdown('<p class="section-header">🔍 Comparateur de communes — Éducation</p>', unsafe_allow_html=True)
                with st.container():
                    st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
                    filter_bar("🔧 Filtres — Comparateur Éducation")
                    ec1, ec2, ec3, ec4 = st.columns([1, 1, 1, 1])
                    with ec1:
                        metro_ec = st.selectbox("Métropole", metros_eff, key="eff_cc_metro")
                    communes_ec = sorted(df_eff_w[df_eff_w["metropole"]==metro_ec]["geo_nom"].dropna().unique())
                    with ec2:
                        annee_ec = st.selectbox("Année", annees_eff, index=len(annees_eff)-1, key="eff_cc_annee")
                    with ec3:
                        com_a_eff = st.selectbox("Commune A", communes_ec, index=0, key="eff_cc_a")
                    with ec4:
                        com_b_eff = st.selectbox("Commune B", communes_ec, index=min(1,len(communes_ec)-1), key="eff_cc_b")
                    st.markdown('</div>', unsafe_allow_html=True)

                df_ea_eff = df_eff_w[(df_eff_w["geo_nom"]==com_a_eff) & (df_eff_w["annee"]==annee_ec) & (df_eff_w["regroupement"]!="TOTAL")]
                df_eb_eff = df_eff_w[(df_eff_w["geo_nom"]==com_b_eff) & (df_eff_w["annee"]==annee_ec) & (df_eff_w["regroupement"]!="TOTAL")]
                st.markdown("---")

                tot_a = int(df_ea_eff["effectif"].sum())
                tot_b = int(df_eb_eff["effectif"].sum())
                delta_eff = tot_a - tot_b
                k1, k2, k3 = st.columns(3)
                k1.metric(f"Effectif total — {com_a_eff}", fmt(tot_a))
                k2.metric(f"Effectif total — {com_b_eff}", fmt(tot_b))
                k3.metric("Écart", f"{delta_eff:+,d}".replace(",","\u202f"))
                st.markdown("---")

                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("##### 📊 Effectifs par filière")
                    df_fil_a = df_ea_eff.groupby("regroupement", as_index=False)["effectif"].sum().assign(Commune=com_a_eff)
                    df_fil_b = df_eb_eff.groupby("regroupement", as_index=False)["effectif"].sum().assign(Commune=com_b_eff)
                    df_fil_cc = pd.concat([df_fil_a, df_fil_b])
                    df_fil_cc["label"] = df_fil_cc["regroupement"].map(lambda r: LABEL_REGROUPEMENT.get(r, r))
                    if not df_fil_cc.empty:
                        fig_fil = px.bar(df_fil_cc, x="effectif", y="label", color="Commune",
                            orientation="h", barmode="group",
                            color_discrete_map={com_a_eff:"#2D6A4F", com_b_eff:"#D4A017"},
                            labels={"label":"","effectif":"Étudiants"},
                            title=f"Filières — {com_a_eff} vs {com_b_eff} ({annee_ec})", height=450)
                        fig_fil.update_layout(yaxis={"categoryorder":"total ascending"})
                        st.plotly_chart(style(fig_fil, 40), use_container_width=True)
                with c2:
                    st.markdown("##### ⚖️ Parité H/F")
                    if "sexe_de_l_etudiant" in df_eff_w.columns:
                        df_sex_a = df_eff_w[(df_eff_w["geo_nom"]==com_a_eff) & (df_eff_w["annee"]==annee_ec) & (df_eff_w["regroupement"]=="TOTAL")].groupby("sexe_de_l_etudiant", as_index=False)["effectif"].sum().assign(Commune=com_a_eff)
                        df_sex_b = df_eff_w[(df_eff_w["geo_nom"]==com_b_eff) & (df_eff_w["annee"]==annee_ec) & (df_eff_w["regroupement"]=="TOTAL")].groupby("sexe_de_l_etudiant", as_index=False)["effectif"].sum().assign(Commune=com_b_eff)
                        df_sex_cc = pd.concat([df_sex_a, df_sex_b])
                        if not df_sex_cc.empty:
                            fig_sex_cc = px.bar(df_sex_cc, x="Commune", y="effectif", color="sexe_de_l_etudiant",
                                barmode="group",
                                color_discrete_map={"Masculin":"#2D6A4F","Feminin":"#D4A017"},
                                labels={"Commune":"","effectif":"Étudiants","sexe_de_l_etudiant":"Genre"},
                                title="Parité H/F par commune", height=400)
                            st.plotly_chart(style(fig_sex_cc, 40), use_container_width=True)
                st.markdown("---")
                st.markdown("##### 📈 Évolution comparative")
                df_evo_a_eff = df_eff_w[(df_eff_w["geo_nom"]==com_a_eff) & (df_eff_w["regroupement"]=="TOTAL")].groupby("annee", as_index=False)["effectif"].sum().assign(Commune=com_a_eff)
                df_evo_b_eff = df_eff_w[(df_eff_w["geo_nom"]==com_b_eff) & (df_eff_w["regroupement"]=="TOTAL")].groupby("annee", as_index=False)["effectif"].sum().assign(Commune=com_b_eff)
                df_evo_cc_eff = pd.concat([df_evo_a_eff, df_evo_b_eff])
                if not df_evo_cc_eff.empty:
                    fig_evo_cc_eff = px.line(df_evo_cc_eff, x="annee", y="effectif", color="Commune",
                        color_discrete_map={com_a_eff:"#2D6A4F", com_b_eff:"#D4A017"},
                        markers=True, title=f"Évolution — {com_a_eff} vs {com_b_eff}", height=380)
                    fig_evo_cc_eff.update_traces(line_width=2.5, marker_size=7)
                    st.plotly_chart(style(fig_evo_cc_eff, 40), use_container_width=True)

    with s3:
        st.markdown('<p class="section-header">🏥 Santé</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="source-note">Source : OpenStreetMap — Établissements de santé géolocalisés · Métropoles françaises</p>',
            unsafe_allow_html=True,
        )

        # ── Chargement GeoJSON ────────────────────────────────────────────────
        import json

        GEOJSON_PATH = Path("solidarite&citoyennete/data_clean/sante/Etablissements_santé_filtre.geojson")

        @st.cache_data
        def charger_sante():
            with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            rows = []
            for feat in data["features"]:
                p = feat["properties"]
                coords = feat["geometry"]["coordinates"]
                rows.append({
                    "type_etab": p.get("type_etablissement", ""),
                    "nom": p.get("nom_etablissement") or "—",
                    "commune":   p.get("commune", ""),
                    "metropole": p.get("Métropole", ""),
                    "lon":       coords[0],
                    "lat":       coords[1],
                })
            return pd.DataFrame(rows)
            
        df_sante = charger_sante()

        TYPE_LABELS = {
            "pharmacy":    "Pharmacie",
            "doctors":     "Médecins / Soins",
            "dentist":     "Dentiste",
            "hospital":    "Hôpital",
            "nursing_home":"EHPAD / Maison de retraite",
            "clinic":      "Clinique / Centre de santé",
        }
        TYPE_COLORS = {
            "pharmacy":    "#2D6A4F",
            "doctors":     "#52B788",
            "dentist":     "#D4A017",
            "hospital":    "#C0392B",
            "nursing_home":"#8E44AD",
            "clinic":      "#1A78C2",
        }

        metros_sante  = sorted(df_sante["metropole"].dropna().unique())
        types_sante   = sorted(df_sante["type_etab"].dropna().unique())

        # ── Onglets ───────────────────────────────────────────────────────
        sante_t1, sante_t2, sante_t3 = st.tabs([
            "🗺️ Carte & Répartition",
            "📊 Statistiques",
            "🏘️ Analyse par commune",
        ])

        # ═════════════════════════════════════════════════════════════════
        # ONGLET 1 — CARTE & RÉPARTITION
        # ═════════════════════════════════════════════════════════════════
        with sante_t1:

            with st.container():
                st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
                filter_bar("🔧 Filtres — Établissements de santé")
                pv1, pv2, pv3 = st.columns(3)
                with pv1:
                    mode_sante = st.radio(
                        "Niveau géographique",
                        ["Comparaison Métropoles", "Détail Communal"],
                        key="sante_mode", horizontal=True,
                    )
                with pv2:
                    sel_metro_sante = st.selectbox(
                        "Métropole",
                        metros_sante,
                        index=metros_sante.index("Grenoble") if "Grenoble" in metros_sante else 0,
                        key="sante_metro_t1",
                    )
                with pv3:
                    sel_types_sante = st.multiselect(
                        "Type d'établissement",
                        options=types_sante,
                        default=types_sante,
                        format_func=lambda t: TYPE_LABELS.get(t, t),
                        key="sante_types_t1",
                    )
                if mode_sante == "Détail Communal":
                    communes_sante_dispo = sorted(
                        df_sante[df_sante["metropole"] == sel_metro_sante]["commune"].dropna().unique()
                    )
                    sel_communes_sante = st.multiselect(
                        "Communes",
                        communes_sante_dispo,
                        default=communes_sante_dispo[:5],
                        key="sante_communes_t1",
                    )
                st.markdown('</div>', unsafe_allow_html=True)

            # Filtrage
            if mode_sante == "Comparaison Métropoles":
                df_sf = df_sante[df_sante["type_etab"].isin(sel_types_sante)].copy()
            else:
                df_sf = df_sante[
                    (df_sante["metropole"] == sel_metro_sante) &
                    (df_sante["commune"].isin(sel_communes_sante)) &
                    (df_sante["type_etab"].isin(sel_types_sante))
                ].copy()

            # KPIs
            sk1, sk2, sk3, sk4, sk5 = st.columns(5)
            sk1.metric("Total établissements", len(df_sf))
            sk2.metric("Pharmacies",           len(df_sf[df_sf["type_etab"] == "pharmacy"]))
            sk3.metric("Médecins / Soins",     len(df_sf[df_sf["type_etab"] == "doctors"]))
            sk4.metric("Hôpitaux",             len(df_sf[df_sf["type_etab"] == "hospital"]))
            sk5.metric("Communes couvertes",   df_sf["commune"].nunique())

            st.markdown("---")
            col_map, col_chart = st.columns([1.1, 0.9])

            with col_map:
                st.markdown("##### 🗺️ Carte des établissements")
                if df_sf.empty:
                    st.info("Aucun établissement pour ces filtres.")
                else:
                    fig_map = px.scatter_mapbox(
                        df_sf,
                        lat="lat", lon="lon",
                        color="type_etab",
                        color_discrete_map=TYPE_COLORS,
                        hover_name="nom",
                        hover_data={"commune": True, "type_etab": False, "lat": False, "lon": False},
                        labels={"type_etab": "Type", "commune": "Commune"},
                        zoom=10 if mode_sante == "Comparaison Métropoles" else 11,
                        height=480,
                        mapbox_style="carto-positron",
                    )
                    fig_map.update_traces(marker=dict(size=7, opacity=0.85))
                    for trace in fig_map.data:
                        trace.name = TYPE_LABELS.get(trace.name, trace.name)
                    fig_map.update_layout(
                        legend=dict(
                            title="Type", orientation="v", x=0.01, y=0.99,
                            bgcolor="rgba(255,255,255,0.85)",
                            bordercolor="#C8E6D4", borderwidth=1,
                            font=dict(size=11),
                        ),
                        margin=dict(l=0, r=0, t=0, b=0),
                        paper_bgcolor="rgba(0,0,0,0)",
                        font_family="Sora",
                    )
                    st.plotly_chart(fig_map, use_container_width=True)

            with col_chart:
                st.markdown("##### 📊 Nombre d'établissements par type")
                counts_sf = (
                    df_sf.groupby("type_etab").size()
                            .reset_index(name="count")
                            .sort_values("count", ascending=True)
                )
                counts_sf["label"] = counts_sf["type_etab"].map(lambda t: TYPE_LABELS.get(t, t))
                fig_bar = px.bar(
                    counts_sf, x="count", y="label", orientation="h",
                    color="type_etab", color_discrete_map=TYPE_COLORS,
                    text="count",
                    labels={"count": "Nombre", "label": ""},
                    height=480,
                )
                fig_bar.update_traces(textposition="outside", showlegend=False)
                fig_bar.update_layout(
                    xaxis_title="Nombre d'établissements",
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font_family="Sora",
                    margin=dict(l=10, r=30, t=10, b=40),
                    xaxis=dict(gridcolor="#E8F5EE"),
                )
                st.plotly_chart(style(fig_bar, 40), use_container_width=True)

        # ═════════════════════════════════════════════════════════════════
        # ONGLET 2 — STATISTIQUES
        # ═════════════════════════════════════════════════════════════════
        with sante_t2:

            with st.container():
                st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
                filter_bar("🔧 Filtres — Statistiques")
                sf1, sf2, sf3 = st.columns(3)
                with sf1:
                    mode_stats = st.radio(
                        "Niveau géographique",
                        ["Comparaison Métropoles", "Détail Communal"],
                        key="sante_stats_mode", horizontal=True,
                    )
                with sf2:
                    sel_metro_stats = st.selectbox(
                        "Métropole",
                        metros_sante,
                        index=metros_sante.index("Grenoble") if "Grenoble" in metros_sante else 0,
                        key="sante_stats_metro",
                    )
                with sf3:
                    sel_types_stats = st.multiselect(
                        "Types",
                        options=types_sante,
                        default=types_sante,
                        format_func=lambda t: TYPE_LABELS.get(t, t),
                        key="sante_stats_types",
                    )
                st.markdown('</div>', unsafe_allow_html=True)

            if mode_stats == "Comparaison Métropoles":
                df_ss = df_sante[df_sante["type_etab"].isin(sel_types_stats)].copy()
            else:
                df_ss = df_sante[
                    (df_sante["metropole"] == sel_metro_stats) &
                    (df_sante["type_etab"].isin(sel_types_stats))
                ].copy()

            st.markdown("---")
            sc1, sc2 = st.columns(2)

            with sc1:
                st.markdown("##### 🗂️ Répartition par type (treemap)")
                if mode_stats == "Comparaison Métropoles":
                    tm_data = df_ss.groupby(["metropole", "type_etab"]).size().reset_index(name="count")
                    tm_data["label"] = tm_data["type_etab"].map(lambda t: TYPE_LABELS.get(t, t))
                    fig_tm = px.treemap(
                        tm_data, path=["metropole", "label"], values="count",
                        color="type_etab", color_discrete_map=TYPE_COLORS, height=360,
                    )
                else:
                    tm_data = df_ss.groupby("type_etab").size().reset_index(name="count")
                    tm_data["label"] = tm_data["type_etab"].map(lambda t: TYPE_LABELS.get(t, t))
                    tm_data["pct"] = (tm_data["count"] / tm_data["count"].sum() * 100).round(1)
                    fig_tm = px.treemap(
                        tm_data, path=["label"], values="count",
                        color="type_etab", color_discrete_map=TYPE_COLORS,
                        custom_data=["pct"], height=360,
                    )
                    fig_tm.update_traces(
                        texttemplate="<b>%{label}</b><br>%{value} étab.<br>%{customdata[0]}%",
                        textfont_size=12,
                    )
                fig_tm.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", font_family="Sora",
                    margin=dict(l=0, r=0, t=10, b=0),
                )
                st.plotly_chart(fig_tm, use_container_width=True)

            with sc2:
                st.markdown("##### 🏆 Top 10 communes par nombre d'établissements")
                group_col = "metropole" if mode_stats == "Comparaison Métropoles" else "commune"
                top_comm = (
                    df_ss.groupby(group_col).size()
                            .reset_index(name="count")
                            .sort_values("count", ascending=False)
                            .head(10)
                )
                fig_top = px.bar(
                    top_comm.sort_values("count"),
                    x="count", y=group_col, orientation="h", text="count",
                    color_discrete_sequence=["#2D6A4F"],
                    labels={"count": "Établissements", group_col: ""},
                    height=360,
                )
                fig_top.update_traces(textposition="outside")
                fig_top.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font_family="Sora", xaxis=dict(gridcolor="#E8F5EE"),
                    margin=dict(l=10, r=30, t=10, b=40),
                )
                st.plotly_chart(style(fig_top, 40), use_container_width=True)

            st.markdown("---")
            st.markdown("##### 📊 Répartition par commune × type (Top 15)")
            scope_stack = df_ss if mode_stats == "Comparaison Métropoles" else df_ss
            top15 = (
                scope_stack.groupby("commune" if mode_stats == "Détail Communal" else "metropole")
                            .size().sort_values(ascending=False).head(15).index.tolist()
            )
            grp_col = "commune" if mode_stats == "Détail Communal" else "metropole"
            df_stack_s = (
                scope_stack[scope_stack[grp_col].isin(top15)]
                .groupby([grp_col, "type_etab"]).size().reset_index(name="count")
            )
            fig_stack_s = px.bar(
                df_stack_s, x=grp_col, y="count", color="type_etab",
                color_discrete_map=TYPE_COLORS, barmode="stack",
                labels={grp_col: "", "count": "Établissements", "type_etab": "Type"},
                height=420,
            )
            for trace in fig_stack_s.data:
                trace.name = TYPE_LABELS.get(trace.name, trace.name)
            fig_stack_s.update_layout(
                xaxis_tickangle=-35,
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_family="Sora", yaxis=dict(gridcolor="#E8F5EE"),
                legend=dict(orientation="h", y=-0.3),
                margin=dict(l=10, r=10, t=10, b=100),
            )
            st.plotly_chart(style(fig_stack_s), use_container_width=True)

            st.markdown("---")
            with st.expander("📄 Tableau de données"):
                df_tab = (
                    df_ss.groupby([grp_col, "type_etab"]).size()
                            .reset_index(name="count")
                )
                df_tab["type_etab"] = df_tab["type_etab"].map(lambda t: TYPE_LABELS.get(t, t))
                df_tab.columns = [grp_col.capitalize(), "Type", "Nb établissements"]
                st.dataframe(df_tab.set_index(grp_col.capitalize()), use_container_width=True)

            with st.expander("📖 Note méthodologique"):
                st.write(
                    "**Source** : OpenStreetMap — données filtrées sur les communes des 5 métropoles.\n\n"
                    "**Types d'établissements** : pharmacie, médecin/soins paramédicaux, dentiste, "
                    "hôpital, EHPAD/maison de retraite, clinique/centre de santé.\n\n"
                    "**Périmètre** : communes appartenant aux métropoles Grenoble, Rennes, "
                    "Saint-Étienne, Rouen, Montpellier."
                )

        # ═════════════════════════════════════════════════════════════════
        # ONGLET 3 — ANALYSE PAR COMMUNE
        # ═════════════════════════════════════════════════════════════════
        with sante_t3:

            with st.container():
                st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
                filter_bar("🔧 Filtres — Analyse par commune")
                cf1, cf2, cf3 = st.columns(3)
                with cf1:
                    mode_comm = st.radio(
                        "Niveau géographique",
                        ["Comparaison Métropoles", "Détail Communal"],
                        key="sante_comm_mode", horizontal=True,
                    )
                with cf2:
                    sel_metro_comm = st.selectbox(
                        "Métropole",
                        metros_sante,
                        index=metros_sante.index("Grenoble") if "Grenoble" in metros_sante else 0,
                        key="sante_comm_metro",
                    )
                with cf3:
                    communes_comm_dispo = sorted(
                        df_sante[df_sante["metropole"] == sel_metro_comm]["commune"].dropna().unique()
                    )
                    commune_focus = st.selectbox(
                        "Commune à analyser",
                        communes_comm_dispo,
                        index=communes_comm_dispo.index("Grenoble") if "Grenoble" in communes_comm_dispo else 0,
                        key="sante_comm_focus",
                    )
                st.markdown('</div>', unsafe_allow_html=True)

            df_metro_comm = df_sante[df_sante["metropole"] == sel_metro_comm].copy()
            df_focus = df_metro_comm[df_metro_comm["commune"] == commune_focus].copy()

            # KPIs
            ck1, ck2, ck3, ck4 = st.columns(4)
            ck1.metric("Total établissements",  len(df_focus))
            ck2.metric("Pharmacies",            len(df_focus[df_focus["type_etab"] == "pharmacy"]))
            ck3.metric("Médecins / Soins",      len(df_focus[df_focus["type_etab"] == "doctors"]))
            ck4.metric("Hôpitaux / Cliniques",  len(df_focus[df_focus["type_etab"].isin(["hospital", "clinic"])]))

            st.markdown("---")
            cc1, cc2 = st.columns(2)

            with cc1:
                st.markdown("##### 🍩 Répartition par type")
                if df_focus.empty:
                    st.info("Aucune donnée pour cette commune.")
                else:
                    donut_data = (
                        df_focus.groupby("type_etab").size().reset_index(name="count")
                    )
                    donut_data["label"] = donut_data["type_etab"].map(lambda t: TYPE_LABELS.get(t, t))
                    fig_donut = px.pie(
                        donut_data, names="label", values="count",
                        color="type_etab", color_discrete_map=TYPE_COLORS,
                        hole=0.45, height=340,
                    )
                    fig_donut.update_traces(textinfo="percent+label", textfont_size=12)
                    fig_donut.update_layout(
                        showlegend=False, paper_bgcolor="rgba(0,0,0,0)",
                        font_family="Sora", margin=dict(l=10, r=10, t=10, b=10),
                    )
                    st.plotly_chart(fig_donut, use_container_width=True)

            with cc2:
                st.markdown("##### 📊 Part dans la métropole par type")
                metro_cnt  = df_metro_comm.groupby("type_etab").size().reset_index(name="total_metro")
                commune_cnt = df_focus.groupby("type_etab").size().reset_index(name="total_commune")
                comp = metro_cnt.merge(commune_cnt, on="type_etab", how="left").fillna(0)
                comp["pct"] = (comp["total_commune"] / comp["total_metro"] * 100).round(1)
                comp["label"] = comp["type_etab"].map(lambda t: TYPE_LABELS.get(t, t))
                comp = comp.sort_values("pct", ascending=True)
                fig_comp = px.bar(
                    comp, x="pct", y="label", orientation="h",
                    text=comp["pct"].apply(lambda v: f"{v:.1f}%"),
                    color="type_etab", color_discrete_map=TYPE_COLORS,
                    labels={"pct": "Part (%)", "label": ""},
                    height=340,
                )
                fig_comp.update_traces(showlegend=False, textposition="outside")
                fig_comp.update_layout(
                    xaxis_title="% des établissements de la métropole",
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font_family="Sora", xaxis=dict(gridcolor="#E8F5EE"),
                    margin=dict(l=10, r=40, t=10, b=40),
                )
                st.plotly_chart(style(fig_comp, 40), use_container_width=True)

            st.markdown("---")
            with st.expander(f"📋 Liste complète — {commune_focus} ({len(df_focus)} établissements)"):
                df_display = df_focus[["type_etab", "nom"]].copy()
                df_display["type_etab"] = df_display["type_etab"].map(lambda t: TYPE_LABELS.get(t, t))
                df_display.columns = ["Type", "Nom"]
                df_display = df_display.sort_values(["Type", "Nom"]).reset_index(drop=True)
                st.dataframe(df_display, use_container_width=True, height=300)

    with s4:
        st.markdown('<p class="section-header">Participation citoyenne - Élections municipales</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="source-note">Source : '
            '<a href="https://www.data.gouv.fr/datasets/elections-municipales-2020-resultats-1er-tour/" target="_blank">'
            'Data.gouv — Élections municipales 2014 & 2020 (1er et 2e tour)</a></p>',
            unsafe_allow_html=True,
        )

        @st.cache_data
        def charger_elections():
            df = pd.read_csv("solidarite&citoyennete/data_clean/participation_citoyenne/elections_2014_2020.csv")
            return df

        df_elec = charger_elections()

        DEP_METRO_ELEC = {
            "Isère": "Grenoble", "Ille-et-Vilaine": "Rennes",
            "Seine-Maritime": "Rouen", "Loire": "Saint-Étienne", "Hérault": "Montpellier",
        }
        df_elec["metropole"] = df_elec["Libellé du département"].map(DEP_METRO_ELEC)
        df_elec["% Participation"] = 100 - df_elec["% Abs/Ins"]

        annees_elec = sorted(df_elec["Année"].dropna().unique().astype(int))
        tours_elec  = sorted(df_elec["Numéro de tour"].dropna().unique().astype(int))
        metros_elec = sorted(df_elec["metropole"].dropna().unique())

        with st.container():
            st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
            filter_bar("Filtres — Participation citoyenne")
            pv1, pv2, pv3 = st.columns(3)
            with pv1:
                mode_part = st.radio(
                    "Niveau géographique",
                    ["Comparaison Métropoles", "Détail Communal"],
                    key="part_mode", horizontal=True,
                )
            with pv2:
                sel_annee_part = st.selectbox("Année", annees_elec,
                    index=len(annees_elec)-1, key="part_annee")
            with pv3:
                sel_tour_part = st.selectbox("Tour", tours_elec,
                    format_func=lambda t: f"Tour {t}", key="part_tour")

            if mode_part == "Détail Communal":
                communes_elec_dispo = sorted(
                    df_elec[df_elec["metropole"] == "Grenoble"]["Libellé de la commune"].dropna().unique()
                )
                sel_communes_part = st.multiselect(
                    "Communes (Grenoble)", communes_elec_dispo,
                    default=communes_elec_dispo[:5], key="part_communes",
                )
            else:
                sel_metros_part = st.multiselect(
                    "Métropoles à comparer", metros_elec, default=metros_elec, key="part_metros",
                )
            st.markdown('</div>', unsafe_allow_html=True)

        df_elec_f = df_elec[
            (df_elec["Année"] == sel_annee_part) &
            (df_elec["Numéro de tour"] == sel_tour_part)
        ]

        if mode_part == "Comparaison Métropoles":
            df_elec_f = df_elec_f[df_elec_f["metropole"].isin(sel_metros_part)]
            df_agg = df_elec_f.groupby("metropole", as_index=False).agg(
                Inscrits=("Inscrits", "sum"),
                Votants=("Votants", "sum"),
                Abstentions=("Abstentions", "sum"),
            )
            df_agg["% Participation"] = (df_agg["Votants"] / df_agg["Inscrits"] * 100).round(2)
            df_agg["% Abstention"]    = (df_agg["Abstentions"] / df_agg["Inscrits"] * 100).round(2)
        else:
            df_elec_f = df_elec_f[df_elec_f["Libellé de la commune"].isin(sel_communes_part)]
            df_agg = df_elec_f.groupby("Libellé de la commune", as_index=False).agg(
                Inscrits=("Inscrits", "sum"),
                Votants=("Votants", "sum"),
                Abstentions=("Abstentions", "sum"),
            )
            df_agg["% Participation"] = (df_agg["Votants"] / df_agg["Inscrits"] * 100).round(2)
            df_agg["% Abstention"]    = (df_agg["Abstentions"] / df_agg["Inscrits"] * 100).round(2)
            df_agg = df_agg.rename(columns={"Libellé de la commune": "metropole"})

        st.markdown("---")

        if df_agg.empty:
            st.warning("⚠️ Aucune donnée pour les filtres sélectionnés.")
        else:
            kpi_cols_part = st.columns(len(df_agg))
            for i, row in df_agg.iterrows():
                with kpi_cols_part[i]:
                    st.metric(
                        label=row["metropole"],
                        value=f"{row['% Participation']:.1f} %",
                        delta=f"{row['% Participation'] - df_agg['% Participation'].mean():+.1f} pts vs moy.",
                    )

            st.markdown("---")
            c1, c2 = st.columns(2)

            with c1:
                st.markdown("##### 🗳️ Taux de participation")
                fig_part = px.bar(
                    df_agg.sort_values("% Participation", ascending=False),
                    x="metropole", y="% Participation",
                    color="metropole",
                    color_discrete_map=COULEURS,
                    text=df_agg.sort_values("% Participation", ascending=False)["% Participation"].apply(lambda v: f"{v:.1f}%"),
                    labels={"metropole": "", "% Participation": "Participation (%)"},
                    title=f"Participation — {sel_annee_part} · Tour {sel_tour_part}",
                    height=400,
                )
                fig_part.update_traces(textposition="outside")
                fig_part.update_layout(showlegend=False, yaxis_range=[0, 100])
                st.plotly_chart(style(fig_part, 40), use_container_width=True)

            with c2:
                st.markdown("##### 📊 Participation vs Abstention")
                df_stack = df_agg[["metropole", "% Participation", "% Abstention"]].melt(
                    id_vars="metropole", var_name="Type", value_name="Taux"
                )
                fig_stack = px.bar(
                    df_stack, x="metropole", y="Taux", color="Type",
                    barmode="stack",
                    color_discrete_map={"% Participation": "#2D6A4F", "% Abstention": "#D4A017"},
                    labels={"metropole": "", "Taux": "%", "Type": ""},
                    title="Répartition Participation / Abstention",
                    height=400,
                )
                fig_stack.update_layout(yaxis_range=[0, 100], legend=dict(orientation="h", y=1.1))
                st.plotly_chart(style(fig_stack, 40), use_container_width=True)

            st.markdown("---")
            st.markdown("##### 📈 Évolution de la participation (2014 → 2020)")
            df_evo = df_elec[df_elec["Numéro de tour"] == sel_tour_part].copy()
            if mode_part == "Comparaison Métropoles":
                df_evo = df_evo[df_evo["metropole"].isin(sel_metros_part)]
                df_evo_agg = df_evo.groupby(["Année", "metropole"], as_index=False).agg(
                    Inscrits=("Inscrits", "sum"), Votants=("Votants", "sum")
                )
                color_col = "metropole"
            else:
                df_evo = df_evo[df_evo["Libellé de la commune"].isin(sel_communes_part)]
                df_evo_agg = df_evo.groupby(["Année", "Libellé de la commune"], as_index=False).agg(
                    Inscrits=("Inscrits", "sum"), Votants=("Votants", "sum")
                )
                df_evo_agg = df_evo_agg.rename(columns={"Libellé de la commune": "metropole"})
                color_col = "metropole"
            df_evo_agg["% Participation"] = (df_evo_agg["Votants"] / df_evo_agg["Inscrits"] * 100).round(2)
            fig_evo = px.line(
                df_evo_agg, x="Année", y="% Participation", color=color_col,
                color_discrete_map=COULEURS, markers=True,
                labels={"Année": "Année", "% Participation": "Participation (%)", color_col: ""},
                title=f"Évolution participation — Tour {sel_tour_part}",
                height=380,
            )
            fig_evo.update_traces(line_width=2.5, marker_size=9)
            fig_evo.update_layout(yaxis_range=[0, 100], legend=dict(orientation="h", y=1.1))
            st.plotly_chart(style(fig_evo), use_container_width=True)

            st.markdown("---")
            with st.expander("📄 Tableau de données"):
                st.dataframe(df_agg.set_index("metropole"), use_container_width=True)
            with st.expander("📖 Note méthodologique"):
                st.write(
                    "**Source** : Data.gouv — Élections municipales 2014 & 2020.\n\n"
                    "**Taux de participation** = Votants / Inscrits × 100.\n\n"
                    "**Périmètre** : communes des 5 métropoles. "
                    "Pour 2014, les communes de moins de 1 000 habitants utilisent un fichier TXT séparé."
                )

    # ──────────────────────────────────────────────────────────────────────────
    # ONGLET REVENUS & PAUVRETÉ — FiLoSoFi IRIS 2021
    # ──────────────────────────────────────────────────────────────────────────
    with s5:
        st.markdown('<p class="section-header">💶 Revenus & pauvreté — FiLoSoFi IRIS 2021</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="source-note">Source : <a href="https://www.insee.fr/fr/statistiques/8268806" target="_blank">'
            'INSEE-DGFIP-Cnaf-Cnav-CCMSA · Fichier localisé social et fiscal (FiLoSoFi) · Revenus déclarés 2021 à l\'IRIS</a></p>',
            unsafe_allow_html=True,
        )

        if df_filo is None or df_filo.empty:
            st.info("📂 Fichier `BASE_TD_FILO_IRIS_2021_DEC.xlsx` introuvable — placez-le dans `solidarite&citoyennete/data_clean/revenus/`.")
        else:
            # ── Libellés des indicateurs ──────────────────────────────────
            FILO_LABELS = {
                "DEC_MED21":    "Revenu médian (€/UC)",
                "DEC_TP6021":   "Taux de bas revenus — seuil 60 % (%)",
                "DEC_Q121":     "1er quartile Q1 (€/UC)",
                "DEC_Q321":     "3e quartile Q3 (€/UC)",
                "DEC_D121":     "1er décile D1 (€/UC)",
                "DEC_D921":     "9e décile D9 (€/UC)",
                "DEC_RD21":     "Rapport interdécile D9/D1",
                "DEC_S80S2021": "Ratio S80/S20",
                "DEC_GI21":     "Indice de Gini",
                "DEC_EQ21":     "Écart interquartile / médiane",
                "DEC_PIMP21":   "Part ménages imposés (%)",
                "DEC_PACT21":   "Part revenus d'activité (%)",
                "DEC_PTSA21":   "dont salaires & traitements (%)",
                "DEC_PCHO21":   "dont indemnités chômage (%)",
                "DEC_PBEN21":   "dont revenus non salariés (%)",
                "DEC_PPEN21":   "Part pensions & retraites (%)",
                "DEC_PAUT21":   "Part autres revenus (%)",
            }
            filo_cols = [c for c in FILO_LABELS if c in df_filo.columns]

            metros_filo = sorted(df_filo["metropole"].dropna().unique())

            # ── Sous-onglets : Vue d'ensemble | Comparateur communes ──────
            filo_vue, filo_comp = st.tabs(["📊 Vue d'ensemble", "🔍 Comparateur de communes"])

            # ════════════════════════════════════════════════════════════════
            # VUE D'ENSEMBLE
            # ════════════════════════════════════════════════════════════════
            with filo_vue:
                with st.container():
                    st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
                    filter_bar("🔧 Filtres — Revenus & pauvreté")
                    fv1, fv2, fv3 = st.columns([2, 2, 2])
                    with fv1:
                        filo_ind = st.selectbox(
                            "Indicateur principal",
                            filo_cols,
                            format_func=lambda c: FILO_LABELS.get(c, c),
                            index=filo_cols.index("DEC_MED21") if "DEC_MED21" in filo_cols else 0,
                            key="filo_ind",
                        )
                    with fv2:
                        sel_metros_filo = st.multiselect(
                            "Métropoles", metros_filo, default=metros_filo, key="filo_metros"
                        )
                    with fv3:
                        filo_niveau = st.selectbox(
                            "Niveau d'analyse", ["Commune (médiane des IRIS)", "IRIS (détail)"],
                            key="filo_niveau"
                        )
                    st.markdown('</div>', unsafe_allow_html=True)

                if not sel_metros_filo:
                    st.warning("⚠️ Sélectionnez au moins une métropole.")
                else:
                    df_f = df_filo[df_filo["metropole"].isin(sel_metros_filo)].copy()
                    lbl  = FILO_LABELS.get(filo_ind, filo_ind)

                    if filo_niveau == "Commune (médiane des IRIS)":
                        df_agg = df_f.groupby(["metropole", "LIBCOM"], as_index=False)[filo_cols].median()
                    else:
                        df_agg = df_f.copy()
                        df_agg["LIBCOM"] = df_agg["LIBIRIS"] + " (" + df_agg["LIBCOM"] + ")"

                    st.markdown("---")

                    # ── KPI par métropole ──────────────────────────────────
                    st.markdown(f"#### 📌 Aperçu — {lbl}")
                    kpi_cols = st.columns(len(sel_metros_filo))
                    for i, metro in enumerate(sel_metros_filo):
                        sub = df_agg[df_agg["metropole"] == metro][filo_ind].dropna()
                        val = sub.median() if not sub.empty else np.nan
                        with kpi_cols[i]:
                            st.markdown(f"""
                            <div class='kpi-card-mob' style='border-top: none; border-left: 5px solid #1e5631; padding-left: 15px; text-align: left;'>
                                <div class='kpi-label'>{metro}</div>
                                <div class='kpi-value'>{fmt(val, dec=1)}</div>
                                <div style='font-size:11px;color:#888'>{lbl}</div>
                            </div>
                            """, unsafe_allow_html=True)

                    st.markdown("---")

                    # ── Ligne 1 : Box-plot + Bar comparatif ───────────────
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"##### 📦 Distribution par métropole")
                        fig_box = px.box(
                            df_f.dropna(subset=[filo_ind]),
                            x="metropole", y=filo_ind,
                            color="metropole",
                            color_discrete_map=COULEURS,
                            labels={"metropole": "", filo_ind: lbl},
                            title=f"Distribution — {lbl}",
                            height=400,
                        )
                        fig_box.update_layout(showlegend=False)
                        st.plotly_chart(style(fig_box, 40), use_container_width=True)

                    with c2:
                        st.markdown(f"##### 🏆 Top / Flop communes")
                        df_bar = df_agg.dropna(subset=[filo_ind]).sort_values(filo_ind, ascending=False)
                        n_show = min(20, len(df_bar))
                        top_n  = pd.concat([df_bar.head(10), df_bar.tail(10)]).drop_duplicates()
                        fig_hbar = px.bar(
                            top_n.sort_values(filo_ind),
                            x=filo_ind, y="LIBCOM",
                            color="metropole",
                            color_discrete_map=COULEURS,
                            orientation="h",
                            labels={"LIBCOM": "", filo_ind: lbl},
                            title=f"Top/Flop communes — {lbl}",
                            height=450,
                        )
                        st.plotly_chart(style(fig_hbar, 40), use_container_width=True)

                    st.markdown("---")

                    # ── Ligne 2 : Scatter médiane vs taux pauvreté + Gini ──
                    c3, c4 = st.columns(2)
                    with c3:
                        st.markdown("##### 💹 Revenu médian vs Taux de bas revenus")
                        if "DEC_MED21" in df_agg.columns and "DEC_TP6021" in df_agg.columns:
                            df_sc = df_agg.dropna(subset=["DEC_MED21", "DEC_TP6021"])
                            fig_sc = px.scatter(
                                df_sc, x="DEC_MED21", y="DEC_TP6021",
                                color="metropole", color_discrete_map=COULEURS,
                                hover_name="LIBCOM",
                                labels={"DEC_MED21": "Revenu médian (€/UC)", "DEC_TP6021": "Taux bas revenus (%)"},
                                title="Médiane vs Précarité",
                                height=400,
                            )
                            fig_sc.update_traces(marker_size=7, marker_opacity=0.75)
                            st.plotly_chart(style(fig_sc, 40), use_container_width=True)
                        else:
                            st.info("Colonnes DEC_MED21 / DEC_TP6021 absentes.")

                    with c4:
                        st.markdown("##### ⚖️ Inégalités — Indice de Gini par commune")
                        if "DEC_GI21" in df_agg.columns:
                            df_gi = df_agg.dropna(subset=["DEC_GI21"]).sort_values("DEC_GI21", ascending=False).head(20)
                            fig_gi = px.bar(
                                df_gi, x="DEC_GI21", y="LIBCOM",
                                color="metropole", color_discrete_map=COULEURS,
                                orientation="h",
                                labels={"LIBCOM": "", "DEC_GI21": "Indice de Gini"},
                                title="Top 20 communes — Indice de Gini",
                                height=420,
                            )
                            fig_gi.update_layout(yaxis={"categoryorder": "total ascending"})
                            st.plotly_chart(style(fig_gi, 40), use_container_width=True)

                    st.markdown("---")

                    # ── Ligne 3 : Structure des revenus (camembert) + D9/D1 ─
                    c5, c6 = st.columns(2)
                    with c5:
                        st.markdown("##### 🥧 Structure des revenus (moyenne métropoles sélectionnées)")
                        struct_cols = {
                            "Salaires & traitements": "DEC_PTSA21",
                            "Indemnités chômage":     "DEC_PCHO21",
                            "Revenus non salariés":   "DEC_PBEN21",
                            "Pensions & retraites":   "DEC_PPEN21",
                            "Autres revenus":         "DEC_PAUT21",
                        }
                        struct_avail = {k: v for k, v in struct_cols.items() if v in df_f.columns}
                        if struct_avail:
                            means = {k: df_f[v].mean() for k, v in struct_avail.items()}
                            fig_pie = px.pie(
                                names=list(means.keys()), values=list(means.values()),
                                title="Composition moyenne du revenu",
                                hole=0.35, height=380,
                            )
                            fig_pie.update_traces(textposition="inside", textinfo="percent+label")
                            st.plotly_chart(style(fig_pie, 40), use_container_width=True)

                    with c6:
                        st.markdown("##### 📊 Rapport D9/D1 — inégalités entre IRIS")
                        if "DEC_RD21" in df_agg.columns:
                            df_rd = df_agg.dropna(subset=["DEC_RD21"])
                            fig_rd = px.box(
                                df_rd, x="metropole", y="DEC_RD21",
                                color="metropole", color_discrete_map=COULEURS,
                                labels={"metropole": "", "DEC_RD21": "D9/D1"},
                                title="Rapport interdécile D9/D1 (plus c'est haut, plus c'est inégal)",
                                height=380,
                            )
                            fig_rd.update_layout(showlegend=False)
                            st.plotly_chart(style(fig_rd, 40), use_container_width=True)

                    st.markdown("---")

                    # ── Statistiques descriptives ──────────────────────────
                    with st.expander("📊 Statistiques descriptives complètes"):
                        desc_cols = ["DEC_MED21", "DEC_TP6021", "DEC_GI21", "DEC_RD21",
                                     "DEC_S80S2021", "DEC_Q121", "DEC_Q321"]
                        desc_avail = [c for c in desc_cols if c in df_f.columns]
                        desc_df = (df_f.groupby("metropole")[desc_avail]
                                   .agg(["median", "mean", "std", "min", "max"])
                                   .round(2))
                        desc_df.columns = [f"{FILO_LABELS.get(c, c)} — {s}" for c, s in desc_df.columns]
                        st.dataframe(desc_df, use_container_width=True)

                    with st.expander("📖 Note méthodologique"):
                        st.write(
                            "**Source** : INSEE-DGFIP-Cnaf-Cnav-CCMSA, Fichier localisé social et fiscal (FiLoSoFi) — Année 2021.\n\n"
                            "**Indicateurs** exprimés par **unité de consommation (UC)** — 1 UC pour le 1er adulte, 0,5 pour les autres personnes ≥ 14 ans, 0,3 pour les moins de 14 ans.\n\n"
                            "**Taux de bas revenus** : part des ménages dont le revenu/UC est inférieur à 60 % du revenu médian métropolitain.\n\n"
                            "**Indice de Gini** : entre 0 (égalité parfaite) et 1 (inégalité maximale).\n\n"
                            "**Périmètre** : IRIS appartenant aux communes des 5 métropoles, identifiés par code département."
                        )

            # ════════════════════════════════════════════════════════════════
            # COMPARATEUR DE COMMUNES
            # ════════════════════════════════════════════════════════════════
            with filo_comp:
                st.markdown('<p class="section-header">🔍 Comparateur de communes — Revenus & pauvreté</p>', unsafe_allow_html=True)

                with st.container():
                    st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
                    filter_bar("🔧 Filtres — Comparateur")
                    fc1, fc2, fc3 = st.columns([1, 2, 2])
                    with fc1:
                        metro_comp_filo = st.selectbox("Métropole", metros_filo, key="filo_comp_metro")
                    communes_filo_dispo = sorted(
                        df_filo[df_filo["metropole"] == metro_comp_filo]["LIBCOM"].dropna().unique()
                    )
                    with fc2:
                        com_a_filo = st.selectbox("Commune A", communes_filo_dispo, index=0, key="filo_com_a")
                    with fc3:
                        default_b = communes_filo_dispo[1] if len(communes_filo_dispo) > 1 else communes_filo_dispo[0]
                        com_b_filo = st.selectbox("Commune B", communes_filo_dispo, index=1, key="filo_com_b")
                    st.markdown('</div>', unsafe_allow_html=True)

                df_ca = df_filo[(df_filo["metropole"] == metro_comp_filo) & (df_filo["LIBCOM"] == com_a_filo)]
                df_cb = df_filo[(df_filo["metropole"] == metro_comp_filo) & (df_filo["LIBCOM"] == com_b_filo)]

                st.markdown("---")

                # KPI côte à côte
                kpi_ind_list = ["DEC_MED21", "DEC_TP6021", "DEC_GI21", "DEC_RD21", "DEC_PIMP21"]
                kpi_ind_dispo = [c for c in kpi_ind_list if c in df_filo.columns]
                ka_cols = st.columns(len(kpi_ind_dispo))
                for i, col in enumerate(kpi_ind_dispo):
                    val_a = df_ca[col].median()
                    val_b = df_cb[col].median()
                    delta = val_a - val_b if pd.notna(val_a) and pd.notna(val_b) else None
                    with ka_cols[i]:
                        st.metric(
                            label=FILO_LABELS.get(col, col),
                            value=f"{val_a:.1f}" if pd.notna(val_a) else "N/D",
                            delta=f"{delta:+.1f} vs {com_b_filo}" if delta is not None else None,
                        )

                st.markdown("---")
                c1, c2 = st.columns(2)

                with c1:
                    # Radar multi-indicateurs
                    st.markdown("##### 🕸️ Profil comparatif (radar)")
                    radar_ind = ["DEC_MED21", "DEC_TP6021", "DEC_GI21", "DEC_RD21",
                                 "DEC_PIMP21", "DEC_PACT21", "DEC_PPEN21"]
                    radar_avail = [c for c in radar_ind if c in df_filo.columns]
                    if len(radar_avail) >= 3:
                        def norm_series(series):
                            mn, mx = series.min(), series.max()
                            return ((series - mn) / (mx - mn) * 100) if mx > mn else series * 0 + 50
                        df_all_metro = df_filo[df_filo["metropole"] == metro_comp_filo]
                        fig_rad = go.Figure()
                        for comm, color_r in [(com_a_filo, "#2D6A4F"), (com_b_filo, "#D4A017")]:
                            df_c = df_filo[(df_filo["metropole"] == metro_comp_filo) & (df_filo["LIBCOM"] == comm)]
                            vals_raw = [df_c[c].median() for c in radar_avail]
                            # Normaliser sur la distribution métropole
                            vals_norm = []
                            for c, v in zip(radar_avail, vals_raw):
                                col_data = df_all_metro[c].dropna()
                                if col_data.empty or col_data.max() == col_data.min():
                                    vals_norm.append(50)
                                else:
                                    vals_norm.append(float((v - col_data.min()) / (col_data.max() - col_data.min()) * 100))
                            cats = [FILO_LABELS.get(c, c).split(" (")[0][:20] for c in radar_avail]
                            fig_rad.add_trace(go.Scatterpolar(
                                r=vals_norm + [vals_norm[0]],
                                theta=cats + [cats[0]],
                                fill="toself", name=comm, line_color=color_r,
                            ))
                        fig_rad.update_layout(
                            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                            height=400, title="Profil normalisé (0–100 dans la métropole)",
                            font_family="Sora", paper_bgcolor="rgba(0,0,0,0)",
                            legend=dict(orientation="h", y=-0.1),
                        )
                        st.plotly_chart(fig_rad, use_container_width=True)

                with c2:
                    # Distribution des IRIS des deux communes
                    st.markdown("##### 📦 Distribution des IRIS par indicateur")
                    sel_ind_comp = st.selectbox(
                        "Indicateur",
                        filo_cols,
                        format_func=lambda c: FILO_LABELS.get(c, c),
                        index=filo_cols.index("DEC_MED21") if "DEC_MED21" in filo_cols else 0,
                        key="filo_comp_ind",
                    )
                    df_dist = pd.concat([
                        df_ca[["LIBIRIS", sel_ind_comp]].assign(Commune=com_a_filo),
                        df_cb[["LIBIRIS", sel_ind_comp]].assign(Commune=com_b_filo),
                    ]).dropna(subset=[sel_ind_comp])
                    if not df_dist.empty:
                        fig_dist = px.bar(
                            df_dist.sort_values(sel_ind_comp),
                            x=sel_ind_comp, y="LIBIRIS",
                            color="Commune",
                            orientation="h",
                            barmode="group",
                            color_discrete_map={com_a_filo: "#2D6A4F", com_b_filo: "#D4A017"},
                            labels={"LIBIRIS": "", sel_ind_comp: FILO_LABELS.get(sel_ind_comp, sel_ind_comp)},
                            title=f"IRIS — {FILO_LABELS.get(sel_ind_comp, sel_ind_comp)}",
                            height=420,
                        )
                        fig_dist.update_layout(yaxis={"categoryorder": "total ascending"})
                        st.plotly_chart(style(fig_dist, 40), use_container_width=True)

                st.markdown("---")
                with st.expander("📄 Tableau comparatif complet"):
                    rows_comp = []
                    for col in filo_cols:
                        rows_comp.append({
                            "Indicateur": FILO_LABELS.get(col, col),
                            com_a_filo: round(df_ca[col].median(), 2) if not df_ca[col].dropna().empty else "N/D",
                            com_b_filo: round(df_cb[col].median(), 2) if not df_cb[col].dropna().empty else "N/D",
                        })
                    st.dataframe(pd.DataFrame(rows_comp).set_index("Indicateur"), use_container_width=True)

# ──────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#9AB8A7;font-size:0.72rem'>"
    "Données INSEE · Recensements de la Population 2011, 2016, 2022 · "
    "Mobilités résidentielles, professionnelles et scolaires 2019–2022</p>",
    unsafe_allow_html=True,
)
