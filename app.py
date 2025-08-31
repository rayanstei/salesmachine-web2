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

# Import du module IA Insights
try:
    from ai_insights import module_ia_insights
except ImportError:
    module_ia_insights = None

# Interface
data, status = load_data()
search_ok, search_msg = test_search()

# Sidebar
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

# Métriques
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🏢 CRM", f"{len(data.get('crm', [])):,}")
with col2:
    st.metric("📋 Référence", f"{len(data.get('ref', [])):,}")
with col3:
    st.metric("📊 APE", len(data.get('ape', [])))
with col4:
    st.metric("💼 ROME", f"{len(data.get('rome', [])):,}")

# Onglets navigation
tab1, tab2 = st.tabs(["🔍 Prospection", "🧠 IA Insights"])

with tab1:
    if search_ok and 'ref' in data and 'crm' in data:
        st.markdown("## 🔍 Test Recherche + Déduplication")
        query = st.text_input("Recherche test", placeholder="cabinet comptable Paris")
        if st.button("🚀 Tester") and query:
            try:
                import salesmachine_validator_corrige
                with st.spinner("Recherche..."):
                    results = salesmachine_validator_corrige.lancer_recherche_entreprises_corrigee(query, 10)
                if results:
                    st.success(f"✅ {len(results)} entreprises trouvées")
                    ref_names = set(data['ref']['Entreprise'].dropna().astype(str).str.lower().str.strip())
                    nouvelles = []
                    for r in results:
                        nom = str(r.get('Nom', '')).lower().strip()
                        if nom and nom not in ref_names:
                            nouvelles.append(r)
                    if nouvelles:
                        st.write(f"**🆕 {len(nouvelles)} nouvelles entreprises:**")
                        df = pd.DataFrame(nouvelles)
                        st.dataframe(df, use_container_width=True)
                        buffer = BytesIO()
                        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                            df.to_excel(writer, index=False, sheet_name='Nouvelles')
                        st.download_button(
                            "📊 Télécharger",
                            buffer.getvalue(),
                            f"nouvelles_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                            "application/vnd.ms-excel"
                        )
                    else:
                        st.info("ℹ️ Toutes les entreprises sont déjà connues")
                else:
                    st.warning("Aucun résultat")
            except Exception as e:
                st.error(f"Erreur: {e}")

with tab2:
    st.markdown("## 🧠 IA Insights")
    if module_ia_insights is not None:
        module_ia_insights(data)
    else:
        st.warning("Module IA Insights introuvable ou non compatible Streamlit.")

st.markdown("## 🚀 Système Prêt !")
data_ok = sum(1 for s in status if "✅" in s)
total_score = data_ok + (1 if search_ok else 0)

if total_score >= 4:
    st.success("🎉 Excellent ! Système opérationnel.")
elif total_score >= 3:
    st.warning("⚠️ Système fonctionnel avec quelques limitations.")
else:
    st.error("❌ Système nécessite des corrections.")

st.markdown(f"**Score**: {total_score}/5 - Prêt pour Streamlit Cloud !")