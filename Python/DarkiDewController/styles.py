"""
Fichier de styles CSS pour l'application de contrôle série.
Thème sombre moderne avec couleurs adaptées aux graphiques.
"""

# Thème sombre principal
DARK_THEME = """
/* ===== STYLES GÉNÉRAUX ===== */
QMainWindow {
    background-color: #2b2b2b;
    color: #ffffff;
}

QWidget {
    background-color: #2b2b2b;
    color: #ffffff;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 10pt;
}

/* ===== BARRE DE MENU ===== */
QMenuBar {
    background-color: #333333;
    border-bottom: 1px solid #444444;
}

QMenuBar::item {
    background-color: transparent;
    padding: 5px 10px;
    border-radius: 3px;
}

QMenuBar::item:selected {
    background-color: #3a3a3a;
}

QMenuBar::item:pressed {
    background-color: #4a4a4a;
}

QMenu {
    background-color: #333333;
    border: 1px solid #444444;
    border-radius: 3px;
    padding: 5px;
}

QMenu::item {
    padding: 5px 20px 5px 10px;
    border-radius: 3px;
}

QMenu::item:selected {
    background-color: #4CAF50;
    color: white;
}

QMenu::separator {
    height: 1px;
    background-color: #444444;
    margin: 5px 0;
}

/* ===== BARRE D'ÉTAT ===== */
QStatusBar {
    background-color: #333333;
    border-top: 1px solid #444444;
    color: #aaaaaa;
    font-size: 9pt;
}

QStatusBar QLabel {
    background-color: transparent;
    color: #aaaaaa;
    padding: 2px 8px;
    border-left: 1px solid #444444;
}

/* ===== GROUPBOX ===== */
QGroupBox {
    background-color: #333333;
    border: 2px solid #444444;
    border-radius: 6px;
    margin-top: 10px;
    padding-top: 10px;
    font-weight: bold;
    font-size: 11pt;
    color: #ffffff;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    background-color: #444444;
    color: #ffffff;
    border-radius: 3px;
    margin-left: 10px;
}

/* ===== BOUTONS ===== */
QPushButton {
    background-color: #444444;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 6px 12px;
    font-weight: 500;
    color: #ffffff;
    min-height: 24px;
}

QPushButton:hover {
    background-color: #4a4a4a;
    border-color: #666666;
}

QPushButton:pressed {
    background-color: #3a3a3a;
    border-color: #4CAF50;
}

QPushButton:disabled {
    background-color: #2a2a2a;
    border-color: #333333;
    color: #666666;
}

/* Boutons spéciaux */
QPushButton[style*="success"] {
    background-color: #2E7D32;
    border-color: #388E3C;
    color: white;
}

QPushButton[style*="success"]:hover {
    background-color: #388E3C;
    border-color: #43A047;
}

QPushButton[style*="danger"] {
    background-color: #C62828;
    border-color: #D32F2F;
    color: white;
}

QPushButton[style*="danger"]:hover {
    background-color: #D32F2F;
    border-color: #E53935;
}

QPushButton[style*="primary"] {
    background-color: #1565C0;
    border-color: #1976D2;
    color: white;
}

QPushButton[style*="primary"]:hover {
    background-color: #1976D2;
    border-color: #1E88E5;
}

/* ===== CHAMPS DE SAISIE ===== */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: #3a3a3a;
    border: 1px solid #555555;
    border-radius: 3px;
    padding: 5px 8px;
    color: #ffffff;
    selection-background-color: #4CAF50;
    min-height: 24px;
}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    border: 1px solid #4CAF50;
    background-color: #404040;
}

QComboBox::drop-down {
    border: none;
    background-color: transparent;
}

QComboBox::down-arrow {
    image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0iI2ZmZmZmZiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNOCAxMC41TDMgNS41aDEweiIvPjwvc3ZnPg==);
}

QComboBox QAbstractItemView {
    background-color: #333333;
    border: 1px solid #444444;
    color: #ffffff;
    selection-background-color: #4CAF50;
    selection-color: white;
}

/* ===== LABELS ===== */
QLabel {
    color: #ffffff;
    padding: 2px;
}

QLabel[style*="title"] {
    font-size: 12pt;
    font-weight: bold;
    color: #4CAF50;
}

QLabel[style*="value"] {
    font-size: 11pt;
    font-weight: 500;
    color: #ffffff;
    background-color: #3a3a3a;
    border-radius: 3px;
    padding: 4px 8px;
    border: 1px solid #444444;
}

QLabel[style*="error"] {
    color: #f44336;
    font-weight: bold;
}

QLabel[style*="success"] {
    color: #4CAF50;
    font-weight: bold;
}

QLabel[style*="warning"] {
    color: #ff9800;
    font-weight: bold;
}

/* ===== TEXT EDIT ===== */
QTextEdit, QPlainTextEdit {
    background-color: #1e1e1e;
    border: 1px solid #444444;
    border-radius: 3px;
    color: #ffffff;
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 10pt;
    padding: 5px;
}

QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #4CAF50;
}

QScrollBar:vertical {
    background-color: #2b2b2b;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #444444;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #555555;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    background-color: transparent;
    height: 0px;
}

/* ===== CHECKBOX & RADIO ===== */
QCheckBox, QRadioButton {
    color: #ffffff;
    padding: 4px;
}

QCheckBox::indicator, QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border-radius: 3px;
    border: 1px solid #555555;
    background-color: #3a3a3a;
}

QCheckBox::indicator:checked, QRadioButton::indicator:checked {
    background-color: #4CAF50;
    border-color: #4CAF50;
}

QCheckBox::indicator:checked {
    image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0iI2ZmZmZmZiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMTMuMzUgNC42NUw2LjIgMTEuOEwyLjY1IDguMjVsMS41LTEuNUw2LjIgOC44bDUuNjUtNS42NXoiLz48L3N2Zz4=);
}

QRadioButton::indicator:checked {
    border-radius: 8px;
}

QCheckBox:hover::indicator, QRadioButton:hover::indicator {
    border-color: #666666;
}

/* ===== ONGLETS ===== */
QTabWidget::pane {
    background-color: #333333;
    border: 1px solid #444444;
    border-radius: 4px;
    margin: 2px;
}

QTabBar::tab {
    background-color: #3a3a3a;
    border: 1px solid #444444;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    padding: 8px 16px;
    margin-right: 2px;
    color: #aaaaaa;
    font-weight: 500;
}

QTabBar::tab:selected {
    background-color: #444444;
    color: #ffffff;
    border-bottom: 2px solid #4CAF50;
}

QTabBar::tab:hover:!selected {
    background-color: #404040;
    color: #dddddd;
}

QTabBar::tab:disabled {
    background-color: #2a2a2a;
    color: #666666;
}

/* ===== PROGRESS BAR ===== */
QProgressBar {
    background-color: #3a3a3a;
    border: 1px solid #444444;
    border-radius: 3px;
    text-align: center;
    color: #ffffff;
    height: 20px;
}

QProgressBar::chunk {
    background-color: #4CAF50;
    border-radius: 3px;
}

/* ===== TABLEAU ===== */
QTableView, QTableWidget {
    background-color: #2b2b2b;
    border: 1px solid #444444;
    gridline-color: #444444;
    color: #ffffff;
    selection-background-color: #4CAF50;
    selection-color: white;
    alternate-background-color: #333333;
}

QHeaderView::section {
    background-color: #3a3a3a;
    border: 1px solid #444444;
    padding: 5px;
    font-weight: bold;
    color: #ffffff;
}

QTableView QTableCornerButton::section {
    background-color: #3a3a3a;
    border: 1px solid #444444;
}

/* ===== LISTE ===== */
QListWidget {
    background-color: #2b2b2b;
    border: 1px solid #444444;
    border-radius: 3px;
    color: #ffffff;
    padding: 2px;
}

QListWidget::item {
    padding: 5px;
    border-bottom: 1px solid #333333;
}

QListWidget::item:selected {
    background-color: #4CAF50;
    color: white;
}

QListWidget::item:hover:!selected {
    background-color: #3a3a3a;
}

/* ===== SCROLL BAR ===== */
QScrollBar:horizontal {
    background-color: #2b2b2b;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #444444;
    border-radius: 6px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #555555;
}

/* ===== TOOLTIP ===== */
QToolTip {
    background-color: #333333;
    border: 1px solid #444444;
    border-radius: 3px;
    color: #ffffff;
    padding: 5px;
}

/* ===== DIALOG ===== */
QDialog {
    background-color: #2b2b2b;
    border: 1px solid #444444;
}

/* ===== SÉPARATEURS ===== */
QFrame[frameShape="4"] /* HLine */ {
    background-color: #444444;
    max-height: 1px;
    min-height: 1px;
}

QFrame[frameShape="5"] /* VLine */ {
    background-color: #444444;
    max-width: 1px;
    min-width: 1px;
}

/* ===== STYLES SPÉCIFIQUES POUR NOTRE APPLICATION ===== */

/* Console HEX */
QTextEdit#hexConsole {
    background-color: #1a1a1a;
    color: #4CAF50;
    font-family: 'Courier New', monospace;
    font-size: 10pt;
    border: 1px solid #333333;
}

/* Graphiques PyQtGraph */
GraphicsView {
    background-color: #1e1e1e;
    border: 1px solid #333333;
    border-radius: 4px;
}

/* Labels de valeur numérique */
QLabel#deltaTempValue {
    color: #2196F3;
    font-size: 14pt;
    font-weight: bold;
}

QLabel#dewOffsetValue {
    color: #FF9800;
    font-size: 14pt;
    font-weight: bold;
}

/* Boutons de commande */
QPushButton#cmdButton {
    background-color: #333333;
    border: 2px solid #555555;
    font-weight: bold;
    min-width: 100px;
}

QPushButton#cmdButton:hover {
    border-color: #4CAF50;
}

/* Indicateurs de connexion */
QLabel#connectedIndicator {
    background-color: #4CAF50;
    border-radius: 8px;
    min-width: 16px;
    min-height: 16px;
}

QLabel#disconnectedIndicator {
    background-color: #f44336;
    border-radius: 8px;
    min-width: 16px;
    min-height: 16px;
}

/* Style pour les données importantes */
QLabel.highlight {
    background-color: rgba(76, 175, 80, 0.1);
    border: 1px solid rgba(76, 175, 80, 0.3);
    border-radius: 4px;
    padding: 8px;
    font-weight: bold;
}

/* Style pour les avertissements */
QLabel.warning {
    background-color: rgba(255, 152, 0, 0.1);
    border: 1px solid rgba(255, 152, 0, 0.3);
    border-radius: 4px;
    padding: 8px;
    color: #ff9800;
}

/* Style pour les erreurs */
QLabel.error {
    background-color: rgba(244, 67, 54, 0.1);
    border: 1px solid rgba(244, 67, 54, 0.3);
    border-radius: 4px;
    padding: 8px;
    color: #f44336;
}

/* Style pour les boutons de graphique */
QPushButton.plotControl {
    background-color: #333333;
    border: 1px solid #444444;
    border-radius: 3px;
    padding: 4px 8px;
    font-size: 9pt;
    min-height: 20px;
}

QPushButton.plotControl:hover {
    background-color: #3a3a3a;
}

/* Style pour les boutons d'export */
QPushButton.exportButton {
    background-color: #2E7D32;
    border-color: #388E3C;
    color: white;
    font-weight: bold;
}

QPushButton.exportButton:hover {
    background-color: #388E3C;
}

/* Style pour les boutons d'effacement */
QPushButton.clearButton {
    background-color: #C62828;
    border-color: #D32F2F;
    color: white;
}

QPushButton.clearButton:hover {
    background-color: #D32F2F;
}
"""

# Thème clair alternatif
LIGHT_THEME = """
/* ===== STYLES GÉNÉRAUX ===== */
QMainWindow {
    background-color: #f5f5f5;
    color: #333333;
}

QWidget {
    background-color: #f5f5f5;
    color: #333333;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 10pt;
}

/* ===== BARRE DE MENU ===== */
QMenuBar {
    background-color: #ffffff;
    border-bottom: 1px solid #dddddd;
}

QMenuBar::item {
    background-color: transparent;
    padding: 5px 10px;
    border-radius: 3px;
}

QMenuBar::item:selected {
    background-color: #e0e0e0;
}

QMenuBar::item:pressed {
    background-color: #d0d0d0;
}

QMenu {
    background-color: #ffffff;
    border: 1px solid #dddddd;
    border-radius: 3px;
    padding: 5px;
}

QMenu::item {
    padding: 5px 20px 5px 10px;
    border-radius: 3px;
}

QMenu::item:selected {
    background-color: #4CAF50;
    color: white;
}

/* ===== BARRE D'ÉTAT ===== */
QStatusBar {
    background-color: #ffffff;
    border-top: 1px solid #dddddd;
    color: #666666;
}

/* ===== GROUPBOX ===== */
QGroupBox {
    background-color: #ffffff;
    border: 2px solid #dddddd;
    border-radius: 6px;
    margin-top: 10px;
    padding-top: 10px;
    font-weight: bold;
    font-size: 11pt;
    color: #333333;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    background-color: #4CAF50;
    color: white;
    border-radius: 3px;
    margin-left: 10px;
}

/* ===== BOUTONS ===== */
QPushButton {
    background-color: #e0e0e0;
    border: 1px solid #cccccc;
    border-radius: 4px;
    padding: 6px 12px;
    font-weight: 500;
    color: #333333;
}

QPushButton:hover {
    background-color: #d0d0d0;
    border-color: #bbbbbb;
}

QPushButton:pressed {
    background-color: #c0c0c0;
    border-color: #4CAF50;
}

/* ===== CHAMPS DE SAISIE ===== */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: white;
    border: 1px solid #cccccc;
    border-radius: 3px;
    padding: 5px 8px;
    color: #333333;
    selection-background-color: #4CAF50;
}

/* ===== LABELS ===== */
QLabel {
    color: #333333;
}

/* ===== TEXT EDIT ===== */
QTextEdit, QPlainTextEdit {
    background-color: white;
    border: 1px solid #cccccc;
    border-radius: 3px;
    color: #333333;
    font-family: 'Consolas', 'Monaco', monospace;
}

/* ===== CHECKBOX & RADIO ===== */
QCheckBox, QRadioButton {
    color: #333333;
}

/* ===== ONGLETS ===== */
QTabWidget::pane {
    background-color: #ffffff;
    border: 1px solid #dddddd;
}

QTabBar::tab {
    background-color: #e0e0e0;
    border: 1px solid #dddddd;
    padding: 8px 16px;
    color: #666666;
}

QTabBar::tab:selected {
    background-color: white;
    color: #333333;
    border-bottom: 2px solid #4CAF50;
}
"""

# Styles pour les boutons de commande spécifiques
COMMAND_BUTTONS = {
    'HELLO': "QPushButton { background-color: #2196F3; color: white; font-weight: bold; }",
    'DELTA': "QPushButton { background-color: #FF9800; color: white; font-weight: bold; }",
    'OFFSET': "QPushButton { background-color: #9C27B0; color: white; font-weight: bold; }",
    'MODE': "QPushButton { background-color: #3F51B5; color: white; font-weight: bold; }",
    'STATUS': "QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }",
    'CONNECT': "QPushButton { background-color: #2E7D32; color: white; font-weight: bold; }",
    'DISCONNECT': "QPushButton { background-color: #C62828; color: white; font-weight: bold; }"
}

# Styles pour les valeurs de statut
STATUS_STYLES = {
    'normal': "QLabel { color: #4CAF50; font-weight: bold; }",
    'warning': "QLabel { color: #FF9800; font-weight: bold; }",
    'error': "QLabel { color: #F44336; font-weight: bold; }",
    'critical': "QLabel { color: #D32F2F; font-weight: bold; background-color: rgba(211, 47, 47, 0.1); }"
}

# Styles pour les graphiques
GRAPH_STYLES = {
    'temperature': "color: #FF5252;",  # Rouge
    'humidity': "color: #2196F3;",     # Bleu
    'tube_temperature': "color: #FF9800;",  # Orange
    'dew_point': "color: #4CAF50;",    # Vert
    'pwm': "color: #9C27B0;",         # Violet
    'delta_temp': "color: #00BCD4;",   # Cyan
    'dew_offset': "color: #795548;"    # Marron
}

# Fonction utilitaire pour appliquer des styles
def apply_theme(app, theme='dark'):
    """
    Applique un thème à l'application
    
    Args:
        app: L'application QApplication
        theme: 'dark' ou 'light'
    """
    if theme == 'dark':
        app.setStyleSheet(DARK_THEME)
    elif theme == 'light':
        app.setStyleSheet(LIGHT_THEME)
    
    # Définir une palette de couleurs cohérente
    palette = app.palette()
    if theme == 'dark':
        palette.setColor(palette.Window, QColor(43, 43, 43))
        palette.setColor(palette.WindowText, QColor(255, 255, 255))
        palette.setColor(palette.Base, QColor(30, 30, 30))
        palette.setColor(palette.AlternateBase, QColor(51, 51, 51))
        palette.setColor(palette.ToolTipBase, QColor(51, 51, 51))
        palette.setColor(palette.ToolTipText, QColor(255, 255, 255))
        palette.setColor(palette.Text, QColor(255, 255, 255))
        palette.setColor(palette.Button, QColor(68, 68, 68))
        palette.setColor(palette.ButtonText, QColor(255, 255, 255))
        palette.setColor(palette.BrightText, QColor(255, 0, 0))
        palette.setColor(palette.Link, QColor(42, 130, 218))
        palette.setColor(palette.Highlight, QColor(76, 175, 80))
        palette.setColor(palette.HighlightedText, QColor(0, 0, 0))
    else:
        palette.setColor(palette.Window, QColor(245, 245, 245))
        palette.setColor(palette.WindowText, QColor(0, 0, 0))
        palette.setColor(palette.Base, QColor(255, 255, 255))
        palette.setColor(palette.AlternateBase, QColor(240, 240, 240))
        palette.setColor(palette.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(palette.ToolTipText, QColor(0, 0, 0))
        palette.setColor(palette.Text, QColor(0, 0, 0))
        palette.setColor(palette.Button, QColor(240, 240, 240))
        palette.setColor(palette.ButtonText, QColor(0, 0, 0))
        palette.setColor(palette.BrightText, QColor(255, 0, 0))
        palette.setColor(palette.Link, QColor(0, 0, 255))
        palette.setColor(palette.Highlight, QColor(76, 175, 80))
        palette.setColor(palette.HighlightedText, QColor(255, 255, 255))
    
    app.setPalette(palette)

# Classes de style pour faciliter l'application
class StyleHelper:
    """Helper pour appliquer des styles spécifiques"""
    
    @staticmethod
    def set_command_button(button, command_type):
        """Applique le style approprié à un bouton de commande"""
        if command_type in COMMAND_BUTTONS:
            button.setStyleSheet(COMMAND_BUTTONS[command_type])
    
    @staticmethod
    def set_status_style(label, status='normal'):
        """Applique le style approprié à un label de statut"""
        if status in STATUS_STYLES:
            label.setStyleSheet(STATUS_STYLES[status])
    
    @staticmethod
    def set_connection_status(widget, connected):
        """Applique le style de statut de connexion"""
        if connected:
            widget.setStyleSheet("""
                QWidget {
                    border: 2px solid #4CAF50;
                    border-radius: 4px;
                    background-color: rgba(76, 175, 80, 0.1);
                }
            """)
        else:
            widget.setStyleSheet("""
                QWidget {
                    border: 2px solid #F44336;
                    border-radius: 4px;
                    background-color: rgba(244, 67, 54, 0.1);
                }
            """)
    
    @staticmethod
    def create_gradient_background(start_color, end_color):
        """Crée un dégradé CSS"""
        return f"""
            background: qlineargradient(
                x1: 0, y1: 0,
                x2: 1, y2: 1,
                stop: 0 {start_color},
                stop: 1 {end_color}
            );
        """

# Styles prédéfinis pour les widgets courants
class WidgetStyles:
    """Styles prédéfinis pour différents widgets"""
    
    @staticmethod
    def title_label():
        """Style pour les titres"""
        return """
            QLabel {
                font-size: 14pt;
                font-weight: bold;
                color: #4CAF50;
                padding: 5px;
                border-bottom: 2px solid #4CAF50;
            }
        """
    
    @staticmethod
    def value_display():
        """Style pour l'affichage des valeurs"""
        return """
            QLabel {
                font-size: 12pt;
                font-weight: bold;
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 4px;
                padding: 8px 12px;
                min-width: 80px;
                text-align: center;
            }
        """
    
    @staticmethod
    def console_output():
        """Style pour les consoles de sortie"""
        return """
            QTextEdit {
                background-color: #1a1a1a;
                color: #4CAF50;
                font-family: 'Courier New', monospace;
                font-size: 10pt;
                border: 1px solid #333333;
                border-radius: 3px;
            }
            QScrollBar:vertical {
                background-color: #2b2b2b;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #4CAF50;
                border-radius: 6px;
                min-height: 20px;
            }
        """
    
    @staticmethod
    def data_table():
        """Style pour les tableaux de données"""
        return """
            QTableWidget {
                background-color: #2b2b2b;
                border: 1px solid #444444;
                gridline-color: #444444;
                color: #ffffff;
                selection-background-color: #4CAF50;
                selection-color: white;
                alternate-background-color: #333333;
            }
            QHeaderView::section {
                background-color: #3a3a3a;
                border: 1px solid #444444;
                padding: 5px;
                font-weight: bold;
                color: #ffffff;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #4CAF50;
                color: white;
            }
        """

# Fonction pour initialiser l'apparence de l'application
def setup_appearance(app, theme='dark'):
    """
    Configure l'apparence complète de l'application
    
    Args:
        app: L'application QApplication
        theme: 'dark' ou 'light'
    """
    # Appliquer le thème
    apply_theme(app, theme)
    
    # Définir une icône d'application
    try:
        from PyQt6.QtGui import QIcon
        app.setWindowIcon(QIcon(":/icons/app_icon.png"))
    except:
        pass
    
    # Configurer la police par défaut
    font = app.font()
    font.setPointSize(10)
    font.setFamily("Segoe UI")
    app.setFont(font)
    
    # Définir le style de fusion
    app.setStyle("Fusion")

# Exemple d'utilisation dans main.py
"""
# Dans votre main.py, ajoutez:
import styles

# Pendant l'initialisation de l'application:
app = QApplication(sys.argv)
styles.setup_appearance(app, theme='dark')

# Pour styliser un bouton spécifique:
button = QPushButton("HELLO")
styles.StyleHelper.set_command_button(button, 'HELLO')

# Pour styliser un label de statut:
label = QLabel("Connecté")
styles.StyleHelper.set_status_style(label, 'normal')
"""

if __name__ == "__main__":
    print("Module de styles pour l'application de contrôle série")
    print("Utilisation: import styles")