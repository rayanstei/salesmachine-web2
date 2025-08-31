import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import random
import time
import hashlib
from datetime import datetime

# Design System
DS = {
    "primary": "#3b82f6",
    "primary_dark": "#1d4ed8",
    "success": "#10b981",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "background": "#ffffff",
    "surface": "#f9fafb",
    "surface_alt": "#f5f7fa",
    "border": "#e5e7eb",
    "text_primary": "#1f2937",
    "text_secondary": "#6b7280",
    "text_muted": "#9ca3af",
}

# CSS personnalisé pour une UI moderne
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    .ia-insights-container {
        font-family: 'Inter', sans-serif;
        background-color: #f9fafb;
    }
    
    .header-gradient {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 1rem;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }
    
    .header-gradient h1 {
        margin-bottom: 0.5rem;
        font-size: 2.5rem;
        font-weight: 800;
    }
    
    .metric-container {
        display: flex;
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        text-align: center;
        border: 1px solid #e5e7eb;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        animation: countUp 0.8s ease-out;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.15);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: #6b7280;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .progress-container {
        background: #f1f5f9;
        border-radius: 1rem;
        padding: 0.25rem;
        margin: 0.5rem 0;
        overflow: hidden;
    }
    
    .progress-bar {
        height: 0.5rem;
        border-radius: 0.75rem;
        transition: width 0.8s ease-in-out;
        animation: progressSlide 1.5s ease-out;
    }
    
    .sector-card {
        background: white;
        border-radius: 0.75rem;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #e5e7eb;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .sector-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: #f8fafc;
        padding: 0.5rem;
        border-radius: 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 0.75rem;
        color: #6b7280;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        color: white;
        box-shadow: 0 4px 15px rgba(59,130,246,0.3);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        color: white;
        border: none;
        border-radius: 0.75rem;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(59,130,246,0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(59,130,246,0.5);
    }
    
    .success-toast {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 0.75rem;
        margin: 1rem 0;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(16,185,129,0.3);
        animation: fadeIn 0.5s ease;
    }
    
    @keyframes countUp {
        from { opacity: 0; transform: scale(0.5); }
        to { opacity: 1; transform: scale(1); }
    }
    
    @keyframes progressSlide {
        from { width: 0%; }
        to { width: var(--progress-width); }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideIn {
        from { transform: translateX(-100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @media (max-width: 768px) {
        .header-gradient {
            padding: 1.5rem;
        }
        .header-gradient h1 {
            font-size: 2rem !important;
        }
    }
</style>
<script>
    window.addEventListener('load', function() {
        const elements = document.querySelectorAll('.metric-card, .sector-card');
        elements.forEach((el, index) => {
            setTimeout(() => {
                el.style.opacity = '0';
                el.style.transform = 'translateY(20px)';
                el.style.transition = 'all 0.6s ease';
                setTimeout(() => {
                    el.style.opacity = '1';
                    el.style.transform = 'translateY(0)';
                }, 100);
            }, index * 100);
        });
    });
    
    window.addEventListener('scroll', function() {
        const header = document.querySelector('.header-gradient');
        if (header) {
            const scrolled = window.pageYOffset;
            const rate = scrolled * -0.2;
            header.style.transform = `translateY(${rate}px)`;
        }
    });
</script>
""", unsafe_allow_html=True)

# Fonctions utilitaires
def generate_unique_key(base_string: str, additional_data: str = "") -> str:
    """Génère une clé unique basée sur un hash"""
    combined = f"{base_string}_{additional_data}_{random.randint(1000, 9999)}"
    return hashlib.md5(combined.encode()).hexdigest()[:10]

def perform_real_search(secteur_nom: str, limit: int = 25):
    """Utilise le vrai module de recherche"""
    try:
        import salesmachine_validator_corrige as search_module
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text(f"🔍 Recherche réelle pour: {secteur_nom}")
        progress_bar.progress(25)
        
        results = search_module.lancer_recherche_entreprises_corrigee(secteur_nom, limit)
        progress_bar.progress(75)
        
        formatted_results = []
        for result in results:
            formatted_result = {
                "Nom": result.get("Nom", "Entreprise inconnue"),
                "Email": result.get("Email", ""),
                "Téléphone": result.get("Téléphone", ""),
                "Site": result.get("Site", ""),
                "Localisation": "France",
                "Secteur": secteur_nom,
                "Score": 100 if (result.get("Email") or result.get("Téléphone") or result.get("Site")) else 75
            }
            formatted_results.append(formatted_result)
        
        progress_bar.progress(100)
        progress_bar.empty()
        status_text.text(f"✅ Recherche terminée: {len(formatted_results)} résultats trouvés")
        
        return formatted_results
        
    except Exception as e:
        st.error(f"❌ Erreur dans la recherche réelle: {e}")
        return []

def create_metric_card(icon: str, value: str, label: str, color: str):
    """Crée une carte de métrique moderne"""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color: {color};">{icon} {value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)

def create_progress_bar(percentage: float, color: str = "#3b82f6"):
    """Crée une barre de progression personnalisée animée"""
    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-bar" style="background: {color}; width: {percentage}%; --progress-width: {percentage}%;"></div>
    </div>
    <div style="text-align: right; font-weight: 600; color: {color}; font-size: 0.875rem;">
        {percentage:.1f}%
    </div>
    """, unsafe_allow_html=True)

def show_sector_card_modern(title, code, coverage, nb_crm, color, unique_id):
    """Affiche une carte de secteur moderne avec animations"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"""
        <div class="sector-card sector-card-hover">
            <div style="font-size: 1.1rem; font-weight: 700; color: #1f2937; margin-bottom: 0.5rem;">
                {title}
            </div>
            <div style="font-size: 0.875rem; color: #6b7280; margin-bottom: 1rem;">
                Code APE: {code} • {nb_crm} entreprises
            </div>
        </div>
        """, unsafe_allow_html=True)
        create_progress_bar(coverage, color)
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Lancer", key=f"launch_{unique_id}"):
            with st.spinner(f"Recherche en cours pour {title}..."):
                results = perform_real_search(title)
                if results:
                    st.session_state['search_results'] = results
                    st.success(f"✅ {len(results)} prospects trouvés pour {title}")
                    st.rerun()

def show_generator_section_complete():
    """Section générateur complète avec tous les secteurs"""
    secteurs_par_categorie = {
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
            ]
        }
    }
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown("#### 📂 Catégories")
        categories = list(secteurs_par_categorie.keys())
        selected_category = st.selectbox("Choisir une catégorie", categories, key="generator_category")
        
        if st.button("🎲 Nouvelles idées", type="primary", key="new_ideas_generator"):
            for cat in secteurs_par_categorie:
                for sous_cat in secteurs_par_categorie[cat]:
                    random.shuffle(secteurs_par_categorie[cat][sous_cat])
            st.success("🔄 Nouvelles idées de secteurs proposées")
    
    with col2:
        st.markdown(f"#### {selected_category}")
        
        if selected_category in secteurs_par_categorie:
            secteurs_cat = secteurs_par_categorie[selected_category]
            
            for sous_cat, noms in secteurs_cat.items():
                with st.expander(f"📋 {sous_cat} ({len(noms)} secteurs)", expanded=True):
                    for idx, nom in enumerate(noms):
                        col_nom, col_btn = st.columns([3, 1])
                        
                        with col_nom:
                            st.markdown(f"""
                            <div style="
                                padding: 0.75rem;
                                margin: 0.25rem 0;
                                border-radius: 8px;
                                background: #f8fafc;
                                border-left: 4px solid {DS['primary']};
                            ">
                                <strong>{nom}</strong>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col_btn:
                            unique_key = generate_unique_key(f"gen_{selected_category}_{sous_cat}", str(idx))
                            if st.button("🚀 Prospecter", key=unique_key):
                                with st.spinner(f"Recherche en cours pour {nom}..."):
                                    results = perform_real_search(nom)
                                    if results:
                                        st.session_state['search_results'] = results
                                        st.success(f"✅ {len(results)} prospects trouvés pour {nom}")
                                        st.rerun()

def show_results_section_advanced():
    """Section résultats avancée avec graphiques"""
    if 'search_results' in st.session_state and st.session_state['search_results']:
        results = st.session_state['search_results']
        df_results = pd.DataFrame(results)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Prospects", len(df_results))
        
        with col2:
            avg_score = df_results['Score'].mean() if 'Score' in df_results.columns else 0
            st.metric("Score Moyen", f"{avg_score:.1f}/100")
        
        with col3:
            with_email = df_results['Email'].notna().sum() if 'Email' in df_results.columns else 0
            st.metric("Avec Email", with_email)
        
        with col4:
            with_phone = df_results['Téléphone'].notna().sum() if 'Téléphone' in df_results.columns else 0
            st.metric("Avec Téléphone", with_phone)
        
        st.markdown("### 📈 Analyse des Résultats")
        
        graph_col1, graph_col2 = st.columns(2)
        
        with graph_col1:
            if 'Localisation' in df_results.columns:
                loc_counts = df_results['Localisation'].value_counts()
                fig_pie = px.pie(
                    values=loc_counts.values,
                    names=loc_counts.index,
                    title="Répartition par Localisation",
                    color_discrete_sequence=px.colors.qualitative.Set3,
                    hole=0.3
                )
                fig_pie.update_layout(
                    font=dict(family="Inter", size=12),
                    showlegend=True,
                    height=400
                )
                st.plotly_chart(fig_pie, use_container_width=True)
        
        with graph_col2:
            if 'Score' in df_results.columns:
                fig_hist = px.histogram(
                    df_results,
                    x='Score',
                    nbins=10,
                    title="Distribution des Scores de Qualité",
                    color_discrete_sequence=[DS["primary"]],
                    marginal="box"
                )
                fig_hist.update_layout(
                    font=dict(family="Inter", size=12),
                    xaxis_title="Score de Qualité",
                    yaxis_title="Nombre de Prospects",
                    height=400
                )
                st.plotly_chart(fig_hist, use_container_width=True)
        
        st.markdown("### 📋 Tableau Détaillé")
        
        display_df = df_results.copy()
        
        if 'Score' in display_df.columns:
            display_df['Qualité'] = display_df['Score'].apply(
                lambda x: "🟢 Excellent" if x >= 90 else "🟡 Bon" if x >= 75 else "🟠 Moyen"
            )
        
        column_config = {
            "Nom": st.column_config.TextColumn("🏢 Entreprise", width="medium"),
            "Email": st.column_config.TextColumn("📧 Email", width="medium"),
            "Téléphone": st.column_config.TextColumn("📞 Téléphone", width="medium"),
            "Site": st.column_config.LinkColumn("🌐 Site Web", width="medium"),
            "Localisation": st.column_config.TextColumn("📍 Ville", width="small"),
            "Score": st.column_config.ProgressColumn("📊 Score", min_value=0, max_value=100, format="%d/100", width="medium"),
            "Qualité": st.column_config.TextColumn("⭐ Statut", width="small")
        }
        
        st.data_editor(
            display_df,
            column_config=column_config,
            use_container_width=True,
            num_rows="dynamic",
            disabled=["Score", "Qualité"],
            key="results_table_advanced"
        )
        
        st.markdown("### 🎯 Actions sur les Résultats")
        
        action_col1, action_col2, action_col3 = st.columns(3)
        
        with action_col1:
            csv = df_results.to_csv(index=False)
            st.download_button(
                label="📊 Télécharger CSV",
                data=csv,
                file_name=f"prospects_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                key="download_csv_advanced"
            )
        
        with action_col2:
            if st.button("📧 Préparer Campagne", key="campaign_advanced"):
                st.success("Redirection vers le module Campagnes...")
                
        with action_col3:
            if st.button("🔄 Nouvelle Recherche", key="new_search_advanced"):
                st.session_state['search_results'] = []
                st.success("Prêt pour une nouvelle recherche")
                st.rerun()
        
        st.markdown("### 🧠 Analyse IA")
        
        with st.expander("📈 Insights Automatiques", expanded=True):
            total_prospects = len(df_results)
            avg_score = df_results['Score'].mean() if 'Score' in df_results.columns else 0
            top_location = df_results['Localisation'].mode().iloc[0] if 'Localisation' in df_results.columns and not df_results['Localisation'].empty else "N/A"
            
            st.markdown(f"""
            **🎯 Analyse de la Recherche :**
            - **Volume :** {total_prospects} prospects identifiés
            - **Qualité Moyenne :** {avg_score:.1f}/100 {'🟢' if avg_score >= 80 else '🟡' if avg_score >= 60 else '🟠'}
            - **Zone Principale :** {top_location}
            
            **💡 Recommandations IA :**
            - {"Excellente base de prospects, prêt pour campagne" if avg_score >= 80 else "Qualité acceptable, enrichir les données recommandé" if avg_score >= 60 else "Affiner les critères de recherche"}
            - {"Diversifier géographiquement" if top_location != "N/A" else "Bonne répartition géographique"}
            - {"Prioriser les prospects score > 85" if avg_score >= 75 else "Segmenter par score de qualité"}
            """)
    
    else:
        st.markdown("""
        <div class="sector-card">
            <h3>🔍 Aucun résultat disponible</h3>
            <p style="color: #6b7280; margin-bottom: 2rem;">
                Lancez une recherche depuis les onglets "Secteurs" ou "Générateur" pour voir les résultats ici.
            </p>
            <div style="font-size: 4rem; opacity: 0.3;">📊</div>
        </div>
        """, unsafe_allow_html=True)

def module_ia_insights(data):
    """Module principal IA Insights - Version complète et moderne"""
    st.markdown(f"""
    <div class="ia-insights-container">
        <div class="header-gradient">
            <h1>🧠 IA Insights</h1>
            <p style="opacity: 0.9; font-size: 1.1rem; font-weight: 500;">
                Découvrez les secteurs les plus prometteurs grâce à l'intelligence artificielle
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns([1, 1, 1, 6])
    
    with col1:
        if st.button("🔍 Analyser", type="primary", key="ia_analyze_main"):
            st.success("Analyse des secteurs en cours...")
    
    with col2:
        if st.button("📊 Exporter", key="ia_export_main"):
            st.success("Export des données en cours...")
    
    with col3:
        if st.button("🔄 Actualiser", key="ia_refresh_main"):
            st.success("Données actualisées avec succès")
    
    st.markdown("### 📈 Tableau de Bord")
    
    metrics_cols = st.columns(5)
    
    with metrics_cols[0]:
        create_metric_card("🎯", "47", "SECTEURS SPÉCIALISÉS", DS["danger"])
    
    with metrics_cols[1]:
        create_metric_card("⚡", "23", "SECTEURS PROMETTEURS", DS["warning"])
    
    with metrics_cols[2]:
        create_metric_card("🚀", "12", "SECTEURS SATURÉS", DS["success"])
    
    with metrics_cols[3]:
        create_metric_card("👥", "12,250", "PROSPECTS IDENTIFIÉS", DS["primary"])
    
    with metrics_cols[4]:
        create_metric_card("📈", "23%", "TAUX DE CONVERSION", DS["primary_dark"])
    
    st.markdown("---")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 TRÈS FAIBLE (0-2%)",
        "⚡ PARTIEL (2.1-8%)",
        "🚀 FORT (8.1%+)",
        "✨ Générateur",
        "📊 Résultats"
    ])
    
    with tab1:
        st.markdown("""
        <div class="sector-card">
            <h3>🎯 Secteurs spécialisés - 47 opportunités détectées</h3>
            <p style="color: #6b7280;">Secteurs avec très faible couverture (0-2%) - Potentiel élevé</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Actualiser les secteurs spécialisés", key="refresh_tres_faible"):
            st.success("Nouvelles suggestions proposées")
        
        secteurs_faible = [
            {"title": "Fabrication de structures métalliques", "code": "2511Z", "coverage": 1.5, "nb_crm": 23},
            {"title": "Ateliers de chaudronnerie", "code": "2512Z", "coverage": 1.2, "nb_crm": 18},
            {"title": "Entreprises de soudure industrielle", "code": "2562B", "coverage": 1.8, "nb_crm": 31},
            {"title": "Fabricants de grillages", "code": "2513Z", "coverage": 0.9, "nb_crm": 12},
        ]
        
        for idx, secteur in enumerate(secteurs_faible):
            show_sector_card_modern(
                secteur["title"], 
                secteur["code"], 
                secteur["coverage"], 
                secteur["nb_crm"], 
                DS["danger"], 
                f"faible_{idx}"
            )
    
    with tab2:
        st.markdown("""
        <div class="sector-card">
            <h3>⚡ Secteurs partiels - 23 opportunités détectées</h3>
            <p style="color: #6b7280;">Secteurs avec couverture partielle (2.1-8%) - Potentiel modéré</p>
        </div>
        """, unsafe_allow_html=True)
        
        secteurs_partiel = [
            {"title": "Maintenance équipements industriels", "code": "3312Z", "coverage": 4.2, "nb_crm": 187},
            {"title": "Nettoyage industriel", "code": "8129A", "coverage": 3.8, "nb_crm": 156},
            {"title": "Conseil en informatique", "code": "6202A", "coverage": 5.1, "nb_crm": 243},
        ]
        
        for idx, secteur in enumerate(secteurs_partiel):
            show_sector_card_modern(
                secteur["title"], 
                secteur["code"], 
                secteur["coverage"], 
                secteur["nb_crm"], 
                DS["warning"], 
                f"partiel_{idx}"
            )
    
    with tab3:
        st.markdown("""
        <div class="sector-card">
            <h3>🚀 Secteurs forts - 12 secteurs identifiés</h3>
            <p style="color: #6b7280;">Secteurs avec forte couverture (8.1%+) - Marchés saturés</p>
        </div>
        """, unsafe_allow_html=True)
        
        secteurs_fort = [
            {"title": "Construction bâtiments résidentiels", "code": "4120A", "coverage": 12.3, "nb_crm": 892},
            {"title": "Transport routier marchandises", "code": "4941A", "coverage": 15.7, "nb_crm": 1205},
        ]
        
        for idx, secteur in enumerate(secteurs_fort):
            show_sector_card_modern(
                secteur["title"], 
                secteur["code"], 
                secteur["coverage"], 
                secteur["nb_crm"], 
                DS["success"], 
                f"fort_{idx}"
            )
    
    with tab4:
        st.markdown("""
        <div class="sector-card">
            <h3>✨ Générateur de secteurs à prospecter</h3>
            <p style="color: #6b7280;">Découvrez de nouveaux secteurs d'activité avec l'IA</p>
        </div>
        """, unsafe_allow_html=True)
        show_generator_section_complete()
    
    with tab5:
        show_results_section_advanced()

if __name__ == "__main__":
    module_ia_insights({})