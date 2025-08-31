from typing import List, Optional
from datamodel import Entreprise, SecteurAPE, MetierROME

class DataRepository:
    def __init__(self):
        self.entreprises: List[Entreprise] = []
        self.secteurs: List[SecteurAPE] = []
        self.metiers: List[MetierROME] = []

    def load_all(self, crm_path: str, ape_path: str, rome_path: str, naf_col: str = "code_ape"):
        from data_loader import load_crm, load_ape, load_rome
        self.entreprises = load_crm(crm_path, naf_col)
        self.secteurs = load_ape(ape_path)
        self.metiers = load_rome(rome_path)

    def get_entreprises(self) -> List[Entreprise]:
        return self.entreprises

    def get_secteurs(self) -> List[SecteurAPE]:
        return self.secteurs

    def get_metiers(self) -> List[MetierROME]:
        return self.metiers