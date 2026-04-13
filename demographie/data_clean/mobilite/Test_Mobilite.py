import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# =================================================================
# 1. CONFIGURATION ET DESIGN
# =================================================================
st.set_page_config(page_title="Observatoire des Mobilités", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    .main .block-container { font-family: 'Inter', sans-serif; color: #2c3e50; }
    
    .kpi-card {
        background-color: white; padding: 20px; border-radius: 12px;
        border-top: 5px solid #3498db; box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        text-align: center; margin-bottom: 10px;
    }
    .kpi-label { font-size: 11px; font-weight: 700; color: #7f8c8d; text-transform: uppercase; letter-spacing: 0.5px;}
    .kpi-value { font-size: 24px; font-weight: 800; color: #2c3e50; margin: 5px 0; }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# 2. RÉFÉRENTIELS COMPLETS
# =================================================================
METROPOLES_DEF = {
    "Grenoble": ["Bresson","Brié-et-Angonnes","Champ-sur-Drac","Champagnier","Claix","Corenc","Domène","Échirolles","Eybens","Fontaine","Fontanil-Cornillon","Gières","Grenoble","Herbeys","Jarrie","La Tronche","Le Gua","Le Pont-de-Claix","Le Sappey-en-Chartreuse","Meylan","Miribel-Lanchâtre","Mont-Saint-Martin","Montchaboud","Murianette","Notre-Dame-de-Commiers","Notre-Dame-de-Mésage","Noyarey","Poisat","Proveysieux","Quaix-en-Chartreuse","Saint-Barthélemy-de-Séchilienne","Saint-Égrève","Saint-Georges-de-Commiers","Saint-Martin-d'Hères","Saint-Martin-le-Vinoux","Saint-Paul-de-Varces","Saint-Pierre-de-Mésage","Sarcenas","Sassenage","Séchilienne","Seyssinet-Pariset","Seyssins","Varces-Allières-et-Risset","Vaulnaveys-le-Bas","Vaulnaveys-le-Haut","Venon","Veurey-Voroize","Vif","Vizille"],
    "Rennes": ["Acigné","Bécherel","Betton","Bourgbarré","Brécé","Bruz","Cesson-Sévigné","Chantepie","Chartres-de-Bretagne","Chavagne","Chevaigné","Cintré","Corps-Nuds","Gévezé","La Chapelle-des-Fougeretz","La Chapelle-Thouarault","L'Hermitage","Le Rheu","Le Verger","Montgermont","Mordelles","Noyal-Châtillon-sur-Seiche","Nouvoitou","Orgères","Pacé","Parthenay-de-Bretagne","Pont-Péan","Rennes","Romillé","Saint-Armel","Saint-Erblon","Saint-Gilles","Saint-Grégoire","Saint-Jacques-de-la-Lande","Saint-Sulpice-la-Forêt","Thorigné-Fouillard","Vern-sur-Seiche","Vezin-le-Coquet","Clayes","La Chapelle-Chaussée","Laillé","Langan","Miniac-sous-Bécherel"],
    "Rouen": ["Amfreville-la-Mi-Voie","Anneville-Ambourville","Bardouville","Belbeuf","Berville-sur-Seine","Bihorel","Bois-Guillaume","Bonsecours","Boos","Canteleu","Caudebec-lès-Elbeuf","Cléon","Darnétal","Déville-lès-Rouen","Duclair","Elbeuf","Épinay-sur-Duclair","Fontaine-sous-Préaux","Franqueville-Saint-Pierre","Freneuse","Gouy","Grand-Couronne","Hautot-sur-Seine","Hénouville","Houppeville","Isneauville","Jumièges","La Bouille","La Londe","La Neuville-Chant-d'Oisel","Le Grand-Quevilly","Le Houlme","Le Mesnil-Esnard","Le Mesnil-sous-Jumièges","Le Petit-Quevilly","Le Trait","Les Authieux-sur-Port-Saint-Ouen","Malaunay","Maromme","Mont-Saint-Aignan","Montmain","Moulineaux","Notre-Dame-de-Bondeville","Oissel","Orival","Petit-Couronne","Quevillon","Quévreville-la-Poterie","Roncherolles-sur-le-Vivier","Rouen","Sahurs","Saint-Aubin-Celloville","Saint-Aubin-Épinay","Saint-Aubin-lès-Elbeuf","Saint-Étienne-du-Rouvray","Saint-Jacques-sur-Darnétal","Saint-Léger-du-Bourg-Denis","Saint-Martin-de-Boscherville","Saint-Martin-du-Vivier","Saint-Paër","Saint-Pierre-de-Manneville","Saint-Pierre-de-Varengeville","Saint-Pierre-lès-Elbeuf","Sainte-Marguerite-sur-Duclair","Sotteville-lès-Rouen","Sotteville-sous-le-Val","Tourville-la-Rivière","Val-de-la-Haye","Yainville","Ymare","Yville-sur-Seine"],
    "Saint-Étienne": ["Aboën","Andrézieux-Bouthéon","Caloire","Cellieu","Chagnon","Chambœuf","Châteauneuf","Dargoire","Doizieux","Farnay","Firminy","Fontanès","Fraisses","Genilac","L'Étrat","L'Horme","La Fouillouse","La Gimond","La Grand-Croix","La Ricamarie","La Talaudière","La Terrasse-sur-Dorlay","La Tour-en-Jarez","La Valla-en-Gier","Le Chambon-Feugerolles","Lorette","Marcenod","Pavezin","Rive-de-Gier","Roche-la-Molière","Rozier-Côtes-d'Aurec","Saint-Bonnet-les-Oules","Saint-Chamond","Saint-Christo-en-Jarez","Saint-Étienne","Saint-Galmier","Saint-Genest-Lerpt","Saint-Héand","Saint-Jean-Bonnefonds","Saint-Joseph","Saint-Martin-la-Plaine","Saint-Maurice-en-Gourgois","Saint-Nizier-de-Fornas","Saint-Paul-en-Cornillon","Saint-Paul-en-Jarez","Saint-Priest-en-Jarez","Saint-Romain-en-Jarez","Sainte-Croix-en-Jarez","Sorbiers","Tartaras","Unieux","Valfleury","Villars"],
    "Montpellier": ["Baillargues","Beaulieu","Castelnau-le-Lez","Castries","Clapiers","Cournonsec","Cournonterral","Fabrègues","Grabels","Jacou","Juvignac","Lattes","Lavérune","Le Crès","Montaud","Montferrier-sur-Lez","Montpellier","Murviel-lès-Montpellier","Pérols","Pignan","Prades-le-Lez","Restinclières","Saint-Brès","Saint-Drézéry","Saint-Geniès-des-Mourgues","Saint-Georges-d'Orques","Saint-Jean-de-Védas","Saussan","Sussargues","Vendargues","Villeneuve-lès-Maguelone"]
}

# =================================================================
# 3. CHARGEMENT DES DONNÉES
# =================================================================
@st.cache_data
def load_all_data():
    df_res = pd.read_csv("Migrations_resid_clean.csv")
    df_prof = pd.read_csv("Mobilite_profess_clean.csv")
    df_scol = pd.read_csv("Mobilite_scolaire_clean.csv")
    for df in [df_res, df_prof, df_scol]:
        df['flux'] = pd.to_numeric(df['flux'], errors='coerce').fillna(0)
    return df_res, df_prof, df_scol

df_res, df_prof, df_scol = load_all_data()

# =================================================================
# 4. NAVIGATION LATÉRALE DYNAMIQUE
# =================================================================
with st.sidebar:
    st.header("🔍 Configuration")
    theme = st.selectbox("Thématique d'analyse", [
        "🏠 Migrations Résidentielles", 
        "💼 Mobilité Professionnelle",
        "🎓 Mobilité Scolaire"
    ])
    
    st.markdown("---")
    mode_analyse = st.radio("Niveau géographique", ["Détail Communal", "Comparaison Métropoles"])
    
    # Choix du DataFrame et des labels selon le thème
    if "Migrations" in theme:
        current_df, col_orig, col_dest = df_res, 'commune_origine', 'commune_destination'
        label_in, label_out = "Nouveaux Arrivants", "Départs"
    elif "Professionnelle" in theme:
        current_df, col_orig, col_dest = df_prof, 'commune_residence', 'commune_travail'
        label_in, label_out = "Travailleurs Entrants", "Résidents Sortants"
    else:
        current_df, col_orig, col_dest = df_scol, 'commune_origine', 'commune_destination'
        label_in, label_out = "Élèves/Étudiants Entrants", "Élèves/Étudiants Sortants"

    annee_dispo = sorted(current_df["annee"].unique(), reverse=True)
    sel_annee = st.selectbox("Année", annee_dispo)
    df_filtered = current_df[(current_df[col_orig] != current_df[col_dest]) & (current_df['annee'] == sel_annee)]

    entities_to_plot = []
    
    # --- LOGIQUE DE FILTRAGE EXCLUSIVE ---
    if mode_analyse == "Détail Communal":
        # On choisit d'abord la métropole parente pour filtrer la liste des communes
        met_choice = st.selectbox("Choisir une métropole", list(METROPOLES_DEF.keys()))
        # Ensuite on choisit les communes de cette métropole
        selection = st.multiselect("Communes", sorted(METROPOLES_DEF[met_choice]), default=METROPOLES_DEF[met_choice][:2])
        
        for ent in selection:
            f_in = df_filtered[df_filtered[col_dest] == ent]['flux'].sum()
            f_out = df_filtered[df_filtered[col_orig] == ent]['flux'].sum()
            entities_to_plot.append({"name": ent, "in": f_in, "out": f_out, "solde": f_in - f_out})
            
    else:
        # MODE COMPARAISON MÉTROPOLES : Le filtre communes disparaît totalement
        selection = st.multiselect("Sélectionner les métropoles", list(METROPOLES_DEF.keys()), default=list(METROPOLES_DEF.keys())[:3])
        
        for m_name in selection:
            coms = METROPOLES_DEF[m_name]
            f_in = df_filtered[df_filtered[col_dest].isin(coms)]['flux'].sum()
            f_out = df_filtered[df_filtered[col_orig].isin(coms)]['flux'].sum()
            entities_to_plot.append({"name": m_name, "in": f_in, "out": f_out, "solde": f_in - f_out})

df_plot = pd.DataFrame(entities_to_plot)

# =================================================================
# 5. CORPS PRINCIPAL
# =================================================================
st.title(f"{theme}")
st.markdown(f"**Observatoire des flux - Données Insee {sel_annee}**")

tab_dash, tab_method = st.tabs(["📊 Tableau de Bord Interactif", "📘 Guide & Méthodologie"])

with tab_dash:
    if not df_plot.empty:
        # --- SECTION INDICATEURS (KPIs) ---
        st.subheader("📌 Focus sur le Bilan (Solde Net)")
        cols = st.columns(len(df_plot))
        for i, row in df_plot.iterrows():
            with cols[i]:
                color = "#2ecc71" if row['solde'] >= 0 else "#e74c3c"
                st.markdown(f"""
                    <div class='kpi-card'>
                        <div class='kpi-label'>{row['name']}</div>
                        <div class='kpi-value'>{int(row['solde']):+,d}</div>
                        <div style='color:{color}; font-size:12px; font-weight:bold;'>BILAN NET</div>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("---")

        # --- SECTION GRAPHIQUES ---
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("⚖️ Volume des Échanges")
            fig_vol = go.Figure()
            fig_vol.add_trace(go.Bar(x=df_plot['name'], y=df_plot['in'], name=label_in, marker_color='#3498db'))
            fig_vol.add_trace(go.Bar(x=df_plot['name'], y=df_plot['out'], name=label_out, marker_color='#bdc3c7'))
            fig_vol.update_layout(barmode='group', template="plotly_white", height=380, margin=dict(t=10))
            st.plotly_chart(fig_vol, use_container_width=True)
        
        with c2:
            st.subheader("🎯 Performance Nette")
            fig_net = px.bar(df_plot, x='name', y='solde', color='solde', color_continuous_scale='RdYlGn')
            fig_net.add_hline(y=0, line_dash="dash", line_color="black")
            fig_net.update_layout(template="plotly_white", height=380, margin=dict(t=10))
            st.plotly_chart(fig_net, use_container_width=True)

        st.markdown("---")
        
        # --- SECTION TOP 10 ---
        st.subheader("🔍 Analyse géographique des partenaires")
        # Si détail communal, on regarde les flux des villes choisies. Si métropole, on agrège les villes de la métropole.
        coms_selection = selection if mode_analyse == "Détail Communal" else [c for m in selection for c in METROPOLES_DEF[m]]
        
        col_left, col_right = st.columns(2)
        with col_left:
            st.markdown(f"📍 **Top 10 : Origines ({label_in})**")
            top_in_data = df_filtered[df_filtered[col_dest].isin(coms_selection)].nlargest(10, 'flux')
            fig_in = px.bar(top_in_data, x='flux', y=col_orig, orientation='h', color_discrete_sequence=['#3498db'])
            fig_in.update_layout(yaxis={'categoryorder':'total ascending'}, height=400, template="plotly_white")
            st.plotly_chart(fig_in, use_container_width=True)

        with col_right:
            st.markdown(f"🚩 **Top 10 : Destinations ({label_out})**")
            top_out_data = df_filtered[df_filtered[col_orig].isin(coms_selection)].nlargest(10, 'flux')
            fig_out = px.bar(top_out_data, x='flux', y=col_dest, orientation='h', color_discrete_sequence=['#e67e22'])
            fig_out.update_layout(yaxis={'categoryorder':'total ascending'}, height=400, template="plotly_white")
            st.plotly_chart(fig_out, use_container_width=True)

    else:
        st.warning("⚠️ Veuillez sélectionner des éléments dans le menu à gauche.")

# =================================================================
# 6. ONGLET MÉTHODOLOGIE (VERSION COMPLÈTE)
# =================================================================
with tab_method:
    st.header("📖 Guide d'interprétation")
    st.markdown("""
    ### 1. Les trois thématiques
    * **Migrations Résidentielles :** Répond à la question *"Où les gens ont-ils choisi de déménager ?"*. C'est l'indicateur de la qualité de vie et du logement.
    * **Mobilité Professionnelle :** Répond à la question *"Où les gens travaillent-ils par rapport à leur dodo ?"*. C'est l'indicateur de la force économique.
    * **Mobilité Scolaire :** Répond à la question *"Où les élèves et étudiants vont-ils apprendre ?"*. C'est l'indicateur du rayonnement éducatif (présence de pôles universitaires ou lycées).
    
    ### 2. Comprendre les Graphiques
    * **Barres Groupées (Bleu/Gris) :** Elles montrent la vitalité globale. Beaucoup de mouvements signifient un territoire très dynamique, même si le solde est nul.
    * **Barres de Solde (Rouge/Vert) :** Elles montrent l'équilibre. Une ville "dortoir" aura un solde professionnel très négatif (départs le matin) mais peut-être un solde résidentiel positif (les gens aiment y vivre).
    * **Graphiques Horizontaux (Top 10) :** Ils servent à identifier vos voisins les plus proches en termes d'échanges. Souvent, les flux se font entre communes limitrophes.

    ### 3. Focus sur la Mobilité Scolaire
    * **Entrants :** Élèves ou étudiants qui viennent étudier dans la zone mais dorment ailleurs. Un chiffre élevé indique un pôle d'enseignement majeur.
    * **Sortants :** Jeunes résidant dans la zone qui doivent en sortir pour trouver leur établissement scolaire ou universitaire.

    ### 4. Source des données
    Données Insee issues du Recensement de la Population. Les flux internes (habiter et travailler/étudier dans la même ville) sont exclus pour zoomer sur les relations entre villes.
    """)    