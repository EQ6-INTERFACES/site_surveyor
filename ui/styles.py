# ui/styles.py

def get_app_stylesheet() -> str:
    """Retorna el estilo completo de la aplicación"""
    return """
    QMainWindow { 
        background-color: #1e1f22; 
        color: #e0e0e0; 
        font-family: 'Segoe UI', sans-serif; 
    }

    QToolBar {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2b2d31, stop:1 #1e1f22);
        border: none;
        spacing: 2px;
        padding: 4px;
        border-bottom: 2px solid #43464d;
    }

    QToolButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5865f2, stop:1 #4752c4);
        color: white;
        border: none;
        padding: 3px 6px;
        border-radius: 3px;
        font-weight: bold;
        font-size: 8pt;
        min-width: 28px;
        min-height: 22px;
        text-align: center;
        margin: 1px;
    }

    QToolButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6b73ff, stop:1 #5865f2);
    }

    QTabBar::tab { 
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2b2d31, stop:1 #1e1f22); 
        color: #a0a0a0; 
        padding: 6px 12px;
        border-top-left-radius: 6px; 
        border-top-right-radius: 6px; 
        font-weight: bold; 
        margin-right: 2px;
        font-size: 8pt;
    } 

    QTabBar::tab:selected { 
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5865f2, stop:1 #4752c4); 
        color: white; 
    }

    QGroupBox { 
        font-size: 9pt;
        font-weight: bold; 
        color: #5865f2; 
        border: 2px solid #43464d; 
        border-radius: 8px; 
        margin-top: 8px;
        padding-top: 8px;
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2b2d31, stop:1 #1e1f22);
    } 

    QPushButton { 
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5865f2, stop:1 #4752c4); 
        color: white; 
        border: none; 
        padding: 4px 8px;
        border-radius: 5px; 
        font-size: 8pt;
        font-weight: bold; 
        min-height: 18px;
    }

    QPushButton:hover { 
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6b73ff, stop:1 #5865f2); 
    }

    QLabel { 
        font-size: 8pt;
        color: #d0d0d0; 
    }

    QLineEdit, QComboBox, QSpinBox { 
        border: 2px solid #43464d; 
        border-radius: 5px; 
        padding: 3px 6px;
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #383c42, stop:1 #2b2d31); 
        font-size: 8pt;
        color: #e0e0e0;
    }

    QGraphicsView { 
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #242424, stop:1 #1a1a1a); 
        border: 2px solid #43464d; 
        border-radius: 10px; 
    }

    QStatusBar {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2b2d31, stop:1 #1e1f22);
        color: #a0a0a0;
        border-top: 2px solid #43464d;
        font-size: 8pt;
        font-weight: bold;
        padding: 2px;
    }

    QTextEdit {
        background-color: #2b2d31;
        color: #e0e0e0;
        border: 1px solid #43464d;
        border-radius: 5px;
        font-family: 'Consolas', monospace;
        font-size: 8pt;
        padding: 5px;
    }

    QTableWidget {
        background-color: #2b2d31;
        alternate-background-color: #383c42;
        gridline-color: #43464d;
        selection-background-color: #5865f2;
    }

    QTableWidget::item {
        padding: 4px;
        border: none;
    }

    QHeaderView::section {
        background-color: #43464d;
        color: #e0e0e0;
        padding: 4px;
        border: 1px solid #5865f2;
        font-weight: bold;
        font-size: 8pt;
    }

    QToolTip {
        background-color: #2b2d31;
        color: #e0e0e0;
        border: 2px solid #5865f2;
        border-radius: 5px;
        padding: 5px;
        font-size: 9pt;
    }

    QScrollBar:vertical {
        background: #2b2d31;
        width: 12px;
        border-radius: 6px;
    }

    QScrollBar::handle:vertical {
        background: #5865f2;
        border-radius: 6px;
        min-height: 20px;
    }

    QScrollBar::handle:vertical:hover {
        background: #6b73ff;
    }
    """

def get_dialog_stylesheet() -> str:
    """Retorna el estilo para diálogos"""
    return """
    QDialog {
        background-color: #1e1f22;
        color: #e0e0e0;
    }
    QGroupBox {
        font-weight: bold;
        color: #5865f2;
        border: 2px solid #43464d;
        border-radius: 8px;
        margin-top: 10px;
        padding-top: 10px;
    }
    QTableWidget {
        background-color: #2b2d31;
        alternate-background-color: #383c42;
        gridline-color: #43464d;
        selection-background-color: #5865f2;
    }
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5865f2, stop:1 #4752c4);
        color: white;
        border: none;
        padding: 8px 15px;
        border-radius: 5px;
        font-weight: bold;
    }
    QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6b73ff, stop:1 #5865f2);
    }
    """