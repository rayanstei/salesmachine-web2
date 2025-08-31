# -*- coding: utf-8 -*-
"""
SalesMachine v2.2 - Module Campagnes Moderne (Amélioré et Corrigé)
- Synergie avec Prospection via shared.py
- Fonctionnalités Lemlist : personnalisation, séquences, A/B testing, rapports visuels
- Esthétique modernisée : animations, progress bars, responsive
- Harmonisation avec Prospection et IA Insights
- Correction : Erreur AttributeError dans Sidebar pour import_from_prospection
- Amélioration : Graphique des rapports plus parlant avec pie chart pour statuts et annotations
- Amélioration : Aperçu email réaliste avec QWebEngineView imitant Gmail
- Amélioration : Onglet Envoi Direct repensé pour plus de lisibilité et esthétique
"""

import sys
import os
import json
import pandas as pd
import random
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar, QFrame, QComboBox,
    QScrollArea, QFileDialog, QMessageBox, QListWidget, QListWidgetItem, QMenu,
    QCheckBox, QWidgetAction, QTabWidget, QAbstractItemView, QTextEdit, QDialog,
    QFormLayout, QDialogButtonBox, QSplitter, QGridLayout, QInputDialog
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QColor, QPainter
from PyQt5.QtWidgets import QGraphicsDropShadowEffect
from PyQt5.QtWebEngineWidgets import QWebEngineView
import qtawesome as qta
from shared import SharedData
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# ======= DESIGN SYSTEM (Harmonisé avec Prospection et IA Insights) =======
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

# ======= CLASSES COMMUNES =======
class ModernToast(QFrame):
    def __init__(self, message, color=DS["success"]):
        super().__init__(None, Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.0)
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {color}, stop:1 {color});
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
    def __init__(self, metrics, parent=None):
        super().__init__()
        self.parent = parent
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
        v.setContentsMargins(0, 0, 0, 0)
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
            ('fa5s.search', "Prospection", False),
            ('fa5s.envelope', "Campagnes", True),
            ('fa5s.chart-bar', "Analytics", False),
            ('fa5s.brain', "IA Insights", False),
            ('fa5s.clipboard-list', "Enrichissement", False),
            ('fa5s.cogs', "Configuration", False),
        ]
        for iconname, name, active in modules:
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
            ('fa5s.plus-circle', "Nouvelle campagne"),
            ('fa5s.download', "Importer Prospects"),
            ('fa5s.sync', "Synchroniser"),
        ]
        for icon, name in quicks:
            quick = QPushButton()
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
            quick.setStyleSheet("padding:7px 0px;border-radius:0px;background:transparent;")
            if name == "Importer Prospects" and self.parent:
                quick.clicked.connect(self.parent.import_from_prospection)
            elif name == "Nouvelle campagne" and self.parent:
                quick.clicked.connect(self.parent.create_new_campaign)
            v.addWidget(quick)
        v.addStretch()

# ======= EMAIL SENDER =======
class EmailSender:
    def __init__(self):
        self.smtp_configs = {
            'gmail': {'smtp_server': 'smtp.gmail.com', 'port': 587, 'name': 'Gmail'},
            'outlook': {'smtp_server': 'smtp-mail.outlook.com', 'port': 587, 'name': 'Outlook'},
            'yahoo': {'smtp_server': 'smtp.mail.yahoo.com', 'port': 587, 'name': 'Yahoo'},
            'orange': {'smtp_server': 'smtp.orange.fr', 'port': 587, 'name': 'Orange'},
            'free': {'smtp_server': 'smtp.free.fr', 'port': 587, 'name': 'Free'}
        }
        self.current_config = {
            'smtp_server': '',
            'port': 587,
            'email': '',
            'password': '',
            'sender_name': ''
        }

    def detect_provider(self, email):
        domain = email.split('@')[-1].lower()
        provider_map = {
            'gmail.com': 'gmail', 'googlemail.com': 'gmail',
            'outlook.com': 'outlook', 'hotmail.com': 'outlook', 'live.com': 'outlook',
            'yahoo.com': 'yahoo', 'yahoo.fr': 'yahoo',
            'orange.fr': 'orange', 'wanadoo.fr': 'orange',
            'free.fr': 'free'
        }
        return provider_map.get(domain, 'gmail')

    def configure(self, email, password, sender_name):
        provider = self.detect_provider(email)
        smtp_config = self.smtp_configs.get(provider, self.smtp_configs['gmail'])
        self.current_config = {
            'smtp_server': smtp_config['smtp_server'],
            'port': smtp_config['port'],
            'email': email,
            'password': password,
            'sender_name': sender_name,
            'provider': smtp_config['name']
        }
        return True

    def send_email(self, recipient_email, subject, body):
        if not self.current_config['email']:
            return {'success': False, 'error': 'Configuration SMTP manquante'}

        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.current_config['sender_name']} <{self.current_config['email']}>"
            message["To"] = recipient_email
            text_part = MIMEText(body, "plain", "utf-8")
            html_body = f"""
            <html>
              <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                  <div style="background: linear-gradient(135deg, #3b82f6, #1d4ed8); color: white; padding: 20px; border-radius: 8px 8px 0 0;">
                    <h1 style="margin: 0; font-size: 24px;">📧 Email de prospection</h1>
                    <p style="margin: 5px 0 0 0; opacity: 0.9;">SalesMachine v2.2</p>
                  </div>
                  <div style="background: white; padding: 30px; border: 1px solid #e5e7eb; border-radius: 0 0 8px 8px;">
                    <div style="white-space: pre-line; margin-bottom: 20px;">
                      {body}
                    </div>
                    <div style="background: #f3f4f6; padding: 15px; border-radius: 6px; font-size: 12px; color: #6b7280;">
                      <strong>📧 Email envoyé via SalesMachine v2.2</strong><br>
                      Envoyé le {datetime.now().strftime("%d/%m/%Y à %H:%M")}<br>
                      Module Campagnes - Générateur d'emails IA
                    </div>
                  </div>
                </div>
              </body>
            </html>
            """
            html_part = MIMEText(html_body, "html", "utf-8")
            message.attach(text_part)
            message.attach(html_part)
            context = ssl.create_default_context()
            with smtplib.SMTP(self.current_config['smtp_server'], self.current_config['port']) as server:
                server.starttls(context=context)
                server.login(self.current_config['email'], self.current_config['password'])
                server.sendmail(self.current_config['email'], recipient_email, message.as_string())
            return {
                'success': True,
                'message': f"✅ Email envoyé à {recipient_email}",
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"❌ Erreur envoi à {recipient_email}"
            }

# ======= SMTP CONFIG DIALOG =======
class SMTPConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration Email")
        self.setFixedSize(450, 350)
        self.config_data = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        title = QLabel("📧 Configuration d'envoi d'emails")
        title.setFont(font(QFont.Bold, 18))
        title.setStyleSheet(f"color: {DS['text_primary']};")
        layout.addWidget(title)
        desc = QLabel("Configurez vos paramètres d'envoi pour les campagnes email réelles.")
        desc.setStyleSheet(f"color: {DS['text_secondary']}; margin-bottom: 10px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("votre.email@gmail.com")
        self.email_input.setStyleSheet(f"""
            border: 2px solid {DS['border']};
            border-radius: 8px;
            padding: 10px 12px;
            font-size: 14px;
            background: white;
        """)
        form_layout.addRow("📧 Votre email:", self.email_input)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Mot de passe d'application")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(f"""
            border: 2px solid {DS['border']};
            border-radius: 8px;
            padding: 10px 12px;
            font-size: 14px;
            background: white;
        """)
        form_layout.addRow("🔐 Mot de passe:", self.password_input)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Votre nom ou entreprise")
        self.name_input.setStyleSheet(f"""
            border: 2px solid {DS['border']};
            border-radius: 8px;
            padding: 10px 12px;
            font-size: 14px;
            background: white;
        """)
        form_layout.addRow("👤 Nom expéditeur:", self.name_input)
        layout.addLayout(form_layout)
        help_text = QLabel("💡 Pour Gmail: Utilisez un mot de passe d'application\n" +
                          "Générez-le sur: myaccount.google.com/apppasswords")
        help_text.setStyleSheet("""
            background: #fef3c7;
            color: #f59e0b;
            padding: 10px;
            border-radius: 6px;
            font-size: 11px;
            font-style: italic;
        """)
        help_text.setWordWrap(True)
        layout.addWidget(help_text)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def accept(self):
        if not all([self.email_input.text().strip(),
                   self.password_input.text().strip(),
                   self.name_input.text().strip()]):
            ModernToast("Veuillez remplir tous les champs", color=DS["danger"]).show()
            return
        self.config_data = {
            'email': self.email_input.text().strip(),
            'password': self.password_input.text().strip(),
            'sender_name': self.name_input.text().strip()
        }
        super().accept()

# ======= CAMPAIGN ENGINE =======
class CampaignEngine:
    def __init__(self):
        self.email_templates = {
            'tech': {
                'intros': [
                    "Bonjour {{nom}}, votre entreprise {{nom_entreprise}} excelle dans le secteur {{secteur}}.",
                    "J’ai remarqué l’expertise de {{nom_entreprise}} à {{ville}} dans {{secteur}}.",
                ],
                'value_props': [
                    "• +45% d'efficacité commerciale\n• Automatisation du lead nurturing\n• ROI de 380% en 6 mois",
                    "• 2x plus de leads qualifiés\n• Réduction de 60% du cycle de vente",
                ],
                'ctas': [
                    "Planifions un call de 15 min pour discuter de {{nom_entreprise}} ?",
                    "Une démo personnalisée vous tente ?",
                ]
            },
            'commerce': {
                'intros': [
                    "Bonjour {{nom}}, {{nom_entreprise}} est un acteur clé à {{ville}}.",
                    "Votre activité dans {{secteur}} m’a interpellé.",
                ],
                'value_props': [
                    "• +65% de conversions\n• Marketing multicanal\n• Scoring comportemental",
                    "• Fidélisation client boostée\n• Gestion intelligente des stocks",
                ],
                'ctas': [
                    "Un café pour parler de {{nom_entreprise}} ?",
                    "Testez notre solution gratuitement ?",
                ]
            }
        }
        self.signatures = [
            "Cordialement,\n{{nom_expediteur}}\n{{entreprise_expediteur}}",
            "Bien à vous,\n{{nom_expediteur}}\n{{entreprise_expediteur}}",
        ]

    def generate_email(self, company_data, email_type="initial", sender_info=None):
        sector_key = 'tech' if 'tech' in company_data.get('secteur', '').lower() else 'commerce'
        template = self.email_templates[sector_key]
        nom = company_data.get('nom', 'Prospect')
        nom_entreprise = company_data.get('nom_entreprise', 'votre entreprise')
        secteur = company_data.get('secteur', 'votre secteur')
        ville = company_data.get('ville', 'votre région')
        sender_name = sender_info.get('sender_name', 'Votre nom') if sender_info else 'Votre nom'
        sender_company = sender_info.get('company', 'Votre entreprise') if sender_info else 'Votre entreprise'

        if email_type == "initial":
            subject = f"Opportunité pour {nom_entreprise}"
            intro = random.choice(template['intros']).format(nom=nom, nom_entreprise=nom_entreprise, secteur=secteur, ville=ville)
            value_prop = random.choice(template['value_props'])
            cta = random.choice(template['ctas']).format(nom_entreprise=nom_entreprise)
        else:
            subject = f"Re: Opportunité pour {nom_entreprise}"
            intro = f"Je reviens vers vous concernant {nom_entreprise}."
            value_prop = "Nos clients obtiennent en moyenne :\n• +30% de chiffre d'affaires\n• +50% de leads qualifiés"
            cta = "Seriez-vous disponible pour un bref échange ?"

        signature = random.choice(self.signatures).format(nom_expediteur=sender_name, entreprise_expediteur=sender_company)

        body = f"""Bonjour,

{intro}

{value_prop}

{cta}

{signature}"""

        return {
            'subject': subject,
            'body': body,
            'personalization_score': random.randint(75, 95)
        }

    def create_campaign_sequence(self, company_data, sender_info=None):
        sequence = []

        email1 = self.generate_email(company_data, "initial", sender_info)
        sequence.append({
            'sequence_number': 1,
            'type': 'Contact initial',
            'send_delay': 0,
            'subject': email1['subject'],
            'body': email1['body'],
            'personalization_score': email1['personalization_score']
        })

        email2 = self.generate_email(company_data, "follow_up", sender_info)
        sequence.append({
            'sequence_number': 2,
            'type': 'Follow-up',
            'send_delay': 3 * 24 * 60 * 60,  # 3 jours en secondes
            'subject': email2['subject'],
            'body': email2['body'],
            'personalization_score': email2['personalization_score']
        })

        return sequence

# ======= MODULE CAMPAGNES MODERNE =======
class CampagnesModuleModern(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SalesMachine v2.2 - Module Campagnes Moderne")
        self.setMinimumSize(1400, 900)
        self.setStyleSheet("background: #ffffff;")
        self.campaign_engine = CampaignEngine()
        self.email_sender = EmailSender()
        self.current_campaigns = []
        self.generated_emails = []
        self.smtp_configured = False
        self.load_sample_data()
        self.metrics = self.compute_metrics()
        self.setup_ui()

    def compute_metrics(self):
        return {
            "campagnes": len(self.current_campaigns),
            "emails_sent": sum(c['emails_sent'] for c in self.current_campaigns),
            "open_rate": f"{random.uniform(30, 60):.1f}%",
            "response_rate": f"{random.uniform(5, 15):.1f}%"
        }

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        self.sidebar = Sidebar(self.metrics, self)
        main_layout.addWidget(self.sidebar)

        splitter = QSplitter(Qt.Horizontal)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(48, 48, 48, 48)
        content_layout.setSpacing(32)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(20)
        title_box = QVBoxLayout()
        title = QLabel()
        title.setPixmap(qta.icon('fa5s.envelope', color=DS["primary"]).pixmap(28, 28))
        title.setText(" Campagnes")
        title.setFont(font(QFont.ExtraBold, 24))
        title.setStyleSheet(f"color:{DS['text_primary']}")
        title_box.addWidget(title)
        self.subtitle = QLabel("")
        self.subtitle.setFont(font(QFont.Medium, 14))
        self.subtitle.setStyleSheet(f"color:{DS['text_secondary']}")
        title_box.addWidget(self.subtitle)
        self._typing_text = "Gérez vos campagnes email avec IA et personnalisation avancée"
        self._typing_idx = 0
        self._typing_timer = QTimer(self)
        self._typing_timer.timeout.connect(self._typing_step)
        self._typing_timer.start(24)
        header_layout.addLayout(title_box)
        header_layout.addStretch()
        config_btn = QPushButton(qta.icon('fa5s.cog'), "Config SMTP")
        config_btn.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {DS['primary']}, stop:1 {DS['primary_dark']});
            color:white;border-radius:8px;padding:12px 24px;font-weight:600;font-size:14px;min-width:120px;
        """)
        config_btn.clicked.connect(self.configure_smtp)
        header_layout.addWidget(config_btn)
        export_btn = QPushButton(qta.icon('fa5s.file-export'), "Exporter")
        export_btn.setStyleSheet("""
            background:white;color:#374151;border:2px solid #e2e8f0;
            border-radius:8px;padding:12px 24px;font-weight:600;font-size:14px;min-width:120px;
        """)
        export_btn.clicked.connect(self.export_campaigns)
        header_layout.addWidget(export_btn)
        new_btn = QPushButton(qta.icon('fa5s.plus-circle'), "Nouvelle")
        new_btn.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {DS['primary']}, stop:1 {DS['primary_dark']});
            color:white;border-radius:8px;padding:12px 24px;font-weight:600;font-size:14px;min-width:120px;
        """)
        new_btn.clicked.connect(self.create_new_campaign)
        header_layout.addWidget(new_btn)
        import_btn = QPushButton(qta.icon('fa5s.download'), "Importer Prospects")
        import_btn.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {DS['success']}, stop:1 {DS['success']});
            color:white;border-radius:8px;padding:12px 24px;font-weight:600;font-size:14px;min-width:120px;
        """)
        import_btn.clicked.connect(self.import_from_prospection)
        header_layout.addWidget(import_btn)
        content_layout.addLayout(header_layout)

        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(28)
        metrics_data = [
            ("fa5s.envelope", self.metrics["campagnes"], "CAMPAGNES CRÉÉES", DS["primary"]),
            ("fa5s.paper-plane", self.metrics["emails_sent"], "EMAILS ENVOYÉS", DS["success"]),
            ("fa5s.eye", self.metrics["open_rate"], "TAUX OUVERTURE", DS["warning"]),
            ("fa5s.reply", self.metrics["response_rate"], "TAUX RÉPONSE", DS["danger"]),
        ]
        for icon, value, label, color in metrics_data:
            metrics_layout.addWidget(MetricCard(icon, value, label, color))
        content_layout.addLayout(metrics_layout)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
QTabWidget::pane {{
    border: 2px solid {DS['border']};
    border-radius: 8px;
    background: white;
    top: -1px;
}}
QTabBar::tab {{
    background: #e0e7ff;
    color: #2563eb;
    padding: 14px 28px;
    margin-right: 2px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-weight: 500;
    font-size: 14px;
    min-width: 120px;
    transition: background 0.2s;
}}
QTabBar::tab:selected {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {DS['primary']}, stop:1 {DS['primary_dark']});
    color: white;
    border-bottom: 3px solid {DS['primary']};
    font-weight: 700;
}}
QTabBar::tab:hover:!selected {{
    background: #dbeafe;
    color: #1d4ed8;
}}
""")
        self.tab_campagnes = self.build_tab_campagnes()
        self.tabs.addTab(self.tab_campagnes, "Campagnes")
        self.tab_direct = self.build_tab_direct()
        self.tabs.addTab(self.tab_direct, "Envoi Direct")
        self.tab_templates = self.build_tab_templates()
        self.tabs.addTab(self.tab_templates, "Templates")
        self.tab_reports = self.build_tab_reports()
        self.tabs.addTab(self.tab_reports, "Rapports")
        self.tab_params = self.build_tab_params()
        self.tabs.addTab(self.tab_params, "Paramètres")
        content_layout.addWidget(self.tabs)

        splitter.addWidget(content_widget)
        main_layout.addWidget(splitter)

    def _typing_step(self):
        if self._typing_idx < len(self._typing_text):
            self.subtitle.setText(self._typing_text[:self._typing_idx+1])
            self._typing_idx += 1
        else:
            self._typing_timer.stop()

    def build_tab_campagnes(self):
        tab = QWidget()
        lyt = QVBoxLayout(tab)
        lyt.setContentsMargins(22, 24, 22, 24)
        lyt.setSpacing(22)
        campagnes_frame = QFrame()
        campagnes_frame.setStyleSheet(f"""
            QFrame {{
                background: #fff;
                border-radius: 16px;
                border: 1.5px solid {DS['border']};
            }}
        """)
        add_glow(campagnes_frame, blur=13)
        hist_layout = QVBoxLayout(campagnes_frame)
        hist_layout.setContentsMargins(10, 10, 10, 10)
        title = QLabel("Liste des campagnes")
        title.setFont(font(QFont.Bold, 18))
        title.setStyleSheet(f"color:{DS['primary']};margin-bottom:14px;")
        hist_layout.addWidget(title)
        self.campagnes_list = QListWidget()
        self.campagnes_list.setMaximumHeight(420)
        self.campagnes_list.setStyleSheet(f"""
            QListWidget {{
                background: {DS['surface_alt']};
                border-radius: 14px;
                font-size: 15px;
                padding: 10px;
            }}
            QListWidget::item:selected {{
                background: {DS['primary_light']};
                color: {DS['primary_dark']};
            }}
        """)
        add_glow(self.campagnes_list, blur=10)
        self.campagnes_list.itemDoubleClicked.connect(self.view_campaign_emails)
        self.campagnes_list.setWindowOpacity(0.0)
        anim = QPropertyAnimation(self.campagnes_list, b"windowOpacity")
        anim.setDuration(500)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.start()
        self.update_campagnes_list()
        hist_layout.addWidget(self.campagnes_list)
        action_layout = QHBoxLayout()
        send_btn = QPushButton(qta.icon('fa5s.paper-plane'), "Envoyer Campagne")
        send_btn.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {DS['success']}, stop:1 {DS['success']});
            color:white;border-radius:8px;padding:12px 24px;font-weight:600;font-size:14px;
        """)
        send_btn.clicked.connect(self.send_campaign)
        action_layout.addWidget(send_btn)
        ab_test_btn = QPushButton(qta.icon('fa5s.balance-scale'), "Lancer A/B Test")
        ab_test_btn.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {DS['warning']}, stop:1 {DS['warning']});
            color:white;border-radius:8px;padding:12px 24px;font-weight:600;font-size:14px;
        """)
        ab_test_btn.clicked.connect(self.run_ab_test)
        action_layout.addWidget(ab_test_btn)
        hist_layout.addLayout(action_layout)
        lyt.addWidget(campagnes_frame)
        lyt.addStretch()
        return tab

    def build_tab_direct(self):
        tab = QWidget()
        lyt = QVBoxLayout(tab)
        lyt.setContentsMargins(22, 24, 22, 24)
        lyt.setSpacing(24)

        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setHandleWidth(10)
        main_splitter.setStyleSheet(f"QSplitter::handle {{ background: {DS['border']}; width: 10px; }}")
        main_splitter.setSizes([700, 300])

        form_widget = QFrame()
        form_widget.setStyleSheet(f"""
            QFrame {{
                background: #fff;
                border-radius: 16px;
                border: 1.5px solid {DS['border']};
            }}
        """)
        add_glow(form_widget, blur=13)
        form_lyt = QVBoxLayout(form_widget)
        form_lyt.setContentsMargins(30, 30, 30, 30)
        form_lyt.setSpacing(20)

        title = QLabel("Envoi Email Direct")
        title.setFont(font(QFont.Bold, 20))
        title.setStyleSheet(f"color:{DS['primary']};margin-bottom:20px;")
        form_lyt.addWidget(title)

        grid_lyt = QGridLayout()
        grid_lyt.setVerticalSpacing(15)
        grid_lyt.setHorizontalSpacing(10)

        dest_label = QLabel("Destinataire:")
        dest_label.setFont(font(QFont.Medium, 14))
        dest_label.setStyleSheet(f"color:{DS['text_primary']};")
        self.direct_recipient = QLineEdit()
        self.direct_recipient.setPlaceholderText("prospect@entreprise.com")
        self.direct_recipient.setStyleSheet(f"""
            border: 2px solid {DS['border']};
            border-radius: 8px;
            padding: 12px 16px;
            font-size: 14px;
            background: white;
            color: {DS['text_primary']};
            min-width: 300px;
        """)
        grid_lyt.addWidget(dest_label, 0, 0)
        grid_lyt.addWidget(self.direct_recipient, 0, 1)

        subject_label = QLabel("Sujet:")
        subject_label.setFont(font(QFont.Medium, 14))
        subject_label.setStyleSheet(f"color:{DS['text_primary']};")
        self.direct_subject = QLineEdit()
        self.direct_subject.setPlaceholderText("Opportunité commerciale exclusive")
        self.direct_subject.setStyleSheet(f"""
            border: 2px solid {DS['border']};
            border-radius: 8px;
            padding: 12px 16px;
            font-size: 14px;
            background: white;
            color: {DS['text_primary']};
            min-width: 300px;
        """)
        grid_lyt.addWidget(subject_label, 1, 0)
        grid_lyt.addWidget(self.direct_subject, 1, 1)

        message_label = QLabel("Message:")
        message_label.setFont(font(QFont.Medium, 14))
        message_label.setStyleSheet(f"color:{DS['text_primary']};")
        self.direct_message = QTextEdit()
        self.direct_message.setPlaceholderText("Votre message ici... Utilisez {{nom}}, {{nom_entreprise}}, {{secteur}} pour personnaliser")
        self.direct_message.setStyleSheet(f"""
            border: 2px solid {DS['border']};
            border-radius: 8px;
            padding: 16px;
            font-size: 14px;
            background: white;
            color: {DS['text_primary']};
            min-height: 250px;
        """)
        grid_lyt.addWidget(message_label, 2, 0)
        grid_lyt.addWidget(self.direct_message, 2, 1, 1, 1)
                # Champ pièce jointe
        attachment_label = QLabel("Pièce jointe :")
        attachment_label.setFont(font(QFont.Medium, 14))
        attachment_label.setStyleSheet(f"color:{DS['text_primary']};")
        self.attachment_path = QLineEdit()
        self.attachment_path.setReadOnly(True)
        self.attachment_path.setStyleSheet(f"""
            border: 2px solid {DS['border']};
            border-radius: 8px;
            padding: 12px 16px;
            font-size: 14px;
            background: #f3f4f6;
            color: {DS['text_secondary']};
            min-width: 300px;
        """)
        attach_btn = QPushButton("Choisir un fichier")
        attach_btn.setStyleSheet(f"""
            background: {DS['primary_light']};
            color: {DS['primary']};
            border: 2px solid {DS['border']};
            border-radius: 8px;
            padding: 8px 18px;
            font-weight: 600;
            font-size: 13px;
        """)
        attach_btn.clicked.connect(self.select_attachment)
        grid_lyt.addWidget(attachment_label, 3, 0)
        attach_layout = QHBoxLayout()
        attach_layout.addWidget(self.attachment_path)
        attach_layout.addWidget(attach_btn)
        grid_lyt.addLayout(attach_layout, 3, 1)
        form_lyt.addLayout(grid_lyt)

        button_frame = QFrame()
        button_frame.setStyleSheet(f"background: {DS['surface_alt']}; border-radius: 8px;")
        button_lyt = QHBoxLayout(button_frame)
        button_lyt.setContentsMargins(20, 10, 20, 10)
        button_lyt.setSpacing(15)
        preview_btn = QPushButton(qta.icon('fa5s.eye', color=DS['primary']), "Aperçu")
        preview_btn.setStyleSheet(f"""
            background: {DS['primary_light']};
            color: {DS['primary']};
            border: 2px solid {DS['border']};
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: 600;
            font-size: 14px;
        """)
        preview_btn.clicked.connect(self.preview_direct_email)
        button_lyt.addWidget(preview_btn)
        send_btn = QPushButton(qta.icon('fa5s.paper-plane', color='white'), "Envoyer")
        send_btn.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {DS['primary']}, stop:1 {DS['primary_dark']});
            color:white;border-radius:8px;padding:12px 24px;font-weight:600;font-size:14px;
        """)
        send_btn.clicked.connect(self.send_direct_email)
        button_lyt.addWidget(send_btn)
        button_lyt.addStretch()
        form_lyt.addWidget(button_frame)

        main_splitter.addWidget(form_widget)

        history_widget = QFrame()
        history_widget.setStyleSheet(f"""
            QFrame {{
                background: {DS['surface']};
                border-radius: 16px;
                border: 1.5px solid {DS['border']};
            }}
        """)
        add_glow(history_widget, blur=10)
        history_lyt = QVBoxLayout(history_widget)
        history_lyt.setContentsMargins(20, 20, 20, 20)
        history_lyt.setSpacing(15)
        history_title = QLabel("Historique des Envois")
        history_title.setFont(font(QFont.Bold, 16))
        history_title.setStyleSheet(f"color:{DS['text_primary']};margin-bottom:10px;")
        history_lyt.addWidget(history_title)
        self.direct_history = QTextEdit()
        self.direct_history.setReadOnly(True)
        self.direct_history.setPlaceholderText("Aucun envoi récent...")
        self.direct_history.setStyleSheet(f"""
            border: 1px solid {DS['border']};
            border-radius: 6px;
            padding: 10px;
            font-size: 13px;
            background: {DS['surface_alt']};
            color: {DS['text_secondary']};
        """)
        history_lyt.addWidget(self.direct_history)
        main_splitter.addWidget(history_widget)

        lyt.addWidget(main_splitter)
        lyt.addStretch()
        return tab
    
    def select_attachment(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Sélectionner une pièce jointe")
        if file_path:
            self.attachment_path.setText(file_path)

    def build_tab_templates(self):
        tab = QWidget()
        lyt = QVBoxLayout(tab)
        lyt.setContentsMargins(22, 24, 22, 24)
        lyt.setSpacing(22)
        templates_frame = QFrame()
        templates_frame.setStyleSheet(f"""
            QFrame {{
                background: #fff;
                border-radius: 16px;
                border: 1.5px solid {DS['border']};
            }}
        """)
        add_glow(templates_frame, blur=13)
        list_lyt = QVBoxLayout(templates_frame)
        list_lyt.setContentsMargins(10, 10, 10, 10)
        title = QLabel("Templates Prêts à l'Emploi")
        title.setFont(font(QFont.Bold, 18))
        title.setStyleSheet(f"color:{DS['primary']};margin-bottom:14px;")
        list_lyt.addWidget(title)
        self.templates_list = QListWidget()
        self.templates_list.setMaximumHeight(420)
        self.templates_list.setStyleSheet(f"""
            QListWidget {{
                background: {DS['surface_alt']};
                border-radius: 14px;
                font-size: 15px;
                padding: 10px;
            }}
            QListWidget::item:selected {{
                background: {DS['primary_light']};
                color: {DS['primary_dark']};
            }}
        """)
        add_glow(self.templates_list, blur=10)
        self.templates_list.itemClicked.connect(lambda item: self.use_template_in_direct(item.text()))
        templates_names = ["Premier contact B2B", "Relance commerciale", "Offre spéciale", "Invitation webinaire", "Suivi après RDV"]
        for name in templates_names:
            self.templates_list.addItem(QListWidgetItem(name))
        list_lyt.addWidget(self.templates_list)
        lyt.addWidget(templates_frame)
        lyt.addStretch()
        return tab

    def build_tab_reports(self):
        tab = QWidget()
        lyt = QVBoxLayout(tab)
        lyt.setContentsMargins(22, 24, 22, 24)
        lyt.setSpacing(22)
        reports_frame = QFrame()
        reports_frame.setStyleSheet(f"""
            QFrame {{
                background: #fff;
                border-radius: 16px;
                border: 1.5px solid {DS['border']};
            }}
        """)
        add_glow(reports_frame, blur=13)
        report_lyt = QVBoxLayout(reports_frame)
        report_lyt.setContentsMargins(30, 30, 30, 30)
        title = QLabel("Rapports de Performance")
        title.setFont(font(QFont.Bold, 18))
        title.setStyleSheet(f"color:{DS['primary']};margin-bottom:14px;")
        report_lyt.addWidget(title)
        self.figure, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 8), height_ratios=[1, 1])
        self.canvas = FigureCanvas(self.figure)
        report_lyt.addWidget(self.canvas)
        self.update_reports()
        lyt.addWidget(reports_frame)
        lyt.addStretch()
        return tab

    def build_tab_params(self):
        tab = QWidget()
        lyt = QVBoxLayout(tab)
        lyt.setContentsMargins(22, 24, 22, 24)
        lyt.setSpacing(22)
        params_frame = QFrame()
        params_frame.setStyleSheet(f"""
            QFrame {{
                background: #fff;
                border-radius: 16px;
                border: 1.5px solid {DS['border']};
            }}
        """)
        add_glow(params_frame, blur=13)
        params_lyt = QVBoxLayout(params_frame)
        params_lyt.setContentsMargins(30, 30, 30, 30)
        title = QLabel("Paramètres du Module")
        title.setFont(font(QFont.Bold, 18))
        title.setStyleSheet(f"color:{DS['primary']};margin-bottom:14px;")
        params_lyt.addWidget(title)
        smtp_status = QLabel(f"SMTP: {'Configuré' if self.smtp_configured else 'Non configuré'}")
        smtp_status.setStyleSheet(f"color: {DS['success'] if self.smtp_configured else DS['danger']}; font-weight: 500;")
        params_lyt.addWidget(smtp_status)
        config_btn = QPushButton("Configurer SMTP")
        config_btn.clicked.connect(self.configure_smtp)
        params_lyt.addWidget(config_btn)
        lyt.addWidget(params_frame)
        lyt.addStretch()
        return tab

    def configure_smtp(self):
        dialog = SMTPConfigDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            config = dialog.config_data
            success = self.email_sender.configure(
                email=config['email'],
                password=config['password'],
                sender_name=config['sender_name']
            )
            if success:
                self.smtp_configured = True
                ModernToast(f"✅ Configuration SMTP enregistrée pour {config['email']}", color=DS["success"]).show()
            else:
                ModernToast("❌ Erreur de configuration SMTP", color=DS["danger"]).show()

    def import_from_prospection(self):
        prospects = SharedData.import_prospects()
        if prospects:
            sender_info = {
                'sender_name': self.email_sender.current_config.get('sender_name', 'Votre nom'),
                'company': 'Votre entreprise'
            }
            for prospect in prospects:
                company_data = {
                    'nom': prospect.get('nom', 'Prospect'),
                    'nom_entreprise': prospect.get('nom_entreprise', 'Entreprise'),
                    'secteur': prospect.get('secteur', 'Inconnu'),
                    'ville': prospect.get('ville', 'Région'),
                    'email': prospect.get('email', '')
                }
                sequence = self.campaign_engine.create_campaign_sequence(company_data, sender_info)
                for email in sequence:
                    email['campaign_id'] = len(self.current_campaigns) + 1
                    email['company'] = company_data['nom_entreprise']
                    email['recipient'] = company_data['email']
                    self.generated_emails.append(email)
            new_campaign = {
                'id': len(self.current_campaigns) + 1,
                'name': f"Campagne importée {datetime.now().strftime('%d/%m %H:%M')}",
                'type': 'Prospection',
                'status': 'ACTIVE',
                'prospects': len(prospects),
                'emails_sent': 0,
                'open_rate': '0%',
                'response_rate': '0%',
                'created_at': datetime.now().strftime("%d/%m %H:%M"),
            }
            self.current_campaigns.append(new_campaign)
            self.update_campagnes_list()
            self.metrics = self.compute_metrics()
            ModernToast(f"✅ {len(prospects)} prospects importés et campagne créée", color=DS["success"]).show()
        else:
            ModernToast("Aucun prospect à importer.", color=DS["warning"]).show()

    def create_new_campaign(self):
        name, ok = QInputDialog.getText(self, "Nouvelle campagne", "Nom de la campagne:")
        if not ok or not name.strip():
            ModernToast("Veuillez entrer un nom de campagne.", color=DS["warning"]).show()
            return
        new_campaign = {
            'id': len(self.current_campaigns) + 1,
            'name': name.strip(),
            'type': 'Manuelle',
            'status': 'DRAFT',
            'prospects': 0,
            'emails_sent': 0,
            'open_rate': '0%',
            'response_rate': '0%',
            'created_at': datetime.now().strftime("%d/%m %H:%M"),
        }
        self.current_campaigns.append(new_campaign)
        self.update_campagnes_list()
        ModernToast(f"✅ Campagne '{name}' créée avec succès", color=DS["success"]).show()

    def update_campagnes_list(self):
        self.campagnes_list.clear()
        for campaign in self.current_campaigns:
            item_text = f"{campaign['name']} | {campaign['prospects']} prospects | {campaign['status']}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, campaign['id'])
            self.campagnes_list.addItem(item)

    def view_campaign_emails(self, item):
        campaign_id = item.data(Qt.UserRole)
        emails = [e for e in self.generated_emails if e['campaign_id'] == campaign_id]
        if not emails:
            ModernToast("Aucun email généré pour cette campagne.", color=DS["warning"]).show()
            return
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Emails - Campagne #{campaign_id}")
        dialog.setMinimumSize(800, 600)
        layout = QVBoxLayout(dialog)
        table = QTableWidget(len(emails), 4)
        table.setHorizontalHeaderLabels(["#", "Type", "Sujet", "Destinataire"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        for i, email in enumerate(emails):
            table.setItem(i, 0, QTableWidgetItem(str(email['sequence_number'])))
            table.setItem(i, 1, QTableWidgetItem(email['type']))
            table.setItem(i, 2, QTableWidgetItem(email['subject']))
            table.setItem(i, 3, QTableWidgetItem(email['recipient']))
        layout.addWidget(table)
        dialog.exec_()

    def send_campaign(self):
        selected_items = self.campagnes_list.selectedItems()
        if not selected_items:
            ModernToast("Sélectionnez une campagne à envoyer.", color=DS["warning"]).show()
            return
        campaign_id = selected_items[0].data(Qt.UserRole)
        emails = [e for e in self.generated_emails if e['campaign_id'] == campaign_id]
        if not emails:
            ModernToast("Aucun email à envoyer pour cette campagne.", color=DS["warning"]).show()
            return
        if not self.smtp_configured:
            ModernToast("Configurez d'abord votre SMTP.", color=DS["danger"]).show()
            return
        for email in emails:
            result = self.email_sender.send_email(email['recipient'], email['subject'], email['body'])
            if result['success']:
                for campaign in self.current_campaigns:
                    if campaign['id'] == campaign_id:
                        campaign['emails_sent'] += 1
                self.direct_history.append(f"{result['timestamp']} - {result['message']}")
            else:
                self.direct_history.append(f"{result['timestamp']} - {result['message']}")
        self.update_campagnes_list()
        self.metrics = self.compute_metrics()
        ModernToast(f"✅ Campagne #{campaign_id} envoyée.", color=DS["success"]).show()

    def run_ab_test(self):
        selected_items = self.campagnes_list.selectedItems()
        if not selected_items:
            ModernToast("Sélectionnez une campagne pour le A/B test.", color=DS["warning"]).show()
            return
        campaign_id = selected_items[0].data(Qt.UserRole)
        emails = [e for e in self.generated_emails if e['campaign_id'] == campaign_id]
        if len(emails) < 2:
            ModernToast("Au moins 2 emails requis pour un A/B test.", color=DS["warning"]).show()
            return
        for i, email in enumerate(emails):
            email['variant'] = "A" if i % 2 == 0 else "B"
        ModernToast(f"✅ A/B Test lancé pour la campagne #{campaign_id}.", color=DS["success"]).show()

    def preview_direct_email(self):
        if not all([self.direct_recipient.text().strip(), self.direct_subject.text().strip(), self.direct_message.toPlainText().strip()]):
            ModernToast("Veuillez remplir tous les champs pour l'aperçu.", color=DS["warning"]).show()
            return

        sender_email = self.email_sender.current_config.get('email', 'votre.email@gmail.com')
        sender_name = self.email_sender.current_config.get('sender_name', 'Votre Nom')
        recipient = self.direct_recipient.text()
        subject = self.direct_subject.text()
        message = self.direct_message.toPlainText()

        # Logo Gmail SVG (petit)
        gmail_logo_svg = """
        <svg width="28" height="28" viewBox="0 0 48 48"><g><path fill="#4285F4" d="M44,39c0,2.2-1.8,4-4,4H8c-2.2,0-4-1.8-4-4V9c0-2.2,1.8-4,4-4h32c2.2,0,4,1.8,4,4V39z"/><path fill="#FFF" d="M24,29.4L8,18.3V39c0,1.1,0.9,2,2,2h28c1.1,0,2-0.9,2-2V18.3L24,29.4z"/><path fill="#EA4335" d="M44,9c0-2.2-1.8-4-4-4H8C5.8,5,4,6.8,4,9v2.7l20,14.3l20-14.3V9z"/><path fill="#34A853" d="M8,5c-2.2,0-4,1.8-4,4v2.7l20,14.3l20-14.3V9c0-2.2-1.8-4-4-4H8z" opacity=".15"/></g></svg>
        """

        # Avatar rond (initiale du nom)
        avatar_letter = sender_name[0].upper() if sender_name else "?"
        avatar_html = f"""
        <div style="width:40px;height:40px;border-radius:50%;background:#e0e0e0;display:flex;align-items:center;justify-content:center;font-size:20px;font-family:Roboto,Arial,sans-serif;color:#555;margin-right:16px;">
            {avatar_letter}
        </div>
        """

        # Menu "..."
        menu_html = """
        <div style="width:32px;height:32px;display:flex;align-items:center;justify-content:center;cursor:pointer;">
            <svg width="20" height="20" viewBox="0 0 20 20"><circle cx="4" cy="10" r="2" fill="#888"/><circle cx="10" cy="10" r="2" fill="#888"/><circle cx="16" cy="10" r="2" fill="#888"/></svg>
        </div>
        """

        # Bouton Répondre
        reply_html = """
        <div style="margin:32px 0 0 0;display:flex;align-items:center;">
            <svg width="24" height="24" viewBox="0 0 24 24" style="margin-right:8px;"><path fill="#1a73e8" d="M10 9V6l-7 7 7 7v-3.1c5.05 0 8.13 1.67 10 5.1-1.5-5-5-10-10-10z"/></svg>
            <span style="color:#1a73e8;font-weight:500;font-family:Roboto,Arial,sans-serif;font-size:15px;cursor:pointer;">Répondre</span>
        </div>
        """

        html_body = f"""
        <html>
          <head>
            <style>
              body {{
                background: #f5f5f5;
                margin: 0;
                padding: 0;
                font-family: Roboto, Arial, sans-serif;
              }}
              .gmail-bar {{
                background: #d93025;
                height: 48px;
                display: flex;
                align-items: center;
                padding-left: 18px;
              }}
              .gmail-logo {{
                width: 28px;
                height: 28px;
                margin-right: 12px;
              }}
              .gmail-title {{
                color: white;
                font-size: 19px;
                font-family: Roboto, Arial, sans-serif;
                font-weight: 500;
                letter-spacing: 1px;
              }}
              .container {{
                max-width: 680px;
                margin: 32px auto;
                background: #fff;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(60,70,90,0.08);
                overflow: hidden;
              }}
              .header {{
                display: flex;
                align-items: flex-start;
                padding: 24px 32px 12px 32px;
                border-bottom: 1px solid #eee;
              }}
              .header-main {{
                flex: 1;
              }}
              .subject {{
                font-size: 20px;
                font-weight: 500;
                color: #222;
                margin-bottom: 8px;
                font-family: Roboto, Arial, sans-serif;
              }}
              .meta {{
                color: #555;
                font-size: 14px;
                margin-bottom: 2px;
                font-family: Roboto, Arial, sans-serif;
              }}
              .meta .to {{
                color: #1a73e8;
                font-weight: 500;
              }}
              .date {{
                color: #888;
                font-size: 13px;
                margin-top: 2px;
              }}
              .body {{
                padding: 32px;
                font-size: 15px;
                color: #222;
                font-family: Roboto, Arial, sans-serif;
                white-space: pre-line;
              }}
            </style>
          </head>
          <body>
            <div class="gmail-bar">
              <span class="gmail-logo">{gmail_logo_svg}</span>
              <span class="gmail-title">Gmail</span>
            </div>
            <div class="container">
              <div class="header">
                {avatar_html}
                <div class="header-main">
                  <div class="subject">{subject}</div>
                  <div class="meta">De : <b>{sender_name}</b> &lt;{sender_email}&gt;</div>
                  <div class="meta">À : <span class="to">{recipient}</span></div>
                  <div class="date">{datetime.now().strftime('%d/%m/%Y %H:%M')}</div>
                </div>
                {menu_html}
              </div>
              <div class="body">{message}</div>
              {reply_html}
            </div>
          </body>
        </html>
        """

        dialog = QDialog(self)
        dialog.setWindowTitle("Aperçu Email (Gmail)")
        dialog.setMinimumSize(700, 700)
        layout = QVBoxLayout(dialog)
        web_view = QWebEngineView()
        web_view.setHtml(html_body)
        layout.addWidget(web_view)
        dialog.exec_()
# ...existing code...

    def send_direct_email(self):
        if not self.smtp_configured:
            ModernToast("Configurez d'abord votre SMTP.", color=DS["danger"]).show()
            return
        recipient = self.direct_recipient.text().strip()
        subject = self.direct_subject.text().strip()
        body = self.direct_message.toPlainText().strip()
        if not all([recipient, subject, body]):
            ModernToast("Veuillez remplir tous les champs.", color=DS["warning"]).show()
            return
        result = self.email_sender.send_email(recipient, subject, body)
        if result['success']:
            self.direct_history.append(f"{result['timestamp']} - {result['message']}")
            ModernToast(result['message'], color=DS["success"]).show()
        else:
            self.direct_history.append(f"{result['timestamp']} - {result['message']}")
            ModernToast(result['message'], color=DS["danger"]).show()

    def use_template_in_direct(self, template_name):
        templates = {
            "Premier contact B2B": "Bonjour {{nom}},\n\nVotre entreprise {{nom_entreprise}} m'intéresse dans le secteur {{secteur}}. Souhaitez-vous en discuter ?\n\nCordialement,\n{{nom_expediteur}}",
            "Relance commerciale": "Bonjour {{nom}},\n\nJe reviens vers vous concernant {{nom_entreprise}}. Toujours intéressé(e) ?\n\nBien à vous,\n{{nom_expediteur}}",
            "Offre spéciale": "Bonjour {{nom}},\n\nUne offre spéciale pour {{nom_entreprise}} : +50% de leads qualifiés ! Intéressé(e) ?\n\nCordialement,\n{{nom_expediteur}}",
            "Invitation webinaire": "Bonjour {{nom}},\n\nRejoignez notre webinaire sur {{secteur}} pour {{nom_entreprise}}. Inscription ?\n\nBien à vous,\n{{nom_expediteur}}",
            "Suivi après RDV": "Bonjour {{nom}},\n\nMerci pour notre échange. Prochaines étapes pour {{nom_entreprise}} ?\n\nCordialement,\n{{nom_expediteur}}"
        }
        template = templates.get(template_name, "")
        self.direct_message.setText(template)

    def update_reports(self):
        self.ax1.clear()
        self.ax2.clear()
        statuses = ['Envoyé', 'Ouvert', 'Répondu', 'Non ouvert']
        counts = [random.randint(50, 200) for _ in statuses]
        self.ax1.pie(counts, labels=statuses, autopct='%1.1f%%', colors=[DS['primary'], DS['success'], DS['warning'], DS['danger']], startangle=90)
        self.ax1.axis('equal')
        self.ax1.set_title('Répartition des statuts email')

        dates = [datetime.now().date() - pd.Timedelta(days=i) for i in range(7)]
        opens = [random.randint(10, 50) for _ in range(7)]
        self.ax2.plot(dates, opens, marker='o', color=DS['primary'], label='Ouvertures')
        self.ax2.set_title('Ouvertures sur 7 jours')
        self.ax2.set_xlabel('Date')
        self.ax2.set_ylabel('Nombre')
        self.ax2.grid(True, linestyle='--', alpha=0.7)
        self.ax2.legend()
        self.figure.tight_layout()
        self.canvas.draw()

    def export_campaigns(self):
        if not self.current_campaigns:
            ModernToast("Aucune campagne à exporter.", color=DS["warning"]).show()
            return
        df = pd.DataFrame(self.current_campaigns)
        file_path, _ = QFileDialog.getSaveFileName(self, "Exporter campagnes", "", "CSV Files (*.csv)")
        if file_path:
            df.to_csv(file_path, index=False)
            ModernToast(f"✅ Campagnes exportées vers {file_path}", color=DS["success"]).show()

    def load_sample_data(self):
        sample_prospects = [
            {"nom": "Jean Dupont", "nom_entreprise": "Tech Innov", "secteur": "Technologie", "ville": "Paris", "email": "jean@techinnov.com"},
            {"nom": "Marie Leclerc", "nom_entreprise": "Boutique Luxe", "secteur": "Commerce", "ville": "Lyon", "email": "marie@boutiqueluxe.com"},
        ]
        sender_info = {
            'sender_name': self.email_sender.current_config.get('sender_name', 'Votre nom'),
            'company': 'Votre entreprise'
        }
        for prospect in sample_prospects:
            sequence = self.campaign_engine.create_campaign_sequence(prospect, sender_info)
            for email in sequence:
                email['campaign_id'] = 1
                email['company'] = prospect['nom_entreprise']
                email['recipient'] = prospect['email']
                self.generated_emails.append(email)
        self.current_campaigns.append({
            'id': 1,
            'name': "Campagne test",
            'type': 'Prospection',
            'status': 'ACTIVE',
            'prospects': 2,
            'emails_sent': 0,
            'open_rate': '0%',
            'response_rate': '0%',
            'created_at': datetime.now().strftime("%d/%m %H:%M"),
        })

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CampagnesModuleModern()
    window.show()
    sys.exit(app.exec_())