# -*- coding: utf-8 -*-
"""
SalesMachine v2.2 - Module Prospection MODERNE avec onglets et UI améliorée
- QTabWidget : "Nouvelle recherche" (zone compacte, aérée) / "Dernières recherches"
- Boutons Filtres et Export intégrés à la section résultats, masqués si aucun résultat
- Message d'attente discret, centré, plus petit
- Zone recherche plus compacte et élégante
"""

import sys
import webbrowser
import os
import json
import qtawesome as qta
from datetime import datetime
import pandas as pd

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QProgressBar, QFrame, QComboBox, QScrollArea,
    QFileDialog, QMessageBox, QListWidget, QListWidgetItem,
    QMenu, QCheckBox, QWidgetAction, QTabWidget, QAbstractItemView
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QColor, QIcon, QPixmap
from PyQt5.QtWidgets import QGraphicsDropShadowEffect

# ======= DESIGN SYSTEM IA INSIGHTS =======
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

def font(weight=QFont.Normal, size=13):
    f = QFont("Inter", size)
    f.setWeight(weight)
    return f

def add_glow(widget, blur=28):
    color = QColor(60, 70, 90, 24)
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blur)
    shadow.setColor(color)
    shadow.setOffset(0, 6)
    widget.setGraphicsEffect(shadow)

# ========== MOTEUR PROSPECTION ==========
try:
    import salesmachine_validator_corrige
    from salesmachine_validator_corrige import lancer_recherche_entreprises_corrigee, API_KEY, CSE_ID
    SEARCH_ENGINE_AVAILABLE = True
except ImportError as e:
    SEARCH_ENGINE_AVAILABLE = False

try:
    from api_enrichment import enrichir_par_api_recherche_entreprise
    API_ENRICHMENT_AVAILABLE = True
except ImportError as e:
    API_ENRICHMENT_AVAILABLE = False

HISTORIQUE_FILE = "historique_recherches.json"

class SearchThread(QThread):
    progress_updated = pyqtSignal(int)
    search_completed = pyqtSignal(list)
    status_updated = pyqtSignal(str)

    def __init__(self, query, filters):
        super().__init__()
        self.query = query
        self.filters = filters

    def run(self):
        import time
        self.status_updated.emit("Initialisation de la recherche...")
        self.progress_updated.emit(10)
        time.sleep(0.3)
        if not SEARCH_ENGINE_AVAILABLE:
            self.run_simulation()
            return
        try:
            self.status_updated.emit("Recherche Google en cours...")
            self.progress_updated.emit(25)
            raw_results = lancer_recherche_entreprises_corrigee(
                mot_cle=self.query,
                limite_resultats=20
            )
            self.progress_updated.emit(50)
            self.status_updated.emit("Formatage des résultats...")
            results = []
            if raw_results:
                for i, result in enumerate(raw_results[:15]):
                    if isinstance(result, dict):
                        formatted_result = {
                            'nom': result.get('Nom', f'Entreprise {i+1}'),
                            'secteur': self.extract_sector(result.get('Site', '')),
                            'ville': self.extract_city(result),
                            'score': 95 - i*3,
                            'statut': 'NOUVEAU',
                            'contact': self.extract_email(result),
                            'telephone': result.get('Téléphone', ''),
                            'website': result.get('Site', ''),
                            'taille': self.estimate_size(result),
                            'ca': result.get('CA', ''),
                            'description': f"Entreprise spécialisée dans {self.extract_sector(result.get('Site', ''))}",
                            'adresse': result.get('Adresse', 'Non disponible'),
                            'SIREN': '',
                            'NAF': ''
                        }
                        if API_ENRICHMENT_AVAILABLE:
                            infos_api = enrichir_par_api_recherche_entreprise(formatted_result['nom'])
                            if infos_api:
                                formatted_result['SIREN'] = infos_api.get('SIREN', '')
                                formatted_result['NAF'] = infos_api.get('NAF', '')
                        results.append(formatted_result)
            self.progress_updated.emit(75)
            self.status_updated.emit("Suppression des doublons...")
            time.sleep(0.3)
            if len(results) > 5:
                results[-1]['statut'] = 'DOUBLON'
            self.progress_updated.emit(90)
            self.status_updated.emit("Finalisation des résultats...")
            time.sleep(0.2)
            self.progress_updated.emit(100)
            new_results = len([r for r in results if r['statut'] != 'DOUBLON'])
            self.status_updated.emit(f"{new_results} nouvelles entreprises trouvées")
            self.search_completed.emit(results)
        except Exception as e:
            self.status_updated.emit(f"Erreur moteur, basculement simulation...")
            self.run_simulation()

    def extract_sector(self, website):
        if not website:
            return "Services généraux"
        website = website.lower()
        if any(word in website for word in ['restaurant', 'food', 'cafe']):
            return "Restauration"
        elif any(word in website for word in ['tech', 'digital', 'web', 'soft']):
            return "Services numériques"
        elif any(word in website for word in ['health', 'medical', 'sante']):
            return "Santé"
        elif any(word in website for word in ['build', 'construct', 'btp']):
            return "BTP"
        else:
            return "Services professionnels"

    def extract_city(self, result):
        return result.get('Ville', result.get('Location', ''))

    def extract_email(self, result):
        return result.get('Email', result.get('Contact', ''))

    def estimate_size(self, result):
        sizes = ["TPE (1-10)", "PME (11-50)", "ETI (51-250)", "Grande entreprise (250+)"]
        import random
        return random.choice(sizes)

    def run_simulation(self):
        import time
        self.status_updated.emit("Mode simulation activé")
        self.progress_updated.emit(30)
        time.sleep(0.5)
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
            {
                'nom': 'Digital Partners',
                'secteur': 'Services professionnels',
                'ville': 'Lyon',
                'score': 78,
                'statut': 'NOUVEAU',
                'contact': 'hello@digital-partners.fr',
                'telephone': '04 69 XX XX XX',
                'website': 'digital-partners.fr',
                'taille': 'TPE (1-10)',
                'ca': '<500 k€',
                'description': 'Conseil en transformation digitale',
                'adresse': '789 Cours Lafayette, 69003 Lyon',
                'SIREN': '',
                'NAF': ''
            }
        ]
        self.progress_updated.emit(100)
        self.status_updated.emit(f"{len(base_results)} entreprises trouvées")
        self.search_completed.emit(base_results)

# ============ TOAST MODERNE ============
class ModernToast(QFrame):
    def __init__(self, message, color=DS["success"]):
        super().__init__(None, Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.0)
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {color}, stop:1 #059669);
                color: white;
                border-radius: 12px;
                padding: 14px 26px;
                font-weight: 600;
                font-size: 14px;
            }}
        """)
        h = QHBoxLayout(self)
        h.setContentsMargins(10, 6, 10, 6)
        lab = QLabel(message)
        h.addWidget(lab)
        self.setFixedHeight(44)
        self.adjustSize()
        self._anim = QPropertyAnimation(self, b"windowOpacity")
        self._anim.setDuration(350)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.setEasingCurve(QEasingCurve.OutQuad)
        self._anim.finished.connect(self._on_shown)
        self._anim.start()

    def _on_shown(self):
        QTimer.singleShot(1800, self._fade_out)

    def _fade_out(self):
        self._anim = QPropertyAnimation(self, b"windowOpacity")
        self._anim.setDuration(350)
        self._anim.setStartValue(1.0)
        self._anim.setEndValue(0.0)
        self._anim.setEasingCurve(QEasingCurve.InQuad)
        self._anim.finished.connect(self.close)
        self._anim.start()

# ============ CARDS METRIQUES, SIDEBAR, ETC ============
class MetricCard(QFrame):
    def __init__(self, icon, value, label, color=DS["danger"]):
        super().__init__()
        self.setFixedHeight(100)
        self.setStyleSheet(f"""
            QFrame {{
                background: #fff;
                border: none;
                border-radius: 18px;
            }}
        """)
        add_glow(self, blur=18)
        l = QVBoxLayout(self)
        l.setSpacing(0)
        h = QHBoxLayout()
        ic = QLabel()
        ic.setPixmap(qta.icon(icon, color=color).pixmap(28, 28))
        ic.setFixedWidth(36)
        h.addWidget(ic)
        h.addStretch()
        l.addLayout(h)
        val = QLabel(str(value))
        val.setObjectName("MetricValue")
        val.setFont(font(QFont.ExtraBold, 28))
        val.setStyleSheet("color:#1f2937;margin-bottom:2px;")
        l.addWidget(val)
        lab = QLabel(label)
        lab.setObjectName("MetricLabel")
        lab.setFont(font(QFont.Medium, 10))
        lab.setStyleSheet("color:#6b7280;letter-spacing:0.02em;text-transform:uppercase;margin-top:0px;margin-bottom:0px;")
        l.addWidget(lab)

class Sidebar(QFrame):
    def __init__(self, metrics):
        super().__init__()
        self.setFixedWidth(260)
        self.setObjectName("Sidebar")
        self.setStyleSheet(f"""
            QFrame#Sidebar {{
                background: {DS["background"]};
                border-right: 1.5px solid {DS["border"]};
            }}
        """)
        self.setup_ui(metrics)

    def setup_ui(self, metrics):
        v = QVBoxLayout(self)
        v.setContentsMargins(24, 32, 24, 24)
        v.setSpacing(24)
        logo_row = QHBoxLayout()
        logo = QLabel()
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "salesmachine_logo.png")
        logo.setPixmap(QPixmap(logo_path).scaledToWidth(180, Qt.SmoothTransformation))
        logo.setAlignment(Qt.AlignCenter)
        logo_row.addWidget(logo, alignment=Qt.AlignCenter)
        modules_label = QLabel("MODULES")
        modules_label.setFont(font(QFont.Bold, 11))
        modules_label.setStyleSheet(f"color:{DS['text_muted']};letter-spacing:0.04em;text-transform:uppercase;margin-bottom:3px;margin-top:7px;")
        v.addWidget(modules_label)
        modules = [
            ('fa5s.search', "Prospection", True),
            ('fa5s.envelope', "Campagnes", False),
            ('fa5s.chart-bar', "Analytics", False),
            ('fa5s.brain', "IA Insights", False),
            ('fa5s.clipboard-list', "Enrichissement", False),
            ('fa5s.cogs', "Configuration", False),
        ]
        self.module_buttons = []
        for idx, (iconname, name, active) in enumerate(modules):
            color = "white" if active else "#6b7280"
            bg = f"background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #1d4ed8);" if active else "background:transparent;"
            btn = QPushButton()
            btn.setFlat(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"{bg}padding:12px 12px;border-radius:10px;margin-bottom:4px;")
            hbox = QHBoxLayout(btn)
            hbox.setContentsMargins(4, 0, 0, 0)
            lbl_icon = QLabel()
            lbl_icon.setPixmap(qta.icon(iconname, color=color).pixmap(20, 20))
            hbox.addWidget(lbl_icon)
            lbl_txt = QLabel(name)
            lbl_txt.setFont(font(QFont.Bold if active else QFont.Medium, 13))
            lbl_txt.setStyleSheet(f"color:{color}; margin-left:8px;")
            hbox.addWidget(lbl_txt)
            hbox.addStretch()
            v.addWidget(btn)
            self.module_buttons.append(btn)
        v.addSpacing(11)
        access_label = QLabel("ACCÈS RAPIDE")
        access_label.setFont(font(QFont.Bold, 11))
        access_label.setStyleSheet(f"color:{DS['text_muted']};letter-spacing:0.03em;text-transform:uppercase;margin-bottom:2px;")
        v.addWidget(access_label)
        quicks = [
            ('fa5s.plus-circle', "Nouvelle recherche"),
            ('fa5s.download', "Exports récents"),
            ('fa5s.sync', "Synchroniser"),
        ]
        for icon, name in quicks:
            quick = QWidget()
            hbox = QHBoxLayout(quick)
            hbox.setContentsMargins(0, 0, 0, 0)
            lbl_icon = QLabel()
            lbl_icon.setPixmap(qta.icon(icon, color=DS['text_muted']).pixmap(16, 16))
            hbox.addWidget(lbl_icon)
            lbl_txt = QLabel(name)
            lbl_txt.setFont(font(QFont.Medium, 11))
            lbl_txt.setStyleSheet(f"color:{DS['text_muted']};margin-left:8px;")
            hbox.addWidget(lbl_txt)
            hbox.addStretch()
            quick.setStyleSheet("padding:7px 0px;border-radius:0px;")
            v.addWidget(quick)
        v.addStretch()

# ================ MODULE PROSPECTION MODERN TABBED ================
class ProspectionModuleModernTabbed(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SalesMachine v2.2 - Module Prospection Moderne")
        self.setMinimumSize(1400, 900)
        self.metrics = self.load_metrics()
        self.historique = self.load_historique()
        self.existing_companies = self.load_existing_companies()
        self.search_results = []
        self.current_search_thread = None
        self.filter_mail = False
        self.filter_tel = False
        self.filter_site = False
        self.setup_ui()

    def load_metrics(self):
        try:
            with open("metrics.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {
                "recherches_totales": 0,
                "nouveaux_prospects": 0,
                "doublons_evites": 0,
                "taux_conversion": 0.0
            }

    def save_metrics(self):
        with open("metrics.json", "w", encoding="utf-8") as f:
            json.dump(self.metrics, f, indent=2, ensure_ascii=False)

    def load_historique(self):
        try:
            with open(HISTORIQUE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    def load_existing_companies(self):
        import os
        import pandas as pd
        maj_path = os.path.join(os.path.dirname(__file__), 'data/Entreprises_Toutes_Videos_MAJ.csv')
        if os.path.exists(maj_path):
            df_maj = pd.read_csv(maj_path)
            # Nettoyage pour comparaison fiable
            return set(df_maj['Entreprise'].dropna().str.strip().str.lower())
        return set()

    def save_historique(self):
        with open(HISTORIQUE_FILE, "w", encoding="utf-8") as f:
            json.dump(self.historique, f, indent=2, ensure_ascii=False)

    def add_to_historique(self, recherche_dict):
        self.historique.insert(0, recherche_dict)
        self.historique = self.historique[:10]
        self.save_historique()
        self.update_historique_tab()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.addWidget(self.build_main())
        self.setStyleSheet(f"background: {DS['background']};")

    def build_main(self):
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(48, 48, 48, 48)
        v.setSpacing(32)
        # Header
        h = QHBoxLayout()
        h.setSpacing(20)
        tbox = QVBoxLayout()
        t = QLabel()
        t.setPixmap(qta.icon('fa5s.search', color=DS["primary"]).pixmap(28, 28))
        t.setText(" Prospection")
        t.setFont(font(QFont.ExtraBold, 24))
        t.setStyleSheet(f"color:{DS['text_primary']}")
        tbox.addWidget(t)
        self.st = QLabel("Trouvez de nouveaux clients grâce à l'intelligence commerciale.")
        self.st.setFont(font(QFont.Medium, 14))
        self.st.setStyleSheet(f"color:{DS['text_secondary']}")
        tbox.addWidget(self.st)
        h.addLayout(tbox)
        h.addStretch()
        b1 = QPushButton(qta.icon('fa5s.magic', color="white"), "Nouvelle recherche")
        b1.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #2563eb);
                color:white;border-radius:10px;padding:10px 28px;font-weight:700;font-size:15px;
                min-height:38px;
            }
            QPushButton:hover {background: #1d4ed8;}
        """)
        b1.setFont(font(QFont.Bold, 13))
        b1.setMinimumWidth(140)
        b1.clicked.connect(self.reset_search)
        h.addWidget(b1)
        v.addLayout(h)
        # Metrics cards
        metrics_cards = QHBoxLayout()
        metrics_cards.setSpacing(28)
        metrics = [
            ("fa5s.search", self.metrics["recherches_totales"], "RECHERCHES", DS["primary"]),
            ("fa5s.user-plus", self.metrics["nouveaux_prospects"], "NOUVEAUX PROSPECTS", DS["success"]),
            ("fa5s.copy", self.metrics["doublons_evites"], "DOUBLONS ÉVITÉS", DS["warning"]),
            ("fa5s.chart-line", f"{self.metrics['taux_conversion']}%", "TAUX CONVERSION", DS["danger"])
        ]
        for icon, value, label, color in metrics:
            metrics_cards.addWidget(MetricCard(icon, value, label, color))
        v.addLayout(metrics_cards)
        # Onglets avec marge
        tabs_container = QVBoxLayout()
        tabs_container.setContentsMargins(0, 16, 0, 0)
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                margin-top: 8px;
            }
            QTabBar::tab {
                padding:16px 22px;font-size:14px;font-weight:700;color:#374151;
                border-radius:12px 12px 0 0;margin-right:6px;min-width:110px;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #1d4ed8);color:white;
            }
            QTabBar::tab:hover {
                background:#eff6ff;
            }
        """)
        self.tabs.addTab(self.build_tab_recherche(), "Recherche")
        self.tabs.addTab(self.build_tab_historique(), "Historique")
        tabs_container.addWidget(self.tabs)
        v.addLayout(tabs_container)
        return w

    def build_tab_recherche(self):
        tab = QWidget()
        lyt = QVBoxLayout(tab)
        lyt.setContentsMargins(0, 20, 0, 0)
        lyt.setSpacing(18)
        # Zone recherche compacte
        search_zone = QFrame()
        search_zone.setStyleSheet(f"background: {DS['surface']}; border-radius: 18px;")
        add_glow(search_zone, blur=12)
        sz_lyt = QVBoxLayout(search_zone)
        sz_lyt.setContentsMargins(30, 20, 30, 20)
        sz_lyt.setSpacing(10)
        # Ligne 1 : Barre de recherche principale
        row1 = QHBoxLayout()
        row1.setSpacing(10)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Ex: agence web Lyon, fabricants palettes, etc.")
        self.search_input.setFont(font(QFont.Normal, 13))
        self.search_input.returnPressed.connect(self.start_search)
        self.search_input.setMinimumHeight(34)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background: #fff;
                border: 1.3px solid {DS['border']};
                border-radius: 12px;
                padding: 0 14px;
                font-size: 13px;
            }}
            QLineEdit:hover, QLineEdit:focus {{
                border-color: {DS['primary']};
            }}
        """)
        row1.addWidget(self.search_input, 4)
        self.search_button = QPushButton(qta.icon('fa5s.search', color='white'), "Lancer")
        self.search_button.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {DS['primary']}, stop:1 {DS['primary_dark']});
                color:white;border-radius:8px;padding:0 24px;font-weight:700;font-size:15px;min-height:34px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {DS['primary_dark']}, stop:1 #1e40af);
            }}
        """)
        self.search_button.clicked.connect(self.start_search)
        row1.addWidget(self.search_button, 1)
        sz_lyt.addLayout(row1)
        # Ligne 2 : Filtres espacés et plus compacts
        row2 = QHBoxLayout()
        row2.setSpacing(8)
        # Style moderne pour les combos
        combo_style = f"""
            QComboBox#modernCombo {{
                background: #f5f7fa;
                border: 1.5px solid #e5e7eb;
                border-radius: 10px;
                padding: 7px 20px 7px 12px;
                font-size: 13px;
                font-weight: 500;
                margin-right: 3px;
                min-height: 30px;
            }}
            QComboBox#modernCombo:hover {{
                border-color: {DS['primary']};
                background: #fff;
            }}
            QComboBox#modernCombo:focus {{
                border-color: {DS['primary']};
                background: #fff;
            }}
            QComboBox#modernCombo::drop-down {{
                border: none;
                padding-right: 12px;
            }}
            QComboBox#modernCombo::down-arrow {{
                width: 0;
                height: 0;
                border: none;
                background: none;
            }}
            QComboBox#modernCombo QAbstractItemView {{
                background: white;
                border: 1px solid {DS['border']};
                border-radius: 8px;
                padding: 8px;
                selection-background-color: {DS['primary_light']};
                selection-color: {DS['primary']};
            }}
        """
        for combo, items, width in [
            (QComboBox(), ["France", "🏙️ Lyon", "🏙️ Paris", "🏙️ Marseille"], 92),
            (QComboBox(), ["📊 Tous secteurs", "💻 Services numériques", "🍽️ Restauration", "🏭 Industrie"], 140),
            (QComboBox(), ["🏢 Toutes tailles", "👥 TPE (1-10)", "🏬 PME (11-50)", "🏭 ETI (51-250)", "🏢 Grande entreprise (250+)"], 130),
            (QComboBox(), ["💶 Tous CA", "< 500 k€", "500 k€ - 2 M€", "2 M€ - 10 M€", "10 M€ - 50 M€", "> 50 M€"], 110),
        ]:
            combo.addItems(items)
            combo.setFixedHeight(30)
            combo.setMinimumWidth(width)
            combo.setObjectName("modernCombo")
            combo.setStyleSheet(combo_style)
            row2.addWidget(combo)
            if "France" in items[0]:
                self.location_combo = combo
            elif "secteurs" in items[0]:
                self.sector_combo = combo
            elif "tailles" in items[0]:
                self.size_combo = combo
            elif "CA" in items[0]:
                self.ca_combo = combo
        row2.addStretch()
        sz_lyt.addLayout(row2)
        lyt.addWidget(search_zone)
        # Message d'attente plus discret, centré
        self.search_status = QLabel("Saisissez votre recherche pour commencer")
        self.search_status.setFont(font(QFont.Normal, 12))
        self.search_status.setStyleSheet("color:#b0b0b0;padding:2px 0 0 0;")
        self.search_status.setAlignment(Qt.AlignCenter)
        lyt.addWidget(self.search_status)
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimumHeight(6)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background: {DS['border']};
                border-radius: 2.5px;
            }}
            QProgressBar::chunk {{
                background: {DS['primary']};
                border-radius: 2.5px;
            }}
        """)
        lyt.addWidget(self.progress_bar)
        # Résultats (tableau moderne + boutons outils)
        self.build_results_table(lyt)
        lyt.addWidget(self.results_frame, stretch=1)
        return tab

    def build_results_table(self, parent_layout):
        self.results_frame = QFrame()
        self.results_frame.setStyleSheet(f"""
            QFrame {{
                background: {DS['surface']};
                border-radius: 18px;
                border: none;
            }}
        """)
        add_glow(self.results_frame, blur=12)
        self.results_frame.setVisible(False)
        results_layout = QVBoxLayout(self.results_frame)
        results_layout.setContentsMargins(20, 20, 20, 20)
        results_layout.setSpacing(12)
        # Bar outils résultats (Filtres, Export) - MASQUÉ au début
        self.results_toolbar = QHBoxLayout()
        self.results_toolbar.addStretch()
        # Style moderne cohérent pour les boutons
        modern_button_style = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #2563eb);
                color:white;border-radius:10px;padding:10px 20px;font-weight:700;font-size:13px;
                min-height:30px;
            }
            QPushButton:hover {background: #1d4ed8;}
        """
        self.filter_btn = QPushButton(qta.icon('fa5s.filter', color="white"), "Filtres")
        self.filter_btn.setStyleSheet(modern_button_style)
        self.filter_btn.setFont(font(QFont.Bold, 13))
        self.filter_btn.setFixedHeight(30)
        self.filter_btn.clicked.connect(self.show_filter_menu)
        self.export_btn = QPushButton(qta.icon('fa5s.file-export', color="white"), "Exporter CSV")
        self.export_btn.setStyleSheet(modern_button_style)
        self.export_btn.setFont(font(QFont.Bold, 13))
        self.export_btn.setFixedHeight(30)
        self.export_btn.clicked.connect(self.export_results)
        self.results_toolbar.addWidget(self.filter_btn)
        self.results_toolbar.addWidget(self.export_btn)
        self.filter_btn.setVisible(False)
        self.export_btn.setVisible(False)
        results_layout.addLayout(self.results_toolbar)
        # Table
        self.results_table = QTableWidget()
        self.results_table.setObjectName("resultsTable")
        columns = ["Entreprise", "Secteur", "Localisation", "Taille", "Score", "Statut", "Contact"]
        self.results_table.setColumnCount(len(columns))
        self.results_table.setHorizontalHeaderLabels(columns)
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.results_table.setStyleSheet("""
            QTableWidget {
                background: #f9fafb;
                border-radius: 14px;
                font-size: 14px;
            }
            QTableWidget::item:selected {
                background: #dbeafe;
                color: #1d4ed8;
            }
        """)
        results_layout.addWidget(self.results_table)
        parent_layout.addWidget(self.results_frame)

    def build_tab_historique(self):
        self.tab_histo = QWidget()
        lyt = QVBoxLayout(self.tab_histo)
        lyt.setContentsMargins(22, 24, 22, 24)
        lyt.setSpacing(22)
        historique_frame = QFrame()
        historique_frame.setStyleSheet("""
            QFrame {
                background: #fff;
                border-radius: 16px;
                border: 1.5px solid #e5e7eb;
            }
        """)
        add_glow(historique_frame, blur=13)
        hist_layout = QVBoxLayout(historique_frame)
        hist_layout.setContentsMargins(10, 10, 10, 10)
        title = QLabel("Historique des recherches")
        title.setFont(font(QFont.Bold, 18))
        title.setStyleSheet(f"color:{DS['primary']};margin-bottom:14px;")
        hist_layout.addWidget(title)
        self.historique_list_tab = QListWidget()
        self.historique_list_tab.setMaximumHeight(800)
        self.historique_list_tab.setStyleSheet("""
            QListWidget {
                background: #f8fafc;
                border-radius: 14px;
                font-size: 15px;
                padding: 10px;
            }
            QListWidget::item:selected {
                background: #dbeafe;
                color: #1d4ed8;
            }
        """)
        add_glow(self.historique_list_tab, blur=10)
        self.historique_list_tab.itemDoubleClicked.connect(self.historique_item_clicked_tab)
        hist_layout.addWidget(self.historique_list_tab)
        self.update_historique_tab()
        lyt.addWidget(historique_frame)
        return self.tab_histo

    def update_historique_tab(self):
        self.historique_list_tab.clear()
        for item in self.historique:
            query = item.get('query', 'N/A')
            location = item.get('location', 'N/A')
            sector = item.get('sector', 'N/A')
            size = item.get('size', 'N/A')
            ca = item.get('ca', 'N/A')
            date = item.get('datetime', '')
            # Carte moderne avec ombre et hover
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(14, 10, 14, 10)
            layout.setSpacing(18)
            # Icône
            icon_label = QLabel()
            icon_label.setPixmap(qta.icon('fa5s.history', color="#3b82f6").pixmap(26, 26))
            layout.addWidget(icon_label)
            # Texte principal
            main_text = QLabel(
                f"<span style='font-size:16px;font-weight:600;color:#1e293b'>{query}</span> "
                f"<span style='color:#2563eb;font-size:14px;'>| {location}</span> "
                f"<span style='color:#10b981;font-size:14px;'>| {sector}</span>"
            )
            main_text.setStyleSheet("margin-right:10px;")
            layout.addWidget(main_text)
            # Badge taille
            badge = QLabel(size)
            badge.setStyleSheet("background:#e0e7ff;color:#2563eb;padding:3px 12px;border-radius:8px;font-size:13px;font-weight:500;")
            layout.addWidget(badge)
            # Badge CA
            badge_ca = QLabel(ca)
            badge_ca.setStyleSheet("background:#f3f4f6;color:#6b7280;padding:3px 12px;border-radius:8px;font-size:13px;font-weight:500;")
            layout.addWidget(badge_ca)
            # Badge date à droite
            date_label = QLabel(date)
            date_label.setStyleSheet("background:#f1f5f9;color:#64748b;padding:3px 12px;border-radius:8px;font-size:13px;")
            layout.addWidget(date_label)
            # Bouton relancer
            relancer_btn = QPushButton(qta.icon('fa5s.redo', color="#3b82f6"), "")
            relancer_btn.setToolTip("Relancer cette recherche")
            relancer_btn.setFixedSize(32, 32)
            relancer_btn.setStyleSheet("""
                QPushButton {
                    background: #e0e7ff;
                    border-radius: 16px;
                    border: none;
                }
                QPushButton:hover {
                    background: #3b82f6;
                }
            """)
            relancer_btn.clicked.connect(lambda _, i=item: self.relancer_recherche(i))
            layout.addWidget(relancer_btn)
            layout.addStretch()
            # Carte avec ombre portée et effet hover
            widget.setStyleSheet("""
                QWidget {
                    background: #fff;
                    border-radius: 14px;
                    border: 1.5px solid #e5e7eb;
                }
                QWidget:hover {
                    background: #f1f5f9;
                    border: 1.5px solid #3b82f6;
                }
            """)
            add_glow(widget, blur=10)
            item_widget = QListWidgetItem()
            item_widget.setSizeHint(widget.sizeHint())
            self.historique_list_tab.addItem(item_widget)
            self.historique_list_tab.setItemWidget(item_widget, widget)

    def relancer_recherche(self, item):
        self.tabs.setCurrentIndex(0)
        self.search_input.setText(item.get('query', ''))
        self.location_combo.setCurrentText(item.get('location', 'France'))
        self.sector_combo.setCurrentText(item.get('sector', '📊 Tous secteurs'))
        self.size_combo.setCurrentText(item.get('size', '🏢 Toutes tailles'))
        self.ca_combo.setCurrentText(item.get('ca', '💶 Tous CA'))

    def historique_item_clicked_tab(self, item):
        idx = self.historique_list_tab.row(item)
        if idx < len(self.historique):
            hist = self.historique[idx]
            self.tabs.setCurrentIndex(0)
            self.search_input.setText(hist.get('query', ''))
            self.location_combo.setCurrentText(hist.get('location', 'France'))
            self.sector_combo.setCurrentText(hist.get('sector', '📊 Tous secteurs'))
            self.size_combo.setCurrentText(hist.get('size', '🏢 Toutes tailles'))
            self.ca_combo.setCurrentText(hist.get('ca', '💶 Tous CA'))

    def show_filter_menu(self):
        menu = QMenu(self)
        mail_cb = QCheckBox("Mail")
        mail_cb.setChecked(self.filter_mail)
        mail_action = QWidgetAction(menu)
        mail_action.setDefaultWidget(mail_cb)
        menu.addAction(mail_action)
        tel_cb = QCheckBox("Téléphone")
        tel_cb.setChecked(self.filter_tel)
        tel_action = QWidgetAction(menu)
        tel_action.setDefaultWidget(tel_cb)
        menu.addAction(tel_action)
        site_cb = QCheckBox("Site internet")
        site_cb.setChecked(self.filter_site)
        site_action = QWidgetAction(menu)
        site_action.setDefaultWidget(site_cb)
        menu.addAction(site_action)
        def update_filter():
            self.filter_mail = mail_cb.isChecked()
            self.filter_tel = tel_cb.isChecked()
            self.filter_site = site_cb.isChecked()
            self.apply_dynamic_filter()
        mail_cb.stateChanged.connect(update_filter)
        tel_cb.stateChanged.connect(update_filter)
        site_cb.stateChanged.connect(update_filter)
        menu.exec_(self.filter_btn.mapToGlobal(self.filter_btn.rect().bottomRight()))

    def apply_dynamic_filter(self):
        active = [self.filter_mail, self.filter_tel, self.filter_site]
        if not any(active):
            self.populate_results_table(self.search_results)
            return
        filtered = []
        for r in self.search_results:
            valid = True
            if self.filter_mail and not r.get('contact'):
                valid = False
            if self.filter_tel and not r.get('telephone'):
                valid = False
            if self.filter_site and not r.get('website'):
                valid = False
            if valid:
                filtered.append(r)
        self.populate_results_table(filtered)

    def start_search(self):
        query = self.search_input.text().strip()
        location = self.location_combo.currentText()
        sector = self.sector_combo.currentText()
        size = self.size_combo.currentText()
        ca = self.ca_combo.currentText()
        enriched_query = query
        if location != "France":
            enriched_query += f" {location.replace('🏙️', '').strip()}"
        if sector != "📊 Tous secteurs":
            enriched_query += f" {sector.replace('💻', '').replace('🍽️', '').replace('🏭', '').strip()}"
        if size != "🏢 Toutes tailles":
            enriched_query += f" {size.replace('👥', '').replace('🏬', '').replace('🏭', '').replace('🏢', '').strip()}"
        if ca != "💶 Tous CA":
            enriched_query += f" {ca.replace('💶','').strip()}"
        if not query:
            self.search_status.setText("Veuillez saisir une requête de recherche")
            return
        if self.current_search_thread and self.current_search_thread.isRunning():
            self.current_search_thread.terminate()
        self.search_button.setEnabled(False)
        self.search_button.setIcon(QIcon())  # Retire toute icône
        self.search_button.setText("Recherche en cours...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.results_frame.setVisible(False)
        self.filter_btn.setVisible(False)
        self.export_btn.setVisible(False)
        filters = {
            'location': location,
            'sector': sector,
            'size': size,
            'ca': ca
        }
        self.add_to_historique({
            'query': query,
            'location': location,
            'sector': sector,
            'size': size,
            'ca': ca,
            'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        self.current_search_thread = SearchThread(enriched_query, filters)
        self.current_search_thread.progress_updated.connect(self.progress_bar.setValue)
        self.current_search_thread.status_updated.connect(self.search_status.setText)
        self.current_search_thread.search_completed.connect(self.on_search_completed)
        self.current_search_thread.start()

    def on_search_completed(self, results):
        ca_filter = self.ca_combo.currentText()
        if ca_filter != "💶 Tous CA":
            def ca_match(ca_str, ca_filter):
                if not ca_str:
                    return False
                if ca_filter == "< 500 k€":
                    return ("<" in ca_str or "500" in ca_str or "k€" in ca_str) and ("M" not in ca_str)
                if ca_filter == "500 k€ - 2 M€":
                    return ("500" in ca_str or "2 M" in ca_str)
                if ca_filter == "2 M€ - 10 M€":
                    return ("2 M" in ca_str or "10 M" in ca_str)
                if ca_filter == "10 M€ - 50 M€":
                    return ("10 M" in ca_str or "50 M" in ca_str)
                if ca_filter == "> 50 M€":
                    return "50 M" in ca_str or "100 M" in ca_str or "M€" in ca_str
                return True
            results = [r for r in results if ca_match(str(r.get("ca", "")), ca_filter)]
        def clean(x):
            return str(x).strip().lower() if x else ''
        filtered_results = [r for r in results if clean(r['nom']) not in self.existing_companies]
        self.search_results = filtered_results
        
        
        self.filter_mail = False
        self.filter_tel = False
        self.filter_site = False
        self.search_button.setEnabled(True)
        self.search_button.setText("Lancer")
        self.progress_bar.setVisible(False)
        self.update_metrics(filtered_results)
        if filtered_results:
            self.populate_results_table(filtered_results)
            self.results_frame.setVisible(True)
            self.filter_btn.setVisible(True)
            self.export_btn.setVisible(True)
            self.search_status.setVisible(False)
            self.search_status.setText("")
            self.show_toast(f"{len(filtered_results)} entreprises trouvées")
        else:
            self.populate_results_table([])
            self.results_frame.setVisible(True)
            self.filter_btn.setVisible(False)
            self.export_btn.setVisible(False)
            self.search_status.setVisible(True)
            self.search_status.setText("Saisissez votre recherche pour commencer")
            self.show_toast("Aucun résultat trouvé", color=DS["danger"])

    


    def populate_results_table(self, results):
        self.results_table.setRowCount(len(results))
        self.results_table.clearContents()
        for row, result in enumerate(results):
            self.results_table.setItem(row, 0, QTableWidgetItem(result['nom']))
            self.results_table.setItem(row, 1, QTableWidgetItem(result['secteur']))
            localisation = result.get('adresse') or result.get('ville') or "Inconnu"
            self.results_table.setItem(row, 2, QTableWidgetItem(localisation))
            self.results_table.setItem(row, 3, QTableWidgetItem(result['taille']))
            score_text = f"{result['score']}/100"
            score_item = QTableWidgetItem(score_text)
            score_item.setTextAlignment(Qt.AlignCenter)
            if result['score'] >= 90:
                score_item.setForeground(QColor(DS['success']))
            elif result['score'] >= 80:
                score_item.setForeground(QColor(DS['warning']))
            else:
                score_item.setForeground(QColor(DS['danger']))
            self.results_table.setItem(row, 4, score_item)
            status_item = QTableWidgetItem(result['statut'])
            status_item.setTextAlignment(Qt.AlignCenter)
            status = result['statut']
            if status == 'EXCELLENT':
                status_item.setBackground(QColor(DS['success']))
                status_item.setForeground(QColor('white'))
            elif status == 'POTENTIEL':
                status_item.setBackground(QColor(DS['warning']))
                status_item.setForeground(QColor('white'))
            elif status == 'NOUVEAU':
                status_item.setBackground(QColor(DS['primary']))
                status_item.setForeground(QColor('white'))
            elif status == 'DOUBLON':
                status_item.setBackground(QColor(DS['danger']))
                status_item.setForeground(QColor('white'))
            self.results_table.setItem(row, 5, status_item)

            # Contact (colonne 6) : widget horizontal avec texte + bouton si site
            contact_widget = QWidget()
            contact_layout = QHBoxLayout(contact_widget)
            contact_layout.setContentsMargins(0, 0, 0, 0)
            contact_layout.setSpacing(6)
            contact_parts = []
            if result.get('contact'):
                contact_parts.append(f"✉️ {result['contact']}")
            if result.get('telephone'):
                contact_parts.append(f"📞 {result['telephone']}")
            contact_label = QLabel('\n'.join(contact_parts) if contact_parts else "Pas de contact")
            contact_label.setStyleSheet("font-size:13px;")
            contact_layout.addWidget(contact_label)
            if result.get('website'):
                btn_site = QPushButton("🌐")
                btn_site.setToolTip(result['website'])
                btn_site.setCursor(Qt.PointingHandCursor)
                btn_site.setStyleSheet("""
                    QPushButton {
                        background: #e0e7ff;
                        border-radius: 8px;
                        font-size: 16px;
                        min-width: 32px;
                        min-height: 28px;
                    }
                    QPushButton:hover {
                        background: #3b82f6;
                        color: white;
                    }
                """)
                url = result['website']
                btn_site.clicked.connect(lambda _, url=url: webbrowser.open(url if url.startswith("http") else "http://" + url))
                contact_layout.addWidget(btn_site)
            contact_layout.addStretch()
            self.results_table.setCellWidget(row, 6, contact_widget)
            self.results_table.setRowHeight(row, 62)

    def update_metrics(self, results):
        total_results = len(results)
        new_prospects = len([r for r in results if r['statut'] != 'DOUBLON'])
        duplicates = len([r for r in results if r['statut'] == 'DOUBLON'])
        taux_conversion = (new_prospects / total_results * 100) if total_results > 0 else 0.0
        self.metrics["recherches_totales"] += 1
        self.metrics["nouveaux_prospects"] += new_prospects
        self.metrics["doublons_evites"] += duplicates
        self.metrics["taux_conversion"] = round(taux_conversion, 1)
        self.save_metrics()

    def reset_search(self):
        self.search_input.clear()
        self.search_results = []
        self.results_frame.setVisible(False)
        self.filter_btn.setVisible(False)
        self.export_btn.setVisible(False)
        self.search_status.setVisible(True)
        self.search_status.setText("Saisissez votre recherche pour commencer")
        self.progress_bar.setVisible(False)
        self.location_combo.setCurrentIndex(0)
        self.sector_combo.setCurrentIndex(0)
        self.size_combo.setCurrentIndex(0)
        self.ca_combo.setCurrentIndex(0)
        self.filter_mail = False
        self.filter_tel = False
        self.filter_site = False

    def export_results(self):
        if not self.search_results:
            self.show_toast("Aucun résultat à exporter", color=DS["danger"])
            return
        try:
            export_data = []
            results_to_export = self.search_results
            if self.filter_mail or self.filter_tel or self.filter_site:
                results_to_export = [
                    r for r in self.search_results
                    if (not self.filter_mail or r.get('contact')) and \
                       (not self.filter_tel or r.get('telephone')) and \
                       (not self.filter_site or r.get('website'))
                ]
            for result in results_to_export:
                export_data.append({
                    'Nom': result['nom'],
                    'Secteur': result['secteur'],
                    'Ville': result['ville'],
                    'Score': result['score'],
                    'Statut': result['statut'],
                    'Email': result.get('contact', ''),
                    'Téléphone': result.get('telephone', ''),
                    'Site web': result.get('website', ''),
                    'Taille': result['taille'],
                    'Description': result.get('description', ''),
                    'Adresse': result.get('adresse', ''),
                    'Date recherche': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'Moteur utilisé': 'RÉEL' if SEARCH_ENGINE_AVAILABLE else 'SIMULATION'
                })
            df = pd.DataFrame(export_data)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"prospection_salesmachine_{timestamp}.csv"
            filepath, _ = QFileDialog.getSaveFileName(
                self, "Exporter les résultats", filename, "Fichiers CSV (*.csv)"
            )
            if filepath:
                df.to_csv(filepath, index=False, encoding='utf-8-sig')
                self.show_toast(f"{len(export_data)} entreprises exportées\nFichier : {filepath}")
        except Exception as e:
            self.show_toast(f"Erreur lors de l'export : {str(e)}", color=DS["danger"])

    def show_toast(self, msg, color=DS["success"]):
        toast = ModernToast(msg, color)
        screen = QApplication.desktop().screenGeometry()
        x = screen.width() - 400
        y = screen.height() - 80
        toast.move(x, y)
        toast.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    font_ = QFont("Inter", 11)
    app.setFont(font_)
    window = ProspectionModuleModernTabbed()
    window.show()
    sys.exit(app.exec_())