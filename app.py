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

# ── Palettes harmonisées ──────────────────────────────────────────────────────
PALETTE_METRO   = px.colors.sequential.Greys[2:]
PALETTE_COMMUNE = px.colors.sequential.Greens_r

# Palette spécifique appliquée aux 5 métropoles (pour les KPI et COULEURS-based charts)
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
        Path("solidarite&citoyennete/data_clean/education/education_filtre.csv"),
        Path("education_filtre.csv"),
    ]
    df = None
    for p in paths:
        if p.exists():
            df = pd.read_csv(p, low_memory=False)
            break
    if df is None:
        return None
    DEP_METRO = {
        "Isère":          "Grenoble",
        "Ille-et-Vilaine":"Rennes",
        "Seine-Maritime": "Rouen",
        "Loire":          "Saint-Étienne",
        "Hérault":        "Montpellier",
    }
    df["metropole"] = df["Libelle_departement"].map(DEP_METRO)
    df["Nombre_d_eleves"] = pd.to_numeric(df["Nombre_d_eleves"], errors="coerce").fillna(0)
    df["Nom_commune"] = df["Nom_commune"].str.replace("Saint-Etienne", "Saint-Étienne", regex=False)
    df["Statut_public_prive"] = df["Statut_public_prive"].astype(str).str.strip()
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
    st.markdown(f'<div class="filter-bar-title">{label}</div>', unsafe_allow_html=True)

def filter_row_label(text):
    st.markdown(
        f"<div style='padding-top:8px; font-weight:600; font-size:14px; color:#1C3A27;'>{text}</div>",
        unsafe_allow_html=True,
    )

def kpi_card_left(title, value, subtitle="", accent="#1a7a4a"):
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
# 6. PAGE D'ACCUEIL
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

    .cards-grid-bottom { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 16px; }
    
    .info-card {
        background: white; border: 1px solid #C8E6D4; border-radius: 12px;
        padding: 22px; border-left: 5px solid #2D6A4F;
    }
    
    .info-card.blue { 
        border-left: 6px solid #111184; 
        border-color: #111184;
        box-shadow: 0 4px 12px rgba(42, 92, 154, 0.08);
    }
    .info-card.blue .info-card-title { color: #111184; font-size: 14px; }
    .info-card.blue .info-card-body { 
        font-size: 16px;
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

    st.markdown("""
    <div class="stats-row">
        <div class="stat-box"><div class="stat-num">5</div><div class="stat-lbl">Métropoles</div></div>
        <div class="stat-box"><div class="stat-num">49</div><div class="stat-lbl">Communes</div></div>
        <div class="stat-box"><div class="stat-num">2</div><div class="stat-lbl">Thématiques</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="info-card blue">
        <div class="info-card-title"> Objectif</div>
        <div class="info-card-body">
            Analyser les données de démographie et de solidarité & citoyenneté afin de produire une analyse complète pour chaque commune de la métropole de Grenoble. 
            Cette étude vise à permettre la comparaison des communes entre elles, ainsi qu'à situer la métropole de Grenoble par rapport à celles de Rouen, Saint-Étienne, Rennes et Montpellier. 
            Elle est également destinée à accompagner les nouveaux élus dans la compréhension des dynamiques territoriales.
        </div>
    </div>
    """, unsafe_allow_html=True)

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
                Étude des allocations CAF, des indicateurs éducatifs et de santé, ainsi que de la participation citoyenne.
            </div>
            <div class="tag-row">
                <span class="tag-orange">Solidarité</span>
                <span class="tag-orange">Education</span>
                <span class="tag-orange">Santé</span>
                <span class="tag-orange">Participation</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="cta-wrapper">', unsafe_allow_html=True)
    if st.button("→   Accéder à l'application", type="primary"):
        st.session_state.page = "app"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ──────────────────────────────────────────────────────────────────────────────
# 7. SIDEBAR + NAVIGATION
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
        <style>
        [data-testid="stSidebar"] {
            background-color: #1B4332 !important;
        }
        div[data-testid="stRadio"] > div {
            gap: 8px;
        }
        div[data-testid="stRadio"] label {
            background-color: rgba(255, 255, 255, 0.9) !important;
            padding: 12px 16px !important;
            border-radius: 12px !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            transition: all 0.3s ease-in-out !important;
            cursor: pointer !important;
        }
        div[data-testid="stRadio"] label:hover {
            background-color: #FFFFFF !important;
            transform: translateX(5px) !important;
            box-shadow: 0px 4px 12px rgba(0,0,0,0.2) !important;
            border: 1px solid #95D5B2 !important;
        }
        div[data-testid="stRadio"] label p {
            color: #1B4332 !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            margin: 0 !important;
        }
        div[data-testid="stRadio"] input:checked + div label {
            background-color: #95D5B2 !important;
            border: 1px solid #FFFFFF !important;
        }
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

    st.write("")
    if st.button("Retour à l'Accueil", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()

    st.markdown('<div class="nav-header">Menu Principal</div>', unsafe_allow_html=True)
    
    vue = st.radio(
        "Navigation",
        ["Description", "Démographie", "Solidarité et citoyenneté"],
        index=0,
        label_visibility="collapsed",
    )

    st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
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
# PAGE DESCRIPTION
# ==============================================================================
if vue == "Description":
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

    st.markdown("""
        <div class="main-intro">
            <p style="font-size: 1.1rem; color: #1C3A27; margin: 0;">
                Cette application présente des analyses comparatives sur <b>5 métropoles françaises et 49 communes de la métropole de Grenoble</b> à partir des données de l'INSEE, la CAF, Data.gouv et OSM France. 
                Chaque page dispose de ses propres filtres en haut de page, adaptés aux données présentées. 
                Selon les onglets, il est possible de filtrer par métropole, par commune, par année ou par thématique.
            </p>
        </div>
    """, unsafe_allow_html=True)

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
        <div class="card-body" style="font-size:0.9rem; color:#555;">Analyse des établissements du premier et du second degré, publics et privés, afin d’observer leur répartition et leurs caractéristiques.</div></div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
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

        with st.container():
            filter_bar("Filtres - Population globale")
            col_geo_label, col_geo_options = st.columns([1, 3])
            with col_geo_label:
                filter_row_label("Niveau géographique")
            with col_geo_options:
                mode_pop = st.radio(
                    "",
                    ["Comparaison Métropoles", "Comparaison communes métropole de Grenoble"],
                    key="pop_mode", horizontal=True, label_visibility="collapsed"
                )
            if mode_pop == "Comparaison Métropoles":
                sel = st.multiselect("Métropoles à comparer", TOUTES, default=TOUTES, key="sel_t1")
            else:
                sel_communes_pop = st.multiselect(
                    "Commune de la métropole de Grenoble", sorted(COMMUNES["Grenoble"]),
                    default=sorted(COMMUNES["Grenoble"])[:2], key="pop_communes",
                )
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("---")

        # ════════════════════════════════════════════════════════════════════
        # VUE COMMUNES
        # ════════════════════════════════════════════════════════════════════
        if mode_pop == "Comparaison communes métropole de Grenoble":
            if not sel_communes_pop:
                st.warning("Sélectionnez au moins une commune.")
                st.stop()

            def commune_kpi_color(i, n):
                pal = PALETTE_COMMUNE
                idx = int(i / max(n - 1, 1) * (len(pal) - 1))
                return pal[idx]

            st.markdown("##### Population en 2022")
            kpi_cols = st.columns(len(sel_communes_pop))
            for i, comm in enumerate(sel_communes_pop):
                pop22  = commune_val(comm, "population_2022")
                tx_var = commune_val(comm, "tx_var_population_2016_2022")
                delta_str   = f"{tx_var:+.2f}%/an" if not np.isnan(tx_var) else "N/D"
                color_delta = "#2D6A4F" if not np.isnan(tx_var) and tx_var >= 0 else ("#C45B2A" if not np.isnan(tx_var) else "#888")
                kpi_color_c = commune_kpi_color(i, len(sel_communes_pop))
                html_card = f"""
                <div style='display:flex;flex-direction:column;justify-content:center;border-radius:8px;
                    overflow:hidden;box-shadow:0 2px 6px rgba(0,0,0,0.1);background:#fff;min-height:80px;
                    border-left:6px solid {kpi_color_c};padding:12px 16px;margin-bottom:10px;'>
                    <div style='font-size:11px;font-weight:700;letter-spacing:0.08em;color:#666;text-transform:uppercase;'>{comm}</div>
                    <div style='font-size:24px;font-weight:bold;color:#111;margin:4px 0;'>{fmt(pop22)}</div>
                    <div style='font-size:12px;font-weight:700;'>
                        <span style='color:{color_delta};'>Var: {delta_str}</span>
                    </div>
                </div>"""
                with kpi_cols[i]:
                    st.markdown(html_card, unsafe_allow_html=True)

            st.markdown("---")

            r1c1, r1c2 = st.columns(2)
            with r1c1:
                st.subheader(
                    "Population totale 2022 (habitants)",
                    help="Nombre d'habitants recensés par l'INSEE au RP 2022. Permet de comparer directement le volume de population de chaque territoire sélectionné."
                )
                data_comm = [{"Commune": c, "Population": commune_val(c, "population_2022")}
                             for c in sel_communes_pop]
                df_comm22 = pd.DataFrame(data_comm).dropna(subset=["Population"]).sort_values("Population", ascending=False)
                if not df_comm22.empty:
                    fig_pop_c = px.bar(
                        df_comm22, x="Commune", y="Population",
                        color="Commune", color_discrete_sequence=PALETTE_COMMUNE, text="Population",
                    )
                    fig_pop_c.update_traces(
                        texttemplate="%{text:,.0f}", textposition="outside", showlegend=False,
                        hovertemplate="<b>Commune : %{x}</b><br>Population 2022 : %{y:,.0f}<extra></extra>",
                    )
                    fig_pop_c.update_layout(showlegend=False, xaxis_title="Commune",
                                            yaxis_title="Habitants", yaxis=dict(tickformat=",d"), height=370)
                    st.plotly_chart(style(fig_pop_c), use_container_width=True)

            with r1c2:
                st.subheader(
                    "Densité (hab/km²) vs Superficie (km²)",
                    help="Croise deux dimensions : la superficie du territoire (axe horizontal) et sa densité de population (axe vertical). La taille de la bulle est proportionnelle à la population totale. Un territoire en haut à gauche = petit mais très dense (profil urbain). Un territoire en bas à droite = grand mais peu peuplé (profil rural ou périurbain)."
                )
                data_dens_c = []
                for i, c in enumerate(sel_communes_pop):
                    d = commune_val(c, "densite_2022")
                    s = commune_val(c, "superficie_km2_2022")
                    p = commune_val(c, "population_2022")
                    if not any(np.isnan(v) for v in [d, s, p]):
                        data_dens_c.append({"Commune": c, "Densité (hab/km²)": d,
                                            "Superficie (km²)": s, "Population": p})
                df_dens_c = pd.DataFrame(data_dens_c)
                if not df_dens_c.empty:
                    fig_dens_c = px.scatter(df_dens_c, x="Superficie (km²)", y="Densité (hab/km²)",
                                            size="Population", color="Commune", text="Commune",
                                            color_discrete_sequence=PALETTE_COMMUNE, size_max=55, height=370)
                    fig_dens_c.update_traces(textposition="top center", textfont_size=10,
                                             hovertemplate="<b>Commune : %{text}</b><br>Superficie : %{x:.2f} km²<br>Densité : %{y:.2f} hab/km²<extra></extra>")
                    fig_dens_c.update_layout(showlegend=False)
                    st.plotly_chart(style(fig_dens_c), use_container_width=True)

            with st.expander("💡 Comment interpréter ces deux graphiques ?"):
                st.write(
                    "**Population totale (barres)** : une barre plus haute signifie simplement plus d'habitants. "
                    "Ce graphique permet de situer l'échelle de chaque territoire et de dimensionner les besoins en services publics (écoles, transports, logements).\n\n"
                    "**Densité vs Superficie (nuage de points)** : la position verticale indique la pression démographique par km². "
                    "Un territoire dense et petit (en haut à gauche) a un profil urbain concentré, souvent avec des contraintes foncières. "
                    "Un territoire peu dense et grand (en bas à droite) a un profil périurbain ou rural, avec des enjeux différents de mobilité et d'accès aux services. "
                    "La taille de la bulle permet de ne pas confondre densité et population totale : une commune peut être grande en superficie mais peu peuplée, et pourtant avoir une forte densité dans son centre."
                )

            st.markdown("---")

            r2c1, r2c2 = st.columns(2)
            with r2c1:
                st.subheader(
                    "Soldes naturel et migratoire (%/an, 2016–2022)",
                    help="Décompose la variation démographique en deux composantes annuelles moyennes sur 2016–2022 :\n• Solde naturel = (naissances − décès) / population\n• Solde migratoire = (arrivées − départs) / population\n• Variation totale = somme des deux\nUn solde positif = le territoire gagne des habitants par ce canal."
                )
                rows_comp_c = []
                for comm in sel_communes_pop:
                    sn  = commune_val(comm, "tx_solde_naturel")
                    sm  = commune_val(comm, "tx_solde_migratoire")
                    tot = commune_val(comm, "tx_var_population_2016_2022")
                    if not all(np.isnan(v) for v in [sn, sm, tot]):
                        rows_comp_c.append({"Commune": comm, "Solde naturel": sn,
                                            "Solde migratoire": sm, "Variation totale": tot})
                if rows_comp_c:
                    df_comp_c = pd.DataFrame(rows_comp_c).melt(
                        id_vars="Commune", var_name="Composante", value_name="Taux (%/an)"
                    ).dropna()
                    n_comp = len(df_comp_c["Composante"].unique())
                    comp_colors = [PALETTE_COMMUNE[int(i * (len(PALETTE_COMMUNE)-1) / max(n_comp-1,1))]
                                   for i in range(n_comp)]
                    fig_comp_c = px.bar(df_comp_c, x="Commune", y="Taux (%/an)", color="Composante",
                                        barmode="group", color_discrete_sequence=comp_colors, height=360)
                    for trace in fig_comp_c.data:
                        trace.hovertemplate = "<b>Commune : %{x}</b><br>" + trace.name + " : %{y:.2f} %/an<extra></extra>"
                    fig_comp_c.add_hline(y=0, line_dash="dot", line_color="#AAAAAA")
                    fig_comp_c.update_layout(xaxis_title="Commune", yaxis_title="Taux (%/an)",
                                             legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02), xaxis_tickangle=-20)
                    st.plotly_chart(style(fig_comp_c), use_container_width=True)
                else:
                    st.info("Données de soldes non disponibles pour ces communes.")

            with r2c2:
                st.subheader(
                    "Naissances & Décès (pour 1 000 habitants)",
                    help="Compare les taux vitaux rapportés à 1 000 habitants :\n• Barres foncées = taux de natalité\n• Barres claires = taux de mortalité\n• Losange = accroissement naturel (naissances − décès)\nUn losange au-dessus de zéro indique que les naissances dépassent les décès sur ce territoire."
                )
                rows_vit_c = []
                for comm in sel_communes_pop:
                    nais = commune_val(comm, "naissances_2024")
                    decs = commune_val(comm, "deces_2024")
                    pop  = commune_val(comm, "population_2022")
                    if not any(np.isnan(v) for v in [nais, decs, pop]) and pop > 0:
                        rows_vit_c.append({"Commune": comm,
                                           "Naissances": round(nais / pop * 1000, 2),
                                           "Décès":      round(decs / pop * 1000, 2),
                                           "Accroissement": round((nais - decs) / pop * 1000, 2)})
                if rows_vit_c:
                    df_vit_c = pd.DataFrame(rows_vit_c)
                    comms_vit = df_vit_c["Commune"].tolist()
                    col_nais = PALETTE_COMMUNE[0]
                    col_decs = PALETTE_COMMUNE[int(len(PALETTE_COMMUNE) * 0.4)]
                    col_accr = PALETTE_COMMUNE[int(len(PALETTE_COMMUNE) * 0.7)]
                    fig_vit_c = go.Figure()
                    fig_vit_c.add_trace(go.Bar(
                        x=comms_vit, y=df_vit_c["Naissances"],
                        name="Naissances / 1 000 hab", marker_color=col_nais,
                        hovertemplate="<b>Commune : %{x}</b><br>Naissances : %{y:.2f} / 1 000 hab<extra></extra>",
                    ))
                    fig_vit_c.add_trace(go.Bar(
                        x=comms_vit, y=df_vit_c["Décès"],
                        name="Décès / 1 000 hab", marker_color=col_decs,
                        hovertemplate="<b>Commune : %{x}</b><br>Décès : %{y:.2f} / 1 000 hab<extra></extra>",
                    ))
                    fig_vit_c.add_trace(go.Scatter(
                        x=comms_vit, y=df_vit_c["Accroissement"],
                        mode="markers+text", name="Accroissement naturel",
                        marker=dict(symbol="diamond", size=12, color=col_accr, line=dict(color="white", width=1.5)),
                        text=[f"{v:+.2f}" for v in df_vit_c["Accroissement"]],
                        textposition="top center", textfont=dict(size=9, color="#1B4332"),
                        hovertemplate="<b>Commune : %{x}</b><br>Accroissement naturel : %{y:.2f} / 1 000 hab<extra></extra>",
                    ))
                    fig_vit_c.update_layout(barmode="group", legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02),
                                            yaxis_title="Pour 1 000 habitants", height=360)
                    st.plotly_chart(style(fig_vit_c), use_container_width=True)
                else:
                    st.info("Données de naissances/décès non disponibles pour ces communes.")

            with st.expander("💡 Comment interpréter ces deux graphiques ?"):
                st.write(
                    "**Soldes naturel et migratoire** : ce graphique décompose la croissance démographique en deux moteurs distincts. "
                    "Le **solde naturel** (naissances − décès) reflète la vitalité biologique du territoire : s'il est négatif, la population vieillit et les décès dépassent les naissances. "
                    "Le **solde migratoire** (arrivées − départs) révèle l'attractivité résidentielle : un solde positif signifie que le territoire attire plus de nouveaux résidents qu'il n'en perd. "
                    "Un territoire peut croître même avec un solde naturel négatif s'il est très attractif (ex : communes résidentielles prisées). À l'inverse, une natalité dynamique peut masquer une fuite des actifs.\n\n"
                    "**Naissances & Décès** : ce graphique complète la lecture en montrant les taux bruts pour 1 000 habitants. "
                    "Le losange représente l'accroissement naturel net : au-dessus de zéro, les naissances dépassent les décès ; en dessous, c'est l'inverse. "
                    "Un taux de natalité élevé (grande barre foncée) combiné à un faible taux de mortalité = territoire jeune et dynamique. "
                    "Un territoire avec une barre claire (décès) plus haute que la barre foncée (naissances) est structurellement vieillissant."
                )

            st.markdown("---")
            st.markdown("#### Tableau récapitulatif - indicateurs clés")
            lignes_tab_c = []
            for comm in sel_communes_pop:
                pop22 = commune_val(comm, "population_2022")
                dens  = commune_val(comm, "densite_2022")
                rev   = commune_val(comm, "revenu_median_2021")
                pauv  = commune_val(comm, "tx_pauvrete_2021")
                tc    = commune_val(comm, "tx_chomage_15_64")
                lignes_tab_c.append({"Commune": comm, "Population 2022": fmt(pop22),
                                     "Densité (hab/km²)": fmt(dens), "Revenu médian": fmt(rev, " €"),
                                     "Taux pauvreté": f"{pauv:.1f}%" if not np.isnan(pauv) else "N/D",
                                     "Taux chômage": f"{tc:.1f}%" if not np.isnan(tc) else "N/D"})
            st.dataframe(pd.DataFrame(lignes_tab_c).set_index("Commune"), use_container_width=True)

        # ════════════════════════════════════════════════════════════════════
        # VUE COMPARAISON MÉTROPOLES
        # ════════════════════════════════════════════════════════════════════
        else:
            if not sel:
                st.warning("Sélectionnez au moins une métropole.")
                st.stop()

            st.markdown("##### Population en 2022")
            kpi_cols = st.columns(len(sel))
            for i, m in enumerate(sel):
                pop22  = epci_val(m, "population_2022")
                tx_var = epci_val(m, "tx_var_population_2016_2022")
                delta_str   = f"{tx_var:+.2f}%/an" if not np.isnan(tx_var) else "N/D"
                color_delta = "#2D6A4F" if not np.isnan(tx_var) and tx_var >= 0 else ("#C45B2A" if not np.isnan(tx_var) else "#888")
                kpi_color = COULEURS.get(m, "#888888")
                html_card = f"""
                <div style='display:flex;flex-direction:column;justify-content:center;border-radius:8px;
                    overflow:hidden;box-shadow:0 2px 6px rgba(0,0,0,0.1);background:#fff;min-height:80px;
                    border-left:6px solid {kpi_color};padding:12px 16px;margin-bottom:10px;'>
                    <div style='font-size:11px;font-weight:700;letter-spacing:0.08em;color:#666;text-transform:uppercase;'>{m}</div>
                    <div style='font-size:24px;font-weight:bold;color:#111;margin:4px 0;'>{fmt(pop22)}</div>
                    <div style='font-size:12px;font-weight:700;'>
                        <span style='color:{color_delta};'>Var: {delta_str}</span>
                    </div>
                </div>"""
                with kpi_cols[i]:
                    st.markdown(html_card, unsafe_allow_html=True)

            st.markdown("---")

            r1c1, r1c2 = st.columns(2)
            with r1c1:
                st.subheader(
                    "Population totale 2022 (habitants)",
                    help="Nombre d'habitants recensés par l'INSEE au RP 2022. Permet de comparer directement le volume de population de chaque territoire sélectionné."
                )
                data_pop_df = [{"Métropole": m, "Population": epci_val(m, "population_2022")} for m in sel]
                df_pop22 = pd.DataFrame(data_pop_df).dropna().sort_values("Population", ascending=False)
                if not df_pop22.empty:
                    fig_pop = px.bar(df_pop22, x="Métropole", y="Population", color="Métropole",
                                     color_discrete_map=COULEURS, text="Population")
                    fig_pop.update_traces(
                        texttemplate="%{text:,.0f}", textposition="outside", showlegend=False,
                        hovertemplate="<b>Métropole : %{x}</b><br>Population 2022 : %{y:,.0f}<extra></extra>",
                    )
                    fig_pop.update_layout(showlegend=False, xaxis_title="Métropole", yaxis_title="Habitants",
                                          yaxis=dict(tickformat=",d"), height=370)
                    st.plotly_chart(style(fig_pop), use_container_width=True)

            with r1c2:
                st.subheader(
                    "Densité (hab/km²) vs Superficie (km²)",
                    help="Croise deux dimensions : la superficie du territoire (axe horizontal) et sa densité de population (axe vertical). La taille de la bulle est proportionnelle à la population totale. Un territoire en haut à gauche = petit mais très dense (profil urbain). Un territoire en bas à droite = grand mais peu peuplé (profil rural ou périurbain)."
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
                    fig_dens = px.scatter(df_dens, x="Superficie (km²)", y="Densité (hab/km²)",
                                          size="Population", color="Métropole",
                                          color_discrete_map=COULEURS, text="Métropole",
                                          size_max=55, height=370)
                    fig_dens.update_traces(textposition="top center", textfont_size=11,
                                           hovertemplate="<b>Métropole : %{text}</b><br>Superficie : %{x:.2f} km²<br>Densité : %{y:.2f} hab/km²<extra></extra>")
                    fig_dens.update_layout(showlegend=False)
                    st.plotly_chart(style(fig_dens), use_container_width=True)

            with st.expander("💡 Comment interpréter ces deux graphiques ?"):
                st.write(
                    "**Population totale (barres)** : une barre plus haute signifie simplement plus d'habitants. "
                    "Ce graphique permet de situer l'échelle de chaque territoire et de dimensionner les besoins en services publics (écoles, transports, logements).\n\n"
                    "**Densité vs Superficie (nuage de points)** : la position verticale indique la pression démographique par km². "
                    "Un territoire dense et petit (en haut à gauche) a un profil urbain concentré, souvent avec des contraintes foncières. "
                    "Un territoire peu dense et grand (en bas à droite) a un profil périurbain ou rural, avec des enjeux différents de mobilité et d'accès aux services. "
                    "La taille de la bulle permet de ne pas confondre densité et population totale : une métropole peut être grande en superficie mais peu peuplée, et pourtant avoir une forte densité dans son centre."
                )

            st.markdown("---")

            r2c1, r2c2 = st.columns(2)
            with r2c1:
                st.subheader(
                    "Soldes naturel et migratoire (%/an, 2016–2022)",
                    help="Décompose la variation démographique en deux composantes annuelles moyennes sur 2016–2022 :\n• Solde naturel = (naissances − décès) / population\n• Solde migratoire = (arrivées − départs) / population\n• Variation totale = somme des deux\nUn solde positif = le territoire gagne des habitants par ce canal."
                )
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
                        id_vars="Métropole", var_name="Composante", value_name="Taux (%/an)"
                    ).dropna()
                    n_comp_m = len(df_comp["Composante"].unique())
                    comp_colors_m = [PALETTE_METRO[int(i * (len(PALETTE_METRO)-1) / max(n_comp_m-1,1))]
                                     for i in range(n_comp_m)]
                    fig_comp = px.bar(df_comp, x="Métropole", y="Taux (%/an)", color="Composante",
                                      barmode="group", color_discrete_sequence=comp_colors_m, height=360)
                    for trace in fig_comp.data:
                        trace.hovertemplate = "<b>Métropole : %{x}</b><br>" + trace.name + " : %{y:.2f} %/an<extra></extra>"
                    fig_comp.add_hline(y=0, line_dash="dot", line_color="#AAAAAA")
                    metros_comp = list(dict.fromkeys(df_comp["Métropole"].tolist()))
                    if "Grenoble" in metros_comp:
                        g_pos = metros_comp.index("Grenoble")
                        fig_comp.add_vrect(x0=g_pos - 0.45, x1=g_pos + 0.45, fillcolor="rgba(255,88,77,0.10)", line_color="#FF584D", line_width=1.5, layer="below")
                    fig_comp.update_layout(xaxis_title="Métropole", yaxis_title="Taux (%/an)",
                                           legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02))
                    st.plotly_chart(style(fig_comp), use_container_width=True)

            with r2c2:
                st.subheader(
                    "Naissances & Décès 2024 (pour 1 000 habitants)",
                    help="Compare les taux vitaux rapportés à 1 000 habitants :\n• Barres foncées = taux de natalité\n• Barres claires = taux de mortalité\n• Losange rouge = accroissement naturel (naissances − décès)\nUn losange au-dessus de zéro indique que les naissances dépassent les décès. La zone rouge identifie Grenoble."
                )
                rows_vit = []
                for m in sel:
                    nais = epci_val(m, "naissances_2024")
                    decs = epci_val(m, "deces_2024")
                    pop  = epci_val(m, "population_2022")
                    if not any(np.isnan(v) for v in [nais, decs, pop]):
                        rows_vit.append({"Métropole": m,
                                         "Naissances": round(nais / pop * 1000, 2),
                                         "Décès":      round(decs / pop * 1000, 2),
                                         "Accroissement": round((nais - decs) / pop * 1000, 2)})
                df_vit = pd.DataFrame(rows_vit)
                if not df_vit.empty:
                    metros_vit = df_vit["Métropole"].tolist()
                    col_nais_m = PALETTE_METRO[int(len(PALETTE_METRO) * 0.3)]
                    col_decs_m = PALETTE_METRO[int(len(PALETTE_METRO) * 0.7)]
                    fig_vit = go.Figure()
                    fig_vit.add_trace(go.Bar(
                        x=metros_vit, y=df_vit["Naissances"],
                        name="Naissances / 1 000 hab", marker_color=col_nais_m,
                        hovertemplate="<b>Métropole : %{x}</b><br>Naissances : %{y:.2f} / 1 000 hab<extra></extra>",
                    ))
                    fig_vit.add_trace(go.Bar(
                        x=metros_vit, y=df_vit["Décès"],
                        name="Décès / 1 000 hab", marker_color=col_decs_m,
                        hovertemplate="<b>Métropole : %{x}</b><br>Décès : %{y:.2f} / 1 000 hab<extra></extra>",
                    ))
                    fig_vit.add_trace(go.Scatter(
                        x=metros_vit, y=df_vit["Accroissement"],
                        mode="markers+text", name="Accroissement naturel",
                        marker=dict(symbol="diamond", size=12, color="#FF584D", line=dict(color="white", width=1.5)),
                        text=[f"{v:+.2f}" for v in df_vit["Accroissement"]],
                        textposition="top center", textfont=dict(size=9, color="#8B2E2E"),
                        hovertemplate="<b>Métropole : %{x}</b><br>Accroissement naturel : %{y:.2f} / 1 000 hab<extra></extra>",
                    ))
                    if "Grenoble" in metros_vit:
                        g_pos = metros_vit.index("Grenoble")
                        fig_vit.add_vrect(x0=g_pos - 0.45, x1=g_pos + 0.45,
                                          fillcolor="rgba(255,88,77,0.10)",
                                          line_color="#FF584D", line_width=1.5, layer="below")
                    fig_vit.update_layout(barmode="group", legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02),
                                          yaxis_title="Pour 1 000 habitants", height=360)
                    st.plotly_chart(style(fig_vit), use_container_width=True)

            with st.expander("💡 Comment interpréter ces deux graphiques ?"):
                st.write(
                    "**Soldes naturel et migratoire** : ce graphique décompose la croissance démographique en deux moteurs distincts. "
                    "Le **solde naturel** (naissances − décès) reflète la vitalité biologique du territoire : s'il est négatif, la population vieillit et les décès dépassent les naissances. "
                    "Le **solde migratoire** (arrivées − départs) révèle l'attractivité résidentielle : un solde positif signifie que le territoire attire plus de nouveaux résidents qu'il n'en perd. "
                    "Un territoire peut croître même avec un solde naturel négatif s'il est très attractif. À l'inverse, une natalité dynamique peut masquer une fuite des actifs. "
                    "La zone rouge identifie Grenoble dans tous les graphiques de comparaison entre métropoles.\n\n"
                    "**Naissances & Décès** : ce graphique complète la lecture en montrant les taux bruts pour 1 000 habitants. "
                    "Le losange rouge représente l'accroissement naturel net : au-dessus de zéro, les naissances dépassent les décès. "
                    "Un taux de natalité élevé combiné à un faible taux de mortalité = territoire jeune et dynamique. "
                    "Un territoire avec des décès plus nombreux que les naissances est structurellement vieillissant et dépend davantage de son attractivité migratoire pour maintenir sa population."
                )

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

            TRANCHES_M25 = ["01","02","03","04","05"]
            TRANCHES_ACT = ["06","07","08","09","10","11","12","13"]
            TRANCHES_SEN = ["14","15","16","17","18","19","20"]

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

            def build_pyramide(df_src, label_entity, color_h, color_f):
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
                fig.update_layout(barmode="relative", bargap=0.06, legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02),
                                  yaxis_title="Tranche d'âge (ans)", xaxis_title="Population",
                                  xaxis=dict(tickformat="~s"), title=dict(text=label_entity, font_size=13), height=480)
                return fig

            with st.container():
                filter_bar("Filtres - Structure par âge")
                fa1, fa2 = st.columns([1, 3])
                with fa1:
                    filter_row_label("Niveau géographique")
                with fa2:
                    mode_age = st.radio("",
                        ["Comparaison Métropoles", "Comparaison communes métropole de Grenoble"],
                        key="age_mode", horizontal=True, label_visibility="collapsed")
                if mode_age == "Comparaison Métropoles":
                    sel_metros_age = st.multiselect("Métropoles", TOUTES, default=TOUTES, key="age_metros")
                else:
                    sel_communes_age = st.multiselect("Commune de la métropole de Grenoble",
                                                      sorted(COMMUNES["Grenoble"]),
                                                      default=sorted(COMMUNES["Grenoble"])[:2],
                                                      key="age_communes")
                annee_age = st.selectbox("Année", annees_dispo, index=len(annees_dispo)-1, key="an_age")
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("---")

            # ── VUE MÉTROPOLES ────────────────────────────────────────────────
            if mode_age == "Comparaison Métropoles":
                if not sel_metros_age:
                    st.warning("Sélectionnez au moins une métropole.")
                    st.stop()

                st.subheader(f"Indicateurs clés - {annee_age}",
                             help="Part des moins de 25 ans et des 65 ans et plus dans la population totale du territoire au recensement sélectionné. Ces deux indicateurs résument le profil jeune ou senior d'un territoire.")
                kpi_cols = st.columns(len(sel_metros_age))
                for i, m in enumerate(sel_metros_age):
                    df_m = df_pop[(df_pop["metropole"] == m) & (df_pop["annee"] == annee_age)]
                    tot   = pop_totale_df(df_m)
                    p_m25 = pop_tranches(df_m, TRANCHES_M25)
                    p_sen = pop_tranches(df_m, TRANCHES_SEN)
                    pct_m25 = p_m25 / tot * 100 if tot > 0 else np.nan
                    pct_sen = p_sen / tot * 100 if tot > 0 else np.nan
                    kpi_color2 = COULEURS.get(m, "#888888")
                    with kpi_cols[i]:
                        st.markdown(f"**{m}**")
                        for title, value in [("Moins de 25 ans", pct_m25), ("65 ans et +", pct_sen)]:
                            val = f"{value:.1f}%" if not np.isnan(value) else "N/D"
                            st.markdown(f"""
                            <div style='display:flex;border-radius:8px;box-shadow:0 2px 6px rgba(0,0,0,0.1);
                                background:#fff;border-left:6px solid {kpi_color2};margin-bottom:10px;padding:10px 16px;'>
                                <div>
                                    <div style='font-size:11px;font-weight:700;color:#666;text-transform:uppercase;'>{title}</div>
                                    <div style='font-size:24px;font-weight:bold;color:#111;'>{val}</div>
                                    <div style='font-size:10px;color:#888;'>Part de la population</div>
                                </div>
                            </div>""", unsafe_allow_html=True)

                st.markdown("---")
                st.subheader(
                    "Pyramides des âges comparées",
                    help="Chaque barre horizontale représente une tranche d'âge quinquennale (ex : 0–4 ans, 5–9 ans…). Les hommes sont à gauche, les femmes à droite. La largeur de chaque barre est proportionnelle au nombre de personnes dans cette tranche. Une base large = beaucoup de jeunes. Un sommet large = fort vieillissement. Une forme en 'toupie' (ventre au milieu) = population en âge de travailler dominante."
                )

                n_m = len(sel_metros_age)
                metro_colors_h = [PALETTE_METRO[int(i * (len(PALETTE_METRO)-1) / max(n_m-1,1))] for i in range(n_m)]
                metro_colors_f = [PALETTE_METRO[max(0, int(i * (len(PALETTE_METRO)-1) / max(n_m-1,1)) - 2)] for i in range(n_m)]
                metro_h_map = {m: ("#FF584D" if m == "Grenoble" else metro_colors_h[i]) for i, m in enumerate(sel_metros_age)}
                metro_f_map = {m: ("#FFBBB7" if m == "Grenoble" else metro_colors_f[i]) for i, m in enumerate(sel_metros_age)}

                ncols = min(len(sel_metros_age), 3)
                rows_pyr = [sel_metros_age[i:i+ncols] for i in range(0, len(sel_metros_age), ncols)]
                for row in rows_pyr:
                    cols = st.columns(len(row))
                    for j, m in enumerate(row):
                        df_m = df_pop[(df_pop["metropole"] == m) & (df_pop["annee"] == annee_age)]
                        fig = build_pyramide(df_m, m, metro_h_map[m], metro_f_map[m])
                        with cols[j]:
                            st.plotly_chart(style(fig, 30), use_container_width=True)

                with st.expander("💡 Comment interpréter la pyramide des âges ?"):
                    st.write(
                        "La pyramide des âges est une photographie de la structure démographique d'un territoire à un instant donné. "
                        "Chaque tranche d'âge quinquennale est représentée par deux barres : les hommes (à gauche) et les femmes (à droite), "
                        "dont la longueur est proportionnelle à l'effectif concerné.\n\n"
                        "**Formes caractéristiques :**\n"
                        "- **Base large, sommet étroit** (forme triangulaire) : territoire jeune avec une natalité élevée — profil plutôt rural ou familial.\n"
                        "- **Sommet large, base étroite** (forme d'urne) : territoire vieillissant avec peu de jeunes — souvent lié à un exode des familles ou à une faible natalité historique.\n"
                        "- **Ventre large au milieu** (toupie) : forte concentration d'actifs (25–54 ans) — territoire attractif économiquement.\n"
                        "- **Asymétrie hommes/femmes** : visible surtout chez les personnes âgées où les femmes ont une espérance de vie plus longue.\n\n"
                        "Comparer deux pyramides côte à côte permet d'identifier rapidement quel territoire vieillit davantage et d'anticiper les besoins futurs (crèches, Ehpad, services de santé)."
                    )

                st.markdown("---")
                st.subheader(
                    "Évolution des groupes d'âge (2011 → 2022)",
                    help="Suit l'évolution de la part des moins de 25 ans et des 65 ans et plus dans la population totale sur les trois recensements disponibles (2011, 2016, 2022). Permet d'identifier les territoires qui vieillissent ou rajeunissent le plus rapidement."
                )
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("##### Part des moins de 25 ans (%)")
                    rows_ev = []
                    for m in sel_metros_age:
                        for an in annees_dispo:
                            df_m = df_pop[(df_pop["metropole"] == m) & (df_pop["annee"] == an)]
                            tot = pop_totale_df(df_m)
                            p = pop_tranches(df_m, TRANCHES_M25)
                            if tot > 0:
                                rows_ev.append({"Métropole": m, "Année": an, "Part (%)": p/tot*100})
                    df_ev = pd.DataFrame(rows_ev)
                    if not df_ev.empty:
                        fig_ev1 = px.line(df_ev, x="Année", y="Part (%)", color="Métropole",
                                          markers=True, color_discrete_map=COULEURS)
                        fig_ev1.update_traces(
                            hovertemplate="<b>Métropole : %{fullData.name}</b><br>Année : %{x}<br>Part : %{y:.2f}%<extra></extra>")
                        st.plotly_chart(style(fig_ev1))
                with c2:
                    st.markdown("##### Part des 65 ans et + (%)")
                    rows_ev2 = []
                    for m in sel_metros_age:
                        for an in annees_dispo:
                            df_m = df_pop[(df_pop["metropole"] == m) & (df_pop["annee"] == an)]
                            tot = pop_totale_df(df_m)
                            p = pop_tranches(df_m, TRANCHES_SEN)
                            if tot > 0:
                                rows_ev2.append({"Métropole": m, "Année": an, "Part (%)": p/tot*100})
                    df_ev2 = pd.DataFrame(rows_ev2)
                    if not df_ev2.empty:
                        fig_ev2 = px.line(df_ev2, x="Année", y="Part (%)", color="Métropole",
                                          markers=True, color_discrete_map=COULEURS)
                        fig_ev2.update_traces(
                            hovertemplate="<b>Métropole : %{fullData.name}</b><br>Année : %{x}<br>Part : %{y:.2f}%<extra></extra>")
                        st.plotly_chart(style(fig_ev2))

                with st.expander("💡 Comment interpréter ces courbes d'évolution ?"):
                    st.write(
                        "Ces graphiques montrent comment la composition par âge de chaque territoire a évolué entre 2011 et 2022.\n\n"
                        "**Part des moins de 25 ans** : une courbe qui descend indique que la proportion de jeunes diminue — soit parce que les familles quittent le territoire, soit parce que la natalité baisse, soit parce que d'autres tranches d'âge progressent plus vite. "
                        "Une courbe stable ou montante signale un territoire qui maintient ou renforce son attractivité pour les familles avec enfants.\n\n"
                        "**Part des 65 ans et plus** : une courbe qui monte = vieillissement progressif du territoire. "
                        "Ce phénomène est naturel dans la plupart des territoires français, mais la vitesse de vieillissement varie selon l'attractivité économique et résidentielle. "
                        "Un territoire qui vieillit vite devra anticiper des besoins accrus en soins, en accessibilité et en services à la personne.\n\n"
                        "**Lire les deux ensemble** : si la part des jeunes baisse pendant que celle des seniors monte, le territoire se polarise vers les personnes âgées. "
                        "Si les deux indicateurs restent stables, le territoire maintient un équilibre démographique."
                    )

            # ── VUE COMMUNES ──────────────────────────────────────────────────
            else:
                communes_age = sel_communes_age if sel_communes_age else []
                if not communes_age:
                    st.info("Sélectionnez au moins une commune.")
                    st.stop()

                st.subheader(f"Indicateurs clés - {annee_age}",
                             help="Part des moins de 25 ans et des 65 ans et plus dans la population totale de la commune au recensement sélectionné. Ces deux indicateurs résument le profil jeune ou senior d'un territoire.")
                kpi_cols = st.columns(len(communes_age))
                n_comm_age = len(communes_age)
                for i, comm in enumerate(communes_age):
                    df_c = df_pop[(df_pop["LIBELLE"] == comm) & (df_pop["annee"] == annee_age)]
                    tot   = pop_totale_df(df_c)
                    p_m25 = pop_tranches(df_c, TRANCHES_M25)
                    p_sen = pop_tranches(df_c, TRANCHES_SEN)
                    pct_m25 = p_m25 / tot * 100 if tot > 0 else np.nan
                    pct_sen = p_sen / tot * 100 if tot > 0 else np.nan
                    kpi_col_comm = PALETTE_COMMUNE[int(i * (len(PALETTE_COMMUNE)-1) / max(n_comm_age-1,1))]
                    with kpi_cols[i]:
                        st.markdown(f"**{comm}**")
                        for title, value in [("Moins de 25 ans", pct_m25), ("65 ans et +", pct_sen)]:
                            val = f"{value:.1f}%" if not np.isnan(value) else "N/D"
                            st.markdown(f"""
                            <div style='display:flex;border-radius:8px;box-shadow:0 2px 6px rgba(0,0,0,0.1);
                                background:#fff;border-left:6px solid {kpi_col_comm};margin-bottom:10px;padding:10px 16px;'>
                                <div>
                                    <div style='font-size:11px;font-weight:700;color:#666;text-transform:uppercase;'>{title}</div>
                                    <div style='font-size:24px;font-weight:bold;color:#111;'>{val}</div>
                                    <div style='font-size:10px;color:#888;'>Part de la population</div>
                                </div>
                            </div>""", unsafe_allow_html=True)

                st.markdown("---")
                st.subheader(
                    "Pyramide(s) des âges",
                    help="Chaque barre horizontale représente une tranche d'âge quinquennale (ex : 0–4 ans, 5–9 ans…). Les hommes sont à gauche, les femmes à droite. La largeur de chaque barre est proportionnelle au nombre de personnes dans cette tranche. Une base large = beaucoup de jeunes. Un sommet large = fort vieillissement. Une forme en 'toupie' (ventre au milieu) = population en âge de travailler dominante."
                )

                comm_colors_h = [PALETTE_COMMUNE[int(i * (len(PALETTE_COMMUNE)-1) / max(n_comm_age-1,1))]
                                 for i in range(n_comm_age)]
                comm_colors_f = [PALETTE_COMMUNE[min(int(i * (len(PALETTE_COMMUNE)-1) / max(n_comm_age-1,1)) + 2, len(PALETTE_COMMUNE)-1)]
                                 for i in range(n_comm_age)]

                ncols = min(len(communes_age), 3)
                rows_pyr_c = [communes_age[i:i+ncols] for i in range(0, len(communes_age), ncols)]
                for row in rows_pyr_c:
                    cols = st.columns(len(row))
                    for j, comm in enumerate(row):
                        abs_idx = communes_age.index(comm)
                        df_c = df_pop[(df_pop["LIBELLE"] == comm) & (df_pop["annee"] == annee_age)]
                        fig = build_pyramide(df_c, comm, comm_colors_h[abs_idx], comm_colors_f[abs_idx])
                        with cols[j]:
                            st.plotly_chart(style(fig, 30), use_container_width=True)

                with st.expander("💡 Comment interpréter la pyramide des âges ?"):
                    st.write(
                        "La pyramide des âges est une photographie de la structure démographique d'un territoire à un instant donné. "
                        "Chaque tranche d'âge quinquennale est représentée par deux barres : les hommes (à gauche) et les femmes (à droite), "
                        "dont la longueur est proportionnelle à l'effectif concerné.\n\n"
                        "**Formes caractéristiques :**\n"
                        "- **Base large, sommet étroit** (forme triangulaire) : territoire jeune avec une natalité élevée — profil plutôt rural ou familial.\n"
                        "- **Sommet large, base étroite** (forme d'urne) : territoire vieillissant avec peu de jeunes — souvent lié à un exode des familles ou à une faible natalité historique.\n"
                        "- **Ventre large au milieu** (toupie) : forte concentration d'actifs (25–54 ans) — territoire attractif économiquement.\n"
                        "- **Asymétrie hommes/femmes** : visible surtout chez les personnes âgées où les femmes ont une espérance de vie plus longue.\n\n"
                        "Comparer deux pyramides côte à côte permet d'identifier rapidement quel territoire vieillit davantage et d'anticiper les besoins futurs (crèches, Ehpad, services de santé)."
                    )

                st.markdown("---")
                st.subheader(
                    "Évolution des groupes d'âge (2011 → 2022)",
                    help="Suit l'évolution de la part des moins de 25 ans et des 65 ans et plus dans la population totale sur les trois recensements disponibles (2011, 2016, 2022). Permet d'identifier les territoires qui vieillissent ou rajeunissent le plus rapidement."
                )
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("##### Part des moins de 25 ans (%)")
                    rows_evc = []
                    for comm in communes_age:
                        for an in annees_dispo:
                            df_c = df_pop[(df_pop["LIBELLE"] == comm) & (df_pop["annee"] == an)]
                            tot = pop_totale_df(df_c)
                            p = pop_tranches(df_c, TRANCHES_M25)
                            if tot > 0:
                                rows_evc.append({"Commune": comm, "Année": an, "Part (%)": p/tot*100})
                    df_evc = pd.DataFrame(rows_evc)
                    if not df_evc.empty:
                        fig_evc1 = px.line(df_evc, x="Année", y="Part (%)", color="Commune",
                                           markers=True, color_discrete_sequence=PALETTE_COMMUNE)
                        fig_evc1.update_traces(
                            hovertemplate="<b>Commune : %{fullData.name}</b><br>Année : %{x}<br>Part : %{y:.2f}%<extra></extra>")
                        st.plotly_chart(style(fig_evc1))
                with c2:
                    st.markdown("##### Part des 65 ans et + (%)")
                    rows_evc2 = []
                    for comm in communes_age:
                        for an in annees_dispo:
                            df_c = df_pop[(df_pop["LIBELLE"] == comm) & (df_pop["annee"] == an)]
                            tot = pop_totale_df(df_c)
                            p = pop_tranches(df_c, TRANCHES_SEN)
                            if tot > 0:
                                rows_evc2.append({"Commune": comm, "Année": an, "Part (%)": p/tot*100})
                    df_evc2 = pd.DataFrame(rows_evc2)
                    if not df_evc2.empty:
                        fig_evc2 = px.line(df_evc2, x="Année", y="Part (%)", color="Commune",
                                           markers=True, color_discrete_sequence=PALETTE_COMMUNE)
                        fig_evc2.update_traces(
                            hovertemplate="<b>Commune : %{fullData.name}</b><br>Année : %{x}<br>Part : %{y:.2f}%<extra></extra>")
                        st.plotly_chart(style(fig_evc2))

                with st.expander("💡 Comment interpréter ces courbes d'évolution ?"):
                    st.write(
                        "Ces graphiques montrent comment la composition par âge de chaque territoire a évolué entre 2011 et 2022.\n\n"
                        "**Part des moins de 25 ans** : une courbe qui descend indique que la proportion de jeunes diminue — soit parce que les familles quittent le territoire, soit parce que la natalité baisse, soit parce que d'autres tranches d'âge progressent plus vite. "
                        "Une courbe stable ou montante signale un territoire qui maintient ou renforce son attractivité pour les familles avec enfants.\n\n"
                        "**Part des 65 ans et plus** : une courbe qui monte = vieillissement progressif du territoire. "
                        "Ce phénomène est naturel dans la plupart des territoires français, mais la vitesse de vieillissement varie selon l'attractivité économique et résidentielle. "
                        "Un territoire qui vieillit vite devra anticiper des besoins accrus en soins, en accessibilité et en services à la personne.\n\n"
                        "**Lire les deux ensemble** : si la part des jeunes baisse pendant que celle des seniors monte, le territoire se polarise vers les personnes âgées. "
                        "Si les deux indicateurs restent stables, le territoire maintient un équilibre démographique."
                    )

# ==============================================================================
# ONGLET 3 - MOBILITÉS
# ==============================================================================
if vue == "Démographie":
    with tab3:

        data_ok = any(df is not None for df in [df_res, df_prof, df_scol])
        if not data_ok:
            st.info("📂 Fichiers de mobilité manquants.")
        else:
            st.markdown("""
                <div style='background-color: #f1f8f5; padding: 15px; border-radius: 10px; border-left: 5px solid #1C3A27; margin-bottom: 20px; font-size: 14px;'>
                    <strong>Comprendre les thématiques :</strong><br>
                    • 🏠 <b>Migrations</b> : Analyse les changements de domicile sur un an.<br>
                    • 💼 <b>Professionnelle</b> : Analyse les flux domicile-travail des actifs.<br>
                    • 🎓 <b>Scolaire</b> : Analyse le trajet entre lieu de résidence et lieu d'études.
                </div>""", unsafe_allow_html=True)

            with st.container():
                filter_bar("Filtres - Mobilités")
                col_geo_label, col_geo_options = st.columns([1, 3])
                with col_geo_label:
                    st.markdown("<div style='padding-top:8px;font-weight:600;font-size:14px;'>Niveau géographique</div>",
                                unsafe_allow_html=True)
                with col_geo_options:
                    mode_mob = st.radio("",
                        ["Comparaison Métropoles", "Comparaison communes métropole de Grenoble"],
                        key="mob_mode", horizontal=True, label_visibility="collapsed")

                if mode_mob == "Comparaison communes métropole de Grenoble":
                    met_choice = "Grenoble"
                    st.markdown("**Communes de la métropole de Grenoble**")
                    sel_communes_mob = st.multiselect("Sélection des communes",
                                                      sorted(COMMUNES[met_choice]),
                                                      default=sorted(COMMUNES[met_choice])[:2],
                                                      key="mob_communes")
                    coms_selection = sel_communes_mob
                else:
                    sel_metros_mob = st.multiselect("Métropoles à comparer", TOUTES, default=TOUTES[:3], key="mob_metros")
                    coms_selection = [c for m in sel_metros_mob for c in COMMUNES[m]]

                mob_col1, mob_col2 = st.columns(2)
                with mob_col1:
                    theme_mob = st.selectbox("Thématique d'analyse",
                        ["🏠 Migrations Résidentielles", "💼 Mobilité Professionnelle", "🎓 Mobilité Scolaire"],
                        key="mob_theme")

                if "Migrations" in theme_mob:
                    current_mob_df, col_orig, col_dest = df_res, "commune_origine", "commune_destination"
                    label_in, label_out = "Arrivées", "Départs"
                elif "Professionnelle" in theme_mob:
                    current_mob_df, col_orig, col_dest = df_prof, "commune_residence", "commune_travail"
                    label_in, label_out = "Entrants", "Sortants"
                else:
                    current_mob_df, col_orig, col_dest = df_scol, "commune_origine", "commune_destination"
                    label_in, label_out = "Élèves Entrants", "Élèves Sortants"

                if current_mob_df is not None:
                    annees_mob = sorted(current_mob_df["annee"].dropna().unique().astype(int), reverse=True)
                    with mob_col2:
                        sel_annee_mob = st.selectbox("Année", annees_mob, key="mob_annee")

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
                entities_mob.append({"name": target, "in": f_in, "out": f_out, "solde": f_in - f_out})
            df_plot_mob = pd.DataFrame(entities_mob)

            if not df_plot_mob.empty:
                st.markdown(f"#### Bilan net - {theme_mob} ({sel_annee_mob})",
                            help="Le solde net = entrées − sorties. Un chiffre positif signifie que le territoire gagne des flux (attractivité). Un chiffre négatif signifie qu'il en perd (répulsion ou dépendance envers un pôle voisin).")

                kpi_cols = st.columns(len(df_plot_mob))
                n_mob = len(df_plot_mob)
                for i, row in df_plot_mob.iterrows():
                    color_solde = "#006400" if row["solde"] >= 0 else "#8B0000"
                    val_formatee = f"{row['solde']:+,d}".replace(",", " ")
                    if mode_mob == "Comparaison communes métropole de Grenoble":
                        kpi_mob_color = PALETTE_COMMUNE[int(i * (len(PALETTE_COMMUNE)-1) / max(n_mob-1,1))]
                    else:
                        kpi_mob_color = COULEURS.get(row['name'], "#1B4332")
                    with kpi_cols[i]:
                        st.markdown(f"""
                        <div style='display:flex;flex-direction:row;align-items:stretch;border-radius:8px;
                            overflow:hidden;box-shadow:0 2px 6px rgba(0,0,0,0.1);background:#fff;
                            min-height:80px;border-left:6px solid {kpi_mob_color};'>
                            <div style='padding:10px 16px;display:flex;flex-direction:column;justify-content:center;'>
                                <div style='font-size:11px;font-weight:700;letter-spacing:0.08em;color:#666;text-transform:uppercase;'>{row['name']}</div>
                                <div style='font-size:24px;font-weight:bold;color:#111;'>{val_formatee}</div>
                                <div style='color:{color_solde};font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;'>SOLDE</div>
                            </div>
                        </div>""", unsafe_allow_html=True)

                st.markdown("---")

                noms_mob = df_plot_mob["name"].tolist()
                greno_vrect_args = None
                if "Grenoble" in noms_mob and mode_mob == "Comparaison Métropoles":
                    g_pos = noms_mob.index("Grenoble")
                    greno_vrect_args = dict(x0=g_pos - 0.45, x1=g_pos + 0.45,
                                            fillcolor="rgba(255,88,77,0.10)",
                                            line_color="#FF584D", line_width=1.5, layer="below")

                if mode_mob == "Comparaison communes métropole de Grenoble":
                    color_in_bar  = PALETTE_COMMUNE[0]
                    color_out_bar = PALETTE_COMMUNE[int(len(PALETTE_COMMUNE) * 0.5)]
                else:
                    color_in_bar  = PALETTE_METRO[int(len(PALETTE_METRO) * 0.3)]
                    color_out_bar = PALETTE_METRO[int(len(PALETTE_METRO) * 0.7)]

                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(
                        "##### Volume des échanges",
                        help="Compare, pour chaque territoire, le total des flux entrants (barres foncées) et sortants (barres claires). Un volume élevé avec des barres équilibrées = territoire de transit qui brasse beaucoup de flux sans en retenir. Un fort déséquilibre entrants > sortants = territoire très attractif."
                    )
                    fig_vol = go.Figure()
                    fig_vol.add_trace(go.Bar(
                        x=noms_mob, y=df_plot_mob["in"], name=label_in,
                        marker_color=color_in_bar,
                        hovertemplate="<b>Territoire : %{x}</b><br>" + label_in + " : %{y:.2s}<extra></extra>",
                    ))
                    fig_vol.add_trace(go.Bar(
                        x=noms_mob, y=df_plot_mob["out"], name=label_out,
                        marker_color=color_out_bar,
                        hovertemplate="<b>Territoire : %{x}</b><br>" + label_out + " : %{y:.2s}<extra></extra>",
                    ))
                    if greno_vrect_args:
                        fig_vol.add_vrect(**greno_vrect_args)
                    fig_vol.update_layout(barmode="group", height=350, margin=dict(t=20, b=60),
                                          legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02),
                                          xaxis=dict(title="Territoire", showgrid=False),
                                          yaxis=dict(title="Nombre de flux", showgrid=True, gridcolor="#eeeeee"))
                    st.plotly_chart(fig_vol, use_container_width=True)

                with c2:
                    st.markdown(
                        "##### Performance nette",
                        help="Solde net = entrées − sorties. Une barre positive (foncé) = le territoire gagne des flux et est attractif. Une barre négative (sombre) = le territoire perd des flux et dépend d'un pôle voisin. Ce graphique classe directement les territoires du plus au moins attractif en un seul indicateur."
                    )
                    colors_net = ["#006400" if s >= 0 else "#8B0000" for s in df_plot_mob["solde"]]
                    fig_net = go.Figure(go.Bar(
                        x=noms_mob, y=df_plot_mob["solde"],
                        marker_color=colors_net,
                        hovertemplate="<b>Territoire : %{x}</b><br>Solde net : %{y:.2s}<extra></extra>",
                    ))
                    fig_net.add_hline(y=0, line_dash="dash", line_color="#888")
                    if greno_vrect_args:
                        fig_net.add_vrect(**greno_vrect_args)
                    fig_net.update_layout(height=350, margin=dict(t=20, b=60),
                                          xaxis=dict(title="Territoire", showgrid=False),
                                          yaxis=dict(title="Solde (entrées − sorties)", showgrid=True, gridcolor="#eeeeee"))
                    st.plotly_chart(fig_net, use_container_width=True)

                with st.expander("💡 Comment interpréter ces deux graphiques ?"):
                    st.write(
                        "**Volume des échanges** : ce graphique compare les flux entrants (barres foncées) et sortants (barres claires) pour chaque territoire. "
                        "Il faut lire les deux barres ensemble pour comprendre la dynamique :\n"
                        "- **Barres élevées et équilibrées** : le territoire est un pôle d'échange ou de transit — beaucoup de personnes entrent et sortent, mais peu restent. Typique d'une ville-étape ou d'un grand pôle d'emploi avec une forte rotation.\n"
                        "- **Forte barre entrante > sortante** : territoire très attractif qui capte plus qu'il ne perd.\n"
                        "- **Forte barre sortante > entrante** : territoire d'émission — les habitants partent davantage qu'ils n'arrivent (souvent une commune résidentielle dont les actifs travaillent ailleurs).\n\n"
                        "**Performance nette (solde)** : c'est la synthèse en un seul chiffre. "
                        "Une barre verte (positive) signifie que le territoire gagne des flux nets — il est attractif. "
                        "Une barre rouge (négative) signifie qu'il en perd. "
                        "Ce graphique permet de classer rapidement les territoires du plus au moins attractif pour la thématique sélectionnée (résidentielle, professionnelle ou scolaire)."
                    )

                st.markdown("---")
                st.markdown("#### Analyse géographique des flux", help="Ces graphiques identifient les 10 principaux territoires d'origine (d'où viennent les personnes) et les 10 principales destinations (où vont les personnes) pour le territoire sélectionné.")

                if mode_mob == "Comparaison Métropoles":
                    selection_unique = len(sel_metros_mob) == 1
                else:
                    selection_unique = len(sel_communes_mob) == 1

                if not selection_unique:
                    if mode_mob == "Comparaison Métropoles":
                        st.info("L'analyse géographique des flux est disponible uniquement pour **une seule métropole** sélectionnée.")
                    else:
                        st.info("L'analyse géographique des flux est disponible uniquement pour **une seule commune** sélectionnée.")
                else:
                    if mode_mob == "Comparaison communes métropole de Grenoble":
                        color_top_in  = PALETTE_COMMUNE[0]
                        color_top_out = PALETTE_COMMUNE[int(len(PALETTE_COMMUNE) * 0.5)]
                    else:
                        color_top_in  = PALETTE_METRO[int(len(PALETTE_METRO) * 0.3)]
                        color_top_out = PALETTE_METRO[int(len(PALETTE_METRO) * 0.7)]

                    col_l, col_r = st.columns(2)
                    with col_l:
                        st.markdown(
                            f"<h5 style='text-align:center;'> Top 10 provenances ({label_in})</h5>",
                            unsafe_allow_html=True
                        )
                        raw_in = df_mob_filtered[df_mob_filtered[col_dest].isin(coms_selection)]
                        grouped_in = raw_in.groupby(col_orig)["flux"].sum().reset_index()
                        top_in = grouped_in.nlargest(10, "flux")
                        if not top_in.empty:
                            fig_in = px.bar(top_in, x="flux", y=col_orig, orientation="h",
                                            color_discrete_sequence=[color_top_in], text_auto=".0f")
                            fig_in.update_layout(yaxis=dict(categoryorder="total ascending", title=""),
                                                 xaxis=dict(title="Nombre de flux"), height=350)
                            st.plotly_chart(fig_in, use_container_width=True)

                    with col_r:
                        st.markdown(
                            f"<h5 style='text-align:center;'> Top 10 destinations ({label_out})</h5>",
                            unsafe_allow_html=True
                        )
                        raw_out = df_mob_filtered[df_mob_filtered[col_orig].isin(coms_selection)]
                        grouped_out = raw_out.groupby(col_dest)["flux"].sum().reset_index()
                        top_out = grouped_out.nlargest(10, "flux")
                        if not top_out.empty:
                            fig_out = px.bar(top_out, x="flux", y=col_dest, orientation="h",
                                             color_discrete_sequence=[color_top_out], text_auto=".0f")
                            fig_out.update_layout(yaxis=dict(categoryorder="total ascending", title=""),
                                                  xaxis=dict(title="Nombre de flux"), height=350)
                            st.plotly_chart(fig_out, use_container_width=True)

# ==============================================================================
# ONGLET 4 — MÉNAGES
# ==============================================================================
if vue == "Démographie":
    with tab4:

        data_men_ok = (df_men_age is not None) and (df_men_csp is not None)
        if not data_men_ok:
            st.info("📂 Fichiers de données sur les ménages introuvables.")
        else:
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
                    "professions_liberales", "cadre_admin_fonction_pub", "prof_scientifique_sup",
                    "info_art_spectacle", "cadre_commercial", "ingenieur_cadre_tech"],
                "Professions\nintermédiaires": [
                    "prof_enseignement", "prof_inter_sante_social", "prof_inter_fonction_pub",
                    "prof_inter_admin_com", "technicien", "agent_maitrise"],
                "Employés": ["emp_fonction_pub", "securite_defense", "emp_admin_entreprise",
                             "emp_commerce", "service_particulier"],
                "Ouvriers": ["ouvrier_qualif_indus", "ouvrier_qualif_artisanal", "conducteur_transport",
                             "cariste_magasinier", "ouvrier_peu_qualif_indus", "ouvrier_peu_qualif_artisanal",
                             "ouvrier_agricole"],
                "Retraités /\nInactifs": ["retraites_inactifs", "chomeur_jamais_travaille"],
            }
            TAILLES = {
                "1 pers.": (1, "1pers"), "2 pers.": (2, "2pers"), "3 pers.": (3, "3pers"),
                "4 pers.": (4, "4pers"), "5 pers.": (5, "5pers"), "6 pers. et +": (6, "6pers_ouplus"),
            }

            def somme_colonnes(df_ent, mots_cles):
                cols = [c for c in df_ent.columns if any(k in c for k in mots_cles)]
                return df_ent[cols].sum().sum() if cols else 0

            def nb_menages_depuis_age(df_ent_age):
                cols_men = [c for c in df_ent_age.columns
                            if c.startswith("Menages_") and c not in ("CODGEO", "LIBGEO")]
                return int(df_ent_age[cols_men].sum().sum()) if cols_men else 0

            def get_population_menages(ent):
                if mode_men == "Comparaison Métropoles":
                    return epci_val(ent, "population_2022")
                else:
                    if df_gen is None:
                        return np.nan
                    comm_norm = normalize_name(ent)
                    geo = df_gen["territoire"].astype(str).str.extract(
                        r"^(Commune|EPCI)\s*:\s*(.*?)\s*\(\d+\)\s*$")
                    mask = (geo[0] == "Commune") & (geo[1].apply(normalize_name) == comm_norm)
                    rows_g = df_gen[mask]
                    if rows_g.empty:
                        return np.nan
                    v = rows_g.iloc[0].get("population_2022", np.nan)
                    return float(v) if pd.notna(v) else np.nan

            def distrib_taille(df_ent_csp):
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

            with st.container():
                filter_bar("Filtres - Ménages")
                col_geo_label, col_geo_options = st.columns([1, 3])
                with col_geo_label:
                    st.markdown("<div style='padding-top:8px;font-weight:600;font-size:14px;'>Niveau géographique</div>",
                                unsafe_allow_html=True)
                with col_geo_options:
                    mode_men = st.radio("",
                        ["Comparaison Métropoles", "Comparaison communes métropole de Grenoble"],
                        key="men_mode", horizontal=True, label_visibility="collapsed")
                if mode_men == "Comparaison communes métropole de Grenoble":
                    sel_communes_men = st.multiselect("Commune de la métropole de Grenoble",
                                                      sorted(COMMUNES["Grenoble"]),
                                                      default=sorted(COMMUNES["Grenoble"])[:3],
                                                      key="men_communes")
                    selection_men = sel_communes_men
                else:
                    sel_metros_men = st.multiselect("Métropoles à comparer", TOUTES, default=TOUTES[:3],
                                                    key="men_metros")
                    selection_men = sel_metros_men

                theme_men = st.selectbox("Thématique d'analyse",
                    ["👨‍👩‍👧 Type & taille de ménage", "🧑‍💼 CSP du chef de ménage"], key="theme_men",
                    help="**Type & taille** : Composition familiale et taille des foyers.\n\n**CSP** : Catégorie socio-professionnelle de la personne de référence du foyer (chef de ménage).")

            st.markdown("---")

            if not selection_men:
                st.warning("⚠️ Sélectionnez au moins un territoire.")
                st.stop()

            def get_df_age(ent):
                if mode_men == "Comparaison Métropoles":
                    return df_men_age[df_men_age["metropole"] == ent]
                return df_men_age[df_men_age["LIBGEO"] == ent]

            def get_df_csp(ent):
                if mode_men == "Comparaison Métropoles":
                    return df_men_csp[df_men_csp["metropole"] == ent]
                return df_men_csp[df_men_csp["LIBGEO"] == ent]

            COLORS_COMM_MEN = ["#081C15","#1B4332","#2D6A4F","#40916C","#52B788",
                               "#74C69D","#95D5B2","#B7E4C7","#D8F3DC"]

            if mode_men == "Comparaison Métropoles":
                COLOR_MAP_ENT = {e: COULEURS.get(e, "#888888") for e in selection_men}
                COLOR_SEQ_ENT = [COULEURS.get(e, "#888888") for e in selection_men]
            else:
                COLOR_MAP_ENT = {e: COLORS_COMM_MEN[i % len(COLORS_COMM_MEN)]
                                 for i, e in enumerate(selection_men)}
                COLOR_SEQ_ENT = [COLORS_COMM_MEN[i % len(COLORS_COMM_MEN)]
                                 for i in range(len(selection_men))]

            PALETTE_TYPE = ["#3A3D44", "#7A7E87", "#A2A6AE", "#C8CACF", "#E8E8EB"]
            PALETTE_CSP_GREY = ["#3A3D44", "#555A62", "#7A7E87", "#9EA2A8",
                                 "#C8CACF", "#DFE0E2", "#E8E8EB"]

            # ════════════════════════════════════════════════════════════════
            # THÈME 1 — TYPE & TAILLE DE MÉNAGE
            # ════════════════════════════════════════════════════════════════
            if "Type" in theme_men:
                cols_age = [c for c in df_men_age.columns if c.startswith("Menages_")]

                st.markdown(
                    "#### Aperçu global des ménages",
                    help="**Nombre de ménages** : total des foyers ordinaires recensés (RP 2022), calculé en sommant toutes les colonnes du fichier Menage_age_situation.\n\n"
                         "**Personnes par ménage** : ratio Population 2022 / Nombre de ménages. La moyenne nationale est d'environ 2,2 personnes par ménage en France. Un ratio élevé (> 2,5) indique un territoire avec beaucoup de familles avec enfants."
                )
                kpi_cols = st.columns(len(selection_men))
                for i, ent in enumerate(selection_men):
                    df_age_ent = get_df_age(ent)
                    nb_men = nb_menages_depuis_age(df_age_ent)
                    pop = get_population_menages(ent)
                    ratio_str = f"{pop / nb_men:.2f} pers./ménage" if nb_men > 0 and not np.isnan(pop) else "N/D"
                    with kpi_cols[i]:
                        st.markdown(render_kpi_card(ent, fmt(nb_men), ratio_str, COLOR_SEQ_ENT[i]),
                                    unsafe_allow_html=True)

                st.markdown("---")

                st.markdown(
                    "##### Distribution par taille de ménage (%)",
                    help="Répartition des ménages selon leur nombre de personnes, calculée depuis le fichier CSP×taille (colonnes Menages_Npers_*). En France : ~37% de personnes seules (1 pers.), ~33% de couples sans enfant (2 pers.). Une forte part de 4 pers. et plus caractérise un territoire à profil familial."
                )
                rows_taille = []
                for ent in selection_men:
                    df_t = distrib_taille(get_df_csp(ent))
                    df_t["Territoire"] = ent
                    rows_taille.append(df_t)
                df_taille_all = pd.concat(rows_taille, ignore_index=True) if rows_taille else pd.DataFrame()

                if not df_taille_all.empty:
                    fig_taille = px.bar(
                        df_taille_all, x="Taille", y="Part (%)", color="Territoire",
                        barmode="group", text_auto=".1f",
                        color_discrete_map=COLOR_MAP_ENT,
                        category_orders={"Taille": list(TAILLES.keys())}, height=380,
                    )
                    fig_taille.update_traces(textposition="outside", textfont_size=9)
                    fig_taille.update_layout(legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02, title=""),
                                             xaxis_title="Taille du ménage",
                                             yaxis_title="Part des ménages (%)", margin=dict(t=20))
                    st.plotly_chart(style(fig_taille), use_container_width=True)

                st.markdown("---")

                c1, c2 = st.columns(2)
                rows_type = []
                for ent in selection_men:
                    df_age_ent = get_df_age(ent)
                    nb_total = df_age_ent[cols_age].sum().sum()
                    for nom, fn in TYPE_GROUPES.items():
                        cols_grp = fn(cols_age)
                        val = df_age_ent[cols_grp].sum().sum() if cols_grp else 0
                        rows_type.append({"Territoire": ent, "Type de ménage": nom,
                                          "Nombre": int(val),
                                          "Part (%)": val / nb_total * 100 if nb_total > 0 else 0})
                df_type = pd.DataFrame(rows_type)

                with c1:
                    st.markdown(
                        "##### Composition des ménages — volume",
                        help="Nombre absolu de foyers par type de composition familiale (personne seule, couple sans enfant, couple avec enfant(s), famille monoparentale, autre). Utile pour dimensionner les besoins réels en logements adaptés (studios, T3/T4, etc.) et en équipements (crèches, écoles)."
                    )
                    if not df_type.empty:
                        fig_vol = px.bar(df_type, x="Type de ménage", y="Nombre", color="Territoire",
                                         barmode="group", color_discrete_map=COLOR_MAP_ENT, height=400)
                        fig_vol.update_layout(legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02, title=""),
                                              xaxis_title="", yaxis_title="Nombre de ménages",
                                              xaxis_tickangle=-15, margin=dict(t=20))
                        st.plotly_chart(style(fig_vol), use_container_width=True)

                with c2:
                    st.markdown(
                        "##### Composition des ménages — structure (%)",
                        help="Répartition en pourcentage (base 100% par territoire). Neutralise l'effet de taille pour comparer la 'sociologie' de territoires de populations très différentes. Une forte part de personnes seules caractérise les centres-villes étudiants ou vieillissants. Une forte part de couples avec enfants indique un profil périurbain ou résidentiel familial."
                    )
                    if not df_type.empty:
                        fig_pct = px.bar(df_type, x="Part (%)", y="Territoire", color="Type de ménage",
                                         orientation="h", barmode="stack", text_auto=".1f",
                                         color_discrete_sequence=PALETTE_TYPE, height=400)
                        fig_pct.update_traces(textposition="inside", textfont_size=9)
                        territoires_pct = list(dict.fromkeys(df_type["Territoire"].tolist()))
                        if "Grenoble" in territoires_pct and mode_men == "Comparaison Métropoles":
                            g_pos = territoires_pct.index("Grenoble")
                            fig_pct.add_hrect(y0=g_pos - 0.45, y1=g_pos + 0.45,
                                              fillcolor="rgba(255,88,77,0.10)",
                                              line_color="#FF584D", line_width=1.5, layer="below")
                        fig_pct.update_layout(legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02, title=""),
                                              xaxis_title="Part des ménages (%)",
                                              yaxis_title="", margin=dict(t=20))
                        st.plotly_chart(style(fig_pct), use_container_width=True)

                with st.expander("💡 Comment interpréter ces graphiques ?"):
                    st.write(
                        "**Distribution par taille** : ce graphique révèle si le territoire est peuplé de petits foyers (studios, couples âgés) ou de grandes familles. "
                        "En France, la taille moyenne d'un ménage est d'environ **2,2 personnes**. "
                        "Un territoire avec beaucoup de ménages à 1 ou 2 personnes a souvent un profil urbain ou vieillissant. "
                        "Un territoire avec une forte part de 4 personnes et plus a un profil périurbain ou familial nécessitant plus d'équipements scolaires et de logements spacieux.\n\n"
                        "**Volume (barres groupées)** : montre les besoins absolus en logements de chaque type pour chaque territoire. "
                        "C'est l'indicateur à utiliser pour dimensionner une politique d'habitat : combien faut-il de studios ? de grands appartements ? de maisons ?\n\n"
                        "**Structure % (barres empilées)** : neutralise l'effet de taille du territoire. "
                        "Un territoire avec 40% de personnes seules a un profil social très différent d'un territoire à 40% de couples avec enfants, même si leurs populations totales sont très différentes. "
                        "Ce graphique permet de comparer objectivement la 'sociologie' des territoires."
                    )

            # ════════════════════════════════════════════════════════════════
            # THÈME 2 — CSP DU CHEF DE MÉNAGE
            # ════════════════════════════════════════════════════════════════
            else:
                cols_csp = [c for c in df_men_csp.columns if c.startswith("Menages_")]

                rows_csp, kpi_csp = [], []
                for ent in selection_men:
                    df_age_ent  = get_df_age(ent)
                    df_csp_ent  = get_df_csp(ent)
                    nb_total_csp = df_csp_ent[cols_csp].sum().sum()
                    nb_men = nb_menages_depuis_age(df_age_ent)
                    pop = get_population_menages(ent)
                    best_grp, best_val = "N/D", 0
                    for nom_grp, mots in CSP_GROUPES.items():
                        val = somme_colonnes(df_csp_ent, mots)
                        pct = val / nb_total_csp * 100 if nb_total_csp > 0 else 0
                        rows_csp.append({"Territoire": ent, "CSP": nom_grp,
                                         "Nombre": int(val), "Part (%)": round(pct, 1)})
                        if val > best_val:
                            best_val = val
                            best_grp = nom_grp.replace("\n", " ")
                    kpi_csp.append({"ent": ent, "total": nb_men, "dominante": best_grp})
                df_csp_all = pd.DataFrame(rows_csp)

                st.markdown(
                    "#### Profil socio-professionnel des ménages",
                    help="La CSP affichée est celle de la **personne de référence du foyer** (chef de ménage), généralement la personne la plus âgée ou celle avec le revenu le plus élevé. Source : INSEE RP 2022, fichier Ménages × CSP × nombre de personnes.\n\n"
                         "**Nombre de ménages** : total des foyers recensés dans le territoire.\n\n"
                         "**CSP dominante** : la catégorie socio-professionnelle qui rassemble le plus grand nombre de ménages."
                )
                kpi_cols = st.columns(len(kpi_csp))
                for i, d in enumerate(kpi_csp):
                    with kpi_cols[i]:
                        st.markdown(render_kpi_card(d["ent"], fmt(d["total"]),
                                                    f"Majorité : {d['dominante']}",
                                                    COLOR_SEQ_ENT[i]), unsafe_allow_html=True)

                st.markdown("---")

                st.markdown(
                    "##### Structure socio-professionnelle des ménages (%)",
                    help="Répartition des ménages par grande catégorie socio-professionnelle (base 100% par territoire). Permet de comparer le profil social de territoires de tailles très différentes sur un pied d'égalité. Un écart important sur la part des cadres indique souvent un pôle d'attractivité économique ou une zone résidentielle favorisée."
                )
                if not df_csp_all.empty:
                    ordre_csp = list(CSP_GROUPES.keys())
                    n_csp = len(ordre_csp)
                    grey_csp = [f"#{v:02x}{v:02x}{v:02x}" for v in
                                [int(0x3A + (0xE8 - 0x3A) * i / (n_csp - 1)) for i in range(n_csp)]]
                    fig_pct_csp = px.bar(df_csp_all, x="Territoire", y="Part (%)", color="CSP",
                                         barmode="stack", text_auto=".1f",
                                         color_discrete_sequence=grey_csp,
                                         category_orders={"CSP": ordre_csp}, height=420)
                    fig_pct_csp.update_traces(textposition="inside", textfont_size=9)
                    territoires_csp = list(dict.fromkeys(df_csp_all["Territoire"].tolist()))
                    if "Grenoble" in territoires_csp and mode_men == "Comparaison Métropoles":
                        g_pos = territoires_csp.index("Grenoble")
                        fig_pct_csp.add_vrect(x0=g_pos - 0.45, x1=g_pos + 0.45,
                                              fillcolor="rgba(255,88,77,0.10)",
                                              line_color="#FF584D", line_width=1.5, layer="below")
                    fig_pct_csp.update_layout(legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02, title=""),
                                              yaxis_title="Part des ménages (%)",
                                              xaxis_title="", margin=dict(t=20))
                    st.plotly_chart(style(fig_pct_csp), use_container_width=True)

                st.markdown("---")

                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(
                        "##### Volume par CSP (nombre de ménages)",
                        help="Nombre absolu de ménages par catégorie socio-professionnelle. Utile pour estimer les besoins en services publics : un grand nombre de ménages de retraités implique des besoins accrus en Ehpad, soins à domicile et transports adaptés ; un grand nombre de cadres signale un besoin en logements de qualité et en services haut de gamme."
                    )
                    if not df_csp_all.empty:
                        fig_vol_csp = px.bar(df_csp_all, x="Nombre", y="CSP", color="Territoire",
                                             orientation="h", barmode="group",
                                             color_discrete_map=COLOR_MAP_ENT,
                                             category_orders={"CSP": list(CSP_GROUPES.keys())}, height=420)
                        fig_vol_csp.update_layout(legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02, title=""),
                                                  xaxis_title="Nombre de ménages",
                                                  yaxis_title="", margin=dict(t=20))
                        st.plotly_chart(style(fig_vol_csp), use_container_width=True)

                with c2:
                    st.markdown(
                        "##### Taille moyenne des ménages par CSP",
                        help="Compare la taille moyenne des foyers selon la CSP du chef de ménage. Calcul : Σ(nb_ménages_Npers × N) / Σ(nb_ménages_Npers) pour chaque CSP. Les ménages de cadres et professions intermédiaires ont souvent plus d'enfants que les ménages d'employés, qui vivent davantage seuls ou en couple. Les retraités ont les ménages les plus petits."
                    )
                    rows_taille_csp = []
                    for ent in selection_men:
                        df_csp_ent = get_df_csp(ent)
                        for nom_grp, mots in CSP_GROUPES.items():
                            total_m, total_p = 0, 0
                            for label, (nb_pers, slug) in TAILLES.items():
                                cols_filtre = [c for c in df_csp_ent.columns
                                               if slug in c and any(k in c for k in mots)]
                                nb = df_csp_ent[cols_filtre].sum().sum() if cols_filtre else 0
                                total_m += nb
                                total_p += nb * nb_pers
                            taille_grp = total_p / total_m if total_m > 0 else np.nan
                            if not np.isnan(taille_grp):
                                rows_taille_csp.append({"Territoire": ent,
                                                        "CSP": nom_grp.replace("\n", " "),
                                                        "Taille moyenne": round(taille_grp, 2)})
                    df_taille_csp = pd.DataFrame(rows_taille_csp)
                    if not df_taille_csp.empty:
                        fig_taille_csp = px.bar(df_taille_csp, x="Taille moyenne", y="CSP", color="Territoire",
                                                orientation="h", barmode="group",
                                                color_discrete_map=COLOR_MAP_ENT,
                                                height=420, text_auto=".2f")
                        fig_taille_csp.update_traces(textposition="outside", textfont_size=9)
                        fig_taille_csp.update_layout(legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02, title=""),
                                                     xaxis_title="Personnes par ménage (moyenne)",
                                                     yaxis_title="", margin=dict(t=20),
                                                     xaxis=dict(range=[0, 5]))
                        st.plotly_chart(style(fig_taille_csp), use_container_width=True)

                with st.expander("💡 Guide d'interprétation des CSP"):
                    st.write(
                        "La **catégorie socio-professionnelle (CSP)** affichée est celle de la personne de référence du ménage (chef de foyer). "
                        "Les 7 grandes catégories regroupent les 30+ sous-catégories de l'INSEE :\n\n"
                        "- **Cadres & Prof. sup.** : ingénieurs, médecins, cadres admin./commerciaux, artistes. "
                        "Fort pouvoir d'achat, ménages souvent bi-actifs avec enfants. La présence élevée de cette catégorie signale un pôle économique attractif ou une zone résidentielle favorisée.\n"
                        "- **Prof. intermédiaires** : infirmiers, techniciens, enseignants du 1er/2nd degré, agents de maîtrise. "
                        "Catégorie pivot du tissu social, souvent bien représentée dans les villes moyennes dynamiques.\n"
                        "- **Employés** : agents de la fonction publique, employés de commerce et de services, agents de sécurité. "
                        "Ménages plus souvent petits (personnes seules ou couples sans enfant).\n"
                        "- **Ouvriers** : qualifiés et peu qualifiés, conducteurs, ouvriers agricoles. "
                        "Historiquement, les ménages ouvriers ont plus d'enfants que la moyenne.\n"
                        "- **Retraités / Inactifs** : retraités de toutes catégories + chômeurs n'ayant jamais travaillé. "
                        "Souvent la catégorie majoritaire dans les communes vieillissantes — indicateur fort du besoin en services gériatriques.\n\n"
                        "**Taille moyenne par CSP** : les différences révèlent les modes de vie associés à chaque catégorie. "
                        "Les ouvriers et agricoles ont historiquement des familles plus nombreuses ; "
                        "les retraités et employés vivent plus souvent seuls ou en couple sans enfant. "
                        "Comparer les tailles entre territoires pour une même CSP révèle des différences culturelles ou sociales locales."
                    )

# ==============================================================================
# ONGLET 5 - Population active 25-54 ans
# ==============================================================================
if vue == "Démographie":
    with tab6:

        if df_csp_new.empty or "ANNEE" not in df_csp_new.columns:
            st.info("📂 Données CSP/Diplôme non trouvées. Vérifiez les fichiers.")
        else:
            st.markdown("""
            <div style='background-color: #f1f8f5; padding: 15px; border-radius: 10px; border-left: 5px solid #1C3A27; margin-bottom: 20px;'>
                <strong>Origine des données :</strong> Ces chiffres sont issus des recensements de l'<b>INSEE</b>.
                Ils recensent la <b>population active de 25 à 54 ans</b>, le cœur stable du marché du travail.
                Quand vous comparez deux territoires, un graphique d'indice de spécialisation s'affiche en plus.
            </div>""", unsafe_allow_html=True)

            with st.container():
                filter_bar("Filtres - Profil des actifs (25-54 ans)")
                csp_geo_l, csp_geo_r = st.columns([1, 3])
                with csp_geo_l:
                    filter_row_label("Niveau géographique")
                with csp_geo_r:
                    mode_analyse = st.radio("",
                        ["Comparaison Métropoles", "Comparaison communes métropole de Grenoble"],
                        key="csp_mode", horizontal=True, label_visibility="collapsed")
                csp_row1_c1, csp_row1_c2 = st.columns(2)
                with csp_row1_c1:
                    theme_analyse = st.selectbox("Thématique",
                        ["Secteurs d'activité (CSP)", "Niveau de diplôme"], key="csp_theme",
                        help="**Secteurs d'activité (CSP)** : répartition des actifs 25–54 ans par catégorie socio-professionnelle.\n\n**Niveau de diplôme** : répartition des actifs 25–54 ans par niveau d'études atteint.")

                current_df_csp  = df_csp_new if theme_analyse == "Secteurs d'activité (CSP)" else df_dip_new
                current_map_csp = CSP_MAP_NEW if theme_analyse == "Secteurs d'activité (CSP)" else DIP_MAP

                annees_csp = sorted(current_df_csp["ANNEE"].dropna().unique(), reverse=True) if not current_df_csp.empty else []
                with csp_row1_c2:
                    sel_annee_csp = st.selectbox("Année", annees_csp, key="csp_annee",
                                                 help="Année du recensement INSEE de référence. Les données disponibles sont généralement 2011, 2016 et 2022.") if annees_csp else None

                if mode_analyse == "Comparaison communes métropole de Grenoble":
                    clist = sorted(COMMUNES["Grenoble"])
                    sel_communes_csp = st.multiselect("Commune de la métropole de Grenoble", clist,
                                                      default=["Grenoble", "Meylan"], key="csp_communes",
                                                      help="Sélectionnez les communes à analyser.")
                    entities_names = sel_communes_csp
                else:
                    sel_metros_csp = st.multiselect("Métropoles", TOUTES, default=["Grenoble", "Rouen"],
                                                    key="csp_metros", help="Sélectionnez les métropoles à comparer.")
                    entities_names = sel_metros_csp

                sel_cats = st.multiselect("Catégories à afficher",
                                          options=list(current_map_csp.values()),
                                          default=list(current_map_csp.values()), key="csp_cats",
                                          help="Filtrez les catégories pour simplifier la lecture des graphiques. Désélectionner une catégorie la retire de tous les graphiques.")

            COLORS_COMM_CSP5 = ["#081C15","#1B4332","#2D6A4F","#40916C","#52B788",
                                 "#74C69D","#95D5B2","#B7E4C7","#D8F3DC"]

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

                    kpi_cols_csp = st.columns(len(entities_csp))
                    for i, entity in enumerate(entities_csp):
                        total_actifs = entity["data"][sel_cats].sum()
                        val_formatee = f"{int(total_actifs):,d}".replace(",", " ")
                        if mode_analyse == "Comparaison Métropoles":
                            kpi_color5 = COULEURS.get(entity['name'], "#888888")
                        else:
                            kpi_color5 = COLORS_COMM_CSP5[i % len(COLORS_COMM_CSP5)]
                        with kpi_cols_csp[i]:
                            st.markdown(f"""
                            <div style='display:flex;flex-direction:row;align-items:stretch;border-radius:8px;
                                overflow:hidden;box-shadow:0 2px 6px rgba(0,0,0,0.1);background:#fff;
                                min-height:80px;border-left:6px solid {kpi_color5};'>
                                <div style='padding:10px 16px;display:flex;flex-direction:column;justify-content:center;'>
                                    <div style='font-size:11px;font-weight:700;letter-spacing:0.08em;color:#666;text-transform:uppercase;'>{entity['name']}</div>
                                    <div style='font-size:24px;font-weight:bold;color:#111;'>{val_formatee}</div>
                                    <div style='color:{kpi_color5};font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;'>Actifs 25-54 ans</div>
                                </div>
                            </div>""", unsafe_allow_html=True)

                    c1, c2 = st.columns(2)
                    with c1:
                        st.subheader(
                            "Répartition en volume",
                            help="Nombre réel d'actifs 25–54 ans par catégorie (CSP ou niveau de diplôme). Permet de comparer les effectifs absolus et de dimensionner les besoins en formation, en emploi ou en services. Une catégorie très représentée en volume a un poids économique réel important sur le territoire."
                        )
                        fig_bar_csp = go.Figure()
                        for i, ent in enumerate(entities_csp):
                            if mode_analyse == "Comparaison Métropoles":
                                bar_color = COULEURS.get(ent["name"], "#888888")
                            else:
                                bar_color = COLORS_COMM_CSP5[i % len(COLORS_COMM_CSP5)]
                            fig_bar_csp.add_trace(go.Bar(
                                x=sel_cats, y=ent["data"][sel_cats],
                                name=ent["name"], marker_color=bar_color,
                                hovertemplate="<b>Territoire : " + ent["name"] + "</b><br>%{x} : %{y:.2s}<extra></extra>",
                            ))
                        fig_bar_csp.update_layout(barmode="group", height=400, margin=dict(t=20, b=20))
                        st.plotly_chart(fig_bar_csp, use_container_width=True)

                    with c2:
                        st.subheader(
                            "Profil structurel (%)",
                            help="Répartition en pourcentage de chaque catégorie dans la population active du territoire (base 100%). Permet de comparer la spécialisation socio-professionnelle ou le niveau d'éducation indépendamment de la taille du territoire. Un territoire avec 30% de cadres a un profil très différent d'un territoire avec 30% d'ouvriers, même si leurs populations totales sont semblables."
                        )
                        fig_radar_csp = go.Figure()
                        for i, ent in enumerate(entities_csp):
                            v = ent["data"][sel_cats]
                            pct = (v / v.sum() * 100).fillna(0)
                            if mode_analyse == "Comparaison Métropoles":
                                radar_color = COULEURS.get(ent["name"], "#888888")
                            else:
                                radar_color = COLORS_COMM_CSP5[i % len(COLORS_COMM_CSP5)]
                            fig_radar_csp.add_trace(go.Scatterpolar(
                                r=list(pct) + [pct.iloc[0]],
                                theta=sel_cats + [sel_cats[0]],
                                fill="toself", name=ent["name"],
                                line_color=radar_color,
                                hovertemplate="<b>Territoire : " + ent["name"] + "</b><br>%{theta} : %{r:.2f}%<extra></extra>",
                            ))
                        fig_radar_csp.update_layout(height=400, margin=dict(t=50, b=50))
                        st.plotly_chart(fig_radar_csp, use_container_width=True)

                    with st.expander("💡 Comment interpréter ces deux graphiques ?"):
                        st.write(
                            "**Répartition en volume (barres groupées)** : ce graphique montre les effectifs réels par catégorie. "
                            "Il est utile pour évaluer le poids économique d'une catégorie : "
                            "un grand nombre d'ouvriers implique des besoins en logements abordables, en transports et en formations industrielles ; "
                            "un grand nombre de cadres signale un territoire à fort potentiel d'innovation mais avec des tensions sur l'immobilier. "
                            "Attention : ce graphique est sensible à la taille du territoire — une grande métropole aura toujours plus d'effectifs absolus qu'une petite commune.\n\n"
                            "**Profil structurel en radar (%)** : ce graphique neutralise l'effet de taille en montrant la part relative de chaque catégorie dans la population active. "
                            "Plus le polygone est étendu sur un axe, plus cette catégorie est surreprésentée par rapport aux autres. "
                            "Deux territoires avec des polygones de forme similaire ont des structures socio-professionnelles proches, même si leurs populations totales sont très différentes. "
                            "Comparer les formes des polygones permet d'identifier rapidement les spécialisations de chaque territoire.\n\n"
                            "**Conseil de lecture** : utilisez le volume pour identifier les enjeux de service public, et le radar pour identifier les spécialisations et les similitudes/différences entre territoires."
                        )

                    if len(entities_csp) == 2:
                        t1_name = entities_names[0]
                        t2_name = entities_names[1]
                        st.markdown("---")
                        st.markdown(f"### Guide de lecture : Spécialisation du Territoire 1 ({t1_name}) face au Territoire 2 ({t2_name})")
                        st.markdown(f"""
                        <div style='background-color:#f8f9fa;padding:18px;border-radius:8px;border:1px solid #e0e0e0;margin-bottom:20px;'>
                            <h5 style='margin-top:0;'>💡 Comment lire ce graphique et ce tableau ?</h5>
                            <p style='font-size:14px;'>L'indice compare si une catégorie est plus ou moins présente en <b>proportion</b> dans le Territoire 1 par rapport au Territoire 2.</p>
                            <ul style='font-size:14px;'>
                                <li><b>Indice > 100 :</b> La catégorie est <b>surreprésentée</b> dans le Territoire 1 ({t1_name}).</li>
                                <li><b>Indice = 100 :</b> Équilibre parfait.</li>
                                <li><b>Indice < 100 :</b> La catégorie est <b>sous-représentée</b> dans le Territoire 1.</li>
                            </ul>
                            <p style='font-size:14px;'><b>Important :</b> Une forte surreprésentation sur un petit nombre a moins d'impact qu'une légère spécialisation sur des milliers d'actifs.</p>
                        </div>""", unsafe_allow_html=True)

                        v1, v2 = entities_csp[0]["data"][sel_cats], entities_csp[1]["data"][sel_cats]
                        t1_total, t2_total = v1.sum(), v2.sum()
                        spec = ((v1 / t1_total) / (v2 / t2_total) * 100).fillna(100)
                        fig_spec = px.bar(x=sel_cats, y=spec, color=spec, color_continuous_scale="RdYlGn",
                                          title=f"Spécialisation : {t1_name} / {t2_name}")
                        fig_spec.add_hline(y=100, line_dash="dash", line_color="black")
                        fig_spec.update_layout(height=450, coloraxis_showscale=False, yaxis_title="Indice (Base 100)")
                        st.plotly_chart(fig_spec, use_container_width=True)

                        with st.expander("Voir le tableau récapitulatif (Effectifs et Indice)", expanded=True):
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
    s1, s2, s3, s4 = st.tabs(["🤝 Solidarité", "🎓 Éducation", "🏥 Santé", "🗳️ Participation citoyenne"])

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

                    with st.container():
                        filter_bar("Filtres - Solidarité CAF")
                        f1, f2 = st.columns([1, 3])
                        with f1:
                            filter_row_label("Niveau géographique")
                        with f2:
                            mode_caf = st.radio(
                                "", ["Comparaison Métropoles", "Comparaison communes métropole de Grenoble"],
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
                                y_max_qf = qf_data.groupby(geo_col)[metric_key].sum().max()

                                if is_metro:
                                    n_tranches = len(qf_order)
                                    grey_shades = [f"#{v:02x}{v:02x}{v:02x}" for v in [int(0x77 + (220 - 0x77) * i / (n_tranches - 1)) for i in range(n_tranches)]]
                                    qf_color_map = {tranche: grey_shades[j] for j, tranche in enumerate(qf_order)}
                                    fig_qf = px.bar(qf_data.sort_values("QF_ord"), x=geo_col, y=metric_key, color="Quotient familial", color_discrete_map=qf_color_map, barmode="stack", labels={geo_col: "", metric_key: label_metric}, height=380)
                                    grenoble_agglo = next((a for a in qf_data[geo_col].unique() if "Grenoble" in a), None)
                                    if grenoble_agglo:
                                        order_x_qf = order_x if order_x else list(dict.fromkeys(qf_data[geo_col].tolist()))
                                        if grenoble_agglo in order_x_qf:
                                            g_pos_qf = order_x_qf.index(grenoble_agglo)
                                            fig_qf.add_vrect(x0=g_pos_qf - 0.45, x1=g_pos_qf + 0.45,
                                                             fillcolor="rgba(255,88,77,0.10)",
                                                             line_color="#FF584D", line_width=1.5, layer="below")
                                else:
                                    fig_qf = px.bar(qf_data.sort_values("QF_ord"), x=geo_col, y=metric_key, color="Quotient familial", color_discrete_sequence=color_seq, barmode="stack", labels={geo_col: "", metric_key: label_metric}, height=380)
                                    fig_qf.update_traces(marker_line_width=0)

                                fig_qf.update_traces(
                                    hovertemplate="<b>%{x}</b><br>" + label_metric + " : <b>%{y:,.0f}</b><extra></extra>"
                                )
                                fig_qf.update_layout(
                                    separators=", ",
                                    yaxis=dict(range=[0, y_max_qf * 1.1]),
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
                                    margin=dict(t=40, r=40, b=80)
                                )
                                st.plotly_chart(style(fig_qf, 40), use_container_width=True)

                                with c2:
                                    st.markdown(f"##### Classement des territoires", help="Volume total pour l'indicateur sélectionné.")
                                    top_ent = df_fil.groupby(geo_col, as_index=False)[metric_key].sum().sort_values(by=metric_key, ascending=True if not is_metro else False)
                                    top_ent["text_display"] = top_ent[metric_key].apply(lambda x: fmt(x, suffix=" €" if "Montant" in metric_key else ""))
                                    if is_metro:
                                        top_ent["Metropole_Key"] = top_ent[geo_col].apply(lambda x: next((m for m in COULEURS.keys() if m in x), x))
                                        fig_top = px.bar(top_ent, x=metric_key, y=geo_col, orientation="h", color="Metropole_Key", color_discrete_map=COULEURS, text="text_display", labels={geo_col: "", metric_key: label_metric}, height=380)
                                    else:
                                        fig_top = px.bar(top_ent, x=metric_key, y=geo_col, orientation="h", color=geo_col, color_discrete_sequence=PALETTE_COMMUNE, text="text_display", labels={geo_col: "", metric_key: label_metric}, height=380)
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
                                fig_bar_comp = px.bar(
                                    bdata_long, x="Valeur", y="Type d'aide", color=color_group,
                                    color_discrete_map=color_map, color_discrete_sequence=color_seq,
                                    barmode="group", orientation="h", text_auto=",.0f",
                                    labels={"Valeur": "Volume", "Type d'aide": "", color_group: "Territoire"}, height=450
                                )
                                fig_bar_comp.update_traces(
                                    hovertemplate="<b>%{y}</b><br>Volume : <b>%{x:,.0f}</b><extra></extra>"
                                )
                                if is_metro:
                                    for trace in fig_bar_comp.data:
                                        if "Grenoble" in trace.name:
                                            trace.marker.line.width = 2
                                            trace.marker.line.color = "#FF584D"
                                fig_bar_comp.update_layout(
                                    separators=", ",
                                    legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02),
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
    # ONGLET 2 - ÉDUCATION (Établissements Scolaires)
    # ──────────────────────────────────────────────────────────────────────────
    with s2:
        if df_eff is None or df_eff.empty:
            st.info("Fichier `education_filtre.csv` introuvable.")
        else:
            st.markdown("""
                        <div style='background-color: #f1f8f5; padding: 15px; border-radius: 10px; border-left: 5px solid #1C3A27; margin-bottom: 20px;'>
                        <strong>Note sur les données :</strong> Le nombre d'élèves est donné à titre indicatif, certains établissements ne renseignent pas cet effectif.
                        Les totaux peuvent donc être sous-estimés et ne reflètent pas nécessairement la réalité exacte. De plus les données concernent seulement le premier et le second degré.
                        </div>""", unsafe_allow_html=True)
            df_eff_w   = df_eff.copy()
            metros_eff = sorted(df_eff_w["metropole"].dropna().unique())

            LABEL_NATURE = {
                "ECOLE MATERNELLE":                        "Maternelle",
                "ECOLE DE NIVEAU ELEMENTAIRE":             "Élémentaire",
                "ECOLE ELEMENTAIRE D APPLICATION":         "Élém. application",
                "ECOLE DE NIVEAU ELEMENTAIRE SPECIALISEE": "Élém. spécialisée",
                "COLLEGE":                                 "Collège",
                "LYCEE D ENSEIGNEMENT GENERAL":            "Lycée Général",
                "LYCEE ENSEIGNT GENERAL ET TECHNOLOGIQUE": "Lycée GT",
                "LYCEE PROFESSIONNEL":                     "Lycée Pro",
                "LYCEE POLYVALENT":                        "Lycée Polyvalent",
                "SECTION D ENSEIGNEMENT PROFESSIONNEL":    "SEP",
                "ETABLISSEMENT REGIONAL D'ENSEIGNT ADAPTE":"EREA",
            }
            TYPES_ETABLISSEMENTS = list(LABEL_NATURE.keys())

            # ── Filtres ─────────────────────────────────────────────────────
            with st.container():
                filter_bar("Filtres - Établissements scolaires")
                f1, f2 = st.columns([1, 3])
                with f1:
                    filter_row_label("Niveau géographique")
                with f2:
                    mode_eff = st.radio(
                        "", ["Comparaison Métropoles", "Comparaison communes métropole de Grenoble"],
                        key="eff_mode", horizontal=True, label_visibility="collapsed"
                    )
                if mode_eff == "Comparaison Métropoles":
                    sel_entites_eff = st.multiselect(
                        "Métropoles à comparer", metros_eff,
                        default=metros_eff, key="eff_metros"
                    )
                else:
                    communes_gre = sorted(
                        df_eff_w[df_eff_w["metropole"] == "Grenoble"]["Nom_commune"].dropna().unique()
                    )
                    sel_entites_eff = st.multiselect(
                        "Communes de Grenoble", communes_gre,
                        default=communes_gre[:5] if communes_gre else [],
                        key="eff_communes"
                    )

                natures_dispo = sorted(df_eff_w["libelle_nature"].dropna().unique())
                c1, c2 = st.columns([1, 1])
                with c1:
                    natures_connues = [n for n in TYPES_ETABLISSEMENTS if n in natures_dispo]
                    nature_choices = ["Tous"] + natures_connues
                    sel_nature = st.selectbox(
                        "Type d'établissement",
                        nature_choices,
                        format_func=lambda n: "Tous" if n == "Tous" else LABEL_NATURE.get(n, n),
                        key="eff_nature"
                    )
                with c2:
                    sel_secteur = st.selectbox(
                        "Secteur", ["Tous", "Public", "Privé"],
                        key="eff_secteur"
                    )
                st.markdown('</div>', unsafe_allow_html=True)

            geo_col  = "metropole" if mode_eff == "Comparaison Métropoles" else "Nom_commune"
            is_metro = (mode_eff == "Comparaison Métropoles")

            # ── Filtrage ────────────────────────────────────────────────────
            df_e = df_eff_w.copy()
            if sel_nature != "Tous":
                df_e = df_e[df_e["libelle_nature"] == sel_nature]
            if sel_secteur != "Tous":
                df_e = df_e[df_e["Statut_public_prive"] == sel_secteur]
            if is_metro:
                df_e = df_e[df_e["metropole"].isin(sel_entites_eff)]
            else:
                df_e = df_e[(df_e["metropole"] == "Grenoble") & (df_e["Nom_commune"].isin(sel_entites_eff))]

            st.markdown("---")

            if df_e.empty or not sel_entites_eff:
                st.warning("⚠️ Aucune donnée pour les filtres sélectionnés.")
            else:
                total_etab   = len(df_e)
                total_eleves = int(df_e["Nombre_d_eleves"].sum())
                nb_rep       = int(df_e["Appartenance_Education_Prioritaire"].isin(["REP", "REP+"]).sum())
                kpi_border_color = "#666" if is_metro else "#1e5631"

                st.markdown("#### Synthèse des établissements scolaires")
                k1, k2, k3 = st.columns(3)
                with k1:
                    st.markdown(render_solidarite_kpi(
                        "Établissements", fmt(total_etab), "Établissements recensés",
                        kpi_border_color), unsafe_allow_html=True)
                with k2:
                    st.markdown(render_solidarite_kpi(
                        "Élèves", fmt(total_eleves), "Élèves inscrits (total)",
                        kpi_border_color), unsafe_allow_html=True)
                with k3:
                    st.markdown(render_solidarite_kpi(
                        "Éducation Prioritaire", fmt(nb_rep), "Établissements REP / REP+",
                        kpi_border_color), unsafe_allow_html=True)

                st.markdown("---")

                # ── Palettes ─────────────────────────────────────────────────
                PALETTE_METRO   = px.colors.sequential.Greys[2:]
                PALETTE_COMMUNE = px.colors.sequential.Greens_r
                color_map = COULEURS if is_metro else None
                color_seq = PALETTE_METRO if is_metro else PALETTE_COMMUNE

                # ── Graphique 1 : Volume d'élèves par territoire ──────────────
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(
                        "##### Volume d'élèves",
                        help="Nombre total d'élèves inscrits selon les filtres sélectionnés."
                    )
                    by_entite = (
                        df_e.groupby(geo_col, as_index=False)["Nombre_d_eleves"]
                        .sum().sort_values("Nombre_d_eleves", ascending=False)
                    )
                    by_entite["text_display"] = by_entite["Nombre_d_eleves"].apply(fmt)
                    y_max_vol = by_entite["Nombre_d_eleves"].max()
                    fig_bar = px.bar(
                        by_entite, x=geo_col, y="Nombre_d_eleves",
                        color=geo_col,
                        color_discrete_map=color_map,
                        color_discrete_sequence=color_seq,
                        text="text_display",
                        labels={geo_col: "", "Nombre_d_eleves": "Élèves"},
                        height=380
                    )
                    fig_bar.update_traces(
                        textposition="inside",
                        hovertemplate="<b>%{x}</b><br>Élèves : <b>%{text}</b><extra></extra>"
                    )
                    fig_bar.update_layout(
                        showlegend=False,
                        yaxis=dict(range=[0, y_max_vol * 1.15]),
                        xaxis=dict(categoryorder="array", categoryarray=by_entite[geo_col].tolist())
                    )
                    if is_metro:
                        grenoble_agglo = next((a for a in by_entite[geo_col].tolist() if "Grenoble" in str(a)), None)
                    st.plotly_chart(style(fig_bar, 40), use_container_width=True)

                # ── Graphique 2 : Nombre d'établissements par territoire ───────
                with c2:
                    st.markdown(
                        "##### Nombre d'établissements",
                        help="Nombre d'établissements recensés selon les filtres sélectionnés."
                    )
                    by_etab = (
                        df_e.groupby(geo_col, as_index=False)
                        .size().rename(columns={"size": "nb_etab"})
                        .sort_values("nb_etab", ascending=False)
                    )
                    by_etab["text_display"] = by_etab["nb_etab"].apply(fmt)
                    y_max_etab = by_etab["nb_etab"].max()
                    fig_etab = px.bar(
                        by_etab, x=geo_col, y="nb_etab",
                        color=geo_col,
                        color_discrete_map=color_map,
                        color_discrete_sequence=color_seq,
                        text="text_display",
                        labels={geo_col: "", "nb_etab": "Établissements"},
                        height=380
                    )
                    fig_etab.update_traces(
                        textposition="inside",
                        hovertemplate="<b>%{x}</b><br>Établissements : <b>%{text}</b><extra></extra>"
                    )
                    fig_etab.update_layout(
                        showlegend=False,
                        yaxis=dict(range=[0, y_max_etab * 1.15]),
                        xaxis=dict(categoryorder="array", categoryarray=by_etab[geo_col].tolist())
                    )
                    if is_metro:
                        grenoble_agglo = next((a for a in by_etab[geo_col].tolist() if "Grenoble" in str(a)), None)
                    st.plotly_chart(style(fig_etab, 40), use_container_width=True)

                st.markdown("---")

                c3, c4 = st.columns(2)

                # ── Graphique 3 : Éducation prioritaire (REP / REP+) ──────────
                with c3:
                    st.markdown(
                        "##### Établissements en éducation prioritaire",
                        help="Nombre d'établissements classés en Réseau d'Éducation Prioritaire (REP) ou REP+ (renforcé) par territoire."
                    )
                    LABEL_REP = {
                        "REP":  "REP",
                        "REP+": "REP+",
                    }
                    df_rep = df_e[df_e["Appartenance_Education_Prioritaire"].isin(["REP", "REP+"])].copy()
                    df_rep["libelle_rep"] = df_rep["Appartenance_Education_Prioritaire"].map(LABEL_REP)

                    if df_rep.empty:
                        st.info("Aucun établissement en éducation prioritaire dans la sélection.")
                    else:
                        rep_agg = (
                            df_rep.groupby([geo_col, "libelle_rep"], as_index=False)
                            .size().rename(columns={"size": "nb_etab"})
                        )
                        rep_agg["text_display"] = rep_agg["nb_etab"].apply(fmt)
                        order_rep = (
                            rep_agg.groupby(geo_col)["nb_etab"]
                            .sum().sort_values(ascending=False).index.tolist()
                        )
                        y_max_rep = rep_agg.groupby(geo_col)["nb_etab"].sum().max()

                        if is_metro:
                            rep_color_map = {LABEL_REP["REP"]: "#888888", LABEL_REP["REP+"]: "#444444"}
                        else:
                            rep_color_map = {LABEL_REP["REP"]: "#52B788", LABEL_REP["REP+"]: "#1B4332"}

                        fig_rep = px.bar(
                            rep_agg, x=geo_col, y="nb_etab",
                            color="libelle_rep", barmode="stack",
                            color_discrete_map=rep_color_map,
                            text="text_display",
                            labels={geo_col: "", "nb_etab": "Établissements", "libelle_rep": "Réseau"},
                            height=400
                        )
                        fig_rep.update_traces(
                            marker_line_width=0,
                            hovertemplate="<b>%{x}</b><br>%{fullData.name} : <b>%{text}</b><extra></extra>"
                        )
                        fig_rep.update_layout(
                            yaxis=dict(range=[0, y_max_rep * 1.15]),
                            xaxis=dict(categoryorder="array", categoryarray=order_rep),
                            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02)
                        )
                        if is_metro:
                            grenoble_agglo = next((a for a in order_rep if "Grenoble" in str(a)), None)
                            if grenoble_agglo:
                                g_pos_rep = order_rep.index(grenoble_agglo)
                                fig_rep.add_vrect(x0=g_pos_rep - 0.45, x1=g_pos_rep + 0.45,
                                                  fillcolor="rgba(255,88,77,0.10)",
                                                  line_color="#FF584D", line_width=1.5, layer="below")
                        st.plotly_chart(style(fig_rep, 40), use_container_width=True)

                # ── Graphique 4 : Services spécialisés ────────────────────────
                with c4:
                    st.markdown(
                        "##### Présence de services spécialisés",
                        help="Nombre d'établissements disposant de restauration, d'hébergement ou ULIS."
                    )
                    services = {"Restauration": "Restauration", "Hebergement": "Hébergement", "ULIS": "ULIS"}
                    rows_svc = []
                    for col_svc, label_svc in services.items():
                        if col_svc in df_e.columns:
                            grp = df_e.groupby(geo_col)[col_svc].apply(
                                lambda s: int((pd.to_numeric(s, errors="coerce").fillna(0) > 0).sum())
                            ).reset_index()
                            grp.columns = [geo_col, "nb_etab"]
                            grp["Service"] = label_svc
                            rows_svc.append(grp)
                    if rows_svc:
                        svc_agg = pd.concat(rows_svc, ignore_index=True)
                        entites_avec_service = svc_agg.groupby(geo_col)["nb_etab"].sum()
                        entites_avec_service = entites_avec_service[entites_avec_service > 0].index
                        svc_agg = svc_agg[svc_agg[geo_col].isin(entites_avec_service)]
                        svc_agg["text_display"] = svc_agg["nb_etab"].apply(fmt)
                        order_svc = df_e.groupby(geo_col).size().sort_values(ascending=False).index.tolist()
                        order_svc = [e for e in order_svc if e in entites_avec_service]

                        if is_metro:
                            svc_color_map = {"Restauration": "#aaaaaa", "Hébergement": "#777777", "ULIS": "#444444"}
                        else:
                            svc_color_map = {"Restauration": "#74C69D", "Hébergement": "#2D6A4F", "ULIS": "#1B4332"}

                        fig_svc = px.bar(
                            svc_agg, x=geo_col, y="nb_etab",
                            color="Service", barmode="group",
                            color_discrete_map=svc_color_map,
                            text="text_display",
                            labels={geo_col: "", "nb_etab": "Établissements", "Service": "Service"},
                            height=400
                        )
                        fig_svc.update_traces(
                            textposition="inside",
                            hovertemplate="<b>%{x}</b><br>%{fullData.name} : <b>%{text}</b><extra></extra>"
                        )
                        fig_svc.update_layout(
                            xaxis=dict(categoryorder="array", categoryarray=order_svc),
                            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02)
                        )
                        if is_metro:
                            grenoble_agglo = next((a for a in order_svc if "Grenoble" in str(a)), None)
                            if grenoble_agglo:
                                g_pos_svc = order_svc.index(grenoble_agglo)
                                fig_svc.add_vrect(x0=g_pos_svc - 0.45, x1=g_pos_svc + 0.45,
                                                  fillcolor="rgba(255,88,77,0.10)",
                                                  line_color="#FF584D", line_width=1.5, layer="below")
                        st.plotly_chart(style(fig_svc, 40), use_container_width=True)

                st.markdown("---")
                with st.expander("Note méthodologique"):
                                    st.markdown("""
                                    - **SEP** (Section d'Enseignement Professionnel) : section rattachée à un lycée général ou technologique qui dispense une formation professionnelle, sans être un lycée professionnel à part entière.
                                    - **EREA** (Établissement Régional d'Enseignement Adapté) : établissement spécialisé accueillant des élèves en situation de handicap ou en grande difficulté scolaire et sociale, avec un accompagnement pédagogique et éducatif renforcé.
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

        with st.container():
            filter_bar("Filtres - Établissements de santé")
            fs1, fs2 = st.columns([1, 3])
            with fs1: filter_row_label("Niveau géographique")
            with fs2:
                mode_sante = st.radio("", ["Comparaison Métropoles", "Comparaison communes métropole de Grenoble"], key="sante_mode", horizontal=True, label_visibility="collapsed")
            if mode_sante == "Comparaison Métropoles":
                sel_metros_sante = st.multiselect("Métropoles à comparer", metros_sante, default=metros_sante, key="sante_metros_multi")
            else:
                communes_sante_dispo = sorted(df_sante[df_sante["metropole"] == "Grenoble"]["commune"].dropna().unique())
                sel_communes_sante = st.multiselect("Communes de Grenoble", communes_sante_dispo, default=communes_sante_dispo[:5], key="sante_communes_t1")
            sel_types_sante = st.multiselect("Type d'établissement", options=types_sante, default=types_sante, format_func=lambda t: TYPE_LABELS.get(t, t), key="sante_types_t1")
            st.markdown('</div>', unsafe_allow_html=True)

        if mode_sante == "Comparaison Métropoles":
            df_sf = df_sante[(df_sante["metropole"].isin(sel_metros_sante)) & (df_sante["type_etab"].isin(sel_types_sante))].copy()
            kpi_border_color = "#666"
        else:
            df_sf = df_sante[(df_sante["metropole"] == "Grenoble") & (df_sante["commune"].isin(sel_communes_sante)) & (df_sante["type_etab"].isin(sel_types_sante))].copy()
            kpi_border_color = "#1e5631"

        st.markdown("---")
        st.markdown(f"#### Synthèse de l'offre de soins")

        sk1, sk2, sk3, sk4, sk5 = st.columns(5)
        with sk1: st.markdown(render_solidarite_kpi("Total", fmt(len(df_sf)), "Établissements", kpi_border_color), unsafe_allow_html=True)
        with sk2: st.markdown(render_solidarite_kpi("Pharmacies", fmt(len(df_sf[df_sf["type_etab"] == "pharmacy"])), "Officines", kpi_border_color), unsafe_allow_html=True)
        with sk3: st.markdown(render_solidarite_kpi("Médecins", fmt(len(df_sf[df_sf["type_etab"] == "doctors"])), "Cabinets", kpi_border_color), unsafe_allow_html=True)
        with sk4: st.markdown(render_solidarite_kpi("Hôpitaux", fmt(len(df_sf[df_sf["type_etab"] == "hospital"])), "Centres hospitaliers", kpi_border_color), unsafe_allow_html=True)
        with sk5: st.markdown(render_solidarite_kpi("Périmètre", fmt(df_sf["commune"].nunique()), "Communes", kpi_border_color), unsafe_allow_html=True)

        st.markdown("---")

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
        elif mode_sante == "Comparaison communes métropole de Grenoble" and geojson_communes is not None and sel_communes_sante:
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
        elif mode_sante == "Comparaison communes métropole de Grenoble":
            if geojson_communes is not None:
                feats_communes = [f for f in geojson_communes["features"] if f["properties"].get("DCOE_L_LIB") in sel_communes_sante]
                if feats_communes:
                    mapbox_layers.append({"source": {"type": "FeatureCollection", "features": feats_communes}, "type": "line", "color": "#40916C", "line": {"width": 1.5}, "opacity": 0.9})
            if geojson_metros is not None:
                feats_grenoble = [f for f in geojson_metros["features"] if f["properties"].get("METROPOLE") == "Grenoble"]
                if feats_grenoble:
                    mapbox_layers.append({"source": {"type": "FeatureCollection", "features": feats_grenoble}, "type": "line", "color": "#1B4332", "line": {"width": 2.5}, "opacity": 0.6})

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
                legend=dict(title="Type", orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02, bgcolor="rgba(255,255,255,0.85)", bordercolor="#C8E6D4", borderwidth=1, font=dict(size=11)),
                margin=dict(l=0, r=0, t=0, b=0),
                paper_bgcolor="rgba(0,0,0,0)",
                font_family="Sora"
            )
            st.plotly_chart(fig_map, use_container_width=True)

        st.markdown("---")
        extra1, extra2 = st.columns(2)

        with extra1:
            if mode_sante == "Comparaison Métropoles":
                st.markdown("##### Offre de soins par métropole et type d'établissement", help="Nombre absolu d'établissements identifiés par type de soin.")
                df_pivot = df_sf.groupby(["metropole", "type_etab"]).size().reset_index(name="count")
                df_pivot["label"] = df_pivot["type_etab"].map(lambda t: TYPE_LABELS.get(t, t))
                df_pivot["text_display"] = df_pivot["count"].apply(lambda x: fmt(x))
                y_max_stack = df_pivot.groupby("metropole")["count"].sum().max()
                order_stack = df_pivot.groupby("metropole")["count"].sum().sort_values(ascending=False).index.tolist()
                fig_stack = px.bar(df_pivot, x="metropole", y="count", color="type_etab", color_discrete_map=TYPE_COLORS, text="text_display", labels={"metropole": "Métropole", "count": "Nombre", "type_etab": "Type"}, height=380, barmode="stack")
                fig_stack.update_traces(
                    textposition="inside",
                    textfont_size=10,
                    hovertemplate="<b>%{x}</b><br>%{fullData.name} : <b>%{text}</b><extra></extra>"
                )
                for trace in fig_stack.data: trace.name = TYPE_LABELS.get(trace.name, trace.name)
                if "Grenoble" in order_stack:
                    g_pos_sante = order_stack.index("Grenoble")
                    fig_stack.add_vrect(x0=g_pos_sante - 0.45, x1=g_pos_sante + 0.45,
                                       fillcolor="rgba(255,88,77,0.10)",
                                       line_color="#FF584D", line_width=1.5, layer="below")
                fig_stack.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_family="Sora",
                    yaxis=dict(range=[0, y_max_stack * 1.1]),
                    xaxis=dict(tickangle=-30, categoryorder="array", categoryarray=order_stack),
                    legend=dict(title="Type", orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02, font=dict(size=10))
                )
                st.plotly_chart(style(fig_stack, 40), use_container_width=True)
            else:
                st.markdown("##### Densité par commune", help="Nombre absolu d'établissements identifiés par commune.")
                df_comm = df_sf.groupby(["commune", "type_etab"]).size().reset_index(name="count")
                df_comm["label"] = df_comm["type_etab"].map(lambda t: TYPE_LABELS.get(t, t))
                df_comm["text_display"] = df_comm["count"].apply(lambda x: fmt(x))
                y_max_comm = df_comm.groupby("commune")["count"].sum().max()
                order_comm = df_comm.groupby("commune")["count"].sum().sort_values(ascending=False).index.tolist()
                fig_comm = px.bar(df_comm, x="commune", y="count", color="type_etab", color_discrete_map=TYPE_COLORS, text="text_display", labels={"commune": "Commune", "count": "Nombre", "type_etab": "Type"}, height=380, barmode="stack")
                fig_comm.update_traces(
                    textposition="inside",
                    textfont_size=10,
                    hovertemplate="<b>%{x}</b><br>%{fullData.name} : <b>%{text}</b><extra></extra>"
                )
                for trace in fig_comm.data: trace.name = TYPE_LABELS.get(trace.name, trace.name)
                fig_comm.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_family="Sora",
                    yaxis=dict(range=[0, y_max_comm * 1.1]),
                    xaxis=dict(tickangle=-30, categoryorder="array", categoryarray=order_comm),
                    legend=dict(title="Type", orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02, font=dict(size=10))
                )
                st.plotly_chart(style(fig_comm, 40), use_container_width=True)

        with extra2:
            st.markdown("##### Part de chaque type d'établissement", help="Répartition relative de l'offre de soins sur les territoires sélectionnés.")
            pie_data = df_sf.groupby("type_etab").size().reset_index(name="count")
            pie_data["label"] = pie_data["type_etab"].map(lambda t: TYPE_LABELS.get(t, t))
            fig_pie = px.pie(pie_data, names="label", values="count", color="type_etab", color_discrete_map=TYPE_COLORS, height=380, hole=0.4)
            fig_pie.update_traces(
                textposition="inside",
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
                df_muni_2020 = pd.read_csv("solidarite&citoyennete/data_clean/participation_citoyenne/elections_2014_2020.csv")
                df_muni_2020 = df_muni_2020[df_muni_2020["Année"] == 2020].copy()
                df_muni_2020["Type d'élection"] = "Municipales"
                df_muni_2026 = pd.read_csv("solidarite&citoyennete/data_clean/participation_citoyenne/municipales_2026.csv")
                df_muni_2026["Type d'élection"] = "Municipales"
                df_muni_2026["Libellé de la commune"] = df_muni_2026["Libellé de la commune"].replace("Oissel-sur-Seine", "Oissel")
                df_p17 = pd.read_csv("solidarite&citoyennete/data_clean/participation_citoyenne/presidentielle_2017.csv")
                df_p17["Type d'élection"] = "Présidentielles"
                df_p22 = pd.read_csv("solidarite&citoyennete/data_clean/participation_citoyenne/presidentielle_2022.csv")
                df_p22["Type d'élection"] = "Présidentielles"
                return pd.concat([df_muni_2014, df_muni_2020, df_muni_2026, df_p17, df_p22], ignore_index=True)

            df_elec = charger_elections()
            DEP_METRO_ELEC = {"Isère": "Grenoble", "Ille-et-Vilaine": "Rennes", "Seine-Maritime": "Rouen", "Loire": "Saint-Étienne", "Hérault": "Montpellier"}
            df_elec["metropole"] = df_elec["Libellé du département"].map(DEP_METRO_ELEC)
            df_elec["% Participation"] = 100 - df_elec["% Abs/Ins"]

            tours_elec  = sorted(df_elec["Numéro de tour"].dropna().unique().astype(int))
            metros_elec = sorted(df_elec["metropole"].dropna().unique())

            st.markdown("""
                        <div style='background-color: #f1f8f5; padding: 15px; border-radius: 10px; border-left: 5px solid #1C3A27; margin-bottom: 20px;'>
                        <strong>Note sur les données :</strong> Les élections municipales de 2020 se sont tenues en pleine crise sanitaire COVID-19,
                        ce qui a fortement impacté la participation. Les taux de participation sont donc exceptionnellement bas
                        et ne reflètent pas le comportement électoral habituel de ces territoires. 
                        </div>""", unsafe_allow_html=True)
            
            with st.container():
                filter_bar("Filtres - Participation citoyenne")
                ft1, ft2 = st.columns([1, 3])
                with ft1: filter_row_label("Type d'élection")
                with ft2: type_election = st.radio("", ["Municipales", "Présidentielles"], key="part_type_election", horizontal=True, label_visibility="collapsed")
                df_elec_type = df_elec[df_elec["Type d'élection"] == type_election]
                annees_elec = sorted(df_elec_type["Année"].dropna().unique().astype(int))
                fp1, fp2 = st.columns([1, 3])
                with fp1: filter_row_label("Niveau géographique")
                with fp2: mode_part = st.radio("", ["Comparaison Métropoles", "Comparaison communes métropole de Grenoble"], key="part_mode", horizontal=True, label_visibility="collapsed")
                if mode_part == "Comparaison communes métropole de Grenoble":
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
                    _part_seq = px.colors.sequential.Greens_r if mode_part == "Comparaison communes métropole de Grenoble" else None
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
                    order_qual = df_agg.sort_values("% Exprimés", ascending=False)["metropole"].tolist()
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
                    if mode_part == "Comparaison Métropoles" and "Grenoble" in order_qual:
                        g_pos_qual = order_qual.index("Grenoble")
                        fig_qual.add_vrect(x0=g_pos_qual - 0.45, x1=g_pos_qual + 0.45,
                                        fillcolor="rgba(255,88,77,0.10)",
                                        line_color="#FF584D", line_width=1.5, layer="below")
                    fig_qual.update_layout(
                        yaxis_range=[0, 100],
                        xaxis=dict(categoryorder="array", categoryarray=order_qual),
                        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02),
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        font_family="Sora", yaxis=dict(gridcolor="#E8F5EE"),
                        margin=dict(l=10, r=10, t=40, b=10)
                    )
                    st.plotly_chart(style(fig_qual, 40), use_container_width=True)

                st.markdown("---")

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
                    if mode_part == "Comparaison Métropoles":
                        entites_delta = df_delta["entite"].tolist()
                        if "Grenoble" in entites_delta:
                            g_pos_delta = entites_delta.index("Grenoble")
                            fig_delta.add_hrect(y0=g_pos_delta - 0.45, y1=g_pos_delta + 0.45,
                                                fillcolor="rgba(255,88,77,0.10)",
                                                line_color="#FF584D", line_width=1.5, layer="below")
                    fig_delta.update_layout(
                        showlegend=False,
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        font_family="Sora", xaxis=dict(gridcolor="#E8F5EE"),
                        margin=dict(l=10, r=60, t=40, b=10)
                    )
                    st.plotly_chart(style(fig_delta), use_container_width=True)
                else:
                    st.info("Données insuffisantes pour calculer la variation.")