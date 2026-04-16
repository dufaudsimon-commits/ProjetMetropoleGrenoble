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
    "Montpellier": "#124660",
    "Saint-Étienne": "#1B9476",
    "Grenoble": "#8BD59E",
    "Rennes": "#C7DBC2",
    "Rouen": "#F4EBD6",
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
    </div>
    """, unsafe_allow_html=True)

    # ── Cartes thématiques ─────────────────────────────────────────────────
    st.markdown("""
    <div class="cards-row">
        <div class="info-card">
            <div class="info-card-title">Démographie</div>
            <div class="info-card-body">
                Analyse de la population, de la structure par âge, des mobilités, des ménages, des mobilités résidentielles, professionnelles et scolaires
                à l'échelle des communes et des EPCI.
            </div>
            <div class="tag-row">
                <span class="tag-green">Population</span>
                <span class="tag-green">Structure des âges</span>
                <span class="tag-green">Population active 25-54 ans</span>
                <span class="tag-green">Mobilités</span>
                <span class="tag-green">Ménages</span>
            </div>
        </div>
        <div class="info-card orange">
            <div class="info-card-title">Solidarité & citoyenneté</div>
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
                <span class="tag-orange">Revenus & pauvreté</span>
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
if vue == "Description":
    st.markdown('<p class="section-header">Description</p>', unsafe_allow_html=True)

    st.markdown("""
    Cette application présente des analyses comparatives sur **5 métropoles françaises** à partir des recensements INSEE 2011, 2016 et 2022.
    Chaque page dispose de ses propres filtres en haut de page, adaptés aux données présentées.
    Selon les onglets, il est possible de filtrer par métropole, par année ou par thématique.
    """)

    st.markdown("---")

    st.markdown("### Périmètre géographique")
    communes_data = {
        "Métropole": list(COMMUNES.keys()),
        "Nombre de communes": [len(v) for v in COMMUNES.values()],
        "Département": ["Isère (38)", "Ille-et-Vilaine (35)", "Seine-Maritime (76)", "Loire (42)", "Hérault (34)"],
    }
    st.dataframe(pd.DataFrame(communes_data).set_index("Métropole"), use_container_width=True)

    st.markdown("---")

    st.markdown("### Thématique 1 - Démographie")

    demo_onglets = [
        {
            "titre": "Population globale",
            "description": "Évolution et comparaison des populations totales entre métropoles.",
            "source": "INSEE - Données générales comparatives (RP 2011–2022)",
            "lien": "https://www.insee.fr/fr/statistiques/1405599?geo=EPCI-200040715+EPCI-243500139",
        },
        {
            "titre": "Structure par âge",
            "description": "Pyramides des âges, part des jeunes, actifs et seniors.",
            "source": "INSEE - Population par tranche d'âge (RP 2011–2022)",
            "lien": "https://www.insee.fr/fr/statistiques/1893204",
        },
        {
            "titre": "Mobilités résidentielles",
            "description": "Flux de migrations résidentielles entre communes et métropoles.",
            "source": "INSEE - Migrations résidentielles 2019–2022",
            "lien": "https://www.insee.fr/fr/statistiques/8582988",
        },
        {
            "titre": "Mobilités professionnelles",
            "description": "Déplacements domicile-travail à l'échelle des métropoles.",
            "source": "INSEE - Mobilité professionnelle 2019–2022",
            "lien": "https://www.insee.fr/fr/statistiques/8582949",
        },
        {
            "titre": "Mobilités scolaires",
            "description": "Flux de déplacements vers les établissements scolaires.",
            "source": "INSEE - Mobilité scolaire 2019–2022",
            "lien": "https://www.insee.fr/fr/statistiques/8582969",
        },
        {
            "titre": "Ménages",
            "description": "Taille et composition des ménages selon l'âge et la CSP.",
            "source": "INSEE - Ménages par âge et situation (RP 2011–2022)",
            "lien": "https://www.insee.fr/fr/statistiques/8582448",
        },
        {
            "titre": "Population active 25-54 ans",
            "description": "Structure socioprofessionnelle et indice de spécialisation entre métropoles.",
            "source": "INSEE - Population 25-54 ans par CSP et diplôme (RP 2011–2022)",
            "lien": "https://www.insee.fr/fr/statistiques/1893185",
        },
    ]

    for onglet in demo_onglets:
        with st.expander(onglet["titre"]):
            st.markdown(onglet["description"])
            st.markdown(f"**Source :** {onglet['source']} · [🔗 Accéder]({onglet['lien']})")

    st.markdown("---")

    st.markdown("### Thématique 2 - Solidarité & citoyenneté")

    solid_onglets = [
        {
            "titre": "Solidarité",
            "description": "Analyse des données CAF : foyers bénéficiaires, montants versés, évolution temporelle.",
            "sources": [
                ("INSEE - Filosofi : âge, type de ménage, niveau de vie", "https://catalogue-donnees.insee.fr/fr/catalogue/recherche/DS_FILOSOFI_AGE_TP_NIVVIE"),
                ("CAF - Allocataires par commune (NDUR)", "https://data.caf.fr/explore/dataset/ndur_s_qf_400_com_f/table/"),
                ("CAF - Bénéficiaires par commune (complément)", "https://data.caf.fr/explore/dataset/s_ben_com_f/table/"),
                ("INSEE - Données générales comparatives EPCI", "https://www.insee.fr/fr/statistiques/1405599?geo=EPCI-200040715+EPCI-243500139"),
            ],
        },
        {
            "titre": "Éducation",
            "description": "Analyse des niveaux de diplôme et de la scolarisation par métropole.",
            "sources": [
                ("INSEE - Statistiques locales (diplômes, scolarisation)", "https://www.insee.fr/fr/statistiques/8307327?sommaire=2500477"),
            ],
        },
        {
            "titre": "Santé",
            "description": "Cartographie et analyse des équipements de santé.",
            "sources": [
                ("OpenData - Équipements de santé OSM France", "https://smartregionidf.opendatasoft.com/explore/dataset/osm-france-healthcare/table/"),
            ],
        },
        {
            "titre": "Participation citoyenne",
            "description": "Taux de participation et résultats des élections municipales 2020.",
            "sources": [
                ("Data.gouv - Élections municipales 2020 (1er tour)", "https://www.data.gouv.fr/datasets/elections-municipales-2020-resultats-1er-tour/"),
            ],
        },
        {
            "titre": "Revenus & pauvreté",
            "description": "...",
            "sources": [
                ("...", "..."),
            ],
        },
    ]

    for onglet in solid_onglets:
        with st.expander(onglet["titre"]):
            st.markdown(onglet["description"])
            for source, lien in onglet["sources"]:
                st.markdown(f"**Source :** {source} · [🔗 Accéder]({lien})")

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
                    ["Comparaison Métropoles", "Détail Communal (Grenoble)"],
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
                    "Communes de Grenoble", sorted(COMMUNES["Grenoble"]),
                    default=sorted(COMMUNES["Grenoble"])[:2], key="pop_communes",
                    help="Sélection des communes utilisées pour les comparaisons d'indicateurs 2022.",
                )
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("---")

        # ════════════════════════════════════════════════════════════════════
        # VUE DÉTAIL COMMUNAL (Grenoble)
        # ════════════════════════════════════════════════════════════════════
        if mode_pop == "Détail Communal (Grenoble)":
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
                    fig_dens_c.update_traces(textposition="top center", textfont_size=10)
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
                        "Solde naturel": "#74C69D",
                        "Solde migratoire": "#2D6A4F",
                        "Variation totale": "#1B4332",
                    }
                    fig_comp_c = px.bar(
                        df_comp_c, x="Commune", y="Taux (%/an)", color="Composante",
                        barmode="group", color_discrete_map=COLOR_COMP, height=360,
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
                    "Naissances & Décès (radar comparatif)",
                    help="Compare l'intensité des naissances et des décès pour 1 000 habitants. L'accroissement naturel est la différence naissances – décès.",
                )
                rows_vit_c = []
                for comm in sel_communes_pop:
                    nais = commune_val(comm, "naissances_2024")
                    decs = commune_val(comm, "deces_2024")
                    pop  = commune_val(comm, "population_2022")
                    if not any(np.isnan(v) for v in [nais, decs, pop]) and pop > 0:
                        rows_vit_c.append({
                            "Commune": comm,
                            "Naissances/1 000 hab": nais / pop * 1000,
                            "Décès/1 000 hab": decs / pop * 1000,
                            "Accroissement naturel": (nais - decs) / pop * 1000,
                        })
                if rows_vit_c:
                    df_vit_c = pd.DataFrame(rows_vit_c)
                    fig_vit_c = go.Figure()
                    categories = ["Naissances/1 000 hab", "Décès/1 000 hab", "Accroissement naturel"]
                    for idx_c, row_v in df_vit_c.iterrows():
                        fig_vit_c.add_trace(go.Scatterpolar(
                            r=[row_v[c] for c in categories] + [row_v[categories[0]]],
                            theta=categories + [categories[0]],
                            fill="toself", name=row_v["Commune"],
                            line_color=COLORS_COMM[idx_c % len(COLORS_COMM)], opacity=0.75,
                        ))
                    fig_vit_c.update_layout(
                        polar=dict(radialaxis=dict(visible=True)),
                        legend=dict(orientation="h", y=-0.15), height=360,
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


                html_card = f"""
                <div style='display: flex; flex-direction: column; justify-content: center; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 6px rgba(0,0,0,0.1); background: #fff; min-height: 80px; border-left: 6px solid #2D6A4F; padding: 12px 16px; margin-bottom: 10px;'>
                    <div style='font-size:11px; font-weight:700; letter-spacing:0.08em; color:#666; text-transform:uppercase;'> {m}</div>
                    <div style='font-size:24px; font-weight:bold; color:#1C3A27; margin: 4px 0;'>{fmt(pop22)}</div>
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
                    fig_dens.update_traces(textposition="top center", textfont_size=11)
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
                        "Solde naturel": "#74C69D",
                        "Solde migratoire": "#2D6A4F",
                        "Variation totale": "#1B4332",
                    }
                    fig_comp = px.bar(
                        df_comp, x="Métropole", y="Taux (%/an)", color="Composante",
                        barmode="group", color_discrete_map=COLOR_COMP, height=360,
                    )
                    fig_comp.add_hline(y=0, line_dash="dot", line_color="#AAAAAA")
                    fig_comp.update_layout(
                        xaxis_title="Métropole", yaxis_title="Taux (%/an)",
                        legend=dict(orientation="h", y=1.12),
                    )
                    st.plotly_chart(style(fig_comp), use_container_width=True)

            with r2c2:
                st.subheader(
                    "Naissances & Décès 2024 (radar comparatif)",
                    help="Compare l'intensité des naissances et des décès pour 1 000 habitants. L'accroissement naturel est la différence naissances – décès.",
                )
                rows_vit = []
                for m in sel:
                    nais = epci_val(m, "naissances_2024")
                    decs = epci_val(m, "deces_2024")
                    pop  = epci_val(m, "population_2022")
                    if not any(np.isnan(v) for v in [nais, decs, pop]):
                        rows_vit.append({
                            "Métropole": m,
                            "Naissances/1 000 hab": nais / pop * 1000,
                            "Décès/1 000 hab": decs / pop * 1000,
                            "Accroissement naturel": (nais - decs) / pop * 1000,
                        })
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
                    fig_vit.update_layout(
                        polar=dict(radialaxis=dict(visible=True)),
                        legend=dict(orientation="h", y=-0.15), height=360,
                    )
                    st.plotly_chart(style(fig_vit), use_container_width=True)

            with st.expander("💡 Comment interpréter ces deux graphiques ?"):
                st.write("Des soldes positifs traduisent une dynamique démographique favorable. Le radar permet de visualiser simultanément trois composantes et d'identifier les métropoles dont la croissance est portée par les naissances plutôt que par l'attractivité migratoire.")

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
                        ["Comparaison Métropoles", "Détail Communal (Grenoble)"],
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
                        "Communes de Grenoble",
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

                # ── Pyramides ─────────────────────────────────────────────
                st.subheader("Pyramides des âges comparées",
                             help="Compare la répartition hommes/femmes par tranche d'âge.")

                COLORS_METRO_H = {"Grenoble": "#2D6A4F", "Rennes": "#1A6FA3",
                                  "Saint-Étienne": "#C45B2A", "Rouen": "#7B3FA0",
                                  "Montpellier": "#D4A017"}
                COLORS_METRO_F = {"Grenoble": "#95D5B2", "Rennes": "#AED4F0",
                                  "Saint-Étienne": "#F2A07A", "Rouen": "#C9A5E0",
                                  "Montpellier": "#F5D87A"}

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
                        st.plotly_chart(style(px.line(df_ev, x="Année", y="Part (%)", color="Métropole",
                                                      markers=True, color_discrete_map=COULEURS)))

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
                        st.plotly_chart(style(px.line(df_ev, x="Année", y="Part (%)", color="Métropole",
                                                      markers=True, color_discrete_map=COULEURS)))

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
            # ── Suppression effet hover radio ────────────────────────────────
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
                        ["Comparaison Métropoles", "Détail Communal"],
                        key="mob_mode",
                        horizontal=True,
                        help="Choisissez si vous voulez voir les communes de Grenoble ou comparer Grenoble aux autres métropoles."
                    )

                # ── LIGNE 2 : Sélection des entités (métropoles ou communes) ─
                if mode_mob == "Détail Communal":
                    met_choice = "Grenoble"
                    st.markdown(f"**Communes de la métropole : {met_choice}**")
                    sel_communes_mob = st.multiselect(
                        "Sélection des communes",
                        sorted(COMMUNES[met_choice]),
                        default=sorted(COMMUNES[met_choice])[:2],
                        key="mob_communes"
                    )
                    coms_selection = sel_communes_mob
                    if len(sel_communes_mob) > 1:
                        txt_aide_geo = f"Analyse des flux cumulés pour le groupe : {', '.join(sel_communes_mob)}."
                    else:
                        txt_aide_geo = "Quelles sont les communes qui interagissent le plus avec votre sélection ?"
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

                # Logique des couleurs et labels (dépend de theme_mob)
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

                st.markdown('</div>', unsafe_allow_html=True)

            # ── Calculs ──────────────────────────────────────────────────────
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
            else:
                for m_name in sel_metros_mob:
                    coms = COMMUNES[m_name]
                    f_in  = df_mob_filtered[df_mob_filtered[col_dest].isin(coms)]["flux"].sum()
                    f_out = df_mob_filtered[df_mob_filtered[col_orig].isin(coms)]["flux"].sum()
                    entities_mob.append({"name": m_name, "in": f_in, "out": f_out, "solde": f_in - f_out})
            df_plot_mob = pd.DataFrame(entities_mob)

            # ── Affichage Principal ───────────────────────────────────────────
            if not df_plot_mob.empty:
                st.markdown(
                    f"#### 📌 Bilan net - {theme_mob} ({sel_annee_mob})",
                    help="Le bilan net (solde) est la différence entre ceux qui arrivent et ceux qui partent. Un chiffre positif indique une attractivité."
                )

                # KPI cards — bordure verte à GAUCHE uniquement
                kpi_cols = st.columns(len(df_plot_mob))
                for i, row in df_plot_mob.iterrows():
                    color_solde = "#2ecc71" if row["solde"] >= 0 else "#e74c3c"
                    with kpi_cols[i]:
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
                            border-left: 6px solid #1a7a4a;
                        '>
                            <div style='
                                padding: 10px 16px;
                                display: flex;
                                flex-direction: column;
                                justify-content: center;
                            '>
                                <div style='font-size:11px; font-weight:700; letter-spacing:0.08em; color:#666; text-transform:uppercase;'>{row['name']}</div>
                                <div style='font-size:24px; font-weight:bold; color:#111;'>{int(row['solde']):+,d}</div>
                                <div style='color:{color_solde}; font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.05em;'>SOLDE</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                st.markdown("---")

                c1, c2 = st.columns(2)
                with c1:
                    # CORRECTION ICI : Utilisation de ##### en Markdown pur au lieu de <h5> en HTML
                    st.markdown(
                        "##### ⚖️ Volume des échanges",
                        help="Compare les entrées (foncé) et les sorties (clair). Si les deux barres sont hautes, la commune est un pôle d'échange majeur."
                    )
                    fig_vol = go.Figure()
                    fig_vol.add_trace(go.Bar(
                        x=df_plot_mob["name"], y=df_plot_mob["in"],
                        name=label_in, marker_color=color_in
                    ))
                    fig_vol.add_trace(go.Bar(
                        x=df_plot_mob["name"], y=df_plot_mob["out"],
                        name=label_out, marker_color=color_out
                    ))
                    fig_vol.update_layout(
                        barmode="group",
                        height=350,
                        margin=dict(t=20, b=60),
                        legend=dict(orientation="h", y=1.2),
                        xaxis=dict(title="Territoire", showgrid=False),
                        yaxis=dict(title="Nombre de flux", showgrid=True, gridcolor="#eeeeee")
                    )
                    st.plotly_chart(fig_vol, use_container_width=True)

                with c2:
                    # CORRECTION ICI : Utilisation de ##### en Markdown pur au lieu de <h5> en HTML
                    st.markdown(
                        "##### 🎯 Performance nette",
                        help="Visualisation directe du gain ou de la perte. Utile pour classer les territoires du plus attractif au moins attractif."
                    )
                    fig_net = px.bar(
                        df_plot_mob, x="name", y="solde",
                        color="solde", color_continuous_scale="RdYlGn"
                    )
                    fig_net.add_hline(y=0, line_dash="dash", line_color="black")
                    fig_net.update_layout(
                        coloraxis_showscale=False,
                        height=350,
                        margin=dict(t=20, b=60),
                        xaxis=dict(title="Territoire", showgrid=False),
                        yaxis=dict(title="Solde (entrées - sorties)", showgrid=True, gridcolor="#eeeeee")
                    )
                    st.plotly_chart(fig_net, use_container_width=True)

                with st.expander("💡 Comment interpréter ces deux graphiques ?"):
                    st.write("""
                    - **Si le volume est élevé mais le solde est proche de zéro** : La commune "brasse" beaucoup de monde (ex: ville étape) mais ne retient pas de population.
                    - **Si le solde est très positif** : Le territoire est un 'aspirateur'. En résidentiel, cela signifie qu'il est très demandé. En professionnel, qu'il est un moteur d'emploi régional.
                    """)

                st.markdown("---")
                st.markdown("#### 🔍 Analyse géographique des partenaires", help=txt_aide_geo)

                if mode_mob == "Détail Communal" and len(sel_communes_mob) > 1:
                    st.info(f"💡 **Analyse de groupe** : Les graphiques ci-dessous affichent les partenaires cumulés pour : {', '.join(sel_communes_mob)}.")

                col_l, col_r = st.columns(2)
                with col_l:
                    st.markdown(
                        f"<h5 style='text-align:center;'>📍 Top 10 provenances ({label_in})</h5>",
                        unsafe_allow_html=True
                    )
                    top_in = df_mob_filtered[df_mob_filtered[col_dest].isin(coms_selection)].nlargest(10, "flux")
                    if not top_in.empty:
                        fig_in = px.bar(
                            top_in, x="flux", y=col_orig,
                            orientation="h",
                            color_discrete_sequence=[color_in],
                            text_auto=".0f"
                        )
                        fig_in.update_layout(
                            yaxis=dict(categoryorder="total ascending", title="Commune d'origine"),
                            xaxis=dict(title="Nombre de flux"),
                            height=350,
                            margin=dict(t=20, b=60)
                        )
                        st.plotly_chart(fig_in, use_container_width=True)

                with col_r:
                    st.markdown(
                        f"<h5 style='text-align:center;'>🚩 Top 10 destinations ({label_out})</h5>",
                        unsafe_allow_html=True
                    )
                    top_out = df_mob_filtered[df_mob_filtered[col_orig].isin(coms_selection)].nlargest(10, "flux")
                    if not top_out.empty:
                        fig_out = px.bar(
                            top_out, x="flux", y=col_dest,
                            orientation="h",
                            color_discrete_sequence=[color_out],
                            text_auto=".0f"
                        )
                        fig_out.update_layout(
                            yaxis=dict(categoryorder="total ascending", title="Commune de destination"),
                            xaxis=dict(title="Nombre de flux"),
                            height=350,
                            margin=dict(t=20, b=60)
                        )
                        st.plotly_chart(fig_out, use_container_width=True)

                with st.expander("❓ Comment lire ces graphiques quand plusieurs communes sont choisies ?"):
                    st.write("""
                    Lorsque vous sélectionnez plusieurs communes, l'outil traite la sélection comme un **territoire unique**. 
                    - Les flux internes entre les communes sélectionnées sont ignorés pour mettre en avant les échanges avec **l'extérieur**.
                    - Cela permet de voir si un groupement de communes dépend d'un même pôle d'attraction (ex: Lyon, Paris ou une autre zone de la métropole).
                    """)
                    
# ==============================================================================
# ONGLET 4 - MÉNAGES
# ==============================================================================
if vue == "Démographie":
    with tab4:
        sous1, sous2 = st.tabs(["👨‍👩‍👧 Type & taille de ménage", "🧑‍💼 CSP des ménages"])

        with sous1:
            if df_men_age is None:
                st.info("📂 Fichier `Menage_age_situation_clean.csv` introuvable.")
            else:
                # ── Bandeau filtres ──────────────────────────────────────────
                with st.container():
                    
                    filter_bar("Filtres - Type & taille de ménage")
                    fm1, fm2 = st.columns([1, 3])
                    with fm1:
                        filter_row_label("Niveau géographique")
                    with fm2:
                        mode_men = st.radio(
                            "",
                            ["Comparaison Métropoles", "Détail Communal"],
                            key="men_mode", horizontal=True,
                            help="Choisissez une vue globale métropole ou un détail communal.",
                        )
                    metro_men = st.selectbox("Métropole parente", TOUTES, key="m_men",
                                             help="Métropole de référence pour les données ménages.")
                    if mode_men == "Détail Communal":
                        cmns_men = sorted(COMMUNES.get(metro_men, []))
                        sel_communes_men = st.multiselect(
                            "Communes", cmns_men, default=cmns_men[:2], key="men_communes",
                            help="Communes sélectionnées pour la vue détail.",
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
                    st.subheader("📌 Indicateurs clés des ménages", help="Volume total de ménages et taille moyenne.")
                    k1, k2 = st.columns(2)
                    k1.metric(f"Nombre de ménages - {metro_men}", fmt(nb_men))
                    k2.metric("Taille moyenne du ménage", f"{taille:.2f} pers." if not np.isnan(taille) else "N/D")
                    st.markdown("---")
                    totaux = {lbl: df_men_m[[c for c in cols if c in df_men_m.columns]].sum().sum()
                              for lbl, cols in TYPE_GROUPES.items()}
                    df_t = pd.DataFrame(list(totaux.items()), columns=["Type", "Ménages"])
                    df_t = df_t[df_t["Ménages"] > 0].sort_values("Ménages", ascending=False)
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"##### Types de ménages - {metro_men}")
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
                    with st.expander("💡 Comment interpréter ces deux graphiques ?"):
                        st.write("Le bar chart classe les types en volume ; le camembert indique leur poids relatif dans l'ensemble des ménages.")
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
                        with st.expander("💡 Comment interpréter ce graphique ?"):
                            st.write("Chaque barre représente un âge du référent ; les couleurs montrent quels types de ménages dominent selon l'âge.")

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
                                st.markdown(f"##### Types de ménages - {comm}")
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
                            st.markdown(f"##### Comparaison - {' · '.join(communes_men)}")
                            fig_ccp = px.bar(df_ccp, x="Type", y="Ménages", color="Commune",
                                             barmode="group",
                                             color_discrete_sequence=["#2D6A4F", "#95D5B2", "#1A6FA3",
                                                                       "#C45B2A", "#D4A017"])
                            fig_ccp.update_layout(xaxis_tickangle=-20, legend=dict(orientation="h"))
                            st.plotly_chart(style(fig_ccp), use_container_width=True)
                            with st.expander("💡 Comment interpréter ce graphique ?"):
                                st.write("Pour chaque type de ménage, compare la hauteur des barres pour voir les écarts entre communes.")
                        else:
                            st.info("Données non disponibles pour ces communes.")

        with sous2:
            if df_men_csp is None:
                st.info("📂 Fichier `Menages_csp_nbpers_clean.csv` introuvable.")
            else:
                # ── Bandeau filtres ──────────────────────────────────────────
                with st.container():
                    
                    filter_bar("Filtres - CSP des ménages")
                    fc1, fc2 = st.columns([2, 2])
                    with fc1:
                        metro_csp_m = st.selectbox("Métropole", TOUTES, key="m_csp",
                                                   help="Métropole analysée pour la répartition des ménages par CSP.")
                    with fc2:
                        comp_csp = st.checkbox("Comparer toutes les métropoles (%)", key="comp_csp",
                                               help="Active une vue en pourcentage pour comparer les structures entre métropoles.")
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
                            st.markdown(f"##### Ménages par CSP - {metro_csp_m}")
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
                        with st.expander("💡 Comment interpréter ces deux graphiques ?"):
                            st.write("Le graphique en barres donne les volumes par CSP ; le camembert montre la structure relative des ménages.")
                else:
                    st.markdown("##### Part des grandes CSP - toutes métropoles (%)")
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
                    with st.expander("💡 Comment interpréter ce graphique ?"):
                        st.write("Chaque barre vaut 100% : compare la composition des CSP entre métropoles, indépendamment de leur taille.")
                    
# ==============================================================================
# ONGLET 5 - CSP COMPARATIF
# ==============================================================================
if vue == "Démographie":
    with tab6:

        if df_csp_new.empty or "ANNEE" not in df_csp_new.columns:
            st.info("📂 Données CSP/Diplôme non trouvées. Vérifiez les chemins FILES_CSP / FILES_DIP.")
        else:
            # ── Bandeau filtres ──────────────────────────────────────────────
            with st.container():
                
                filter_bar("Filtres - Population active 25-54 ans")
                csp_geo_l, csp_geo_r = st.columns([1, 3])
                with csp_geo_l:
                    filter_row_label("Niveau géographique")
                with csp_geo_r:
                    mode_analyse = st.radio("",
                                            ["Comparaison Métropoles", "Détail Communal"],
                                            key="csp_mode", horizontal=True,
                                            help="Choisissez une analyse à l'échelle communale ou métropolitaine.")
                csp_row1_c1, csp_row1_c2 = st.columns(2)
                with csp_row1_c1:
                    theme_analyse = st.selectbox(
                        "Thématique",
                        ["Secteurs d'activité (CSP)", "Niveau de diplôme"],
                        key="csp_theme",
                        help="Choix de la famille d'indicateurs comparés.",
                    )
                current_df_csp  = df_csp_new if theme_analyse == "Secteurs d'activité (CSP)" else df_dip_new
                current_map_csp = CSP_MAP_NEW if theme_analyse == "Secteurs d'activité (CSP)" else DIP_MAP

                annees_csp = sorted(current_df_csp["ANNEE"].dropna().unique(), reverse=True) if not current_df_csp.empty else []
                with csp_row1_c2:
                    sel_annee_csp = st.selectbox("Année", annees_csp, key="csp_annee",
                                                 help="Année de comparaison.") if annees_csp else None

                if mode_analyse == "Par Communes (Grenoble)":
                    clist = sorted(COMMUNES["Grenoble"])
                    sel_communes_csp = st.multiselect("Communes (Grenoble)", clist,
                                                      default=["Grenoble"], key="csp_communes",
                                                      help="Communes comparées dans la métropole de Grenoble.")
                else:
                    sel_metros_csp = st.multiselect("Métropoles", TOUTES,
                                                    default=["Grenoble", "Rouen"], key="csp_metros",
                                                    help="Métropoles retenues pour la comparaison.")

                sel_cats = st.multiselect("Catégories à afficher",
                                          options=list(current_map_csp.values()),
                                          default=list(current_map_csp.values()),
                                          key="csp_cats",
                                          help="Indicateurs affichés dans les graphiques et tableaux.")

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
                        f"{theme_analyse} - {noms} · {sel_annee_csp}</h2>",
                        unsafe_allow_html=True,
                    )
                    st.caption("ℹ️ Survolez les aides (?) des titres pour comprendre les indicateurs.")

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
                        st.subheader("Répartition en volume", help="Compare les effectifs absolus par catégorie.")
                        fig_bar_csp = go.Figure()
                        for ent in entities_csp:
                            fig_bar_csp.add_trace(go.Bar(
                                x=sel_cats, y=ent["data"][sel_cats],
                                name=ent["name"], marker_color=COULEURS.get(ent["name"], "#3498db"),
                            ))
                        fig_bar_csp.update_layout(barmode="group",
                                                  height=420, legend=dict(orientation="h", y=1.12),
                                                  xaxis_tickangle=-30)
                        st.plotly_chart(style(fig_bar_csp, 50), use_container_width=True)
                    with c2:
                        st.subheader("Profil structurel (%)", help="Compare la composition relative de chaque territoire.")
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
                            polar=dict(radialaxis=dict(visible=True, range=[0, max(max_pct * 1.2, 10)])),
                            legend=dict(orientation="h", y=-0.15), height=420,
                        )
                        st.plotly_chart(style(fig_radar_csp, 50), use_container_width=True)
                    with st.expander("💡 Comment interpréter ces deux graphiques ?"):
                        st.write("Le graphique en volume montre les effectifs bruts ; le radar montre la spécialisation relative en pourcentage.")

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
                        k1.metric(f"Actifs - {entities_csp[0]['name']}", f"{int(t1):,}".replace(",", "\u202f"))
                        k2.metric(f"Actifs - {entities_csp[1]['name']}", f"{int(t2):,}".replace(",", "\u202f"))
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
                                f"{entities_csp[0]['name']} - Effectif": [int(v1[c]) for c in sel_cats],
                                f"{entities_csp[1]['name']} - Effectif": [int(v2[c]) for c in sel_cats],
                                "Différence": [int(v1[c] - v2[c]) for c in sel_cats],
                                "Indice spécialisation": [round(spec[c], 1) for c in sel_cats],
                            })
                            st.dataframe(table_df, use_container_width=True)

                    elif len(entities_csp) > 2:
                        st.markdown("---")
                        st.markdown("#### Tableau récapitulatif")
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
    # ONGLET SOLIDARITÉ - CAF
    # ──────────────────────────────────────────────────────────────────────────
    with s1:
        st.markdown(
            '<p class="source-note">Source : <a href="https://data.caf.fr" target="_blank">' +
            "Caisse d\'Allocations Familiales - CAF 5 Métropoles 2020–2023</a></p>",
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
                    "Nombre foyers NDUR":        "Foyers - Toutes aides",
                    "Nombre personnes NDUR":     "Personnes - Toutes aides",
                    "Montant total NDUR":        "Montant total (€) - Toutes aides",
                    "Nombre foyers NDURPAJE":    "Foyers - PAJE",
                    "Nombre personnes NDURPAJE": "Personnes - PAJE",
                    "Montant total NDURPAJE":    "Montant (€) - PAJE",
                    "Nombre foyers NDUREJ":      "Foyers - Aide jeunes enfants",
                    "Nombre personnes NDUREJ":   "Personnes - Aide jeunes enfants",
                    "Montant total NDUREJ":      "Montant (€) - Aide jeunes enfants",
                    "Nombre foyers NDURAL":      "Foyers - Allocation logement",
                    "Nombre personnes NDURAL":   "Personnes - Allocation logement",
                    "Montant total NDURAL":      "Montant (€) - Allocation logement",
                    "Nombre foyers NDURINS":     "Foyers - Insertion sociale",
                    "Nombre personnes NDURINS":  "Personnes - Insertion sociale",
                    "Montant total NDURINS":     "Montant (€) - Insertion sociale",
                }
                available_metrics = {k: v for k, v in ALL_METRIC_LABELS.items() if k in df_caf.columns}
                if not available_metrics:
                    st.warning("Aucune mesure CAF trouvée.")
                else:
                    for col in available_metrics:
                        df_caf[col] = pd.to_numeric(df_caf[col], errors="coerce").fillna(0)
                    years_caf  = sorted(df_caf["Annee"].dropna().unique())
                    agglos_caf = sorted(df_caf["Agglomeration"].dropna().unique())

                    with st.container():
                        
                        filter_bar("Filtres - Solidarité CAF")
                        caf_f1, caf_f2, caf_f3 = st.columns([1, 1, 2])
                        
                        with caf_f1:
                            metric_key = st.selectbox("Indicateur", list(available_metrics.keys()),
                                                    format_func=lambda k: available_metrics[k], index=0, key="caf_metric")
                        with caf_f2:
                            year_caf = st.selectbox("Année", years_caf, index=len(years_caf)-1, key="caf_year")
                        with caf_f3:
                            mode_caf = st.radio("Niveau géographique", ["Comparaison Métropoles", "Détail Communal (Grenoble)"], key="caf_mode", horizontal=True)

                        if mode_caf == "Comparaison Métropoles":
                            sel_agglos_caf = st.multiselect("Agglomérations", agglos_caf, default=agglos_caf, key="caf_agglos")
                        else:
                            gre_agglo = next((a for a in agglos_caf if "Grenoble" in a), "Grenoble Alpes Métropole")
                            communes_gre_caf = sorted(df_caf[df_caf["Agglomeration"] == gre_agglo]["Nom_Commune"].dropna().unique()) if "Nom_Commune" in df_caf.columns else []
                            sel_communes_caf = st.multiselect("Communes de Grenoble", communes_gre_caf, default=communes_gre_caf[:2] if communes_gre_caf else [], key="caf_communes")
                        st.markdown('</div>', unsafe_allow_html=True)

                    if mode_caf == "Comparaison Métropoles":
                        if not sel_agglos_caf:
                            st.warning("⚠️ Sélectionnez au moins une agglomération.")
                        else:
                            metric       = metric_key
                            label_metric = available_metrics[metric]
                            df_fil = df_caf[df_caf["Agglomeration"].isin(sel_agglos_caf)]
                            df_yr  = df_fil[df_fil["Annee"] == year_caf]

                            st.markdown("---")
                            
                            total_val = df_yr[metric].sum()
                            nb_agglo  = int(df_yr["Agglomeration"].nunique())
                            nb_com    = int(df_yr["Nom_Commune"].nunique()) if "Nom_Commune" in df_yr.columns else 0
                            max_agglo = df_yr.groupby("Agglomeration")[metric].sum().idxmax() if not df_yr.empty else "-"

                            k1, k2, k3, k4 = st.columns(4)
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
                                    # Fix de la couleur pour coller au dictionnaire des villes de l'agglo
                                    qf_data["Metropole_Key"] = qf_data["Agglomeration"].apply(lambda x: next((m for m in COULEURS.keys() if m in x), x))

                                    fig_qf = px.bar(qf_data.sort_values("QF_ord"), x="Agglomeration", y=metric,
                                        color="Quotient familial", barmode="stack",
                                        color_discrete_sequence=px.colors.sequential.Greens_r,
                                        labels={"Agglomeration": "", metric: label_metric},
                                        title="Composition par quotient familial", height=380)
                                    st.plotly_chart(style(fig_qf, 40), use_container_width=True)
                            with c4:
                                st.markdown(f"##### 🏆 Top 15 communes - {year_caf}")
                                if "Nom_Commune" in df_yr.columns:
                                    top15 = df_yr.groupby(["Nom_Commune","Agglomeration"], as_index=False)[metric].sum().nlargest(15, metric)
                                    top15["Metropole_Key"] = top15["Agglomeration"].apply(lambda x: next((m for m in COULEURS.keys() if m in x), x))
                                    fig_top = px.bar(top15, x=metric, y="Nom_Commune", orientation="h",
                                        color="Metropole_Key", color_discrete_map=COULEURS, text_auto=".3s",
                                        labels={"Nom_Commune": "", metric: label_metric, "Metropole_Key": "Métropole"},
                                        title=f"Top 15 communes - {label_metric}", height=420)
                                    fig_top.update_layout(yaxis={"categoryorder": "total ascending"})
                                    st.plotly_chart(style(fig_top, 40), use_container_width=True)
                            st.markdown("---")

                            st.markdown("##### 🕸️ Profil comparatif des aides - radar")
                            aides_f = {"Foyers PAJE":"Nombre foyers NDURPAJE","Foyers aj. enf.":"Nombre foyers NDUREJ",
                                "Foyers alloc. log.":"Nombre foyers NDURAL","Foyers insertion":"Nombre foyers NDURINS",
                                "Foyers total":"Nombre foyers NDUR"}
                            aides_d = {k: v for k, v in aides_f.items() if v in df_yr.columns}
                            if len(aides_d) >= 3:
                                rdata = df_yr.groupby("Agglomeration")[list(aides_d.values())].sum().reset_index()
                                rdata.columns = ["Agglomeration"] + list(aides_d.keys())
                                rdata["Metropole_Key"] = rdata["Agglomeration"].apply(lambda x: next((m for m in COULEURS.keys() if m in x), x))
                                fig_radar = go.Figure()
                                cats_r = list(aides_d.keys())
                                for _, rr in rdata.iterrows():
                                    vv = [rr[c] for c in cats_r] + [rr[cats_r[0]]]
                                    fig_radar.add_trace(go.Scatterpolar(r=vv, theta=cats_r+[cats_r[0]],
                                        fill="toself", name=rr["Metropole_Key"],
                                        line_color=COULEURS.get(rr["Metropole_Key"], "#999")))
                                fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True)), height=420,
                                    title=f"Profil des aides - {year_caf}", font_family="Sora",
                                    paper_bgcolor="rgba(0,0,0,0)")
                                st.plotly_chart(fig_radar, use_container_width=True)
                            st.markdown("---")
                            with st.expander("📄 Données détaillées"):
                                st.dataframe(df_yr.groupby(
                                    ["Agglomeration","Quotient familial"] if "Quotient familial" in df_yr.columns else ["Agglomeration"],
                                    as_index=False)[list(available_metrics.keys())].sum(), use_container_width=True)
                            with st.expander("📖 Note méthodologique"):
                                st.write("**Sources** : CAF - données communales 2020–2023.\n\n"
                                    "**NDUR** : dossiers unifiés réels. **NDURPAJE** : prestation jeune enfant. "
                                    "**NDURAL** : allocation logement. **NDURINS** : insertion sociale (RSA...).")

                    else:
                        if not sel_communes_caf:
                            st.warning("⚠️ Sélectionnez au moins une commune.")
                        else:
                            metric = metric_key
                            label_metric = available_metrics[metric]
                            gre_agglo = next((a for a in agglos_caf if "Grenoble" in a), "Grenoble Alpes Métropole")
                            df_fil = df_caf[(df_caf["Agglomeration"] == gre_agglo) & (df_caf["Nom_Commune"].isin(sel_communes_caf))]
                            df_yr  = df_fil[df_fil["Annee"] == year_caf]

                            st.markdown("---")
                            kpi_cols = st.columns(len(sel_communes_caf))
                            for i, comm in enumerate(sel_communes_caf):
                                val = df_yr[df_yr["Nom_Commune"] == comm][metric].sum() if not df_yr.empty else 0
                                with kpi_cols[i]:
                                    st.metric(label=f" {comm}", value=fmt(val))

                            st.markdown("---")
                            c1, c2 = st.columns(2)
                            with c1:
                                st.markdown(f"##### {label_metric} par commune")
                                fig_ccb = px.bar(df_yr, x="Nom_Commune", y=metric, color="Nom_Commune",
                                                 color_discrete_sequence=px.colors.sequential.Greens_r,
                                                 labels={"Nom_Commune": "", metric: label_metric},
                                                 title=f"Comparaison - {year_caf}", height=400)
                                st.plotly_chart(style(fig_ccb, 40), use_container_width=True)
                            with c2:
                                st.markdown(f"##### 📈 Évolution - {label_metric}")
                                df_evo = df_fil.groupby(["Annee", "Nom_Commune"], as_index=False)[metric].sum()
                                fig_ecc = px.line(df_evo, x="Annee", y=metric, color="Nom_Commune",
                                                  color_discrete_sequence=px.colors.sequential.Greens_r,
                                                  markers=True, title=f"Évolution des aides", height=400)
                                st.plotly_chart(style(fig_ecc, 40), use_container_width=True)

                            if "Quotient familial" in df_caf.columns:
                                st.markdown("---")
                                st.markdown("##### 👨‍👩‍👧 Structure par quotient familial")
                                qf_data = df_yr.groupby(["Nom_Commune", "Quotient familial"], as_index=False)[metric].sum()
                                if not qf_data.empty:
                                    fig_qfcc = px.bar(qf_data, x="Quotient familial", y=metric, color="Nom_Commune", barmode="group",
                                                      color_discrete_sequence=px.colors.sequential.Greens_r,
                                                      labels={"Nom_Commune": "", metric: "Foyers / Montant"},
                                                      title="Répartition par quotient familial", height=380)
                                    fig_qfcc.update_layout(xaxis_tickangle=-30)
                                    st.plotly_chart(style(fig_qfcc, 40), use_container_width=True)

    # ──────────────────────────────────────────────────────────────────────────
    # ONGLET ÉDUCATION - Effectifs étudiants
    # ──────────────────────────────────────────────────────────────────────────
    with s2:
        st.markdown('<p class="source-note">Source : <a href="https://data.enseignementsup-recherche.gouv.fr" target="_blank">' +
            "MESRI - Effectifs dans l\'enseignement supérieur · Communes des 5 métropoles</a></p>",
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

            with st.container():
                
                filter_bar("Filtres - Effectifs enseignement supérieur")
                ef1, ef2, ef3, ef4 = st.columns([1, 1, 1, 1])
                with ef1:
                    mode_eff = st.radio("Niveau géographique", ["Comparaison Métropoles", "Détail Communal (Grenoble)"], key="eff_mode", horizontal=True)
                with ef2:
                    annee_eff = st.selectbox("Année", annees_eff, index=len(annees_eff)-1, key="eff_annee")
                with ef3:
                    regr_choices = ["TOTAL"] + [r for r in regroupements_dispo if r != "TOTAL"]
                    sel_regr = st.selectbox("Type d'établissement", regr_choices,
                        format_func=lambda r: LABEL_REGROUPEMENT.get(r, r), index=0, key="eff_regr")
                with ef4:
                    sel_secteur = st.selectbox("Secteur",
                        ["Tous","Établissements publics","Établissements privés"], key="eff_secteur")
                
                if mode_eff == "Comparaison Métropoles":
                    sel_metros_eff = st.multiselect("Métropoles", metros_eff, default=metros_eff, key="eff_metros")
                else:
                    communes_gre_eff = sorted(df_eff_w[df_eff_w["metropole"] == "Grenoble"]["geo_nom"].dropna().unique())
                    sel_communes_eff = st.multiselect("Communes de Grenoble", communes_gre_eff, default=communes_gre_eff[:2] if communes_gre_eff else [], key="eff_communes")
                st.markdown('</div>', unsafe_allow_html=True)

            if mode_eff == "Comparaison Métropoles":
                if not sel_metros_eff:
                    st.warning("⚠️ Sélectionnez au moins une métropole.")
                else:
                    df_e = df_eff_w[df_eff_w["metropole"].isin(sel_metros_eff) & (df_eff_w["regroupement"]==sel_regr)]
                    if sel_secteur != "Tous":
                        df_e = df_e[df_e["secteur_de_l_etablissement"]==sel_secteur]
                    df_e_yr = df_e[df_e["annee"]==annee_eff]
                    st.markdown("---")

                    total_eff   = int(df_e_yr["effectif"].sum())
                    best_metro  = df_e_yr.groupby("metropole")["effectif"].sum().idxmax() if not df_e_yr.empty else "-"
                    k1, k2, k3, k4 = st.columns(4)
                    k1.metric(f"Effectif total ({annee_eff})", fmt(total_eff))
                    k2.metric("Métropoles", int(df_e_yr["metropole"].nunique()))
                    k3.metric("Communes couvertes", int(df_e_yr["geo_nom"].nunique()))
                    k4.metric("1ère métropole", best_metro)
                    st.markdown("---")

                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"##### 📊 Effectifs par métropole - {annee_eff}")
                        by_metro = df_e_yr.groupby("metropole", as_index=False)["effectif"].sum().sort_values("effectif", ascending=False)
                        fig_em = px.bar(by_metro, x="metropole", y="effectif", color="metropole",
                            color_discrete_map=COULEURS, text_auto=".3s",
                            labels={"metropole":"","effectif":"Étudiants"},
                            title=f"Effectif - {LABEL_REGROUPEMENT.get(sel_regr, sel_regr)} · {annee_eff}", height=380)
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
                            title=f"Répartition par filière - {annee_eff}", hole=0.4,
                            color_discrete_sequence=px.colors.sequential.Greens_r, height=400)
                        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
                        st.plotly_chart(style(fig_pie, 40), use_container_width=True)
                    with c4:
                        st.markdown(f"##### ⚖️ Parité femmes / hommes ({annee_eff})")
                        if "sexe_de_l_etudiant" in df_e_yr.columns:
                            sex_agg = df_e_yr.groupby(["metropole","sexe_de_l_etudiant"], as_index=False)["effectif"].sum()
                            fig_sex = px.bar(sex_agg, x="metropole", y="effectif", color="sexe_de_l_etudiant",
                                barmode="group",
                                color_discrete_map={"Masculin":"#2D6A4F","Feminin":"#95D5B2"},
                                labels={"metropole":"","effectif":"Étudiants","sexe_de_l_etudiant":"Genre"},
                                title=f"Parité H/F - {LABEL_REGROUPEMENT.get(sel_regr, sel_regr)}", height=400)
                            fig_sex.update_layout(legend=dict(orientation="h", y=1.1))
                            st.plotly_chart(style(fig_sex, 40), use_container_width=True)
                    st.markdown("---")

                    c5, c6 = st.columns(2)
                    with c5:
                        st.markdown(f"##### 🏆 Top 15 communes - {annee_eff}")
                        top_com = df_e_yr.groupby(["geo_nom","metropole"], as_index=False)["effectif"].sum().nlargest(15,"effectif")
                        fig_tc = px.bar(top_com, x="effectif", y="geo_nom", orientation="h",
                            color="metropole", color_discrete_map=COULEURS, text_auto=".3s",
                            labels={"geo_nom":"","effectif":"Étudiants"},
                            title=f"Top communes - {annee_eff}", height=430)
                        fig_tc.update_layout(yaxis={"categoryorder":"total ascending"})
                        st.plotly_chart(style(fig_tc, 40), use_container_width=True)
                    with c6:
                        st.markdown(f"##### 🏫 Public vs Privé ({annee_eff})")
                        if "secteur_de_l_etablissement" in df_e_yr.columns:
                            sec_agg = df_e_yr.groupby(["metropole","secteur_de_l_etablissement"], as_index=False)["effectif"].sum()
                            fig_sec = px.bar(sec_agg, x="metropole", y="effectif",
                                color="secteur_de_l_etablissement", barmode="stack",
                                color_discrete_map={"Établissements publics":"#2D6A4F","Établissements privés":"#95D5B2"},
                                labels={"metropole":"","effectif":"Étudiants","secteur_de_l_etablissement":"Secteur"},
                                title=f"Répartition public / privé - {annee_eff}", height=430)
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

            else:
                if not sel_communes_eff:
                    st.warning("⚠️ Sélectionnez au moins une commune.")
                else:
                    df_e = df_eff_w[(df_eff_w["metropole"] == "Grenoble") & (df_eff_w["geo_nom"].isin(sel_communes_eff)) & (df_eff_w["regroupement"]==sel_regr)]
                    if sel_secteur != "Tous":
                        df_e = df_e[df_e["secteur_de_l_etablissement"]==sel_secteur]
                    df_e_yr = df_e[df_e["annee"]==annee_eff]

                    st.markdown("---")
                    kpi_cols = st.columns(len(sel_communes_eff))
                    for i, comm in enumerate(sel_communes_eff):
                        val = df_e_yr[df_e_yr["geo_nom"] == comm]["effectif"].sum() if not df_e_yr.empty else 0
                        with kpi_cols[i]:
                            st.metric(label=f"🎓 {comm}", value=fmt(val))

                    st.markdown("---")
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"##### 📊 Effectifs - {LABEL_REGROUPEMENT.get(sel_regr, sel_regr)}")
                        fig_ccb = px.bar(df_e_yr.groupby("geo_nom", as_index=False)["effectif"].sum(), x="geo_nom", y="effectif", color="geo_nom",
                                         color_discrete_sequence=px.colors.sequential.Greens_r,
                                         labels={"geo_nom": "", "effectif": "Étudiants"},
                                         title=f"Comparaison - {annee_eff}", height=400)
                        st.plotly_chart(style(fig_ccb, 40), use_container_width=True)
                    with c2:
                        st.markdown(f"##### 📈 Évolution - {LABEL_REGROUPEMENT.get(sel_regr, sel_regr)}")
                        df_evo = df_e.groupby(["annee", "geo_nom"], as_index=False)["effectif"].sum()
                        fig_ecc = px.line(df_evo, x="annee", y="effectif", color="geo_nom",
                                          color_discrete_sequence=px.colors.sequential.Greens_r,
                                          labels={"annee": "Année", "effectif": "Étudiants"},
                                          markers=True, title=f"Évolution des effectifs", height=400)
                        st.plotly_chart(style(fig_ecc, 40), use_container_width=True)

                    st.markdown("---")
                    c3, c4 = st.columns(2)
                    with c3:
                        st.markdown("##### 📊 Effectifs par filière")
                        df_fil = df_eff_w[(df_eff_w["metropole"] == "Grenoble") & (df_eff_w["geo_nom"].isin(sel_communes_eff)) & (df_eff_w["annee"] == annee_eff) & (df_eff_w["regroupement"] != "TOTAL")]
                        if sel_secteur != "Tous":
                            df_fil = df_fil[df_fil["secteur_de_l_etablissement"]==sel_secteur]
                        df_fil_agg = df_fil.groupby(["regroupement", "geo_nom"], as_index=False)["effectif"].sum()
                        df_fil_agg["label"] = df_fil_agg["regroupement"].map(lambda r: LABEL_REGROUPEMENT.get(r, r))
                        if not df_fil_agg.empty:
                            fig_fil = px.bar(df_fil_agg, x="effectif", y="label", color="geo_nom", orientation="h", barmode="group",
                                             color_discrete_sequence=px.colors.sequential.Greens_r,
                                             labels={"label": "", "effectif": "Étudiants"},
                                             title="Filières", height=400)
                            st.plotly_chart(style(fig_fil, 40), use_container_width=True)
                    with c4:
                        st.markdown("##### ⚖️ Parité H/F")
                        if "sexe_de_l_etudiant" in df_eff_w.columns:
                            df_sex = df_eff_w[(df_eff_w["metropole"] == "Grenoble") & (df_eff_w["geo_nom"].isin(sel_communes_eff)) & (df_eff_w["annee"] == annee_eff) & (df_eff_w["regroupement"] == sel_regr)]
                            df_sex_agg = df_sex.groupby(["geo_nom", "sexe_de_l_etudiant"], as_index=False)["effectif"].sum()
                            if not df_sex_agg.empty:
                                fig_sex = px.bar(df_sex_agg, x="geo_nom", y="effectif", color="sexe_de_l_etudiant", barmode="group",
                                                 color_discrete_map={"Masculin": "#2D6A4F", "Feminin": "#95D5B2"},
                                                 labels={"geo_nom": "", "effectif": "Étudiants", "sexe_de_l_etudiant": "Genre"},
                                                 title="Parité H/F", height=400)
                                st.plotly_chart(style(fig_sex, 40), use_container_width=True)

        with s3:
            st.markdown(
                '<p class="source-note">Source : OpenStreetMap - Établissements de santé géolocalisés</p>',
                unsafe_allow_html=True,
            )

            # ── Chargement GeoJSON établissements ────────────────────────────────────
            import json

            GEOJSON_PATH = Path("solidarite&citoyennete/data_clean/sante/Etablissements_santé_filtre.geojson")

            # ── Chargement GeoJSON contours métropoles ────────────────────────────────
            # Propriété utilisée : "METROPOLE" (ex : "Grenoble", "Rennes", ...)
            GEOJSON_METROS_PATH = Path("solidarite&citoyennete/data_clean/sante/contour_metropoles.geojson")

            # ── Chargement GeoJSON contours communes de Grenoble ─────────────────────
            # Propriété utilisée : "DCOE_L_LIB" pour le nom de commune
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
                        "nom":       p.get("nom_etablissement") or "-",
                        # ✅ CORRIGÉ : utiliser DCOE_L_LIB pour la commune
                        "commune":   p.get("DCOE_L_LIB", p.get("commune", "")),
                        # ✅ CORRIGÉ : utiliser METROPOLE (majuscules) pour la métropole
                        "metropole": p.get("METROPOLE", p.get("Métropole", p.get("metropole", ""))),
                        "lon":       coords[0],
                        "lat":       coords[1],
                    })
                return pd.DataFrame(rows)

            @st.cache_data
            def charger_geojson_metros():
                if not GEOJSON_METROS_PATH.exists():
                    return None
                with open(GEOJSON_METROS_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)

            @st.cache_data
            def charger_geojson_communes():
                if not GEOJSON_COMMUNES_PATH.exists():
                    return None
                with open(GEOJSON_COMMUNES_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)

            df_sante          = charger_sante()
            geojson_metros    = charger_geojson_metros()
            geojson_communes  = charger_geojson_communes()

            TYPE_LABELS = {
                "pharmacy":    "Pharmacie",
                "doctors":     "Médecins / Soins",
                "dentist":     "Dentiste",
                "hospital":    "Hôpital",
                "nursing_home":"EHPAD / Maison de retraite",
                "clinic":      "Clinique / Centre de santé",
            }

            TYPE_COLORS_GREEN = {
                "pharmacy":    "#1B4332",
                "doctors":     "#2D6A4F",
                "dentist":     "#40916C",
                "hospital":    "#52B788",
                "nursing_home":"#74C69D",
                "clinic":      "#95D5B2",
            }

            metros_sante = sorted(df_sante["metropole"].dropna().unique())
            types_sante  = sorted(df_sante["type_etab"].dropna().unique())

            # ── Filtres ───────────────────────────────────────────────────────────────
            with st.container():

                filter_bar("Filtres - Établissements de santé")
                pv1, pv2, pv3 = st.columns(3)
                with pv1:
                    mode_sante = st.radio(
                        "Niveau géographique",
                        ["Comparaison Métropoles", "Détail Communal"],
                        key="sante_mode", horizontal=True,
                    )
                with pv2:
                    if mode_sante == "Comparaison Métropoles":
                        sel_metros_sante = st.multiselect(
                            "Métropoles",
                            metros_sante,
                            default=metros_sante,
                            key="sante_metros_multi",
                        )
                        if not sel_metros_sante:
                            sel_metros_sante = metros_sante
                    else:
                        st.info("📍 Détail limité à la métropole de **Grenoble**")
                        sel_metros_sante = ["Grenoble"]
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
                        df_sante[df_sante["metropole"] == "Grenoble"]["commune"].dropna().unique()
                    )
                    sel_communes_sante = st.multiselect(
                        "Communes de Grenoble",
                        communes_sante_dispo,
                        default=communes_sante_dispo[:5],
                        key="sante_communes_t1",
                    )
                st.markdown('</div>', unsafe_allow_html=True)

            # ── Filtrage du DataFrame ─────────────────────────────────────────────────
            if mode_sante == "Comparaison Métropoles":
                df_sf = df_sante[
                    (df_sante["metropole"].isin(sel_metros_sante)) &
                    (df_sante["type_etab"].isin(sel_types_sante))
                ].copy()
            else:
                df_sf = df_sante[
                    (df_sante["metropole"] == "Grenoble") &
                    (df_sante["commune"].isin(sel_communes_sante)) &
                    (df_sante["type_etab"].isin(sel_types_sante))
                ].copy()

            # ── KPIs ──────────────────────────────────────────────────────────────────
            sk1, sk2, sk3, sk4, sk5 = st.columns(5)
            sk1.metric("Total établissements", len(df_sf))
            sk2.metric("Pharmacies",           len(df_sf[df_sf["type_etab"] == "pharmacy"]))
            sk3.metric("Médecins / Soins",     len(df_sf[df_sf["type_etab"] == "doctors"]))
            sk4.metric("Hôpitaux",             len(df_sf[df_sf["type_etab"] == "hospital"]))
            sk5.metric("Communes couvertes",   df_sf["commune"].nunique())

            st.markdown("---")

            # ── Calcul du zoom automatique selon l'étendue géographique ──────────────
            def auto_zoom_and_center(df):
                """Retourne (lat_center, lon_center, zoom) en fonction de l'étendue des points."""
                if df.empty:
                    return 46.5, 2.5, 5
                lat_min, lat_max = df["lat"].min(), df["lat"].max()
                lon_min, lon_max = df["lon"].min(), df["lon"].max()
                lat_c = (lat_min + lat_max) / 2
                lon_c = (lon_min + lon_max) / 2
                span = max(lat_max - lat_min, lon_max - lon_min)
                if span < 0.1:
                    zoom = 13
                elif span < 0.3:
                    zoom = 11
                elif span < 1:
                    zoom = 10
                elif span < 3:
                    zoom = 8
                elif span < 6:
                    zoom = 7
                else:
                    zoom = 5
                return lat_c, lon_c, zoom

            lat_c, lon_c, zoom_level = auto_zoom_and_center(df_sf)

            # ── Carte + graphique principal ───────────────────────────────────────────
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
                        color_discrete_map=TYPE_COLORS_GREEN,
                        hover_name="nom",
                        hover_data={"commune": True, "metropole": True, "type_etab": False, "lat": False, "lon": False},
                        labels={"type_etab": "Type", "commune": "Commune", "metropole": "Métropole"},
                        zoom=zoom_level,
                        center={"lat": lat_c, "lon": lon_c},
                        height=480,
                        mapbox_style="carto-positron",
                    )
                    fig_map.update_traces(marker=dict(size=7, opacity=0.85))

                    # ── Contours : métropoles ou communes selon le mode ───────────────
                    if mode_sante == "Comparaison Métropoles" and geojson_metros is not None:
                        # ✅ CORRIGÉ : filtrer sur la clé "METROPOLE" (majuscules)
                        feats_filtrees = [
                            f for f in geojson_metros["features"]
                            if f["properties"].get("METROPOLE") in sel_metros_sante
                        ]
                        geojson_filtre = {"type": "FeatureCollection", "features": feats_filtrees}
                        fig_map.update_layout(
                            mapbox={
                                "layers": [{
                                    "source":  geojson_filtre,
                                    "type":    "line",
                                    "color":   "#2D6A4F",
                                    "line":    {"width": 2},
                                    "opacity": 0.8,
                                }]
                            }
                        )

                    elif mode_sante == "Détail Communal" and geojson_communes is not None:
                        # ✅ CORRIGÉ : filtrer sur la clé "DCOE_L_LIB" (nom de commune réel)
                        feats_filtrees = [
                            f for f in geojson_communes["features"]
                            if f["properties"].get("DCOE_L_LIB") in sel_communes_sante
                        ]
                        geojson_filtre = {"type": "FeatureCollection", "features": feats_filtrees}
                        fig_map.update_layout(
                            mapbox={
                                "layers": [{
                                    "source":  geojson_filtre,
                                    "type":    "line",
                                    "color":   "#40916C",
                                    "line":    {"width": 1.5},
                                    "opacity": 0.9,
                                }]
                            }
                        )

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
                    color="type_etab", color_discrete_map=TYPE_COLORS_GREEN,
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

            # ── Graphiques supplémentaires ────────────────────────────────────────────
            st.markdown("---")
            st.markdown("##### 📈 Analyses complémentaires")

            extra1, extra2 = st.columns(2)

            with extra1:
                if mode_sante == "Comparaison Métropoles":
                    st.markdown("###### Répartition par métropole et type")
                    df_pivot = (
                        df_sf.groupby(["metropole", "type_etab"])
                            .size()
                            .reset_index(name="count")
                    )
                    df_pivot["label"] = df_pivot["type_etab"].map(lambda t: TYPE_LABELS.get(t, t))
                    fig_stack = px.bar(
                        df_pivot,
                        x="metropole", y="count",
                        color="type_etab",
                        color_discrete_map=TYPE_COLORS_GREEN,
                        text="count",
                        labels={"metropole": "Métropole", "count": "Nombre", "type_etab": "Type"},
                        height=380,
                        barmode="stack",
                    )
                    fig_stack.update_traces(textposition="inside", textfont_size=10)
                    for trace in fig_stack.data:
                        trace.name = TYPE_LABELS.get(trace.name, trace.name)
                    fig_stack.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        font_family="Sora",
                        xaxis=dict(tickangle=-30),
                        yaxis=dict(gridcolor="#E8F5EE"),
                        legend=dict(title="Type", font=dict(size=10)),
                        margin=dict(l=10, r=10, t=10, b=60),
                    )
                    st.plotly_chart(style(fig_stack, 40), use_container_width=True)
                else:
                    st.markdown("###### Répartition par commune")
                    df_comm = (
                        df_sf.groupby(["commune", "type_etab"])
                            .size()
                            .reset_index(name="count")
                    )
                    df_comm["label"] = df_comm["type_etab"].map(lambda t: TYPE_LABELS.get(t, t))
                    fig_comm = px.bar(
                        df_comm,
                        x="commune", y="count",
                        color="type_etab",
                        color_discrete_map=TYPE_COLORS_GREEN,
                        text="count",
                        labels={"commune": "Commune", "count": "Nombre", "type_etab": "Type"},
                        height=380,
                        barmode="stack",
                    )
                    fig_comm.update_traces(textposition="inside", textfont_size=10)
                    for trace in fig_comm.data:
                        trace.name = TYPE_LABELS.get(trace.name, trace.name)
                    fig_comm.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        font_family="Sora",
                        xaxis=dict(tickangle=-30),
                        yaxis=dict(gridcolor="#E8F5EE"),
                        legend=dict(title="Type", font=dict(size=10)),
                        margin=dict(l=10, r=10, t=10, b=60),
                    )
                    st.plotly_chart(style(fig_comm, 40), use_container_width=True)

            with extra2:
                st.markdown("###### Part de chaque type d'établissement")
                pie_data = df_sf.groupby("type_etab").size().reset_index(name="count")
                pie_data["label"] = pie_data["type_etab"].map(lambda t: TYPE_LABELS.get(t, t))
                fig_pie = px.pie(
                    pie_data,
                    names="label",
                    values="count",
                    color="type_etab",
                    color_discrete_map=TYPE_COLORS_GREEN,
                    height=380,
                    hole=0.4,
                )
                fig_pie.update_traces(
                    textposition="outside",
                    textinfo="percent+label",
                    pull=[0.03] * len(pie_data),
                )
                fig_pie.update_layout(
                    showlegend=False,
                    paper_bgcolor="rgba(0,0,0,0)",
                    font_family="Sora",
                    margin=dict(l=10, r=10, t=10, b=10),
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            if mode_sante == "Comparaison Métropoles":
                st.markdown("---")
                st.markdown("###### 🏙️ Nombre d'établissements par métropole sélectionnée")

                df_metro_count = (
                    df_sf.groupby("metropole")
                        .size()
                        .reset_index(name="count")
                        .sort_values("count", ascending=False)
                )
                fig_metros = px.bar(
                    df_metro_count,
                    x="metropole", y="count",
                    color="count",
                    color_continuous_scale=["#B7E4C7", "#1B4332"],
                    text="count",
                    labels={"metropole": "Métropole", "count": "Nombre d'établissements"},
                    height=320,
                )
                fig_metros.update_traces(textposition="outside")
                fig_metros.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font_family="Sora",
                    coloraxis_showscale=False,
                    xaxis=dict(tickangle=-20),
                    yaxis=dict(gridcolor="#E8F5EE"),
                    margin=dict(l=10, r=10, t=10, b=60),
                )
                st.plotly_chart(style(fig_metros, 40), use_container_width=True)

            if mode_sante == "Détail Communal" and not df_sf.empty:
                st.markdown("---")
                st.markdown("######  Classement des communes sélectionnées par nombre d'établissements")
                df_top_comm = (
                    df_sf.groupby("commune")
                        .size()
                        .reset_index(name="count")
                        .sort_values("count", ascending=True)
                )
                fig_top = px.bar(
                    df_top_comm,
                    x="count", y="commune", orientation="h",
                    color="count",
                    color_continuous_scale=["#B7E4C7", "#1B4332"],
                    text="count",
                    labels={"commune": "Commune", "count": "Nombre d'établissements"},
                    height=max(300, 40 * len(df_top_comm)),
                )
                fig_top.update_traces(textposition="outside")
                fig_top.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font_family="Sora",
                    coloraxis_showscale=False,
                    xaxis=dict(gridcolor="#E8F5EE"),
                    margin=dict(l=10, r=30, t=10, b=40),
                )
                st.plotly_chart(style(fig_top, 40), use_container_width=True)

    with s4:
        st.markdown(
            '<p class="source-note">Source : '
            '<a href="https://www.data.gouv.fr/datasets/elections-municipales-2020-resultats-1er-tour/" target="_blank">'
            'Data.gouv - Élections municipales 2014 & 2020 (1er et 2e tour)</a></p>',
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
            
            filter_bar("Filtres - Participation citoyenne")
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
                    title=f"Participation - {sel_annee_part} · Tour {sel_tour_part}",
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
                    color_discrete_map={"% Participation": "#2D6A4F", "% Abstention": "#95D5B2"},
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
                title=f"Évolution participation - Tour {sel_tour_part}",
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
                    "**Source** : Data.gouv - Élections municipales 2014 & 2020.\n\n"
                    "**Taux de participation** = Votants / Inscrits × 100.\n\n"
                    "**Périmètre** : communes des 5 métropoles. "
                    "Pour 2014, les communes de moins de 1 000 habitants utilisent un fichier TXT séparé."
                )

    # ──────────────────────────────────────────────────────────────────────────
    # ONGLET REVENUS & PAUVRETÉ - FiLoSoFi IRIS 2021
    # ──────────────────────────────────────────────────────────────────────────
    with s5:
        st.markdown(
            '<p class="source-note">Source : <a href="https://www.insee.fr/fr/statistiques/8268806" target="_blank">'
            'INSEE-DGFIP-Cnaf-Cnav-CCMSA · Fichier localisé social et fiscal (FiLoSoFi) · Revenus déclarés 2021 à l\'IRIS</a></p>',
            unsafe_allow_html=True,
        )

        if df_filo is None or df_filo.empty:
            st.info("📂 Fichier `BASE_TD_FILO_IRIS_2021_DEC.xlsx` introuvable - placez-le dans `solidarite&citoyennete/data_clean/revenus/`.")
        else:
            # ── Libellés des indicateurs ──────────────────────────────────
            FILO_LABELS = {
                "DEC_MED21":    "Revenu médian (€/UC)",
                "DEC_TP6021":   "Taux de bas revenus - seuil 60 % (%)",
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

            with st.container():
                
                filter_bar("Filtres - Revenus & pauvreté")
                fv1, fv2, fv3 = st.columns([1, 1, 2])
                with fv1:
                    filo_ind = st.selectbox(
                        "Indicateur",
                        filo_cols,
                        format_func=lambda c: FILO_LABELS.get(c, c),
                        index=filo_cols.index("DEC_MED21") if "DEC_MED21" in filo_cols else 0,
                        key="filo_ind",
                    )
                with fv2:
                    mode_filo = st.radio("Niveau géographique", ["Comparaison Métropoles", "Détail Communal (Grenoble)"], key="filo_mode", horizontal=True)
                with fv3:
                    if mode_filo == "Comparaison Métropoles":
                        sel_metros_filo = st.multiselect("Métropoles", metros_filo, default=metros_filo, key="filo_metros")
                        filo_niveau = st.selectbox("Niveau d'analyse", ["Commune (médiane des IRIS)", "IRIS (détail)"], key="filo_niveau")
                    else:
                        communes_gre_filo = sorted(df_filo[df_filo["metropole"] == "Grenoble"]["LIBCOM"].dropna().unique())
                        sel_communes_filo = st.multiselect("Communes de Grenoble", communes_gre_filo, default=communes_gre_filo[:2] if communes_gre_filo else [], key="filo_communes")
                st.markdown('</div>', unsafe_allow_html=True)

            if mode_filo == "Comparaison Métropoles":
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
                    st.markdown(f"#### 📌 Aperçu - {lbl}")
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
                            title=f"Distribution - {lbl}",
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
                            title=f"Top/Flop communes - {lbl}",
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
                        st.markdown("##### ⚖️ Inégalités - Indice de Gini par commune")
                        if "DEC_GI21" in df_agg.columns:
                            df_gi = df_agg.dropna(subset=["DEC_GI21"]).sort_values("DEC_GI21", ascending=False).head(20)
                            fig_gi = px.bar(
                                df_gi, x="DEC_GI21", y="LIBCOM",
                                color="metropole", color_discrete_map=COULEURS,
                                orientation="h",
                                labels={"LIBCOM": "", "DEC_GI21": "Indice de Gini"},
                                title="Top 20 communes - Indice de Gini",
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
                                color_discrete_sequence=px.colors.sequential.Greens_r,
                                hole=0.35, height=380,
                            )
                            fig_pie.update_traces(textposition="inside", textinfo="percent+label")
                            st.plotly_chart(style(fig_pie, 40), use_container_width=True)

                    with c6:
                        st.markdown("##### 📊 Rapport D9/D1 - inégalités entre IRIS")
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
                        desc_df.columns = [f"{FILO_LABELS.get(c, c)} - {s}" for c, s in desc_df.columns]
                        st.dataframe(desc_df, use_container_width=True)

                    with st.expander("📖 Note méthodologique"):
                        st.write(
                            "**Source** : INSEE-DGFIP-Cnaf-Cnav-CCMSA, Fichier localisé social et fiscal (FiLoSoFi) - Année 2021.\n\n"
                            "**Indicateurs** exprimés par **unité de consommation (UC)** - 1 UC pour le 1er adulte, 0,5 pour les autres personnes ≥ 14 ans, 0,3 pour les moins de 14 ans.\n\n"
                            "**Taux de bas revenus** : part des ménages dont le revenu/UC est inférieur à 60 % du revenu médian métropolitain.\n\n"
                            "**Indice de Gini** : entre 0 (égalité parfaite) et 1 (inégalité maximale).\n\n"
                            "**Périmètre** : IRIS appartenant aux communes des 5 métropoles, identifiés par code département."
                        )

            else:
                if not sel_communes_filo:
                    st.warning("⚠️ Sélectionnez au moins une commune.")
                else:
                    df_f = df_filo[(df_filo["metropole"] == "Grenoble") & (df_filo["LIBCOM"].isin(sel_communes_filo))].copy()
                    lbl  = FILO_LABELS.get(filo_ind, filo_ind)

                    st.markdown("---")
                    kpi_cols = st.columns(len(sel_communes_filo))
                    for i, comm in enumerate(sel_communes_filo):
                        val = df_f[df_f["LIBCOM"] == comm][filo_ind].median()
                        with kpi_cols[i]:
                            st.metric(label=f"💶 {comm}", value=f"{val:.1f}" if pd.notna(val) else "N/D")

                    st.markdown("---")
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"##### 📊 {lbl} par commune (médiane)")
                        df_bar = df_f.groupby("LIBCOM", as_index=False)[filo_ind].median()
                        fig_bar = px.bar(df_bar, x="LIBCOM", y=filo_ind, color="LIBCOM",
                                         color_discrete_sequence=px.colors.sequential.Greens_r,
                                         labels={"LIBCOM": "", filo_ind: lbl},
                                         title=f"Comparaison intercommunale", height=400)
                        st.plotly_chart(style(fig_bar, 40), use_container_width=True)
                    with c2:
                        st.markdown("##### 📦 Distribution des IRIS")
                        df_dist = df_f.dropna(subset=[filo_ind])
                        if not df_dist.empty:
                            fig_dist = px.box(df_dist, x="LIBCOM", y=filo_ind, color="LIBCOM",
                                              color_discrete_sequence=px.colors.sequential.Greens_r,
                                              labels={"LIBCOM": "", filo_ind: lbl},
                                              title=f"Distribution par IRIS - {lbl}", height=400)
                            st.plotly_chart(style(fig_dist, 40), use_container_width=True)

                    st.markdown("---")
                    st.markdown("##### 🕸️ Profil comparatif (radar)")
                    radar_ind = ["DEC_MED21", "DEC_TP6021", "DEC_GI21", "DEC_RD21", "DEC_PIMP21", "DEC_PACT21", "DEC_PPEN21"]
                    radar_avail = [c for c in radar_ind if c in df_f.columns]
                    if len(radar_avail) >= 3:
                        df_all_metro = df_filo[df_filo["metropole"] == "Grenoble"]
                        fig_rad = go.Figure()
                        
                        green_palette = px.colors.sequential.Greens_r
                        for idx, comm in enumerate(sel_communes_filo):
                            df_c = df_f[df_f["LIBCOM"] == comm]
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
                                line_color=green_palette[idx % len(green_palette)]
                            ))
                        fig_rad.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=400,
                                              title="Profil normalisé (0–100 dans la métropole)", paper_bgcolor="rgba(0,0,0,0)",
                                              legend=dict(orientation="h", y=-0.1))
                        st.plotly_chart(fig_rad, use_container_width=True)
