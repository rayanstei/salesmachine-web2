import pandas as pd
from typing import List
from datamodel import Entreprise, SecteurAPE, MetierROME

def load_crm(filepath: str, naf_col: str = "code_ape") -> List[Entreprise]:
    df = pd.read_csv(filepath, dtype=str)
    if naf_col not in df.columns:
        raise ValueError(f"Colonne '{naf_col}' absente du fichier CRM")
    entreprises = []
    for _, row in df.iterrows():
        entreprises.append(Entreprise(
            nom=row.get('nom', row.get('Entreprise', '')),
            code_ape=row[naf_col],
            siret=row.get('siret'),
            autres_infos=row.to_dict()
        ))
    return entreprises

def load_ape(filepath: str) -> List[SecteurAPE]:
    df = pd.read_csv(filepath, dtype=str)
    secteurs = []
    for _, row in df.iterrows():
        secteurs.append(SecteurAPE(
            code=row['code'],
            libelle=row['libelle'],
            secteur=row.get('secteur')
        ))
    return secteurs

def load_rome(filepath: str) -> List[MetierROME]:
    df = pd.read_excel(filepath, dtype=str)
    metiers = []
    for _, row in df.iterrows():
        metiers.append(MetierROME(
            code=row['code'],
            libelle=row['libelle'],
            famille=row.get('famille')
        ))
    return metiers