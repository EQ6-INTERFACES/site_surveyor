#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎨 WIDGETS - Site Surveyor Pro v16.0
Widgets personalizados CON TOOLTIPS CORREGIDOS y SERVICIOS FUNCIONANDO
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
    """Widget que representa un punto de survey con tooltip CORREGIDO"""
    
    def __init__(self, survey_point, parent=None):
        super().__init__(parent)
        self.survey_point = survey_point
        self.setRect(-8, -8, 16, 16)  # Círculo más grande para mejor visibilidad
        
        # Estilo visual del punto
        self.setBrush(QBrush(QColor(76, 175, 80, 200)))  # Verde con transparencia
        self.setPen(QPen(QColor(255, 255, 255), 3))  # Borde blanco más grueso
        
        # CORREGIR: Configurar flags correctos para tooltips
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, True)
        self.setAcceptHoverEvents(True)
        
        # Posicionar en coordenadas del punto
        self.setPos(survey_point.x, survey_point.y)
        
        # Z-Value alto para que aparezca encima
        self.setZValue(10)
    
    def _create_tooltip(self) -> str:
        """Crea tooltip con información detallada del punto"""
        sp = self.survey_point
        
        # Información básica
        tooltip = f"🎯 Punto de Medición #{getattr(sp, 'point_id', 'N/A')}\n"
        tooltip += f"📍 Posición: ({int(sp.x)}, {int(sp.y)})\n"
        tooltip += f"⏰ Timestamp: {sp.timestamp.strftime('%H:%M:%S')}\n"
        tooltip += f"📡 Redes detectadas: {len(sp.networks)}\n"
        tooltip += "─" * 30 + "\n"
        
        # Métricas WiFi
        if sp.networks:
            signals = [net.signal for net in sp.networks if hasattr(net, 'signal')]
            if signals:
                avg_signal = sum(signals) / len(signals)
                max_signal = max(signals)
                tooltip += f"📶 RSSI Promedio: {avg_signal:.1f} dBm\n"
                tooltip += f"📶 RSSI Máximo: {max_signal:.1f} dBm\n"
            
            # Red principal (mejor señal)
            best_net = max(sp.networks, key=lambda n: getattr(n, 'signal', -100))
            tooltip += f"\n🏆 Red Principal:\n"
            tooltip += f"   SSID: {best_net.ssid}\n"
            tooltip += f"   RSSI: {best_net.signal} dBm\n"
            tooltip += f"   Canal: {best_net.channel}\n"
            tooltip += f"   Seguridad: {best_net.security}\n"
        
        # Datos iPerf si existen
        if hasattr(sp, 'iperf_results') and sp.iperf_results:
            tooltip += "\n🚀 Pruebas de Rendimiento:\n"
            tooltip += f"   ⬇️ Download: {sp.iperf_results.download_speed:.1f} Mbps\n"
            tooltip += f"   ⬆️ Upload: {sp.iperf_results.upload_speed:.1f} Mbps\n"
            tooltip += f"   📊 Latencia: {sp.iperf_results.latency:.1f} ms\n"
            if hasattr(sp.iperf_results, 'jitter'):
                tooltip += f"   📈 Jitter: {sp.iperf_results.jitter:.1f} ms\n"
        
        return tooltip
    
    def hoverEnterEvent(self, event):
        """Al entrar el mouse sobre el punto - MEJORADO"""
        super().hoverEnterEvent(event)
        # Crear y mostrar tooltip actualizado
        tooltip_text = self._create_tooltip()
        self.setToolTip(tooltip_text)
        
        # Efecto visual al hover
        self.setRect(-10, -10, 20, 20)
        self.setBrush(QBrush(QColor(100, 200, 100, 220)))
        self.setPen(QPen(QColor(255, 255, 0), 4))  # Borde amarillo brillante
    
    def hoverLeaveEvent(self, event):
        """Al salir el mouse del punto"""
        super().hoverLeaveEvent(event)
        self.setRect(-8, -8, 16, 16)
        self.setBrush(QBrush(QColor(76, 175, 80, 200)))
        self.setPen(QPen(QColor(255, 255, 255), 3))

class APWidget(QGraphicsEllipseItem):
    """Widget que representa un Access Point en el mapa - MEJORADO"""
    
    def __init__(self, ap_data, parent=None):
        super().__init__(parent)
        self.ap_data = ap_data
        self.setRect(-10, -10, 20, 20)  # Más grande que los puntos de survey
        
        # Estilo visual del AP - Forma de diamante
        self.setBrush(QBrush(QColor(255, 165, 0, 180)))  # Naranja con transparencia
        self.setPen(QPen(QColor(255, 255, 255), 3))
        
        # Configurar como interactivo
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setAcceptHoverEvents(True)
        
        # Z-Value alto para que aparezca encima
        self.setZValue(15)
        
        # Posicionar en coordenadas del AP
        if hasattr(ap_data, 'x') and hasattr(ap_data, 'y'):
            self.setPos(ap_data.x, ap_data.y)
        else:
            self.setPos(getattr(ap_data, 'estimated_x', 0), getattr(ap_data, 'estimated_y', 0))
    
    def hoverEnterEvent(self, event):
        super().hoverEnterEvent(event)
        # Crear tooltip dinámico
        confidence = getattr(self.ap_data, 'confidence', 0)
        measurement_count = getattr(self.ap_data, 'measurement_count', 0)
        
        tooltip = f"📡 Access Point\n"
        tooltip += f"SSID: {self.ap_data.ssid}\n"
        tooltip += f"BSSID: {self.ap_data.bssid}\n"
        tooltip += f"Confianza: {confidence:.1%}\n"
        tooltip += f"Mediciones: {measurement_count}\n"
        tooltip += f"Estado: {getattr(self.ap_data, 'status', 'Estimado')}"
        
        self.setToolTip(tooltip)
        self.setBrush(QBrush(QColor(255, 200, 100, 220)))
        self.setRect(-12, -12, 24, 24)
    
    def hoverLeaveEvent(self, event):
        super().hoverLeaveEvent(event)
        self.setBrush(QBrush(QColor(255, 165, 0, 180)))
        self.setRect(-10, -10, 20, 20)

class ServiceMonitor(QWidget):
    """Widget para monitoreo de servicios CON FUNCIONAMIENTO COMPLETO"""
    
    def __init__(self, service_name: str, service_url: str, color: str, parent=None):
        super().__init__(parent)
        self.service_name = service_name
        self.service_url = service_url
        self.color = color
        self.current_latency = 0
        self.packet_loss = 0
        self.is_monitoring = False
        self.ping_history = []  # Historial para estadísticas
        
        # Timer automático para monitoreo
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self.auto_ping)
        self.monitor_timer.setInterval(5000)  # Ping cada 5 segundos
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz del widget"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)
        
        # Indicador de estado
        self.status_indicator = QLabel("⚫")
        self.status_indicator.setStyleSheet("color: #666; font-size: 14px;")
        self.status_indicator.setFixedWidth(20)
        
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
        self.latency_label.setFixedWidth(60)
        self.latency_label.setAlignment(Qt.AlignCenter)
        
        # Estadísticas adicionales
        self.stats_label = QLabel("0% loss")
        self.stats_label.setStyleSheet("color: #ccc; font-size: 9px;")
        self.stats_label.setFixedWidth(50)
        
        # Botón de ping manual
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
        ping_btn.setToolTip("Ping manual")
        
        layout.addWidget(self.status_indicator)
        layout.addWidget(name_label)
        layout.addWidget(url_label)
        layout.addWidget(self.mini_chart)
        layout.addWidget(self.latency_label)
        layout.addWidget(self.stats_label)
        layout.addWidget(ping_btn)
        layout.addStretch()
        
        self.setStyleSheet("""
            ServiceMonitor {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2b2d31, stop:1 #1e1f22);
                border: 2px solid #43464d;
                border-radius: 8px;
                margin: 2px;
            }
            ServiceMonitor:hover {
                border: 2px solid #5865f2;
            }
        """)
        
        self.setFixedHeight(55)
    
    def update_latency(self, latency_ms: float, success: bool = True):
        """Actualiza la latencia mostrada y estadísticas"""
        self.current_latency = latency_ms
        self.ping_history.append({'latency': latency_ms, 'success': success, 'timestamp': datetime.now()})
        
        # Mantener solo últimos 20 pings para estadísticas
        if len(self.ping_history) > 20:
            self.ping_history.pop(0)
        
        # Calcular pérdida de paquetes
        if self.ping_history:
            failed_pings = sum(1 for p in self.ping_history if not p['success'])
            self.packet_loss = (failed_pings / len(self.ping_history)) * 100
        
        # Actualizar UI
        if not success or latency_ms >= 999:
            self.latency_label.setText("FAIL")
            self.status_indicator.setText("🔴")
            color = "#F44336"
        else:
            self.latency_label.setText(f"{latency_ms:.0f} ms")
            if latency_ms < 30:
                color = "#4CAF50"
                self.status_indicator.setText("🟢")
            elif latency_ms < 100:
                color = "#FFC107"
                self.status_indicator.setText("🟡")
            else:
                color = "#F44336"
                self.status_indicator.setText("🟠")
        
        # Actualizar estadísticas
        self.stats_label.setText(f"{self.packet_loss:.0f}% loss")
        
        self.mini_chart.add_data_point(latency_ms if success else 200)
        self.latency_label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 11px;")
    
    def manual_ping(self):
        """Ejecuta ping manual"""
        self.execute_ping()
    
    def auto_ping(self):
        """Ejecuta ping automático (llamado por timer)"""
        if self.is_monitoring:
            self.execute_ping()
    
    def execute_ping(self):
        """Ejecuta el ping real en thread separado - MEJORADO"""
        def ping_worker():
            try:
                # Normalizar URL (remover protocolos)
                target = self.service_url.replace('https://', '').replace('http://', '').split('/')[0]
                
                if os.name == 'nt':
                    # Windows
                    cmd = ['ping', '-n', '1', '-w', '3000', target]
                else:
                    # Linux/Mac
                    cmd = ['ping', '-c', '1', '-W', '3', target]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0:
                    # Extraer latencia del resultado
                    latency = self.parse_ping_output(result.stdout)
                    if latency is not None:
                        QTimer.singleShot(0, lambda: self.update_latency(latency, True))
                    else:
                        QTimer.singleShot(0, lambda: self.update_latency(999, False))
                else:
                    QTimer.singleShot(0, lambda: self.update_latency(999, False))
                    
            except subprocess.TimeoutExpired:
                QTimer.singleShot(0, lambda: self.update_latency(999, False))
            except Exception as e:
                print(f"Error en ping a {self.service_name}: {e}")
                QTimer.singleShot(0, lambda: self.update_latency(999, False))
        
        threading.Thread(target=ping_worker, daemon=True).start()
    
    def parse_ping_output(self, output: str) -> Optional[float]:
        """Extrae latencia del output de ping - MEJORADO"""
        try:
            if os.name == 'nt':
                # Windows: buscar "tiempo=XXXms" o "time=XXXms"
                patterns = [
                    r'tiempo[<=](\d+)ms',
                    r'time[<=](\d+)ms',
                    r'tiempo=(\d+)ms',
                    r'time=(\d+)ms'
                ]
            else:
                # Linux/Mac: buscar "time=X.XXX ms"
                patterns = [
                    r'time=(\d+\.?\d*)\s*ms',
                    r'time=(\d+\.?\d*)',
                ]
            
            for pattern in patterns:
                match = re.search(pattern, output, re.IGNORECASE)
                if match:
                    return float(match.group(1))
            
            return None
        except Exception:
            return None
    
    def start_monitoring(self):
        """Inicia monitoreo automático"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_timer.start()
            print(f"🟢 Iniciando monitoreo de {self.service_name}")
            # Hacer primer ping inmediatamente
            self.execute_ping()

    def stop_monitoring(self):
        """Detiene monitoreo automático"""  
        if self.is_monitoring:
            self.is_monitoring = False
            self.monitor_timer.stop()
            self.status_indicator.setText("⚫")
            print(f"🛑 Deteniendo monitoreo de {self.service_name}")
    
    def toggle_monitoring(self):
        """Alterna entre iniciar y detener monitoreo"""
        if self.is_monitoring:
            self.stop_monitoring()
        else:
            self.start_monitoring()
    
    def get_statistics(self) -> dict:
        """Retorna estadísticas del servicio para el reporte"""
        if not self.ping_history:
            return {
                'service_name': self.service_name,
                'service_url': self.service_url,
                'current_latency': 0,
                'avg_latency': 0,
                'min_latency': 0,
                'max_latency': 0,
                'packet_loss': 0,
                'status': 'No data'
            }
        
        successful_pings = [p for p in self.ping_history if p['success']]
        
        if successful_pings:
            latencies = [p['latency'] for p in successful_pings]
            avg_latency = sum(latencies) / len(latencies)
            min_latency = min(latencies)
            max_latency = max(latencies)
        else:
            avg_latency = min_latency = max_latency = 0
        
        return {
            'service_name': self.service_name,
            'service_url': self.service_url,
            'current_latency': self.current_latency,
            'avg_latency': avg_latency,
            'min_latency': min_latency,
            'max_latency': max_latency,
            'packet_loss': self.packet_loss,
            'total_pings': len(self.ping_history),
            'successful_pings': len(successful_pings),
            'status': 'Active' if self.is_monitoring else 'Inactive'
        }

class MiniChart(QWidget):
    """Widget de mini gráfica mejorado"""
    
    def __init__(self, service_name: str, max_points: int = 30, parent=None):
        super().__init__(parent)
        self.service_name = service_name
        self.max_points = max_points
        self.data_points = []
        self.max_value = 100.0
        self.min_value = 0.0
        
        self.setFixedSize(120, 45)  # Más grande
        self.setStyleSheet("""
            MiniChart {
                background: #1a1a1a;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
            }
        """)
    
    def add_data_point(self, value: float):
        """Agrega un nuevo punto de datos"""
        self.data_points.append(value)
        
        if len(self.data_points) > self.max_points:
            self.data_points.pop(0)
        
        if self.data_points:
            self.max_value = max(max(self.data_points) * 1.1, 10)
            self.min_value = 0
        
        self.update()
    
    def paintEvent(self, event):
        """Dibuja la mini gráfica mejorada"""
        if len(self.data_points) < 2:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Fondo con gradiente
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(25, 25, 25))
        gradient.setColorAt(1, QColor(15, 15, 15))
        painter.fillRect(self.rect(), gradient)
        
        width = self.width() - 10
        height = self.height() - 10
        
        points = []
        
        # Calcular puntos de la gráfica
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
            
            # Color basado en el último valor
            if last_value < 30:
                color = QColor(76, 175, 80)  # Verde
                gradient_color = QColor(76, 175, 80, 50)
            elif last_value < 100:
                color = QColor(255, 193, 7)  # Amarillo
                gradient_color = QColor(255, 193, 7, 50)
            else:
                color = QColor(244, 67, 54)  # Rojo
                gradient_color = QColor(244, 67, 54, 50)
            
            # Dibujar área bajo la curva
            area_points = [QPointF(5, height + 5)] + points + [QPointF(width + 5, height + 5)]
            area_polygon = QPolygonF(area_points)
            painter.setBrush(QBrush(gradient_color))
            painter.setPen(QPen(Qt.PenStyle.NoPen))
            painter.drawPolygon(area_polygon)
            
            # Dibujar línea principal
            pen = QPen(color, 2)
            painter.setPen(pen)
            painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            
            for i in range(len(points) - 1):
                painter.drawLine(points[i], points[i + 1])
            
            # Dibujar punto final
            painter.setBrush(QBrush(color))
            painter.drawEllipse(points[-1], 4, 4)

class HeatmapLegend(QWidget):
    """Widget de leyenda para el heatmap"""
    
    def __init__(self, metric_type: str = "rssi", parent=None):
        super().__init__(parent)
        self.metric_type = metric_type
        self.setFixedSize(200, 60)
        self.setStyleSheet("""
            HeatmapLegend {
                background: rgba(30, 31, 34, 200);
                border: 2px solid #43464d;
                border-radius: 8px;
            }
        """)
    
    def paintEvent(self, event):
        """Dibuja la leyenda del heatmap"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Fondo semi-transparente
        painter.fillRect(self.rect(), QColor(30, 31, 34, 220))
        
        # Título
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        
        if self.metric_type == "rssi":
            painter.drawText(10, 20, "Señal WiFi (dBm)")
            labels = ["-90", "-70", "-50", "-30"]
            colors = [QColor(33, 150, 243), QColor(244, 67, 54), QColor(255, 193, 7), QColor(76, 175, 80)]
        elif self.metric_type == "speed":
            painter.drawText(10, 20, "Velocidad (Mbps)")
            labels = ["0", "25", "50", "100+"]
            colors = [QColor(244, 67, 54), QColor(255, 193, 7), QColor(76, 175, 80), QColor(33, 150, 243)]
        else:
            painter.drawText(10, 20, "Latencia (ms)")
            labels = ["0", "50", "100", "200+"]
            colors = [QColor(76, 175, 80), QColor(255, 193, 7), QColor(244, 67, 54), QColor(33, 150, 243)]
        
        # Dibujar barra de colores
        bar_width = 160
        bar_height = 15
        bar_x = 15
        bar_y = 30
        
        segment_width = bar_width / len(colors)
        
        for i, (label, color) in enumerate(zip(labels, colors)):
            # Segmento de color
            rect = QRect(bar_x + int(i * segment_width), bar_y, int(segment_width), bar_height)
            painter.fillRect(rect, color)
            
            # Etiqueta
            painter.setPen(QPen(QColor(255, 255, 255), 1))
            painter.setFont(QFont("Arial", 8))
            text_x = bar_x + int(i * segment_width) + int(segment_width/2) - 10
            painter.drawText(text_x, bar_y + bar_height + 12, label)

class ZoomableGraphicsView(QGraphicsView):
    """Vista gráfica con capacidad de zoom mejorada"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.zoom_factor = 1.15
        self.setMouseTracking(True)  # Para tooltips
        
        # Configurar para mejor rendimiento
        self.setOptimizationFlags(QGraphicsView.OptimizationFlag.DontAdjustForAntialiasing)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.SmartViewportUpdate)
    
    def wheelEvent(self, event):
        """Maneja el zoom con la rueda del mouse"""
        # Zoom centrado en el cursor
        old_pos = self.mapToScene(event.position().toPoint())
        
        if event.angleDelta().y() > 0:
            zoom_in_factor = self.zoom_factor
        else:
            zoom_in_factor = 1 / self.zoom_factor
        
        self.scale(zoom_in_factor, zoom_in_factor)
        
        # Mantener posición del cursor
        new_pos = self.mapToScene(event.position().toPoint())
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())