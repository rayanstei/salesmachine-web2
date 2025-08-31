# -*- coding: utf-8 -*-
"""
IA INSIGHTS - MAQUETTE FINALE 2024
Module complet prêt à brancher sur tes fichiers métiers/data.
Version PATCHÉE : 
- Affiche bien TOUS les secteurs spécialisés/prometteurs/saturés dans chaque onglet (avec rotation par 4, bouton "Actualiser").
- Générateur contient la base complète (copiée de ton ancien script), avec toutes les sous-catégories et métiers.
- L'interface, design, style et structure sont inchangés.
"""

import sys
import os
import random
import webbrowser
import qtawesome as qta
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QColor, QPainter
from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QScrollArea

# ====== DATASETTINGS (VISUEL) ======
DS = {
    "primary": "#3b82f6",
    "primary_dark": "#1d4ed8",
    "success": "#10b981",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "background": "#ffffff",
    "surface": "#f9fafb",
    "surface_alt": "#f5f7fa",
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

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)
from data_repository import DataRepository
from config import DEFAULT_CONFIG
import salesmachine_validator_corrige as cse_search

SECTEURS_NON_EXPLOITABLES = [
    "culture du riz", "culture de céréales", "élevage de vaches", "élevage de porcs",
    "pêche en mer", "sylviculture", "chasse", "apiculture",
    "commerce de détail", "coiffure", "soins de beauté", "restauration",
    "débits de boissons", "boulangerie", "épicerie", "pharmacie",
    "administration publique", "enseignement primaire", "enseignement secondaire",
    "activités hospitalières", "action sociale",
    "industries extractives", "imprimerie de journaux", "autre imprimerie",
    "activités de pré-presse", "activités de soutien", "rechapage de pneumatiques",
    "autres activités", "activités diverses", "n.c.a.", "activités de post-production",
    "en plastique", "et de", "ou de", "activités de", "fabrication de autres",
    "commerce de détail de", "réparation de", "location de"
]

def est_secteur_exploitable(libelle_secteur):
    libelle_lower = libelle_secteur.lower()
    for terme_exclu in SECTEURS_NON_EXPLOITABLES:
        if terme_exclu in libelle_lower:
            return False
    return True

def filtrer_par_secteur_cible(secteur_ape, secteur_cible):
    secteurs_exclus = ['Autre', 'Secteur public / Administration', 'Enseignement / Éducation']
    if secteur_cible in secteurs_exclus:
        return False
    secteurs_b2b = [
        'Informatique / Numérique', 'Conseil / Services aux entreprises',
        'Commerce / Distribution', 'Bâtiment / Construction', 'Industrie',
        'Transport / Logistique', 'Agriculture / Agroalimentaire'
    ]
    return secteur_cible in secteurs_b2b

class RechercheThread(QThread):
    finished = pyqtSignal(list, str, str)
    def __init__(self, secteur_libelle, limite=25, parent=None):
        super().__init__(parent)
        self.secteur_libelle = secteur_libelle
        self.limite = limite
    def run(self):
        resultats = cse_search.lancer_recherche_entreprises_corrigee(self.secteur_libelle, self.limite)
        dossier_exports = "exports"
        dernier_export = ""
        if os.path.exists(dossier_exports):
            fichiers = [f for f in os.listdir(dossier_exports) if self.secteur_libelle.replace(" ", "_") in f and f.endswith(".xlsx")]
            if fichiers:
                fichiers.sort(reverse=True)
                dernier_export = os.path.join(dossier_exports, fichiers[0])
        self.finished.emit(resultats, self.secteur_libelle, dernier_export)

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

class SectionFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background: {DS['surface']};
                border: 1.5px solid {DS['border']};
                border-radius: 24px;
            }}
        """)
        add_glow(self, blur=18)

class CardFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background: #fff;
                border: none;
                border-radius: 16px;
            }
        """)
        add_glow(self, blur=7)

class Sidebar(QFrame):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(260)
        self.setObjectName("Sidebar")
        self.setStyleSheet(f"""
            QFrame#Sidebar {{
                background: {DS["background"]};
                border-right: 1.5px solid {DS["border"]};
            }}
        """)
        self.setup_ui()
    def setup_ui(self):
        v = QVBoxLayout(self)
        v.setContentsMargins(24, 32, 24, 24)
        v.setSpacing(24)
        logo_row = QHBoxLayout()
        logo = QLabel()
        logo.setPixmap(qta.icon('fa5s.robot', color='white').pixmap(44, 44))
        logo.setFixedSize(44, 44)
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet(f"background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {DS['primary']}, stop:1 {DS['primary_dark']});border-radius:8px;")
        logo_row.addWidget(logo)
        app_title = QLabel("SalesMachine")
        app_title.setFont(font(QFont.Bold, 16))
        app_title.setStyleSheet(f"color:{DS['text_primary']};margin-left:7px;")
        logo_row.addWidget(app_title)
        logo_row.addStretch()
        v.addLayout(logo_row)
        modules_label = QLabel("MODULES")
        modules_label.setFont(font(QFont.Bold, 11))
        modules_label.setStyleSheet(f"color:{DS['text_muted']};letter-spacing:0.04em;text-transform:uppercase;margin-bottom:3px;margin-top:7px;")
        v.addWidget(modules_label)
        modules = [
            ('fa5s.search', "Prospection"),
            ('fa5s.envelope', "Campagnes"),
            ('fa5s.chart-bar', "Analytics"),
            ('fa5s.brain', "IA Insights"),
            ('fa5s.clipboard-list', "Enrichissement"),
            ('fa5s.cogs', "Configuration"),
        ]
        active_idx = 3
        for idx, (iconname, name) in enumerate(modules):
            active = (idx == active_idx)
            color = "white" if active else "#6b7280"
            bg = f"background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #1d4ed8);" if active else "background:transparent;"
            mod = QWidget()
            hbox = QHBoxLayout(mod)
            hbox.setContentsMargins(4, 0, 0, 0)
            lbl_icon = QLabel()
            lbl_icon.setPixmap(qta.icon(iconname, color=color).pixmap(20, 20))
            hbox.addWidget(lbl_icon)
            lbl_txt = QLabel(name)
            lbl_txt.setFont(font(QFont.Bold if active else QFont.Medium, 13))
            lbl_txt.setStyleSheet(f"color:{color}; margin-left:8px;")
            hbox.addWidget(lbl_txt)
            hbox.addStretch()
            mod.setStyleSheet(f"{bg}padding:12px 12px;border-radius:10px;margin-bottom:4px;")
            v.addWidget(mod)
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

class GeneratorPanel(QWidget):
    """Générateur de secteurs - version complète de ta base métiers"""
    def __init__(self, parent_module):
        super().__init__()
        self.parent_module = parent_module
        self.setup_secteurs_database()
        self.setup_ui()
        self.current_category = "Industrie"
        self.refresh_secteurs()
    def setup_secteurs_database(self):
        self.secteurs_par_categorie = {
             "Industrie": {
                "Fabrication métallique": [
                    "Fabricants de palettes métalliques",
                    "Ateliers de chaudronnerie",
                    "Entreprises de soudure industrielle",
                    "Fabricants de grillages",
                    "Ateliers de tôlerie fine",
                    "Fabricants de structures métalliques",
                    "Entreprises de découpe laser",
                    "Ateliers d'usinage de précision"
                ],
                "Fabrication bois": [
                    "Fabricants de palettes bois",
                    "Menuiseries industrielles",
                    "Fabricants d'emballages bois",
                    "Scieries industrielles",
                    "Fabricants de caisses bois",
                    "Entreprises de traitement du bois",
                    "Fabricants de panneaux bois",
                    "Ateliers d'ébénisterie industrielle"
                ],
                "Plastique & Polymères": [
                    "Fabricants d'emballages plastiques",
                    "Entreprises d'injection plastique",
                    "Fabricants de films plastiques",
                    "Ateliers de thermoformage",
                    "Fabricants de tuyaux plastiques",
                    "Entreprises d'extrusion plastique",
                    "Fabricants de contenants plastiques",
                    "Recycleurs de plastiques"
                ],
                "Électronique & Composants": [
                    "Fabricants de circuits imprimés",
                    "Assembleurs de composants électroniques",
                    "Fabricants de connecteurs",
                    "Entreprises de câblage industriel",
                    "Fabricants de capteurs",
                    "Intégrateurs de systèmes électroniques",
                    "Fabricants d'éclairage LED",
                    "Entreprises d'automatisation"
                ]
            },

            "Services B2B": {
                "Maintenance & Réparation": [
                    "Maintenance de machines-outils",
                    "Réparation d'équipements industriels",
                    "Maintenance d'ascenseurs",
                    "Dépannage de systèmes informatiques",
                    "Maintenance de climatisation",
                    "Réparation de compresseurs",
                    "Maintenance de véhicules industriels",
                    "Services de maintenance préventive"
                ],
                "Nettoyage & Hygiène": [
                    "Nettoyage de bureaux",
                    "Nettoyage industriel",
                    "Services de décontamination",
                    "Nettoyage de vitres en hauteur",
                    "Entretien d'espaces verts",
                    "Nettoyage de sols techniques",
                    "Désinfection professionnelle",
                    "Nettoyage après sinistre"
                ],
                "Conseil & Expertise": [
                    "Conseil en informatique",
                    "Bureaux d'études techniques",
                    "Audit énergétique",
                    "Conseil en organisation",
                    "Expertise comptable",
                    "Conseil en sécurité",
                    "Formation professionnelle",
                    "Conseil en qualité"
                ],
                "Sécurité & Surveillance": [
                    "Gardiennage de sites",
                    "Sécurité événementielle",
                    "Installation d'alarmes",
                    "Télésurveillance",
                    "Transport de fonds",
                    "Protection rapprochée",
                    "Sécurité incendie",
                    "Contrôle d'accès"
                ]
            },

            "BTP & Construction": {
                "Gros œuvre": [
                    "Entreprises de terrassement",
                    "Maçonnerie générale",
                    "Construction métallique",
                    "Béton armé",
                    "Fondations spéciales",
                    "Démolition industrielle",
                    "Travaux publics",
                    "Construction modulaire"
                ],
                "Second œuvre": [
                    "Électricité industrielle",
                    "Plomberie industrielle",
                    "Installation de chauffage",
                    "Climatisation industrielle",
                    "Isolation thermique",
                    "Cloisons sèches",
                    "Faux plafonds",
                    "Revêtements de sols"
                ],
                "Spécialités": [
                    "Étanchéité industrielle",
                    "Couverture industrielle",
                    "Bardage métallique",
                    "Menuiserie aluminium",
                    "Vitrerie industrielle",
                    "Ascensoristes",
                    "Automatismes de bâtiment",
                    "Sécurité incendie"
                ]
            },

            "Transport & Logistique": {
                "Transport spécialisé": [
                    "Transport de matières dangereuses",
                    "Transport frigorifique",
                    "Transport exceptionnel",
                    "Transport de véhicules",
                    "Déménagement industriel",
                    "Transport de déchets",
                    "Transport express",
                    "Transport international"
                ],
                "Logistique": [
                    "Entreposage sous douane",
                    "Préparation de commandes",
                    "Cross-docking",
                    "Logistique e-commerce",
                    "Stockage frigorifique",
                    "Gestion d'inventaires",
                    "Emballage industriel",
                    "Distribution dernière mile"
                ]
            },

            "Commerce Spécialisé": {
                "Équipements industriels": [
                    "Distributeurs de machines-outils",
                    "Fournisseurs d'outillage professionnel",
                    "Négoce de matériel de manutention",
                    "Commerce d'équipements de soudage",
                    "Distributeurs de compresseurs",
                    "Fournisseurs d'EPI",
                    "Commerce de matériel électrique",
                    "Distributeurs de pompes industrielles"
                ],
                "Matières premières": [
                    "Négoce de métaux",
                    "Distribution de produits chimiques",
                    "Commerce de bois industriel",
                    "Fournisseurs de plastiques",
                    "Négoce de tissus techniques",
                    "Distribution de composants",
                    "Commerce de quincaillerie",
                    "Fournisseurs d'abrasifs"
                ]
            }
        }
    def setup_ui(self):
        gmain = QHBoxLayout(self)
        gmain.setContentsMargins(0, 0, 0, 0)
        cat_panel = QFrame()
        cat_panel.setFixedWidth(335)
        cat_panel.setStyleSheet("""
            QFrame {
                background: #fff;
                border: none;
                border-radius: 20px;
            }
        """)
        add_glow(cat_panel, blur=15)
        vcat = QVBoxLayout(cat_panel)
        vcat.setContentsMargins(32, 28, 32, 28)
        vcat.setSpacing(7)
        tcat = QLabel()
        tcat.setText("  <b>Catégories</b>")
        tcat.setFont(font(QFont.Bold, 16))
        tcat.setStyleSheet("color:#212121;")
        cat_icon = qta.icon('fa5s.folder-open', color=DS["warning"]).pixmap(22, 22)
        tcat.setPixmap(cat_icon)
        tcat.setIndent(4)
        vcat.addWidget(tcat)
        self.cat_buttons = {}
        for i, cat in enumerate(self.secteurs_par_categorie.keys()):
            btn = QPushButton(cat)
            btn.setObjectName("categoryBtn")
            btn.setCheckable(True)
            btn.setChecked(i == 0)
            btn.setFont(font(QFont.Bold if i==0 else QFont.Medium, 14))
            btn.setStyleSheet("""
                QPushButton {background:transparent;color:#212121;font-size:14px;text-align:left;padding:13px 16px 13px 12px;border-radius:12px;margin-bottom:2px;}
                QPushButton:checked {background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #1d4ed8);color:white;}
                QPushButton:hover {background:rgba(59,130,246,0.07);}
            """)
            btn.clicked.connect(lambda _, b=btn, c=cat: self.select_cat(b, c))
            vcat.addWidget(btn)
            self.cat_buttons[cat] = btn
        vcat.addStretch()
        gmain.addWidget(cat_panel)
        main_panel = QFrame()
        main_panel.setStyleSheet("""
            QFrame {
                background: #fff;
                border: none;
                border-radius: 20px;
            }
        """)
        add_glow(main_panel, blur=18)
        vmain = QVBoxLayout(main_panel)
        vmain.setContentsMargins(30, 30, 30, 30)
        vmain.setSpacing(13)
        header = QHBoxLayout()
        icat = QLabel()
        icat.setPixmap(qta.icon('fa5s.magic', color=DS['warning']).pixmap(25, 25))
        header.addWidget(icat)
        self.sector_title = QLabel("Générateur de secteurs à prospecter")
        self.sector_title.setFont(font(QFont.Bold, 19))
        self.sector_title.setStyleSheet("color:#1f2937;")
        header.addWidget(self.sector_title)
        header.addStretch()
        btn_nouvelles = QPushButton(qta.icon('fa5s.magic', color="white"), "Nouvelles idées")
        btn_nouvelles.setFont(font(QFont.Bold, 13))
        btn_nouvelles.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #1d4ed8);
                color:white;border-radius:11px;padding:10px 24px;font-weight:700;font-size:13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1d4ed8, stop:1 #3b82f6);
            }
        """)
        btn_nouvelles.clicked.connect(self.generate_new_ideas)
        header.addWidget(btn_nouvelles)
        vmain.addLayout(header)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; }")
        self.scroll_content = QWidget()
        self.scroll_vbox = QVBoxLayout(self.scroll_content)
        self.scroll_vbox.setContentsMargins(0,0,0,0)
        self.scroll_vbox.setSpacing(17)
        self.scroll_area.setWidget(self.scroll_content)
        vmain.addWidget(self.scroll_area)
        gmain.addWidget(main_panel)
    def generate_new_ideas(self):
        # Mélange les listes !
        for cat in self.secteurs_par_categorie:
            for sous_cat in self.secteurs_par_categorie[cat]:
                random.shuffle(self.secteurs_par_categorie[cat][sous_cat])
        self.refresh_secteurs()
        self.parent_module.show_toast("🔄 Nouvelles idées de secteurs proposées.")
    def refresh_secteurs(self):
        self.show_sectors(self.current_category)
    def select_cat(self, btn, cat):
        for b in self.cat_buttons.values():
            b.setChecked(b==btn)
        self.current_category = cat
        self.show_sectors(cat)
    def show_sectors(self, cat):
        self.sector_title.setText(cat)
        while self.scroll_vbox.count():
            child = self.scroll_vbox.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        sectors = self.secteurs_par_categorie[cat]
        for sous_cat, noms in sectors.items():
            block = QFrame()
            block.setStyleSheet("""
                QFrame {
                    background: #f6f7fd;
                    border-radius: 14px;
                    border: none;
                }
            """)
            vblock = QVBoxLayout(block)
            vblock.setContentsMargins(22, 12, 22, 12)
            vblock.setSpacing(8)
            htitle = QHBoxLayout()
            stitle = QLabel(f"<b>{sous_cat}</b>")
            stitle.setFont(font(QFont.Bold, 14))
            stitle.setStyleSheet("color:#212121;")
            badge = QLabel(str(len(noms)))
            badge.setFont(font(QFont.Bold, 12))
            badge.setStyleSheet("""
                background:#3b82f6;color:white;
                border-radius:9px;
                padding:2px 11px 2px 11px;
                margin-left:7px;
            """)
            htitle.addWidget(stitle)
            htitle.addWidget(badge)
            htitle.addStretch()
            vblock.addLayout(htitle)
            for name in noms:
                card = QFrame()
                card.setStyleSheet("""
                    QFrame {
                        background: #fff;
                        border-radius: 11px;
                        border: none;
                    }
                """)
                hcard = QHBoxLayout(card)
                hcard.setContentsMargins(18, 10, 18, 10)
                hcard.setSpacing(22)
                lab = QLabel(name)
                lab.setFont(font(QFont.Medium, 13))
                lab.setStyleSheet("color:#1a2540;")
                hcard.addWidget(lab)
                hcard.addStretch()
                btn = QPushButton(qta.icon('fa5s.rocket', color="white"), "Prospecter")
                btn.setFont(font(QFont.Bold, 12))
                btn.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2563eb, stop:1 #1d4ed8);
                        color:white;border-radius:8px;padding:7px 20px;font-weight:700;font-size:13px;
                    }
                    QPushButton:hover {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1d4ed8, stop:1 #2563eb);
                    }
                """)
                btn.setFixedHeight(34)
                btn.clicked.connect(lambda _, n=name, b=btn: self.launch_generator(n, b))
                hcard.addWidget(btn)
                vblock.addWidget(card)
            self.scroll_vbox.addWidget(block)
        self.scroll_vbox.addStretch()
    def launch_generator(self, secteur_nom, btn):
        self.parent_module.launch_prospection(secteur_nom, btn)

class MetricCard(QFrame):
    def __init__(self, icon, value, label, color="#ef4444"):
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

class ModernProgress(QWidget):
    def __init__(self, percent, color):
        super().__init__()
        self.value = 0
        self.target = percent
        self.color = color
        self.setFixedSize(100, 8)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._timer.start(12)
    def _animate(self):
        if self.value < self.target:
            self.value += max(0.5, (self.target - self.value) / 8)
            self.update()
        else:
            self.value = self.target
            self._timer.stop()
            self.update()
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(DS["border"]))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, 100, 8, 4, 4)
        painter.setBrush(QColor(self.color))
        painter.drawRoundedRect(0, 0, int(1.0 * self.value), 8, 4, 4)
        painter.end()

class ResultsTableWidget(QWidget):
    def __init__(self, DS, parent=None):
        super().__init__(parent)
        self.DS = DS
        self.table = QTableWidget()
        columns = ["Entreprise", "Secteur", "Localisation", "Taille", "Score", "Statut", "Contact"]
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.setColumnWidth(6, 220)
        self.table.horizontalHeader().setStretchLastSection(True)  
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(self.table.SelectRows)
        self.table.setStyleSheet("""
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
        layout = QVBoxLayout(self)
        layout.addWidget(self.table)

    def populate(self, results):
        self.table.setRowCount(len(results))
        self.table.clearContents()
        for row, result in enumerate(results):
            # Nom de l'entreprise
            self.table.setItem(row, 0, QTableWidgetItem(result.get('Nom', 'Inconnu')))
            # Secteur (vide si non présent)
            self.table.setItem(row, 1, QTableWidgetItem(''))
            # Localisation (vide si non présent)
            self.table.setItem(row, 2, QTableWidgetItem(''))
            # Taille (vide si non présent)
            self.table.setItem(row, 3, QTableWidgetItem(''))

            # Score (exemple : 100 si Email ou Téléphone ou Site, sinon 0)
            has_contact = bool(result.get('Email') or result.get('Téléphone') or result.get('Site'))
            score = 100 if has_contact else 0
            score_text = f"{score}/100"
            score_item = QTableWidgetItem(score_text)
            score_item.setTextAlignment(Qt.AlignCenter)
            if score >= 90:
                score_item.setForeground(QColor(self.DS['success']))
            elif score >= 80:
                score_item.setForeground(QColor(self.DS['warning']))
            else:
                score_item.setForeground(QColor(self.DS['danger']))
            self.table.setItem(row, 4, score_item)

            # Statut (exemple : EXCELLENT si score 100, NOUVEAU sinon)
            if score == 100:
                statut = "EXCELLENT"
                statut_color = self.DS['success']
            else:
                statut = "NOUVEAU"
                statut_color = self.DS['primary']
            status_item = QTableWidgetItem(statut)
            status_item.setTextAlignment(Qt.AlignCenter)
            status_item.setBackground(QColor(statut_color))
            status_item.setForeground(QColor('white'))
            self.table.setItem(row, 5, status_item)

            # Contact (colonne 6) : widget horizontal avec texte + bouton si site
            contact_widget = QWidget()
            contact_layout = QHBoxLayout(contact_widget)
            contact_layout.setContentsMargins(0, 0, 0, 0)
            contact_layout.setSpacing(6)
            contact_parts = []
            if result.get('Email'):
                contact_parts.append(f"✉️ {result.get('Email')}")
            if result.get('Téléphone'):
                contact_parts.append(f"📞 {result.get('Téléphone')}")
            contact_label = QLabel('\n'.join(contact_parts) if contact_parts else "Pas de contact")
            contact_label.setStyleSheet("font-size:13px;")
            contact_layout.addWidget(contact_label)
            if result.get('Site'):
                btn_site = QPushButton("🌐")
                btn_site.setToolTip(result['Site'])
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
                url = result['Site']
                btn_site.clicked.connect(lambda _, url=url: webbrowser.open(url if url.startswith("http") else "http://" + url))
                contact_layout.addWidget(btn_site)
            contact_layout.addStretch()
            self.table.setCellWidget(row, 6, contact_widget)
            self.table.setRowHeight(row, 62)

class IAInsightsModule(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IA Insights - SaaS Moderne")
        self.resize(1400, 900)
        self.repo = DataRepository()
        self.load_data()
        self.existing_companies = self.load_existing_companies()
        self.metrics, self.secteurs_by_cat = self.analyse_opportunites()
        self.current_category = "tres-faible"
        self.recherche_thread = None
        self.rotation_indices = {cat: 0 for cat in self.secteurs_by_cat}
        self.setup_ui()
    def load_data(self):
        self.repo.load_all(
            DEFAULT_CONFIG["crm_path"],
            DEFAULT_CONFIG["ape_path"],
            DEFAULT_CONFIG["rome_path"],
            DEFAULT_CONFIG["naf_col"]

            
        )
    

    def load_existing_companies(self):
        import os
        import pandas as pd
        # Chemin du fichier Entreprises_Toutes_Videos_MAJ.csv (remonte d'un dossier)
        maj_path = os.path.join(os.path.dirname(__file__), '..', 'Entreprises_Toutes_Videos_MAJ.csv')
        maj_path = os.path.abspath(maj_path)
        if os.path.exists(maj_path):
            df_maj = pd.read_csv(maj_path)
            # Nettoyage pour comparaison fiable
            return set(df_maj['Entreprise'].dropna().str.strip().str.lower())
        return set()

    def analyse_opportunites(self):
        import pandas as pd
        try:
            entreprises = self.repo.get_entreprises()
            secteurs_ape = self.repo.get_secteurs()
            crm_path = os.path.join(os.path.dirname(__file__), 'crm.csv')
            df_crm = pd.read_csv(crm_path)
            if not entreprises or not secteurs_ape:
                return self.generer_metriques_vides()
            secteur_mapping = {}
            if 'code_ape_mappe' in df_crm.columns and 'secteur_cible' in df_crm.columns:
                for _, row in df_crm.iterrows():
                    code = row.get('code_ape_mappe')
                    secteur = row.get('secteur_cible')
                    if code and secteur:
                        secteur_mapping[code] = secteur
            ape_count = {}
            total_crm = len(entreprises)
            for ent in entreprises:
                ape = getattr(ent, 'code_ape', None)
                if ape:
                    ape_count[ape] = ape_count.get(ape, 0) + 1
            secteurs_metrics = []
            for secteur in secteurs_ape:
                secteur_cible = secteur_mapping.get(secteur.code, 'Autre')
                if (est_secteur_exploitable(secteur.libelle) and
                    filtrer_par_secteur_cible(secteur.code, secteur_cible)):
                    nb_crm = ape_count.get(secteur.code, 0)
                    couverture = (nb_crm / total_crm) * 100 if total_crm else 0
                    secteurs_metrics.append({
                        "title": secteur.libelle,
                        "code": secteur.code,
                        "couverture": round(couverture, 1),
                        "nb_crm": nb_crm,
                        "secteur": secteur_cible,
                    })
        except Exception as e:
            print(f"❌ Erreur analyse hybride: {e}")
            return self.generer_metriques_vides()
        def classify_couverture(couv):
            if couv <= 2:
                return "tres-faible"
            elif couv <= 8:
                return "partiel"
            return "fort"
        secteurs_by_cat = {"tres-faible": [], "partiel": [], "fort": []}
        for s in secteurs_metrics:
            cat = classify_couverture(s["couverture"])
            secteurs_by_cat[cat].append(s)
        secteurs_by_cat["tres-faible"].sort(key=lambda x: x["couverture"])
        secteurs_by_cat["partiel"].sort(key=lambda x: x["couverture"])
        secteurs_by_cat["fort"].sort(key=lambda x: -x["couverture"])
        metrics = {
            "tres-faible": len(secteurs_by_cat["tres-faible"]),
            "partiel": len(secteurs_by_cat["partiel"]),
            "fort": len(secteurs_by_cat["fort"]),
            "prospects": total_crm,
            "conversion": 23
        }
        return metrics, secteurs_by_cat
    def generer_metriques_vides(self):
        return {
            "tres-faible": 0,
            "partiel": 0,
            "fort": 0,
            "prospects": 0,
            "conversion": 0
        }, {"tres-faible": [], "partiel": [], "fort": []}
    def setup_ui(self):
        layout = QHBoxLayout(self)
        main_widget = self.build_main()
        layout.addWidget(main_widget)
        self.setStyleSheet(f"background: {DS['background']};")
    def build_main(self):
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(48, 48, 48, 48)
        v.setSpacing(32)
        h = QHBoxLayout()
        h.setSpacing(20)
        tbox = QVBoxLayout()
        t = QLabel()
        t.setPixmap(qta.icon('fa5s.brain', color=DS["primary"]).pixmap(28, 28))
        t.setText(" IA Insights")
        t.setFont(font(QFont.ExtraBold, 24))
        t.setStyleSheet(f"color:{DS['text_primary']}")
        tbox.addWidget(t)
        self.st = QLabel("")
        self.st.setFont(font(QFont.Medium, 14))
        self.st.setStyleSheet(f"color:{DS['text_secondary']}")
        tbox.addWidget(self.st)
        self._typing_text = "Découvrez les secteurs les plus prometteurs grâce à l'intelligence artificielle"
        self._typing_idx = 0
        self._typing_timer = QTimer(self)
        self._typing_timer.timeout.connect(self._typing_step)
        self._typing_timer.start(24)
        h.addLayout(tbox)
        h.addStretch()
        b1 = QPushButton(qta.icon('fa5s.magic'), "Analyser")
        b1.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {DS['primary']}, stop:1 {DS['primary_dark']});
            color:white;border-radius:8px;padding:12px 24px;font-weight:600;font-size:14px;min-width:120px;
        """)
        b1.clicked.connect(self.action_analyze)
        h.addWidget(b1)
        b2 = QPushButton(qta.icon('fa5s.file-export'), "Exporter")
        b2.setStyleSheet("""
            background:white;color:#374151;border:2px solid #e2e8f0;
            border-radius:8px;padding:12px 24px;font-weight:600;font-size:14px;min-width:120px;
        """)
        b2.clicked.connect(self.action_export)
        h.addWidget(b2)
        v.addLayout(h)
        metrics_block = QHBoxLayout()
        metrics_block.setSpacing(28)
        metrics = [
            ("fa5s.bullseye", self.metrics["tres-faible"], "SECTEURS SPÉCIALISÉS", DS["danger"]),
            ("fa5s.bolt", self.metrics["partiel"], "SECTEURS PROMETTEURS", DS["warning"]),
            ("fa5s.rocket", self.metrics["fort"], "SECTEURS SATURÉS", DS["success"]),
            ("fa5s.users", self.metrics["prospects"], "PROSPECTS IDENTIFIÉS", DS["primary"]),
            ("fa5s.chart-line", f"{self.metrics['conversion']}%", "TAUX DE CONVERSION", DS["primary_dark"])
        ]
        for icon, value, label, color in metrics:
            metrics_block.addWidget(MetricCard(icon, value, label, color))
        v.addLayout(metrics_block)
        section = SectionFrame()
        section.setStyleSheet(f"QFrame {{ background: {DS['surface']}; border: 1.5px solid {DS['border']}; border-radius: 24px;}}")
        section_lyt = QVBoxLayout(section)
        section_lyt.setContentsMargins(38, 26, 38, 26)
        section_lyt.setSpacing(18)
        self.tab_buttons = []
        tabs_bar = QHBoxLayout()
        tabs_bar.setSpacing(0)
        tab_labels = [
            ("TRÈS FAIBLE (0-2%)", "bullseye"),
            ("PARTIEL (2.1-8%)", "bolt"),
            ("FORT (8.1%+)", "rocket"),
            ("✨ Générateur", "magic"),
            ("📊 Résultat", "table"),
        ]
        self.results_tab_btn = None

        for i, (txt, icon) in enumerate(tab_labels):
            tab = QPushButton(qta.icon(f"fa5s.{icon}", color="white"), f" {txt}")
            tab.setCheckable(True)
            tab.setChecked(i == 3)
            tab.setFont(font(QFont.Bold, 13))
            tab.setStyleSheet(f"""
                QPushButton {{
                    background: {'qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #1d4ed8);' if i==3 else '#fff'};
                    color: {'#fff' if i==3 else '#1f2937'};
                    border-radius:24px;
                    border:none;
                    padding:14px 36px;
                    margin-right:18px;
                    font-weight:700;
                }}
                QPushButton:checked {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #1d4ed8);
                    color:#fff;
                }}
                QPushButton:hover {{
                    background: #f1f5f9; color:#222;
                }}
            """)
            tab.clicked.connect(lambda _, idx=i: self.select_tab(idx))
            self.tab_buttons.append(tab)
            tabs_bar.addWidget(tab)
            if i == 4:  # Résultat
                tab.hide()
                self.results_tab_btn = tab

        tabs_bar.addStretch()
        section_lyt.addLayout(tabs_bar)
        
        self.results_table_widget = ResultsTableWidget(DS)
        self.results_table_widget.hide()
        self.block_stack = QStackedWidget()
        for cat in ["tres-faible", "partiel", "fort"]:
            block = QFrame()
            block.setStyleSheet("""
                QFrame {
                    background: #fff;
                    border-radius: 14px;
                    border: none;
                }
            """)
            l = QVBoxLayout(block)
            l.setSpacing(18)
            l.setContentsMargins(22, 12, 22, 12)
            header = QHBoxLayout()
            emoji = "🎯" if cat=="tres-faible" else ("⚡" if cat=="partiel" else "🚀")
            title = QLabel(f"{emoji} Secteurs spécialisés")
            title.setFont(font(QFont.Bold, 14))
            title.setStyleSheet("color:#344051;")
            nb = QLabel(f"- {len(self.secteurs_by_cat.get(cat, []))} opportunités détectées")
            nb.setFont(font(QFont.Medium, 14))
            nb.setStyleSheet("color:#344051;")
            header.addWidget(title)
            header.addWidget(nb)
            header.addStretch()
            btn_refresh = QPushButton(qta.icon('fa5s.sync', color="white"), "Actualiser")
            btn_refresh.setFont(font(QFont.Bold, 13))
            btn_refresh.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #1d4ed8);
                    color:white;border-radius:11px;padding:10px 24px;font-weight:700;font-size:13px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1d4ed8, stop:1 #3b82f6);
                }
            """)
            btn_refresh.clicked.connect(lambda _, c=cat: self.action_refresh(c))
            header.addWidget(btn_refresh)
            l.addLayout(header)
            sectors = self.secteurs_by_cat.get(cat, [])
            rot = self.rotation_indices.get(cat, 0)
            display = [sectors[(rot + i) % len(sectors)] for i in range(min(4, len(sectors)))] if sectors else []
            if display:
                for sector in display:
                    l.addWidget(self.create_sector_card(sector, cat))
            else:
                l.addWidget(QLabel("Aucun secteur trouvé pour cette catégorie."))
            l.addStretch()
            self.block_stack.addWidget(block)
        self.generator_panel = GeneratorPanel(self)
        self.block_stack.addWidget(self.generator_panel)
        self.block_stack.addWidget(self.results_table_widget)  
        self.block_stack.setCurrentIndex(3)
        section_lyt.addWidget(self.block_stack)
        v.addWidget(section)
        return w
    def select_tab(self, idx):
        for i, btn in enumerate(self.tab_buttons):
            btn.setChecked(i == idx)
        self.block_stack.setCurrentIndex(idx)
    def action_analyze(self):
        self.metrics, self.secteurs_by_cat = self.analyse_opportunites()
        self.setup_ui()
    def action_export(self):
        self.show_toast("Fonction Export à brancher selon besoin.")
    def action_lancer(self, sector, btn=None):
        secteur_nom = sector["title"]
        self.launch_prospection(secteur_nom, btn)
    def launch_prospection(self, secteur_nom, btn_widget=None):
        if hasattr(self, "recherche_thread") and self.recherche_thread and self.recherche_thread.isRunning():
            self.show_toast("Recherche déjà en cours...")
            return
        self.recherche_thread = RechercheThread(secteur_nom, 25)
        self.recherche_thread.finished.connect(lambda resultats, secteur, export: self.on_recherche_finished(resultats, secteur, export, btn_widget))
        self.recherche_thread.start()
        self.show_toast(f"🔍 Recherche Google entreprises '{secteur_nom}' en cours...")
    def on_recherche_finished(self, resultats, secteur, export_path, btn_widget=None):
    # --- FILTRAGE DES ENTREPRISES DÉJÀ DANS LA BASE ---
        def clean(x):
            return str(x).strip().lower() if x else ''
        filtered_results = [r for r in resultats if clean(r.get('Nom', '')) not in self.existing_companies]

        if filtered_results:
            message = f"✅ {len(filtered_results)} prospects trouvés pour \"{secteur}\""
            if export_path:
                message += f"\n📁 Export: {export_path}"
            self.results_table_widget.populate(filtered_results)
            self.results_table_widget.show()
            if self.results_tab_btn:
                self.results_tab_btn.show()
                self.block_stack.setCurrentIndex(4)
                for i, btn in enumerate(self.tab_buttons):
                    btn.setChecked(i == 4)
        else:
            message = f"❌ Aucun prospect trouvé pour \"{secteur}\""
            self.results_table_widget.hide()
        self.show_toast(message)
        if btn_widget:
            btn_widget.setIcon(qta.icon('fa5s.check-circle', color='#10b981'))
            btn_widget.setText("Terminé")
            QTimer.singleShot(1400, lambda: self.reset_btn(btn_widget))
    def reset_btn(self, btn_widget):
        btn_widget.setIcon(qta.icon('fa5s.rocket', color='white'))
        btn_widget.setText("Lancer")
        btn_widget.setEnabled(True)    
    def show_toast(self, msg, color=DS["success"]):
        toast = ModernToast(msg, color)
        screen = QApplication.desktop().screenGeometry()
        x = screen.width() - 400
        y = screen.height() - 80
        toast.move(x, y)
        toast.show()
    def _typing_step(self):
        if self._typing_idx < len(self._typing_text):
            self.st.setText(self._typing_text[:self._typing_idx+1])
            self._typing_idx += 1
        else:
            self._typing_timer.stop()
    def create_sector_card(self, sector, cat):
        card = QFrame()
        card.setObjectName("opportunityCard")
        card.setMinimumHeight(66)
        card.setMaximumHeight(84)
        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)
        left_layout = QVBoxLayout()
        left_layout.setSpacing(4)
        left_layout.setContentsMargins(0, 0, 0, 0)
        title_lab = QLabel(sector["title"])
        title_lab.setObjectName("sectorTitle")
        title_lab.setFont(font(QFont.Bold, 15))
        title_lab.setStyleSheet("color:#1f2937;")
        left_layout.addWidget(title_lab)
        layout.addLayout(left_layout)
        layout.addStretch()
        progress_and_button_layout = QHBoxLayout()
        progress_and_button_layout.setSpacing(8)
        colors = {"tres-faible": "#ef4444", "partiel": "#f59e0b", "fort": "#10b981"}
        color = colors.get(cat, "#6b7280")
        progress_bar = ModernProgress(sector['couverture'], color)
        progress_bar.setFixedSize(100, 8)
        progress_and_button_layout.addWidget(progress_bar)
        percent_lab = QLabel(f"{sector['couverture']}%")
        percent_lab.setFont(font(QFont.Medium, 13))
        percent_lab.setStyleSheet(f"color: {color};")
        progress_and_button_layout.addWidget(percent_lab)
        btn_lancer = QPushButton("Lancer")
        btn_lancer.setFont(font(QFont.Bold, 13))
        btn_lancer.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #1d4ed8);
                color:white;border-radius:11px;padding:10px 24px;font-weight:700;font-size:13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1d4ed8, stop:1 #3b82f6);
            }
        """)
        btn_lancer.clicked.connect(lambda: self.action_lancer(sector, btn_lancer))
        progress_and_button_layout.addWidget(btn_lancer)
        layout.addLayout(progress_and_button_layout)
        card.setStyleSheet("""
            QFrame#opportunityCard {
                background: #fff;
                border: none;
                border-radius: 12px;
            }
        """)
        add_glow(card, blur=18)
        return card
    def action_refresh(self, cat):
        if cat in self.secteurs_by_cat and self.secteurs_by_cat[cat]:
            self.rotation_indices[cat] = (self.rotation_indices[cat] + 4) % len(self.secteurs_by_cat[cat])
            idx = ["tres-faible", "partiel", "fort"].index(cat)
            self.select_tab(idx)
            self.show_toast("Nouvelles suggestions proposées.")
if __name__ == "__main__":
    app = QApplication(sys.argv)
    font_ = QFont("Inter", 11)
    app.setFont(font_)
    window = IAInsightsModule()
    window.show()
    sys.exit(app.exec_())