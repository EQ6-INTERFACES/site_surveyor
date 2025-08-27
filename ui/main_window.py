# ui/main_window.py - CORREGIDO CON HEATMAPS POR SSID Y APs FUNCIONALES
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import os
import json
from datetime import datetime
from typing import Optional, List, Dict

from core import Config, WiFiScanner, SurveyPoint, NetworkData, IperfResults, ProjectInfo
from analysis import APLocator, HeatmapGenerator
from reporting import ReportGenerator
from .widgets import SurveyPointWidget, APWidget, ServiceMonitor, ZoomableGraphicsView, HeatmapLegend
from .styles import get_app_stylesheet

class HeatmapDialog(QDialog):
    """Diálogo para seleccionar opciones del heatmap"""
    
    def __init__(self, available_networks: List[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Generar Heatmap")
        self.setModal(True)
        self.resize(400, 300)
        self.setStyleSheet(get_app_stylesheet())
        
        layout = QVBoxLayout(self)
        
        # Tipo de métrica
        metric_group = QGroupBox("📊 Métrica a visualizar")
        metric_layout = QVBoxLayout(metric_group)
        
        self.metric_combo = QComboBox()
        self.metric_combo.addItems([
            "RSSI (Señal WiFi)",
            "SNR (Relación Señal/Ruido)",
            "Download (Velocidad descarga)",
            "Upload (Velocidad subida)",
            "Ping (Latencia)",
            "Jitter (Variación de latencia)"
        ])
        metric_layout.addWidget(self.metric_combo)
        
        layout.addWidget(metric_group)
        
        # Selección de red
        network_group = QGroupBox("📡 Red específica (opcional)")
        network_layout = QVBoxLayout(network_group)
        
        self.all_networks_radio = QRadioButton("Todas las redes (señal más fuerte)")
        self.all_networks_radio.setChecked(True)
        network_layout.addWidget(self.all_networks_radio)
        
        self.specific_network_radio = QRadioButton("Red específica:")
        network_layout.addWidget(self.specific_network_radio)
        
        self.network_combo = QComboBox()
        self.network_combo.setEnabled(False)
        self.network_combo.addItems(["Seleccionar red..."] + available_networks)
        network_layout.addWidget(self.network_combo)
        
        # Conectar radio buttons
        self.specific_network_radio.toggled.connect(self.network_combo.setEnabled)
        
        layout.addWidget(network_group)
        
        # Botones
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        
        generate_btn = QPushButton("Generar Heatmap")
        generate_btn.clicked.connect(self.accept)
        generate_btn.setStyleSheet("QPushButton { background: #4CAF50; }")
        
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()
        button_layout.addWidget(generate_btn)
        
        layout.addLayout(button_layout)
    
    def get_selected_options(self) -> dict:
        """Retorna las opciones seleccionadas"""
        metric_map = {
            "RSSI (Señal WiFi)": "rssi",
            "SNR (Relación Señal/Ruido)": "snr",
            "Download (Velocidad descarga)": "download",
            "Upload (Velocidad subida)": "upload",
            "Ping (Latencia)": "ping",
            "Jitter (Variación de latencia)": "jitter"
        }
        
        metric = metric_map[self.metric_combo.currentText()]
        
        target_ssid = None
        if self.specific_network_radio.isChecked() and self.network_combo.currentIndex() > 0:
            target_ssid = self.network_combo.currentText()
        
        return {
            'metric': metric,
            'target_ssid': target_ssid,
            'description': self.metric_combo.currentText() + 
                         (f" - {target_ssid}" if target_ssid else " - Todas las redes")
        }

class MainWindow(QMainWindow):
    """Ventana principal de Site Surveyor Pro - CORREGIDA"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Site Surveyor Pro v15.1 - Enterprise Edition")
        self.setGeometry(100, 100, 1400, 900)
        self.setStyleSheet(get_app_stylesheet())
        
        # Inicializar componentes
        self.config = Config()
        self.scanner = WiFiScanner()
        self.ap_locator = APLocator()
        self.heatmap_gen = HeatmapGenerator()
        self.project_info = ProjectInfo()
        
        # Estado de la aplicación
        self.survey_points: List[SurveyPoint] = []
        self.ap_positions: Dict = {}
        self.floor_plan_path: Optional[str] = None
        self.pixels_per_meter: Optional[float] = None
        self.survey_mode = False
        self.calibration_mode = False
        self.calibration_points = []
        self.current_networks = []
        self.current_heatmap_legend = None  # Para la leyenda del heatmap
        
        # Inicializar UI
        self.create_ui()
        self.create_toolbar()
        self.setup_status_bar()
        
        # Inicializar servicios
        self.scanner.start_iperf_server()
        
        # Timer para escaneo WiFi
        self.wifi_timer = QTimer()
        self.wifi_timer.timeout.connect(self.scan_wifi)
        self.wifi_timer.start(self.config.get('wifi', 'scan_interval', 15) * 1000)
        
        # Hacer escaneo inicial
        QTimer.singleShot(1000, self.scan_wifi)
    
    def create_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # Sidebar
        sidebar = self.create_sidebar()
        sidebar.setMaximumWidth(350)
        
        # Vista del mapa
        map_widget = self.create_map_view()
        
        main_layout.addWidget(sidebar, 3)
        main_layout.addWidget(map_widget, 7)
    
    def create_toolbar(self):
        toolbar = QToolBar("Principal")
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(12, 12))
        
        # Acciones de archivo
        load_plan_action = QAction("📂\nPlano", self)
        load_plan_action.triggered.connect(self.load_floor_plan)
        toolbar.addAction(load_plan_action)
        
        save_action = QAction("💾\nGuardar", self)
        save_action.triggered.connect(self.save_survey)
        toolbar.addAction(save_action)
        
        load_action = QAction("📈\nCargar", self)
        load_action.triggered.connect(self.load_survey)
        toolbar.addAction(load_action)
        
        toolbar.addSeparator()
        
        # Survey
        calibrate_action = QAction("📏\nEscala", self)
        calibrate_action.triggered.connect(self.start_calibration)
        toolbar.addAction(calibrate_action)
        
        self.survey_action = QAction("▶\nSurvey", self)
        self.survey_action.triggered.connect(self.toggle_survey_mode)
        toolbar.addAction(self.survey_action)
        
        toolbar.addSeparator()
        
        # Análisis
        ap_action = QAction("📡\nAPs", self)
        ap_action.triggered.connect(self.estimate_aps)
        toolbar.addAction(ap_action)
        
        heatmap_action = QAction("🗺\nMapa", self)
        heatmap_action.triggered.connect(self.show_heatmap_dialog)
        toolbar.addAction(heatmap_action)
        
        report_action = QAction("📄\nReporte", self)
        report_action.triggered.connect(self.generate_report)
        toolbar.addAction(report_action)
        
        self.addToolBar(toolbar)
    
    def create_sidebar(self):
        tabs = QTabWidget()
        
        # Tab 1: Proyecto
        project_tab = self.create_project_tab()
        tabs.addTab(project_tab, "📋 Proyecto")
        
        # Tab 2: Redes WiFi
        wifi_tab = self.create_wifi_tab()
        tabs.addTab(wifi_tab, "📡 Redes")
        
        # Tab 3: Servicios
        services_tab = self.create_services_tab()
        tabs.addTab(services_tab, "📊 Servicios")
        
        # Tab 4: Log
        log_tab = self.create_log_tab()
        tabs.addTab(log_tab, "📜 Log")
        
        return tabs
    
    def create_project_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Información del cliente
        client_group = QGroupBox("🏢 Cliente")
        client_layout = QGridLayout(client_group)
        
        client_layout.addWidget(QLabel("Cliente:"), 0, 0)
        self.client_entry = QLineEdit()
        client_layout.addWidget(self.client_entry, 0, 1)
        
        client_layout.addWidget(QLabel("Sitio:"), 1, 0)
        self.site_entry = QLineEdit()
        client_layout.addWidget(self.site_entry, 1, 1)
        
        client_layout.addWidget(QLabel("Técnico:"), 2, 0)
        self.technician_entry = QLineEdit()
        client_layout.addWidget(self.technician_entry, 2, 1)
        
        layout.addWidget(client_group)
        
        # Estadísticas
        stats_group = QGroupBox("📊 Estadísticas")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_label = QLabel("📍 Puntos: 0\n📡 APs: 0\n🗺 Mapas: 0")
        self.stats_label.setStyleSheet("color: #d0d0d0; font-family: monospace;")
        stats_layout.addWidget(self.stats_label)
        
        layout.addWidget(stats_group)
        
        # Información de calibración
        cal_group = QGroupBox("📏 Calibración")
        cal_layout = QVBoxLayout(cal_group)
        
        self.calibration_label = QLabel("Sin calibrar")
        self.calibration_label.setStyleSheet("color: #f44336;")
        cal_layout.addWidget(self.calibration_label)
        
        layout.addWidget(cal_group)
        layout.addStretch()
        
        return widget
    
    def create_wifi_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header = QHBoxLayout()
        header.addWidget(QLabel("📡 Redes WiFi:"))
        
        refresh_btn = QPushButton("🔄")
        refresh_btn.setMaximumSize(30, 25)
        refresh_btn.clicked.connect(self.scan_wifi)
        header.addWidget(refresh_btn)
        
        layout.addLayout(header)
        
        # Tabla de redes
        self.wifi_table = QTableWidget()
        self.wifi_table.setColumnCount(5)
        self.wifi_table.setHorizontalHeaderLabels(["SSID", "BSSID", "RSSI", "Canal", "Seguridad"])
        
        header = self.wifi_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        
        self.wifi_table.setAlternatingRowColors(True)
        self.wifi_table.verticalHeader().setDefaultSectionSize(20)
        
        layout.addWidget(self.wifi_table)
        
        return widget
    
    def create_services_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header = QHBoxLayout()
        header.addWidget(QLabel("📊 Monitoreo de Servicios"))
        
        self.toggle_all_btn = QPushButton("▶ Iniciar Todo")
        self.toggle_all_btn.clicked.connect(self.toggle_all_services)
        header.addWidget(self.toggle_all_btn)
        
        layout.addLayout(header)
        
        # Servicios
        services_scroll = QScrollArea()
        services_scroll.setWidgetResizable(True)
        services_scroll.setMaximumHeight(350)
        
        services_widget = QWidget()
        services_layout = QVBoxLayout(services_widget)
        services_layout.setSpacing(2)
        
        self.service_widgets = {}
        services = [
            ("DNS Google", "8.8.8.8", "#FF9500"),
            ("DNS Cloudflare", "1.1.1.1", "#FF6B35"),
            ("Gateway Local", self.scanner._get_gateway_ip(), "#4CD964"),
            ("Microsoft Teams", "teams.microsoft.com", "#5558AF"),
            ("Google Meet", "meet.google.com", "#4285F4")
        ]
        
        for name, target, color in services:
            service = ServiceMonitor(name, target, color)
            self.service_widgets[name] = service
            services_layout.addWidget(service)
        
        services_scroll.setWidget(services_widget)
        layout.addWidget(services_scroll)
        
        return widget
    
    def create_log_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        header = QHBoxLayout()
        header.addWidget(QLabel("📜 Log:"))
        
        clear_btn = QPushButton("🗑")
        clear_btn.setMaximumSize(30, 25)
        clear_btn.clicked.connect(self.clear_log)
        header.addWidget(clear_btn)
        
        layout.addLayout(header)
        
        self.log_widget = QTextEdit()
        self.log_widget.setReadOnly(True)
        self.log_widget.setMaximumHeight(200)
        layout.addWidget(self.log_widget)
        
        return widget
    
    def create_map_view(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Header
        map_header = QHBoxLayout()
        
        self.floor_plan_info = QLabel("📂 Sin plano cargado")
        self.floor_plan_info.setStyleSheet("color: #d0d0d0; font-weight: bold;")
        
        zoom_in_btn = QPushButton("🔍+")
        zoom_in_btn.setMaximumSize(35, 25)
        zoom_in_btn.clicked.connect(self.zoom_in)
        
        zoom_out_btn = QPushButton("🔍-")
        zoom_out_btn.setMaximumSize(35, 25)
        zoom_out_btn.clicked.connect(self.zoom_out)
        
        fit_btn = QPushButton("📐")
        fit_btn.setMaximumSize(35, 25)
        fit_btn.clicked.connect(self.fit_in_view)
        
        clear_btn = QPushButton("🗑")
        clear_btn.setMaximumSize(35, 25)
        clear_btn.clicked.connect(self.clear_heatmap)
        
        map_header.addWidget(self.floor_plan_info)
        map_header.addStretch()
        map_header.addWidget(clear_btn)
        map_header.addWidget(zoom_out_btn)
        map_header.addWidget(fit_btn)
        map_header.addWidget(zoom_in_btn)
        
        layout.addLayout(map_header)
        
        # Vista gráfica
        self.graphics_view = ZoomableGraphicsView()
        self.scene = QGraphicsScene()
        self.graphics_view.setScene(self.scene)
        self.graphics_view.mousePressEvent = self.on_map_click
        
        layout.addWidget(self.graphics_view)
        
        return widget
    
    def setup_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        ip = self.scanner.local_ip
        self.status_bar.showMessage(f"🚀 Site Surveyor Pro v15.1 | IP: {ip}")
    
    def log(self, message: str):
        """Registrar mensaje en log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_widget.append(f"[{timestamp}] {message}")
        scrollbar = self.log_widget.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def update_stats(self):
        """Actualizar estadísticas"""
        num_points = len(self.survey_points)
        num_aps = len(self.ap_positions)
        num_maps = 1 if any(item.zValue() == 1 for item in self.scene.items()) else 0
        
        self.stats_label.setText(f"📍 Puntos: {num_points}\n📡 APs: {num_aps}\n🗺 Mapas: {num_maps}")
    
    def scan_wifi(self):
        """Escanear redes WiFi"""
        networks = self.scanner.scan()
        self.current_networks = networks
        self.update_wifi_table(networks)
        self.log(f"📡 {len(networks)} redes detectadas")
    
    def update_wifi_table(self, networks: List[NetworkData]):
        """Actualizar tabla de redes"""
        self.wifi_table.setRowCount(len(networks))
        
        for row, network in enumerate(networks):
            self.wifi_table.setItem(row, 0, QTableWidgetItem(network.ssid))
            self.wifi_table.setItem(row, 1, QTableWidgetItem(network.bssid))
            
            rssi_item = QTableWidgetItem(f"{network.signal} dBm")
            if network.signal >= -60:
                rssi_item.setBackground(QColor(200, 255, 200))
            elif network.signal >= -70:
                rssi_item.setBackground(QColor(255, 255, 200))
            else:
                rssi_item.setBackground(QColor(255, 200, 200))
            self.wifi_table.setItem(row, 2, rssi_item)
            
            self.wifi_table.setItem(row, 3, QTableWidgetItem(str(network.channel)))
            self.wifi_table.setItem(row, 4, QTableWidgetItem(network.security))
    
    def toggle_all_services(self):
        """Toggle todos los servicios"""
        any_active = any(w.is_monitoring for w in self.service_widgets.values())
        
        for widget in self.service_widgets.values():
            if any_active:
                widget.stop_monitoring()
            else:
                widget.start_monitoring()
        
        self.toggle_all_btn.setText("⏸ Detener Todo" if not any_active else "▶ Iniciar Todo")
    
    def load_floor_plan(self):
        """Cargar plano de piso"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Cargar Plano", "", 
            "Imágenes (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_path:
            pixmap = QPixmap(file_path)
            if pixmap.isNull():
                QMessageBox.critical(self, "Error", "No se pudo cargar la imagen")
                return
            
            self.floor_plan_path = file_path
            self.scene.clear()
            self.scene.addPixmap(pixmap)
            self.scene.setSceneRect(pixmap.rect())
            
            self.graphics_view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
            
            filename = os.path.basename(file_path)
            self.floor_plan_info.setText(f"📂 {filename}")
            self.log(f"📂 Plano cargado: {filename}")
    
    def start_calibration(self):
        """Iniciar calibración de escala"""
        if not self.floor_plan_path:
            QMessageBox.warning(self, "Sin Plano", "Primero debe cargar un plano")
            return
        
        self.calibration_mode = True
        self.calibration_points = []
        self.log("📏 Iniciando calibración de escala")
        
        QMessageBox.information(
            self, "Calibración", 
            "Haga clic en dos puntos cuya distancia conoce"
        )
    
    def toggle_survey_mode(self):
        """Toggle modo survey"""
        if not self.floor_plan_path:
            QMessageBox.warning(self, "Sin Plano", "Primero debe cargar un plano")
            return
        
        self.survey_mode = not self.survey_mode
        self.survey_action.setText("⏸\nSurvey" if self.survey_mode else "▶\nSurvey")
        
        status = "iniciado" if self.survey_mode else "detenido"
        self.log(f"📍 Modo survey {status}")
        
        # Ajustar frecuencia de escaneo
        interval = 5000 if self.survey_mode else 15000
        self.wifi_timer.setInterval(interval)
    
    def on_map_click(self, event):
        """Manejar click en mapa"""
        if event.button() != Qt.MouseButton.LeftButton:
            return
        
        try:
            scene_pos = self.graphics_view.mapToScene(event.position().toPoint())
        except AttributeError:
            scene_pos = self.graphics_view.mapToScene(event.pos())
        
        x, y = scene_pos.x(), scene_pos.y()
        
        if self.calibration_mode:
            self.handle_calibration_click(x, y)
        elif self.survey_mode:
            self.handle_survey_click(x, y)
    
    def handle_calibration_click(self, x: float, y: float):
        """Manejar click de calibración"""
        self.calibration_points.append((x, y))
        
        # Agregar punto visual
        point = QGraphicsEllipseItem(-5, -5, 10, 10)
        point.setPos(x, y)
        point.setBrush(QBrush(QColor(255, 0, 0)))
        point.setZValue(20)
        self.scene.addItem(point)
        
        if len(self.calibration_points) == 2:
            distance, ok = QInputDialog.getDouble(
                self, "Distancia Real", 
                "Ingrese la distancia real (metros):",
                1.0, 0.1, 1000.0, 2
            )
            
            if ok and distance > 0:
                import math
                p1, p2 = self.calibration_points
                pixel_distance = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
                self.pixels_per_meter = pixel_distance / distance
                
                self.ap_locator.pixels_per_meter = self.pixels_per_meter
                
                self.calibration_label.setText(f"{self.pixels_per_meter:.2f} px/m")
                self.calibration_label.setStyleSheet("color: #4CAF50;")
                
                self.log(f"📏 Escala: {self.pixels_per_meter:.2f} px/m")
                QMessageBox.information(
                    self, "Calibración", 
                    f"Escala: {self.pixels_per_meter:.2f} píxeles por metro"
                )
            
            self.calibration_mode = False
            self.calibration_points = []
    
    def handle_survey_click(self, x: float, y: float):
        """Manejar click de survey"""
        # Escanear redes
        networks = self.scanner.scan()
        if not networks:
            QMessageBox.warning(self, "Error", "No se detectaron redes")
            return
        
        # Realizar pruebas de rendimiento
        iperf_results = self.scanner.perform_full_test()
        
        # Crear punto
        survey_point = SurveyPoint(
            x=x, 
            y=y, 
            timestamp=datetime.now(),
            networks=networks, 
            iperf_results=iperf_results
        )
        self.survey_points.append(survey_point)
        
        # Agregar visualización
        point_widget = SurveyPointWidget(survey_point)
        self.scene.addItem(point_widget)
        
        self.update_stats()
        self.log(f"📍 Punto {len(self.survey_points)} medido")
    
    def estimate_aps(self):
        """Estimar posiciones de APs - CORREGIDO"""
        if not self.survey_points:
            QMessageBox.warning(self, "Sin Datos", "Se necesitan puntos de survey")
            return
        
        if not self.pixels_per_meter:
            QMessageBox.warning(self, "Sin Calibración", "Primero calibre la escala")
            return
        
        try:
            # CORREGIR: Configurar correctamente el localizador de APs
            self.ap_locator = APLocator(pixels_per_meter=self.pixels_per_meter)
            
            # Estimar posiciones
            estimated_aps = self.ap_locator.estimate_all_aps(self.survey_points)
            self.ap_positions = estimated_aps
            
            # Limpiar APs anteriores del mapa
            for item in self.scene.items():
                if isinstance(item, APWidget):
                    self.scene.removeItem(item)
            
            # Visualizar APs estimados
            for bssid, ap_data in estimated_aps.items():
                try:
                    ap_widget = APWidget(ap_data)
                    self.scene.addItem(ap_widget)
                except Exception as e:
                    print(f"Error agregando AP widget: {e}")
            
            self.update_stats()
            self.log(f"📡 {len(estimated_aps)} APs estimados")
            
            # Mostrar resumen
            if estimated_aps:
                summary = "APs Localizados:\n\n"
                for bssid, ap in estimated_aps.items():
                    confidence = getattr(ap, 'confidence', 0)
                    summary += f"• {ap.ssid}\n  Confianza: {confidence:.1%}\n\n"
                
                msg = QMessageBox(self)
                msg.setWindowTitle("APs Estimados")
                msg.setText(f"Se estimaron {len(estimated_aps)} posiciones de APs")
                msg.setDetailedText(summary)
                msg.exec()
            else:
                QMessageBox.warning(self, "Sin Resultados", 
                                   "No se pudieron estimar posiciones de APs.\n"
                                   "Verifique que tenga suficientes mediciones.")
                
        except Exception as e:
            self.log(f"❌ Error estimando APs: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error al estimar APs:\n{str(e)}")
    
    def show_heatmap_dialog(self):
        """Mostrar diálogo para generar heatmap"""
        if len(self.survey_points) < 3:
            QMessageBox.warning(self, "Sin Datos", "Se necesitan al menos 3 puntos")
            return
        
        # Obtener lista de SSIDs únicos
        all_ssids = set()
        for point in self.survey_points:
            for network in point.networks:
                all_ssids.add(network.ssid)
        
        sorted_ssids = sorted(list(all_ssids))
        
        dialog = HeatmapDialog(sorted_ssids, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            options = dialog.get_selected_options()
            self.generate_heatmap_with_options(options)
    
    def generate_heatmap_with_options(self, options: dict):
        """Generar heatmap con opciones específicas"""
        try:
            # Obtener dimensiones del plano
            pixmap_items = [item for item in self.scene.items() if isinstance(item, QGraphicsPixmapItem)]
            if not pixmap_items:
                QMessageBox.warning(self, "Sin Plano", "No hay plano cargado")
                return
            
            floor_plan = pixmap_items[0].pixmap()
            width, height = floor_plan.width(), floor_plan.height()
            
            # Buscar BSSID del SSID seleccionado si aplica
            target_bssid = None
            if options['target_ssid']:
                for point in self.survey_points:
                    for network in point.networks:
                        if network.ssid == options['target_ssid']:
                            target_bssid = network.bssid
                            break
                    if target_bssid:
                        break
            
            # Generar heatmap
            from PIL import Image as PILImage
            heatmap_pil = self.heatmap_gen.generate(
                self.survey_points, 
                width, 
                height, 
                target_bssid=target_bssid,
                metric=options['metric']
            )
            
            # Convertir a QPixmap
            image_data = heatmap_pil.tobytes("raw", "RGBA")
            qimage = QImage(image_data, width, height, QImage.Format.Format_RGBA8888)
            heatmap_pixmap = QPixmap.fromImage(qimage)
            
            # Remover heatmaps y leyendas anteriores
            items_to_remove = []
            for item in self.scene.items():
                if item.zValue() == 1 or isinstance(item, HeatmapLegend):
                    items_to_remove.append(item)
            
            for item in items_to_remove:
                self.scene.removeItem(item)
            
            if self.current_heatmap_legend:
                try:
                    self.scene.removeItem(self.current_heatmap_legend)
                except:
                    pass
            
            # Agregar nuevo heatmap
            heatmap_item = self.scene.addPixmap(heatmap_pixmap)
            heatmap_item.setZValue(1)
            
            # Agregar leyenda
            legend = HeatmapLegend(options['metric'])
            self.scene.addWidget(legend)
            legend.setPos(20, 20)  # Posición fija en la esquina
            legend.setZValue(2)
            self.current_heatmap_legend = legend
            
            self.update_stats()
            self.log(f"🗺 Heatmap generado: {options['description']}")
            
            # Actualizar información del plano
            if options['target_ssid']:
                self.floor_plan_info.setText(f"🗺 Heatmap: {options['target_ssid']} ({options['metric']})")
            else:
                self.floor_plan_info.setText(f"🗺 Heatmap: Todas las redes ({options['metric']})")
            
        except Exception as e:
            self.log(f"❌ Error generando heatmap: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error generando heatmap:\n{str(e)}")
    
    def generate_heatmap(self):
        """Generar heatmap básico (para compatibilidad)"""
        self.show_heatmap_dialog()
    
    def generate_report(self):
        """Generar reporte PDF con datos de servicios"""
        if not self.survey_points:
            QMessageBox.warning(self, "Sin Datos", "No hay datos para el reporte")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Guardar Reporte", "", "PDF (*.pdf)"
        )
        
        if file_path:
            # Preparar información del proyecto
            self.project_info.client_name = self.client_entry.text()
            self.project_info.name = self.site_entry.text()
            self.project_info.location = self.site_entry.text()
            
            # Recopilar estadísticas de servicios
            service_stats = []
            for service_widget in self.service_widgets.values():
                stats = service_widget.get_statistics()
                service_stats.append(stats)
            
            # Generar reporte
            generator = ReportGenerator()
            success_path = generator.generate_report(
                survey_points=self.survey_points,
                networks=self.current_networks,
                project_info=self.project_info.__dict__,
                service_stats=service_stats,  # Agregar estadísticas de servicios
                output_path=file_path
            )
            
            if success_path:
                QMessageBox.information(self, "Reporte", "Reporte generado exitosamente")
                self.log(f"📄 Reporte generado: {os.path.basename(file_path)}")
                
                # Preguntar si abrir el archivo
                reply = QMessageBox.question(
                    self, "Abrir Reporte", 
                    "¿Desea abrir el reporte generado?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    import subprocess
                    import platform
                    
                    try:
                        if platform.system() == 'Windows':
                            subprocess.run(['start', file_path], shell=True)
                        elif platform.system() == 'Darwin':  # macOS
                            subprocess.run(['open', file_path])
                        else:  # Linux
                            subprocess.run(['xdg-open', file_path])
                    except Exception as e:
                        self.log(f"No se pudo abrir el reporte: {e}")
            else:
                QMessageBox.critical(self, "Error", "Error generando reporte")
    
    def save_survey(self):
        """Guardar survey"""
        if not self.survey_points:
            QMessageBox.warning(self, "Sin Datos", "No hay datos para guardar")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Guardar Survey", "", "JSON (*.json)"
        )
        
        if file_path:
            data = {
                'project': {
                    'client_name': self.client_entry.text(),
                    'site_name': self.site_entry.text(),
                    'technician_name': self.technician_entry.text(),
                    'floor_plan_path': self.floor_plan_path,
                    'pixels_per_meter': self.pixels_per_meter
                },
                'survey_points': [p.to_dict() for p in self.survey_points],
                'ap_positions': {k: v.__dict__ for k, v in self.ap_positions.items()},
                'timestamp': datetime.now().isoformat()
            }
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.log(f"💾 Survey guardado: {os.path.basename(file_path)}")
    
    def load_survey(self):
        """Cargar survey"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Cargar Survey", "", "JSON (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                # Cargar información del proyecto
                project = data.get('project', {})
                self.client_entry.setText(project.get('client_name', ''))
                self.site_entry.setText(project.get('site_name', ''))
                self.technician_entry.setText(project.get('technician_name', ''))
                self.pixels_per_meter = project.get('pixels_per_meter')
                
                if self.pixels_per_meter:
                    self.calibration_label.setText(f"{self.pixels_per_meter:.2f} px/m")
                    self.calibration_label.setStyleSheet("color: #4CAF50;")
                    self.ap_locator.pixels_per_meter = self.pixels_per_meter
                
                # Limpiar puntos existentes
                self.survey_points = []
                
                # Cargar puntos de survey
                for point_data in data.get('survey_points', []):
                    try:
                        # Reconstruir punto
                        x = point_data['x']
                        y = point_data['y']
                        timestamp = datetime.fromisoformat(point_data['timestamp'])
                        
                        networks = []
                        for net_data in point_data.get('networks', []):
                            network = NetworkData(
                                ssid=net_data['ssid'],
                                bssid=net_data['bssid'],
                                signal=net_data['signal'],
                                frequency=net_data['frequency'],
                                channel=net_data['channel'],
                                security=net_data['security']
                            )
                            networks.append(network)
                        
                        iperf_results = None
                        if point_data.get('iperf_results'):
                            iperf_results = IperfResults()
                            iperf_data = point_data['iperf_results']
                            iperf_results.download_speed = iperf_data.get('download_speed', 0)
                            iperf_results.upload_speed = iperf_data.get('upload_speed', 0)
                            iperf_results.latency = iperf_data.get('latency', 0)
                            iperf_results.jitter = iperf_data.get('jitter', 0)
                        
                        survey_point = SurveyPoint(
                            x=x, 
                            y=y, 
                            timestamp=timestamp,
                            networks=networks, 
                            iperf_results=iperf_results
                        )
                        self.survey_points.append(survey_point)
                        
                        # Visualizar
                        point_widget = SurveyPointWidget(survey_point)
                        self.scene.addItem(point_widget)
                    except Exception as e:
                        print(f"Error cargando punto: {e}")
                        continue
                
                self.update_stats()
                self.log(f"📈 Survey cargado: {os.path.basename(file_path)}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error cargando archivo: {str(e)}")
    
    def clear_heatmap(self):
        """Limpiar heatmap"""
        items_to_remove = []
        for item in self.scene.items():
            if item.zValue() == 1 or isinstance(item, HeatmapLegend):
                items_to_remove.append(item)
        
        for item in items_to_remove:
            self.scene.removeItem(item)
        
        if self.current_heatmap_legend:
            self.current_heatmap_legend = None
        
        # Restaurar información del plano
        if self.floor_plan_path:
            filename = os.path.basename(self.floor_plan_path)
            self.floor_plan_info.setText(f"📂 {filename}")
        
        self.update_stats()
        self.log("🗑 Heatmap limpiado")
    
    def clear_log(self):
        """Limpiar log"""
        self.log_widget.clear()
    
    def zoom_in(self):
        self.graphics_view.scale(1.25, 1.25)
    
    def zoom_out(self):
        self.graphics_view.scale(0.8, 0.8)
    
    def fit_in_view(self):
        self.graphics_view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
    
    def closeEvent(self, event):
        """Al cerrar la aplicación"""
        # Detener servicios de monitoreo
        for service_widget in self.service_widgets.values():
            service_widget.stop_monitoring()
        
        self.scanner.stop_iperf_server()
        
        if self.survey_points:
            reply = QMessageBox.question(
                self, "Guardar",
                "¿Desea guardar los datos antes de cerrar?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
            elif reply == QMessageBox.StandardButton.Yes:
                self.save_survey()
        
        event.accept()