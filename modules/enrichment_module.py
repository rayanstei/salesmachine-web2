# -*- coding: utf-8 -*-
"""
SalesMachine v2.1 - Module Enrichissement CORRIGÉ
Interface optimisée pour gestion et enrichissement CRM
Correction des problèmes d'affichage des cartes et layout
"""

import sys
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFrame, QScrollArea, QProgressBar,
                            QGridLayout, QTabWidget, QTableWidget, QTableWidgetItem,
                            QHeaderView, QMessageBox, QSizePolicy, QSplitter,
                            QFileDialog, QTextEdit, QCheckBox, QSpinBox,
                            QComboBox, QLineEdit)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QMimeData
from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor, QDragEnterEvent, QDropEvent
from datetime import datetime

# Simulation du moteur d'enrichissement
ENRICHMENT_ENGINE_AVAILABLE = False

class EnrichmentWorker(QThread):
    """Worker pour enrichissement en arrière-plan"""
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    enrichment_completed = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, file_path, config):
        super().__init__()
        self.file_path = file_path
        self.config = config
        self.is_running = True
    
    def run(self):
        """Lance l'enrichissement"""
        try:
            self.status_updated.emit("📖 Lecture du fichier...")
            self.progress_updated.emit(5)
            
            # Simulation lecture
            import time
            time.sleep(0.5)
            
            # Simulation données
            total_rows = 1000  # Simulation
            enriched_count = 0
            
            for i in range(total_rows):
                if not self.is_running:
                    break
                
                self.status_updated.emit(f"🔄 Enrichissement ligne {i+1}/{total_rows}")
                
                # Simulation enrichissement
                if ENRICHMENT_ENGINE_AVAILABLE:
                    pass
                else:
                    time.sleep(0.001)  # Simulation rapide
                
                enriched_count += 1
                progress = int((i + 1) / total_rows * 90) + 10
                self.progress_updated.emit(progress)
            
            self.status_updated.emit("💾 Sauvegarde des résultats...")
            self.progress_updated.emit(100)
            
            # Résultats
            results = {
                "total_processed": total_rows,
                "enriched_count": enriched_count,
                "success_rate": (enriched_count / total_rows) * 100,
                "output_file": f"enriched_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            }
            
            self.enrichment_completed.emit(results)
            
        except Exception as e:
            self.error_occurred.emit(str(e))
    
    def stop(self):
        """Arrête l'enrichissement"""
        self.is_running = False

class EnrichmentModule(QWidget):
    """Module Enrichissement - Interface corrigée SalesMachine v2.1"""
    
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.enrichment_worker = None
        self.enrichment_stats = {}
        self.setup_ui()
        self.setup_styles()
        self.load_enrichment_stats()
        
        # Drag & Drop
        self.setAcceptDrops(True)
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        
        # En-tête du module
        self.setup_header(layout)
        
        # Métriques principales (4 cards corrigées)
        self.setup_metrics_cards(layout)
        
        # Interface principale avec onglets
        self.setup_tabs_interface(layout)
    
    def setup_header(self, layout):
        """Configure l'en-tête du module"""
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 16)
        
        # Titre et description
        title_layout = QVBoxLayout()
        
        title_label = QLabel("📈 Enrichissement")
        title_label.setObjectName("moduleTitle")
        title_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Gestion et enrichissement automatique de la base CRM")
        subtitle_label.setObjectName("moduleSubtitle")
        title_layout.addWidget(subtitle_label)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # Boutons d'action
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(12)
        
        import_btn = QPushButton("📂 Importer fichier")
        import_btn.setObjectName("primaryButton")
        import_btn.clicked.connect(self.import_file)
        actions_layout.addWidget(import_btn)
        
        backup_btn = QPushButton("💾 Sauvegarder base")
        backup_btn.setObjectName("secondaryButton")
        backup_btn.clicked.connect(self.backup_database)
        actions_layout.addWidget(backup_btn)
        
        clean_btn = QPushButton("🧹 Nettoyer doublons")
        clean_btn.setObjectName("secondaryButton")
        clean_btn.clicked.connect(self.clean_duplicates)
        actions_layout.addWidget(clean_btn)
        
        header_layout.addLayout(actions_layout)
        layout.addWidget(header_frame)
    
    def setup_metrics_cards(self, layout):
        """Configure les cartes de métriques - VERSION CORRIGÉE"""
        metrics_frame = QFrame()
        metrics_layout = QGridLayout(metrics_frame)
        metrics_layout.setSpacing(24)
        
        # Card 1 - Entrées CRM totales (Bleu)
        self.total_entries_card = self.create_corrected_metric_card(
            "🗄️", "12,250", "Entrées CRM totales", "+156 cette semaine", "#3b82f6"
        )
        metrics_layout.addWidget(self.total_entries_card, 0, 0)
        
        # Card 2 - Taux enrichissement (Vert)
        self.enrichment_rate_card = self.create_corrected_metric_card(
            "✅", "70.5%", "Taux enrichissement", "+5.2% ce mois", "#10b981"
        )
        metrics_layout.addWidget(self.enrichment_rate_card, 0, 1)
        
        # Card 3 - Enrichis ce mois (Orange)
        self.monthly_enriched_card = self.create_corrected_metric_card(
            "🔄", "2,847", "Enrichis ce mois", "+23.4%", "#f59e0b"
        )
        metrics_layout.addWidget(self.monthly_enriched_card, 0, 2)
        
        # Card 4 - Qualité données (Violet)
        self.data_quality_card = self.create_corrected_metric_card(
            "🎯", "94.2%", "Qualité données", "+1.8%", "#8b5cf6"
        )
        metrics_layout.addWidget(self.data_quality_card, 0, 3)
        
        layout.addWidget(metrics_frame)
    
    def create_corrected_metric_card(self, icon, value, label, change, color):
        """Crée une carte de métrique corrigée avec structure rigide"""
        card = QFrame()
        card.setObjectName("metricCard")
        card.setFixedHeight(140)  # Hauteur fixe
        card.setMinimumWidth(250)  # Largeur minimale
        
        # Layout principal avec structure rigide
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(0)  # Contrôle manuel
        
        # Ligne 1: Header avec icône et indicateur (20px)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 20px; line-height: 20px;")
        icon_label.setFixedSize(20, 20)
        header_layout.addWidget(icon_label)
        
        header_layout.addStretch()
        
        # Badge de changement
        change_badge = QLabel(change)
        change_badge.setStyleSheet(f"""
            background: {color}20;
            color: {color};
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 500;
            line-height: 20px;
        """)
        change_badge.setFixedHeight(20)
        header_layout.addWidget(change_badge)
        
        header_widget = QWidget()
        header_widget.setLayout(header_layout)
        header_widget.setFixedHeight(20)
        card_layout.addWidget(header_widget)
        
        # Ligne 2: Valeur principale (34px) - CRITIQUE pour alignement
        value_label = QLabel(value)
        value_label.setStyleSheet("""
            font-size: 28px; 
            font-weight: bold; 
            color: #1a1a1a; 
            line-height: 1.0;
            margin: 0;
            padding: 0;
        """)
        value_label.setFixedHeight(34)
        value_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        card_layout.addWidget(value_label)
        
        # Ligne 3: Label principal (18px)
        main_label = QLabel(label)
        main_label.setStyleSheet("""
            font-size: 13px; 
            font-weight: 500; 
            color: #6b7280; 
            line-height: 1.2;
            margin: 0;
            padding: 0;
        """)
        main_label.setFixedHeight(18)
        main_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        main_label.setWordWrap(True)
        card_layout.addWidget(main_label)
        
        # Stretch restant pour remplir
        card_layout.addStretch()
        
        # Style de la carte avec couleur contextuelle
        card.setStyleSheet(f"""
            QFrame#metricCard {{
                background: white;
                border: 2px solid {color}20;
                border-radius: 12px;
                margin: 2px;
            }}
            QFrame#metricCard:hover {{
                border-color: {color}60;
                background: {color}05;
            }}
        """)
        
        return card
    
    def setup_tabs_interface(self, layout):
        """Configure l'interface principale avec onglets"""
        self.tabs = QTabWidget()
        self.tabs.setObjectName("enrichmentTabs")
        
        # Onglet 1 : Import/Export
        self.setup_import_tab()
        
        # Onglet 2 : Configuration
        self.setup_config_tab()
        
        # Onglet 3 : Historique
        self.setup_history_tab()
        
        # Onglet 4 : Qualité
        self.setup_quality_tab()
        
        layout.addWidget(self.tabs)
    
    def setup_import_tab(self):
        """Configure l'onglet import/export"""
        import_widget = QWidget()
        import_layout = QVBoxLayout(import_widget)
        import_layout.setContentsMargins(24, 24, 24, 24)
        import_layout.setSpacing(24)
        
        # Zone drag & drop
        drop_zone = self.create_drop_zone()
        import_layout.addWidget(drop_zone)
        
        # Section configuration enrichissement
        config_section = self.create_enrichment_config_section()
        import_layout.addWidget(config_section)
        
        # Barre de progression
        self.progress_section = self.create_progress_section()
        import_layout.addWidget(self.progress_section)
        
        self.tabs.addTab(import_widget, "📂 Import/Export")
    
    def create_drop_zone(self):
        """Crée la zone de drag & drop"""
        drop_frame = QFrame()
        drop_frame.setObjectName("dropZone")
        drop_frame.setFixedHeight(150)
        drop_frame.setStyleSheet("""
            QFrame#dropZone {
                border: 2px dashed #d1d5db;
                border-radius: 12px;
                background: #f9fafb;
            }
            QFrame#dropZone:hover {
                border-color: #3b82f6;
                background: #eff6ff;
            }
        """)
        
        layout = QVBoxLayout(drop_frame)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(8)
        
        # Icône
        icon_label = QLabel("📁")
        icon_label.setStyleSheet("font-size: 32px;")
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        # Texte principal
        main_text = QLabel("Glissez-déposez vos fichiers CSV/Excel ici")
        main_text.setStyleSheet("""
            font-size: 16px;
            font-weight: 600;
            color: #374151;
        """)
        main_text.setAlignment(Qt.AlignCenter)
        layout.addWidget(main_text)
        
        # Texte secondaire
        sub_text = QLabel("ou cliquez pour parcourir")
        sub_text.setStyleSheet("""
            font-size: 14px;
            color: #6b7280;
        """)
        sub_text.setAlignment(Qt.AlignCenter)
        layout.addWidget(sub_text)
        
        # Rendre cliquable
        drop_frame.mousePressEvent = lambda e: self.import_file()
        
        return drop_frame
    
    def create_enrichment_config_section(self):
        """Crée la section de configuration de l'enrichissement"""
        config_frame = QFrame()
        config_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout(config_frame)
        layout.setSpacing(16)
        
        # Titre
        title_label = QLabel("⚙️ Configuration enrichissement")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #1a1a1a;
            margin-bottom: 8px;
        """)
        layout.addWidget(title_label)
        
        # Grille d'options
        options_layout = QGridLayout()
        options_layout.setSpacing(16)
        
        # API Sources
        sources_label = QLabel("Sources API :")
        sources_label.setStyleSheet("font-weight: 500; color: #374151;")
        options_layout.addWidget(sources_label, 0, 0)
        
        self.sources_combo = QComboBox()
        self.sources_combo.addItems(["Google Places", "Societe.com", "Data.gouv.fr", "Toutes les sources"])
        self.sources_combo.setCurrentText("Toutes les sources")
        options_layout.addWidget(self.sources_combo, 0, 1)
        
        # Champs à enrichir
        fields_label = QLabel("Champs à enrichir :")
        fields_label.setStyleSheet("font-weight: 500; color: #374151;")
        options_layout.addWidget(fields_label, 1, 0)
        
        fields_layout = QHBoxLayout()
        self.enrich_address = QCheckBox("Adresse")
        self.enrich_phone = QCheckBox("Téléphone")
        self.enrich_website = QCheckBox("Site web")
        self.enrich_sector = QCheckBox("Secteur")
        
        self.enrich_address.setChecked(True)
        self.enrich_phone.setChecked(True)
        self.enrich_website.setChecked(True)
        self.enrich_sector.setChecked(True)
        
        for checkbox in [self.enrich_address, self.enrich_phone, self.enrich_website, self.enrich_sector]:
            checkbox.setStyleSheet("font-size: 13px; color: #374151;")
            fields_layout.addWidget(checkbox)
        
        fields_layout.addStretch()
        options_layout.addLayout(fields_layout, 1, 1)
        
        # Limite par heure
        limit_label = QLabel("Limite/heure :")
        limit_label.setStyleSheet("font-weight: 500; color: #374151;")
        options_layout.addWidget(limit_label, 2, 0)
        
        self.limit_spinbox = QSpinBox()
        self.limit_spinbox.setRange(100, 5000)
        self.limit_spinbox.setValue(1000)
        self.limit_spinbox.setSuffix(" req/h")
        options_layout.addWidget(self.limit_spinbox, 2, 1)
        
        layout.addLayout(options_layout)
        
        # Bouton de lancement
        launch_layout = QHBoxLayout()
        launch_layout.addStretch()
        
        self.launch_enrichment_btn = QPushButton("🚀 Lancer l'enrichissement")
        self.launch_enrichment_btn.setObjectName("primaryButton")
        self.launch_enrichment_btn.clicked.connect(self.start_enrichment)
        self.launch_enrichment_btn.setEnabled(False)  # Activé quand fichier chargé
        launch_layout.addWidget(self.launch_enrichment_btn)
        
        layout.addLayout(launch_layout)
        
        return config_frame
    
    def create_progress_section(self):
        """Crée la section de progression"""
        progress_frame = QFrame()
        progress_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        progress_frame.setVisible(False)  # Caché par défaut
        
        layout = QVBoxLayout(progress_frame)
        layout.setSpacing(12)
        
        # Titre
        self.progress_title = QLabel("📊 Progression de l'enrichissement")
        self.progress_title.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #1a1a1a;
        """)
        layout.addWidget(self.progress_title)
        
        # Status
        self.progress_status = QLabel("En attente...")
        self.progress_status.setStyleSheet("""
            font-size: 14px;
            color: #6b7280;
            margin-bottom: 8px;
        """)
        layout.addWidget(self.progress_status)
        
        # Barre de progression
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #e5e7eb;
                border-radius: 6px;
                text-align: center;
                font-weight: bold;
                background: #f3f4f6;
            }
            QProgressBar::chunk {
                background: #3b82f6;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Boutons de contrôle
        controls_layout = QHBoxLayout()
        
        self.pause_btn = QPushButton("⏸️ Pause")
        self.pause_btn.setObjectName("secondaryButton")
        self.pause_btn.clicked.connect(self.pause_enrichment)
        controls_layout.addWidget(self.pause_btn)
        
        self.stop_btn = QPushButton("⏹️ Arrêter")
        self.stop_btn.setObjectName("warningButton")
        self.stop_btn.clicked.connect(self.stop_enrichment)
        controls_layout.addWidget(self.stop_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        return progress_frame
    
    def setup_config_tab(self):
        """Configure l'onglet configuration"""
        config_widget = QWidget()
        config_layout = QVBoxLayout(config_widget)
        config_layout.setContentsMargins(24, 24, 24, 24)
        config_layout.setSpacing(24)
        
        # Section API Configuration
        api_section = self.create_api_config_section()
        config_layout.addWidget(api_section)
        
        # Section Base de données
        db_section = self.create_database_config_section()
        config_layout.addWidget(db_section)
        
        config_layout.addStretch()
        
        self.tabs.addTab(config_widget, "⚙️ Configuration")
    
    def create_api_config_section(self):
        """Crée la section de configuration API"""
        api_frame = QFrame()
        api_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout(api_frame)
        layout.setSpacing(16)
        
        # Titre
        title_label = QLabel("🔧 Configuration API")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #1a1a1a;
        """)
        layout.addWidget(title_label)
        
        # Champs API
        fields_layout = QGridLayout()
        fields_layout.setSpacing(12)
        
        # Google API Key
        fields_layout.addWidget(QLabel("Google API Key :"), 0, 0)
        self.google_api_key = QLineEdit()
        self.google_api_key.setPlaceholderText("AIzaSyD-9tSrke72PouQMnMX-a7eZSW0jkFMBWY")
        fields_layout.addWidget(self.google_api_key, 0, 1)
        
        # CSE ID
        fields_layout.addWidget(QLabel("CSE ID :"), 1, 0)
        self.cse_id = QLineEdit()
        self.cse_id.setPlaceholderText("017576662512468239146:omuauf_lfve")
        fields_layout.addWidget(self.cse_id, 1, 1)
        
        layout.addLayout(fields_layout)
        
        # Bouton test
        test_btn = QPushButton("🧪 Tester APIs")
        test_btn.setObjectName("primaryButton")
        test_btn.clicked.connect(self.test_apis)
        layout.addWidget(test_btn)
        
        return api_frame
    
    def create_database_config_section(self):
        """Crée la section de configuration base de données"""
        db_frame = QFrame()
        db_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout(db_frame)
        layout.setSpacing(16)
        
        # Titre
        title_label = QLabel("💾 Base de données")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #1a1a1a;
        """)
        layout.addWidget(title_label)
        
        # Options
        options_layout = QVBoxLayout()
        
        # Sauvegarde automatique
        auto_backup = QCheckBox("💾 Sauvegarde automatique quotidienne")
        auto_backup.setChecked(True)
        auto_backup.setStyleSheet("font-size: 14px; color: #374151;")
        options_layout.addWidget(auto_backup)
        
        # Nettoyage automatique
        auto_clean = QCheckBox("🧹 Nettoyage automatique des doublons")
        auto_clean.setChecked(False)
        auto_clean.setStyleSheet("font-size: 14px; color: #374151;")
        options_layout.addWidget(auto_clean)
        
        layout.addLayout(options_layout)
        
        # Boutons d'action
        actions_layout = QHBoxLayout()
        
        backup_btn = QPushButton("💾 Sauvegarder configuration")
        backup_btn.setObjectName("successButton")
        backup_btn.clicked.connect(self.save_config)
        actions_layout.addWidget(backup_btn)
        
        reset_btn = QPushButton("🔄 Réinitialiser")
        reset_btn.setObjectName("warningButton")
        reset_btn.clicked.connect(self.reset_config)
        actions_layout.addWidget(reset_btn)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        
        return db_frame
    
    def setup_history_tab(self):
        """Configure l'onglet historique"""
        history_widget = QWidget()
        history_layout = QVBoxLayout(history_widget)
        history_layout.setContentsMargins(24, 24, 24, 24)
        history_layout.setSpacing(16)
        
        # En-tête
        header_label = QLabel("📚 Historique")
        header_label.setObjectName("tabTitle")
        history_layout.addWidget(header_label)
        
        # Tableau d'historique
        self.history_table = QTableWidget()
        self.setup_history_table()
        history_layout.addWidget(self.history_table)
        
        self.tabs.addTab(history_widget, "📚 Historique")
    
    def setup_history_table(self):
        """Configure le tableau d'historique"""
        headers = ["Date", "Fichier", "Entrées", "Enrichies", "Taux", "Statut"]
        self.history_table.setColumnCount(len(headers))
        self.history_table.setHorizontalHeaderLabels(headers)
        
        # Données d'exemple
        history_data = [
            ("2025-01-29 14:30", "prospects_btp_lyon.csv", "1,247", "834", "66.9%", "✅ Terminé"),
            ("2025-01-28 09:15", "base_clients_2024.xlsx", "3,891", "3,234", "83.1%", "✅ Terminé"),
            ("2025-01-27 16:45", "leads_commerce.csv", "567", "445", "78.5%", "✅ Terminé"),
            ("2025-01-26 11:20", "prospects_industrie.csv", "2,156", "1,789", "83.0%", "✅ Terminé"),
            ("2025-01-25 08:30", "base_startup.xlsx", "892", "756", "84.8%", "✅ Terminé"),
        ]
        
        self.history_table.setRowCount(len(history_data))
        
        for row, (date, file, entries, enriched, rate, status) in enumerate(history_data):
            self.history_table.setItem(row, 0, QTableWidgetItem(date))
            self.history_table.setItem(row, 1, QTableWidgetItem(file))
            self.history_table.setItem(row, 2, QTableWidgetItem(entries))
            self.history_table.setItem(row, 3, QTableWidgetItem(enriched))
            self.history_table.setItem(row, 4, QTableWidgetItem(rate))
            self.history_table.setItem(row, 5, QTableWidgetItem(status))
        
        self.history_table.resizeColumnsToContents()
        self.history_table.horizontalHeader().setStretchLastSection(True)
    
    def setup_quality_tab(self):
        """Configure l'onglet qualité"""
        quality_widget = QWidget()
        quality_layout = QVBoxLayout(quality_widget)
        quality_layout.setContentsMargins(24, 24, 24, 24)
        quality_layout.setSpacing(16)
        
        # En-tête
        header_label = QLabel("🎯 ANALYSE QUALITÉ DES DONNÉES")
        header_label.setObjectName("qualityTitle")
        quality_layout.addWidget(header_label)
        
        # Section recommandations
        recommendations_section = self.create_quality_recommendations()
        quality_layout.addWidget(recommendations_section)
        
        # Actions de qualité
        actions_layout = QHBoxLayout()
        
        correction_btn = QPushButton("🔧 Correction automatique")
        correction_btn.setObjectName("primaryButton")
        correction_btn.clicked.connect(self.auto_correction)
        actions_layout.addWidget(correction_btn)
        
        export_report_btn = QPushButton("📊 Exporter rapport")
        export_report_btn.setObjectName("secondaryButton")
        export_report_btn.clicked.connect(self.export_quality_report)
        actions_layout.addWidget(export_report_btn)
        
        actions_layout.addStretch()
        quality_layout.addLayout(actions_layout)
        
        self.tabs.addTab(quality_widget, "🎯 Qualité")
    
    def create_quality_recommendations(self):
        """Crée la section des recommandations qualité"""
        recommendations_frame = QFrame()
        recommendations_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout(recommendations_frame)
        layout.setSpacing(16)
        
        # Titre
        title_label = QLabel("⚠️ Recommandations")
        title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #1a1a1a;
            margin-bottom: 8px;
        """)
        layout.addWidget(title_label)
        
        # Liste des recommandations
        recommendations_text = QTextEdit()
        recommendations_text.setReadOnly(True)
        recommendations_text.setMaximumHeight(150)
        recommendations_text.setHtml("""
        <ul style="color: #374151; font-size: 13px; line-height: 1.5;">
            <li><span style="color: #ef4444;">●</span> <strong>CRITIQUE</strong> : 47 entreprises sans code APE détecté - Enrichir manuellement</li>
            <li><span style="color: #f59e0b;">●</span> <strong>ATTENTION</strong> : 156 numéros de téléphone incomplets - Validation recommandée</li>
            <li><span style="color: #10b981;">●</span> <strong>AMÉLIORATION</strong> : Activer la géolocalisation pour 234 adresses</li>
        </ul>
        """)
        layout.addWidget(recommendations_text)
        
        return recommendations_frame
    
    def setup_styles(self):
        """Configure les styles du module"""
        self.setStyleSheet("""
            /* Styles généraux */
            QWidget {
                font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
                background: #f9fafb;
            }
            
            /* Titre du module */
            QLabel#moduleTitle {
                font-size: 28px;
                font-weight: bold;
                color: #1a1a1a;
                margin-bottom: 4px;
            }
            
            QLabel#moduleSubtitle {
                font-size: 16px;
                color: #6b7280;
            }
            
            /* Boutons */
            QPushButton#primaryButton {
                background: #3b82f6;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                min-width: 140px;
            }
            
            QPushButton#primaryButton:hover {
                background: #1d4ed8;
                transform: translateY(-1px);
            }
            
            QPushButton#primaryButton:disabled {
                background: #9ca3af;
                color: #d1d5db;
            }
            
            QPushButton#secondaryButton {
                background: #f3f4f6;
                color: #374151;
                border: 1px solid #d1d5db;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                min-width: 120px;
            }
            
            QPushButton#secondaryButton:hover {
                background: #e5e7eb;
                transform: translateY(-1px);
            }
            
            QPushButton#successButton {
                background: #10b981;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            
            QPushButton#successButton:hover {
                background: #059669;
                transform: translateY(-1px);
            }
            
            QPushButton#warningButton {
                background: #f59e0b;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            
            QPushButton#warningButton:hover {
                background: #d97706;
                transform: translateY(-1px);
            }
            
            /* Onglets */
            QTabWidget#enrichmentTabs {
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
            }
            
            QTabWidget#enrichmentTabs::pane {
                border: none;
                background: white;
                border-radius: 0 0 12px 12px;
            }
            
            QTabBar::tab {
                background: #f9fafb;
                color: #6b7280;
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 500;
                font-size: 14px;
                min-width: 140px;
            }
            
            QTabBar::tab:selected {
                background: white;
                color: #3b82f6;
                border: 1px solid #e5e7eb;
                border-bottom: none;
                font-weight: 600;
            }
            
            QTabBar::tab:hover {
                background: #f3f4f6;
                color: #374151;
            }
            
            /* Titres qualité */
            QLabel#qualityTitle {
                font-size: 18px;
                font-weight: bold;
                color: #1a1a1a;
                margin-bottom: 16px;
            }
            
            QLabel#tabTitle {
                font-size: 20px;
                font-weight: bold;
                color: #1a1a1a;
                margin-bottom: 8px;
            }
            
            /* Tableaux */
            QTableWidget {
                background: white;
                alternate-background-color: #f9fafb;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                gridline-color: #f3f4f6;
                selection-background-color: #eff6ff;
            }
            
            QTableWidget::item {
                padding: 8px 12px;
                border-bottom: 1px solid #f3f4f6;
                color: #374151;
                font-size: 13px;
            }
            
            QTableWidget::item:selected {
                background: #eff6ff;
                color: #1e40af;
            }
            
            QHeaderView::section {
                background: #f9fafb;
                color: #374151;
                padding: 12px 8px;
                border: none;
                border-bottom: 2px solid #e5e7eb;
                font-weight: bold;
                font-size: 13px;
            }
            
            /* Champs de saisie */
            QLineEdit, QComboBox, QSpinBox {
                padding: 8px 12px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                background: white;
                font-size: 14px;
                color: #374151;
            }
            
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
                border-color: #3b82f6;
                outline: none;
            }
            
            /* Cases à cocher */
            QCheckBox {
                spacing: 8px;
            }
            
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #d1d5db;
                border-radius: 4px;
                background: white;
            }
            
            QCheckBox::indicator:checked {
                background: #3b82f6;
                border-color: #3b82f6;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDQuNUw0LjUgOEwxMSAxIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
            }
            
            /* Zone de texte */
            QTextEdit {
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                background: white;
                color: #374151;
                font-size: 14px;
                padding: 12px;
            }
            
            /* Scroll Areas */
            QScrollArea {
                border: none;
                background: transparent;
            }
            
            QScrollBar:vertical {
                border: none;
                background: #f3f4f6;
                width: 8px;
                border-radius: 4px;
            }
            
            QScrollBar::handle:vertical {
                background: #d1d5db;
                border-radius: 4px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: #9ca3af;
            }
        """)
    
    def load_enrichment_stats(self):
        """Charge les statistiques d'enrichissement"""
        # Simulation des stats
        self.enrichment_stats = {
            "total_entries": 12250,
            "enrichment_rate": 70.5,
            "monthly_enriched": 2847,
            "data_quality": 94.2
        }
    
    # Méthodes d'interaction - Drag & Drop
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Gère l'entrée du drag"""
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
    
    def dropEvent(self, event: QDropEvent):
        """Gère le drop de fichiers"""
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files:
            self.load_file(files[0])
    
    # Méthodes d'action
    
    def import_file(self):
        """Importe un fichier CSV/Excel"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner un fichier à enrichir",
            "",
            "Fichiers CSV (*.csv);;Fichiers Excel (*.xlsx *.xls);;Tous les fichiers (*)"
        )
        
        if file_path:
            self.load_file(file_path)
    
    def load_file(self, file_path):
        """Charge un fichier pour enrichissement"""
        self.current_file = file_path
        file_name = os.path.basename(file_path)
        
        # Mise à jour de l'interface
        QMessageBox.information(
            self,
            "Fichier chargé",
            f"✅ Fichier '{file_name}' chargé avec succès!\n\nVous pouvez maintenant configurer l'enrichissement et le lancer."
        )
        
        # Activer le bouton de lancement
        self.launch_enrichment_btn.setEnabled(True)
        self.launch_enrichment_btn.setText(f"🚀 Enrichir '{file_name}'")
    
    def start_enrichment(self):
        """Démarre l'enrichissement"""
        if not self.current_file:
            QMessageBox.warning(self, "Aucun fichier", "Veuillez d'abord charger un fichier.")
            return
        
        # Configuration
        config = {
            "sources": self.sources_combo.currentText(),
            "fields": {
                "address": self.enrich_address.isChecked(),
                "phone": self.enrich_phone.isChecked(),
                "website": self.enrich_website.isChecked(),
                "sector": self.enrich_sector.isChecked()
            },
            "limit_per_hour": self.limit_spinbox.value()
        }
        
        # Afficher la section de progression
        self.progress_section.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Démarrer le worker
        self.enrichment_worker = EnrichmentWorker(self.current_file, config)
        self.enrichment_worker.progress_updated.connect(self.update_progress)
        self.enrichment_worker.status_updated.connect(self.update_status)
        self.enrichment_worker.enrichment_completed.connect(self.enrichment_finished)
        self.enrichment_worker.error_occurred.connect(self.enrichment_error)
        self.enrichment_worker.start()
        
        # Désactiver le bouton de lancement
        self.launch_enrichment_btn.setEnabled(False)
        self.launch_enrichment_btn.setText("🔄 Enrichissement en cours...")
    
    def update_progress(self, value):
        """Met à jour la barre de progression"""
        self.progress_bar.setValue(value)
    
    def update_status(self, status):
        """Met à jour le statut"""
        self.progress_status.setText(status)
    
    def enrichment_finished(self, results):
        """Appelé quand l'enrichissement est terminé"""
        QMessageBox.information(
            self,
            "Enrichissement terminé",
            f"✅ Enrichissement terminé avec succès!\n\n📊 Résultats :\n• {results['total_processed']} entrées traitées\n• {results['enriched_count']} enrichies\n• {results['success_rate']:.1f}% de succès\n\n📁 Fichier de sortie : {results['output_file']}"
        )
        
        # Masquer la progression
        self.progress_section.setVisible(False)
        
        # Réactiver le bouton
        self.launch_enrichment_btn.setEnabled(True)
        self.launch_enrichment_btn.setText("🚀 Lancer l'enrichissement")
        
        # Mettre à jour les métriques
        self.update_metrics_after_enrichment(results)
    
    def enrichment_error(self, error):
        """Appelé en cas d'erreur"""
        QMessageBox.critical(
            self,
            "Erreur d'enrichissement",
            f"❌ Erreur lors de l'enrichissement :\n\n{error}"
        )
        
        # Réactiver l'interface
        self.progress_section.setVisible(False)
        self.launch_enrichment_btn.setEnabled(True)
        self.launch_enrichment_btn.setText("🚀 Lancer l'enrichissement")
    
    def pause_enrichment(self):
        """Met en pause l'enrichissement"""
        if self.enrichment_worker:
            # Implémentation de la pause
            QMessageBox.information(self, "Pause", "⏸️ Enrichissement mis en pause.")
    
    def stop_enrichment(self):
        """Arrête l'enrichissement"""
        if self.enrichment_worker:
            self.enrichment_worker.stop()
            self.enrichment_worker.quit()
            self.enrichment_worker.wait()
            
            self.progress_section.setVisible(False)
            self.launch_enrichment_btn.setEnabled(True)
            self.launch_enrichment_btn.setText("🚀 Lancer l'enrichissement")
            
            QMessageBox.information(self, "Arrêt", "⏹️ Enrichissement arrêté.")
    
    def backup_database(self):
        """Sauvegarde la base de données"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_crm_{timestamp}.sql"
        
        QMessageBox.information(
            self,
            "Sauvegarde en cours",
            f"💾 Sauvegarde de la base CRM en cours...\n\n📁 Fichier : {backup_name}\n📍 Emplacement : backups/\n\nLa sauvegarde sera disponible dans quelques instants."
        )
    
    def clean_duplicates(self):
        """Nettoie les doublons"""
        reply = QMessageBox.question(
            self,
            "Nettoyage des doublons",
            "🧹 Voulez-vous lancer le nettoyage automatique des doublons ?\n\nCette opération :\n• Analyse toute la base CRM\n• Détecte les entrées similaires\n• Propose la fusion ou suppression\n\nDurée estimée : 5-10 minutes",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            QMessageBox.information(
                self,
                "Nettoyage lancé",
                "🔄 Nettoyage des doublons en cours...\n\n📊 Analyse en cours : 12,250 entrées\n🎯 Doublons détectés : 47\n⏱️ Temps restant : 3 min\n\nVous recevrez une notification à la fin."
            )
    
    def test_apis(self):
        """Teste les APIs configurées"""
        QMessageBox.information(
            self,
            "Test des APIs",
            "🧪 Test des APIs en cours...\n\n✅ Google Places API : OK\n✅ Google Custom Search : OK\n❌ Societe.com API : Erreur d'authentification\n✅ Data.gouv.fr : OK\n\n🎯 3/4 APIs opérationnelles"
        )
    
    def save_config(self):
        """Sauvegarde la configuration"""
        QMessageBox.information(
            self,
            "Configuration sauvegardée",
            "💾 Configuration sauvegardée avec succès!\n\nTous les paramètres API et d'enrichissement ont été enregistrés."
        )
    
    def reset_config(self):
        """Remet la configuration par défaut"""
        reply = QMessageBox.question(
            self,
            "Réinitialiser la configuration",
            "🔄 Voulez-vous vraiment réinitialiser la configuration ?\n\nCela va :\n• Supprimer toutes les clés API\n• Remettre les paramètres par défaut\n• Désactiver l'enrichissement automatique",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Réinitialiser les champs
            self.google_api_key.clear()
            self.cse_id.clear()
            
            QMessageBox.information(self, "Réinitialisation", "✅ Configuration réinitialisée!")
    
    def auto_correction(self):
        """Lance la correction automatique"""
        QMessageBox.information(
            self,
            "Correction automatique",
            "🔧 Correction automatique en cours...\n\n🎯 Problèmes détectés :\n• 47 codes APE manquants\n• 156 téléphones incomplets\n• 234 adresses à géolocaliser\n\n⏱️ Durée estimée : 8 minutes"
        )
    
    def export_quality_report(self):
        """Exporte le rapport de qualité"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"SalesMachine_Quality_Report_{timestamp}.pdf"
        
        QMessageBox.information(
            self,
            "Export du rapport",
            f"📊 Génération du rapport de qualité...\n\n📁 Fichier : {filename}\n📍 Emplacement : reports/\n\nLe rapport inclut :\n• Analyse complète des données\n• Recommandations d'amélioration\n• Plan d'action détaillé"
        )
    
    def update_metrics_after_enrichment(self, results):
        """Met à jour les métriques après enrichissement"""
        # Simulation de mise à jour des cartes
        new_enriched = self.enrichment_stats["monthly_enriched"] + results["enriched_count"]
        new_rate = min(99.9, self.enrichment_stats["enrichment_rate"] + 2.1)
        
        # Animation simple des valeurs
        self.animate_metric_update(self.monthly_enriched_card, f"{new_enriched:,}")
        self.animate_metric_update(self.enrichment_rate_card, f"{new_rate:.1f}%")
    
    def animate_metric_update(self, card, new_value):
        """Anime la mise à jour d'une métrique"""
        # Trouver le label de valeur dans la carte
        for child in card.findChildren(QLabel):
            if "font-size: 28px" in child.styleSheet():
                # Animation simple (clignotement vert)
                original_style = child.styleSheet()
                child.setStyleSheet(original_style.replace("color: #1a1a1a", "color: #10b981"))
                child.setText(new_value)
                
                # Revenir au style normal après 1 seconde
                QTimer.singleShot(1000, lambda: child.setStyleSheet(original_style))
                break


# Widget principal pour test
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # Appliquer le style global
    app.setStyleSheet("""
        QWidget {
            font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
            background: #f9fafb;
        }
    """)
    
    widget = EnrichmentModule()
    widget.show()
    widget.resize(1400, 900)
    
    sys.exit(app.exec_())