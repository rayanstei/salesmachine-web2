from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Entreprise:
    nom: str
    code_ape: str
    siret: Optional[str] = None
    autres_infos: Optional[dict] = None

@dataclass
class SecteurAPE:
    code: str
    libelle: str
    secteur: Optional[str] = None

@dataclass
class MetierROME:
    code: str
    libelle: str
    famille: Optional[str] = None

@dataclass
class Opportunite:
    code_ape: str
    secteur: str
    nb_crm: int
    nb_total: int
    couverture: float
    potentiel: int

@dataclass
class Recommandation:
    titre: str
    code_ape: str
    description: str
    score: float