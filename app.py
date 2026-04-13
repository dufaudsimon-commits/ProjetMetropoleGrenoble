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
# 5. EN-TÊTE + NAVIGATION (sidebar minimale : navigation seule)
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(
    "<h1 style='color:#1C3A27;font-size:2rem;margin-bottom:2px'>📊 Tableau de bord démographique</h1>"
    "<p style='color:#5A8A6A;margin-bottom:20px'>Analyse comparative · 5 métropoles françaises · Données INSEE RP 2011–2022</p>",
    unsafe_allow_html=True,
)

if st.session_state.page == "home":
    st.title("Projet Métropoles — Accueil")
    c1, c2 = st.columns([1.2, 0.8])
    with c1:
        st.markdown("""
### Objectif
Comparer les dynamiques territoriales des 5 métropoles à partir des données de **démographie** et de **solidarité & citoyenneté**.

### Contenu
- Démographie : population, âge, mobilités, ménages
- Solidarité & citoyenneté : CAF, éducation, santé, participation citoyenne
        """.strip())
        if st.button("Aller à l'application", type="primary"):
            st.session_state.page = "app"
            st.rerun()
    with c2:
        img = Path("assets/accueil.png")
        if img.exists():
            st.image(str(img), use_container_width=True)
        else:
            st.info("Image optionnelle : ajoute `assets/accueil.png`.")
    st.stop()

# Sidebar : navigation uniquement
with st.sidebar:
    if st.button("🏠 Accueil"):
        st.session_state.page = "home"
        st.rerun()
    st.markdown("---")
    vue = st.radio("Navigation", ["Description", "Démographie", "Solidarité et citoyenneté"],
                   index=0, label_visibility="collapsed")

# ──────────────────────────────────────────────────────────────────────────────
# 6. PAGES
# ──────────────────────────────────────────────────────────────────────────────
if vue == "Description":
    st.markdown('<p class="section-header">Description</p>', unsafe_allow_html=True)

    st.markdown("""
    Cette application présente des analyses comparatives sur 5 métropoles françaises soit:
    Grenoble, Rennes, Rouen, Saint-Étienne et Montpellier.

    Chaque page dispose de ses propres filtres en haut de page, adaptés aux données présentées.
    Selon les onglets, il est possible de filtrer par métropole, par année ou par thématique.
    """)

    st.markdown("---")

    st.markdown("### 🏙️ Volet 1 — Démographie")
    st.markdown("""
    Accessible via le menu de gauche → Bouton **Démographie**. Ce volet contient 5 onglets :

    - **🏙️ Population globale** — Évolution et comparaison des populations totales entre métropoles.
    - **👥 Structure par âge** — Pyramides des âges, part des jeunes, actifs et seniors.
    - **🚌 Mobilités** — Flux résidentiels, professionnels et scolaires.
    - **🏠 Ménages** — Taille et composition des ménages selon l'âge et la CSP.
    - **📊 CSP comparatif** — Structure socioprofessionnelle et indice de spécialisation.
    """)

    st.markdown("---")

    st.markdown("### 🤝 Volet 2 — Solidarité & citoyenneté")
    st.markdown("""
    Accessible via le menu de gauche → Bouton **Solidarité et citoyenneté**. Ce volet contient 5 onglets :

    - **🤝 Solidarité** — Analyse des données CAF (foyers bénéficiaires, montants versés, évolution).
    - **🎓 Éducation** — *(à venir)*
    - **🏥 Santé** — *(à venir)*
    - **🗳️ Participation citoyenne** — *(à venir)*
    - **🗄️ Base de données** — *(à venir)*
    """)

    st.markdown("---")

    st.markdown("""
    <p class="source-note">Sources : INSEE — Recensements de la Population 2011, 2016, 2022 ·
    Mobilités résidentielles, professionnelles et scolaires 2019–2022 · CAF — 5 métropoles</p>
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
            'INSEE — Données générales comparatives & Population par tranche d\'âge (RP 2011–2022)</a></p>',
            unsafe_allow_html=True,
        )

        # ── Bandeau filtres ──────────────────────────────────────────────────
        with st.container():
            st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
            filter_bar("🔧 Filtres — Population globale")
            sel = st.multiselect(
                "Métropoles à comparer", TOUTES, default=TOUTES, key="sel_t1",
                label_visibility="collapsed",
            )
            st.markdown('</div>', unsafe_allow_html=True)

        if not sel:
            st.warning("Sélectionnez au moins une métropole.")
            st.stop()

        st.markdown(
            "<h2 style='color:#1C3A27;font-size:1.4rem;margin:0 0 4px'>🏙️ Population globale</h2>"
            "<p style='color:#5A8A6A;font-size:0.82rem;margin-bottom:18px'>"
            "Vue d'ensemble comparative des 5 métropoles — Recensements INSEE RP 2011 · 2016 · 2022</p>",
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
                    data_dens.append({"Métropole": m, "Densité (hab/km²)": d, "Superficie (km²)": s, "Population": p})
            df_dens = pd.DataFrame(data_dens)
            if not df_dens.empty:
                fig_dens = px.scatter(df_dens, x="Superficie (km²)", y="Densité (hab/km²)",
                                      size="Population", color="Métropole",
                                      color_discrete_map=COULEURS, text="Métropole", size_max=55, height=370)
                fig_dens.update_traces(textposition="top center", textfont_size=11)
                fig_dens.update_layout(showlegend=False)
                st.plotly_chart(style(fig_dens), use_container_width=True)

        st.markdown("---")
        st.markdown("#### 📈 Évolution de la population 2011 → 2022")
        r2c1, r2c2 = st.columns([3, 2])
        with r2c1:
            st.markdown("##### Trajectoire démographique")
            if df_pop is not None:
                rows_evol = []
                for m in sel:
                    for an in [2011, 2016, 2022]:
                        p = pop_from_age(m, an)
                        if not np.isnan(p):
                            rows_evol.append({"Métropole": m, "Année": an, "Population": p})
                df_evol = pd.DataFrame(rows_evol)
                if not df_evol.empty:
                    base = df_evol[df_evol["Année"] == 2011].set_index("Métropole")["Population"]
                    df_evol["Indice"] = df_evol.apply(
                        lambda r: r["Population"] / base.get(r["Métropole"], np.nan) * 100, axis=1)
                    fig_evol = go.Figure()
                    for m in sel:
                        sub_e = df_evol[df_evol["Métropole"] == m].sort_values("Année")
                        fig_evol.add_trace(go.Scatter(
                            x=sub_e["Année"], y=sub_e["Indice"], name=m, mode="lines+markers",
                            line=dict(color=COULEURS.get(m, "#888"), width=2.5), marker=dict(size=9),
                            customdata=sub_e["Population"],
                        ))
                    fig_evol.add_hline(y=100, line_dash="dot", line_color="#AAAAAA",
                                       annotation_text="Base 2011", annotation_position="left")
                    fig_evol.update_layout(yaxis_title="Indice (base 100 = 2011)",
                                           xaxis=dict(tickvals=[2011, 2016, 2022]),
                                           legend=dict(orientation="h", y=1.12), height=370)
                    st.plotly_chart(style(fig_evol), use_container_width=True)
            else:
                st.info("Fichier Population_tranche_age_clean.csv non chargé.")
        with r2c2:
            st.markdown("##### Croissance 2011→2022 (gain net)")
            rows_gain = []
            for m in sel:
                p11 = pop_from_age(m, 2011)
                p22 = pop_from_age(m, 2022)
                if not (np.isnan(p11) or np.isnan(p22)):
                    rows_gain.append({"Métropole": m, "Gain net": p22 - p11,
                                      "Croissance (%)": (p22 - p11) / p11 * 100})
            df_gain = pd.DataFrame(rows_gain).sort_values("Gain net", ascending=True)
            if not df_gain.empty:
                colors_gain = ["#2D6A4F" if v >= 0 else "#C45B2A" for v in df_gain["Gain net"]]
                fig_gain = go.Figure(go.Bar(
                    x=df_gain["Gain net"], y=df_gain["Métropole"], orientation="h",
                    marker_color=colors_gain,
                    text=[f"{int(g):+,} ({c:+.1f}%)".replace(",", "\u202f")
                          for g, c in zip(df_gain["Gain net"], df_gain["Croissance (%)"])],
                    textposition="outside",
                ))
                fig_gain.add_vline(x=0, line_dash="dot", line_color="#999")
                fig_gain.update_layout(xaxis_title="Habitants gagnés (2011→2022)",
                                       showlegend=False, height=370)
                st.plotly_chart(style(fig_gain), use_container_width=True)

        st.markdown("---")
        st.markdown("#### ⚖️ Composantes de la variation démographique")
        r3c1, r3c2 = st.columns(2)
        with r3c1:
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
                COLOR_COMP = {"Solde naturel": "#74C69D", "Solde migratoire": "#1A6FA3", "Variation totale": "#2D6A4F"}
                fig_comp = px.bar(df_comp, x="Métropole", y="Taux (%/an)", color="Composante",
                                  barmode="group", color_discrete_map=COLOR_COMP, height=360)
                fig_comp.add_hline(y=0, line_dash="dot", line_color="#AAAAAA")
                fig_comp.update_layout(legend=dict(orientation="h", y=1.12))
                st.plotly_chart(style(fig_comp), use_container_width=True)
        with r3c2:
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
        st.markdown("#### 💶 Revenus, pauvreté & logement")
        r4c1, r4c2, r4c3 = st.columns(3)
        with r4c1:
            st.markdown("##### Revenu médian 2021 (€/an)")
            data_rev = [{"Métropole": m, "Revenu médian (€)": epci_val(m, "revenu_median_2021")} for m in sel]
            df_rev = pd.DataFrame(data_rev).dropna().sort_values("Revenu médian (€)")
            if not df_rev.empty:
                fig_rev = px.bar(df_rev, x="Revenu médian (€)", y="Métropole", orientation="h",
                                 color="Métropole", color_discrete_map=COULEURS, text_auto=".0f", height=300)
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
                    textposition="outside",
                ))
                fig_pauv.update_layout(xaxis_title="%", showlegend=False, height=300)
                st.plotly_chart(style(fig_pauv), use_container_width=True)
        with r4c3:
            st.markdown("##### Logements : vacance & propriétaires (%)")
            rows_log = []
            for m in sel:
                vac  = epci_val(m, "part_logements_vacants")
                prop = epci_val(m, "part_proprietaires")
                rp   = epci_val(m, "part_res_principales")
                if not all(np.isnan(v) for v in [vac, prop]):
                    rows_log.append({"Métropole": m, "Logements vacants (%)": vac,
                                     "Propriétaires (%)": prop, "Rés. principales (%)": rp})
            df_log = pd.DataFrame(rows_log)
            if not df_log.empty:
                df_log_m = df_log.melt(id_vars="Métropole", var_name="Indicateur", value_name="Part (%)").dropna()
                fig_log = px.bar(df_log_m, x="Métropole", y="Part (%)", color="Indicateur",
                                 barmode="group", height=300,
                                 color_discrete_sequence=["#C45B2A", "#2D6A4F", "#1A6FA3"])
                fig_log.update_layout(legend=dict(orientation="h", y=1.15, font_size=10))
                st.plotly_chart(style(fig_log), use_container_width=True)

        st.markdown("---")
        st.markdown("#### 📋 Tableau récapitulatif — indicateurs clés")
        lignes_tab = []
        for m in sel:
            tx_v  = epci_val(m, "tx_var_population_2016_2022")
            tc    = epci_val(m, "tx_chomage_15_64")
            rev   = epci_val(m, "revenu_median_2021")
            pauv  = epci_val(m, "tx_pauvrete_2021")
            dens  = epci_val(m, "densite_2022")
            p11   = pop_from_age(m, 2011)
            p22_t = pop_from_age(m, 2022)
            croiss = f"+{(p22_t-p11)/p11*100:.1f}%" if not (np.isnan(p11) or np.isnan(p22_t)) else "N/D"
            lignes_tab.append({
                "Métropole": m,
                "Population 2022": fmt(epci_val(m, "population_2022")),
                "Densité (hab/km²)": fmt(dens),
                "Croissance 2011–22": croiss,
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
        st.caption("Sources : INSEE — Données générales comparatives (RP 2022) & Population par tranche d'âge (RP 2011–2022).")

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
                f1, f2, f3 = st.columns(3)
                with f1:
                    metro_age = st.selectbox("Métropole", TOUTES, key="metro_age")
                with f2:
                    annee_age = st.selectbox("Année", annees, index=len(annees)-1, key="an_age")
                with f3:
                    mode_cc = st.checkbox("Comparer deux communes", key="cc_age")
                if mode_cc:
                    cmns = sorted(COMMUNES.get(metro_age, []))
                    fcc1, fcc2 = st.columns(2)
                    with fcc1:
                        comm_a = st.selectbox("Commune A", cmns, key="ca")
                    with fcc2:
                        comm_b = st.selectbox("Commune B", cmns, index=min(1, len(cmns)-1), key="cb")
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("---")

            df_m = df_pop[(df_pop["metropole"] == metro_age) & (df_pop["annee"] == annee_age)]
            if not mode_cc:
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
            else:
                st.markdown(f"##### {comm_a} vs {comm_b} ({annee_age})")
                df_ca = df_pop[(df_pop["LIBELLE"] == comm_a) & (df_pop["annee"] == annee_age)]
                df_cb = df_pop[(df_pop["LIBELLE"] == comm_b) & (df_pop["annee"] == annee_age)]
                if not df_ca.empty and not df_cb.empty and ch and cf:
                    rows_c = [{"Tranche": label_col(h),
                               comm_a: df_ca[h].sum() + df_ca[f].sum(),
                               comm_b: df_cb[h].sum() + df_cb[f].sum()}
                              for h, f in zip(ch, cf)]
                    df_cc = pd.melt(pd.DataFrame(rows_c), id_vars="Tranche",
                                    var_name="Commune", value_name="Population")
                    fig_cc = px.bar(df_cc, x="Tranche", y="Population", color="Commune",
                                    barmode="group", color_discrete_sequence=["#2D6A4F", "#95D5B2"])
                    fig_cc.update_layout(xaxis_tickangle=-40, legend=dict(orientation="h", y=1.08))
                    st.plotly_chart(style(fig_cc), use_container_width=True)
                else:
                    st.info("Données insuffisantes pour ces communes.")

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
                        metro_men = st.selectbox("Métropole", TOUTES, key="m_men")
                    with fm2:
                        mode_cc_men = st.checkbox("Comparer deux communes", key="cc_men")
                    if mode_cc_men:
                        cmns_men = sorted(COMMUNES.get(metro_men, []))
                        fcc1, fcc2 = st.columns(2)
                        with fcc1:
                            comm_ma = st.selectbox("Commune A", cmns_men, key="cma")
                        with fcc2:
                            comm_mb = st.selectbox("Commune B", cmns_men, index=min(1, len(cmns_men)-1), key="cmb")
                    st.markdown('</div>', unsafe_allow_html=True)

                st.markdown("---")

                df_men_m = df_men_age[df_men_age["metropole"] == metro_men]
                cols_m = [c for c in df_men_age.columns if c.startswith("Menages_")]
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
                    "40–54 ans": "40_54ans", "55–64 ans": "55_64ans", "65–79 ans": "65_79ans", "80 ans +": "plus80ans",
                }

                if not mode_cc_men:
                    totaux = {lbl: df_men_m[[c for c in cols if c in df_men_m.columns]].sum().sum()
                              for lbl, cols in TYPE_GROUPES.items()}
                    df_t = pd.DataFrame(list(totaux.items()), columns=["Type", "Ménages"])
                    df_t = df_t[df_t["Ménages"] > 0].sort_values("Ménages", ascending=False)
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"##### Types de ménages — {metro_men}")
                        fig_t = px.bar(df_t, x="Ménages", y="Type", orientation="h",
                                       color_discrete_sequence=[COULEURS[metro_men]], text_auto=".0f")
                        fig_t.update_layout(yaxis={"autorange": "reversed"}, yaxis_title="", xaxis_title="Ménages")
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
                    st.markdown(f"##### {comm_ma} vs {comm_mb}")
                    rows_cc = []
                    for comm in [comm_ma, comm_mb]:
                        df_cc = df_men_age[df_men_age["LIBGEO"] == comm]
                        for lbl, cols in TYPE_GROUPES.items():
                            valid = [c for c in cols if c in df_cc.columns]
                            rows_cc.append({"Commune": comm, "Type": lbl,
                                            "Ménages": df_cc[valid].sum().sum() if valid else 0})
                    df_ccp = pd.DataFrame(rows_cc)
                    if df_ccp["Ménages"].sum() > 0:
                        fig_ccp = px.bar(df_ccp, x="Type", y="Ménages", color="Commune",
                                         barmode="group", color_discrete_sequence=["#2D6A4F", "#95D5B2"])
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
    s1, s2, s3, s4, s5 = st.tabs(["Solidarité", "Éducation", "Santé", "Participation citoyenne", "data_base"])

    # ──────────────────────────────────────────────────────────────────────────
    # ONGLET SOLIDARITÉ — CAF
    # ──────────────────────────────────────────────────────────────────────────
    with s1:
        st.markdown('<p class="section-header">🤝 Solidarité — Données CAF</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="source-note">Source : <a href="https://data.caf.fr" target="_blank">'
            'Caisse d\'Allocations Familiales — CAF 5 Métropoles 2020–2023</a></p>',
            unsafe_allow_html=True,
        )
        if df_caf is None or df_caf.empty:
            st.info("📂 Fichier `CAF_5_Metropoles.csv` introuvable.")
        else:
            required_cols = {"Annee", "Agglomeration"}
            if not required_cols.issubset(set(df_caf.columns)):
                st.error("Le fichier CAF doit contenir au minimum les colonnes `Annee` et `Agglomeration`.")
            else:
                # Colonnes numériques disponibles
                ALL_METRIC_LABELS = {
                    "Nombre foyers NDUR":       "Foyers — Toutes aides (NDUR)",
                    "Nombre personnes NDUR":    "Personnes — Toutes aides (NDUR)",
                    "Montant total NDUR":       "Montant total (€) — Toutes aides",
                    "Nombre foyers NDURPAJE":   "Foyers — PAJE",
                    "Nombre personnes NDURPAJE":"Personnes — PAJE",
                    "Montant total NDURPAJE":   "Montant (€) — PAJE",
                    "Nombre foyers NDUREJ":     "Foyers — Aide jeunes enfants",
                    "Nombre personnes NDUREJ":  "Personnes — Aide jeunes enfants",
                    "Montant total NDUREJ":     "Montant (€) — Aide jeunes enfants",
                    "Nombre foyers NDURAL":     "Foyers — Allocation logement",
                    "Nombre personnes NDURAL":  "Personnes — Allocation logement",
                    "Montant total NDURAL":     "Montant (€) — Allocation logement",
                    "Nombre foyers NDURINS":    "Foyers — Insertion sociale",
                    "Nombre personnes NDURINS": "Personnes — Insertion sociale",
                    "Montant total NDURINS":    "Montant (€) — Insertion sociale",
                }
                available_metrics = {k: v for k, v in ALL_METRIC_LABELS.items() if k in df_caf.columns}

                if not available_metrics:
                    st.warning("Aucune mesure CAF standard trouvée dans le fichier.")
                else:
                    # ── Conversion numérique globale ──────────────────────────
                    for col in available_metrics:
                        df_caf[col] = pd.to_numeric(df_caf[col], errors="coerce").fillna(0)

                    years_caf  = sorted(df_caf["Annee"].dropna().unique())
                    agglos_caf = sorted(df_caf["Agglomeration"].dropna().unique())

                    # ── Bandeau filtres ───────────────────────────────────────
                    with st.container():
                        st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
                        filter_bar("🔧 Filtres — Solidarité CAF")
                        caf_f1, caf_f2, caf_f3 = st.columns([2, 1, 2])
                        with caf_f1:
                            metric_key = st.selectbox(
                                "Indicateur",
                                list(available_metrics.keys()),
                                format_func=lambda k: available_metrics[k],
                                index=0,
                                key="caf_metric",
                            )
                        with caf_f2:
                            year_caf = st.selectbox("Année", years_caf, index=len(years_caf) - 1, key="caf_year")
                        with caf_f3:
                            sel_agglos_caf = st.multiselect(
                                "Agglomérations", agglos_caf, default=agglos_caf, key="caf_agglos"
                            )
                        st.markdown('</div>', unsafe_allow_html=True)

                    if not sel_agglos_caf:
                        st.warning("⚠️ Sélectionnez au moins une agglomération.")
                    else:
                        metric = metric_key
                        label_metric = available_metrics[metric]
                        df_fil = df_caf[df_caf["Agglomeration"].isin(sel_agglos_caf)]
                        df_yr  = df_fil[df_fil["Annee"] == year_caf]

                        st.markdown("---")

                        # ── KPI ───────────────────────────────────────────────
                        total_val    = df_yr[metric].sum()
                        nb_communes  = int(df_yr["Nom_Commune"].nunique()) if "Nom_Commune" in df_yr.columns else 0
                        nb_agglos    = int(df_yr["Agglomeration"].nunique())
                        max_agglo    = df_yr.groupby("Agglomeration")[metric].sum().idxmax() if not df_yr.empty else "—"

                        k1, k2, k3, k4 = st.columns(4)
                        k1.metric(f"Total {year_caf}", fmt(total_val))
                        k2.metric("Agglomérations", nb_agglos)
                        k3.metric("Communes couvertes", nb_communes)
                        k4.metric("1ère agglomération", max_agglo)

                        st.markdown("---")

                        # ── Ligne 1 : Bar comparatif + Évolution temporelle ───
                        c1, c2 = st.columns(2)
                        with c1:
                            st.markdown(f"##### 📊 Comparatif {year_caf}")
                            by_agg = (df_yr.groupby("Agglomeration", as_index=False)[metric]
                                      .sum().sort_values(metric, ascending=False))
                            fig_bar = px.bar(
                                by_agg, x="Agglomeration", y=metric,
                                color="Agglomeration",
                                color_discrete_map=COULEURS,
                                labels={"Agglomeration": "", metric: label_metric},
                                text_auto=".3s",
                                title=f"{label_metric} — {year_caf}",
                                height=380,
                            )
                            fig_bar.update_traces(textposition="outside")
                            fig_bar.update_layout(showlegend=False)
                            st.plotly_chart(style(fig_bar, 40), use_container_width=True)

                        with c2:
                            st.markdown("##### 📈 Évolution 2020–2023")
                            evo = (df_fil.groupby(["Annee", "Agglomeration"], as_index=False)[metric]
                                   .sum().sort_values("Annee"))
                            fig_evo = px.line(
                                evo, x="Annee", y=metric, color="Agglomeration",
                                color_discrete_map=COULEURS,
                                markers=True,
                                labels={"Annee": "Année", metric: label_metric},
                                title=f"Évolution — {label_metric}",
                                height=380,
                            )
                            fig_evo.update_traces(line_width=2.5, marker_size=8)
                            st.plotly_chart(style(fig_evo, 40), use_container_width=True)

                        st.markdown("---")

                        # ── Ligne 2 : Quotient familial + Heatmap communes ────
                        c3, c4 = st.columns(2)
                        with c3:
                            st.markdown(f"##### 👨‍👩‍👧 Répartition par quotient familial ({year_caf})")
                            if "Quotient familial" in df_yr.columns:
                                qf_order = [
                                    "Moins de 400 euros", "Entre 400 et 799 euros",
                                    "Entre 800 et 1199 euros", "Entre 1200 et 1599 euros",
                                    "Entre 1600 et 1999 euros", "Entre 2000 et 3999 euros",
                                    "4000 euros ou plus", "Inconnu",
                                ]
                                qf_data = (df_yr.groupby(["Agglomeration", "Quotient familial"], as_index=False)[metric]
                                           .sum())
                                qf_data["QF_ord"] = pd.Categorical(qf_data["Quotient familial"],
                                                                    categories=qf_order, ordered=True)
                                qf_data = qf_data.sort_values("QF_ord")
                                fig_qf = px.bar(
                                    qf_data, x="Agglomeration", y=metric, color="Quotient familial",
                                    barmode="stack",
                                    labels={"Agglomeration": "", metric: label_metric},
                                    title="Composition par quotient familial",
                                    height=380,
                                )
                                st.plotly_chart(style(fig_qf, 40), use_container_width=True)
                            else:
                                st.info("Colonne `Quotient familial` absente.")

                        with c4:
                            st.markdown(f"##### 🏆 Top 15 communes — {year_caf}")
                            if "Nom_Commune" in df_yr.columns:
                                top15 = (df_yr.groupby(["Nom_Commune", "Agglomeration"], as_index=False)[metric]
                                         .sum().nlargest(15, metric))
                                fig_top = px.bar(
                                    top15, x=metric, y="Nom_Commune",
                                    orientation="h",
                                    color="Agglomeration",
                                    color_discrete_map=COULEURS,
                                    labels={"Nom_Commune": "", metric: label_metric},
                                    text_auto=".3s",
                                    title=f"Top 15 communes — {label_metric}",
                                    height=420,
                                )
                                fig_top.update_layout(yaxis={"categoryorder": "total ascending"})
                                st.plotly_chart(style(fig_top, 40), use_container_width=True)

                        st.markdown("---")

                        # ── Radar multi-aides ─────────────────────────────────
                        st.markdown("##### 🕸️ Profil comparatif des aides — radar")
                        aides_foyers = {
                            "Foyers PAJE": "Nombre foyers NDURPAJE",
                            "Foyers aj. enf.": "Nombre foyers NDUREJ",
                            "Foyers alloc. log.": "Nombre foyers NDURAL",
                            "Foyers insertion": "Nombre foyers NDURINS",
                            "Foyers total": "Nombre foyers NDUR",
                        }
                        aides_dispo = {k: v for k, v in aides_foyers.items() if v in df_yr.columns}
                        if len(aides_dispo) >= 3:
                            radar_data = (df_yr.groupby("Agglomeration")[list(aides_dispo.values())]
                                          .sum().reset_index())
                            radar_data.columns = ["Agglomeration"] + list(aides_dispo.keys())
                            fig_radar = go.Figure()
                            categories_r = list(aides_dispo.keys())
                            for _, row_r in radar_data.iterrows():
                                vals = [row_r[c] for c in categories_r] + [row_r[categories_r[0]]]
                                fig_radar.add_trace(go.Scatterpolar(
                                    r=vals,
                                    theta=categories_r + [categories_r[0]],
                                    fill="toself",
                                    name=row_r["Agglomeration"],
                                    line_color=COULEURS.get(row_r["Agglomeration"], "#999"),
                                ))
                            fig_radar.update_layout(
                                polar=dict(radialaxis=dict(visible=True)),
                                height=420,
                                title=f"Profil des aides par agglomération — {year_caf}",
                                font_family="Sora",
                                paper_bgcolor="rgba(0,0,0,0)",
                            )
                            st.plotly_chart(fig_radar, use_container_width=True)

                        st.markdown("---")
                        with st.expander("📄 Voir les données détaillées"):
                            st.dataframe(
                                df_yr.groupby(["Agglomeration", "Quotient familial"] if "Quotient familial" in df_yr.columns else ["Agglomeration"],
                                              as_index=False)[list(available_metrics.keys())].sum(),
                                use_container_width=True,
                            )
                        with st.expander("📖 Note méthodologique"):
                            st.write(
                                "**Sources** : Caisse d'Allocations Familiales (CAF) — données communales 2020–2023.\n\n"
                                "**NDUR** : Nombre de dossiers unifiés réels (ensemble des allocataires actifs).\n\n"
                                "**NDURPAJE** : Prestation d'accueil du jeune enfant.\n\n"
                                "**NDUREJ** : Allocation au jeune enfant.\n\n"
                                "**NDURAL** : Aide personnalisée au logement + allocation logement.\n\n"
                                "**NDURINS** : Minima sociaux et insertion sociale (RSA, etc.).\n\n"
                                "Les montants sont en euros."
                            )

    # ──────────────────────────────────────────────────────────────────────────
    # ONGLET ÉDUCATION — Effectifs étudiants
    # ──────────────────────────────────────────────────────────────────────────
    with s2:
        st.markdown('<p class="section-header">🎓 Éducation — Effectifs dans l\'enseignement supérieur</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="source-note">Source : <a href="https://data.enseignementsup-recherche.gouv.fr" target="_blank">'
            'MESRI — Effectifs dans l\'enseignement supérieur · Communes des 5 métropoles</a></p>',
            unsafe_allow_html=True,
        )

        if df_eff is None or df_eff.empty:
            st.info("📂 Fichier `effectifs_5_villes.csv` introuvable.")
        else:
            df_eff_w = df_eff.copy()

            # ── Listes de valeurs disponibles ────────────────────────────────
            annees_eff   = sorted(df_eff_w["annee"].dropna().unique().astype(int))
            metros_eff   = sorted(df_eff_w["metropole"].dropna().unique())

            LABEL_REGROUPEMENT = {
                "TOTAL":     "Tous types confondus",
                "UNIV":      "Universités",
                "STS":       "STS & assimilés",
                "CPGE":      "CPGE",
                "GE":        "Grandes Écoles",
                "ING_autres":"Écoles d'ingénieurs",
                "EC_COM":    "Écoles de commerce",
                "EC_ART":    "Écoles d'art",
                "EC_JUR":    "Écoles juridiques",
                "EC_PARAM":  "Écoles paramédicales",
                "EC_autres": "Autres écoles",
                "INP":       "INP",
                "EPEU":      "EPEU",
                "ENS":       "ENS",
                "IUFM":      "IUFM / INSPE",
            }

            regroupements_dispo = sorted(df_eff_w["regroupement"].dropna().unique())

            # ── Bandeau filtres ───────────────────────────────────────────────
            with st.container():
                st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
                filter_bar("🔧 Filtres — Effectifs enseignement supérieur")
                ef1, ef2, ef3, ef4 = st.columns([1, 1, 1, 1])
                with ef1:
                    sel_metros_eff = st.multiselect(
                        "Métropoles", metros_eff, default=metros_eff, key="eff_metros"
                    )
                with ef2:
                    annee_eff = st.selectbox(
                        "Année", annees_eff, index=len(annees_eff) - 1, key="eff_annee"
                    )
                with ef3:
                    regr_choices = [r for r in ["TOTAL"] + [r for r in regroupements_dispo if r != "TOTAL"]]
                    sel_regr = st.selectbox(
                        "Type d'établissement",
                        regr_choices,
                        format_func=lambda r: LABEL_REGROUPEMENT.get(r, r),
                        index=0,
                        key="eff_regr",
                    )
                with ef4:
                    sel_secteur = st.selectbox(
                        "Secteur", ["Tous", "Établissements publics", "Établissements privés"],
                        key="eff_secteur"
                    )
                st.markdown('</div>', unsafe_allow_html=True)

            if not sel_metros_eff:
                st.warning("⚠️ Sélectionnez au moins une métropole.")
            else:
                # Filtrage
                df_e = df_eff_w[
                    df_eff_w["metropole"].isin(sel_metros_eff) &
                    (df_eff_w["regroupement"] == sel_regr)
                ]
                if sel_secteur != "Tous":
                    df_e = df_e[df_e["secteur_de_l_etablissement"] == sel_secteur]

                df_e_yr = df_e[df_e["annee"] == annee_eff]

                st.markdown("---")

                # ── KPI globaux ────────────────────────────────────────────────
                total_eff   = int(df_e_yr["effectif"].sum())
                nb_communes = int(df_e_yr["geo_nom"].nunique())
                nb_metros   = int(df_e_yr["metropole"].nunique())
                best_metro  = df_e_yr.groupby("metropole")["effectif"].sum().idxmax() if not df_e_yr.empty else "—"

                k1, k2, k3, k4 = st.columns(4)
                k1.metric(f"Effectif total ({annee_eff})", fmt(total_eff))
                k2.metric("Métropoles", nb_metros)
                k3.metric("Communes couvertes", nb_communes)
                k4.metric("1ère métropole", best_metro)

                st.markdown("---")

                # ── Ligne 1 : Bar comparatif + Évolution ──────────────────────
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"##### 📊 Effectifs par métropole — {annee_eff}")
                    by_metro = (df_e_yr.groupby("metropole", as_index=False)["effectif"]
                                .sum().sort_values("effectif", ascending=False))
                    fig_em = px.bar(
                        by_metro, x="metropole", y="effectif",
                        color="metropole",
                        color_discrete_map=COULEURS,
                        labels={"metropole": "", "effectif": "Étudiants"},
                        text_auto=".3s",
                        title=f"Effectif — {LABEL_REGROUPEMENT.get(sel_regr, sel_regr)} · {annee_eff}",
                        height=380,
                    )
                    fig_em.update_traces(textposition="outside")
                    fig_em.update_layout(showlegend=False)
                    st.plotly_chart(style(fig_em, 40), use_container_width=True)

                with c2:
                    st.markdown("##### 📈 Évolution des effectifs")
                    df_e_all = df_eff_w[
                        df_eff_w["metropole"].isin(sel_metros_eff) &
                        (df_eff_w["regroupement"] == sel_regr)
                    ]
                    if sel_secteur != "Tous":
                        df_e_all = df_e_all[df_e_all["secteur_de_l_etablissement"] == sel_secteur]
                    evo_e = (df_e_all.groupby(["annee", "metropole"], as_index=False)["effectif"]
                             .sum().sort_values("annee"))
                    fig_evo_e = px.line(
                        evo_e, x="annee", y="effectif", color="metropole",
                        color_discrete_map=COULEURS,
                        markers=True,
                        labels={"annee": "Année", "effectif": "Étudiants", "metropole": "Métropole"},
                        title="Évolution des effectifs étudiants",
                        height=380,
                    )
                    fig_evo_e.update_traces(line_width=2.5, marker_size=7)
                    st.plotly_chart(style(fig_evo_e, 40), use_container_width=True)

                st.markdown("---")

                # ── Ligne 2 : Répartition par type établissement + Parité H/F ─
                c3, c4 = st.columns(2)
                with c3:
                    st.markdown(f"##### 🏛️ Répartition par type d'établissement ({annee_eff})")
                    df_type = df_eff_w[
                        df_eff_w["metropole"].isin(sel_metros_eff) &
                        (df_eff_w["annee"] == annee_eff) &
                        (df_eff_w["regroupement"] != "TOTAL")
                    ]
                    if sel_secteur != "Tous":
                        df_type = df_type[df_type["secteur_de_l_etablissement"] == sel_secteur]
                    type_agg = (df_type.groupby("regroupement", as_index=False)["effectif"]
                                .sum().sort_values("effectif", ascending=False).head(10))
                    type_agg["label"] = type_agg["regroupement"].map(
                        lambda r: LABEL_REGROUPEMENT.get(r, r))
                    fig_type = px.pie(
                        type_agg, names="label", values="effectif",
                        title=f"Répartition par filière — {annee_eff}",
                        hole=0.4,
                        height=400,
                    )
                    fig_type.update_traces(textposition="inside", textinfo="percent+label")
                    st.plotly_chart(style(fig_type, 40), use_container_width=True)

                with c4:
                    st.markdown(f"##### ⚖️ Parité femmes / hommes ({annee_eff})")
                    df_sex = df_e_yr.copy()
                    if "sexe_de_l_etudiant" in df_sex.columns:
                        sex_agg = (df_sex.groupby(["metropole", "sexe_de_l_etudiant"], as_index=False)["effectif"]
                                   .sum())
                        fig_sex = px.bar(
                            sex_agg, x="metropole", y="effectif",
                            color="sexe_de_l_etudiant",
                            barmode="group",
                            color_discrete_map={"Masculin": "#2D6A4F", "Feminin": "#D4A017"},
                            labels={"metropole": "", "effectif": "Étudiants", "sexe_de_l_etudiant": "Genre"},
                            title=f"Parité H/F — {LABEL_REGROUPEMENT.get(sel_regr, sel_regr)}",
                            height=400,
                        )
                        fig_sex.update_layout(legend=dict(orientation="h", y=1.1))
                        st.plotly_chart(style(fig_sex, 40), use_container_width=True)
                    else:
                        st.info("Données de genre non disponibles.")

                st.markdown("---")

                # ── Top communes + Secteur public/privé ───────────────────────
                c5, c6 = st.columns(2)
                with c5:
                    st.markdown(f"##### 🏆 Top 15 communes — {annee_eff}")
                    top_com = (df_e_yr.groupby(["geo_nom", "metropole"], as_index=False)["effectif"]
                               .sum().nlargest(15, "effectif"))
                    fig_tc = px.bar(
                        top_com, x="effectif", y="geo_nom",
                        orientation="h",
                        color="metropole",
                        color_discrete_map=COULEURS,
                        labels={"geo_nom": "", "effectif": "Étudiants"},
                        text_auto=".3s",
                        title=f"Top communes par effectif — {annee_eff}",
                        height=430,
                    )
                    fig_tc.update_layout(yaxis={"categoryorder": "total ascending"})
                    st.plotly_chart(style(fig_tc, 40), use_container_width=True)

                with c6:
                    st.markdown(f"##### 🏫 Public vs Privé ({annee_eff})")
                    if "secteur_de_l_etablissement" in df_e_yr.columns:
                        sec_agg = (df_e_yr.groupby(["metropole", "secteur_de_l_etablissement"], as_index=False)["effectif"]
                                   .sum())
                        fig_sec = px.bar(
                            sec_agg, x="metropole", y="effectif",
                            color="secteur_de_l_etablissement",
                            barmode="stack",
                            color_discrete_map={
                                "Établissements publics": "#2D6A4F",
                                "Établissements privés": "#D4A017",
                            },
                            labels={"metropole": "", "effectif": "Étudiants", "secteur_de_l_etablissement": "Secteur"},
                            title=f"Répartition public / privé — {annee_eff}",
                            height=430,
                        )
                        fig_sec.update_layout(legend=dict(orientation="h", y=1.1))
                        st.plotly_chart(style(fig_sec, 40), use_container_width=True)

                st.markdown("---")
                with st.expander("📄 Voir le tableau de données"):
                    st.dataframe(
                        df_e_yr.groupby(["metropole", "geo_nom", "regroupement", "secteur_de_l_etablissement"],
                                        as_index=False)["effectif"].sum().sort_values("effectif", ascending=False),
                        use_container_width=True,
                    )
                with st.expander("📖 Note méthodologique"):
                    st.write(
                        "**Source** : Ministère de l'Enseignement Supérieur, de la Recherche et de l'Innovation (MESRI).\n\n"
                        "**Périmètre** : Communes appartenant aux 5 agglomérations (Grenoble, Rennes, Rouen, Saint-Étienne, Montpellier), "
                        "identifiées via le code département (38, 35, 76, 42, 34).\n\n"
                        "**TOTAL** : agrège tous types d'établissements. Les autres filtres permettent de descendre par filière.\n\n"
                        "**Effectif** : nombre d'étudiants inscrits en formation initiale."
                    )
    with s3:
        st.markdown('<p class="section-header">🏥 Santé</p>', unsafe_allow_html=True)
        st.info("📂 Page en cours de construction — branchez un fichier CSV dans `solidarite&citoyennete/data_clean/sante/`.")

    with s4:
        st.markdown('<p class="section-header">🗳️ Participation citoyenne</p>', unsafe_allow_html=True)
        st.info("📂 Page en cours de construction — branchez un fichier CSV dans `solidarite&citoyennete/data_clean/participation/`.")

    with s5:
        st.markdown('<p class="section-header">🗄️ Base de données</p>', unsafe_allow_html=True)
        st.markdown("""
        <div class="filter-bar">
        <div class="filter-bar-title">📦 Jeux de données disponibles</div>
        </div>
        """, unsafe_allow_html=True)

        datasets = {
            "CAF — 5 Métropoles": {
                "desc": "Données CAF communales 2020–2023 (foyers, personnes, montants par type d'aide et quotient familial).",
                "path": "solidarite&citoyennete/data_clean/solidarite/CAF_5_Metropoles.csv",
                "icon": "🤝",
                "status": "✅ Disponible" if df_caf is not None else "❌ Introuvable",
            },
            "Effectifs enseignement supérieur": {
                "desc": "Effectifs étudiants par commune, filière et genre — 5 départements · 2002–2024.",
                "path": "solidarite&citoyennete/data_clean/education/effectifs_5_villes.csv",
                "icon": "🎓",
                "status": "✅ Disponible" if df_eff is not None else "❌ Introuvable",
            },
            "Santé": {
                "desc": "À brancher — indicateurs de santé par commune ou agglomération.",
                "path": "solidarite&citoyennete/data_clean/sante/",
                "icon": "🏥",
                "status": "🔜 À venir",
            },
            "Participation citoyenne": {
                "desc": "À brancher — taux de participation, associations, vie démocratique locale.",
                "path": "solidarite&citoyennete/data_clean/participation/",
                "icon": "🗳️",
                "status": "🔜 À venir",
            },
        }

        for name, info in datasets.items():
            with st.expander(f"{info['icon']} {name} — {info['status']}"):
                st.markdown(f"**Description :** {info['desc']}")
                st.markdown(f"**Chemin attendu :** `{info['path']}`")
                if "✅" in info["status"]:
                    if name == "CAF — 5 Métropoles" and df_caf is not None:
                        st.markdown(f"**Dimensions :** {df_caf.shape[0]:,} lignes × {df_caf.shape[1]} colonnes".replace(",", "\u202f"))
                        st.dataframe(df_caf.head(5), use_container_width=True)
                    elif name == "Effectifs enseignement supérieur" and df_eff is not None:
                        st.markdown(f"**Dimensions :** {df_eff.shape[0]:,} lignes × {df_eff.shape[1]} colonnes".replace(",", "\u202f"))
                        st.dataframe(df_eff.head(5), use_container_width=True)

# ──────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#9AB8A7;font-size:0.72rem'>"
    "Données INSEE · Recensements de la Population 2011, 2016, 2022 · "
    "Mobilités résidentielles, professionnelles et scolaires 2019–2022</p>",
    unsafe_allow_html=True,
)
