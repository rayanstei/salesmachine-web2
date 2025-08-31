import requests
import json
import logging

def enrichir_par_api_recherche_entreprise(nom_entreprise):
    url = "https://recherche-entreprises.api.gouv.fr/search"
    params = {"q": nom_entreprise}
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data and data.get('results'):
            first_result = data['results'][0]
            siren = first_result.get('siren', '')
            naf = first_result.get('activite_principale', '') or first_result.get('code_naf', '')
            return {'SIREN': siren, 'NAF': naf}
    except requests.exceptions.RequestException as e:
        logging.error(f"Erreur lors de l'appel à l'API d'enrichissement pour {nom_entreprise}: {e}")
    except json.JSONDecodeError:
        logging.error(f"Erreur de décodage JSON de la réponse de l'API pour {nom_entreprise}")
    return {}