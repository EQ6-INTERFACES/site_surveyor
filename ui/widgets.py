#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎨 WIDGETS - Site Surveyor Pro v16.0
Widgets personalizados COMPLETOS Y FUNCIONALES
"""

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from datetime import datetime
from typing import Optional
import math
import subprocess
import threading
import os
import re

class SurveyPointWidget(QGraphicsEllipseItem):
    """Widget que representa un punto de survey con tooltip funcional"""
    
    def __init__(self, survey_point, parent=None):
        super().__init__(parent)
        self.survey_point = survey_point
        self.setRect(-6, -6, 12, 12)  # Círculo de 12px de diámetro
        
        # Estilo visual del punto
        self.setBrush(QBrush(QColor(76, 175, 80)))  # Verde
        self.setPen(QPen(QColor(255, 255, 255), 2))  # Borde blanco
        
        # Configurar como interactivo
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setAcceptHoverEvents(True)
        
        # Tooltip mejorado
        self.setToolTip(self._create_tooltip())
        
        # Posicionar en coordenadas del punto
        self.setPos(survey_point.x, survey_point.y)
    
    def _create_tooltip(self) -> str:
        """Crea tooltip con información detallada del punto"""
        sp = self.survey_point
        
        # Información básica
        tooltip = f"Punto de Medición #{sp.point_id}\n"
        tooltip += f"Posición: ({int(sp.x)}, {int(sp.y)})\n"
        tooltip += f"Timestamp: {sp.timestamp.strftime('%H:%M:%S')}\n"
        tooltip += f"Redes detectadas: {len(sp.networks)}\n\n"
        
        # Métricas WiFi
        if sp.networks:
            tooltip += f"RSSI Promedio: {sp.avg_signal_strength:.1f} dBm\n"
            tooltip += f"RSSI Máximo: {sp.max_signal_strength:.1f} dBm\n"
            tooltip += f"SNR Promedio: {sp.avg_snr:.1f} dB\n\n"
            
            # Red principal (mejor señal)
            best_net = max(sp.networks, key=lambda n: n.signal)
            tooltip += f"Red Principal: {best_net.ssid}\n"
            tooltip += f"  • RSSI: {best_net.signal} dBm\n"
            tooltip += f"  • Canal: {best_net.channel}\n"
            tooltip += f"  • Seguridad: {best_net.security}\n\n"
        
        # Datos iPerf si existen
        if sp.iperf_results:
            tooltip += "Pruebas de Rendimiento:\n"
            tooltip += f"Download: {sp.iperf_results.download_speed:.1f} Mbps\n"
            tooltip += f"Upload: {sp.iperf_results.upload_speed:.1f} Mbps\n"
            tooltip += f"Latencia: {sp.iperf_results.latency:.1f} ms\n"
            tooltip += f"Jitter: {sp.iperf_results.jitter:.1f} ms\n"
        
        return tooltip
    
    def hoverEnterEvent(self, event):
        """Al entrar el mouse sobre el punto"""
        super().hoverEnterEvent(event)
        self.setRect(-8, -8, 16, 16)
        self.setBrush(QBrush(QColor(100, 200, 100)))
    
    def hoverLeaveEvent(self, event):
        """Al salir el mouse del punto"""
        super().hoverLeaveEvent(event)
        self.setRect(-6, -6, 12, 12)
        self.setBrush(QBrush(QColor(76, 175, 80)))

class APWidget(QGraphicsEllipseItem):
    """Widget que representa un Access Point en el mapa"""
    
    def __init__(self, ap_data, parent=None):
        super().__init__(parent)
        self.ap_data = ap_data
        self.setRect(-8, -8, 16, 16)
        
        # Estilo visual del AP
        self.setBrush(QBrush(QColor(255, 165, 0)))  # Naranja
        self.setPen(QPen(QColor(255, 255, 255), 2))
        
        # Configurar como interactivo
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setAcceptHoverEvents(True)
        
        # Tooltip para el AP
        tooltip = f"Access Point: {ap_data.ssid}\nBSSID: {ap_data.bssid}\nConfianza: {ap_data.confidence:.1f}"
        self.setToolTip(tooltip)
        
        # Posicionar en coordenadas del AP
        self.setPos(ap_data.estimated_x, ap_data.estimated_y)
    
    def hoverEnterEvent(self, event):
        super().hoverEnterEvent(event)
        self.setBrush(QBrush(QColor(255, 200, 100)))
    
    def hoverLeaveEvent(self, event):
        super().hoverLeaveEvent(event)
        self.setBrush(QBrush(QColor(255, 165, 0)))

class MiniChart(QWidget):
    """Widget de mini gráfica para mostrar métricas en tiempo real"""
    
    def __init__(self, service_name: str, max_points: int = 30, parent=None):
        super().__init__(parent)
        self.service_name = service_name
        self.max_points = max_points
        self.data_points = []
        self.max_value = 100.0
        self.min_value = 0.0
        
        self.setFixedSize(100, 40)
        self.setStyleSheet("""
            MiniChart {
                background: #1e1e1e;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
            }
        """)
        
        # Inicializar con algunos puntos
        for _ in range(5):
            self.data_points.append(0)
    
    def add_data_point(self, value: float):
        """Agrega un nuevo punto de datos"""
        self.data_points.append(value)
        
        if len(self.data_points) > self.max_points:
            self.data_points.pop(0)
        
        if self.data_points:
            self.max_value = max(max(self.data_points) * 1.1, 1)
            self.min_value = min(min(self.data_points), 0)
        
        self.update()
    
    def paintEvent(self, event):
        """Dibuja la mini gráfica"""
        if len(self.data_points) < 2:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        painter.fillRect(self.rect(), QColor(30, 30, 30))
        
        width = self.width() - 10
        height = self.height() - 10
        
        points = []
        
        for i, value in enumerate(self.data_points):
            if self.max_value > self.min_value:
                normalized = (value - self.min_value) / (self.max_value - self.min_value)
            else:
                normalized = 0.5
                
            x = 5 + (i / (len(self.data_points) - 1)) * width
            y = height + 5 - (normalized * height)
            points.append(QPointF(x, y))
        
        if len(points) >= 2:
            last_value = self.data_points[-1]
            if last_value < 30:
                color = QColor(76, 175, 80)
            elif last_value < 100:
                color = QColor(255, 193, 7)
            else:
                color = QColor(244, 67, 54)
            
            pen = QPen(color, 2)
            painter.setPen(pen)
            
            for i in range(len(points) - 1):
                painter.drawLine(points[i], points[i + 1])
            
            painter.setBrush(QBrush(color))
            painter.drawEllipse(points[-1], 3, 3)

class ServiceMonitor(QWidget):
    """Widget para monitoreo de servicios con mini gráficas"""
    
    def __init__(self, service_name: str, service_url: str, color: str, parent=None):
        super().__init__(parent)
        self.service_name = service_name
        self.service_url = service_url
        self.color = color
        self.current_latency = 0
        self.is_monitoring = False
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz del widget"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)
        
        # Nombre del servicio
        name_label = QLabel(self.service_name)
        name_label.setStyleSheet("color: white; font-weight: bold; font-size: 11px;")
        name_label.setFixedWidth(100)
        
        # URL del servicio
        url_label = QLabel(self.service_url)
        url_label.setStyleSheet("color: #888; font-size: 10px;")
        url_label.setFixedWidth(120)
        
        # Mini gráfica
        self.mini_chart = MiniChart(self.service_name)
        
        # Latencia actual
        self.latency_label = QLabel("-- ms")
        self.latency_label.setStyleSheet(f"color: {self.color}; font-weight: bold; font-size: 11px;")
        self.latency_label.setFixedWidth(50)
        self.latency_label.setAlignment(Qt.AlignCenter)
        
        # Botón de ping
        ping_btn = QPushButton("📡")
        ping_btn.setFixedSize(24, 24)
        ping_btn.setStyleSheet(f"""
            QPushButton {{
                background: {self.color};
                border: none;
                border-radius: 4px;
                font-size: 10px;
            }}
            QPushButton:hover {{
                background: {self.color}dd;
            }}
        """)
        ping_btn.clicked.connect(self.manual_ping)
        
        layout.addWidget(name_label)
        layout.addWidget(url_label)
        layout.addWidget(self.mini_chart)
        layout.addWidget(self.latency_label)
        layout.addWidget(ping_btn)
        layout.addStretch()
        
        self.setStyleSheet("""
            ServiceMonitor {
                background: #2b2b2b;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                margin: 2px;
            }
            ServiceMonitor:hover {
                border: 1px solid #0d7377;
            }
        """)
        
        self.setFixedHeight(50)
    
    def update_latency(self, latency_ms: float):
        """Actualiza la latencia mostrada"""
        self.current_latency = latency_ms
        self.latency_label.setText(f"{latency_ms:.0f} ms")
        
        self.mini_chart.add_data_point(latency_ms)
        
        if latency_ms < 30:
            color = "#4CAF50"
        elif latency_ms < 100:
            color = "#FFC107"
        else:
            color = "#F44336"
            
        self.latency_label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 11px;")
    
    def manual_ping(self):
        """Ejecuta ping manual"""
        def ping_worker():
            try:
                if os.name == 'nt':
                    cmd = ['ping', '-n', '1', self.service_url]
                else:
                    cmd = ['ping', '-c', '1', self.service_url]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0:
                    if os.name == 'nt':
                        match = re.search(r'time[<=](\d+)ms', result.stdout)
                    else:
                        match = re.search(r'time=(\d+\.?\d*)', result.stdout)
                    
                    if match:
                        latency = float(match.group(1))
                        QTimer.singleShot(0, lambda: self.update_latency(latency))
                    else:
                        QTimer.singleShot(0, lambda: self.update_latency(999))
                else:
                    QTimer.singleShot(0, lambda: self.update_latency(999))
                    
            except Exception as e:
                print(f"Error en ping a {self.service_name}: {e}")
                QTimer.singleShot(0, lambda: self.update_latency(999))
        
        threading.Thread(target=ping_worker, daemon=True).start()
    def start_monitoring(self):
     """Inicia monitoreo automático"""
     self.is_monitoring = True

def stop_monitoring(self):
    """Detiene monitoreo automático"""  
    self.is_monitoring = False
    

class ZoomableGraphicsView(QGraphicsView):
    """Vista gráfica con capacidad de zoom"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.zoom_factor = 1.15
    
    def wheelEvent(self, event):
        """Maneja el zoom con la rueda del mouse"""
        if event.angleDelta().y() > 0:
            self.scale(self.zoom_factor, self.zoom_factor)
        else:
            self.scale(1/self.zoom_factor, 1/self.zoom_factor)