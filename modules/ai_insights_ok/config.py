import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DEFAULT_CONFIG = {
    "crm_path": os.environ.get("CRM_PATH", os.path.join(BASE_DIR, "crm.csv")),
    "ape_path": os.environ.get("APE_PATH", os.path.join(BASE_DIR, "ape.csv")),
    "rome_path": os.environ.get("ROME_PATH", os.path.join(BASE_DIR, "rome.xlsx")),
    "naf_col": os.environ.get("NAF_COL", "code_ape_mappe")
}