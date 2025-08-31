# -*- coding: utf-8 -*-
"""
SALESMACHINE VALIDATOR CORRIGÉ
Système de recherche optimisé avec plus de résultats + export Excel garanti
"""

import requests
import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import pandas as pd
import os
from datetime import datetime

# Configuration API existante
API_KEY = "AIzaSyBMsXj-VDOTX6djmCIzAYijiu9vDTfJ-JU"
CSE_ID = "d6187d7735ae14d11"

# Blacklist élargie (Amazon, Kompass, annuaires, etc.)
blacklist_domaines = [
    "wikipedia", "fandom", "youtube", "facebook", "twitter", "instagram",
    "pinterest", "indeed", "glassdoor", "researchgate", "viadeo", "top10",
    "gouv", "insee", "senat", "legifrance", "linkedin", "data.gouv", "dalloz",
    "onisep", "copainsdavant", "societeinfo", "societe.com", "leboncoin",
    "emploi", "formation", "cours", "stage", "offre", "amazon", "kompass",
    "pagesjaunes", "yellowpages", "annuaire", "123pages", "bloomberg", "verif",
    "fr-fr.facebook", "aboutads", "yelp", "trustpilot", "tripadvisor", "apple.com",
    "maps.google", "business.site", "business.google", "crunchbase", "sortlist",
    "pagespro", "mappy", "fr.linkedin.com", "fr.viadeo.com", "europages", "fr.kompass",
    "pappers", "dirigeant", "infogreffe", "manageo", "score3", "bilan", "societe-france", "webwiki", "TOP10", "hellopro"
]

# Blacklist sur le nom de domaine pur (pour éviter tout contournement)
def domaine_blackliste(url):
    try:
        netloc = urlparse(url).netloc.lower().replace('www.', '')
        for d in blacklist_domaines:
            if d in netloc:
                return True
    except Exception:
        pass
    return False

# Titres à exclure s'ils sont trop génériques ou non professionnels
titres_trop_generiques = [
    "accueil", "home", "presentation", "présentation", "bienvenue", "contact", "qui sommes-nous", "notre société", "index", "about", "main page", "page d'accueil"
]

def titre_trop_generique(titre):
    titre_norm = titre.strip().lower()
    # Seulement un mot ou très court
    if len(titre_norm) < 6:
        return True
    for tg in titres_trop_generiques:
        if titre_norm == tg or titre_norm.startswith(tg) or titre_norm.endswith(tg):
            return True
    # Si le titre n'a qu'un seul mot
    if len(titre_norm.split()) <= 1:
        return True
    return False

def generer_variantes_dynamiques(mot_cle, limite_resultats=30):
    """Génère dynamiquement des variantes pertinentes pour n'importe quel secteur"""
    base = mot_cle.lower().strip()
    villes = ["Paris", "Lyon", "Marseille", "Bordeaux", "Lille", "Nantes"]
    suffixes = [
        "entreprise", "société", "professionnel", "expert", "spécialiste", "RGE", "bâtiment"
    ]
    variantes = set()
    variantes.add(base)
    # Avec suffixes
    for suffixe in suffixes:
        variantes.add(f"{base} {suffixe}")
    # Avec villes
    for ville in villes:
        variantes.add(f"{base} {ville}")
        variantes.add(f"{base} entreprise {ville}")
    # Combinaisons
    for suffixe in suffixes:
        for ville in villes:
            variantes.add(f"{base} {suffixe} {ville}")
    # Option : variantes inversées
    for suffixe in suffixes:
        variantes.add(f"{suffixe} {base}")
    return list(variantes)[:8]  # Limite à 8 variantes pour le quota

def est_entreprise_valide(url, titre, snippet, mot_cle):
    """Validation renforcée et stricte"""
    url_lower = url.lower()
    titre_lower = titre.lower()
    snippet_lower = snippet.lower()
    
    
    # Blacklist domaines (dans l'URL ou netloc)
    if any(d in url_lower for d in blacklist_domaines) or domaine_blackliste(url):
        return False
    
    # Exclure blogs et articles dans l'URL
    if "blog" in url_lower or "article" in url_lower:
        return False
    
    # Blacklist contenu
    mots_exclus = [
        "forum", "emploi", "fiche métier", "avis", "definition", "cours",
        "formation", "stage", "offre emploi", "recrutement", "wikipedia",
        "facebook", "linkedin", "twitter", "youtube", "annuaire", "actualités",
        "blog", "article", "news", "agenda", "presse", "publicité", "magazine"
    ]
    if any(mot in snippet_lower for mot in mots_exclus):
        return False
    if any(mot in titre_lower for mot in mots_exclus):
        return False

    # Exclure titres trop génériques
    if titre_trop_generique(titre):
        return False

    # Filtrage par mots-clés du secteur (obligatoire dans titre ou snippet)
    # Le mot-clé principal et chaque mot séparé (ex: "chaudronnerie industrielle" -> ["chaudronnerie", "industrielle"])
    keywords = [mot_cle.strip().lower()] + [x for x in mot_cle.lower().split() if len(x) > 3]
    is_relevant = any(kw in titre_lower or kw in snippet_lower for kw in keywords)
    if not is_relevant:
        return False

    # Vérifications positives (bonus)
    mots_positifs = [
        "entreprise", "societe", "sarl", "sas", "etablissement",
        "professionnel", "service", "expert", "specialiste"
    ]
    score_positif = sum(1 for mot in mots_positifs if mot in titre_lower or mot in snippet_lower)
    return score_positif >= 1

def extraire_infos_site_optimise(url):
    """Extraction d'infos optimisée avec timeout et gestion d'erreurs"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, timeout=8, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(" ", strip=True)
        
        # Extraction téléphone améliorée
        tel_patterns = [
            r"0[1-9](?:[\s.-]?[0-9]{2}){4}",
            r"\+33[\s.-]?[1-9](?:[\s.-]?[0-9]{2}){4}",
            r"(?:tel|téléphone|phone)[\s:]*([0-9\s.-]{10,})"
        ]
        
        telephones = []
        for pattern in tel_patterns:
            tels = re.findall(pattern, text, re.IGNORECASE)
            telephones.extend(tels)
            telephones = [t for t in telephones if t.strip().startswith("0") or t.strip().startswith("+33")]
        
        # Extraction email améliorée
        emails = re.findall(r"[\w.-]+@[\w.-]+\.\w+", text)
        emails = [email for email in emails if not any(spam in email.lower() for spam in ['spam', 'noreply', 'example'])]
        
        # Nom d'entreprise depuis l'URL
        domain_parts = urlparse(url).netloc.replace("www.", "").split(".")
        nom_base = domain_parts[0] if domain_parts else "Entreprise"
        
        # Essayer d'extraire le nom depuis le title
        title_tag = soup.find('title')
        if title_tag:
            title_text = title_tag.get_text().strip()
            # Prendre la première partie avant " | " ou " - "
            nom_title = re.split(r'[|\-]', title_text)[0].strip()
            if len(nom_title) > 3 and len(nom_title) < 50:
                nom_base = nom_title
        
        return {
            "Nom": nom_base.title(),
            "Site": url,
            "Téléphone": telephones[0] if telephones else "",
            "Email": emails[0] if emails else ""
        }
        
    except Exception as e:
        print(f"      ⚠️ Erreur extraction {url}: {str(e)[:50]}")
        # Retourner au moins les infos de base
        domain_parts = urlparse(url).netloc.replace("www.", "").split(".")
        nom_fallback = domain_parts[0].title() if domain_parts else "Entreprise"
        
        return {
            "Nom": nom_fallback,
            "Site": url,
            "Téléphone": "",
            "Email": ""
        }

def google_search_optimise(query, api_key, cse_id, num=10):
    """Recherche Google optimisée avec gestion d'erreurs"""
    try:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'q': query,
            'key': api_key,
            'cx': cse_id,
            'num': num,
            'gl': 'fr',  # Géolocalisation France
            'lr': 'lang_fr'  # Langue française
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if 'error' in data:
            print(f"      ❌ Erreur API: {data['error'].get('message', 'Erreur inconnue')}")
            return []
        
        return data.get("items", [])
        
    except requests.exceptions.RequestException as e:
        print(f"      ❌ Erreur réseau: {str(e)}")
        return []
    except Exception as e:
        print(f"      ❌ Erreur inattendue: {str(e)}")
        return []

def lancer_recherche_entreprises_corrigee(mot_cle, limite_resultats=30):
    """Fonction principale corrigée avec plus de résultats et filtrage strict"""
    print(f"🔍 RECHERCHE CORRIGÉE : {mot_cle}")
    print(f"🎯 Objectif : {limite_resultats} résultats maximum")
    
    # Générer variantes dynamiques
    variantes = generer_variantes_dynamiques(mot_cle, limite_resultats)
    print(f"🔁 {len(variantes)} variantes générées")
    
    resultats_bruts = []
    urls_vues = set()
    noms_vus = set()  # Pour filtrer les doublons sur le nom
    
    for i, variante in enumerate(variantes, 1):
        if len(resultats_bruts) >= limite_resultats:
            break
            
        print(f"  🔍 Variante {i}/{len(variantes)}: '{variante}'")
        
        # Recherche Google
        items = google_search_optimise(variante, API_KEY, CSE_ID, num=10)
        
        if not items:
            print(f"      ⚠️ Aucun résultat pour cette variante")
            continue
        
        print(f"      📊 {len(items)} résultats Google reçus")
        
        # Traiter chaque résultat
        for item in items:
            if len(resultats_bruts) >= limite_resultats:
                break
                
            url = item.get("link", "")
            titre = item.get("title", "")
            snippet = item.get("snippet", "")
            
            # Éviter doublons d'URL
            if url in urls_vues:
                continue
            urls_vues.add(url)
            
            # Validation renforcée sur la pertinence (oblige présence d'un mot-clé secteur)
            if not est_entreprise_valide(url, titre, snippet, mot_cle):
                continue
            
            # Extraction d'infos
            infos = extraire_infos_site_optimise(url)
            if infos:
                nom_normalise = infos["Nom"].strip().lower()
                # Filtrage des doublons sur le nom d'entreprise
                if nom_normalise in noms_vus:
                    continue
                noms_vus.add(nom_normalise)
                print(f"      ✅ Ajouté: {infos['Nom']}")
                resultats_bruts.append(infos)
        
        print(f"      📈 Total accumulé: {len(resultats_bruts)}")
        
        # Pause entre variantes pour éviter rate limit
        if i < len(variantes):
            import time
            time.sleep(1)
    
    print(f"✅ RECHERCHE TERMINÉE")
    print(f"📊 {len(resultats_bruts)} entreprises trouvées")
    
    # Export automatique Excel
    if resultats_bruts:
        export_excel_garanti(resultats_bruts, mot_cle)
    
    return resultats_bruts

def export_excel_garanti(resultats, mot_cle):
    """Export Excel garanti avec horodatage"""
    try:
        # Créer dossier exports
        if not os.path.exists("exports"):
            os.makedirs("exports")
        
        # Nom de fichier avec timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"exports/recherche_{mot_cle.replace(' ', '_')}_{timestamp}.xlsx"
        
        # Créer DataFrame
        df = pd.DataFrame(resultats)
        
        # Export Excel avec plusieurs onglets
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Onglet principal
            df.to_excel(writer, sheet_name='Entreprises_Trouvees', index=False)
            
            # Onglet statistiques
            stats = {
                'Métrique': [
                    'Mot-clé recherché',
                    'Total entreprises',
                    'Avec site web',
                    'Avec téléphone', 
                    'Avec email',
                    'Date recherche'
                ],
                'Valeur': [
                    mot_cle,
                    len(df),
                    len(df[df['Site'] != '']),
                    len(df[df['Téléphone'] != '']),
                    len(df[df['Email'] != '']),
                    datetime.now().strftime("%Y-%m-%d %H:%M")
                ]
            }
            
            stats_df = pd.DataFrame(stats)
            stats_df.to_excel(writer, sheet_name='Statistiques', index=False)
        
        print(f"📊 Export Excel réussi : {filename}")
        return filename
        
    except Exception as e:
        print(f"❌ Erreur export Excel : {e}")
        return None

# Test de compatibilité avec l'ancien système
def lancer_recherche_entreprises(mot_cle):
    """Fonction de compatibilité avec l'ancien nom"""
    return lancer_recherche_entreprises_corrigee(mot_cle, limite_resultats=25)