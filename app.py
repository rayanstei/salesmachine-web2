import streamlit as st
import pandas as pd
import sys
from datetime import datetime
from io import BytesIO

sys.path.append('./modules')

st.set_page_config(page_title="SalesMachine 3.0", page_icon="🚀", layout="wide")

st.markdown("""
<div style="background: linear-gradient(135deg, #3b82f6, #1d4ed8); padding: 2rem; 
           border-radius: 15px; color: white; text-align: center; margin-bottom: 2rem;">
    <h1>🚀 SalesMachine 3.0 Web</h1>
    <p>Migration PyQt5 → Streamlit réussie !</p>
</div>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    data = {}
    status = []
    
    try:
        data['crm'] = pd.read_csv('data/crm.csv', encoding='utf-8')
        status.append(f"✅ CRM: {len(data['crm']):,} entreprises")
    except Exception as e:
        status.append(f"❌ CRM: {e}")
    
    try:
        data['ref'] = pd.read_csv('data/Entreprises_Toutes_Videos_MAJ.csv', encoding='utf-8')
        status.append(f"✅ Référence: {len(data['ref']):,} entreprises")
    except Exception as e:
        status.append(f"❌ Référence: {e}")
        
    try:
        data['ape'] = pd.read_csv('data/ape.csv', encoding='utf-8')
        status.append(f"✅ APE: {len(data['ape'])} codes")
    except Exception as e:
        status.append(f"❌ APE: {e}")
        
    try:
        data['rome'] = pd.read_excel('data/rome.xlsx')
        status.append(f"✅ ROME: {len(data['rome']):,} métiers")
    except Exception as e:
        status.append(f"❌ ROME: {e}")
    
    return data, status

def test_search():
    try:
        import salesmachine_validator_corrige
        if hasattr(salesmachine_validator_corrige, 'API_KEY'):
            api = salesmachine_validator_corrige.API_KEY
            if api and len(api) > 10:
                return True, f"✅ Moteur OK (API: {api[:8]}...)"
        return False, "⚠️ API non configurée"
    except ImportError as e:
        return False, f"❌ Moteur: {e}"

# Import du module IA Insights compatible Streamlit
try:
    from ai_insights_streamlit import module_ia_insights
    ai_insights_available = True
    st.success("✅ Module IA Insights chargé avec succès")
except ImportError as e:
    ai_insights_available = False
    st.error(f"❌ Module IA Insights non disponible: {e}")

# Import du module Prospection compatible Streamlit
try:
    from prospection_streamlit import module_prospection
    prospection_available = True
    st.success("✅ Module Prospection chargé avec succès")
except ImportError as e:
    prospection_available = False
    st.error(f"❌ Module Prospection non disponible: {e}")

# Interface
data, status = load_data()
search_ok, search_msg = test_search()

# Sidebar pour navigation entre modules
st.sidebar.markdown("## 📊 État Système")
for s in status:
    if "✅" in s:
        st.sidebar.success(s)
    else:
        st.sidebar.error(s)

if search_ok:
    st.sidebar.success(search_msg)
else:
    st.sidebar.error(search_msg)

st.sidebar.markdown("## 🚀 Modules")
module_selected = st.sidebar.radio(
    "Sélectionner un module",
    options=["🔍 Prospection", "🧠 IA Insights"]
)

# Affichage du module sélectionné
if module_selected == "🔍 Prospection":
    if prospection_available:
        module_prospection(data)
    else:
        st.warning("Module Prospection introuvable ou non compatible Streamlit.")
        st.markdown("""
        **Pour résoudre ce problème :**
        1. Vérifiez que le fichier `modules/prospection_streamlit.py` existe
        2. Vérifiez les dépendances : `pip install plotly`
        3. Redémarrez l'application
        """)
elif module_selected == "🧠 IA Insights":
    st.markdown("## 🧠 IA Insights")
    if ai_insights_available:
        module_ia_insights(data)
    else:
        st.warning("Module IA Insights introuvable ou non compatible Streamlit.")
        st.markdown("""
        **Pour résoudre ce problème :**
        1. Vérifiez que le fichier `modules/ai_insights_streamlit.py` existe
        2. Vérifiez les dépendances : `pip install plotly`
        3. Redémarrez l'application
        """)

# Section de statut système
st.markdown("---")
st.markdown("## 🚀 Statut Système")

data_ok = sum(1 for s in status if "✅" in s)
total_score = data_ok + (1 if search_ok else 0) + (1 if ai_insights_available else 0) + (1 if prospection_available else 0)

# Indicateur de santé du système
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("### 📊 Données")
    if data_ok >= 3:
        st.success(f"✅ {data_ok}/4 sources chargées")
    elif data_ok >= 2:
        st.warning(f"⚠️ {data_ok}/4 sources chargées")
    else:
        st.error(f"❌ {data_ok}/4 sources chargées")

with col2:
    st.markdown("### 🔍 Recherche")
    if search_ok:
        st.success("✅ Moteur opérationnel")
    else:
        st.error("❌ Moteur non configuré")

with col3:
    st.markdown("### 🧠 IA Insights")
    if ai_insights_available:
        st.success("✅ Module chargé")
    else:
        st.error("❌ Module non disponible")

with col4:
    st.markdown("### 🔍 Prospection")
    if prospection_available:
        st.success("✅ Module chargé")
    else:
        st.error("❌ Module non disponible")

# Score global
if total_score >= 6:
    st.success("🎉 Excellent ! Système entièrement opérationnel.")
    
elif total_score >= 4:
    st.warning("⚠️ Système fonctionnel avec quelques limitations.")
else:
    st.error("❌ Système nécessite des corrections importantes.")

st.markdown(f"**Score Global**: {total_score}/7 - {'Prêt pour production' if total_score >= 4 else 'Configuration requise'}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6b7280; padding: 1rem;">
    <p><strong>SalesMachine 3.0 Web</strong> - Propulsé par Streamlit</p>
    <p>Version développeur - Pour support: vérifiez les logs et la configuration</p>
</div>
""", unsafe_allow_html=True)