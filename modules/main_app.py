# main_app.py
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QStackedWidget, QLabel, QVBoxLayout
)
from PyQt5.QtCore import Qt

# Ajoute le dossier modules au path pour les imports
sys.path.append(r"C:\Users\laeti\OneDrive\Bureau\Sauvgarde avant nettoyage final\SalesMachine_v21_CLEAN_dev_3\ui\modules")

from prospection_module_refonte import ProspectionModuleModernTabbed, Sidebar
from ai_insights.ai_insights_module import IAInsightsModule

# Widget pour modules en maintenance
class MaintenanceWidget(QWidget):
    def __init__(self, module_name):
        super().__init__()
        v = QVBoxLayout(self)
        v.addStretch()
        label = QLabel(f"🛠️ {module_name}\nEn cours de maintenance")
        label.setStyleSheet("font-size:22px;color:#64748b;font-weight:600;")
        label.setAlignment(Qt.AlignCenter)
        v.addWidget(label)
        v.addStretch()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SalesMachine")
        self.setMinimumSize(1500, 900)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # --- Sidebar ---
        self.sidebar = Sidebar({})
        layout.addWidget(self.sidebar)

        # --- QStackedWidget pour les modules ---
        self.stack = QStackedWidget()
        layout.addWidget(self.stack, 1)

        # --- Modules réels et maintenance ---
        self.prospection_module = ProspectionModuleModernTabbed()
        self.campagnes_module = MaintenanceWidget("Campagnes")  # Remplace par ton vrai module si tu l'as
        self.analytics_module = MaintenanceWidget("Analytics")
        self.ai_insights_module = IAInsightsModule()
        self.enrichissement_module = MaintenanceWidget("Enrichissement")
        self.configuration_module = MaintenanceWidget("Configuration")

        # Ajoute les modules au stack (dans l'ordre de la sidebar)
        self.stack.addWidget(self.prospection_module)      # index 0
        self.stack.addWidget(self.campagnes_module)        # index 1
        self.stack.addWidget(self.analytics_module)        # index 2
        self.stack.addWidget(self.ai_insights_module)      # index 3
        self.stack.addWidget(self.enrichissement_module)   # index 4
        self.stack.addWidget(self.configuration_module)    # index 5

        # --- Connexion des boutons de la sidebar à la navigation (ÉTAPE 3) ---
        for idx, btn in enumerate(self.sidebar.module_buttons):
            btn.clicked.connect(lambda _, i=idx: self.stack.setCurrentIndex(i))

        self.stack.setCurrentIndex(0)  # Prospection par défaut

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())