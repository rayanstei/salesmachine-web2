# -*- coding: utf-8 -*-
"""
MODULE IA INSIGHTS - VERSION MAQUETTE SAAS MODERNE (identique)
Ajout : toast notification animée (slide/fade), bouton "Lancer" animé, ombre profonde, progress bar animée, typo header
"""

import sys
import random
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QRect, QEasingCurve, pyqtProperty
from PyQt5.QtGui import QFont, QColor, QPainter, QPalette, QBrush, QPainterPath
from PyQt5.QtWidgets import QGraphicsDropShadowEffect

# ===== DESIGN SYSTEM =====
DS = {
    "primary": "#3b82f6",
    "primary_dark": "#1d4ed8",
    "primary_light": "#dbeafe",
    "success": "#10b981",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "background": "#f9fafb",
    "surface": "#ffffff",
    "surface_alt": "#f8fafc",
    "border": "#e2e8f0",
    "text_primary": "#1f2937",
    "text_secondary": "#6b7280",
    "text_muted": "#9ca3af",
}

def font(weight=QFont.Normal, size=13):
    f = QFont("Inter", size)
    f.setWeight(weight)
    return f

def add_shadow(widget, color="#3b82f6", blur=32, dx=0, dy=8):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blur)
    shadow.setColor(QColor(color))
    shadow.setOffset(dx, dy)
    widget.setGraphicsEffect(shadow)

class ModernToast(QFrame):
    """Toast notification moderne (slide/fade animée)"""
    def __init__(self, message, color=DS["success"]):
        super().__init__(None, Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.opacity = 0.0
        self._message = message
        self._color = color
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

class ModernProgress(QWidget):
    def __init__(self, percent, color):
        super().__init__()
        self.value = 0
        self.target = percent
        self.color = color
        self.setFixedSize(120, 8)
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
        painter.drawRoundedRect(0, 0, 120, 8, 4, 4)
        painter.setBrush(QColor(self.color))
        painter.drawRoundedRect(0, 0, int(1.2 * self.value), 8, 4, 4)
        painter.end()

class Sidebar(QFrame):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(280)
        self.setObjectName("Sidebar")
        self.setStyleSheet(f"""
            QFrame#Sidebar {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {DS["surface"]}, stop:1 {DS["surface_alt"]});
                border-right: 1px solid {DS["border"]};
            }}
        """)
        self.setup_ui()

    def setup_ui(self):
        v = QVBoxLayout(self)
        v.setContentsMargins(24, 32, 24, 32)
        v.setSpacing(32)
        logo_row = QHBoxLayout()
        logo = QLabel("SM")
        logo.setFixedSize(44, 44)
        logo.setAlignment(Qt.AlignCenter)
        logo.setFont(font(QFont.Bold, 18))
        logo.setStyleSheet(f"background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {DS['primary']}, stop:1 {DS['primary_dark']});color:white;border-radius:8px;")
        logo_row.addWidget(logo)
        app_title = QLabel("SalesMachine")
        app_title.setFont(font(QFont.Bold, 16))
        app_title.setStyleSheet(f"color:{DS['text_primary']}")
        logo_row.addWidget(app_title)
        logo_row.addStretch()
        v.addLayout(logo_row)
        modules_label = QLabel("MODULES")
        modules_label.setFont(font(QFont.Bold, 11))
        modules_label.setStyleSheet(f"color:{DS['text_muted']};letter-spacing:0.04em;text-transform:uppercase;")
        v.addWidget(modules_label)
        modules = [
            ("🔍", "Prospection", False),
            ("✉️", "Campagnes", False),
            ("📈", "Analytics", False),
            ("🧠", "IA Insights", True),
            ("📋", "Enrichissement", False),
            ("⚙️", "Configuration", False)
        ]
        for icon, name, active in modules:
            mod = QLabel(f"{icon} {name}")
            mod.setFont(font(QFont.Bold if active else QFont.Medium, 13))
            mod.setStyleSheet(
                f"color:{'white' if active else DS['text_secondary']};"
                f"background: {'qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #1d4ed8)' if active else 'transparent'};"
                "padding:14px 16px;border-radius:8px;"
                "margin-bottom:4px;"
            )
            v.addWidget(mod)
        v.addSpacing(18)
        access_label = QLabel("ACCÈS RAPIDE")
        access_label.setFont(font(QFont.Bold, 11))
        access_label.setStyleSheet(f"color:{DS['text_muted']};letter-spacing:0.04em;text-transform:uppercase;")
        v.addWidget(access_label)
        quicks = [
            ("➕", "Nouvelle recherche"),
            ("⬇️", "Exports récents"),
            ("🔄", "Synchroniser")
        ]
        for icon, name in quicks:
            quick = QLabel(f"{icon} {name}")
            quick.setFont(font(QFont.Medium, 11))
            quick.setStyleSheet(f"color:{DS['text_muted']};padding:8px 16px;border-radius:6px;")
            v.addWidget(quick)
        v.addStretch()

class MetricCard(QFrame):
    def __init__(self, color, icon, value, label):
        super().__init__()
        self.setFixedHeight(110)
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #fff, stop:1 #fdfdfd);
                border: 1px solid {DS['border']};
                border-radius: 12px;
            }}
            QLabel#MetricValue {{
                color: {DS['text_primary']};
                font-size: 32px;
                font-weight: 800;
            }}
            QLabel#MetricLabel {{
                color: {DS['text_secondary']};
                font-size: 12px;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 0.025em;
            }}
        """)
        l = QVBoxLayout(self)
        l.setSpacing(0)
        h = QHBoxLayout()
        ic = QLabel(icon)
        ic.setFont(font(QFont.Bold, 24))
        ic.setStyleSheet(f"color:{color}")
        h.addWidget(ic)
        h.addStretch()
        l.addLayout(h)
        val = QLabel(str(value))
        val.setObjectName("MetricValue")
        val.setFont(font(QFont.Bold, 32))
        l.addWidget(val)
        lab = QLabel(label)
        lab.setObjectName("MetricLabel")
        l.addWidget(lab)
        add_shadow(self, color=color, blur=32, dx=0, dy=8)

class SectorCard(QFrame):
    def __init__(self, label, code, nb, percent, color, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #fff, stop:1 #fdfdfd);
                border: 1px solid {DS['border']};
                border-radius: 12px;
                padding: 20px;
            }}
            QFrame:hover {{
                background: linear-gradient(145deg, #f8fafc, #ffffff);
                border-color: {DS['primary']};
            }}
        """)
        layout = QHBoxLayout(self)
        layout.setSpacing(16)
        info = QVBoxLayout()
        t1 = QLabel(label)
        t1.setFont(font(QFont.Bold, 14))
        t1.setStyleSheet(f"color:{DS['text_primary']};margin-bottom:4px;")
        info.addWidget(t1)
        t2 = QLabel(f"Code APE: {code} • {nb} entreprises")
        t2.setFont(font(QFont.Normal, 11))
        t2.setStyleSheet(f"color:{DS['text_secondary']}")
        info.addWidget(t2)
        layout.addLayout(info)
        layout.addStretch()
        pb = ModernProgress(percent, color)
        layout.addWidget(pb)
        pct = QLabel(f"{percent:.1f}%")
        pct.setFont(font(QFont.Bold, 11))
        pct.setStyleSheet(f"min-width:42px;color:{DS['text_primary']};")
        layout.addWidget(pct)
        # --- Bouton Lancer animé ---
        self.btn = QPushButton("🚀 Lancer")
        self.btn.setObjectName("btnLaunch")
        self.btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {DS['primary']}, stop:1 {DS['primary_dark']});
                color:white;border-radius:6px;padding:8px 16px;font-weight:600;font-size:12px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {DS['primary_dark']}, stop:1 #1e40af);
            }}
        """)
        self.btn.setFixedHeight(32)
        self.btn.clicked.connect(self.animate_btn)
        layout.addWidget(self.btn)
        add_shadow(self, color=color, blur=32, dx=0, dy=8)

    def animate_btn(self):
        self.btn.setText("⏳ Recherche...")
        self.btn.setDisabled(True)
        self.btn.setStyleSheet(f"""
            QPushButton {{
                background: #6b7280;
                color: white;
                border-radius: 6px;
                padding:8px 16px;font-weight:600;font-size:12px;
            }}
        """)
        QTimer.singleShot(1700, self.btn_done)

    def btn_done(self):
        self.btn.setText("✅ Terminé")
        self.btn.setStyleSheet(f"""
            QPushButton {{
                background: #10b981;
                color: white;
                border-radius: 6px;
                padding:8px 16px;font-weight:600;font-size:12px;
            }}
        """)
        QTimer.singleShot(1400, self.btn_reset)

    def btn_reset(self):
        self.btn.setText("🚀 Lancer")
        self.btn.setEnabled(True)
        self.btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {DS['primary']}, stop:1 {DS['primary_dark']});
                color:white;border-radius:6px;padding:8px 16px;font-weight:600;font-size:12px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {DS['primary_dark']}, stop:1 #1e40af);
            }}
        """)

    def show_toast(self, msg):
        toast = ModernToast(msg)
        screen = QApplication.desktop().screenGeometry()
        x = screen.width() - 400
        y = screen.height() - 80
        toast.move(x, y)
        toast.show()

class GeneratorPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setSpacing(32)
        layout.setContentsMargins(0, 0, 0, 0)
        cat_panel = QFrame()
        cat_panel.setFixedWidth(320)
        cat_panel.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #fff, stop:1 #f8fafc);
                border: 1px solid {DS['border']};
                border-radius: 16px;
                padding:24px;
            }}
        """)
        add_shadow(cat_panel, color=DS["primary"], blur=32, dx=0, dy=8)
        vcat = QVBoxLayout(cat_panel)
        title = QLabel("📂 Catégories")
        title.setFont(font(QFont.Bold, 16))
        vcat.addWidget(title)
        self.cat_buttons = {}
        cats = ["Industrie", "Services B2B", "BTP et Construction", "Transport et Logistique", "Commerce Spécialisé"]
        for i, cat in enumerate(cats):
            btn = QPushButton(cat)
            btn.setObjectName("categoryBtn")
            btn.setCheckable(True)
            btn.setChecked(i == 0)
            btn.setStyleSheet("""
                QPushButton {background:transparent;color:#374151;font-size:13px;font-weight:500;text-align:left;padding:14px 20px;border-radius:8px;}
                QPushButton:checked {background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #1d4ed8);color:white;font-weight:700;}
                QPushButton:hover {background:#f1f5f9;}
            """)
            btn.clicked.connect(lambda _, b=btn, c=cat: self.select_cat(b, c))
            vcat.addWidget(btn)
            self.cat_buttons[cat] = btn
        vcat.addStretch()
        layout.addWidget(cat_panel)
        self.sectors_panel = QFrame()
        self.sectors_panel.setStyleSheet(f"""
            QFrame {{
                background: #fff;
                border: 1px solid {DS['border']};
                border-radius: 16px;
                padding:32px;
            }}
        """)
        add_shadow(self.sectors_panel, color=DS["primary"], blur=32, dx=0, dy=8)
        vsector = QVBoxLayout(self.sectors_panel)
        self.sector_title = QLabel("🏭 Industrie")
        self.sector_title.setFont(font(QFont.Bold, 16))
        vsector.addWidget(self.sector_title)
        self.grid = QGridLayout()
        vsector.addLayout(self.grid)
        layout.addWidget(self.sectors_panel)
        self.show_sectors("Industrie")

    def select_cat(self, btn, cat):
        for b in self.cat_buttons.values():
            b.setChecked(b==btn)
        icons = {
            'Industrie': '🏭', 'Services B2B': '💼', 'BTP et Construction': '🏗️',
            'Transport et Logistique': '🚛', 'Commerce Spécialisé': '🏪'
        }
        self.sector_title.setText(f"{icons.get(cat, '📁')} {cat}")
        self.show_sectors(cat)

    def show_sectors(self, cat):
        sectors = {
            'Industrie': ["Fabricants de palettes métalliques", "Ateliers de chaudronnerie", "Entreprises de soudure industrielle", "Fabricants de grillages"],
            'Services B2B': ["Maintenance machines-outils", "Nettoyage industriel", "Audit énergétique"],
            'BTP et Construction': ["Construction métallique", "Travaux publics", "Revêtements de sols"],
            'Transport et Logistique': ["Transport frigorifique", "Transport exceptionnel"],
            'Commerce Spécialisé': ["Distributeurs de machines-outils", "Fournisseurs d'EPI"]
        }
        for i in reversed(range(self.grid.count())):
            w = self.grid.itemAt(i).widget()
            if w: w.deleteLater()
        for i, name in enumerate(sectors.get(cat, [])):
            w = QFrame()
            w.setStyleSheet(f"""
                QFrame {{
                    background: transparent;
                    border: 1px solid {DS['border']};
                    border-radius: 8px;
                    padding: 16px;
                }}
                QFrame:hover {{
                    background: linear-gradient(145deg, #f9fafb, #ffffff);
                    border-color: {DS['primary']};
                }}
            """)
            h = QHBoxLayout(w)
            lab = QLabel(name)
            lab.setFont(font(QFont.Medium, 12))
            lab.setStyleSheet("color:#374151;")
            h.addWidget(lab)
            h.addStretch()
            btn = QPushButton("🚀 Prospecter")
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {DS['primary']}, stop:1 {DS['primary_dark']});
                    color:white;border-radius:6px;padding:8px 16px;font-weight:600;font-size:12px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {DS['primary_dark']}, stop:1 #1e40af);
                }}
            """)
            btn.setFixedHeight(32)
            btn.clicked.connect(lambda _, n=name, b=btn: self.animate_btn(b))
            h.addWidget(btn)
            self.grid.addWidget(w, i//2, i%2)

    def animate_btn(self, btn):
        btn.setText("⏳ Recherche...")
        btn.setDisabled(True)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: #6b7280;
                color: white;
                border-radius: 6px;
                padding:8px 16px;font-weight:600;font-size:12px;
            }}
        """)
        QTimer.singleShot(1700, lambda: self.btn_done(btn))

    def btn_done(self, btn):
        btn.setText("✅ Terminé")
        btn.setStyleSheet(f"""
            QPushButton {{
                background: #10b981;
                color: white;
                border-radius: 6px;
                padding:8px 16px;font-weight:600;font-size:12px;
            }}
        """)
        QTimer.singleShot(1400, lambda: self.btn_reset(btn))

    def btn_reset(self, btn):
        btn.setText("🚀 Prospecter")
        btn.setEnabled(True)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {DS['primary']}, stop:1 {DS['primary_dark']});
                color:white;border-radius:6px;padding:8px 16px;font-weight:600;font-size:12px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {DS['primary_dark']}, stop:1 #1e40af);
            }}
        """)

    def show_toast(self, msg):
        toast = ModernToast(msg)
        screen = QApplication.desktop().screenGeometry()
        x = screen.width() - 400
        y = screen.height() - 80
        toast.move(x, y)
        toast.show()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IA Insights - SaaS Moderne")
        self.resize(1400, 900)
        layout = QHBoxLayout(self)
        self.sidebar = Sidebar()
        layout.addWidget(self.sidebar)
        layout.addWidget(self.build_main())
        self.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f9fafb, stop:1 #f1f5f9);")

    def build_main(self):
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(48, 48, 48, 48)
        v.setSpacing(32)
        # Header avec animation typing du sous-titre
        h = QHBoxLayout()
        h.setSpacing(20)
        tbox = QVBoxLayout()
        t = QLabel("🧠 IA Insights")
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
        b1 = QPushButton("Analyser")
        b1.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {DS['primary']}, stop:1 {DS['primary_dark']});
            color:white;border-radius:8px;padding:12px 24px;font-weight:600;font-size:14px;min-width:120px;
            box-shadow:0 2px 8px rgba(59,130,246,0.25);
        """)
        h.addWidget(b1)
        b2 = QPushButton("Exporter")
        b2.setStyleSheet("""
            background:white;color:#374151;border:2px solid #e2e8f0;
            border-radius:8px;padding:12px 24px;font-weight:600;font-size:14px;min-width:120px;
        """)
        h.addWidget(b2)
        v.addLayout(h)
        # Metrics dashboard
        metrics = QHBoxLayout()
        metrics.setSpacing(24)
        metrics.addWidget(MetricCard(DS["danger"], "🎯", "47", "Secteurs spécialisés"))
        metrics.addWidget(MetricCard(DS["warning"], "⚡", "23", "Secteurs prometteurs"))
        metrics.addWidget(MetricCard(DS["success"], "🚀", "12", "Secteurs saturés"))
        metrics.addWidget(MetricCard(DS["primary"], "👥", "12,250", "Prospects identifiés"))
        metrics.addWidget(MetricCard(DS["text_secondary"], "📈", "23%", "Taux de conversion"))
        v.addLayout(metrics)
        # Tabs pills
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabBar::tab {
                padding:14px 28px;border-radius:24px;font-weight:600;font-size:13px;color:#6b7280;
                background:transparent;min-width:120px;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #1d4ed8);color:white;
            }
        """)
        # Tab 1 — Très faible
        tab1 = QWidget()
        t1v = QVBoxLayout(tab1)
        t1v.setContentsMargins(0, 24, 0, 0)
        t1v.setSpacing(12)
        head = QHBoxLayout()
        head.addWidget(QLabel("🎯 Secteurs spécialisés - 47 opportunités détectées"))
        head.addStretch()
        btn = QPushButton("Actualiser")
        btn.setStyleSheet("""
            background:white;color:#374151;border:2px solid #e2e8f0;
            border-radius:8px;padding:10px 24px;font-weight:600;font-size:13px;min-width:120px;
        """)
        btn.clicked.connect(lambda: self.show_toast("Liste mise à jour"))
        head.addWidget(btn)
        t1v.addLayout(head)
        t1v.addWidget(SectorCard("Fabrication de structures métalliques", "2511Z", 23, 1.5, DS["danger"]))
        t1v.addWidget(SectorCard("Ateliers de chaudronnerie", "2512Z", 18, 1.2, DS["danger"]))
        t1v.addWidget(SectorCard("Entreprises de soudure industrielle", "2562B", 31, 1.8, DS["danger"]))
        t1v.addStretch()
        # Tab 2 — Partiel
        tab2 = QWidget(); t2v = QVBoxLayout(tab2)
        t2v.setContentsMargins(0, 24, 0, 0); t2v.setSpacing(12)
        t2v.addWidget(QLabel("⚡ Secteurs partiels (exemple)"))
        t2v.addWidget(SectorCard("Maintenance équipements industriels", "3312Z", 187, 4.2, DS["warning"]))
        t2v.addWidget(SectorCard("Nettoyage industriel", "8129A", 156, 3.8, DS["warning"]))
        t2v.addWidget(SectorCard("Conseil en informatique", "6202A", 243, 5.1, DS["warning"]))
        t2v.addStretch()
        # Tab 3 — Fort
        tab3 = QWidget(); t3v = QVBoxLayout(tab3)
        t3v.setContentsMargins(0, 24, 0, 0); t3v.setSpacing(12)
        t3v.addWidget(QLabel("🚀 Secteurs forts (exemple)"))
        t3v.addWidget(SectorCard("Construction bâtiments résidentiels", "4120A", 892, 12.3, DS["success"]))
        t3v.addWidget(SectorCard("Transport routier marchandises", "4941A", 1205, 15.7, DS["success"]))
        t3v.addStretch()
        # Générateur
        tab4 = GeneratorPanel()
        self.tabs.addTab(tab1, "TRÈS FAIBLE (0-2%)")
        self.tabs.addTab(tab2, "PARTIEL (2.1-8%)")
        self.tabs.addTab(tab3, "FORT (8.1%+)")
        self.tabs.addTab(tab4, "✨ Générateur")
        v.addWidget(self.tabs)
        return w

    def _typing_step(self):
        if self._typing_idx < len(self._typing_text):
            self.st.setText(self._typing_text[:self._typing_idx+1])
            self._typing_idx += 1
        else:
            self._typing_timer.stop()

    def show_toast(self, msg):
        toast = ModernToast(msg)
        screen = QApplication.desktop().screenGeometry()
        x = screen.width() - 400
        y = screen.height() - 80
        toast.move(x, y)
        toast.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    font_ = QFont("Inter", 11)
    app.setFont(font_)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())