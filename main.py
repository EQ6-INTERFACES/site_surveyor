# main.py
import sys
import atexit
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from ui import MainWindow, get_app_stylesheet

def main():
    """Punto de entrada principal"""
    print("Iniciando Site Surveyor Pro v15.1...")
    
    app = QApplication(sys.argv)
    app.setApplicationName("Site Surveyor Pro v15.1")
    app.setApplicationVersion("15.1")
    
    # Configurar fuente
    font = QFont("Segoe UI", 9)
    app.setFont(font)
    
    # Aplicar estilo
    app.setStyle('Fusion')
    app.setStyleSheet(get_app_stylesheet())
    
    # Crear y mostrar ventana principal
    window = MainWindow()
    window.showMaximized()
    
    # Cleanup al salir
    def cleanup():
        if hasattr(window, 'scanner'):
            window.scanner.stop_iperf_server()
    
    atexit.register(cleanup)
    
    print("Site Surveyor Pro v15.1 listo")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()