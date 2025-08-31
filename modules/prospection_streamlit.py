import streamlit as st
import pandas as pd
import plotly.express as px
import time
import random
from datetime import datetime
from io import BytesIO
import json
import os

# Design System (repris de l'original, avec améliorations pour plus de style)
DS = {
    "primary": "#3b82f6",
    "primary_dark": "#1d4ed8",
    "primary_light": "#dbeafe",
    "success": "#10b981",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "background": "#ffffff",
    "surface": "#f9fafb",
    "surface_alt": "#f3f6fa",
    "border": "#e5e7eb",
    "text_primary": "#1f2937",
    "text_secondary": "#6b7280",
    "text_muted": "#9ca3af",
}

# CSS personnalisé pour une UI ultra-moderne
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    .prospection-container {
        font-family: 'Inter', sans-serif;
        background-color: #f9fafb;
    }
    
    .header-gradient {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        padding: 2rem;
        border-radius: 1.25rem;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 12px 30px rgba(59,130,246,0.2);
        animation: fadeIn 0.8s ease-out;
    }
    
    .header-gradient h1 {
        margin-bottom: 0.5rem;
        font-size: 2.5rem;
        font-weight: 800;
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
        margin: 1rem 0;
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
        border-radius: 1.25rem;
        padding: 2rem;
        margin: 1rem 0;
        border: 1px solid #e5e7eb;
        box-shadow: 0 6px 20px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        animation: slideIn 0.6s ease;
    }
    
    .sector-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.15);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 1.25rem;
        background: #f8fafc;
        padding: 0.75rem;
        border-radius: 1.25rem;
        box-shadow: inset 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 1rem;
        color: #6b7280;
        font-weight: 600;
        padding: 0.85rem 1.75rem;
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
        background: linear-gradient(135deg, #1d4ed8, #3b82f6);
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
    
    .error-toast {
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 0.75rem;
        margin: 1rem 0;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(239,68,68,0.3);
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
    
    .animate-entry {
        animation: slideIn 0.6s ease;
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
    
    const buttons = document.querySelectorAll('.stButton > button');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-3px)';
            this.style.boxShadow = '0 10px 30px rgba(59,130,246,0.5)';
        });
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 4px 15px rgba(59,130,246,0.3)';
        });
    });
</script>
""", unsafe_allow_html=True)

HISTORIQUE_FILE = "historique_recherches.json"

def load_historique():
    if os.path.exists(HISTORIQUE_FILE):
        with open(HISTORIQUE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_historique(historique):
    with open(HISTORIQUE_FILE, 'w', encoding='utf-8') as f:
        json.dump(historique, f, ensure_ascii=False, indent=4)

def show_toast(message: str, type: str = "success"):
    """Affiche une notification toast stylée"""
    if type == "success":
        st.markdown(f'<div class="success-toast animate-entry">✅ {message}</div>', unsafe_allow_html=True)
    elif type == "error":
        st.markdown(f'<div class="error-toast animate-entry">❌ {message}</div>', unsafe_allow_html=True)
    elif type == "warning":
        st.warning(f"⚠️ {message}")
    else:
        st.info(f"ℹ️ {message}")

def perform_search(query: str, filters: dict):
    """Recherche réelle si possible, sinon simulation."""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Recherche réelle
    try:
        import salesmachine_validator_corrige
        from salesmachine_validator_corrige import lancer_recherche_entreprises_corrigee
        SEARCH_ENGINE_AVAILABLE = True
        status_text.text("✅ Moteur de recherche réel chargé")
        progress_bar.progress(10)
    except Exception as e:
        SEARCH_ENGINE_AVAILABLE = False
        show_toast(f"❌ Moteur de recherche non disponible : {str(e)}", "error")
        status_text.text("⚠️ Passage en mode simulation")
        progress_bar.progress(10)

    try:
        from api_enrichment import enrichir_par_api_recherche_entreprise
        API_ENRICHMENT_AVAILABLE = True
        status_text.text("✅ API d'enrichissement chargée")
        progress_bar.progress(20)
    except ImportError:
        API_ENRICHMENT_AVAILABLE = False
        status_text.text("ℹ️ API d'enrichissement non disponible")
        progress_bar.progress(20)

    if not SEARCH_ENGINE_AVAILABLE:
        # Mode simulation
        status_text.text("🔄 Mode simulation activé")
        progress_bar.progress(30)
        time.sleep(2)  # Simule le temps de recherche
        base_results = [
            {
                'nom': 'TechStart Solutions',
                'secteur': 'Services numériques',
                'ville': 'Lyon',
                'score': 92,
                'statut': 'EXCELLENT',
                'contact': 'contact@techstart-solutions.fr',
                'telephone': '04 78 XX XX XX',
                'website': 'techstart-solutions.fr',
                'taille': '15-25 employés',
                'ca': '1-2 M€',
                'description': 'Développement d\'applications mobiles innovantes',
                'adresse': '123 Rue de la République, 69002 Lyon',
                'SIREN': '',
                'NAF': ''
            },
            {
                'nom': 'Innovation Corp',
                'secteur': 'Industrie manufacturière',
                'ville': 'Villeurbanne',
                'score': 87,
                'statut': 'POTENTIEL',
                'contact': 'contact@innovation-corp.com',
                'telephone': '04 72 XX XX XX',
                'website': 'innovation-corp.com',
                'taille': '50-100 employés',
                'ca': '10-15 M€',
                'description': 'Fabrication de composants électroniques',
                'adresse': '456 Avenue Innovation, 69100 Villeurbanne',
                'SIREN': '',
                'NAF': ''
            },
        ]
        progress_bar.progress(100)
        status_text.text("✅ Simulation terminée")
        progress_bar.empty()
        status_text.empty()
        return base_results

    # Recherche réelle
    try:
        status_text.text(f"🔍 Recherche pour : {query}")
        progress_bar.progress(25)
        results = lancer_recherche_entreprises_corrigee(query, 20)
        progress_bar.progress(50)
        status_text.text("📋 Formatage des résultats...")

        formatted = []
        if results:
            for i, result in enumerate(results[:15]):
                if isinstance(result, dict):
                    formatted_result = {
                        'nom': result.get('Nom', f'Entreprise {i+1}'),
                        'secteur': extract_sector(result.get('Site', '')),
                        'ville': extract_city(result),
                        'score': 95 - i*3,
                        'statut': 'NOUVEAU',
                        'contact': extract_email(result),
                        'telephone': result.get('Téléphone', ''),
                        'website': result.get('Site', ''),
                        'taille': estimate_size(result),
                        'ca': result.get('CA', ''),
                        'description': f"Entreprise spécialisée dans {extract_sector(result.get('Site', ''))}",
                        'adresse': result.get('Adresse', 'Non disponible'),
                        'SIREN': '',
                        'NAF': ''
                    }
                    if API_ENRICHMENT_AVAILABLE:
                        status_text.text(f"🔄 Enrichissement pour {formatted_result['nom']}...")
                        try:
                            infos_api = enrichir_par_api_recherche_entreprise(formatted_result['nom'])
                            if infos_api:
                                formatted_result['SIREN'] = infos_api.get('SIREN', '')
                                formatted_result['NAF'] = infos_api.get('NAF', '')
                        except Exception:
                            pass
                    formatted.append(formatted_result)
            status_text.text(f"✅ {len(formatted)} résultats trouvés")
        else:
            status_text.text("⚠️ Aucun résultat brut retourné")
            show_toast("Aucun résultat trouvé pour cette recherche", "warning")

        # Filtrage CA
        ca_filter = filters.get('ca', "Tous CA")
        if ca_filter != "Tous CA":
            formatted = [r for r in formatted if ca_match(r.get('ca', ''), ca_filter)]

        progress_bar.progress(100)
        progress_bar.empty()
        status_text.empty()
        return formatted
    except Exception as e:
        show_toast(f"❌ Erreur lors de la recherche : {str(e)}", "error")
        progress_bar.empty()
        status_text.empty()
        return []

def extract_sector(website):
    if not website:
        return "Services généraux"
    website = website.lower()
    if any(word in website for word in ['restaurant', 'food', 'cafe']):
        return "Restauration"
    if any(word in website for word in ['tech', 'digital', 'web', 'soft']):
        return "Services numériques"
    if any(word in website for word in ['health', 'medical', 'sante']):
        return "Santé"
    if any(word in website for word in ['build', 'construct', 'btp']):
        return "BTP"
    return "Services professionnels"

def extract_city(result):
    return result.get('Ville', result.get('Location', ''))

def extract_email(result):
    return result.get('Email', result.get('Contact', ''))

def estimate_size(result):
    sizes = ["TPE (1-10)", "PME (11-50)", "ETI (51-250)", "Grande entreprise (250+)"]
    return random.choice(sizes)

def ca_match(ca_str, ca_filter):
    if not ca_str:
        return False
    ca_str = str(ca_str).lower()
    if ca_filter == "< 500 k€":
        return ("<" in ca_str or "500" in ca_str or "k€" in ca_str) and ("m" not in ca_str)
    if ca_filter == "500 k€ - 2 M€":
        return ("500" in ca_str or "2 m" in ca_str)
    if ca_filter == "2 M€ - 10 M€":
        return ("2 m" in ca_str or "10 m" in ca_str)
    if ca_filter == "10 M€ - 50 M€":
        return ("10 m" in ca_str or "50 m" in ca_str)
    if ca_filter == "> 50 M€":
        return "50 m" in ca_str or "100 m" in ca_str or "m€" in ca_str
    return True

def create_metric_card(icon: str, value: str, label: str, color: str):
    st.markdown(f"""
    <div class="metric-card animate-entry">
        <div class="metric-value" style="color: {color};">{icon} {value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)

def module_prospection(data):
    """Module Prospection adapté pour Streamlit, avec relance historique et recherche réelle."""
    # Chargement de l'historique depuis fichier ou session
    if 'historique' not in st.session_state:
        histo = load_historique()
        st.session_state.historique = histo if histo else []

    if 'existing_companies' not in st.session_state:
        st.session_state.existing_companies = set(data['ref']['Entreprise'].dropna().astype(str).str.lower().str.strip()) if 'ref' in data else set()

    if 'metrics' not in st.session_state:
        st.session_state.metrics = {
            "recherches_totales": 0,
            "nouveaux_prospects": 0,
            "doublons_evites": 0,
            "taux_conversion": 0.0
        }

    if 'search_results' not in st.session_state:
        st.session_state.search_results = []

    if 'filter_mail' not in st.session_state:
        st.session_state.filter_mail = False
    if 'filter_tel' not in st.session_state:
        st.session_state.filter_tel = False
    if 'filter_site' not in st.session_state:
        st.session_state.filter_site = False

    # Header stylé
    st.markdown(f"""
    <div class="header-gradient animate-entry">
        <h1>🔍 Module Prospection</h1>
        <p style="opacity: 0.9; font-size: 1.1rem; font-weight: 500;">
            Recherchez et enrichissez vos prospects avec IA
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Métrics dashboard amélioré
    st.markdown("### 📈 Tableau de Bord")
    metrics_cols = st.columns(4)
    with metrics_cols[0]:
        create_metric_card("🔍", st.session_state.metrics["recherches_totales"], "Recherches Totales", DS["primary"])
    with metrics_cols[1]:
        create_metric_card("🆕", st.session_state.metrics["nouveaux_prospects"], "Nouveaux Prospects", DS["success"])
    with metrics_cols[2]:
        create_metric_card("🚫", st.session_state.metrics["doublons_evites"], "Doublons Évités", DS["warning"])
    with metrics_cols[3]:
        create_metric_card("📈", f"{st.session_state.metrics['taux_conversion']}%", "Taux Conversion", DS["primary_dark"])

    st.markdown("---")

    # Onglets pour Nouvelle Recherche et Dernières Recherches
    tab1, tab2 = st.tabs(["➕ Nouvelle Recherche", "📜 Dernières Recherches"])

    # --- Nouvelle Recherche ---
    with tab1:
        # Si relance depuis l'historique, pré-remplir les champs
        relance = st.session_state.get("relance_recherche", None)
        if relance:
            query_default = relance.get("query", "")
            location_default = relance.get("location", "Toutes")
            sector_default = relance.get("sector", "Tous")
            size_default = relance.get("size", "Toutes")
            ca_default = relance.get("ca", "Tous CA")
            st.session_state["relance_recherche"] = None  # Reset après usage
        else:
            query_default, location_default, sector_default, size_default, ca_default = "", "Toutes", "Tous", "Toutes", "Tous CA"

        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        with col1:
            query = st.text_input("Recherche (ex: cabinet comptable Paris)", key="search_input", value=query_default)
        with col2:
            location = st.selectbox("📍 Localisation", ["Toutes", "Paris", "Lyon", "Marseille", "Autre"], key="location_combo", index=["Toutes", "Paris", "Lyon", "Marseille", "Autre"].index(location_default))
        with col3:
            sector = st.selectbox("🏭 Secteur", ["Tous", "Services numériques", "Industrie", "BTP", "Autre"], key="sector_combo", index=["Tous", "Services numériques", "Industrie", "BTP", "Autre"].index(sector_default))
        with col4:
            size = st.selectbox("👥 Taille", ["Toutes", "TPE (1-10)", "PME (11-50)", "ETI (51-250)", "Grande entreprise (250+)"], key="size_combo", index=["Toutes", "TPE (1-10)", "PME (11-50)", "ETI (51-250)", "Grande entreprise (250+)"].index(size_default))
        ca = st.selectbox("💶 CA", ["Tous CA", "< 500 k€", "500 k€ - 2 M€", "2 M€ - 10 M€", "10 M€ - 50 M€", "> 50 M€"], key="ca_combo", index=["Tous CA", "< 500 k€", "500 k€ - 2 M€", "2 M€ - 10 M€", "10 M€ - 50 M€", "> 50 M€"].index(ca_default))
        filters = {'location': location, 'sector': sector, 'size': size, 'ca': ca}

        if st.button("🚀 Lancer Recherche", type="primary"):
            if query:
                with st.spinner("Recherche en cours..."):
                    # Construction query enrichie
                    enriched_query = query
                    if location != "Toutes":
                        enriched_query += f" {location}"
                    if sector != "Tous":
                        enriched_query += f" {sector}"
                    if size != "Toutes":
                        enriched_query += f" {size}"
                    if ca != "Tous CA":
                        enriched_query += f" {ca}"
                    results = perform_search(enriched_query, filters)
                    # Déduplication
                    def clean(x): return str(x).strip().lower() if x else ''
                    filtered_results = [r for r in results if clean(r['nom']) not in st.session_state.existing_companies]
                    st.session_state.search_results = filtered_results
                    # Metrics
                    total_results = len(filtered_results)
                    new_prospects = len([r for r in filtered_results if r['statut'] != 'DOUBLON'])
                    duplicates = total_results - new_prospects
                    taux_conversion = (new_prospects / total_results * 100) if total_results > 0 else 0.0
                    st.session_state.metrics["recherches_totales"] += 1
                    st.session_state.metrics["nouveaux_prospects"] += new_prospects
                    st.session_state.metrics["doublons_evites"] += duplicates
                    st.session_state.metrics["taux_conversion"] = round(taux_conversion, 1)
                    # Historique (sauvegarde fichier + session)
                    hist_item = {
                        'query': query,
                        'location': location,
                        'sector': sector,
                        'size': size,
                        'ca': ca,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                        'results_count': len(filtered_results)
                    }
                    st.session_state.historique.insert(0, hist_item)
                    st.session_state.historique = st.session_state.historique[:10]
                    save_historique(st.session_state.historique)
                    show_toast(f"{len(filtered_results)} entreprises trouvées")
                    st.rerun()
            else:
                show_toast("Veuillez entrer une requête de recherche", "warning")

        # Filtres avancés (mail, tel, site)
        col_filter1, col_filter2, col_filter3 = st.columns(3)
        with col_filter1:
            st.session_state.filter_mail = st.checkbox("✉️ Avec Email")
        with col_filter2:
            st.session_state.filter_tel = st.checkbox("📞 Avec Téléphone")
        with col_filter3:
            st.session_state.filter_site = st.checkbox("🌐 Avec Site Web")

        # Résultats
        if st.session_state.search_results:
            results_to_display = st.session_state.search_results
            if st.session_state.filter_mail or st.session_state.filter_tel or st.session_state.filter_site:
                results_to_display = [
                    r for r in results_to_display
                    if (not st.session_state.filter_mail or r.get('contact')) and
                       (not st.session_state.filter_tel or r.get('telephone')) and
                       (not st.session_state.filter_site or r.get('website'))
                ]
            st.markdown("### 📊 Résultats de Recherche")
            df_results = pd.DataFrame(results_to_display)
            column_config = {
                "nom": st.column_config.TextColumn("🏢 Nom", width="medium"),
                "secteur": st.column_config.TextColumn("🏭 Secteur", width="medium"),
                "ville": st.column_config.TextColumn("📍 Ville", width="small"),
                "taille": st.column_config.TextColumn("👥 Taille", width="small"),
                "score": st.column_config.ProgressColumn("📊 Score", min_value=0, max_value=100, format="%d/100", width="small"),
                "statut": st.column_config.TextColumn("⭐ Statut", width="small"),
                "contact": st.column_config.TextColumn("✉️ Email", width="medium"),
                "telephone": st.column_config.TextColumn("📞 Téléphone", width="medium"),
                "website": st.column_config.LinkColumn("🌐 Site", width="medium"),
            }
            st.data_editor(
                df_results,
                column_config=column_config,
                use_container_width=True,
                hide_index=False
            )
            # Visualisation graphique
            if results_to_display:
                st.markdown("### 📈 Analyse des Résultats")
                sector_counts = df_results['secteur'].value_counts()
                fig = px.pie(
                    values=sector_counts.values,
                    names=sector_counts.index,
                    title="Répartition par Secteur",
                    color_discrete_sequence=px.colors.qualitative.Set3,
                    hole=0.3
                )
                fig.update_layout(font=dict(family="Inter", size=12), height=400)
                st.plotly_chart(fig, use_container_width=True)
            # Bouton Export stylé
            if st.button("📊 Exporter Résultats", type="secondary"):
                csv = df_results.to_csv(index=False)
                st.download_button(
                    label="⬇️ Télécharger CSV",
                    data=csv,
                    file_name=f"prospection_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv"
                )
                show_toast("Export prêt au téléchargement")

    # --- Dernières recherches ---
    with tab2:
        st.markdown("""
        <div class="sector-card animate-entry">
            <h3>📜 Dernières Recherches</h3>
        </div>
        """, unsafe_allow_html=True)
        if st.session_state.historique:
            for idx, hist in enumerate(st.session_state.historique):
                col1, col2 = st.columns([6, 1])
                with col1:
                    st.markdown(f"""
                    <div class="sector-card animate-entry" style="padding:1rem 2rem">
                        <div style="font-size: 1.1rem; font-weight: 700; color: #1f2937;">
                            {hist['query']}
                        </div>
                        <div style="font-size: 0.875rem; color: #6b7280;">
                            {hist.get('timestamp','')} • {hist['results_count']} résultats<br>
                            <span style="color:#2563eb;">{hist.get('location','')} | {hist.get('sector','')} | {hist.get('size','')} | {hist.get('ca','')}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    if st.button("🔄 Relancer", key=f"relance_{idx}"):
                        st.session_state["relance_recherche"] = hist
                        st.rerun()
        else:
            st.info("Aucun historique disponible. Lancez une recherche pour commencer.")