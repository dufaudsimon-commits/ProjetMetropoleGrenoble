# =============================================================================
# APPLICATION STREAMLIT — DÉMOGRAPHIE DES MÉTROPOLES FRANÇAISES
# Grenoble · Rennes · Saint-Étienne · Rouen · Montpellier
# Sources : INSEE — Recensements de la Population 2011, 2016, 2022
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

# Noms EXACTS dans le fichier Donnees_generales_comparatives_clean.csv
# Seuls Grenoble et Rennes ont une ligne EPCI agrégée dans ce fichier INSEE.
# Rouen, Saint-Étienne, Montpellier n'y ont que des lignes par commune.
NOM_EPCI = {
    "Grenoble": "EPCI : Grenoble-Alpes-Métropole (200040715)",
    "Rennes":   "EPCI : Rennes Métropole (243500139)",
}

COULEURS = {
    "Grenoble":      "#2D6A4F",
    "Rennes":        "#1A6FA3",
    "Saint-Étienne": "#C45B2A",
    "Rouen":         "#7B3FA0",
    "Montpellier":   "#D4A017",
}
TOUTES = list(COMMUNES.keys())

DEP_MAP = {
    "Grenoble": "38",
    "Rennes": "35",
    "Rouen": "76",
    "Saint-Étienne": "42",
    "Montpellier": "34",
}

CSP_MAP = {
    "Agriculteurs": "Agriculteurs",
    "Artisans, commerçants, chefs d'entreprise": "Artisans & Chefs d'ent.",
    "Cadres et professions intellectuelles supérieures": "Cadres & Prof. Sup.",
    "Professions intermédiaires": "Prof. Intermédiaires",
    "Employés": "Employés",
    "Ouvriers": "Ouvriers",
}

# Nomenclature colonnes âge : ageq_recNNsXrpop2016
# NN = 01..20 (tranches 5 ans), s1 = Hommes, s2 = Femmes
LABEL_TRANCHE = {
    "01":"0–4","02":"5–9","03":"10–14","04":"15–19","05":"20–24",
    "06":"25–29","07":"30–34","08":"35–39","09":"40–44","10":"45–49",
    "11":"50–54","12":"55–59","13":"60–64","14":"65–69","15":"70–74",
    "16":"75–79","17":"80–84","18":"85–89","19":"90–94","20":"95+",
}
TRANCHES_JEUNES  = ["01","02","03","04"]           # 0-19 ans
TRANCHES_ACTIFS  = ["05","06","07","08","09","10","11","12","13"]  # 20-64 ans
TRANCHES_SENIORS = ["14","15","16","17","18","19","20"]  # 65 ans +

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
def charger_mob_scol():
    p = DATA_DIR / "mobilite" / "Mobilite_scolaire_clean.csv"
    return pd.read_csv(p) if p.exists() else None

@st.cache_data
def charger_mob_prof():
    p = DATA_DIR / "mobilite" / "Mobilite_profess_clean.csv"
    return pd.read_csv(p) if p.exists() else None

@st.cache_data
def charger_caf():
    p = Path("solidarite&citoyennete/data_clean/solidarite/CAF_5_Metropoles.csv")
    if not p.exists():
        return None
    df = pd.read_csv(p, sep=";", low_memory=False)
    if "Date_Ref" in df.columns and "Annee" not in df.columns:
        df["Annee"] = pd.to_datetime(df["Date_Ref"], errors="coerce").dt.year
    return df

@st.cache_data
def charger_csp_comparatif():
    def read_table(path: Path) -> pd.DataFrame:
        if path.suffix.lower() in [".xlsx", ".xls"]:
            return pd.read_excel(path)
        return pd.read_csv(path, sep=None, engine="python", low_memory=False)

    candidate_dirs = [
        Path("data_clean/demographie/population_2554"),
        Path("demographie/data_clean/population_2554"),
        Path("solidarite&citoyennete/data_clean/demographie/population_2554"),
        Path("."),
    ]
    patterns = [
        "Commune_*2554*sect*activite*.xlsx",
        "Commune_*2554*sect*activite*.xls",
        "Commune_*2554*sect*activite*.csv",
        "Commune_*2554*sect*activite*.txt",
    ]

    discovered = []
    for base in candidate_dirs:
        if not base.exists():
            continue
        for pat in patterns:
            discovered.extend(sorted(base.rglob(pat)))
        if "population_2554" in str(base).lower():
            discovered.extend(sorted(base.rglob("*.xlsx")))
            discovered.extend(sorted(base.rglob("*.xls")))
            discovered.extend(sorted(base.rglob("*.csv")))
            discovered.extend(sorted(base.rglob("*.txt")))

    seen = set()
    files = []
    for p in discovered:
        key = str(p.resolve())
        if key not in seen:
            seen.add(key)
            files.append(p)

    all_data = []
    for path in files:
        try:
            df = read_table(path)
            if df.empty:
                continue
            if "RR" in str(df.iloc[0, 0]):
                df = df.drop(0).reset_index(drop=True)
            c_dep = [c for c in df.columns if "DÉPARTEMENT" in str(c).upper() or "DEPARTEMENT" in str(c).upper() or "DR24" in str(c).upper()][0]
            c_lib = [c for c in df.columns if "LIBELLÉ" in str(c).upper() or "LIBELLE" in str(c).upper()][0]
            year = None
            for token in path.name.replace("-", "_").split("_"):
                if token.isdigit() and len(token) == 4:
                    year = int(token)
                    break
            res = pd.DataFrame({
                "DEP": df[c_dep].astype(str).str.zfill(2),
                "LIBELLE": df[c_lib].astype(str),
                "ANNEE": year,
                "LIB_NORM": df[c_lib].apply(normalize_csp_name),
            })
            for raw, clean in CSP_MAP.items():
                cols = [c for c in df.columns if raw in str(c)]
                res[clean] = df[cols].apply(pd.to_numeric, errors="coerce").fillna(0).sum(axis=1)
            all_data.append(res)
        except Exception:
            continue
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

df_gen     = charger_generales()
df_pop     = charger_pop_age()
df_men_age = charger_men_age()
df_men_csp = charger_men_csp()
df_mob_sc  = charger_mob_scol()
df_mob_pr  = charger_mob_prof()
df_caf     = charger_caf()
df_csp_cmp = charger_csp_comparatif()

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
    """Ligne EPCI dans df_gen — disponible uniquement pour Grenoble et Rennes."""
    if df_gen is None or metro not in NOM_EPCI:
        return None
    rows = df_gen[df_gen["territoire"] == NOM_EPCI[metro]]
    return rows.iloc[0] if not rows.empty else None

def get_val_gen(metro, col):
    """
    Récupère une valeur du fichier général pour une métropole.
    Priorité 1 : ligne EPCI (Grenoble, Rennes).
    Priorité 2 : somme des communes (Rouen, Saint-Étienne, Montpellier) — colonnes additives.
    Priorité 3 : calcul depuis df_pop pour population_2022.
    """
    # Priorité 1
    row = get_epci_row(metro)
    if row is not None:
        v = row.get(col, np.nan)
        if not pd.isna(v):
            return float(v)

    # Priorité 2 — agrégation communes dans df_gen
    if df_gen is not None:
        commune_list = COMMUNES.get(metro, [])
        mask = df_gen["territoire"].apply(
            lambda t: any(f": {c} (" in str(t) for c in commune_list)
        )
        sub = df_gen[mask]
        if not sub.empty and col in sub.columns:
            vals = pd.to_numeric(sub[col], errors="coerce")
            if vals.notna().any():
                # Pour les totaux, on somme ; pour les taux, on n'agrège pas
                taux_cols = {"densite_2022","tx_var_population_2016_2022","tx_solde_naturel",
                             "tx_solde_migratoire","tx_chomage_15_64","tx_activite_15_64",
                             "tx_pauvrete_2021","tx_var_emploi_2016_2022","revenu_median_2021",
                             "part_admin","part_agri","part_industrie","part_construction",
                             "part_commerce","part_logements_vacants","part_menages_imposes",
                             "part_proprietaires","part_res_principales","part_res_secondaires",
                             "part_etab_1_9","part_etab_10_plus","part_emploi_salarie"}
                if col in taux_cols:
                    return float(vals.mean())  # moyenne des communes pour les taux
                return float(vals.sum())       # somme pour les effectifs

    # Priorité 3 — population depuis df_pop
    if col == "population_2022" and df_pop is not None:
        dm = df_pop[(df_pop["metropole"] == metro) & (df_pop["annee"] == 2022)]
        if not dm.empty:
            ac = [c for c in dm.columns if "ageq_rec" in c]
            return float(dm[ac].sum().sum())

    return np.nan

def cols_h(df):
    """Colonnes Hommes (s1), triées par numéro de tranche."""
    return sorted([c for c in df.columns if "ageq_rec" in c and "s1" in c])

def cols_f(df):
    """Colonnes Femmes (s2), triées par numéro de tranche."""
    return sorted([c for c in df.columns if "ageq_rec" in c and "s2" in c])

def label_col(col):
    import re
    m = re.search(r"ageq_rec(\d{2})", col)
    return LABEL_TRANCHE.get(m.group(1), col) if m else col

def somme_tranches(df_src, tranches, annee=None):
    """Somme H+F pour les tranches données, avec filtre optionnel sur l'année."""
    if annee is not None:
        df_src = df_src[df_src["annee"] == annee]
    total = 0
    for t in tranches:
        for sx in ["s1","s2"]:
            col = f"ageq_rec{t}{sx}rpop2016"
            if col in df_src.columns:
                total += df_src[col].sum()
    return total

def style(fig, marge_t=20):
    fig.update_layout(template="plotly_white", plot_bgcolor="rgba(0,0,0,0)",
                      paper_bgcolor="rgba(0,0,0,0)", font_family="Sora",
                      margin=dict(t=marge_t, b=20, l=10, r=10))
    return fig

def normalize_csp_name(text):
    if pd.isna(text):
        return ""
    return (
        unicodedata.normalize("NFKD", str(text))
        .encode("ascii", "ignore")
        .decode("utf-8")
        .lower()
        .strip()
    )

# ──────────────────────────────────────────────────────────────────────────────
# 5. EN-TÊTE
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
        st.markdown(
            """
### Objectif
Comparer les dynamiques territoriales des 5 métropoles à partir des données de **démographie** et de **solidarité & citoyenneté**.

### Contenu
- Démographie : population, âge, mobilités, ménages
- Solidarité & citoyenneté : CAF, éducation, santé, participation citoyenne
            """.strip()
        )
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

with st.sidebar:
    if st.button("🏠 Accueil"):
        st.session_state.page = "home"
        st.rerun()
    st.markdown("---")
    vue = st.radio("Navigation", ["Description", "Démographie", "Solidarité et citoyenneté"], index=0, label_visibility="collapsed")

# ──────────────────────────────────────────────────────────────────────────────
# 6. ONGLETS
# ──────────────────────────────────────────────────────────────────────────────
if vue == "Description":
    st.markdown('<p class="section-header">Description</p>', unsafe_allow_html=True)
    st.write("Cette application présente des analyses comparatives sur les volets démographie et solidarité/citoyenneté.")
    st.write("Utilise le volet gauche pour choisir entre `Démographie` et `Solidarité et citoyenneté`.")
    st.stop()

if vue == "Démographie":
    tab1, tab2, tab3, tab4, tab6 = st.tabs([
        "🏙️  Population globale",
        "👥  Structure par âge",
        "🚌  Mobilités",
        "🏠  Ménages",
        "📊  CSP_comparatif",
    ])

# ==============================================================================
# ONGLET 1 — POPULATION GLOBALE
# ==============================================================================
if vue == "Démographie":
    with tab1:
        st.markdown('<p class="section-header">Population — Vue d\'ensemble</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="source-note">Source : <a href="https://www.insee.fr/fr/statistiques/1405599" target="_blank">'
            'INSEE — Données générales comparatives (RP 2022)</a> — '
            'Lignes EPCI disponibles pour Grenoble & Rennes uniquement ; '
            'les autres métropoles sont calculées par agrégation de leurs communes.</p>',
            unsafe_allow_html=True,
        )

    st.markdown("**🔧 Sélectionnez les métropoles à comparer**")
    sel = st.multiselect("Métropoles", TOUTES, default=["Grenoble","Rennes"],
                         key="sel_t1", label_visibility="collapsed")
    if not sel:
        st.warning("Sélectionnez au moins une métropole.")
        st.stop()
    st.markdown("---")

    # KPIs
    kpi_cols = st.columns(len(sel))
    for i, m in enumerate(sel):
        pop = get_val_gen(m, "population_2022")
        tx  = get_val_gen(m, "tx_var_population_2016_2022")
        with kpi_cols[i]:
            delta = f"{tx:+.2f} %/an (2016–22)" if not np.isnan(tx) else None
            st.metric(f"🌿 {m}", fmt(pop), delta=delta)

    st.markdown("---")
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("##### Population totale 2022")
        data = [{"Métropole": m, "Population": get_val_gen(m,"population_2022")} for m in sel]
        df_p = pd.DataFrame(data).dropna()
        if not df_p.empty:
            fig = px.bar(df_p, x="Métropole", y="Population",
                         color="Métropole", color_discrete_map=COULEURS, text_auto=".3s")
            fig.update_traces(marker_line_width=0, textfont_size=11)
            fig.update_layout(showlegend=False, yaxis_title="Habitants")
            st.plotly_chart(style(fig), use_container_width=True)

    with col_b:
        st.markdown("##### Décomposition de la variation démographique (%/an, 2016–2022)")
        rows_var = []
        for m in sel:
            row = get_epci_row(m)  # disponible Grenoble + Rennes seulement
            if row is not None:
                rows_var.append({
                    "Métropole":       m,
                    "Variation totale":  row.get("tx_var_population_2016_2022", np.nan),
                    "Solde naturel":     row.get("tx_solde_naturel", np.nan),
                    "Solde migratoire":  row.get("tx_solde_migratoire", np.nan),
                })
        if rows_var:
            df_var = pd.DataFrame(rows_var).melt(
                id_vars="Métropole", var_name="Composante", value_name="Taux (%/an)").dropna()
            fig2 = px.bar(df_var, x="Taux (%/an)", y="Métropole", color="Composante",
                          orientation="h", barmode="group",
                          color_discrete_sequence=["#2D6A4F","#74C69D","#B7E4C7"])
            fig2.add_vline(x=0, line_dash="dot", line_color="#AAAAAA")
            fig2.update_layout(legend=dict(orientation="h", y=1.12))
            st.plotly_chart(style(fig2), use_container_width=True)
        else:
            st.info("Les taux de variation détaillés (solde naturel / migratoire) sont disponibles uniquement pour Grenoble et Rennes dans le fichier source INSEE.")

    st.markdown("---")
    col_c, col_d = st.columns(2)

    with col_c:
        st.markdown("##### Densité de population (hab/km²) en 2022")
        data_d = [{"Métropole": m, "Densité": get_val_gen(m,"densite_2022")} for m in sel]
        df_d = pd.DataFrame(data_d).dropna().sort_values("Densité")
        if not df_d.empty:
            fig3 = px.bar(df_d, x="Densité", y="Métropole", orientation="h",
                          color="Métropole", color_discrete_map=COULEURS, text_auto=".0f")
            fig3.update_layout(showlegend=False, xaxis_title="hab/km²", yaxis_title="")
            fig3.update_traces(marker_line_width=0)
            st.plotly_chart(style(fig3), use_container_width=True)

    with col_d:
        st.markdown("##### Tableau récapitulatif")
        lignes = []
        for m in sel:
            tx_v = get_val_gen(m,"tx_var_population_2016_2022")
            tc   = get_val_gen(m,"tx_chomage_15_64")
            rev  = get_val_gen(m,"revenu_median_2021")
            lignes.append({
                "Métropole":          m,
                "Population 2022":    fmt(get_val_gen(m,"population_2022")),
                "Densité (hab/km²)":  fmt(get_val_gen(m,"densite_2022")),
                "Var. pop./an":       f"{tx_v:+.2f}%" if not np.isnan(tx_v) else "N/D",
                "Taux chômage":       f"{tc:.1f}%" if not np.isnan(tc) else "N/D",
                "Revenu médian":      fmt(rev, " €"),
                "Nb. ménages":        fmt(get_val_gen(m,"nb_menages_2022")),
            })
        st.dataframe(pd.DataFrame(lignes).set_index("Métropole"), use_container_width=True)
        st.caption("N/D : indicateur non disponible au niveau EPCI pour cette métropole dans le fichier source INSEE.")

# ==============================================================================
# ONGLET 2 — STRUCTURE PAR ÂGE
# ==============================================================================
if vue == "Démographie":
    with tab2:
        st.markdown('<p class="section-header">Structure par âge et par sexe</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="source-note">Source : <a href="https://www.insee.fr/fr/statistiques/1893204" target="_blank">'
            'INSEE — Population par tranche d\'âge quinquennal (RP 2011, 2016, 2022)</a> — '
            'Colonnes ageq_recNN : NN=01..20 (tranches de 5 ans), s1=Hommes, s2=Femmes</p>',
            unsafe_allow_html=True,
        )

    if df_pop is None:
        st.info("📂 Fichier `Population_tranche_age_clean.csv` introuvable dans `Donnees_clean/`.")
    else:
        annees = sorted(df_pop["annee"].dropna().unique().astype(int).tolist())
        ch = cols_h(df_pop)
        cf = cols_f(df_pop)

        # FILTRES
        st.markdown("**🔧 Filtres**")
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
                comm_b = st.selectbox("Commune B", cmns, index=min(1,len(cmns)-1), key="cb")
        st.markdown("---")

        df_m = df_pop[(df_pop["metropole"] == metro_age) & (df_pop["annee"] == annee_age)]

        if not mode_cc:
            st.markdown(f"##### Pyramide des âges — {metro_age} ({annee_age})")
            if ch and cf and not df_m.empty:
                labels = [label_col(c) for c in ch]
                fig_p = go.Figure()
                fig_p.add_trace(go.Bar(
                    y=labels, x=[-df_m[c].sum() for c in ch], name="Hommes",
                    orientation="h", marker_color="#2D6A4F"))
                fig_p.add_trace(go.Bar(
                    y=labels, x=[df_m[c].sum() for c in cf], name="Femmes",
                    orientation="h", marker_color="#95D5B2"))
                fig_p.update_layout(barmode="relative", bargap=0.06,
                                    legend=dict(orientation="h", y=1.08),
                                    yaxis_title="Tranche d'âge (ans)",
                                    xaxis_title="Population")
                st.plotly_chart(style(fig_p, 40), use_container_width=True)
            else:
                st.info("Données insuffisantes pour la pyramide.")
        else:
            st.markdown(f"##### {comm_a} vs {comm_b} ({annee_age})")
            df_ca = df_pop[(df_pop["LIBELLE"]==comm_a) & (df_pop["annee"]==annee_age)]
            df_cb = df_pop[(df_pop["LIBELLE"]==comm_b) & (df_pop["annee"]==annee_age)]
            if not df_ca.empty and not df_cb.empty and ch and cf:
                rows_c = [{"Tranche": label_col(h),
                           comm_a: df_ca[h].sum() + df_ca[f].sum(),
                           comm_b: df_cb[h].sum() + df_cb[f].sum()}
                          for h, f in zip(ch, cf)]
                df_cc = pd.melt(pd.DataFrame(rows_c), id_vars="Tranche",
                                var_name="Commune", value_name="Population")
                fig_cc = px.bar(df_cc, x="Tranche", y="Population", color="Commune",
                                barmode="group", color_discrete_sequence=["#2D6A4F","#95D5B2"])
                fig_cc.update_layout(xaxis_tickangle=-40, legend=dict(orientation="h", y=1.08))
                st.plotly_chart(style(fig_cc), use_container_width=True)
            else:
                st.info("Données insuffisantes pour ces communes.")

        st.markdown("---")
        st.markdown("##### Indices démographiques par métropole")
        idx_c = st.columns(len(TOUTES))
        for i, m in enumerate(TOUTES):
            dm = df_pop[(df_pop["metropole"]==m) & (df_pop["annee"]==annee_age)]
            pj = somme_tranches(dm, TRANCHES_JEUNES)
            pa = somme_tranches(dm, TRANCHES_ACTIFS)
            ps = somme_tranches(dm, TRANCHES_SENIORS)
            iv = (ps/pj*100) if pj>0 else np.nan
            rd = ((pj+ps)/pa*100) if pa>0 else np.nan
            with idx_c[i]:
                st.metric(f"Vieillissement\n{m}", f"{iv:.0f}" if not np.isnan(iv) else "N/D",
                          help="65+ / <20 ans × 100")
                st.metric(f"Dépendance\n{m}", f"{rd:.0f}%" if not np.isnan(rd) else "N/D",
                          help="(Jeunes + Seniors) / Actifs")

        st.markdown("---")
        st.markdown("##### Évolution de la population totale (2011 → 2022)")
        sel_evol = st.multiselect("Métropoles", TOUTES,
                                  default=["Grenoble","Rennes"], key="evol")
        if sel_evol and ch and cf:
            df_e = df_pop[df_pop["metropole"].isin(sel_evol)].copy()
            df_e["pop_totale"] = df_e[[c for c in ch+cf if c in df_e.columns]].sum(axis=1)
            df_g = df_e.groupby(["metropole","annee"])["pop_totale"].sum().reset_index()
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
        st.markdown('<p class="section-header">Dynamiques de mobilité</p>', unsafe_allow_html=True)
        st_sc, st_pr = st.tabs(["🎓 Mobilités scolaires","💼 Mobilités professionnelles"])

    with st_sc:
        st.markdown('<p class="source-note">Source : <a href="https://www.insee.fr/fr/statistiques/8582969" target="_blank">INSEE — Mobilités scolaires 2019 & 2022</a></p>', unsafe_allow_html=True)
        if df_mob_sc is None:
            st.info("📂 Fichier `Mobilite_scolaire_clean.csv` introuvable dans `Donnees_clean/`.")
        else:
            ann_sc = sorted(df_mob_sc["annee"].dropna().unique().astype(int).tolist())
            st.markdown("**🔧 Filtres**")
            fs1, fs2 = st.columns(2)
            with fs1:
                an_s = st.selectbox("Année", ann_sc, index=len(ann_sc)-1, key="an_s")
            with fs2:
                metro_s = st.selectbox("Métropole d'origine", TOUTES, key="m_s")
            st.markdown("---")
            df_s = df_mob_sc[(df_mob_sc["annee"]==an_s) &
                             (df_mob_sc["commune_origine"].isin(COMMUNES[metro_s]))]
            if df_s.empty:
                st.info(f"Aucune donnée scolaire pour {metro_s} en {an_s}.")
            else:
                k1,k2 = st.columns(2)
                k1.metric("Total élèves en mobilité", fmt(df_s["flux"].sum()))
                k2.metric("Communes de destination distinctes", str(df_s["commune_destination"].nunique()))
                st.markdown("---")
                c1,c2 = st.columns(2)
                with c1:
                    st.markdown("##### Top 15 communes de destination")
                    top = (df_s.groupby("commune_destination")["flux"].sum()
                           .sort_values(ascending=False).head(15).reset_index())
                    fig_s = px.bar(top, x="flux", y="commune_destination", orientation="h",
                                   color_discrete_sequence=[COULEURS[metro_s]], text_auto=".0f")
                    fig_s.update_layout(yaxis={"autorange":"reversed"}, xaxis_title="Élèves", yaxis_title="")
                    st.plotly_chart(style(fig_s), use_container_width=True)
                with c2:
                    st.markdown("##### Intra- vs extra-département")
                    dep_o = df_s["dep_origine"].iloc[0] if "dep_origine" in df_s.columns else ""
                    df_s2 = df_s.copy()
                    df_s2["type"] = df_s2["dep_destination"].apply(
                        lambda d: "Intra-département" if d==dep_o else "Autre département")
                    pie = df_s2.groupby("type")["flux"].sum().reset_index()
                    fig_p = px.pie(pie, names="type", values="flux", hole=0.42,
                                   color_discrete_sequence=["#2D6A4F","#B7E4C7"])
                    st.plotly_chart(style(fig_p), use_container_width=True)

    with st_pr:
        st.markdown('<p class="source-note">Source : <a href="https://www.insee.fr/fr/statistiques/8582949" target="_blank">INSEE — Mobilités professionnelles 2019 & 2022</a></p>', unsafe_allow_html=True)
        if df_mob_pr is None:
            st.info("📂 Fichier `Mobilite_profess_clean.csv` introuvable dans `Donnees_clean/`.")
        else:
            ann_pr = sorted(df_mob_pr["annee"].dropna().unique().astype(int).tolist())
            st.markdown("**🔧 Filtres**")
            fp1, fp2 = st.columns(2)
            with fp1:
                an_p = st.selectbox("Année", ann_pr, index=len(ann_pr)-1, key="an_p")
            with fp2:
                metro_p = st.selectbox("Métropole de résidence", TOUTES, key="m_p")
            st.markdown("---")
            df_p = df_mob_pr[(df_mob_pr["annee"]==an_p) &
                             (df_mob_pr["commune_residence"].isin(COMMUNES[metro_p]))]
            if df_p.empty:
                st.info(f"Aucune donnée professionnelle pour {metro_p} en {an_p}.")
            else:
                k1,k2 = st.columns(2)
                k1.metric("Total actifs en mobilité", fmt(df_p["flux"].sum()))
                k2.metric("Communes de travail distinctes", str(df_p["commune_travail"].nunique()))
                st.markdown("---")
                c1,c2 = st.columns(2)
                with c1:
                    st.markdown("##### Top 15 lieux de travail")
                    top_t = (df_p.groupby("commune_travail")["flux"].sum()
                             .sort_values(ascending=False).head(15).reset_index())
                    fig_pt = px.bar(top_t, x="flux", y="commune_travail", orientation="h",
                                    color_discrete_sequence=[COULEURS[metro_p]], text_auto=".0f")
                    fig_pt.update_layout(yaxis={"autorange":"reversed"}, xaxis_title="Actifs", yaxis_title="")
                    st.plotly_chart(style(fig_pt), use_container_width=True)
                with c2:
                    st.markdown("##### Même département vs autre")
                    df_p2 = df_p.copy()
                    df_p2["type"] = df_p2.apply(
                        lambda r: "Même département"
                        if r.get("dep_residence","")==r.get("dep_travail","")
                        else "Autre département", axis=1)
                    pie_p = df_p2.groupby("type")["flux"].sum().reset_index()
                    fig_pp = px.pie(pie_p, names="type", values="flux", hole=0.42,
                                    color_discrete_sequence=["#1A6FA3","#AED4F0"])
                    st.plotly_chart(style(fig_pp), use_container_width=True)
                if len(ann_pr) >= 2:
                    st.markdown("---")
                    st.markdown("##### Évolution du flux total (2019 → 2022)")
                    comp = [{"Année": str(yr),
                             "Flux": df_mob_pr[(df_mob_pr["annee"]==yr) &
                                               (df_mob_pr["commune_residence"].isin(COMMUNES[metro_p]))]["flux"].sum()}
                            for yr in ann_pr]
                    fig_ev = px.bar(pd.DataFrame(comp), x="Année", y="Flux", color="Année",
                                    color_discrete_sequence=["#AED4F0","#1A6FA3"], text_auto=".3s")
                    fig_ev.update_layout(showlegend=False)
                    st.plotly_chart(style(fig_ev), use_container_width=True)

# ==============================================================================
# ONGLET 4 — MÉNAGES
# ==============================================================================
if vue == "Démographie":
    with tab4:
        st.markdown('<p class="section-header">Structure des ménages</p>', unsafe_allow_html=True)
        st.markdown('<p class="source-note">Source : <a href="https://www.insee.fr/fr/statistiques/8582448" target="_blank">INSEE — Ménages par âge, situation familiale et CSP (RP 2022)</a></p>', unsafe_allow_html=True)

        sous1, sous2 = st.tabs(["👨‍👩‍👧 Type & taille de ménage","🧑‍💼 CSP des ménages"])

    with sous1:
        if df_men_age is None:
            st.info("📂 Fichier `Menage_age_situation_clean.csv` introuvable dans `Donnees_clean/`.")
        else:
            st.markdown("**🔧 Filtres**")
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
                    comm_mb = st.selectbox("Commune B", cmns_men,
                                           index=min(1,len(cmns_men)-1), key="cmb")
            st.markdown("---")

            df_men_m = df_men_age[df_men_age["metropole"] == metro_men]
            cols_m = [c for c in df_men_age.columns if c.startswith("Menages_")]

            # KPIs — nombre de ménages calculé depuis le fichier ménages (somme de toutes les cellules)
            nb_men = df_men_m[cols_m].sum().sum() if not df_men_m.empty else np.nan
            pop_m  = np.nan
            if df_pop is not None:
                dm2 = df_pop[(df_pop["metropole"]==metro_men) & (df_pop["annee"]==2022)]
                if not dm2.empty:
                    pop_m = dm2[[c for c in dm2.columns if "ageq_rec" in c]].sum().sum()
            taille = (pop_m / nb_men) if (not np.isnan(nb_men) and nb_men > 0) else np.nan

            k1, k2 = st.columns(2)
            k1.metric(f"Nombre de ménages — {metro_men}", fmt(nb_men))
            k2.metric("Taille moyenne du ménage",
                      f"{taille:.2f} pers." if not np.isnan(taille) else "N/D")
            st.markdown("---")

            TYPE_GROUPES = {
                "Personne seule":      [c for c in cols_m if "pers_seule" in c],
                "Couple sans enfant":  [c for c in cols_m if "cpl_sans_enf" in c],
                "Couple avec enfant":  [c for c in cols_m if "cpl_avec_enfant" in c or "cpl_1enf" in c],
                "Fam. mono. (mère)":   [c for c in cols_m if "mere_enf" in c],
                "Fam. mono. (père)":   [c for c in cols_m if "pere_enf" in c],
                "Autre ménage":        [c for c in cols_m if "autre_menage" in c],
            }
            AGE_LABELS = {
                "< 20 ans": "moins20ans","20–24 ans":"20_24ans","25–39 ans":"25_39ans",
                "40–54 ans":"40_54ans","55–64 ans":"55_64ans","65–79 ans":"65_79ans","80 ans +":"plus80ans",
            }

            if not mode_cc_men:
                totaux = {lbl: df_men_m[[c for c in cols if c in df_men_m.columns]].sum().sum()
                          for lbl, cols in TYPE_GROUPES.items()}
                df_t = pd.DataFrame(list(totaux.items()), columns=["Type","Ménages"])
                df_t = df_t[df_t["Ménages"]>0].sort_values("Ménages", ascending=False)

                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"##### Types de ménages — {metro_men}")
                    fig_t = px.bar(df_t, x="Ménages", y="Type", orientation="h",
                                   color_discrete_sequence=[COULEURS[metro_men]], text_auto=".0f")
                    fig_t.update_layout(yaxis={"autorange":"reversed"}, yaxis_title="", xaxis_title="Ménages")
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
                            rows_a.append({"Âge référent":age_l,"Type":type_l,"Ménages":val})
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
                    df_cc = df_men_age[df_men_age["LIBGEO"]==comm]
                    for lbl, cols in TYPE_GROUPES.items():
                        valid = [c for c in cols if c in df_cc.columns]
                        rows_cc.append({"Commune":comm,"Type":lbl,
                                        "Ménages":df_cc[valid].sum().sum() if valid else 0})
                df_ccp = pd.DataFrame(rows_cc)
                if df_ccp["Ménages"].sum() > 0:
                    fig_ccp = px.bar(df_ccp, x="Type", y="Ménages", color="Commune",
                                     barmode="group", color_discrete_sequence=["#2D6A4F","#95D5B2"])
                    fig_ccp.update_layout(xaxis_tickangle=-20, legend=dict(orientation="h"))
                    st.plotly_chart(style(fig_ccp), use_container_width=True)
                else:
                    st.info("Données non disponibles pour ces communes.")

    with sous2:
        if df_men_csp is None:
            st.info("📂 Fichier `Menages_csp_nbpers_clean.csv` introuvable dans `Donnees_clean/`.")
        else:
            st.markdown("**🔧 Filtres**")
            fc1, fc2 = st.columns(2)
            with fc1:
                metro_csp = st.selectbox("Métropole", TOUTES, key="m_csp")
            with fc2:
                comp_csp = st.checkbox("Comparer toutes les métropoles (%)", key="comp_csp")
            st.markdown("---")

            cols_csp = [c for c in df_men_csp.columns if c.startswith("Menages_")]
            CSP_GROUPES = {
                "Agriculteurs":           ["agriculteurs"],
                "Artisans / Commerçants": ["artisans","commercants","chef_entreprise"],
                "Cadres & Prof. sup.":    ["professions_liberales","cadre_admin","prof_scientifique",
                                           "ingenieur","info_art","cadre_commercial"],
                "Prof. intermédiaires":   ["prof_enseignement","prof_inter","technicien","agent_maitrise"],
                "Employés":               ["emp_fonction","emp_admin","emp_commerce",
                                           "service_particulier","securite"],
                "Ouvriers":               ["ouvrier","conducteur","cariste"],
                "Inactifs / Retraités":   ["retraites_inactifs","chomeur"],
            }

            def agg_csp(df_src):
                return {grp: df_src[[c for c in cols_csp if any(kw in c for kw in kws) and c in df_src.columns]].sum().sum()
                        for grp, kws in CSP_GROUPES.items()}

            if not comp_csp:
                df_csp_m = df_men_csp[df_men_csp["metropole"]==metro_csp]
                if df_csp_m.empty:
                    st.warning(f"Aucune donnée CSP pour {metro_csp}. Vérifiez le fichier `Menages_csp_nbpers_clean.csv`.")
                else:
                    tot_csp = agg_csp(df_csp_m)
                    df_cp = pd.DataFrame(list(tot_csp.items()), columns=["CSP","Ménages"])
                    df_cp = df_cp[df_cp["Ménages"]>0].sort_values("Ménages", ascending=False)
                    c1,c2 = st.columns(2)
                    with c1:
                        st.markdown(f"##### Ménages par CSP — {metro_csp}")
                        fig_cp = px.bar(df_cp, x="Ménages", y="CSP", orientation="h",
                                        color="Ménages", color_continuous_scale="Greens", text_auto=".0f")
                        fig_cp.update_layout(yaxis={"autorange":"reversed"},
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
                    df_m = df_men_csp[df_men_csp["metropole"]==m]
                    tot = agg_csp(df_m)
                    total_m = sum(tot.values())
                    for grp, val in tot.items():
                        rows_c.append({"Métropole":m,"CSP":grp,
                                       "Part (%)": (val/total_m*100) if total_m>0 else 0})
                fig_comp = px.bar(pd.DataFrame(rows_c), x="Métropole", y="Part (%)",
                                  color="CSP", barmode="stack",
                                  color_discrete_sequence=px.colors.sequential.Greens_r)
                fig_comp.update_layout(yaxis_title="Part des ménages (%)",
                                       legend=dict(orientation="h", y=1.1, font_size=10))
                st.plotly_chart(style(fig_comp, 50), use_container_width=True)

# ==============================================================================
# ONGLET 5 — CSP COMPARATIF
# ==============================================================================
if vue == "Démographie":
    with tab6:
        st.markdown('<p class="section-header">CSP comparatif</p>', unsafe_allow_html=True)
        if df_csp_cmp.empty or ("ANNEE" not in df_csp_cmp.columns):
            st.info("Données CSP comparatif non trouvées dans les fichiers `population_2554`.")
        else:
            annees = sorted(df_csp_cmp["ANNEE"].dropna().unique(), reverse=True)
            if not annees:
                st.info("Aucune année CSP disponible.")
            else:
                with st.sidebar:
                    st.markdown("---")
                    st.markdown("### Filtres CSP comparatif")
                    sel_annee = st.selectbox("📅 Choisir l'année", annees, key="csp_cmp_year")
                    mode = st.selectbox("🎯 Niveau d'analyse", ["Comparatif Communes (Isère)", "Comparatif Métropoles"], key="csp_cmp_mode")

                df_y = df_csp_cmp[df_csp_cmp["ANNEE"] == sel_annee]
                if mode == "Comparatif Communes (Isère)":
                    clist = sorted(COMMUNES["Grenoble"])
                    with st.sidebar:
                        ent_a = st.selectbox("Commune A (Référence)", clist, index=clist.index("Grenoble"), key="csp_cmp_com_a")
                        ent_b = st.selectbox("Commune B (Comparaison)", clist, index=clist.index("Saint-Martin-d'Hères"), key="csp_cmp_com_b")
                    target_a = df_y[(df_y["DEP"] == "38") & (df_y["LIB_NORM"] == normalize_csp_name(ent_a))]
                    target_b = df_y[(df_y["DEP"] == "38") & (df_y["LIB_NORM"] == normalize_csp_name(ent_b))]
                else:
                    met_list = list(DEP_MAP.keys())
                    with st.sidebar:
                        ent_a = st.selectbox("Métropole A", met_list, index=0, key="csp_cmp_met_a")
                        ent_b = st.selectbox("Métropole B", met_list, index=4, key="csp_cmp_met_b")

                    def get_agg(name):
                        dep = DEP_MAP[name]
                        comm_norm = [normalize_csp_name(c) for c in COMMUNES[name]]
                        return df_y[(df_y["DEP"] == dep) & (df_y["LIB_NORM"].isin(comm_norm))].sum(numeric_only=True).to_frame().T

                    target_a, target_b = get_agg(ent_a), get_agg(ent_b)

                with st.sidebar:
                    sel_csp = st.multiselect("📂 Catégories CSP à afficher", list(CSP_MAP.values()), default=list(CSP_MAP.values()), key="csp_cmp_multi")

                if sel_csp and (not target_a.empty) and (not target_b.empty):
                    val_a = target_a[sel_csp].sum(axis=1).values[0]
                    val_b = target_b[sel_csp].sum(axis=1).values[0]
                    st.title(f"📊 {ent_a} vs {ent_b} • {sel_annee}")

                    k1, k2, k3, k4 = st.columns(4)
                    k1.metric(f"Actifs {ent_a}", f"{int(val_a):,}".replace(",", " "))
                    k2.metric(f"Actifs {ent_b}", f"{int(val_b):,}".replace(",", " "))
                    k3.metric("Écart brut", f"{int(val_a - val_b):+,}".replace(",", " "))
                    k4.metric("Indice de masse", f"{(val_a / val_b) if val_b != 0 else 0:.2f}x")

                    col_left, col_right = st.columns(2)
                    with col_left:
                        fig_bar = go.Figure()
                        fig_bar.add_trace(go.Bar(x=sel_csp, y=target_a[sel_csp].iloc[0], name=ent_a, marker_color="#3498db"))
                        fig_bar.add_trace(go.Bar(x=sel_csp, y=target_b[sel_csp].iloc[0], name=ent_b, marker_color="#e67e22"))
                        fig_bar.update_layout(barmode="group", template="plotly_white", height=400)
                        st.plotly_chart(fig_bar, use_container_width=True)
                    with col_right:
                        pct_a = (target_a[sel_csp].iloc[0] / val_a * 100) if val_a != 0 else 0
                        pct_b = (target_b[sel_csp].iloc[0] / val_b * 100) if val_b != 0 else 0
                        fig_radar = go.Figure()
                        fig_radar.add_trace(go.Scatterpolar(r=pct_a, theta=sel_csp, fill="toself", name=ent_a, line_color="#3498db"))
                        fig_radar.add_trace(go.Scatterpolar(r=pct_b, theta=sel_csp, fill="toself", name=ent_b, line_color="#e67e22"))
                        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, max(max(pct_a), max(pct_b), 1) + 5])), template="plotly_white", height=400)
                        st.plotly_chart(fig_radar, use_container_width=True)

                    st.subheader("🎯 Analyse de Spécialisation")
                    spec_index = (pct_a / pct_b * 100).fillna(100)
                    fig_spec = px.bar(x=sel_csp, y=spec_index, labels={"x": "Catégorie", "y": "Indice de spécificité (%)"}, color=spec_index, color_continuous_scale="RdYlGn")
                    fig_spec.add_hline(y=100, line_dash="dash", line_color="black")
                    st.plotly_chart(fig_spec, use_container_width=True)

                    with st.expander("📄 Voir le tableau de données complet"):
                        table_df = pd.DataFrame({
                            "Catégorie CSP": sel_csp,
                            f"{ent_a} (Effectif)": target_a[sel_csp].iloc[0].values,
                            f"{ent_b} (Effectif)": target_b[sel_csp].iloc[0].values,
                            "Différence": target_a[sel_csp].iloc[0].values - target_b[sel_csp].iloc[0].values,
                        })
                        st.table(table_df.style.format(precision=0))
                else:
                    st.warning("Sélectionne des catégories CSP et une comparaison valide.")

# ==============================================================================
# ONGLET 5 — SOLIDARITE & CITOYENNETE
# ==============================================================================
if vue == "Solidarité et citoyenneté":
    st.markdown('<p class="section-header">solidarite&citoyennete</p>', unsafe_allow_html=True)
    s1, s2, s3, s4, s5 = st.tabs(["solidarite", "education", "sante", "participation_citoyenne", "data_base"])

    with s1:
        st.subheader("Analyse CAF - 5 Métropoles")
        if df_caf is None or df_caf.empty:
            st.info("📂 Fichier `CAF_5_Metropoles.csv` introuvable dans `solidarite&citoyennete/data_clean/solidarite/`.")
        else:
            required_cols = {"Annee", "Agglomeration"}
            if not required_cols.issubset(set(df_caf.columns)):
                st.error("Le fichier CAF doit contenir au minimum les colonnes `Annee` et `Agglomeration`.")
            else:
                metric_candidates = [
                    "Nombre foyers NDUR", "Nombre personnes NDUR", "Montant total NDUR",
                    "Nombre foyers NDURPAJE", "Nombre personnes NDURPAJE", "Montant total NDURPAJE",
                    "Nombre foyers NDURINS", "Nombre personnes NDURINS", "Montant total NDURINS",
                ]
                metrics = [c for c in metric_candidates if c in df_caf.columns]
                if not metrics:
                    st.warning("Aucune mesure CAF standard trouvée.")
                else:
                    c1, c2 = st.columns(2)
                    with c1:
                        metric = st.selectbox("Indicateur CAF", metrics, index=0)
                    with c2:
                        years = sorted(df_caf["Annee"].dropna().unique())
                        year = st.selectbox("Année", years, index=len(years) - 1)

                    df_caf[metric] = pd.to_numeric(df_caf[metric], errors="coerce").fillna(0)

                    k1, k2, k3 = st.columns(3)
                    k1.metric(f"Total {metric} ({year})", f"{df_caf[df_caf['Annee'] == year][metric].sum():,.0f}".replace(",", " "))
                    k2.metric("Agglomérations", int(df_caf["Agglomeration"].nunique()))
                    k3.metric("Communes (année)", int(df_caf[df_caf["Annee"] == year]["Nom_Commune"].nunique()) if "Nom_Commune" in df_caf.columns else 0)

                    a, b = st.columns(2)
                    with a:
                        by_agg = df_caf[df_caf["Annee"] == year].groupby("Agglomeration", as_index=False)[metric].sum().sort_values(metric, ascending=False)
                        fig1 = px.bar(by_agg, x="Agglomeration", y=metric, color="Agglomeration", title=f"{metric} en {year}")
                        fig1.update_layout(showlegend=False)
                        st.plotly_chart(style(fig1), use_container_width=True)
                    with b:
                        evo = df_caf.groupby(["Annee", "Agglomeration"], as_index=False)[metric].sum().sort_values("Annee")
                        fig2 = px.line(evo, x="Annee", y=metric, color="Agglomeration", markers=True, title=f"Évolution de {metric}")
                        st.plotly_chart(style(fig2), use_container_width=True)

    with s2:
        st.info("Page `education` prête à brancher sur les fichiers de `solidarite&citoyennete/data_clean/education`.")
    with s3:
        st.info("Page `sante` prête à brancher sur les fichiers de `solidarite&citoyennete/data_clean/sante`.")
    with s4:
        st.info("Page `participation_citoyenne` prête à brancher sur les fichiers de `solidarite&citoyennete/data_clean/participation_citoyenne`.")
    with s5:
        st.info("Page `data_base` prête à brancher sur les fichiers de `solidarite&citoyennete/data_base`.")

# ──────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#9AB8A7;font-size:0.72rem'>"
    "Données INSEE · Recensements de la Population 2011, 2016, 2022 · "
    "Mobilités scolaires et professionnelles 2019–2022</p>",
    unsafe_allow_html=True,
)
