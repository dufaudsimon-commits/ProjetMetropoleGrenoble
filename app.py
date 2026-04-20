# =============================================================================
# APPLICATION STREAMLIT - DÉMOGRAPHIE DES MÉTROPOLES FRANÇAISES
# Grenoble · Rennes · Saint-Étienne · Rouen · Montpellier
# Sources : INSEE - Recensements de la Population 2011, 2016, 2022
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

# Palette spécifique appliquée aux 5 métropoles 
COULEURS = {
    "Montpellier": "#77818C",
    "Saint-Étienne": "#A2A6AE",
    "Grenoble": "#FF584D",
    "Rennes": "#C5C9CE",
    "Rouen": "#E8E8EB",
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

def filter_bar(label="Filtres"):
    """Ouvre un conteneur visuellement encadré pour les filtres en haut de page."""
    st.markdown(f'<div class="filter-bar-title">{label}</div>', unsafe_allow_html=True)

def filter_row_label(text):
    """Label gauche harmonise avec l'onglet Mobilites."""
    st.markdown(
        f"<div style='padding-top:8px; font-weight:600; font-size:14px; color:#1C3A27;'>{text}</div>",
        unsafe_allow_html=True,
    )

def kpi_card_left(title, value, subtitle="", accent="#1a7a4a"):
    """Carte KPI avec bordure gauche, style Mobilites."""
    st.markdown(f"""
    <div style='
        display: flex;
        flex-direction: row;
        align-items: stretch;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        background: #fff;
        min-height: 80px;
        border-left: 6px solid {accent};
    '>
        <div style='padding: 10px 16px; display: flex; flex-direction: column; justify-content: center;'>
            <div style='font-size:11px; font-weight:700; letter-spacing:0.08em; color:#666; text-transform:uppercase;'>{title}</div>
            <div style='font-size:24px; font-weight:bold; color:#111;'>{value}</div>
            <div style='color:#1a7a4a; font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.05em;'>{subtitle}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# 5. EN-TÊTE
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(
    "<h1 style='color:#1C3A27;font-size:2rem;margin-bottom:2px'>Observatoire de la métropole de Grenoble : Profils internes et rayonnement métropolitain</h1>"
    "<p style='color:#5A8A6A;margin-bottom:20px'>Analyses intercommunales et intermétropoles</p>",
    unsafe_allow_html=True,
)


# ──────────────────────────────────────────────────────────────────────────────
# 6. PAGE D'ACCUEIL (Version avec Objectif agrandi)
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

    /* Grille pour les deux thématiques du bas */
    .cards-grid-bottom { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 16px; }
    
    .info-card {
        background: white; border: 1px solid #C8E6D4; border-radius: 12px;
        padding: 22px; border-left: 5px solid #2D6A4F;
    }
    
    /* STYLE SPÉCIFIQUE OBJECTIF (BLEU ET GRANDE POLICE) */
    .info-card.blue { 
        border-left: 6px solid #111184; 
        border-color: #111184;
        box-shadow: 0 4px 12px rgba(42, 92, 154, 0.08); /* Petit relief bleu */
    }
    .info-card.blue .info-card-title { color: #111184; font-size: 14px; }
    .info-card.blue .info-card-body { 
        font-size: 16px; /* Taille augmentée */
        font-weight: 400;
        line-height: 1.6;
        color: #1a1a1a;
    }

    .info-card.orange { border-left-color: #C45B2A; }
    
    .info-card-title {
        font-size: 12px; font-weight: 700; color: #2D6A4F; text-transform: uppercase;
        letter-spacing: 0.08em; margin-bottom: 12px;
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
    
    .cta-wrapper { margin-top: 20px; }
    div[data-testid="stButton"] > button[kind="primary"] {
        background: #2D6A4F !important; color: white !important;
        border: none !important; border-radius: 12px !important;
        padding: 14px 28px !important; font-size: 15px !important;
        font-weight: 700 !important; width: 100% !important;
        transition: background 0.2s !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Hero banner ────────────────────────────────────────────────────────
    img_path = Path("grenoble-1600x900.jpg")
    img_col_html = ""
    if img_path.exists():
        import base64
        with open(img_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()
        img_col_html = f'<div class="hero-img-col"><img src="data:image/jpeg;base64,{img_b64}"/><div class="hero-img-overlay"></div></div>'

    st.markdown(f"""
    <div class="hero-accueil">
        <div class="hero-inner">
            <div class="hero-text-col">
                <div class="hero-badge">Outil d'aide à la décision</div>
                <div class="hero-title">Différentes dynamiques<br>et enjeux territoriaux</div>
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
        <div class="stat-box"><div class="stat-num">49</div><div class="stat-lbl">Communes</div></div>
        <div class="stat-box"><div class="stat-num">2</div><div class="stat-lbl">Thématiques</div></div>
    </div>
    """, unsafe_allow_html=True)

    # ── Carte Objectif (Pleine largeur + Bleue + Police agrandie) ──────────
    st.markdown("""
    <div class="info-card blue">
        <div class="info-card-title"> Objectif</div>
        <div class="info-card-body">
            Analyser les données de démographie et de solidarité & citoyenneté afin de produire une analyse complète pour chaque commune de la métropole de Grenoble. 
            Cette étude vise à permettre la comparaison des communes entre elles, ainsi qu’à situer la métropole de Grenoble par rapport à celles de Rouen, Saint-Étienne, Rennes et Montpellier. 
            Elle est également destinée à accompagner les nouveaux élus dans la compréhension des dynamiques territoriales.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Cartes thématiques (Deux colonnes en dessous) ──────────────────────
    st.markdown("""
    <div class="cards-grid-bottom">
        <div class="info-card">
            <div class="info-card-title"> Démographie</div>
            <div class="info-card-body">
                Analyse de la population, de la structure par âge, des ménages, des mobilités résidentielles, professionnelles et scolaires.
            </div>
            <div class="tag-row">
                <span class="tag-green">Population</span>
                <span class="tag-green">Âges</span>
                <span class="tag-green">Actifs</span>
                <span class="tag-green">Mobilités</span>
                <span class="tag-green">Population active 25-54 ans</span>
            </div>
        </div>
        <div class="info-card orange">
            <div class="info-card-title"> Solidarité & citoyenneté</div>
            <div class="info-card-body">
                Étude des allocations CAF, des indicateurs éducatifs et de santé, ainsi que de la participation citoyenne et du taux de pauvreté.
            </div>
            <div class="tag-row">
                <span class="tag-orange">Solidarité</span>
                <span class="tag-orange">Education</span>
                <span class="tag-orange">Santé</span>
                <span class="tag-orange">Participation</span>
                <span class="tag-orange">Revenus et pauvreté</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Bouton CTA ─────────────────────────────────────────────────────────
    st.markdown('<div class="cta-wrapper">', unsafe_allow_html=True)
    if st.button("→   Accéder à l'application", type="primary"):
        st.session_state.page = "app"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
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
            S. Dufaud  • J. Ben-Hadj-Salem <br>
            H. Unaldi • M. Desjobert--Mutelet
        </div>
    </div>
    """, unsafe_allow_html=True)
# ──────────────────────────────────────────────────────────────────────────────
# 8. PAGES
# ──────────────────────────────────────────────────────────────────────────────
# ==============================================================================
# PAGE DESCRIPTION - NOUVEAU DESIGN
# ==============================================================================

if vue == "Description":
    # 1. CSS Global pour la page
    st.markdown("""
        <style>
        .main-intro {
            background: white;
            padding: 25px;
            border-radius: 15px;
            border-left: 8px solid #2D6A4F;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            margin-bottom: 30px;
        }
        /* Style du Tableau */
        .modern-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 1em;
            font-family: 'Sora', sans-serif;
            border-radius: 12px 12px 0 0;
            overflow: hidden;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
        }
        .modern-table thead tr {
            background-color: #2D6A4F;
            color: #ffffff;
            text-align: left;
            font-weight: bold;
        }
        .modern-table th, .modern-table td {
            padding: 12px 15px;
        }
        .modern-table tbody tr {
            border-bottom: 1px solid #dddddd;
            background-color: white;
        }
        .modern-table tbody tr:nth-of-type(even) {
            background-color: #f3f3f3;
        }
        .modern-table tbody tr:last-of-type {
            border-bottom: 2px solid #2D6A4F;
        }
        .badge-count {
            background-color: #e7f3ef;
            color: #2D6A4F;
            padding: 4px 8px;
            border-radius: 6px;
            font-weight: bold;
        }
        /* Style des Cartes Thématiques */
        .feature-card {
            background: white;
            padding: 20px;
            border-radius: 15px;
            border: 1px solid #E0E0E0;
            height: 100%;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        .theme-badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 0.7rem;
            font-weight: bold;
            text-transform: uppercase;
            margin-bottom: 10px;
        }
        .badge-demo { background: #E6FFFA; color: #2D6A4F; }
        .badge-solid { background: #FFF5F5; color: #C45B2A; }
        </style>
    """, unsafe_allow_html=True)

    # 1. Introduction
    st.markdown("""
        <div class="main-intro">
            <p style="font-size: 1.1rem; color: #1C3A27; margin: 0;">
                Cette application présente des analyses comparatives sur <b>5 métropoles françaises et 49 communes de la métropole de Grenoble</b> à partir des données de l'INSEE, la CAF, Data.gouv et OSM France. 
                Chaque page dispose de ses propres filtres en haut de page, adaptés aux données présentées. 
                Selon les onglets, il est possible de filtrer par métropole, par commune, par année ou par thématique.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # 2. Tableau du Périmètre (Généré proprement)
    st.markdown('<p style="font-size:1.5rem; font-weight:700; color:#1C3A27; margin-bottom:10px;">Périmètre d\'analyse</p>', unsafe_allow_html=True)
    
    table_html = """
    <table class="modern-table">
        <thead>
            <tr>
                <th>Métropole</th>
                <th>Nombre de communes</th>
                <th>Département</th>
            </tr>
        </thead>
        <tbody>
            <tr><td>Grenoble-Alpes Métropole</td><td><span class="badge-count">49</span></td><td>Isère (38)</td></tr>
            <tr><td>Rennes Métropole</td><td><span class="badge-count">43</span></td><td>Ille-et-Vilaine (35)</td></tr>
            <tr><td>Rouen Normandie Métropole</td><td><span class="badge-count">71</span></td><td>Seine-Maritime (76)</td></tr>
            <tr><td>Saint-Étienne Métropole</td><td><span class="badge-count">53</span></td><td>Loire (42)</td></tr>
            <tr><td>Montpellier Méditerranée Métropole</td><td><span class="badge-count">31</span></td><td>Hérault (34)</td></tr>
        </tbody>
    </table>
    """
    st.markdown(table_html, unsafe_allow_html=True)

    # 3. Thématique Démographie
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p style="font-size:1.5rem; font-weight:700; color:#2D6A4F; border-bottom: 2px solid #2D6A4F;"> Thématique 1 : Démographie</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""<div class="feature-card"><div class="theme-badge badge-demo">Villes</div><div class="card-title"><b> Population globale</b></div>
        <div class="card-body" style="font-size:0.9rem; color:#555;">Découvrez ici le nombre total d'habitants. Cela permet de voir la densité de population et de comparer les métropoles et communes entre elles.</div></div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""<div class="feature-card"><div class="theme-badge badge-demo">Foyers</div><div class="card-title"><b> Ménages</b></div>
        <div class="card-body" style="font-size:0.9rem; color:#555;">On regarde ici comment vivent les gens chez eux. Cela montre s'il y a beaucoup de familles ou de personnes seules, et combien il y a d'habitants par logement.</div></div>""", unsafe_allow_html=True)

    with col2:
        st.markdown("""<div class="feature-card"><div class="theme-badge badge-demo">Âges</div><div class="card-title"><b> Structure par âge</b></div>
        <div class="card-body" style="font-size:0.9rem; color:#555;">Est-ce que la ville est plutôt jeune ou vieille ? Cette partie montre le nombre d'enfants, de travailleurs et de retraités pour chaque endroit étudié.</div></div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""<div class="feature-card"><div class="theme-badge badge-demo">Travail</div><div class="card-title"><b> Population active</b></div>
        <div class="card-body" style="font-size:0.9rem; color:#555;">Ici, on s'intéresse aux personnes qui ont l'âge de travailler (25 à 54 ans). On analyse leurs métiers et leur niveau d'études ou leurs diplômes.</div></div>""", unsafe_allow_html=True)

    with col3:
        st.markdown("""<div class="feature-card"><div class="theme-badge badge-demo">Trajets</div><div class="card-title"><b> Mobilité</b></div>
        <div class="card-body" style="font-size:0.9rem; color:#555;"><b>Toutes les mobilités :</b> On étudie les déplacements des habitants. Cela comprend les nouveaux arrivants, les trajets domicile-travail et les déplacements pour l'école.</div></div>""", unsafe_allow_html=True)

    # 4. Thématique Solidarité
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p style="font-size:1.5rem; font-weight:700; color:#C45B2A; border-bottom: 2px solid #C45B2A;"> Thématique 2 : Solidarité & Citoyenneté</p>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""<div class="feature-card"><div class="theme-badge badge-solid">Aide</div><div class="card-title"><b> Solidarité</b></div>
        <div class="card-body" style="font-size:0.9rem; color:#555;">Retrouvez ici les aides versées aux familles par la CAF. Cela permet de voir les zones où les gens ont le plus besoin de soutien financier.</div></div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""<div class="feature-card"><div class="theme-badge badge-solid">Vote</div><div class="card-title"><b> Participation</b></div>
        <div class="card-body" style="font-size:0.9rem; color:#555;">On regarde ici si les habitants votent beaucoup aux élections locales. C'est un bon moyen de voir si les gens s'intéressent à la vie de leur commune.</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""<div class="feature-card"><div class="theme-badge badge-solid">École</div><div class="card-title"><b> Éducation</b></div>
        <div class="card-body" style="font-size:0.9rem; color:#555;">On regarde combien de jeunes étudient et quels diplômes ils obtiennent dans chaque territoire et suivre leurs évolutions.</div></div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""<div class="feature-card"><div class="theme-badge badge-solid">Argent</div><div class="card-title"><b> Pauvreté</b></div>
        <div class="card-body" style="font-size:0.9rem; color:#555;">Découvrez les revenus médians des habitants. On regarde si les gens gagnent bien leur vie ou s'ils sont dans une situation de pauvreté monétaire.</div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""<div class="feature-card"><div class="theme-badge badge-solid">Soin</div><div class="card-title"><b> Santé</b></div>
        <div class="card-body" style="font-size:0.9rem; color:#555;">Cette page liste les établissements de santés disponibles. Cela sert à voir si l'on peut se soigner facilement près de chez soi dans chaque quartier.</div></div>""", unsafe_allow_html=True)

    st.stop()   

if vue == "Démographie":
    tab1, tab2, tab3, tab4, tab6 = st.tabs([
        "🏙️  Population globale",
        "👥  Structure par âge",
        "🚌  Mobilités",
        "🏠  Ménages",
        "📊  Population active 25-54 ans",
    ])

# ==============================================================================
# ONGLET 1 - POPULATION GLOBALE
# ==============================================================================
if vue == "Démographie":
    with tab1:

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
            filter_bar("Filtres - Population globale")
            col_geo_label, col_geo_options = st.columns([1, 3])
            with col_geo_label:
                filter_row_label("Niveau géographique")
            with col_geo_options:
                mode_pop = st.radio(
                    "",
                    ["Comparaison Métropoles", "Comparaison communes métropole de Grenoble"],
                    key="pop_mode", horizontal=True,
                    help="Choisissez une comparaison entre métropoles ou un détail des communes de Grenoble.",
                )
            if mode_pop == "Comparaison Métropoles":
                sel = st.multiselect(
                    "Métropoles à comparer", TOUTES, default=TOUTES, key="sel_t1",
                    help="Sélection des métropoles affichées dans les KPI et graphiques.",
                )
            else:
                sel_communes_pop = st.multiselect(
                    "Commune de la métropole de Grenoble", sorted(COMMUNES["Grenoble"]),
                    default=sorted(COMMUNES["Grenoble"])[:2], key="pop_communes",
                    help="Sélection des communes utilisées pour les comparaisons d'indicateurs 2022.",
                )
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("---")

        # ════════════════════════════════════════════════════════════════════
        # VUE DÉTAIL COMMUNAL (Grenoble)
        # ════════════════════════════════════════════════════════════════════
        if mode_pop == "Comparaison communes métropole de Grenoble":
            if not sel_communes_pop:
                st.warning("Sélectionnez au moins une commune.")
                st.stop()

            COLORS_COMM = ["#081C15", "#1B4332", "#2D6A4F", "#40916C", "#52B788",
                           "#74C69D", "#95D5B2", "#B7E4C7", "#D8F3DC"]


            # ── KPIs ─────────────────────────────────────────────────────────
            st.markdown(
                "##### Population en 2022", 
                help="La variation annuelle moyenne est calculée sur la période 2016–2022 à partir des recensements INSEE. Elle combine le solde naturel et migratoire."
            )
            
            kpi_cols = st.columns(len(sel_communes_pop))
            for i, comm in enumerate(sel_communes_pop):
                pop22  = commune_val(comm, "population_2022")
                tx_var = commune_val(comm, "tx_var_population_2016_2022")
                
                delta_str = f"{tx_var:+.2f}%/an" if not np.isnan(tx_var) else "N/D"
                color_delta = "#2D6A4F" if not np.isnan(tx_var) and tx_var >= 0 else ("#C45B2A" if not np.isnan(tx_var) else "#888")

                html_card = f"""
                <div style='display: flex; flex-direction: column; justify-content: center; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 6px rgba(0,0,0,0.1); background: #fff; min-height: 80px; border-left: 6px solid #2D6A4F; padding: 12px 16px; margin-bottom: 10px;'>
                    <div style='font-size:11px; font-weight:700; letter-spacing:0.08em; color:#666; text-transform:uppercase;'> {comm}</div>
                    <div style='font-size:24px; font-weight:bold; color:#1C3A27; margin: 4px 0;'>{fmt(pop22)}</div>
                    <div style='font-size:12px; font-weight:700;'>
                        <span style='color:{color_delta};'>Var: {delta_str}</span>
                    </div>
                </div>
                """
                with kpi_cols[i]:
                    st.markdown(html_card, unsafe_allow_html=True)

            st.markdown("---")

            # ── Graphique 1 : Population 2022 ────────────────────────────────
            r1c1, r1c2 = st.columns(2)
            with r1c1:
                st.subheader(
                    "Population totale 2022 (habitants)",
                    help="Comparaison directe du volume de population de chaque métropole au RP 2022.",
                )
                data_comm = [
                    {"Commune": c, "Population": commune_val(c, "population_2022"),
                     "Couleur": COLORS_COMM[i % len(COLORS_COMM)]}
                    for i, c in enumerate(sel_communes_pop)
                ]
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
                    fig_pop_c.update_layout(
                        showlegend=False, xaxis_title="Commune", yaxis_title="Habitants",
                        yaxis=dict(tickformat=",d"), height=370,
                    )
                    st.plotly_chart(style(fig_pop_c), use_container_width=True)

            with r1c2:
                st.subheader(
                    "Densité (hab/km²) vs Superficie (km²)",
                    help="Une bulle grande et haute signifie un territoire à la fois peuplé et dense. La taille de la bulle est proportionnelle à la population.",
                )
                data_dens_c = []
                for i, c in enumerate(sel_communes_pop):
                    d = commune_val(c, "densite_2022")
                    s = commune_val(c, "superficie_km2_2022")
                    p = commune_val(c, "population_2022")
                    if not any(np.isnan(v) for v in [d, s, p]):
                        data_dens_c.append({
                            "Commune": c, "Densité (hab/km²)": d,
                            "Superficie (km²)": s, "Population": p,
                            "Couleur": COLORS_COMM[i % len(COLORS_COMM)],
                        })
                df_dens_c = pd.DataFrame(data_dens_c)
                if not df_dens_c.empty:
                    fig_dens_c = px.scatter(
                        df_dens_c, x="Superficie (km²)", y="Densité (hab/km²)",
                        size="Population", color="Commune", text="Commune",
                        color_discrete_sequence=COLORS_COMM, size_max=55, height=370,
                    )
                    fig_dens_c.update_traces(
                        textposition="top center", textfont_size=10,
                        hovertemplate="<b>Commune : %{text}</b><br>Superficie : %{x:.2f} km²<br>Densité : %{y:.2f} hab/km²<br>Population : %{marker.size:,.0f}<extra></extra>",
                    )
                    fig_dens_c.update_layout(
                        showlegend=False, xaxis_title="Superficie (km²)", yaxis_title="Densité (hab/km²)",
                    )
                    st.plotly_chart(style(fig_dens_c), use_container_width=True)

            with st.expander("💡 Comment interpréter ces deux graphiques ?"):
                st.write("Le graphique en barres montre les volumes absolus de population ; le nuage de points complète la lecture avec la pression spatiale (densité) rapportée à la superficie du territoire.")

            st.markdown("---")

            # ── Graphiques 2 : Soldes & Radar (Réintégrés) ───────────────────
            r2c1, r2c2 = st.columns(2)
            with r2c1:
                st.subheader(
                    "Soldes naturel et migratoire (%/an, 2016–2022)",
                    help="Le solde naturel = (naissances – décès) / population. Le solde migratoire = (arrivées – départs) / population. La variation totale est la somme des deux.",
                )
                rows_comp_c = []
                for comm in sel_communes_pop:
                    sn  = commune_val(comm, "tx_solde_naturel")
                    sm  = commune_val(comm, "tx_solde_migratoire")
                    tot = commune_val(comm, "tx_var_population_2016_2022")
                    if not all(np.isnan(v) for v in [sn, sm, tot]):
                        rows_comp_c.append({
                            "Commune": comm, "Solde naturel": sn,
                            "Solde migratoire": sm, "Variation totale": tot,
                        })
                if rows_comp_c:
                    df_comp_c = pd.DataFrame(rows_comp_c).melt(
                        id_vars="Commune", var_name="Composante", value_name="Taux (%/an)"
                    ).dropna()
                    COLOR_COMP = {
                        "Solde naturel": "#FFB3AE",
                        "Solde migratoire": "#FF584D",
                        "Variation totale": "#8B2E2E",
                    }
                    fig_comp_c = px.bar(
                        df_comp_c, x="Commune", y="Taux (%/an)", color="Composante",
                        barmode="group", color_discrete_map=COLOR_COMP, height=360,
                    )
                    fig_comp_c.update_traces(
                        hovertemplate="<b>Commune : %{x}</b><br>%{fullData.name} : %{y:.2f} %/an<extra></extra>"
                    )
                    fig_comp_c.add_hline(y=0, line_dash="dot", line_color="#AAAAAA")
                    fig_comp_c.update_layout(
                        xaxis_title="Commune", yaxis_title="Taux (%/an)",
                        legend=dict(orientation="h", y=1.12),
                        xaxis_tickangle=-20,
                    )
                    st.plotly_chart(style(fig_comp_c), use_container_width=True)
                else:
                    st.info("Données de soldes non disponibles pour ces communes.")

            with r2c2:
                st.subheader(
                    "Naissances & Décès (pour 1 000 habitants)",
                    help="Compare le taux de natalité et de mortalité pour 1 000 habitants. Le losange indique l'accroissement naturel (naissances – décès). Un accroissement positif signifie que les naissances dépassent les décès.",
                )
                rows_vit_c = []
                for comm in sel_communes_pop:
                    nais = commune_val(comm, "naissances_2024")
                    decs = commune_val(comm, "deces_2024")
                    pop  = commune_val(comm, "population_2022")
                    if not any(np.isnan(v) for v in [nais, decs, pop]) and pop > 0:
                        rows_vit_c.append({
                            "Commune": comm,
                            "Naissances/1 000 hab": round(nais / pop * 1000, 2),
                            "Décès/1 000 hab": round(decs / pop * 1000, 2),
                            "Accroissement naturel": round((nais - decs) / pop * 1000, 2),
                        })
                if rows_vit_c:
                    df_vit_c = pd.DataFrame(rows_vit_c)
                    fig_vit_c = go.Figure()
                    for idx_c, row_v in df_vit_c.iterrows():
                        c_h = COLORS_COMM[idx_c % len(COLORS_COMM)]
                        fig_vit_c.add_trace(go.Bar(
                            x=[row_v["Commune"]], y=[row_v["Naissances/1 000 hab"]],
                            name=f"Naissances — {row_v['Commune']}",
                            marker_color=c_h, showlegend=True,
                            hovertemplate=f"<b>Commune : {row_v['Commune']}</b><br>Naissances : {row_v['Naissances/1 000 hab']:.2f} / 1 000 hab<extra></extra>",
                        ))
                        fig_vit_c.add_trace(go.Bar(
                            x=[row_v["Commune"]], y=[row_v["Décès/1 000 hab"]],
                            name=f"Décès — {row_v['Commune']}",
                            marker_color=c_h, marker_opacity=0.4,
                            marker_line_color=c_h, marker_line_width=1.5,
                            showlegend=True,
                            hovertemplate=f"<b>Commune : {row_v['Commune']}</b><br>Décès : {row_v['Décès/1 000 hab']:.2f} / 1 000 hab<extra></extra>",
                        ))
                        fig_vit_c.add_trace(go.Scatter(
                            x=[row_v["Commune"]], y=[row_v["Accroissement naturel"]],
                            mode="markers+text",
                            name=f"Accroissement — {row_v['Commune']}",
                            marker=dict(symbol="diamond", size=12, color="#8B2E2E",
                                        line=dict(color="white", width=1.5)),
                            text=[f"{row_v['Accroissement naturel']:+.2f}"],
                            textposition="top center", textfont=dict(size=10, color="#8B2E2E"),
                            showlegend=False,
                            hovertemplate=f"<b>Commune : {row_v['Commune']}</b><br>Accroissement naturel : {row_v['Accroissement naturel']:.2f} / 1 000 hab<extra></extra>",
                        ))
                    fig_vit_c.update_layout(
                        barmode="group",
                        legend=dict(orientation="h", y=1.12, font_size=9),
                        yaxis_title="Pour 1 000 habitants",
                        height=360,
                    )
                    st.plotly_chart(style(fig_vit_c), use_container_width=True)
                else:
                    st.info("Données de naissances/décès non disponibles pour ces communes.")

            with st.expander("💡 Comment interpréter ces deux graphiques ?"):
                st.write("Des soldes positifs traduisent une dynamique démographique favorable. Le radar permet de visualiser simultanément trois composantes et d'identifier les métropoles dont la croissance est portée par les naissances plutôt que par l'attractivité migratoire.")

            st.markdown("---")
            st.markdown("#### Tableau récapitulatif - indicateurs clés")
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

        # ════════════════════════════════════════════════════════════════════
        # VUE COMPARAISON MÉTROPOLES
        # ════════════════════════════════════════════════════════════════════
        else:
            if not sel:
                st.warning("Sélectionnez au moins une métropole.")
                st.stop()

            # ── KPIs ─────────────────────────────────────────────────────────
            st.markdown(
                "##### Population en 2022",
                help="La variation annuelle moyenne est calculée sur la période 2016–2022 à partir des recensements INSEE. Elle combine le solde naturel et migratoire."
            )

            kpi_cols = st.columns(len(sel))
            for i, m in enumerate(sel):
                pop22  = epci_val(m, "population_2022")
                tx_var = epci_val(m, "tx_var_population_2016_2022")
                
                delta_str = f"{tx_var:+.2f}%/an" if not np.isnan(tx_var) else "N/D"
                color_delta = "#2D6A4F" if not np.isnan(tx_var) and tx_var >= 0 else ("#C45B2A" if not np.isnan(tx_var) else "#888")


                kpi_color = COULEURS.get(m, "#888888")
                html_card = f"""
                <div style='display: flex; flex-direction: column; justify-content: center; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 6px rgba(0,0,0,0.1); background: #fff; min-height: 80px; border-left: 6px solid {kpi_color}; padding: 12px 16px; margin-bottom: 10px;'>
                    <div style='font-size:11px; font-weight:700; letter-spacing:0.08em; color:#666; text-transform:uppercase;'>{m}</div>
                    <div style='font-size:24px; font-weight:bold; color:#111; margin: 4px 0;'>{fmt(pop22)}</div>
                    <div style='font-size:12px; font-weight:700;'>
                        <span style='color:{color_delta};'>Var: {delta_str}</span>
                    </div>
                </div>
                """
                with kpi_cols[i]:
                    st.markdown(html_card, unsafe_allow_html=True)

            st.markdown("---")

            # ── Population & densité ─────────────────────────────────────────
            r1c1, r1c2 = st.columns(2)
            with r1c1:
                st.subheader(
                    "Population totale 2022 (habitants)",
                    help="Comparaison directe du volume de population de chaque métropole au RP 2022.",
                )
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
                    fig_pop.update_layout(
                        showlegend=False, xaxis_title="Métropole", yaxis_title="Habitants",
                        yaxis=dict(tickformat=",d"), height=370,
                    )
                    st.plotly_chart(style(fig_pop), use_container_width=True)

            with r1c2:
                st.subheader(
                    "Densité (hab/km²) vs Superficie (km²)",
                    help="Une bulle grande et haute signifie un territoire à la fois peuplé et dense. La taille de la bulle est proportionnelle à la population.",
                )
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
                    fig_dens = px.scatter(
                        df_dens, x="Superficie (km²)", y="Densité (hab/km²)",
                        size="Population", color="Métropole",
                        color_discrete_map=COULEURS, text="Métropole",
                        size_max=55, height=370,
                    )
                    fig_dens.update_traces(
                        textposition="top center", textfont_size=11,
                        hovertemplate="<b>Métropole : %{text}</b><br>Superficie : %{x:.2f} km²<br>Densité : %{y:.2f} hab/km²<br>Population : %{marker.size:,.0f}<extra></extra>",
                    )
                    fig_dens.update_layout(
                        showlegend=False, xaxis_title="Superficie (km²)", yaxis_title="Densité (hab/km²)",
                    )
                    st.plotly_chart(style(fig_dens), use_container_width=True)

            with st.expander("💡 Comment interpréter ces deux graphiques ?"):
                st.write("Le graphique en barres montre les volumes absolus de population ; le nuage de points complète la lecture avec la pression spatiale (densité) rapportée à la superficie du territoire.")

            st.markdown("---")

            # ── Soldes & radar ───────────────────────────────────────────────
            r2c1, r2c2 = st.columns(2)
            with r2c1:
                st.subheader(
                    "Soldes naturel et migratoire (%/an, 2016–2022)",
                    help="Le solde naturel = (naissances – décès) / population. Le solde migratoire = (arrivées – départs) / population. La variation totale est la somme des deux.",
                )
                rows_comp = []
                for m in sel:
                    sn  = epci_val(m, "tx_solde_naturel")
                    sm  = epci_val(m, "tx_solde_migratoire")
                    tot = epci_val(m, "tx_var_population_2016_2022")
                    if not all(np.isnan(v) for v in [sn, sm, tot]):
                        rows_comp.append({
                            "Métropole": m, "Solde naturel": sn,
                            "Solde migratoire": sm, "Variation totale": tot,
                        })
                if rows_comp:
                    df_comp = pd.DataFrame(rows_comp).melt(
                        id_vars="Métropole", var_name="Composante", value_name="Taux (%/an)"
                    ).dropna()
                    COLOR_COMP = {
                        "Solde naturel":    "#C8CACF",
                        "Solde migratoire": "#7A7E87",
                        "Variation totale": "#3A3D44",
                    }
                    fig_comp = px.bar(
                        df_comp, x="Métropole", y="Taux (%/an)", color="Composante",
                        barmode="group", color_discrete_map=COLOR_COMP, height=360,
                    )
                    for trace in fig_comp.data:
                        xs = list(trace.x) if trace.x is not None else []
                        trace.marker.line.color = ["#FF584D" if str(x) == "Grenoble" else "rgba(0,0,0,0)" for x in xs]
                        trace.marker.line.width = [2 if str(x) == "Grenoble" else 0 for x in xs]
                        trace.hovertemplate = "<b>Métropole : %{x}</b><br>" + trace.name + " : %{y:.2f} %/an<extra></extra>"
                    fig_comp.add_hline(y=0, line_dash="dot", line_color="#AAAAAA")
                    fig_comp.update_layout(
                        xaxis_title="Métropole", yaxis_title="Taux (%/an)",
                        legend=dict(orientation="h", y=1.12),
                    )
                    st.plotly_chart(style(fig_comp), use_container_width=True)

            with r2c2:
                st.subheader(
                    "Naissances & Décès 2024 (pour 1 000 habitants)",
                    help="Barres foncées = naissances, barres claires = décès. Le losange rouge = accroissement naturel. Bordures rouges = Grenoble.",
                )
                rows_vit = []
                for m in sel:
                    nais = epci_val(m, "naissances_2024")
                    decs = epci_val(m, "deces_2024")
                    pop  = epci_val(m, "population_2022")
                    if not any(np.isnan(v) for v in [nais, decs, pop]):
                        rows_vit.append({
                            "Métropole": m,
                            "Naissances": round(nais / pop * 1000, 2),
                            "Décès":      round(decs / pop * 1000, 2),
                            "Accroissement": round((nais - decs) / pop * 1000, 2),
                        })
                df_vit = pd.DataFrame(rows_vit)
                if not df_vit.empty:
                    metros_vit = df_vit["Métropole"].tolist()
                    border_col  = ["#FF584D" if m == "Grenoble" else "rgba(0,0,0,0)" for m in metros_vit]
                    border_w    = [2 if m == "Grenoble" else 0 for m in metros_vit]
                    fig_vit = go.Figure()
                    fig_vit.add_trace(go.Bar(
                        x=metros_vit, y=df_vit["Naissances"], name="Naissances / 1 000 hab",
                        marker_color="#7A7E87", marker_line_color=border_col, marker_line_width=border_w,
                        hovertemplate="<b>Métropole : %{x}</b><br>Naissances : %{y:.2f} / 1 000 hab<extra></extra>",
                    ))
                    fig_vit.add_trace(go.Bar(
                        x=metros_vit, y=df_vit["Décès"], name="Décès / 1 000 hab",
                        marker_color="#C8CACF", marker_line_color=border_col, marker_line_width=border_w,
                        hovertemplate="<b>Métropole : %{x}</b><br>Décès : %{y:.2f} / 1 000 hab<extra></extra>",
                    ))
                    fig_vit.add_trace(go.Scatter(
                        x=metros_vit, y=df_vit["Accroissement"], mode="markers+text",
                        name="Accroissement naturel",
                        marker=dict(symbol="diamond", size=12, color="#FF584D", line=dict(color="white", width=1.5)),
                        text=[f"{v:+.2f}" for v in df_vit["Accroissement"]],
                        textposition="top center", textfont=dict(size=9, color="#8B2E2E"),
                        hovertemplate="<b>Métropole : %{x}</b><br>Accroissement naturel : %{y:.2f} / 1 000 hab<extra></extra>",
                    ))
                    fig_vit.update_layout(
                        barmode="group", legend=dict(orientation="h", y=1.12),
                        yaxis_title="Pour 1 000 habitants", height=360,
                    )
                    st.plotly_chart(style(fig_vit), use_container_width=True)

            with st.expander("💡 Comment interpréter ces deux graphiques ?"):
                st.write("Des soldes positifs traduisent une dynamique démographique favorable. Le graphique Naissances & Décès permet de comparer directement les taux vitaux de chaque métropole : les barres pleines représentent les naissances, les barres claires les décès, et le losange rouge l'accroissement naturel (différence).")

            st.markdown("---")
            st.markdown("#### Tableau récapitulatif - indicateurs clés")
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
            
# ==============================================================================
# ONGLET 2 - STRUCTURE PAR ÂGE
# ==============================================================================
if vue == "Démographie":
    with tab2:

        if df_pop is None:
            st.info("📂 Fichier `Population_tranche_age_clean.csv` introuvable.")
        else:
            annees_dispo = sorted(df_pop["annee"].dropna().unique().astype(int).tolist())
            ch_all = cols_h(df_pop)
            cf_all = cols_f(df_pop)

            # ── Constantes tranches ──────────────────────────────────────────
            TRANCHES_M25  = ["01","02","03","04","05"]
            TRANCHES_ACT  = ["06","07","08","09","10","11","12","13"]
            TRANCHES_SEN  = ["14","15","16","17","18","19","20"]
            TRANCHES_M20  = ["01","02","03","04"]

            def pop_tranches(df_src, tranches):
                total = 0
                for t in tranches:
                    for sx in ["s1", "s2"]:
                        col = f"ageq_rec{t}{sx}rpop2016"
                        if col in df_src.columns:
                            total += pd.to_numeric(df_src[col], errors="coerce").fillna(0).sum()
                return float(total)

            def pop_totale_df(df_src):
                age_cols = [c for c in df_src.columns if "ageq_rec" in c]
                return pd.to_numeric(df_src[age_cols].stack(), errors="coerce").sum()

            def build_pyramide(df_src, label_entity, color_h="#2D6A4F", color_f="#95D5B2"):
                labels = [LABEL_TRANCHE.get(f"{i:02d}", f"{i:02d}") for i in range(1, 21)]
                vals_h, vals_f = [], []
                for i in range(1, 21):
                    t = f"{i:02d}"
                    ch_col = f"ageq_rec{t}s1rpop2016"
                    cf_col = f"ageq_rec{t}s2rpop2016"
                    vals_h.append(-pd.to_numeric(df_src[ch_col], errors="coerce").fillna(0).sum() if ch_col in df_src.columns else 0)
                    vals_f.append(pd.to_numeric(df_src[cf_col], errors="coerce").fillna(0).sum() if cf_col in df_src.columns else 0)

                fig = go.Figure()
                fig.add_trace(go.Bar(y=labels, x=vals_h, name="Hommes", orientation="h", marker_color=color_h))
                fig.add_trace(go.Bar(y=labels, x=vals_f, name="Femmes", orientation="h", marker_color=color_f))
                fig.update_layout(
                    barmode="relative", bargap=0.06,
                    legend=dict(orientation="h", y=1.08),
                    yaxis_title="Tranche d'âge (ans)",
                    xaxis_title="Population",
                    xaxis=dict(tickformat="~s"),
                    title=dict(text=label_entity, font_size=13),
                    height=480,
                )
                return fig

            # ── Filtres ──────────────────────────────────────────────
            with st.container():
                filter_bar("Filtres - Structure par âge")

                fa1, fa2 = st.columns([1, 3])
                with fa1:
                    filter_row_label("Niveau géographique")

                with fa2:
                    mode_age = st.radio(
                        "",
                        ["Comparaison Métropoles", "Comparaison communes métropole de Grenoble"],
                        key="age_mode", horizontal=True,
                        help="Choisissez la vue de comparaison entre métropoles ou le détail communal Grenoble.",
                    )

                if mode_age == "Comparaison Métropoles":
                    sel_metros_age = st.multiselect(
                        "Métropoles", TOUTES, default=TOUTES,
                        key="age_metros",
                        help="Métropoles incluses dans la comparaison par âge.",
                    )
                else:
                    sel_communes_age = st.multiselect(
                        "Commune de la métropole de Grenoble",
                        sorted(COMMUNES["Grenoble"]),
                        default=sorted(COMMUNES["Grenoble"])[:2],
                        key="age_communes",
                        help="Communes sélectionnées pour la comparaison des structures d'âge.",
                    )

                annee_age = st.selectbox(
                    "Année", annees_dispo,
                    index=len(annees_dispo)-1,
                    key="an_age",
                    help="Année de référence des pyramides et indicateurs."
                )

                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("---")

            # ════════════════════════════════════════════════════════════════
            # VUE MÉTROPOLES
            # ════════════════════════════════════════════════════════════════
            if mode_age == "Comparaison Métropoles":

                if not sel_metros_age:
                    st.warning("Sélectionnez au moins une métropole.")
                    st.stop()

                st.subheader(
                    f"Indicateurs clés - {annee_age}",
                    help="Part d'une partie de la population dans la population totale"
                )

                kpi_cols = st.columns(len(sel_metros_age))

                for i, m in enumerate(sel_metros_age):
                    df_m = df_pop[(df_pop["metropole"] == m) & (df_pop["annee"] == annee_age)]

                    tot   = pop_totale_df(df_m)
                    p_m25 = pop_tranches(df_m, TRANCHES_M25)
                    p_sen = pop_tranches(df_m, TRANCHES_SEN)

                    pct_m25 = p_m25 / tot * 100 if tot > 0 else np.nan
                    pct_sen = p_sen / tot * 100 if tot > 0 else np.nan

                    with kpi_cols[i]:
                        st.markdown(f"**{m}**")

                        kpi_color2 = COULEURS.get(m, "#888888")
                        for title, value in [
                            ("Moins de 25 ans", pct_m25),
                            ("65 ans et +", pct_sen),
                        ]:
                            val = f"{value:.1f}%" if not np.isnan(value) else "N/D"

                            st.markdown(f"""
                            <div style='
                                display:flex;
                                border-radius:8px;
                                box-shadow:0 2px 6px rgba(0,0,0,0.1);
                                background:#fff;
                                border-left:6px solid {kpi_color2};
                                margin-bottom:10px;
                                padding:10px 16px;
                            '>
                                <div>
                                    <div style='font-size:11px;font-weight:700;color:#666;text-transform:uppercase;'>{title}</div>
                                    <div style='font-size:24px;font-weight:bold;color:#111;'>{val}</div>
                                    <div style='font-size:10px;color:#888;'>Part de la population</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                st.markdown("---")

                # ── Pyramides ─────────────────────────────────────────────
                st.subheader("Pyramides des âges comparées",
                             help="Compare la répartition hommes/femmes par tranche d'âge.")

                COLORS_METRO_H = {
                    "Grenoble":      "#FF584D",
                    "Rennes":        "#C5C9CE",
                    "Saint-Étienne": "#A2A6AE",
                    "Rouen":         "#E8E8EB",
                    "Montpellier":   "#77818C",
                }
                COLORS_METRO_F = {
                    "Grenoble":      "#FFBBB7",
                    "Rennes":        "#E2E4E7",
                    "Saint-Étienne": "#C8CACF",
                    "Rouen":         "#F4F4F6",
                    "Montpellier":   "#A4ABB2",
                }

                ncols = min(len(sel_metros_age), 3)
                rows = [sel_metros_age[i:i+ncols] for i in range(0, len(sel_metros_age), ncols)]

                for row in rows:
                    cols = st.columns(len(row))
                    for j, m in enumerate(row):
                        df_m = df_pop[(df_pop["metropole"] == m) & (df_pop["annee"] == annee_age)]
                        fig = build_pyramide(df_m, m,
                                             COLORS_METRO_H.get(m, "#2D6A4F"),
                                             COLORS_METRO_F.get(m, "#95D5B2"))
                        with cols[j]:
                            st.plotly_chart(style(fig, 30), use_container_width=True)

                with st.expander("💡 Comment interpréter ces deux graphiques ?"):
                    st.write("La pyramide montre la forme de la population par âge et sexe.")

                st.markdown("---")

                # ── Évolution ─────────────────────────────────────────────
                st.subheader("Évolution des groupes d'âge (2011 → 2022)",
                             help="Suit les tendances des jeunes et des seniors dans le temps.")

                c1, c2 = st.columns(2)

                with c1:
                    st.markdown("##### Part des moins de 25 ans (%)")
                    rows = []
                    for m in sel_metros_age:
                        for an in annees_dispo:
                            df_m = df_pop[(df_pop["metropole"] == m) & (df_pop["annee"] == an)]
                            tot = pop_totale_df(df_m)
                            p = pop_tranches(df_m, TRANCHES_M25)
                            if tot > 0:
                                rows.append({"Métropole": m, "Année": an, "Part (%)": p/tot*100})
                    df_ev = pd.DataFrame(rows)
                    if not df_ev.empty:
                        fig_ev_line = px.line(df_ev, x="Année", y="Part (%)", color="Métropole",
                                              markers=True, color_discrete_map=COULEURS)
                        fig_ev_line.update_traces(
                            hovertemplate="<b>Métropole : %{fullData.name}</b><br>Année : %{x}<br>Part : %{y:.2f}%<extra></extra>"
                        )
                        st.plotly_chart(style(fig_ev_line))

                with c2:
                    st.markdown("##### Part des 65 ans et + (%)")
                    rows = []
                    for m in sel_metros_age:
                        for an in annees_dispo:
                            df_m = df_pop[(df_pop["metropole"] == m) & (df_pop["annee"] == an)]
                            tot = pop_totale_df(df_m)
                            p = pop_tranches(df_m, TRANCHES_SEN)
                            if tot > 0:
                                rows.append({"Métropole": m, "Année": an, "Part (%)": p/tot*100})
                    df_ev = pd.DataFrame(rows)
                    if not df_ev.empty:
                        fig_ev_line2 = px.line(df_ev, x="Année", y="Part (%)", color="Métropole",
                                               markers=True, color_discrete_map=COULEURS)
                        fig_ev_line2.update_traces(
                            hovertemplate="<b>Métropole : %{fullData.name}</b><br>Année : %{x}<br>Part : %{y:.2f}%<extra></extra>"
                        )
                        st.plotly_chart(style(fig_ev_line2))

                with st.expander("💡 Comment interpréter ces deux graphiques ?"):
                    st.write("Si la courbe monte, la part du groupe augmente dans la population ; compare les pentes pour identifier les territoires qui vieillissent ou rajeunissent le plus.")

            # ════════════════════════════════════════════════════════════════
            # VUE COMMUNALE
            # ════════════════════════════════════════════════════════════════
            else:

                communes_age = sel_communes_age if sel_communes_age else []
                if not communes_age:
                    st.info("Sélectionnez au moins une commune.")
                    st.stop()

                st.subheader(
                    f"Indicateurs clés - {annee_age}",
                    help="Part d'une partie de la population dans la population totale"
                )

                kpi_cols = st.columns(len(communes_age))

                for i, comm in enumerate(communes_age):
                    df_c = df_pop[(df_pop["LIBELLE"] == comm) & (df_pop["annee"] == annee_age)]

                    tot   = pop_totale_df(df_c)
                    p_m25 = pop_tranches(df_c, TRANCHES_M25)
                    p_sen = pop_tranches(df_c, TRANCHES_SEN)

                    pct_m25 = p_m25 / tot * 100 if tot > 0 else np.nan
                    pct_sen = p_sen / tot * 100 if tot > 0 else np.nan

                    with kpi_cols[i]:
                        st.markdown(f"**{comm}**")

                        for title, value in [
                            ("Moins de 25 ans", pct_m25),
                            ("65 ans et +", pct_sen),
                        ]:
                            val = f"{value:.1f}%" if not np.isnan(value) else "N/D"

                            st.markdown(f"""
                            <div style='
                                display:flex;
                                border-radius:8px;
                                box-shadow:0 2px 6px rgba(0,0,0,0.1);
                                background:#fff;
                                border-left:6px solid #1e5631;
                                margin-bottom:10px;
                                padding:10px 16px;
                            '>
                                <div>
                                    <div style='font-size:11px;font-weight:700;color:#666;text-transform:uppercase;'>{title}</div>
                                    <div style='font-size:24px;font-weight:bold;color:#111;'>{val}</div>
                                    <div style='font-size:10px;color:#888;'>Part de la population</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                st.markdown("---")

                st.subheader("🔺 Pyramide(s) des âges",
                             help="Compare la répartition hommes/femmes par tranche d'âge.")

                COLORS_COMM = ["#2D6A4F", "#1A6FA3", "#C45B2A", "#7B3FA0", "#D4A017"]
                COLORS_COMM_F = ["#95D5B2", "#AED4F0", "#F2A07A", "#C9A5E0", "#F5D87A"]

                ncols = min(len(communes_age), 3)
                rows = [communes_age[i:i+ncols] for i in range(0, len(communes_age), ncols)]

                for row in rows:
                    cols = st.columns(len(row))
                    for j, comm in enumerate(row):
                        df_c = df_pop[(df_pop["LIBELLE"] == comm) & (df_pop["annee"] == annee_age)]
                        fig = build_pyramide(
                            df_c, comm,
                            COLORS_COMM[j % len(COLORS_COMM)],
                            COLORS_COMM_F[j % len(COLORS_COMM_F)]
                        )
                        with cols[j]:
                            st.plotly_chart(style(fig, 30), use_container_width=True)

                with st.expander("💡 Comment interpréter ces deux graphiques ?"):
                    st.write("La pyramide montre la forme de la population par âge et sexe.")

                st.markdown("---")

                st.subheader("Évolution des groupes d'âge (2011 → 2022)",
                             help="Suit les tendances des jeunes et des seniors dans le temps.")

                c1, c2 = st.columns(2)

                with c1:
                    st.markdown("##### Part des moins de 25 ans (%)")
                    rows = []
                    for comm in communes_age:
                        for an in annees_dispo:
                            df_c = df_pop[(df_pop["LIBELLE"] == comm) & (df_pop["annee"] == an)]
                            tot = pop_totale_df(df_c)
                            p = pop_tranches(df_c, TRANCHES_M25)
                            if tot > 0:
                                rows.append({"Commune": comm, "Année": an, "Part (%)": p/tot*100})
                    df_ev = pd.DataFrame(rows)
                    if not df_ev.empty:
                        st.plotly_chart(style(px.line(df_ev, x="Année", y="Part (%)", color="Commune", markers=True)))

                with c2:
                    st.markdown("##### Part des 65 ans et + (%)")
                    rows = []
                    for comm in communes_age:
                        for an in annees_dispo:
                            df_c = df_pop[(df_pop["LIBELLE"] == comm) & (df_pop["annee"] == an)]
                            tot = pop_totale_df(df_c)
                            p = pop_tranches(df_c, TRANCHES_SEN)
                            if tot > 0:
                                rows.append({"Commune": comm, "Année": an, "Part (%)": p/tot*100})
                    df_ev = pd.DataFrame(rows)
                    if not df_ev.empty:
                        st.plotly_chart(style(px.line(df_ev, x="Année", y="Part (%)", color="Commune", markers=True)))

                with st.expander("💡 Comment interpréter ces deux graphiques ?"):
                    st.write("Si la courbe monte, la part du groupe augmente dans la population ; compare les pentes pour identifier les territoires qui vieillissent ou rajeunissent le plus.")

# ==============================================================================
# ONGLET 3 - MOBILITÉS
# ==============================================================================
if vue == "Démographie":
    with tab3:
        
        # Vérification des données
        data_ok = any(df is not None for df in [df_res, df_prof, df_scol])
        if not data_ok:
            st.info("📂 Fichiers de mobilité manquants.")
        else:
            # ── Introduction Méthodologique ──────────────────────────────────
            st.markdown("""
                <div style='background-color: #f1f8f5; padding: 15px; border-radius: 10px; border-left: 5px solid #1C3A27; margin-bottom: 20px; font-size: 14px;'>
                    <strong>Comprendre les thématiques :</strong><br>
                    • 🏠 <b>Migrations</b> : Analyse les changements de domicile sur un an. Reflète l'attractivité résidentielle (envie de s'installer).<br>
                    • 💼 <b>Professionnelle</b> : Analyse les flux domicile-travail des actifs. Identifie les pôles d'emploi face aux villes-dortoirs.<br>
                    • 🎓 <b>Scolaire</b> : Analyse le trajet entre lieu de résidence et lieu d'études. Mesure le rayonnement des centres d'enseignement.<br>
                    <br>
                    <em>Ces données INSEE permettent de comparer si un territoire "aspire" ou "perd" des populations selon leurs activités.</em>
                </div>
                """, unsafe_allow_html=True)
            # ── Style CSS pour les radios ────────────────────────────────────
            st.markdown("""
                <style>
                div[data-testid="stRadio"] > label { display: none; }
                div[data-testid="stRadio"] > div {
                    flex-direction: row;
                    align-items: center;
                    gap: 1.5rem;
                }
                div[data-testid="stRadio"] > div > label:hover {
                    background-color: transparent !important;
                    box-shadow: none !important;
                    cursor: pointer;
                }
                </style>
            """, unsafe_allow_html=True)

            # ── Bandeau filtres ──────────────────────────────────────────────
            with st.container():
                filter_bar("Filtres - Mobilités")

                # ── LIGNE 1 : Niveau géographique ────────────────────────────
                col_geo_label, col_geo_options = st.columns([1, 3])
                with col_geo_label:
                    st.markdown(
                        "<div style='padding-top:8px; font-weight:600; font-size:14px;'>Niveau géographique</div>",
                        unsafe_allow_html=True
                    )
                with col_geo_options:
                    mode_mob = st.radio(
                        "",
                        ["Comparaison Métropoles", "Comparaison communes métropole de Grenoble"],
                        key="mob_mode",
                        horizontal=True,
                        help="Choisissez si vous voulez voir les communes de Grenoble ou comparer Grenoble aux autres métropoles."
                    )

                # ── LIGNE 2 : Sélection des entités ──────────────────────────
                if mode_mob == "Comparaison communes métropole de Grenoble":
                    met_choice = "Grenoble"
                    st.markdown(f"**Communes de la métropole de Grenoble**")
                    sel_communes_mob = st.multiselect(
                        "Sélection des communes",
                        sorted(COMMUNES[met_choice]),
                        default=sorted(COMMUNES[met_choice])[:2],
                        key="mob_communes"
                    )
                    coms_selection = sel_communes_mob
                    txt_aide_geo = f"Analyse des flux cumulés pour le groupe : {', '.join(sel_communes_mob)}."
                else:
                    sel_metros_mob = st.multiselect(
                        "Métropoles à comparer",
                        TOUTES,
                        default=TOUTES[:3],
                        key="mob_metros"
                    )
                    coms_selection = [c for m in sel_metros_mob for c in COMMUNES[m]]
                    txt_aide_geo = "Comparaison des flux globaux entre les métropoles sélectionnées."

                # ── LIGNE 3 : Thématique + Année ─────────────────────────────
                mob_col1, mob_col2 = st.columns(2)
                with mob_col1:
                    theme_mob = st.selectbox(
                        "Thématique d'analyse",
                        ["🏠 Migrations Résidentielles", "💼 Mobilité Professionnelle", "🎓 Mobilité Scolaire"],
                        key="mob_theme",
                        help="""
                        - **Migrations** : Où les gens déménagent-ils ?
                        - **Professionnelle** : Où travaillent les actifs (flux domicile-travail) ?
                        - **Scolaire** : Où étudient les élèves/étudiants ?
                        """
                    )

                # Logique des couleurs et labels selon la thématique
                if "Migrations" in theme_mob:
                    current_mob_df, col_orig, col_dest = df_res, "commune_origine", "commune_destination"
                    label_in, label_out, color_in, color_out = "Arrivées", "Départs", "#2D6A4F", "#B7E4C7"
                elif "Professionnelle" in theme_mob:
                    current_mob_df, col_orig, col_dest = df_prof, "commune_residence", "commune_travail"
                    label_in, label_out, color_in, color_out = "Entrants", "Sortants", "#1A6FA3", "#AED4F0"
                else:
                    current_mob_df, col_orig, col_dest = df_scol, "commune_origine", "commune_destination"
                    label_in, label_out, color_in, color_out = "Élèves Entrants", "Élèves Sortants", "#7B3FA0", "#D5B8F0"

                if current_mob_df is not None:
                    annees_mob = sorted(current_mob_df["annee"].dropna().unique().astype(int), reverse=True)
                    with mob_col2:
                        sel_annee_mob = st.selectbox("Année", annees_mob, key="mob_annee")

            # ── Calculs ──────────────────────────────────────────────────────
            df_mob_filtered = current_mob_df[
                (current_mob_df[col_orig] != current_mob_df[col_dest]) &
                (current_mob_df["annee"] == sel_annee_mob)
            ]
            
            entities_mob = []
            targets = sel_communes_mob if mode_mob == "Comparaison communes métropole de Grenoble" else sel_metros_mob
            
            for target in targets:
                coms = [target] if mode_mob == "Comparaison communes métropole de Grenoble" else COMMUNES[target]
                
                f_in  = int(df_mob_filtered[df_mob_filtered[col_dest].isin(coms)]["flux"].sum())
                f_out = int(df_mob_filtered[df_mob_filtered[col_orig].isin(coms)]["flux"].sum())
                solde = f_in - f_out
                
                entities_mob.append({
                    "name": target, 
                    "in": f_in, 
                    "out": f_out, 
                    "solde": solde
                })
                
            df_plot_mob = pd.DataFrame(entities_mob)

            # ── Affichage Principal ───────────────────────────────────────────
            if not df_plot_mob.empty:
                st.markdown(
                    f"#### Bilan net - {theme_mob} ({sel_annee_mob})",
                    help="Le bilan net (solde) est la différence entre ceux qui arrivent et ceux qui partent. Un chiffre positif indique une attractivité."
                )

                # KPI cards
                kpi_cols = st.columns(len(df_plot_mob))
                for i, row in df_plot_mob.iterrows():
                    color_solde = "#2ecc71" if row["solde"] >= 0 else "#e74c3c"
                    # Formatage français : +20 157
                    val_formatee = f"{row['solde']:+,d}".replace(",", " ")
                    
                    kpi_mob_color = COULEURS.get(row['name'], "#888888")
                    with kpi_cols[i]:
                        st.markdown(f"""
                        <div style='display: flex; flex-direction: row; align-items: stretch; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 6px rgba(0,0,0,0.1); background: #fff; min-height: 80px; border-left: 6px solid {kpi_mob_color};'>
                            <div style='padding: 10px 16px; display: flex; flex-direction: column; justify-content: center;'>
                                <div style='font-size:11px; font-weight:700; letter-spacing:0.08em; color:#666; text-transform:uppercase;'>{row['name']}</div>
                                <div style='font-size:24px; font-weight:bold; color:#111;'>{val_formatee}</div>
                                <div style='color:{color_solde}; font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.05em;'>SOLDE</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                st.markdown("---")

                noms_mob = df_plot_mob["name"].tolist()
                border_mob   = ["#FF584D" if n == "Grenoble" else "rgba(0,0,0,0)" for n in noms_mob]
                border_w_mob = [2.5 if n == "Grenoble" else 0 for n in noms_mob]

                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("##### 📊 Volume des échanges",
                        help="Barres foncées = entrées, barres claires = sorties. Bordures rouges = Grenoble.")
                    fig_vol = go.Figure()
                    fig_vol.add_trace(go.Bar(
                        x=noms_mob, y=df_plot_mob["in"], name=label_in,
                        marker_color="#7A7E87",
                        marker_line_color=border_mob, marker_line_width=border_w_mob,
                        hovertemplate="<b>Territoire : %{x}</b><br>" + label_in + " : %{y:.2s}<extra></extra>",
                    ))
                    fig_vol.add_trace(go.Bar(
                        x=noms_mob, y=df_plot_mob["out"], name=label_out,
                        marker_color="#C8CACF",
                        marker_line_color=border_mob, marker_line_width=border_w_mob,
                        hovertemplate="<b>Territoire : %{x}</b><br>" + label_out + " : %{y:.2s}<extra></extra>",
                    ))
                    fig_vol.update_layout(barmode="group", height=350, margin=dict(t=20, b=60),
                        legend=dict(orientation="h", y=1.2),
                        xaxis=dict(title="Territoire", showgrid=False),
                        yaxis=dict(title="Nombre de flux", showgrid=True, gridcolor="#eeeeee"))
                    st.plotly_chart(fig_vol, use_container_width=True)

                with c2:
                    st.markdown("##### 📈 Performance nette",
                        help="Solde = entrées − sorties. Gris foncé = positif, gris clair = négatif. Bordures rouges = Grenoble.")
                    colors_net = ["#7A7E87" if s >= 0 else "#3A3D44" for s in df_plot_mob["solde"]]
                    fig_net = go.Figure(go.Bar(
                        x=noms_mob, y=df_plot_mob["solde"],
                        marker_color=colors_net,
                        marker_line_color=border_mob, marker_line_width=border_w_mob,
                        hovertemplate="<b>Territoire : %{x}</b><br>Solde net : %{y:.2s}<extra></extra>",
                    ))
                    fig_net.add_hline(y=0, line_dash="dash", line_color="#888")
                    fig_net.update_layout(height=350, margin=dict(t=20, b=60),
                        xaxis=dict(title="Territoire", showgrid=False),
                        yaxis=dict(title="Solde (entrées − sorties)", showgrid=True, gridcolor="#eeeeee"))
                    st.plotly_chart(fig_net, use_container_width=True)

                with st.expander("❓ Comment interpréter ces deux graphiques ?"):
                    st.write("""
                    - **Si le volume est élevé mais le solde est proche de zéro** : La commune "brasse" beaucoup de monde (ex: ville étape ou pôle de transit) mais ne retient pas de population.
                    - **Si le solde est très positif** : Le territoire est un 'aspirateur'. En résidentiel, cela signifie qu'il est très demandé. En professionnel, qu'il est un moteur d'emploi régional.
                    """)

                st.markdown("---")
                st.markdown("#### 🌍 Analyse géographique des flux", help=txt_aide_geo)

                if mode_mob == "Comparaison communes métropole de Grenoble" and len(sel_communes_mob) > 1:
                    st.info(f"**Analyse de groupe** : Les graphiques ci-dessous affichent les partenaires cumulés pour : {', '.join(sel_communes_mob)}.")

                col_l, col_r = st.columns(2)
                
                # --- TOP 10 PROVENANCES (CUMULÉ) ---
                with col_l:
                    st.markdown(f"<h5 style='text-align:center;'> Top 10 provenances ({label_in})</h5>", unsafe_allow_html=True)
                    raw_in = df_mob_filtered[df_mob_filtered[col_dest].isin(coms_selection)]
                    grouped_in = raw_in.groupby(col_orig)["flux"].sum().reset_index()
                    top_in = grouped_in.nlargest(10, "flux")
                    if not top_in.empty:
                        fig_in = px.bar(top_in, x="flux", y=col_orig, orientation="h", color_discrete_sequence=[color_in], text_auto=".0f")
                        fig_in.update_layout(yaxis=dict(categoryorder="total ascending", title=""), xaxis=dict(title="Nombre de flux"), height=350)
                        st.plotly_chart(fig_in, use_container_width=True)

                # --- TOP 10 DESTINATIONS (CUMULÉ) ---
                with col_r:
                    st.markdown(f"<h5 style='text-align:center;'> Top 10 destinations ({label_out})</h5>", unsafe_allow_html=True)
                    raw_out = df_mob_filtered[df_mob_filtered[col_orig].isin(coms_selection)]
                    grouped_out = raw_out.groupby(col_dest)["flux"].sum().reset_index()
                    top_out = grouped_out.nlargest(10, "flux")
                    if not top_out.empty:
                        fig_out = px.bar(top_out, x="flux", y=col_dest, orientation="h", color_discrete_sequence=[color_out], text_auto=".0f")
                        fig_out.update_layout(yaxis=dict(categoryorder="total ascending", title=""), xaxis=dict(title="Nombre de flux"), height=350)
                        st.plotly_chart(fig_out, use_container_width=True)

                with st.expander("📘 Guide d'interprétation des flux cumulés"):
                    nom_territoire = "votre sélection" if len(coms_selection) > 1 else coms_selection[0]
                    st.markdown(f"""
                    ### Comment lire ces graphiques ?
                    Lorsque vous analysez **{nom_territoire}**, l'outil regroupe les données pour offrir une vision stratégique.
                    
                    #### 1. Le principe du "Territoire Unique"
                    L'outil trace une frontière globale autour de votre sélection. Toutes les communes choisies sont traitées comme un seul bloc cohérent. 
                    
                    #### 2. Fusion et Cumul des données
                    Les flux venant d'une même ville vers différentes communes de votre zone sont **additionnés**.
                    * *Exemple :* Si 100 personnes de Lyon vont à Grenoble et 50 à Meylan, vous verrez une seule barre **"Lyon : 150"**.
                    
                    #### 3. Filtrage des flux internes
                    Les déplacements effectués **entre** les communes que vous avez sélectionnées sont masqués pour se concentrer uniquement sur les échanges avec l'extérieur.
                    """) 
# ==============================================================================
# ONGLET 4 — MÉNAGES
# ==============================================================================
if vue == "Démographie":
    with tab4:

        data_men_ok = (df_men_age is not None) and (df_men_csp is not None)
        if not data_men_ok:
            st.info("📂 Fichiers de données sur les ménages introuvables.")
        else:
            # ── Définition des regroupements ──────────────────────────────────
            TYPE_GROUPES = {
                "Personne seule":        lambda cols: [c for c in cols if "pers_seule" in c],
                "Couple sans enfant":    lambda cols: [c for c in cols if "cpl_sans_enf" in c],
                "Couple avec enfant(s)": lambda cols: [c for c in cols if "cpl_avec_enfant" in c or "cpl_1enf" in c],
                "Famille monoparentale": lambda cols: [c for c in cols if "fam_monoparentale" in c],
                "Autre ménage":          lambda cols: [c for c in cols if "autre_menage" in c],
            }

            CSP_GROUPES = {
                "Agriculteurs":              ["agriculteurs"],
                "Artisans / Commerçants /\nChefs d'entreprise": ["artisans", "commercants", "chef_entreprise"],
                "Cadres & Prof.\nintellectuelles sup.": [
                    "professions_liberales", "cadre_admin_fonction_pub",
                    "prof_scientifique_sup", "info_art_spectacle",
                    "cadre_commercial", "ingenieur_cadre_tech",
                ],
                "Professions\nintermédiaires": [
                    "prof_enseignement", "prof_inter_sante_social",
                    "prof_inter_fonction_pub", "prof_inter_admin_com",
                    "technicien", "agent_maitrise",
                ],
                "Employés": [
                    "emp_fonction_pub", "securite_defense",
                    "emp_admin_entreprise", "emp_commerce", "service_particulier",
                ],
                "Ouvriers": [
                    "ouvrier_qualif_indus", "ouvrier_qualif_artisanal",
                    "conducteur_transport", "cariste_magasinier",
                    "ouvrier_peu_qualif_indus", "ouvrier_peu_qualif_artisanal",
                    "ouvrier_agricole",
                ],
                "Retraités /\nInactifs": ["retraites_inactifs", "chomeur_jamais_travaille"],
            }

            TAILLES = {
                "1 pers.":      (1, "1pers"),
                "2 pers.":      (2, "2pers"),
                "3 pers.":      (3, "3pers"),
                "4 pers.":      (4, "4pers"),
                "5 pers.":      (5, "5pers"),
                "6 pers. et +": (6, "6pers_ouplus"),
            }

            # ── Fonctions utilitaires ────────────────────────────────────────
            def somme_colonnes(df_ent, mots_cles):
                cols = [c for c in df_ent.columns if any(k in c for k in mots_cles)]
                return df_ent[cols].sum().sum() if cols else 0

            def nb_menages_depuis_age(df_ent_age):
                """
                Nombre total de ménages depuis le fichier Menage_age_situation.
                On somme toutes les colonnes Menages_* en excluant CODGEO et LIBGEO.
                Chaque cellule représente un nombre de ménages d'un type donné :
                la somme donne le total des ménages du territoire.
                """
                cols_men = [
                    c for c in df_ent_age.columns
                    if c.startswith("Menages_") and c not in ("CODGEO", "LIBGEO")
                ]
                return int(df_ent_age[cols_men].sum().sum()) if cols_men else 0

            def get_population_menages(ent):
                """
                Retourne la population municipale 2022 depuis df_gen
                (Donnees_generales_comparatives.csv) pour calculer le ratio
                personnes/ménage.

                - Métropoles  : epci_val() → ligne EPCI du df_gen
                - Communes    : commune_val() → ligne commune du df_gen
                  (disponible uniquement pour les communes de Grenoble)

                On utilise df_gen comme source unique de population car c'est
                le fichier de référence cohérent avec le fichier ménages.
                """
                if mode_men == "Comparaison Métropoles":
                    return epci_val(ent, "population_2022")
                else:
                    # commune_val est définie dans l'onglet 1 mais accessible
                    # car les fonctions Python sont dans le même scope d'exécution
                    if df_gen is None:
                        return np.nan
                    comm_norm = normalize_name(ent)
                    geo = df_gen["territoire"].astype(str).str.extract(
                        r"^(Commune|EPCI)\s*:\s*(.*?)\s*\(\d+\)\s*$"
                    )
                    mask = (geo[0] == "Commune") & (geo[1].apply(normalize_name) == comm_norm)
                    rows_g = df_gen[mask]
                    if rows_g.empty:
                        return np.nan
                    v = rows_g.iloc[0].get("population_2022", np.nan)
                    return float(v) if pd.notna(v) else np.nan

            def distrib_taille(df_ent_csp):
                """
                Distribution par taille de ménage depuis le fichier CSP×taille.
                Les colonnes Menages_Npers_* donnent le nombre de ménages
                de taille N pour chaque CSP. On les somme toutes par taille.
                """
                rows = []
                for label, (nb_pers, slug) in TAILLES.items():
                    cols = [c for c in df_ent_csp.columns if slug in c]
                    nb = df_ent_csp[cols].sum().sum() if cols else 0
                    rows.append({"Taille": label, "Ménages": int(nb)})
                df_t = pd.DataFrame(rows)
                total = df_t["Ménages"].sum()
                df_t["Part (%)"] = df_t["Ménages"] / total * 100 if total > 0 else 0
                return df_t

            def render_kpi_card(title, value, subtitle, accent_color="#1a7a4a"):
                return f"""
                <div style='display:flex;flex-direction:row;align-items:stretch;border-radius:8px;
                    overflow:hidden;box-shadow:0 2px 6px rgba(0,0,0,0.1);background:#fff;
                    min-height:80px;border-left:6px solid {accent_color};margin-bottom:10px;'>
                    <div style='padding:10px 16px;display:flex;flex-direction:column;
                        justify-content:center;width:100%;'>
                        <div style='font-size:11px;font-weight:700;letter-spacing:0.08em;
                            color:#666;text-transform:uppercase;'>{title}</div>
                        <div style='font-size:24px;font-weight:bold;color:#111;margin:4px 0;'>{value}</div>
                        <div style='color:{accent_color};font-size:11px;font-weight:700;
                            text-transform:uppercase;letter-spacing:0.05em;'>{subtitle}</div>
                    </div>
                </div>"""

            # ── Bandeau filtres ──────────────────────────────────────────────
            with st.container():
                filter_bar("Filtres - Ménages")

                col_geo_label, col_geo_options = st.columns([1, 3])
                with col_geo_label:
                    st.markdown(
                        "<div style='padding-top:8px;font-weight:600;font-size:14px;'>"
                        "Niveau géographique</div>", unsafe_allow_html=True,
                    )
                with col_geo_options:
                    mode_men = st.radio(
                        "", ["Comparaison Métropoles", "Comparaison communes métropole de Grenoble"],
                        key="men_mode", horizontal=True,
                        help="Comparez les métropoles entre elles, ou analysez les communes de Grenoble.",
                    )

                if mode_men == "Comparaison communes métropole de Grenoble":
                    sel_communes_men = st.multiselect(
                        "Commune de la métropole de Grenoble",
                        sorted(COMMUNES["Grenoble"]),
                        default=sorted(COMMUNES["Grenoble"])[:3],
                        key="men_communes",
                        help="Communes de la métropole grenobloise à comparer.",
                    )
                    selection_men = sel_communes_men
                else:
                    sel_metros_men = st.multiselect(
                        "Métropoles à comparer", TOUTES, default=TOUTES[:3],
                        key="men_metros",
                        help="Sélectionnez les métropoles à comparer.",
                    )
                    selection_men = sel_metros_men

                theme_men = st.selectbox(
                    "Thématique d'analyse",
                    ["👨‍👩‍👧 Type & taille de ménage", "🧑‍💼 CSP du chef de ménage"],
                    key="theme_men",
                    help=(
                        "**Type & taille** : Composition familiale (personne seule, couple, "
                        "famille monoparentale…) et taille moyenne du ménage.\n\n"
                        "**CSP** : Catégorie socio-professionnelle de la personne de référence "
                        "du foyer, croisée avec la taille du ménage."
                    ),
                )

            st.markdown("---")

            if not selection_men:
                st.warning("⚠️ Sélectionnez au moins un territoire.")
                st.stop()

            # ── Extraction des données selon le mode ─────────────────────────
            def get_df_age(ent):
                if mode_men == "Comparaison Métropoles":
                    return df_men_age[df_men_age["metropole"] == ent]
                return df_men_age[df_men_age["LIBGEO"] == ent]

            def get_df_csp(ent):
                if mode_men == "Comparaison Métropoles":
                    return df_men_csp[df_men_csp["metropole"] == ent]
                return df_men_csp[df_men_csp["LIBGEO"] == ent]

            PALETTE_TYPE = ["#1B4332", "#2D6A4F", "#40916C", "#74C69D", "#D8F3DC"]
            PALETTE_CSP  = ["#081C15", "#1B4332", "#2D6A4F", "#40916C",
                            "#52B788", "#74C69D", "#B7E4C7"]
            COLOR_ENT = (
                [COULEURS.get(e, "#333") for e in selection_men]
                if mode_men == "Comparaison Métropoles"
                else ["#081C15","#2D6A4F","#40916C","#74C69D","#95D5B2",
                      "#B7E4C7","#1A6FA3","#C45B2A","#7B3FA0"]
            )

            # ════════════════════════════════════════════════════════════════
            # THÈME 1 — TYPE & TAILLE DE MÉNAGE
            # ════════════════════════════════════════════════════════════════
            if "Type" in theme_men:
                cols_age = [c for c in df_men_age.columns if c.startswith("Menages_")]

                # ── KPIs ────────────────────────────────────────────────────
                st.markdown(
                    "#### Aperçu global des ménages",
                    help=(
                        "**Nombre de ménages** : somme de toutes les colonnes Menages_* "
                        "du fichier Menage_age_situation (RP 2022). Chaque colonne représente "
                        "un type de ménage dans une tranche d'âge donnée.\n\n"
                        "**Personnes par ménage** : Population 2022 (source : "
                        "Donnees_generales_comparatives.csv) divisée par le nombre de ménages. "
                        "Pour une métropole, c'est la population EPCI / total des ménages des "
                        "communes de la métropole. La valeur nationale est d'environ 2,2 pers./ménage."
                    ),
                )
                kpi_cols = st.columns(len(selection_men))
                for i, ent in enumerate(selection_men):
                    df_age_ent = get_df_age(ent)
                    nb_men = nb_menages_depuis_age(df_age_ent)
                    pop = get_population_menages(ent)
                    if nb_men > 0 and not np.isnan(pop):
                        ratio = pop / nb_men
                        ratio_str = f"{ratio:.2f} pers./ménage"
                    else:
                        ratio_str = "N/D"
                    with kpi_cols[i]:
                        st.markdown(
                            render_kpi_card(
                                ent,
                                fmt(nb_men),
                                ratio_str,
                                COLOR_ENT[i % len(COLOR_ENT)],
                            ),
                            unsafe_allow_html=True,
                        )

                st.markdown("---")

                # ── Graphique 1 : Distribution par taille ────────────────────
                st.markdown(
                    "##### Distribution par taille de ménage (%)",
                    help=(
                        "Répartition des ménages selon leur nombre de personnes, "
                        "calculée depuis le fichier CSP×taille (colonnes Menages_Npers_*). "
                        "En France, environ 37% des ménages sont des personnes seules (1 pers.), "
                        "et 33% sont des couples sans enfant (2 pers.). "
                        "Une forte part de grands ménages (4+ pers.) indique un profil familial."
                    ),
                )
                rows_taille = []
                for ent in selection_men:
                    df_csp_ent = get_df_csp(ent)
                    df_t = distrib_taille(df_csp_ent)
                    df_t["Territoire"] = ent
                    rows_taille.append(df_t)
                df_taille_all = pd.concat(rows_taille, ignore_index=True) if rows_taille else pd.DataFrame()

                if not df_taille_all.empty:
                    fig_taille = px.bar(
                        df_taille_all, x="Taille", y="Part (%)", color="Territoire",
                        barmode="group", text_auto=".1f",
                        color_discrete_sequence=COLOR_ENT,
                        category_orders={"Taille": list(TAILLES.keys())},
                        height=380,
                    )
                    fig_taille.update_traces(textposition="outside", textfont_size=9)
                    fig_taille.update_layout(
                        legend=dict(orientation="h", y=1.12, title=""),
                        xaxis_title="Taille du ménage",
                        yaxis_title="Part des ménages (%)",
                        margin=dict(t=20),
                    )
                    st.plotly_chart(style(fig_taille), use_container_width=True)

                st.markdown("---")

                # ── Graphiques 2 & 3 : Type de ménage ────────────────────────
                c1, c2 = st.columns(2)
                rows_type = []
                for ent in selection_men:
                    df_age_ent = get_df_age(ent)
                    nb_total = df_age_ent[cols_age].sum().sum()
                    for nom, fn in TYPE_GROUPES.items():
                        cols_grp = fn(cols_age)
                        val = df_age_ent[cols_grp].sum().sum() if cols_grp else 0
                        rows_type.append({
                            "Territoire": ent,
                            "Type de ménage": nom,
                            "Nombre": int(val),
                            "Part (%)": val / nb_total * 100 if nb_total > 0 else 0,
                        })
                df_type = pd.DataFrame(rows_type)

                with c1:
                    st.markdown(
                        "##### Composition des ménages — volume",
                        help=(
                            "Nombre absolu de foyers par type de composition familiale. "
                            "Permet de dimensionner les besoins réels en logements adaptés "
                            "(studios pour personnes seules, grands logements pour familles…)."
                        ),
                    )
                    if not df_type.empty:
                        fig_vol = px.bar(
                            df_type, x="Type de ménage", y="Nombre", color="Territoire",
                            barmode="group", color_discrete_sequence=COLOR_ENT, height=400,
                        )
                        fig_vol.update_layout(
                            legend=dict(orientation="h", y=1.12, title=""),
                            xaxis_title="", yaxis_title="Nombre de ménages",
                            xaxis_tickangle=-15, margin=dict(t=20),
                        )
                        st.plotly_chart(style(fig_vol), use_container_width=True)

                with c2:
                    st.markdown("##### Composition des ménages — structure (%)", help="...")
                    if not df_type.empty:
                        # Palette grise pour les 5 types
                        grey_types = ["#3A3D44", "#7A7E87", "#A2A6AE", "#C8CACF", "#E8E8EB"]
                        fig_pct = px.bar(
                            df_type, x="Part (%)", y="Territoire", color="Type de ménage",
                            orientation="h", barmode="stack", text_auto=".1f",
                            color_discrete_sequence=grey_types, height=400,
                        )
                        fig_pct.update_traces(textposition="inside", textfont_size=9)
                        # Bordure rouge pour Grenoble
                        for trace in fig_pct.data:
                            ys = list(trace.y) if trace.y is not None else []
                            trace.marker.line.color = ["#FF584D" if str(y) == "Grenoble" else "rgba(0,0,0,0)" for y in ys]
                            trace.marker.line.width = [2 if str(y) == "Grenoble" else 0 for y in ys]
                        fig_pct.update_layout(
                            legend=dict(orientation="h", y=1.12, title=""),
                            xaxis_title="Part des ménages (%)", yaxis_title="", margin=dict(t=20),
                        )
                        st.plotly_chart(style(fig_pct), use_container_width=True)

                with st.expander("💡 Comment interpréter ces graphiques ?"):
                    st.write(
                        "**Distribution par taille (en haut)** : révèle si le territoire est "
                        "plutôt composé de petits foyers (urbain, vieillissant) ou de grandes "
                        "familles (périurbain). La moyenne nationale est d'environ **2,2 personnes "
                        "par ménage**.\n\n"
                        "**Volume (gauche)** : montre les besoins absolus en logements. "
                        "Utile pour les politiques d'urbanisme.\n\n"
                        "**Structure % (droite)** : neutralise l'effet taille pour comparer "
                        "deux communes de populations très différentes sur un pied d'égalité."
                    )

            # ════════════════════════════════════════════════════════════════
            # THÈME 2 — CSP DU CHEF DE MÉNAGE
            # ════════════════════════════════════════════════════════════════
            else:
                cols_csp = [c for c in df_men_csp.columns if c.startswith("Menages_")]

                # ── Agrégation CSP par territoire ────────────────────────────
                rows_csp = []
                kpi_csp = []
                for ent in selection_men:
                    df_age_ent  = get_df_age(ent)
                    df_csp_ent  = get_df_csp(ent)
                    nb_total_csp = df_csp_ent[cols_csp].sum().sum()
                    nb_men = nb_menages_depuis_age(df_age_ent)
                    pop = get_population_menages(ent)
                    ratio_str = (
                        f"{pop / nb_men:.2f} pers./ménage"
                        if nb_men > 0 and not np.isnan(pop)
                        else "N/D"
                    )
                    best_grp, best_val = "N/D", 0
                    for nom_grp, mots in CSP_GROUPES.items():
                        val = somme_colonnes(df_csp_ent, mots)
                        pct = val / nb_total_csp * 100 if nb_total_csp > 0 else 0
                        rows_csp.append({
                            "Territoire": ent,
                            "CSP": nom_grp,
                            "Nombre": int(val),
                            "Part (%)": round(pct, 1),
                        })
                        if val > best_val:
                            best_val = val
                            best_grp = nom_grp.replace("\n", " ")
                    kpi_csp.append({
                        "ent": ent,
                        "total": nb_men,
                        "dominante": best_grp,
                        "ratio": ratio_str,
                    })

                df_csp_all = pd.DataFrame(rows_csp)

                # ── KPIs ────────────────────────────────────────────────────
                st.markdown(
                    "#### Profil socio-professionnel des ménages",
                    help=(
                        "La **CSP du chef de ménage** est celle de la personne de référence "
                        "du foyer. Source : INSEE RP 2022.\n\n"
                        "**Nombre de ménages** : total des foyers du fichier Menage_age_situation.\n\n"
                        "**CSP dominante** : la catégorie qui rassemble le plus grand nombre "
                        "de ménages dans le territoire sélectionné.\n\n"
                        "**Personnes par ménage** : Population 2022 (Donnees_generales_comparatives) "
                        "/ Nombre de ménages (Menage_age_situation)."
                    ),
                )
                kpi_cols = st.columns(len(kpi_csp))
                for i, d in enumerate(kpi_csp):
                    with kpi_cols[i]:
                        st.markdown(
                            render_kpi_card(
                                d["ent"],
                                fmt(d["total"]),
                                f"Majorité : {d['dominante']}",
                                COLOR_ENT[i % len(COLOR_ENT)],
                            ),
                            unsafe_allow_html=True,
                        )

                st.markdown("---")

                # ── Graphique 1 : Structure CSP empilée ──────────────────────
                st.markdown(
                    "##### Structure socio-professionnelle des ménages (%)",
                    help=(
                        "Répartition des ménages par grande catégorie socio-professionnelle "
                        "(base 100% par territoire). Permet de comparer le profil social "
                        "de territoires de tailles très différentes.\n\n"
                        "**Cadres & Prof. sup.** : ingénieurs, médecins, enseignants du supérieur, "
                        "cadres admin. et commerciaux.\n"
                        "**Prof. intermédiaires** : infirmiers, techniciens, enseignants du 1er/2nd degré.\n"
                        "**Employés** : agents de la fonction publique, employés de commerce, "
                        "agents de sécurité.\n"
                        "**Retraités/Inactifs** : inclut les chômeurs n'ayant jamais travaillé."
                    ),
                )
                if not df_csp_all.empty:
                    ordre_csp = list(CSP_GROUPES.keys())
                    n_csp = len(ordre_csp)
                    grey_csp = [f"#{v:02x}{v:02x}{v:02x}" for v in
                                [int(0x3A + (0xE8 - 0x3A) * i / (n_csp - 1)) for i in range(n_csp)]]
                    fig_pct_csp = px.bar(
                        df_csp_all, x="Territoire", y="Part (%)", color="CSP",
                        barmode="stack", text_auto=".1f",
                        color_discrete_sequence=grey_csp,
                        category_orders={"CSP": ordre_csp}, height=420,
                    )
                    fig_pct_csp.update_traces(textposition="inside", textfont_size=9)
                    for trace in fig_pct_csp.data:
                        xs = list(trace.x) if trace.x is not None else []
                        trace.marker.line.color = ["#FF584D" if str(x) == "Grenoble" else "rgba(0,0,0,0)" for x in xs]
                        trace.marker.line.width = [2 if str(x) == "Grenoble" else 0 for x in xs]
                    fig_pct_csp.update_layout(
                        legend=dict(orientation="h", y=1.15, title=""),
                        yaxis_title="Part des ménages (%)", xaxis_title="", margin=dict(t=20),
                    )
                    st.plotly_chart(style(fig_pct_csp), use_container_width=True)

                st.markdown("---")

                # ── Graphiques 2 & 3 ────────────────────────────────────────
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(
                        "##### Volume par CSP (nombre de ménages)",
                        help=(
                            "Nombre absolu de ménages par catégorie. "
                            "Utile pour estimer les besoins en services (ex : nombre de "
                            "ménages de retraités → besoins en Ehpad, transports adaptés)."
                        ),
                    )
                    if not df_csp_all.empty:
                        fig_vol_csp = px.bar(
                            df_csp_all, x="Nombre", y="CSP", color="Territoire",
                            orientation="h", barmode="group",
                            color_discrete_sequence=COLOR_ENT,
                            category_orders={"CSP": list(CSP_GROUPES.keys())},
                            height=420,
                        )
                        fig_vol_csp.update_layout(
                            legend=dict(orientation="h", y=1.12, title=""),
                            xaxis_title="Nombre de ménages", yaxis_title="",
                            margin=dict(t=20),
                        )
                        st.plotly_chart(style(fig_vol_csp), use_container_width=True)

                with c2:
                    st.markdown(
                        "##### Taille moyenne des ménages par CSP",
                        help=(
                            "Compare la taille moyenne des ménages selon la CSP du chef de ménage. "
                            "Calcul depuis le fichier CSP×taille : "
                            "pour chaque CSP, Σ(nb_ménages_Npers × N) / Σ(nb_ménages_Npers). "
                            "Les ménages de cadres et professions intermédiaires ont souvent plus "
                            "d'enfants que les ménages d'employés, qui vivent davantage seuls."
                        ),
                    )
                    rows_taille_csp = []
                    for ent in selection_men:
                        df_csp_ent = get_df_csp(ent)
                        for nom_grp, mots in CSP_GROUPES.items():
                            total_m, total_p = 0, 0
                            for label, (nb_pers, slug) in TAILLES.items():
                                cols_filtre = [
                                    c for c in df_csp_ent.columns
                                    if slug in c and any(k in c for k in mots)
                                ]
                                nb = df_csp_ent[cols_filtre].sum().sum() if cols_filtre else 0
                                total_m += nb
                                total_p += nb * nb_pers
                            taille_grp = total_p / total_m if total_m > 0 else np.nan
                            if not np.isnan(taille_grp):
                                rows_taille_csp.append({
                                    "Territoire": ent,
                                    "CSP": nom_grp.replace("\n", " "),
                                    "Taille moyenne": round(taille_grp, 2),
                                })
                    df_taille_csp = pd.DataFrame(rows_taille_csp)
                    if not df_taille_csp.empty:
                        fig_taille_csp = px.bar(
                            df_taille_csp, x="Taille moyenne", y="CSP", color="Territoire",
                            orientation="h", barmode="group",
                            color_discrete_sequence=COLOR_ENT,
                            height=420, text_auto=".2f",
                        )
                        fig_taille_csp.update_traces(textposition="outside", textfont_size=9)
                        fig_taille_csp.update_layout(
                            legend=dict(orientation="h", y=1.12, title=""),
                            xaxis_title="Personnes par ménage (moyenne)",
                            yaxis_title="", margin=dict(t=20),
                            xaxis=dict(range=[0, 5]),
                        )
                        st.plotly_chart(style(fig_taille_csp), use_container_width=True)

                with st.expander("💡 Guide d'interprétation des CSP"):
                    st.write(
                        "La **CSP** est celle de la personne de référence du ménage (chef de ménage). "
                        "Les 7 grandes catégories regroupent les 30+ sous-catégories de l'INSEE :\n\n"
                        "- **Cadres & Prof. sup.** : ingénieurs, médecins, cadres admin./commerciaux, "
                        "artistes. Fort pouvoir d'achat, ménages souvent bi-actifs.\n"
                        "- **Prof. intermédiaires** : infirmiers, techniciens, enseignants du 1er/2nd degré, "
                        "agents de maîtrise.\n"
                        "- **Employés** : agents de la fonction publique, employés de commerce et "
                        "de services, agents de sécurité.\n"
                        "- **Ouvriers** : qualifiés et peu qualifiés, conducteurs, ouvriers agricoles.\n"
                        "- **Retraités / Inactifs** : retraités de toutes catégories + chômeurs "
                        "n'ayant jamais travaillé. Souvent la catégorie majoritaire dans les communes "
                        "vieillissantes.\n\n"
                        "**Taille moyenne par CSP** : les ménages ouvriers et agricoles ont "
                        "historiquement plus d'enfants ; les cadres ont des ménages de taille intermédiaire ; "
                        "les retraités et employés vivent plus souvent seuls ou en couple sans enfant."
                    )
                                  
# ==============================================================================
# ONGLET 5 - Population active 25-54 ans
# ==============================================================================
if vue == "Démographie":
    with tab6:

        if df_csp_new.empty or "ANNEE" not in df_csp_new.columns:
            st.info("📂 Données CSP/Diplôme non trouvées. Vérifiez les fichiers.")
        else:
            # ── Introduction Méthodologique ──────────────────────────────────
            st.markdown("""
            <div style='background-color: #f1f8f5; padding: 15px; border-radius: 10px; border-left: 5px solid #1C3A27; margin-bottom: 20px;'>
                <strong>Origine des données :</strong> Ces chiffres sont issus des recensements de l'<b>INSEE</b>. 
                Ils recensent la <b>population active de 25 à 54 ans</b>, c'est-à-dire les personnes en âge de travailler qui occupent un emploi ou en recherchent un. 
                Cette tranche d'âge est privilégiée car elle représente le cœur stable du marché du travail.
                A noter, quand vous choisissez de comparer deux territoires, un graphique d'indice de spécialisation s'affiche en plus.
            </div>
            """, unsafe_allow_html=True)

            # ── Bandeau filtres ──────────────────────────────────────────────
            with st.container():
                filter_bar("Filtres - Profil des actifs (25-54 ans)")
                
                csp_geo_l, csp_geo_r = st.columns([1, 3])
                with csp_geo_l:
                    filter_row_label("Niveau géographique")
                with csp_geo_r:
                    mode_analyse = st.radio("",
                        ["Comparaison Métropoles", "Comparaison communes métropole de Grenoble"],
                        key="csp_mode", horizontal=True,
                        help="Choisissez de comparer les grandes métropoles entre elles ou de zoomer sur les communes de la métropole grenobloise.")

                csp_row1_c1, csp_row1_c2 = st.columns(2)
                with csp_row1_c1:
                    theme_analyse = st.selectbox(
                        "Thématique",
                        ["Secteurs d'activité (CSP)", "Niveau de diplôme"],
                        key="csp_theme",
                        help="Secteurs d'activité (CSP) : catégories socio-professionnelles. Niveau de diplôme : niveau d'études atteint."
                    )
                
                current_df_csp  = df_csp_new if theme_analyse == "Secteurs d'activité (CSP)" else df_dip_new
                current_map_csp = CSP_MAP_NEW if theme_analyse == "Secteurs d'activité (CSP)" else DIP_MAP

                annees_csp = sorted(current_df_csp["ANNEE"].dropna().unique(), reverse=True) if not current_df_csp.empty else []
                with csp_row1_c2:
                    sel_annee_csp = st.selectbox("Année", annees_csp, key="csp_annee", 
                                                 help="Sélectionnez l'année de référence du recensement.") if annees_csp else None

                if mode_analyse == "Comparaison communes métropole de Grenoble":
                    clist = sorted(COMMUNES["Grenoble"])
                    sel_communes_csp = st.multiselect("Commune de la métropole de Grenoble", clist, default=["Grenoble", "Meylan"], 
                                                     key="csp_communes", help="Sélectionnez les communes à analyser.")
                    entities_names = sel_communes_csp
                else:
                    sel_metros_csp = st.multiselect("Métropoles", TOUTES, default=["Grenoble", "Rouen"], 
                                                   key="csp_metros", help="Sélectionnez les métropoles à comparer.")
                    entities_names = sel_metros_csp

                sel_cats = st.multiselect("Catégories à afficher",
                                          options=list(current_map_csp.values()),
                                          default=list(current_map_csp.values()),
                                          key="csp_cats",
                                          help="Filtrez les catégories pour simplifier la lecture des graphiques.")

            # ── Logique de calcul ───────────────────────────────────────────
            if sel_annee_csp:
                df_year_csp = current_df_csp[current_df_csp["ANNEE"] == sel_annee_csp]
                entities_csp = []

                for name in entities_names:
                    if mode_analyse == "Comparaison communes métropole de Grenoble":
                        subset = df_year_csp[(df_year_csp["LIB_NORM"] == normalize_name(name)) & (df_year_csp["DEP"] == "38")]
                        if not subset.empty:
                            entities_csp.append({"name": name, "data": subset.iloc[0]})
                    else:
                        dep = DEP_MAP[name]
                        norms = [normalize_name(c) for c in COMMUNES[name]]
                        subset = df_year_csp[(df_year_csp["DEP"] == dep) & (df_year_csp["LIB_NORM"].isin(norms))]
                        if not subset.empty:
                            agg = subset[list(current_map_csp.values())].sum()
                            entities_csp.append({"name": name, "data": agg})

                if entities_csp and sel_cats:
                    st.markdown("---")
                    
                    # ── INDICATEURS (KPI) ────────────────────
                    kpi_cols_csp = st.columns(len(entities_csp))
                    for i, entity in enumerate(entities_csp):
                        total_actifs = entity["data"][sel_cats].sum()
                        val_formatee = f"{int(total_actifs):,d}".replace(",", " ")
                        kpi_color5 = COULEURS.get(entity['name'], "#888888")
                        with kpi_cols_csp[i]:
                            st.markdown(f"""
                            <div style='display: flex; flex-direction: row; align-items: stretch; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 6px rgba(0,0,0,0.1); background: #fff; min-height: 80px; border-left: 6px solid {kpi_color5};'>
                                <div style='padding: 10px 16px; display: flex; flex-direction: column; justify-content: center;'>
                                    <div style='font-size:11px; font-weight:700; letter-spacing:0.08em; color:#666; text-transform:uppercase;'>{entity['name']}</div>
                                    <div style='font-size:24px; font-weight:bold; color:#111;'>{val_formatee}</div>
                                    <div style='color:{kpi_color5}; font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.05em;'>Actifs 25-54 ans</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                    # ── Graphiques de base ───────────────────────────────────
                    c1, c2 = st.columns(2)
                    with c1:
                        st.subheader("Répartition en volume", help="Nombre réel de personnes par catégorie.")
                        fig_bar_csp = go.Figure()
                        for ent in entities_csp:
                            ent_color = COULEURS.get(ent["name"], "#888888")
                            is_greno = ent["name"] == "Grenoble"
                            fig_bar_csp.add_trace(go.Bar(
                                x=sel_cats, y=ent["data"][sel_cats],
                                name=ent["name"],
                                marker_color=ent_color,
                                marker_line_color="#FF584D" if is_greno else "rgba(0,0,0,0)",
                                marker_line_width=2 if is_greno else 0,
                                hovertemplate="<b>Territoire : " + ent["name"] + "</b><br>%{x} : %{y:.2s}<extra></extra>",
                            ))
                        fig_bar_csp.update_layout(barmode="group", height=400, margin=dict(t=20, b=20))
                        st.plotly_chart(fig_bar_csp, use_container_width=True)

                    with c2:
                        st.subheader("Profil structurel (%)", help="Part relative de chaque catégorie.")
                        fig_radar_csp = go.Figure()
                        for ent in entities_csp:
                            v = ent["data"][sel_cats]
                            pct = (v / v.sum() * 100).fillna(0)
                            fig_radar_csp.add_trace(go.Scatterpolar(
                                r=list(pct) + [pct.iloc[0]],
                                theta=sel_cats + [sel_cats[0]],
                                fill="toself", name=ent["name"],
                                line_color=COULEURS.get(ent["name"], "#888"),
                                hovertemplate="<b>Territoire : " + ent["name"] + "</b><br>%{theta} : %{r:.2f}%<extra></extra>",
                            ))
                        fig_radar_csp.update_layout(height=400, margin=dict(t=50, b=50))
                        st.plotly_chart(fig_radar_csp, use_container_width=True)

                    # ── INDICE DE SPÉCIALISATION (Si 2 entités) ──────────────
                    if len(entities_csp) == 2:
                        t1_name = entities_names[0]
                        t2_name = entities_names[1]
                        
                        st.markdown("---")
                        st.markdown(f"### 🎯 Guide de lecture : Spécialisation du Territoire 1 ({t1_name}) face au Territoire 2 ({t2_name})")
                        
                        st.markdown(f"""
                        <div style='background-color: #f8f9fa; padding: 18px; border-radius: 8px; border: 1px solid #e0e0e0; margin-bottom: 20px;'>
                            <h5 style='margin-top:0;'>💡 Comment lire ce graphique et ce tableau ?</h5>
                            <p style='font-size: 14px;'>L'indice compare si une catégorie est plus ou moins présente en <b>proportion</b> dans le Territoire 1 par rapport au Territoire 2.</p>
                            <ul style='font-size: 14px;'>
                                <li><b>Indice > 100 :</b> La catégorie est <b>surreprésentée</b> dans le Territoire 1 ({t1_name}). Elle y pèse plus lourd qu'ailleurs.</li>
                                <li><b>Indice = 100 :</b> Équilibre parfait. La catégorie a le même poids relatif dans les deux zones.</li>
                                <li><b>Indice < 100 :</b> La catégorie est <b>sous-représentée</b> dans le Territoire 1. Cela signifie qu'elle est proportionnellement plus importante dans le Territoire 2 ({t2_name}).</li>
                            </ul>
                            <p style='font-size: 14px;'><b>Important :</b> Ne regardez pas que l'indice ! Une forte surreprésentation sur un petit nombre de personnes (voir colonne <i>Eff.</i> du tableau) a moins d'impact qu'une légère spécialisation sur des milliers d'actifs.</p>
                        </div>
                        """, unsafe_allow_html=True)

                        v1, v2 = entities_csp[0]["data"][sel_cats], entities_csp[1]["data"][sel_cats]
                        t1_total, t2_total = v1.sum(), v2.sum()
                        spec = ((v1 / t1_total) / (v2 / t2_total) * 100).fillna(100)

                        fig_spec = px.bar(x=sel_cats, y=spec, color=spec, color_continuous_scale="RdYlGn", 
                                          title=f"Spécialisation : {t1_name} / {t2_name}")
                        fig_spec.add_hline(y=100, line_dash="dash", line_color="black")
                        fig_spec.update_layout(height=450, coloraxis_showscale=False, yaxis_title="Indice (Base 100)")
                        st.plotly_chart(fig_spec, use_container_width=True)

                        with st.expander("📊 Voir le tableau récapitulatif (Effectifs et Indice)", expanded=True):
                            table_df = pd.DataFrame({
                                "Catégorie": sel_cats,
                                f"{t1_name} (Territoire 1 - Eff.)": [f"{int(v1[c]):,d}".replace(",", " ") for c in sel_cats],
                                f"{t2_name} (Territoire 2 - Eff.)": [f"{int(v2[c]):,d}".replace(",", " ") for c in sel_cats],
                                "Indice spécialisation": [int(spec[c]) for c in sel_cats],
                            })
                            st.dataframe(table_df.set_index("Catégorie"), use_container_width=True)
# ==============================================================================
# SOLIDARITÉ & CITOYENNETÉ
# ==============================================================================
if vue == "Solidarité et citoyenneté":
    st.markdown('<p class="section-header">Solidarité & citoyenneté</p>', unsafe_allow_html=True)
    s1, s2, s3, s4, s5 = st.tabs(["🤝 Solidarité", "🎓 Éducation", "🏥 Santé", "🗳️ Participation", "💶 Revenus & pauvreté"])

    # --- Fonction utilitaire locale pour harmoniser les cartes KPI ---
    def render_solidarite_kpi(title, value, subtitle, border_color="#1e5631"):
        return f"""
        <div style='display: flex; flex-direction: row; align-items: stretch; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 6px rgba(0,0,0,0.1); background: #fff; min-height: 80px; border-left: 6px solid {border_color}; margin-bottom: 10px;'>
            <div style='padding: 10px 16px; display: flex; flex-direction: column; justify-content: center; width: 100%;'>
                <div style='font-size:11px; font-weight:700; letter-spacing:0.08em; color:#666; text-transform:uppercase;'>{title}</div>
                <div style='font-size:24px; font-weight:bold; color:#111; margin: 2px 0;'>{value}</div>
                <div style='color:{border_color}; font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:0.05em;'>{subtitle}</div>
            </div>
        </div>
        """

    # ──────────────────────────────────────────────────────────────────────────
    # ONGLET 1 - SOLIDARITÉ (CAF)
    # ──────────────────────────────────────────────────────────────────────────
    with s1:
        if df_caf is None or df_caf.empty:
            st.info("📂 Fichier `CAF_5_Metropoles.csv` introuvable.")
        else:
            required_cols = {"Annee", "Agglomeration"}
            if not required_cols.issubset(set(df_caf.columns)):
                st.error("Colonnes Annee / Agglomeration manquantes.")
            else:
                ALL_METRIC_LABELS = {
                    "Nombre foyers NDUR": "Foyers aidés (toutes aides)",
                    "Nombre personnes NDUR": "Personnes concernées (toutes aides)",
                    "Montant total NDUR": "Montant total versé (€)",
                    "Nombre foyers NDURPAJE": "Foyers aidés – Jeunes enfants",
                    "Nombre personnes NDURPAJE": "Personnes concernées – Jeunes enfants",
                    "Montant total NDURPAJE": "Montant versé – Jeunes enfants (€)",
                    "Nombre foyers NDUREJ": "Foyers aidés – Enfance & jeunesse",
                    "Nombre personnes NDUREJ": "Personnes concernées – Enfance & jeunesse",
                    "Montant total NDUREJ": "Montant versé – Enfance & jeunesse (€)",
                    "Nombre foyers NDURAL": "Foyers aidés – Logement",
                    "Nombre personnes NDURAL": "Personnes concernées – Logement",
                    "Montant total NDURAL": "Montant versé – Logement (€)",
                    "Nombre foyers NDURINS": "Foyers aidés – Insertion",
                    "Nombre personnes NDURINS": "Personnes concernées – Insertion",
                    "Montant total NDURINS": "Montant versé – Insertion (€)",
                }
                available_metrics = {k: v for k, v in ALL_METRIC_LABELS.items() if k in df_caf.columns}
                if not available_metrics:
                    st.warning("Aucune mesure CAF trouvée.")
                else:
                    for col in available_metrics:
                        df_caf[col] = pd.to_numeric(df_caf[col], errors="coerce").fillna(0)
                    years_caf  = sorted(df_caf["Annee"].dropna().unique())
                    agglos_caf = sorted(df_caf["Agglomeration"].dropna().unique())
                    gre_agglo = next((a for a in agglos_caf if "Grenoble" in a), "Grenoble Alpes Métropole")

                    # ── Filtres ──
                    with st.container():
                        filter_bar("Filtres - Solidarité CAF")
                        f1, f2 = st.columns([1, 3])
                        with f1:
                            filter_row_label("Niveau géographique")
                        with f2:
                            mode_caf = st.radio(
                                "", ["Comparaison Métropoles", "Détail Communal"], 
                                key="caf_mode", horizontal=True, label_visibility="collapsed"
                            )

                        if mode_caf == "Comparaison Métropoles":
                            sel_entites_caf = st.multiselect("Métropoles à comparer", agglos_caf, default=agglos_caf, key="caf_agglos")
                        else:
                            communes_gre_caf = sorted(df_caf[df_caf["Agglomeration"] == gre_agglo]["Nom_Commune"].dropna().unique()) if "Nom_Commune" in df_caf.columns else []
                            sel_entites_caf = st.multiselect("Communes de Grenoble", communes_gre_caf, default=communes_gre_caf[:5] if communes_gre_caf else [], key="caf_communes")

                        c1, c2 = st.columns(2)
                        with c1:
                            metric_key = st.selectbox("Indicateur", list(available_metrics.keys()), format_func=lambda k: available_metrics[k], index=0, key="caf_metric")
                        with c2:
                            year_caf = st.selectbox("Année", years_caf, index=len(years_caf)-1, key="caf_year")
                        st.markdown('</div>', unsafe_allow_html=True)

                    # ── Filtrage ──
                    geo_col = "Agglomeration" if mode_caf == "Comparaison Métropoles" else "Nom_Commune"
                    is_metro = (mode_caf == "Comparaison Métropoles")
                    
                    df_fil = df_caf[df_caf["Annee"] == year_caf]
                    if is_metro:
                        df_fil = df_fil[df_fil["Agglomeration"].isin(sel_entites_caf)]
                    else:
                        df_fil = df_fil[(df_fil["Agglomeration"] == gre_agglo) & (df_fil["Nom_Commune"].isin(sel_entites_caf))]

                    st.markdown("---")

                    if df_fil.empty or not sel_entites_caf:
                        st.warning("⚠️ Aucune donnée pour les filtres sélectionnés.")
                    else:
                        label_metric = available_metrics[metric_key]
                        total_val = df_fil[metric_key].sum()
                        nb_entites = df_fil[geo_col].nunique()
                        max_entite = df_fil.groupby(geo_col)[metric_key].sum().idxmax()
                        
                        # ── KPIs ──
                        st.markdown(f"#### Synthèse des allocations - {year_caf}")
                        k1, k2, k3 = st.columns(3)
                        kpi_border_color = "#666" if is_metro else "#1e5631"

                        with k1:
                            suffix = " €" if "Montant" in metric_key else ""
                            st.markdown(render_solidarite_kpi(f"Total ({year_caf})", fmt(total_val, suffix=suffix), label_metric, kpi_border_color), unsafe_allow_html=True)
                        with k2:
                            st.markdown(render_solidarite_kpi("Périmètre", fmt(nb_entites), "Unités comparées", kpi_border_color), unsafe_allow_html=True)
                        with k3:
                            st.markdown(render_solidarite_kpi("Top Territoire", max_entite, "Volume le plus élevé", kpi_border_color), unsafe_allow_html=True)

                        st.markdown("---")

                        # ── Graphiques ──
                        c1, c2 = st.columns(2)
                        PALETTE_METRO = px.colors.sequential.Greys[2:]
                        PALETTE_COMMUNE = px.colors.sequential.Greens_r
                        color_map = COULEURS if is_metro else None
                        color_seq = PALETTE_METRO if is_metro else PALETTE_COMMUNE
                        color_group = "Metropole_Key" if is_metro else geo_col

                        if is_metro:
                            df_fil["Metropole_Key"] = df_fil["Agglomeration"].apply(lambda x: next((m for m in COULEURS.keys() if m in x), x))

                        with c1:
                            st.markdown(f"##### Quotient familial ({year_caf})", help="Répartition des foyers bénéficiaires selon leur tranche de revenus (Quotient Familial CAF).")
                            if "Quotient familial" in df_fil.columns:
                                qf_order = ["Moins de 400 euros", "Entre 400 et 799 euros", "Entre 800 et 1199 euros", "Entre 1200 et 1599 euros", "Entre 1600 et 1999 euros", "Entre 2000 et 3999 euros", "4000 euros ou plus", "Inconnu"]
                                qf_data = df_fil.groupby([geo_col, "Quotient familial"], as_index=False)[metric_key].sum()
                                qf_data["QF_ord"] = pd.Categorical(qf_data["Quotient familial"], categories=qf_order, ordered=True)
                                order_x = qf_data.groupby(geo_col)[metric_key].sum().sort_values(ascending=False).index.tolist()
                                
                                if is_metro:
                                    n_tranches = len(qf_order)
                                    grey_shades = [f"#{v:02x}{v:02x}{v:02x}" for v in [int(0x77 + (220 - 0x77) * i / (n_tranches - 1)) for i in range(n_tranches)]]
                                    qf_color_map = {tranche: grey_shades[j] for j, tranche in enumerate(qf_order)}
                                    
                                    fig_qf = px.bar(qf_data.sort_values("QF_ord"), x=geo_col, y=metric_key, color="Quotient familial", color_discrete_map=qf_color_map, barmode="stack", labels={geo_col: "", metric_key: label_metric}, height=380)
                                    
                                    grenoble_agglo = next((a for a in qf_data[geo_col].unique() if "Grenoble" in a), None)
                                    if grenoble_agglo:
                                        for trace in fig_qf.data:
                                            marker_colors = ["#FF584D" if str(agg) == str(grenoble_agglo) else "#000000" for agg in (trace.x if trace.x is not None else [])]
                                            marker_widths = [1 if str(agg) == str(grenoble_agglo) else 0 for agg in (trace.x if trace.x is not None else [])]
                                            if marker_colors:
                                                trace.marker.line.color = marker_colors
                                                trace.marker.line.width = marker_widths
                                else:
                                    fig_qf = px.bar(qf_data.sort_values("QF_ord"), x=geo_col, y=metric_key, color="Quotient familial", color_discrete_sequence=color_seq, barmode="stack", labels={geo_col: "", metric_key: label_metric}, height=380)
                                    fig_qf.update_traces(marker_line_width=0)
                                    
                                fig_qf.update_traces(
                                    hovertemplate="<b>%{x}</b><br>" + label_metric + " : <b>%{y:,.0f}</b><extra></extra>"
                                )
                                fig_qf.update_layout(
                                    separators=", ",
                                    xaxis=dict(
                                        categoryorder='array',
                                        categoryarray=order_x,
                                        tickangle=-30,
                                        title=""
                                    ),
                                    legend=dict(
                                        orientation="v",
                                        yanchor="middle",
                                        y=0.5,
                                        xanchor="left",
                                        x=1.02,
                                        title=""
                                    ),
                                    margin=dict(t=40, r=140, b=80)
                                )
                                st.plotly_chart(style(fig_qf, 40), use_container_width=True)

                                with c2:
                                    st.markdown(f"##### Classement des territoires", help="Volume total pour l'indicateur sélectionné.")
                                    
                                    top_ent = df_fil.groupby(geo_col, as_index=False)[metric_key].sum().sort_values(by=metric_key, ascending=True if not is_metro else False)
                                    top_ent["text_display"] = top_ent[metric_key].apply(lambda x: fmt(x, suffix=" €" if "Montant" in metric_key else ""))

                                    if is_metro:
                                        top_ent["Metropole_Key"] = top_ent[geo_col].apply(lambda x: next((m for m in COULEURS.keys() if m in x), x))
                                        fig_top = px.bar(
                                            top_ent,
                                            x=metric_key,
                                            y=geo_col,
                                            orientation="h",
                                            color="Metropole_Key",
                                            color_discrete_map=COULEURS,
                                            text="text_display",
                                            labels={geo_col: "", metric_key: label_metric},
                                            height=380
                                        )
                                    else:
                                        fig_top = px.bar(
                                            top_ent,
                                            x=metric_key,
                                            y=geo_col,
                                            orientation="h",
                                            color=geo_col,
                                            color_discrete_sequence=PALETTE_COMMUNE,
                                            text="text_display",
                                            labels={geo_col: "", metric_key: label_metric},
                                            height=380
                                        )
                                    fig_top.update_traces(
                                        textposition="inside",
                                        insidetextanchor="end",
                                        hovertemplate="<b>%{y}</b><br>" + label_metric + " : <b>%{text}</b><extra></extra>"
                                    )
                                    fig_top.update_layout(
                                        yaxis={"categoryorder": "total ascending"},
                                        showlegend=False,
                                        margin=dict(t=20, b=20, l=10, r=10)
                                    )
                                    st.plotly_chart(style(fig_top, 40), use_container_width=True)

                        # ── Bloc de comparaison mis à jour ──
                        INDICATEURS_GLOBAUX = ["Nombre foyers NDUR", "Nombre personnes NDUR", "Montant total NDUR"]
                        if metric_key in INDICATEURS_GLOBAUX:
                            st.markdown("---")
                            st.markdown(f"##### Structure détaillée de la solidarité", help="Répartition du total sélectionné par grandes catégories d'allocations.")

                            current_root = metric_key.split("NDUR")[0] 
                            aides_full_map = {
                                "Insertion (RSA, AAH...)": current_root + "NDURINS",
                                "Logement (APL, ALS...)": current_root + "NDURAL",
                                "Jeunes enfants (PAJE)": current_root + "NDURPAJE",
                                "Enfance & Jeunesse": current_root + "NDUREJ"
                            }
                            aides_d = {label: col for label, col in aides_full_map.items() if col in df_fil.columns}

                            if aides_d:
                                bdata = df_fil.groupby(geo_col, as_index=False)[list(aides_d.values())].sum()
                                if is_metro:
                                    bdata["Metropole_Key"] = bdata[geo_col].apply(lambda x: next((m for m in COULEURS.keys() if m in x), x))
                                
                                bdata = bdata.rename(columns={v: k for k, v in aides_d.items()})
                                bdata_long = bdata.melt(
                                    id_vars=[geo_col] + (["Metropole_Key"] if is_metro else []),
                                    value_vars=list(aides_d.keys()),
                                    var_name="Type d'aide",
                                    value_name="Valeur"
                                )
                                
                                # Correction text_auto : ,.0f affiche l'entier avec le séparateur défini dans le layout
                                fig_bar_comp = px.bar(
                                    bdata_long, x="Valeur", y="Type d'aide", color=color_group,
                                    color_discrete_map=color_map, color_discrete_sequence=color_seq,
                                    barmode="group", orientation="h", text_auto=",.0f",
                                    labels={"Valeur": "Volume", "Type d'aide": "", color_group: "Territoire"}, height=450
                                )

                                # Correction infobulle : ,.0f pour utiliser le séparateur d'espace
                                fig_bar_comp.update_traces(
                                    hovertemplate="<b>%{y}</b><br>Volume : <b>%{x:,.0f}</b><extra></extra>"
                                )

                                # Bordure Orange spécifique pour Grenoble
                                if is_metro:
                                    for trace in fig_bar_comp.data:
                                        if "Grenoble" in trace.name:
                                            trace.marker.line.width = 2
                                            trace.marker.line.color = "#FF584D"

                                # LE RÉGLAGE CLÉ : separators=", " (virgule puis ESPACE)
                                fig_bar_comp.update_layout(
                                    separators=", ", 
                                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0), 
                                    margin=dict(t=80, b=40, l=150), 
                                    yaxis={"categoryorder": "total ascending"}
                                )
                                
                                st.plotly_chart(style(fig_bar_comp, 40), use_container_width=True)

                        with st.expander("Note méthodologique"):
                            st.markdown("""
                                        - **Foyers aidés** : ménages percevant au moins une aide CAF  
                                        - **Personnes concernées** : individus vivant dans ces foyers  
                                        - **Montants (€)** : total des aides versées  
                                        - **Quotient familial** : niveau de vie du foyer (revenus / parts)
                                        - **Logement** : APL, ALS, ALF  
                                        - **Insertion** : RSA, AAH, prime d'activité  
                                        - **Jeunes enfants (PAJE)** : naissance, garde, petite enfance  
                                        - **Enfance & jeunesse** : allocations familiales, rentrée scolaire
                                        """)

    # ──────────────────────────────────────────────────────────────────────────
    # ONGLET 2 - ÉDUCATION (Effectifs Étudiants)
    # ──────────────────────────────────────────────────────────────────────────
    with s2:
        if df_eff is None or df_eff.empty:
            st.info("📂 Fichier `effectifs_5_villes.csv` introuvable.")
        else:
            df_eff_w      = df_eff.copy()
            annees_eff    = sorted(df_eff_w["annee"].dropna().unique().astype(int))
            metros_eff    = sorted(df_eff_w["metropole"].dropna().unique())
            LABEL_REGROUPEMENT = {"TOTAL":"Toutes formations","UNIV":"Universités","STS":"STS & assimilés","CPGE":"CPGE","GE":"Grandes Écoles","ING_autres":"Écoles d'ingénieurs","EC_COM":"Écoles de commerce","EC_ART":"Écoles d'art","EC_JUR":"Écoles juridiques","EC_PARAM":"Écoles paramédicales","EC_autres":"Autres écoles","INP":"INP","EPEU":"EPEU","ENS":"ENS","IUFM":"IUFM / INSPE"}
            regroupements_dispo = sorted(df_eff_w["regroupement"].dropna().unique())

            # ── Filtres ──
            with st.container():
                filter_bar("Filtres - Effectifs enseignement supérieur")
                f1, f2 = st.columns([1, 3])
                with f1:
                    filter_row_label("Niveau géographique")
                with f2:
                    mode_eff = st.radio(
                        "", ["Comparaison Métropoles", "Détail Communal"], 
                        key="eff_mode", horizontal=True, label_visibility="collapsed"
                    )
                
                if mode_eff == "Comparaison Métropoles":
                    sel_entites_eff = st.multiselect("Métropoles à comparer", metros_eff, default=metros_eff, key="eff_metros")
                else:
                    communes_gre_eff = sorted(df_eff_w[df_eff_w["metropole"] == "Grenoble"]["geo_nom"].dropna().unique())
                    sel_entites_eff = st.multiselect("Communes de Grenoble", communes_gre_eff, default=communes_gre_eff[:5] if communes_gre_eff else [], key="eff_communes")
                
                c1, c2, c3 = st.columns([1, 1, 1])
                with c1:
                    annee_eff = st.selectbox("Année", annees_eff, index=len(annees_eff)-1, key="eff_annee")
                with c2:
                    regr_choices = ["TOTAL"] + [r for r in regroupements_dispo if r != "TOTAL"]
                    sel_regr = st.selectbox("Type d'établissement", regr_choices, format_func=lambda r: LABEL_REGROUPEMENT.get(r, r), index=0, key="eff_regr")
                with c3:
                    sel_secteur = st.selectbox("Secteur", ["Tous","Établissements publics","Établissements privés"], key="eff_secteur")
                st.markdown('</div>', unsafe_allow_html=True)

            # ── Filtrage ──
            geo_col = "metropole" if mode_eff == "Comparaison Métropoles" else "geo_nom"
            is_metro = (mode_eff == "Comparaison Métropoles")

            df_e = df_eff_w[df_eff_w["regroupement"] == sel_regr]
            if sel_secteur != "Tous":
                df_e = df_e[df_e["secteur_de_l_etablissement"] == sel_secteur]

            if is_metro:
                df_e = df_e[df_e["metropole"].isin(sel_entites_eff)]
            else:
                df_e = df_e[(df_e["metropole"] == "Grenoble") & (df_e["geo_nom"].isin(sel_entites_eff))]
                
            df_e_yr = df_e[df_e["annee"] == annee_eff]

            st.markdown("---")

            if df_e_yr.empty or not sel_entites_eff:
                st.warning("⚠️ Aucune donnée pour les filtres sélectionnés.")
            else:
                # ── KPIs ──
                # CORRECTION : total_eff au lieu de total_val
                total_eff   = int(df_e_yr["effectif"].sum())
                nb_entites  = int(df_e_yr[geo_col].nunique())
                max_entite  = df_e_yr.groupby(geo_col)["effectif"].sum().idxmax()
                kpi_border_color = "#666" if is_metro else "#1e5631"
                
                st.markdown(f"#### Synthèse des effectifs étudiants - {annee_eff}")
                k1, k2, k3 = st.columns(3)
                with k1:
                    st.markdown(render_solidarite_kpi(f"Effectif total", fmt(total_eff), "Étudiants inscrits", kpi_border_color), unsafe_allow_html=True)
                with k2:
                    st.markdown(render_solidarite_kpi("Périmètre", fmt(nb_entites), "Unités comparées", kpi_border_color), unsafe_allow_html=True)
                with k3:
                    st.markdown(render_solidarite_kpi("Top Territoire", max_entite, "Volume le plus élevé", kpi_border_color), unsafe_allow_html=True)
                        
                st.markdown("---")

                # ── Graphiques ──
                PALETTE_METRO = px.colors.sequential.Greys[2:]
                PALETTE_COMMUNE = px.colors.sequential.Greens_r
                color_map = COULEURS if is_metro else None
                color_seq = PALETTE_METRO if is_metro else PALETTE_COMMUNE

                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"##### Volume d'étudiants ({annee_eff})", help="Nombre absolu d'étudiants inscrits selon les filières et secteurs sélectionnés.")
                    by_entite = df_e_yr.groupby(geo_col, as_index=False)["effectif"].sum().sort_values("effectif", ascending=False)
                    by_entite["text_display"] = by_entite["effectif"].apply(lambda x: fmt(x))
                    fig_bar = px.bar(by_entite, x=geo_col, y="effectif", color=geo_col, color_discrete_map=color_map, color_discrete_sequence=color_seq, text="text_display", labels={geo_col:"", "effectif":"Étudiants"}, height=380)
                    fig_bar.update_traces(
                        textposition="outside",
                        hovertemplate="<b>%{x}</b><br>Étudiants : <b>%{text}</b><extra></extra>"
                    )
                    fig_bar.update_layout(showlegend=False)
                    st.plotly_chart(style(fig_bar, 40), use_container_width=True)
                    
                with c2:
                    st.markdown("##### Évolution des effectifs", help="Tendance d'évolution du nombre d'étudiants sur l'ensemble des années disponibles.")
                    evo_e = df_e.groupby(["annee", geo_col], as_index=False)["effectif"].sum().sort_values("annee")
                    evo_e["effectif_fmt"] = evo_e["effectif"].apply(lambda x: f"{int(x):,}".replace(",", " "))
                    fig_line = px.line(evo_e, x="annee", y="effectif", color=geo_col, color_discrete_map=color_map, color_discrete_sequence=color_seq, markers=True, labels={"annee":"Année", "effectif":"Étudiants", geo_col:"Territoire"}, height=380)
                    fig_line.update_traces(
                        customdata=evo_e["effectif_fmt"],
                        line_width=2.5,
                        marker_size=7,
                        hovertemplate=
                        "<b>%{fullData.name}</b><br>" +
                        "Année : <b>%{x}</b><br>" +
                        "Étudiants : <b>%{customdata}</b>" +
                        "<extra></extra>"
                    )
                    y_max = evo_e["effectif"].max()
                    fig_line.update_yaxes(
                        range=[0, y_max * 1.1]
                    )
                    st.plotly_chart(style(fig_line, 40), use_container_width=True)
                    
                st.markdown("---")

                c3, c4 = st.columns(2)
                with c3:
                    st.markdown(f"##### Public vs Privé ({annee_eff})", help="Proportion d'étudiants inscrits dans le public par rapport au privé.")
                    if "secteur_de_l_etablissement" in df_e_yr.columns:
                        sec_agg = df_e_yr.groupby([geo_col, "secteur_de_l_etablissement"], as_index=False)["effectif"].sum()
                        sec_agg["text_display"] = sec_agg["effectif"].apply(lambda x: fmt(x))
                        order_sec = sec_agg.groupby(geo_col)["effectif"].sum().sort_values(ascending=False).index.tolist()

                        secteurs = sorted(sec_agg["secteur_de_l_etablissement"].dropna().unique())
                        n_secteurs = len(secteurs)

                        if is_metro:
                            grey_shades_sec = [f"#{v:02x}{v:02x}{v:02x}" for v in [int(0x77 + (220 - 0x77) * i / max(n_secteurs - 1, 1)) for i in range(n_secteurs)]]
                            sec_color_map = {s: grey_shades_sec[j] for j, s in enumerate(secteurs)}

                            fig_sec = px.bar(sec_agg, x=geo_col, y="effectif", color="secteur_de_l_etablissement", barmode="stack",
                                color_discrete_map=sec_color_map,
                                text="text_display", labels={geo_col:"", "effectif":"Étudiants", "secteur_de_l_etablissement":"Secteur"}, height=400)
                            grenoble_agglo = next((a for a in sec_agg[geo_col].unique() if "Grenoble" in a), None)
                            if grenoble_agglo:
                                for trace in fig_sec.data:
                                    marker_colors = ["#FF584D" if str(x) == str(grenoble_agglo) else "#000000" for x in (trace.x if trace.x is not None else [])]
                                    marker_widths = [1 if str(x) == str(grenoble_agglo) else 0 for x in (trace.x if trace.x is not None else [])]
                                    if marker_colors:
                                        trace.marker.line.color = marker_colors
                                        trace.marker.line.width = marker_widths
                        else:
                            fig_sec = px.bar(sec_agg, x=geo_col, y="effectif", color="secteur_de_l_etablissement", barmode="stack",
                                color_discrete_map={"Établissements publics": "#2D6A4F", "Établissements privés": "#95D5B2"},
                                text="text_display", labels={geo_col:"", "effectif":"Étudiants", "secteur_de_l_etablissement":"Secteur"}, height=400)
                            fig_sec.update_traces(marker_line_width=0)

                        fig_sec.update_traces(
                            hovertemplate="<b>%{x}</b><br>%{fullData.name} : <b>%{text}</b><extra></extra>"
                        )
                        fig_sec.update_layout(
                            xaxis=dict(categoryorder="array", categoryarray=order_sec),
                            legend=dict(orientation="h", y=1.1)
                        )
                        st.plotly_chart(style(fig_sec, 40), use_container_width=True)

                with c4:
                    st.markdown(f"##### Parité Femmes / Hommes ({annee_eff})", help="Répartition par genre des étudiants inscrits.")
                    if "sexe_de_l_etudiant" in df_e_yr.columns:
                        sex_agg = df_e_yr.groupby([geo_col, "sexe_de_l_etudiant"], as_index=False)["effectif"].sum()
                        sex_agg["text_display"] = sex_agg["effectif"].apply(lambda x: fmt(x))
                        order_sex = sex_agg.groupby(geo_col)["effectif"].sum().sort_values(ascending=False).index.tolist()

                        genres = sorted(sex_agg["sexe_de_l_etudiant"].dropna().unique())
                        n_genres = len(genres)

                        if is_metro:
                            grey_shades_sex = [f"#{v:02x}{v:02x}{v:02x}" for v in [int(0x77 + (220 - 0x77) * i / max(n_genres - 1, 1)) for i in range(n_genres)]]
                            sex_color_map = {g: grey_shades_sex[j] for j, g in enumerate(genres)}

                            fig_sex = px.bar(sex_agg, x=geo_col, y="effectif", color="sexe_de_l_etudiant", barmode="group",
                                color_discrete_map=sex_color_map,
                                text="text_display", labels={geo_col:"", "effectif":"Étudiants", "sexe_de_l_etudiant":"Genre"}, height=400)
                            grenoble_agglo = next((a for a in sex_agg[geo_col].unique() if "Grenoble" in a), None)
                            if grenoble_agglo:
                                for trace in fig_sex.data:
                                    marker_colors = ["#FF584D" if str(x) == str(grenoble_agglo) else "#000000" for x in (trace.x if trace.x is not None else [])]
                                    marker_widths = [1 if str(x) == str(grenoble_agglo) else 0 for x in (trace.x if trace.x is not None else [])]
                                    if marker_colors:
                                        trace.marker.line.color = marker_colors
                                        trace.marker.line.width = marker_widths
                        else:
                            fig_sex = px.bar(sex_agg, x=geo_col, y="effectif", color="sexe_de_l_etudiant", barmode="group",
                                color_discrete_map={"Masculin": "#2D6A4F", "Feminin": "#95D5B2"},
                                text="text_display", labels={geo_col:"", "effectif":"Étudiants", "sexe_de_l_etudiant":"Genre"}, height=400)
                            fig_sex.update_traces(marker_line_width=0)

                        fig_sex.update_traces(
                            hovertemplate="<b>%{x}</b><br>%{fullData.name} : <b>%{text}</b><extra></extra>"
                        )
                        fig_sex.update_layout(
                            xaxis=dict(categoryorder="array", categoryarray=order_sex),
                            legend=dict(orientation="h", y=1.1)
                        )
                        st.plotly_chart(style(fig_sex, 40), use_container_width=True)

                st.markdown("---")
                
                with st.expander("Note méthodologique"):
                    st.markdown("""
                                * **CPGE** : Classes Préparatoires aux Grandes Écoles.
                                * **STS** : Sections de Techniciens Supérieurs (BTS).
                                """)

    # ──────────────────────────────────────────────────────────────────────────
    # ONGLET 3 - SANTÉ
    # ──────────────────────────────────────────────────────────────────────────
    with s3:
        import json
        GEOJSON_PATH = Path("solidarite&citoyennete/data_clean/sante/Etablissements_santé_filtre.geojson")
        GEOJSON_METROS_PATH = Path("solidarite&citoyennete/data_clean/sante/contour_metropole.geojson")
        GEOJSON_COMMUNES_PATH = Path("solidarite&citoyennete/data_clean/sante/contour_communes.geojson")

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
                    "nom": p.get("nom_etablissement") or "-",
                    "commune": p.get("DCOE_L_LIB", p.get("commune", "")),
                    "metropole": p.get("METROPOLE", p.get("Métropole", p.get("metropole", ""))),
                    "lon": coords[0],
                    "lat": coords[1],
                })
            return pd.DataFrame(rows)

        @st.cache_data
        def charger_geojson_metros():
            if not GEOJSON_METROS_PATH.exists(): return None
            with open(GEOJSON_METROS_PATH, "r", encoding="utf-8") as f: return json.load(f)

        @st.cache_data
        def charger_geojson_communes():
            if not GEOJSON_COMMUNES_PATH.exists(): return None
            with open(GEOJSON_COMMUNES_PATH, "r", encoding="utf-8") as f: return json.load(f)

        df_sante = charger_sante()
        geojson_metros = charger_geojson_metros()
        geojson_communes = charger_geojson_communes()

        TYPE_LABELS = {"pharmacy": "Pharmacie", "doctors": "Médecins / Soins", "dentist": "Dentiste", "hospital": "Hôpital", "nursing_home": "EHPAD / M. retraite", "clinic": "Clinique / C. santé"}
        TYPE_COLORS = {"pharmacy": "#264653", "doctors": "#2a9d8f", "dentist": "#e9c46a", "hospital": "#f4a261", "nursing_home": "#e76f51", "clinic": "#5DC26E"}
        metros_sante = sorted(df_sante["metropole"].dropna().unique())
        types_sante = sorted(df_sante["type_etab"].dropna().unique())

        # ── Filtres ──
        with st.container():
            filter_bar("Filtres - Établissements de santé")
            fs1, fs2 = st.columns([1, 3])
            with fs1: filter_row_label("Niveau géographique")
            with fs2:
                mode_sante = st.radio("", ["Comparaison Métropoles", "Détail Communal"], key="sante_mode", horizontal=True, label_visibility="collapsed")
            if mode_sante == "Comparaison Métropoles":
                sel_metros_sante = st.multiselect("Métropoles à comparer", metros_sante, default=metros_sante, key="sante_metros_multi")
            else:
                communes_sante_dispo = sorted(df_sante[df_sante["metropole"] == "Grenoble"]["commune"].dropna().unique())
                sel_communes_sante = st.multiselect("Communes de Grenoble", communes_sante_dispo, default=communes_sante_dispo[:5], key="sante_communes_t1")
            
            sel_types_sante = st.multiselect("Type d'établissement", options=types_sante, default=types_sante, format_func=lambda t: TYPE_LABELS.get(t, t), key="sante_types_t1")
            st.markdown('</div>', unsafe_allow_html=True)

        # ── Filtrage ──
        if mode_sante == "Comparaison Métropoles":
            df_sf = df_sante[(df_sante["metropole"].isin(sel_metros_sante)) & (df_sante["type_etab"].isin(sel_types_sante))].copy()
            kpi_border_color = "#666"
        else:
            df_sf = df_sante[(df_sante["metropole"] == "Grenoble") & (df_sante["commune"].isin(sel_communes_sante)) & (df_sante["type_etab"].isin(sel_types_sante))].copy()
            kpi_border_color = "#1e5631"

        st.markdown("---")
        st.markdown(f"#### Synthèse de l'offre de soins")

        # ── KPIs ──
        sk1, sk2, sk3, sk4, sk5 = st.columns(5)
        with sk1: st.markdown(render_solidarite_kpi("Total", fmt(len(df_sf)), "Établissements", kpi_border_color), unsafe_allow_html=True)
        with sk2: st.markdown(render_solidarite_kpi("Pharmacies", fmt(len(df_sf[df_sf["type_etab"] == "pharmacy"])), "Officines", kpi_border_color), unsafe_allow_html=True)
        with sk3: st.markdown(render_solidarite_kpi("Médecins", fmt(len(df_sf[df_sf["type_etab"] == "doctors"])), "Cabinets", kpi_border_color), unsafe_allow_html=True)
        with sk4: st.markdown(render_solidarite_kpi("Hôpitaux", fmt(len(df_sf[df_sf["type_etab"] == "hospital"])), "Centres hospitaliers", kpi_border_color), unsafe_allow_html=True)
        with sk5: st.markdown(render_solidarite_kpi("Périmètre", fmt(df_sf["commune"].nunique()), "Communes", kpi_border_color), unsafe_allow_html=True)

        st.markdown("---")

        # ── Helpers zoom ──
        import math
        def bbox_from_features(features):
            lons, lats = [], []
            for feat in features:
                geom = feat.get("geometry", {})
                t = geom.get("type", "")
                if t == "Point":
                    lons.append(geom["coordinates"][0]); lats.append(geom["coordinates"][1])
                elif t == "Polygon":
                    for ring in geom["coordinates"]:
                        for c in ring: lons.append(c[0]); lats.append(c[1])
                elif t == "MultiPolygon":
                    for poly in geom["coordinates"]:
                        for ring in poly:
                            for c in ring: lons.append(c[0]); lats.append(c[1])
            if not lons: return None
            return min(lats), max(lats), min(lons), max(lons)

        def zoom_from_bbox(bbox, map_width_px=1200, map_height_px=480, margin=1.3):
            lat_min, lat_max, lon_min, lon_max = bbox
            span_lat = max((lat_max - lat_min) * margin, 0.01)
            span_lon = max((lon_max - lon_min) * margin, 0.01)
            zoom_lon = math.log2(360 / span_lon) + math.log2(map_width_px / 256)
            zoom_lat = math.log2(180 / span_lat) + math.log2(map_height_px / 256)
            return round(min(zoom_lon, zoom_lat) - 0.5, 1)

        if mode_sante == "Comparaison Métropoles" and geojson_metros is not None and sel_metros_sante:
            feats_zoom = [f for f in geojson_metros["features"] if f["properties"].get("METROPOLE") in sel_metros_sante]
        elif mode_sante == "Détail Communal" and geojson_communes is not None and sel_communes_sante:
            feats_zoom = [f for f in geojson_communes["features"] if f["properties"].get("DCOE_L_LIB") in sel_communes_sante]
        else:
            feats_zoom = []

        bbox = bbox_from_features(feats_zoom)
        if bbox:
            lat_min, lat_max, lon_min, lon_max = bbox
            lat_c, lon_c, zoom_level = (lat_min + lat_max) / 2, (lon_min + lon_max) / 2, zoom_from_bbox(bbox)
        elif not df_sf.empty:
            bbox_pts = bbox_from_features([{"geometry": {"type": "Point", "coordinates": [row.lon, row.lat]}} for _, row in df_sf.iterrows()])
            lat_c, lon_c, zoom_level = (bbox_pts[0] + bbox_pts[1]) / 2, (bbox_pts[2] + bbox_pts[3]) / 2, zoom_from_bbox(bbox_pts)
        else:
            lat_c, lon_c, zoom_level = 46.5, 2.5, 5

        mapbox_layers = []
        if mode_sante == "Comparaison Métropoles" and geojson_metros is not None:
            feats_filtrees = [f for f in geojson_metros["features"] if f["properties"].get("METROPOLE") in sel_metros_sante]
            if feats_filtrees:
                mapbox_layers.append({"source": {"type": "FeatureCollection", "features": feats_filtrees}, "type": "line", "color": "#2D6A4F", "line": {"width": 2}, "opacity": 0.8})
        elif mode_sante == "Détail Communal":
            if geojson_communes is not None:
                feats_communes = [f for f in geojson_communes["features"] if f["properties"].get("DCOE_L_LIB") in sel_communes_sante]
                if feats_communes:
                    mapbox_layers.append({"source": {"type": "FeatureCollection", "features": feats_communes}, "type": "line", "color": "#40916C", "line": {"width": 1.5}, "opacity": 0.9})
            if geojson_metros is not None:
                feats_grenoble = [f for f in geojson_metros["features"] if f["properties"].get("METROPOLE") == "Grenoble"]
                if feats_grenoble:
                    mapbox_layers.append({"source": {"type": "FeatureCollection", "features": feats_grenoble}, "type": "line", "color": "#1B4332", "line": {"width": 2.5}, "opacity": 0.6})

        # ── Carte ──
        st.markdown("##### Carte de l'offre de santé", help="Localisation des établissements extraits via OpenStreetMap.")
        if df_sf.empty:
            st.info("Aucun établissement pour ces filtres.")
        else:
            fig_map = px.scatter_mapbox(
                df_sf, lat="lat", lon="lon", color="type_etab",
                color_discrete_map=TYPE_COLORS,
                hover_name="nom",
                hover_data={"commune": True, "metropole": True, "type_etab": False, "lat": False, "lon": False},
                labels={"type_etab": "Type", "commune": "Commune", "metropole": "Métropole"},
                height=480, mapbox_style="carto-positron"
            )
            for trace in fig_map.data:
                trace.name = TYPE_LABELS.get(trace.name, trace.name)
                trace.hovertemplate = (
                    "<b>%{hovertext}</b><br>"
                    "Commune : <b>%{customdata[0]}</b><br>"
                    "Métropole : <b>%{customdata[1]}</b>"
                    "<extra></extra>"
                )
            fig_map.update_layout(
                mapbox_zoom=zoom_level,
                mapbox_center={"lat": lat_c, "lon": lon_c},
                mapbox_layers=mapbox_layers,
                legend=dict(title="Type", orientation="v", x=0.01, y=0.99, bgcolor="rgba(255,255,255,0.85)", bordercolor="#C8E6D4", borderwidth=1, font=dict(size=11)),
                margin=dict(l=0, r=0, t=0, b=0),
                paper_bgcolor="rgba(0,0,0,0)",
                font_family="Sora"
            )
            st.plotly_chart(fig_map, use_container_width=True)

        st.markdown("---")
        extra1, extra2 = st.columns(2)

        with extra1:
            if mode_sante == "Comparaison Métropoles":
                st.markdown("##### Densité par métropole et type", help="Nombre absolu d'établissements identifiés par type de soin.")
                df_pivot = df_sf.groupby(["metropole", "type_etab"]).size().reset_index(name="count")
                df_pivot["label"] = df_pivot["type_etab"].map(lambda t: TYPE_LABELS.get(t, t))
                df_pivot["text_display"] = df_pivot["count"].apply(lambda x: fmt(x))
                fig_stack = px.bar(df_pivot, x="metropole", y="count", color="type_etab", color_discrete_map=TYPE_COLORS, text="text_display", labels={"metropole": "Métropole", "count": "Nombre", "type_etab": "Type"}, height=380, barmode="stack")
                fig_stack.update_traces(
                    textposition="inside",
                    textfont_size=10,
                    hovertemplate="<b>%{x}</b><br>%{fullData.name} : <b>%{text}</b><extra></extra>"
                )
                for trace in fig_stack.data: trace.name = TYPE_LABELS.get(trace.name, trace.name)
                fig_stack.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_family="Sora", xaxis=dict(tickangle=-30), legend=dict(title="Type", font=dict(size=10)))
                st.plotly_chart(style(fig_stack, 40), use_container_width=True)
            else:
                st.markdown("##### Densité par commune", help="Nombre absolu d'établissements identifiés par commune.")
                df_comm = df_sf.groupby(["commune", "type_etab"]).size().reset_index(name="count")
                df_comm["label"] = df_comm["type_etab"].map(lambda t: TYPE_LABELS.get(t, t))
                df_comm["text_display"] = df_comm["count"].apply(lambda x: fmt(x))
                fig_comm = px.bar(df_comm, x="commune", y="count", color="type_etab", color_discrete_map=TYPE_COLORS, text="text_display", labels={"commune": "Commune", "count": "Nombre", "type_etab": "Type"}, height=380, barmode="stack")
                fig_comm.update_traces(
                    textposition="inside",
                    textfont_size=10,
                    hovertemplate="<b>%{x}</b><br>%{fullData.name} : <b>%{text}</b><extra></extra>"
                )
                for trace in fig_comm.data: trace.name = TYPE_LABELS.get(trace.name, trace.name)
                fig_comm.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_family="Sora", xaxis=dict(tickangle=-30), legend=dict(title="Type", font=dict(size=10)))
                st.plotly_chart(style(fig_comm, 40), use_container_width=True)

        with extra2:
            st.markdown("##### Part de chaque type d'établissement", help="Répartition relative de l'offre de soins sur les territoires sélectionnés.")
            pie_data = df_sf.groupby("type_etab").size().reset_index(name="count")
            pie_data["label"] = pie_data["type_etab"].map(lambda t: TYPE_LABELS.get(t, t))
            fig_pie = px.pie(pie_data, names="label", values="count", color="type_etab", color_discrete_map=TYPE_COLORS, height=380, hole=0.4)
            fig_pie.update_traces(
                textposition="outside",
                textinfo="percent+label",
                pull=[0.03] * len(pie_data),
                hovertemplate="<b>%{label}</b><br>Établissements : <b>%{value:,.0f}</b><br>Part : <b>%{percent}</b><extra></extra>"
            )
            fig_pie.update_layout(showlegend=False, paper_bgcolor="rgba(0,0,0,0)", font_family="Sora", margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_pie, use_container_width=True)

    # ──────────────────────────────────────────────────────────────────────────
    # ONGLET 4 - PARTICIPATION (Élections)
    # ──────────────────────────────────────────────────────────────────────────
    with s4:
        @st.cache_data
        def charger_elections():
            df_muni_2014 = pd.read_csv("solidarite&citoyennete/data_clean/participation_citoyenne/elections_2014_2020.csv")
            df_muni_2014 = df_muni_2014[df_muni_2014["Année"] == 2014].copy()
            df_muni_2014["Type d'élection"] = "Municipales"
 
            df_muni_2026 = pd.read_csv("solidarite&citoyennete/data_clean/participation_citoyenne/municipales_2026.csv")
            df_muni_2026["Type d'élection"] = "Municipales"
            df_muni_2026["Libellé de la commune"] = df_muni_2026["Libellé de la commune"].replace("Oissel-sur-Seine", "Oissel")
 
            df_p17 = pd.read_csv("solidarite&citoyennete/data_clean/participation_citoyenne/presidentielle_2017.csv")
            df_p17["Type d'élection"] = "Présidentielles"
 
            df_p22 = pd.read_csv("solidarite&citoyennete/data_clean/participation_citoyenne/presidentielle_2022.csv")
            df_p22["Type d'élection"] = "Présidentielles"
 
            return pd.concat([df_muni_2014, df_muni_2026, df_p17, df_p22], ignore_index=True)
 
        df_elec = charger_elections()
        DEP_METRO_ELEC = {"Isère": "Grenoble", "Ille-et-Vilaine": "Rennes", "Seine-Maritime": "Rouen", "Loire": "Saint-Étienne", "Hérault": "Montpellier"}
        df_elec["metropole"] = df_elec["Libellé du département"].map(DEP_METRO_ELEC)
        df_elec["% Participation"] = 100 - df_elec["% Abs/Ins"]
 
        tours_elec  = sorted(df_elec["Numéro de tour"].dropna().unique().astype(int))
        metros_elec = sorted(df_elec["metropole"].dropna().unique())
 
        # ── Filtres ──
        with st.container():
            filter_bar("Filtres - Participation citoyenne")
 
            # -- Type d'élection --
            ft1, ft2 = st.columns([1, 3])
            with ft1: filter_row_label("Type d'élection")
            with ft2: type_election = st.radio("", ["Municipales", "Présidentielles"], key="part_type_election", horizontal=True, label_visibility="collapsed")
 
            # Filtrer le df selon le type pour alimenter les autres filtres
            df_elec_type = df_elec[df_elec["Type d'élection"] == type_election]
            annees_elec = sorted(df_elec_type["Année"].dropna().unique().astype(int))
 
            # -- Niveau géographique --
            fp1, fp2 = st.columns([1, 3])
            with fp1: filter_row_label("Niveau géographique")
            with fp2: mode_part = st.radio("", ["Comparaison Métropoles", "Détail Communal"], key="part_mode", horizontal=True, label_visibility="collapsed")
 
            if mode_part == "Détail Communal":
                communes_elec_dispo = sorted(df_elec_type[df_elec_type["metropole"] == "Grenoble"]["Libellé de la commune"].dropna().unique())
                sel_communes_part = st.multiselect("Communes de Grenoble", communes_elec_dispo, default=communes_elec_dispo[:5], key="part_communes")
            else:
                sel_metros_part = st.multiselect("Métropoles à comparer", metros_elec, default=metros_elec, key="part_metros")
 
            fc1, fc2 = st.columns(2)
            with fc1:
                label_annee = "Année (Municipales)" if type_election == "Municipales" else "Année (Présidentielles)"
                sel_annee_part = st.selectbox(label_annee, annees_elec, index=len(annees_elec)-1, key="part_annee")
            with fc2:
                sel_tour_part = st.selectbox("Tour", tours_elec, format_func=lambda t: f"Tour {t}", key="part_tour")
            st.markdown('</div>', unsafe_allow_html=True)
 
        # ── Filtrage ──
        df_elec_f = df_elec_type[
            (df_elec_type["Année"] == sel_annee_part) &
            (df_elec_type["Numéro de tour"] == sel_tour_part)
        ]
        if mode_part == "Comparaison Métropoles":
            df_elec_f = df_elec_f[df_elec_f["metropole"].isin(sel_metros_part)]
            df_agg = df_elec_f.groupby("metropole", as_index=False).agg(Inscrits=("Inscrits", "sum"), Votants=("Votants", "sum"), Abstentions=("Abstentions", "sum"), Non_Exprimes=("Non-Exprimés", "sum"), Exprimes=("Exprimés", "sum"))
            kpi_border_color = "#666"
        else:
            df_elec_f = df_elec_f[df_elec_f["Libellé de la commune"].isin(sel_communes_part)]
            df_agg = df_elec_f.groupby("Libellé de la commune", as_index=False).agg(Inscrits=("Inscrits", "sum"), Votants=("Votants", "sum"), Abstentions=("Abstentions", "sum"), Non_Exprimes=("Non-Exprimés", "sum"), Exprimes=("Exprimés", "sum"))
            df_agg = df_agg.rename(columns={"Libellé de la commune": "metropole"})
            kpi_border_color = "#1e5631"
 
        df_agg["% Participation"] = (df_agg["Votants"] / df_agg["Inscrits"] * 100).round(2)
        df_agg["% Abstention"]    = (df_agg["Abstentions"] / df_agg["Inscrits"] * 100).round(2)
        df_agg["% Non-Exprimés"]  = (df_agg["Non_Exprimes"] / df_agg["Votants"] * 100).round(2)
        df_agg["% Exprimés"]      = (df_agg["Exprimes"] / df_agg["Votants"] * 100).round(2)
 
        st.markdown("---")
 
        # ── KPIs ──
        if not df_agg.empty:
            total_inscrits      = int(df_agg["Inscrits"].sum())
            total_votants       = int(df_agg["Votants"].sum())
            total_exprimes      = int(df_agg["Exprimes"].sum())
            total_abstentions   = int(df_agg["Abstentions"].sum())
            total_non_exp       = int(df_agg["Non_Exprimes"].sum())
            taux_part_global    = round(total_votants / total_inscrits * 100, 1) if total_inscrits else 0
            taux_abs_global     = round(total_abstentions / total_inscrits * 100, 1) if total_inscrits else 0
            taux_non_exp_global = round(total_non_exp / total_votants * 100, 1) if total_votants else 0
 
            st.markdown(f"#### Bilan Électoral - {sel_annee_part} (Tour {sel_tour_part})")
            kpi_cols = st.columns(4)
            with kpi_cols[0]: st.markdown(render_solidarite_kpi("Inscrits", fmt(total_inscrits), "Listes électorales", kpi_border_color), unsafe_allow_html=True)
            with kpi_cols[1]: st.markdown(render_solidarite_kpi("Participation", f"{taux_part_global} %", "Votants / Inscrits", kpi_border_color), unsafe_allow_html=True)
            with kpi_cols[2]: st.markdown(render_solidarite_kpi("Abstention", f"{taux_abs_global} %", "Absents / Inscrits", kpi_border_color), unsafe_allow_html=True)
            with kpi_cols[3]: st.markdown(render_solidarite_kpi("Blancs & Nuls", f"{taux_non_exp_global} %", "Non-exprimés / Votants", kpi_border_color), unsafe_allow_html=True)
 
        st.markdown("---")
 
        if df_agg.empty:
            st.warning("⚠️ Aucune donnée pour les filtres sélectionnés.")
        else:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("##### Taux de participation", help="Pourcentage d'inscrits ayant déposé un bulletin dans l'urne (incluant les blancs et nuls).")
                df_part_sorted = df_agg.sort_values("% Participation", ascending=True)
                df_part_sorted["text_display"] = df_part_sorted["% Participation"].apply(lambda v: f"{v:.1f} %")
                _part_color_map = COULEURS if mode_part == "Comparaison Métropoles" else None
                _part_seq = px.colors.sequential.Greens_r if mode_part == "Détail Communal" else None
                fig_part = px.bar(
                    df_part_sorted, x="% Participation", y="metropole", orientation="h",
                    color="metropole", color_discrete_map=_part_color_map, color_discrete_sequence=_part_seq,
                    text="text_display",
                    labels={"metropole": "", "% Participation": "Participation (%)"},
                    height=380
                )
                fig_part.update_traces(
                    textposition="outside",
                    hovertemplate="<b>%{y}</b><br>Participation : <b>%{text}</b><extra></extra>"
                )
                fig_part.update_layout(
                    showlegend=False, xaxis_range=[0, 100],
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font_family="Sora", xaxis=dict(gridcolor="#E8F5EE"),
                    margin=dict(l=10, r=40, t=40, b=10)
                )
                st.plotly_chart(style(fig_part, 40), use_container_width=True)
 
            with c2:
                st.markdown("##### Qualité du vote", help="Parmi les votants, proportion de votes valides (Exprimés) vs proportion de votes blancs ou nuls (Non-Exprimés).")
                df_qual = df_agg[["metropole", "% Exprimés", "% Non-Exprimés"]].melt(id_vars="metropole", var_name="Type", value_name="Taux")
                df_qual["text_display"] = df_qual["Taux"].apply(lambda v: f"{v:.1f} %")
                fig_qual = px.bar(
                    df_qual, x="metropole", y="Taux", color="Type", barmode="stack",
                    color_discrete_map={"% Exprimés": "#555555", "% Non-Exprimés": "#aaaaaa"} if mode_part == "Comparaison Métropoles" else {"% Exprimés": "#2D6A4F", "% Non-Exprimés": "#95D5B2"},
                    text="text_display",
                    labels={"metropole": "", "Taux": "%", "Type": ""},
                    height=380
                )
                fig_qual.update_traces(
                    hovertemplate="<b>%{x}</b><br>%{fullData.name} : <b>%{text}</b><extra></extra>"
                )
                fig_qual.update_layout(
                    yaxis_range=[0, 100],
                    legend=dict(orientation="h", y=1.1),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font_family="Sora", yaxis=dict(gridcolor="#E8F5EE"),
                    margin=dict(l=10, r=10, t=40, b=10)
                )
                st.plotly_chart(style(fig_qual, 40), use_container_width=True)
 
            st.markdown("---")
 
            # ── Évolution de la participation ──
            if type_election == "Municipales":
                titre_evolution = "##### Évolution de la participation (2014 → 2026)"
                help_evolution  = "Différence en points de pourcentage de la participation entre les élections municipales de 2014 et 2026."
                annee_debut, annee_fin = 2014, 2026
            else:
                titre_evolution = "##### Évolution de la participation (2017 → 2022)"
                help_evolution  = "Différence en points de pourcentage de la participation entre les élections présidentielles de 2017 et 2022."
                annee_debut, annee_fin = 2017, 2022
 
            st.markdown(titre_evolution, help=help_evolution)
 
            df_delta_base = df_elec_type[df_elec_type["Numéro de tour"] == sel_tour_part].copy()
            if mode_part == "Comparaison Métropoles":
                df_delta_base = df_delta_base[df_delta_base["metropole"].isin(sel_metros_part)]
                grp_col = "metropole"
            else:
                df_delta_base = df_delta_base[df_delta_base["Libellé de la commune"].isin(sel_communes_part)]
                grp_col = "Libellé de la commune"
 
            df_delta_agg = df_delta_base.groupby(["Année", grp_col], as_index=False).agg(Inscrits=("Inscrits", "sum"), Votants=("Votants", "sum"))
            df_delta_agg["% Participation"] = (df_delta_agg["Votants"] / df_delta_agg["Inscrits"] * 100).round(2)
 
            df_debut = df_delta_agg[df_delta_agg["Année"] == annee_debut].set_index(grp_col)["% Participation"]
            df_fin   = df_delta_agg[df_delta_agg["Année"] == annee_fin].set_index(grp_col)["% Participation"]
            df_delta = (df_fin - df_debut).dropna().reset_index()
            df_delta.columns = ["entite", "Δ Participation (pts)"]
            df_delta = df_delta.sort_values("Δ Participation (pts)")
            df_delta["couleur"] = df_delta["Δ Participation (pts)"].apply(lambda v: "#e76f51" if v < 0 else "#2D6A4F")
            df_delta["text_display"] = df_delta["Δ Participation (pts)"].apply(lambda v: f"{v:+.1f} pts")
 
            if not df_delta.empty:
                fig_delta = px.bar(
                    df_delta, x="Δ Participation (pts)", y="entite", orientation="h",
                    color="couleur", color_discrete_map="identity",
                    text="text_display",
                    labels={"entite": "", "Δ Participation (pts)": "Variation (pts)"},
                    height=max(300, len(df_delta) * 50)
                )
                fig_delta.update_traces(
                    textposition="outside",
                    hovertemplate="<b>%{y}</b><br>Variation : <b>%{text}</b><extra></extra>"
                )
                fig_delta.add_vline(x=0, line_dash="dash", line_color="#888", line_width=1)
                fig_delta.update_layout(
                    showlegend=False,
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font_family="Sora", xaxis=dict(gridcolor="#E8F5EE"),
                    margin=dict(l=10, r=60, t=40, b=10)
                )
                st.plotly_chart(style(fig_delta), use_container_width=True)
            else:
                st.info("Données insuffisantes pour calculer la variation.")

    # ──────────────────────────────────────────────────────────────────────────
    # ONGLET 5 - REVENUS & PAUVRETÉ (FiLoSoFi)
    # ──────────────────────────────────────────────────────────────────────────
    with s5:
        if df_filo is None or df_filo.empty:
            st.info("📂 Fichier `BASE_TD_FILO_IRIS_2021_DEC.xlsx` introuvable - placez-le dans `solidarite&citoyennete/data_clean/revenus/`.")
        else:
            FILO_LABELS = {
                "DEC_MED21": "Revenu médian (€/UC)", "DEC_GI21": "Indice de Gini", "DEC_PIMP21": "Part ménages imposés (%)", "DEC_PACT21": "Part revenus d'activité (%)", "DEC_PTSA21": "dont salaires & traitements (%)", "DEC_PCHO21": "dont indemnités chômage (%)", "DEC_PBEN21": "dont revenus non salariés (%)", "DEC_PPEN21": "Part pensions & retraites (%)", "DEC_PAUT21": "Part autres revenus (%)",
            }
            filo_cols = [c for c in FILO_LABELS if c in df_filo.columns]
            metros_filo = sorted(df_filo["metropole"].dropna().unique())

            # ── Filtres ──
            with st.container():
                filter_bar("Filtres - Revenus & pauvreté")
                f1, f2 = st.columns([1, 3])
                with f1: filter_row_label("Niveau géographique")
                with f2: mode_filo = st.radio("", ["Comparaison Métropoles", "Détail Communal"], key="filo_mode", horizontal=True, label_visibility="collapsed")

                if mode_filo == "Comparaison Métropoles":
                    sel_entites_filo = st.multiselect("Métropoles", metros_filo, default=metros_filo, key="filo_metros")
                else:
                    communes_gre_filo = sorted(df_filo[df_filo["metropole"] == "Grenoble"]["LIBCOM"].dropna().unique())
                    sel_entites_filo = st.multiselect("Communes de Grenoble", communes_gre_filo, default=communes_gre_filo[:5] if communes_gre_filo else [], key="filo_communes")

                filo_ind = st.selectbox(
                    "Indicateur principal",
                    filo_cols,
                    format_func=lambda c: FILO_LABELS.get(c, c),
                    index=filo_cols.index("DEC_MED21") if "DEC_MED21" in filo_cols else 0,
                    key="filo_ind"
                )
            st.markdown('</div>', unsafe_allow_html=True)

            # ── Filtrage ──
            geo_col = "metropole" if mode_filo == "Comparaison Métropoles" else "LIBCOM"
            is_metro = (mode_filo == "Comparaison Métropoles")

            if is_metro: df_f = df_filo[df_filo["metropole"].isin(sel_entites_filo)].copy()
            else: df_f = df_filo[(df_filo["metropole"] == "Grenoble") & (df_filo["LIBCOM"].isin(sel_entites_filo))].copy()

            lbl = FILO_LABELS.get(filo_ind, filo_ind)
            st.markdown("---")

            if df_f.empty or not sel_entites_filo:
                st.warning("⚠️ Aucune donnée pour les filtres sélectionnés.")
            else:
                # ── KPIs ──
                st.markdown(f"#### Aperçu - {lbl}")
                kpi_cols = st.columns(len(sel_entites_filo))
                for i, entite in enumerate(sel_entites_filo):
                    sub = df_f[df_f[geo_col] == entite][filo_ind].dropna()
                    val = sub.median() if not sub.empty else np.nan
                    
                    suffix = " €" if "Revenu" in lbl else (" %" if "Part" in lbl else "")
                    val_str = fmt(val, suffix=suffix, dec=1) if pd.notna(val) else "N/D"
                    kpi_color = COULEURS.get(entite, "#1e5631") if is_metro else "#1e5631"

                    with kpi_cols[i]:
                        st.markdown(render_solidarite_kpi(entite, val_str, lbl, kpi_color), unsafe_allow_html=True)

                st.markdown("---")

                # ── Graphiques spécifiques ──
                if is_metro:
                    st.markdown(f"##### Distribution par métropole", help="Boîte à moustaches montrant la dispersion de l'indicateur sélectionné au sein des IRIS de chaque agglomération.")
                    fig_box = px.box(
                        df_f.dropna(subset=[filo_ind]), x=geo_col, y=filo_ind,
                        color=geo_col, color_discrete_map=COULEURS,
                        labels={geo_col: "", filo_ind: lbl}, height=400
                    )
                    fig_box.update_traces(
                        hovertemplate="<b>%{x}</b><br>" + lbl + " : <b>%{y:,.1f}</b><extra></extra>"
                    )
                    fig_box.update_layout(showlegend=False)
                    st.plotly_chart(style(fig_box, 40), use_container_width=True)

                    st.markdown("---")
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("##### Revenu médian vs Taux de bas revenus", help="Met en relation le niveau de vie global de la métropole avec sa précarité (taux de bas revenus).")
                        if "DEC_MED21" in df_f.columns and "DEC_TP6021" in df_f.columns:
                            df_sc = df_f.groupby(geo_col, as_index=False)[["DEC_MED21", "DEC_TP6021"]].median().dropna()
                            fig_sc = px.scatter(
                                df_sc, x="DEC_MED21", y="DEC_TP6021",
                                color=geo_col, color_discrete_map=COULEURS,
                                text=geo_col,
                                labels={"DEC_MED21": "Revenu médian (€/UC)", "DEC_TP6021": "Taux bas revenus (%)", geo_col: ""},
                                height=400
                            )
                            fig_sc.update_traces(
                                marker_size=12,
                                textposition="top center",
                                hovertemplate="<b>%{text}</b><br>Revenu médian : <b>%{x:,.0f} €</b><br>Taux bas revenus : <b>%{y:.1f} %</b><extra></extra>"
                            )
                            fig_sc.update_layout(showlegend=False)
                            st.plotly_chart(style(fig_sc, 40), use_container_width=True)

                    with c2:
                        st.markdown("##### Inégalités - Indice de Gini", help="L'indice de Gini mesure les inégalités au sein du territoire. Un indice proche de 0 indique une égalité parfaite ; proche de 1, des inégalités très fortes.")
                        if "DEC_GI21" in df_f.columns:
                            df_gi = df_f.groupby(geo_col, as_index=False)["DEC_GI21"].median().dropna().sort_values("DEC_GI21", ascending=False)
                            df_gi["text_display"] = df_gi["DEC_GI21"].apply(lambda v: f"{v:.3f}")
                            fig_gi = px.bar(
                                df_gi, x="DEC_GI21", y=geo_col,
                                color=geo_col, color_discrete_map=COULEURS,
                                orientation="h", text="text_display",
                                labels={geo_col: "", "DEC_GI21": "Indice de Gini"},
                                height=400
                            )
                            fig_gi.update_traces(
                                hovertemplate="<b>%{y}</b><br>Indice de Gini : <b>%{text}</b><extra></extra>"
                            )
                            fig_gi.update_layout(yaxis={"categoryorder": "total ascending"}, showlegend=False)
                            st.plotly_chart(style(fig_gi, 40), use_container_width=True)

                else:
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"##### {lbl} par commune", help="Valeur médiane de l'indicateur sélectionné pour l'ensemble des IRIS de la commune.")
                        df_bar = df_f.groupby(geo_col, as_index=False)[filo_ind].median()
                        df_bar["text_display"] = df_bar[filo_ind].apply(lambda v: f"{v:,.1f}".replace(",", " "))
                        fig_bar = px.bar(
                            df_bar, x=geo_col, y=filo_ind,
                            color=geo_col, color_discrete_sequence=px.colors.sequential.Greens_r,
                            text="text_display",
                            labels={geo_col: "", filo_ind: lbl},
                            height=400
                        )
                        fig_bar.update_traces(
                            hovertemplate="<b>%{x}</b><br>" + lbl + " : <b>%{text}</b><extra></extra>"
                        )
                        fig_bar.update_layout(showlegend=False)
                        st.plotly_chart(style(fig_bar, 40), use_container_width=True)
                        
                    with c2:
                        st.markdown(f"##### Dispersion au sein des quartiers (IRIS)", help=f"Boîte à moustaches montrant la variance du {lbl} entre les différents quartiers (IRIS) d'une même commune.")
                        df_dist = df_f.dropna(subset=[filo_ind])
                        if not df_dist.empty:
                            fig_dist = px.box(
                                df_dist, x=geo_col, y=filo_ind,
                                color=geo_col, color_discrete_sequence=px.colors.sequential.Greens_r,
                                labels={geo_col: "", filo_ind: lbl},
                                height=400
                            )
                            fig_dist.update_traces(
                                hovertemplate="<b>%{x}</b><br>" + lbl + " : <b>%{y:,.1f}</b><extra></extra>"
                            )
                            fig_dist.update_layout(showlegend=False)
                            st.plotly_chart(style(fig_dist, 40), use_container_width=True)

                    st.markdown("---")
                    
                    st.markdown("##### Profil socio-économique comparatif", help="Comparaison multidimensionnelle normalisée de 0 à 100 par rapport aux valeurs maximales observées sur la Métropole de Grenoble.")
                    radar_ind = ["DEC_MED21", "DEC_TP6021", "DEC_GI21", "DEC_RD21", "DEC_PIMP21", "DEC_PACT21", "DEC_PPEN21"]
                    radar_avail = [c for c in radar_ind if c in df_f.columns]
                    
                    if len(radar_avail) >= 3:
                        df_all_metro = df_filo[df_filo["metropole"] == "Grenoble"]
                        fig_rad = go.Figure()
                        green_palette = px.colors.sequential.Greens_r  # communes → vert
                        
                        for idx, comm in enumerate(sel_entites_filo):
                            df_c = df_f[df_f[geo_col] == comm]
                            vals_raw = [df_c[c].median() for c in radar_avail]
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
                                fill="toself",
                                name=comm,
                                line_color=green_palette[idx % len(green_palette)],
                                hovertemplate="<b>%{theta}</b><br>Score normalisé : <b>%{r:.1f}</b><extra></extra>"
                            ))
                            
                        fig_rad.update_layout(
                            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                            height=400,
                            paper_bgcolor="rgba(0,0,0,0)",
                            legend=dict(orientation="v", x=1.05, y=0.5, yanchor="middle")
                        )
                        st.plotly_chart(fig_rad, use_container_width=True)

                with st.expander("Note méthodologique"):
                    st.markdown("""
                    * **Revenu médian (€/UC)** : Niveau de revenu tel que 50% de la population gagne moins et 50% gagne plus. L'UC (Unité de Consommation) permet de pondérer selon la taille du foyer.
                    * **Indice de Gini** : Mesure synthétique des inégalités de revenus (entre 0 et 1). Plus il est proche de 1, plus les revenus sont inégalement répartis (quelques personnes concentrent l'essentiel de la richesse).
                    * **Taux de bas revenus** : Part de la population vivant sous le seuil de bas revenus (fixé à 60% du revenu médian national).
                    * **Structure des revenus** : Permet de voir si l'économie locale est principalement portée par les salaires de l'activité, les pensions de retraite ou les revenus non-salariés.
                    """)
