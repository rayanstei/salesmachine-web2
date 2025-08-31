import streamlit as st
import pandas as pd
import random
from io import BytesIO

try:
    import salesmachine_validator_corrige
    GOOGLE_SEARCH_OK = True
except ImportError:
    GOOGLE_SEARCH_OK = False

# === DATA : Générateur de secteurs, par catégories et sous-catégories ===
SECTEURS_PAR_CATEGORIE = {
    "Industrie": {
        "Fabrication métallique": [
            "Fabricants de palettes métalliques",
            "Ateliers de chaudronnerie",
            "Entreprises de soudure industrielle",
            "Fabricants de grillages",
            "Ateliers de tôlerie fine",
            "Fabricants de structures métalliques",
            "Entreprises de découpe laser",
            "Ateliers d'usinage de précision"
        ],
        "Fabrication bois": [
            "Fabricants de palettes bois",
            "Menuiseries industrielles",
            "Fabricants d'emballages bois",
            "Scieries industrielles",
            "Fabricants de caisses bois",
            "Entreprises de traitement du bois",
            "Fabricants de panneaux bois",
            "Ateliers d'ébénisterie industrielle"
        ],
        "Plastique & Polymères": [
            "Fabricants d'emballages plastiques",
            "Entreprises d'injection plastique",
            "Fabricants de films plastiques",
            "Ateliers de thermoformage",
            "Fabricants de tuyaux plastiques",
            "Entreprises d'extrusion plastique",
            "Fabricants de contenants plastiques",
            "Recycleurs de plastiques"
        ],
        "Électronique & Composants": [
            "Fabricants de circuits imprimés",
            "Assembleurs de composants électroniques",
            "Fabricants de connecteurs",
            "Entreprises de câblage industriel",
            "Fabricants de capteurs",
            "Intégrateurs de systèmes électroniques",
            "Fabricants d'éclairage LED",
            "Entreprises d'automatisation"
        ]
    },
    "Services B2B": {
        "Maintenance & Réparation": [
            "Maintenance de machines-outils",
            "Réparation d'équipements industriels",
            "Maintenance d'ascenseurs",
            "Dépannage de systèmes informatiques",
            "Maintenance de climatisation",
            "Réparation de compresseurs",
            "Maintenance de véhicules industriels",
            "Services de maintenance préventive"
        ],
        "Nettoyage & Hygiène": [
            "Nettoyage de bureaux",
            "Nettoyage industriel",
            "Services de décontamination",
            "Nettoyage de vitres en hauteur",
            "Entretien d'espaces verts",
            "Nettoyage de sols techniques",
            "Désinfection professionnelle",
            "Nettoyage après sinistre"
        ],
        "Conseil & Expertise": [
            "Conseil en informatique",
            "Bureaux d'études techniques",
            "Audit énergétique",
            "Conseil en organisation",
            "Expertise comptable",
            "Conseil en sécurité",
            "Formation professionnelle",
            "Conseil en qualité"
        ],
        "Sécurité & Surveillance": [
            "Gardiennage de sites",
            "Sécurité événementielle",
            "Installation d'alarmes",
            "Télésurveillance",
            "Transport de fonds",
            "Protection rapprochée",
            "Sécurité incendie",
            "Contrôle d'accès"
        ]
    },
    "BTP & Construction": {
        "Gros œuvre": [
            "Entreprises de terrassement",
            "Maçonnerie générale",
            "Construction métallique",
            "Béton armé",
            "Fondations spéciales",
            "Démolition industrielle",
            "Travaux publics",
            "Construction modulaire"
        ],
        "Second œuvre": [
            "Électricité industrielle",
            "Plomberie industrielle",
            "Installation de chauffage",
            "Climatisation industrielle",
            "Isolation thermique",
            "Cloisons sèches",
            "Faux plafonds",
            "Revêtements de sols"
        ],
        "Spécialités": [
            "Étanchéité industrielle",
            "Couverture industrielle",
            "Bardage métallique",
            "Menuiserie aluminium",
            "Vitrerie industrielle",
            "Ascensoristes",
            "Automatismes de bâtiment",
            "Sécurité incendie"
        ]
    },
    "Transport & Logistique": {
        "Transport spécialisé": [
            "Transport de matières dangereuses",
            "Transport frigorifique",
            "Transport exceptionnel",
            "Transport de véhicules",
            "Déménagement industriel",
            "Transport de déchets",
            "Transport express",
            "Transport international"
        ],
        "Logistique": [
            "Entreposage sous douane",
            "Préparation de commandes",
            "Cross-docking",
            "Logistique e-commerce",
            "Stockage frigorifique",
            "Gestion d'inventaires",
            "Emballage industriel",
            "Distribution dernière mile"
        ]
    },
    "Commerce Spécialisé": {
        "Équipements industriels": [
            "Distributeurs de machines-outils",
            "Fournisseurs d'outillage professionnel",
            "Négoce de matériel de manutention",
            "Commerce d'équipements de soudage",
            "Distributeurs de compresseurs",
            "Fournisseurs d'EPI",
            "Commerce de matériel électrique",
            "Distributeurs de pompes industrielles"
        ],
        "Matières premières": [
            "Négoce de métaux",
            "Distribution de produits chimiques",
            "Commerce de bois industriel",
            "Fournisseurs de plastiques",
            "Négoce de tissus techniques",
            "Distribution de composants",
            "Commerce de quincaillerie",
            "Fournisseurs d'abrasifs"
        ]
    }
}

def analyser_opportunites(data):
    try:
        df_crm = data['crm']
        df_ape = data['ape']
        total_crm = len(df_crm)
        secteur_mapping = {}
        if 'code_ape_mappe' in df_crm.columns and 'secteur_cible' in df_crm.columns:
            for _, row in df_crm.iterrows():
                code = row.get('code_ape_mappe')
                secteur = row.get('secteur_cible')
                if code and secteur:
                    secteur_mapping[code] = secteur

        ape_count = {}
        for _, row in df_crm.iterrows():
            code = row.get('code_ape') or row.get('code_ape_mappe')
            if code:
                ape_count[code] = ape_count.get(code, 0) + 1

        secteurs_metrics = []
        for _, row in df_ape.iterrows():
            code = row['code']
            libelle = row['libelle']
            secteur_cible = secteur_mapping.get(code, 'Autre')
            nb_crm = ape_count.get(code, 0)
            couverture = (nb_crm / total_crm) * 100 if total_crm else 0
            secteurs_metrics.append({
                "title": libelle,
                "code": code,
                "couverture": round(couverture, 1),
                "nb_crm": nb_crm,
                "secteur": secteur_cible,
            })
        def classify_couverture(couv):
            if couv <= 2:
                return "très faible"
            elif couv <= 8:
                return "partiel"
            return "fort"
        secteurs_by_cat = {"très faible": [], "partiel": [], "fort": []}
        for s in secteurs_metrics:
            cat = classify_couverture(s["couverture"])
            secteurs_by_cat[cat].append(s)
        return secteurs_by_cat, total_crm
    except Exception as e:
        st.warning(f"Erreur analyse IA Insights : {e}")
        return {"très faible": [], "partiel": [], "fort": []}, 0

def lancer_recherche_entreprises(secteur, limit=10):
    if GOOGLE_SEARCH_OK:
        try:
            return salesmachine_validator_corrige.lancer_recherche_entreprises_corrigee(secteur, limit)
        except Exception as e:
            st.error(f"Erreur lors de la prospection Google CSE : {e}")
            return []
    else:
        st.warning("Module de prospection Google non disponible.")
        return []

def module_ia_insights(data):
    st.markdown("## 🧠 IA Insights – Analyse sectorielle intelligente")

    # ---- Vue standard IA Insights ----
    secteurs_by_cat, total_crm = analyser_opportunites(data)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Secteurs spécialisés", len(secteurs_by_cat["très faible"]))
    with col2:
        st.metric("Secteurs prometteurs", len(secteurs_by_cat["partiel"]))
    with col3:
        st.metric("Secteurs saturés", len(secteurs_by_cat["fort"]))
    with col4:
        st.metric("Entreprises CRM", total_crm)

    onglets = st.tabs(["📊 Répartition des secteurs", "✨ Nouvelles idées – Générateur"])
    # --- Onglet Répartition sectorielle classique ---
    with onglets[0]:
        tabs = st.tabs(["Spécialisés (0-2%)", "Prometteurs (2-8%)", "Saturés (8%+)"])
        cats = ["très faible", "partiel", "fort"]
        for idx, cat in enumerate(cats):
            with tabs[idx]:
                st.write(f"**{len(secteurs_by_cat[cat])} secteurs**")
                if secteurs_by_cat[cat]:
                    df = pd.DataFrame(secteurs_by_cat[cat])
                    st.dataframe(df[["title", "couverture", "nb_crm", "secteur"]], use_container_width=True)
                else:
                    st.info("Aucun secteur trouvé pour cette catégorie.")
    # --- Onglet Générateur d'idées ---
    with onglets[1]:
        st.markdown("### 💡 Générateur de nouveaux secteurs à prospecter")
        # Pour éviter de mélanger à chaque rafraîchissement
        if "secteurs_shuffle" not in st.session_state:
            st.session_state.secteurs_shuffle = {cat: {scat: list(lst) for scat, lst in sous.items()} for cat, sous in SECTEURS_PAR_CATEGORIE.items()}
            st.session_state.current_cat = list(SECTEURS_PAR_CATEGORIE.keys())[0]
            st.session_state.prospection_results = {}  # Pour stocker les résultats de prospection

        col_gen1, col_gen2 = st.columns([1,3])
        with col_gen1:
            st.markdown("**Catégories**")
            for cat in SECTEURS_PAR_CATEGORIE.keys():
                if st.button(cat, key=f"cat_{cat}"):
                    st.session_state.current_cat = cat
        with col_gen2:
            cat = st.session_state.current_cat
            st.markdown(f"#### {cat}")
            st.write("Clique sur 'Nouvelles idées' pour mélanger les suggestions de chaque sous-catégorie.")
            if st.button("✨ Nouvelles idées", key="shuffle"):
                for scat in st.session_state.secteurs_shuffle[cat]:
                    random.shuffle(st.session_state.secteurs_shuffle[cat][scat])
                st.success("Propositions mélangées !")
            sous_cat = st.session_state.secteurs_shuffle[cat]
            for sous, metiers in sous_cat.items():
                with st.expander(f"**{sous}** ({len(metiers)})", expanded=True):
                    cols = st.columns(2)
                    for idx, m in enumerate(metiers):
                        with cols[idx%2]:
                            st.markdown(f"- {m}")
                            prospect_key = f"{cat}_{sous}_{m}_prospect"
                            if st.button(f"Prospecter : {m}", key=prospect_key):
                                with st.spinner(f"Recherche Google CSE pour « {m} »..."):
                                    results = lancer_recherche_entreprises(m, limit=10)
                                    st.session_state.prospection_results[prospect_key] = results
                            # Affichage résultats si disponibles
                            if prospect_key in st.session_state.prospection_results:
                                results = st.session_state.prospection_results[prospect_key]
                                if results:
                                    st.success(f"{len(results)} entreprises trouvées pour {m}")
                                    dfresults = pd.DataFrame(results)
                                    st.dataframe(dfresults, use_container_width=True)
                                    # Export Excel
                                    buffer = BytesIO()
                                    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                                        dfresults.to_excel(writer, index=False)
                                    st.download_button(
                                        "📊 Télécharger résultats",
                                        buffer.getvalue(),
                                        f"prospection_{m}.xlsx",
                                        "application/vnd.ms-excel"
                                    )
                                else:
                                    st.warning("Aucun résultat trouvé.")

    st.write("### 📝 Suggestions d’amélioration")
    st.info("- Ajoutez ici vos graphes Plotly ou analyses IA avancées selon vos besoins.")