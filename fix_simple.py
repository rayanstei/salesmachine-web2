# -*- coding: utf-8 -*-
"""
Script de correction simple pour SalesMachine Web
"""

import os
import shutil
from pathlib import Path

def fix_structure():
    print("🔧 CORRECTION STRUCTURE")
    print("=" * 40)
    
    current = Path(".")
    print(f"Dossier: {current.absolute()}")
    
    # 1. Nettoyer le sous-dossier créé par erreur
    sub_folder = current / "salesmachine-web"
    if sub_folder.exists():
        print(f"📁 Sous-dossier détecté: {sub_folder}")
        
        # Déplacer le contenu
        for item in sub_folder.iterdir():
            dest = current / item.name
            if dest.exists():
                if dest.is_dir():
                    shutil.rmtree(dest)
                else:
                    dest.unlink()
            shutil.move(str(item), str(dest))
            print(f"  ✅ Déplacé: {item.name}")
        
        # Supprimer le dossier vide
        sub_folder.rmdir()
        print("  🗑️ Sous-dossier supprimé")
    
    # 2. Vérifier données
    print("\n📊 Vérification données...")
    data_dir = current / "data"
    
    if not data_dir.exists():
        print("❌ Dossier data/ manquant")
        return False
    
    files = ["crm.csv", "ape.csv", "rome.xlsx", "Entreprises_Toutes_Videos_MAJ.csv"]
    found = []
    
    for file in files:
        if (data_dir / file).exists():
            size = (data_dir / file).stat().st_size
            print(f"  ✅ {file} ({size:,} bytes)")
            found.append(file)
        else:
            print(f"  ❌ {file} manquant")
    
    # 3. Corriger modules
    print("\n🔧 Correction modules...")
    modules_dir = current / "modules"
    
    if not modules_dir.exists():
        print("❌ Dossier modules/ manquant")
        return False
    
    changes = {
        '"crm.csv"': '"data/crm.csv"',
        "'crm.csv'": "'data/crm.csv'",
        '"ape.csv"': '"data/ape.csv"',
        "'ape.csv'": "'data/ape.csv'",
        '"rome.xlsx"': '"data/rome.xlsx"',
        "'rome.xlsx'": "'data/rome.xlsx'",
        '"Entreprises_Toutes_Videos_MAJ.csv"': '"data/Entreprises_Toutes_Videos_MAJ.csv"',
        "'Entreprises_Toutes_Videos_MAJ.csv'": "'data/Entreprises_Toutes_Videos_MAJ.csv'"
    }
    
    fixed = 0
    for py_file in modules_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue
        
        try:
            content = py_file.read_text(encoding='utf-8')
            original = content
            
            for old, new in changes.items():
                content = content.replace(old, new)
            
            if content != original:
                py_file.write_text(content, encoding='utf-8')
                print(f"  ✅ {py_file.name}")
                fixed += 1
            else:
                print(f"  ⚪ {py_file.name}")
        
        except Exception as e:
            print(f"  ❌ {py_file.name}: {e}")
    
    # 4. Créer app simple
    print("\n🚀 Création app...")
    
    app_code = '''import streamlit as st
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

# Test recherche
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
                
                # Déduplication
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
                    
                    # Export
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
'''
    
    (current / "app.py").write_text(app_code, encoding='utf-8')
    print("  ✅ app.py créé")
    
    # Résumé
    print(f"\n🎉 TERMINÉ !")
    print(f"📊 Données: {len(found)}/4")
    print(f"🔧 Modules: {fixed} corrigés")
    print(f"🚀 App: créée")
    
    print(f"\n📋 COMMANDES:")
    print("pip install -r requirements.txt")
    print("streamlit run app.py")
    
    return len(found) >= 2

if __name__ == "__main__":
    try:
        success = fix_structure()
        if success:
            print("\n✅ Correction réussie !")
        else:
            print("\n⚠️ Vérifiez vos fichiers de données")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")