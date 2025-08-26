#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🗃️ DATA MODELS - Site Surveyor Pro v16.0
Modelos de datos completos y corregidos
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any

@dataclass
class NetworkData:
    """Información de una red WiFi detectada"""
    ssid: str
    bssid: str
    signal: int            # RSSI en dBm
    frequency: int         # MHz
    channel: int
    security: str
    vendor: str = "Unknown"
    quality: int = 0       # 0-100%
    noise: int = -96       # dBm
    snr: float = 0.0       # Signal-to-Noise Ratio
    bandwidth: str = "20MHz"
    
    def __post_init__(self):
        # Calcular SNR si no está definido
        if self.snr == 0.0:
            self.snr = max(0, self.signal - self.noise)
        
        # Calcular calidad si no está definida
        if self.quality == 0:
            self.quality = max(0, min(100, (self.signal + 100) * 2))
    
    @property
    def band(self) -> str:
        """Determina la banda (2.4GHz o 5GHz)"""
        return "5GHz" if self.frequency > 5000 else "2.4GHz"
    
    @property
    def signal_strength(self) -> int:
        """Alias para signal (compatibilidad)"""
        return self.signal
    
    @property
    def signal_quality(self) -> int:
        """Alias para quality (compatibilidad)"""
        return self.quality
        
    @property
    def noise_floor(self) -> int:
        """Alias para noise (compatibilidad)"""
        return self.noise

class IperfResults:
    """Resultados de pruebas iPerf"""
    def __init__(self):
        self.download_speed = 0.0
        self.upload_speed = 0.0  
        self.latency = 0.0
        self.jitter = 0.0
        self.packet_loss = 0.0
        self.timestamp = None
        self.server_info = ""
        self.error_message = ""
    
    # Propiedades para compatibilidad con el código existente
    @property
    def download_mbps(self):
        """Alias para download_speed"""
        return self.download_speed

    @property
    def upload_mbps(self):
        """Alias para upload_speed"""
        return self.upload_speed

    @property  
    def ping_ms(self):
        """Alias para latency"""
        return self.latency
    
    @property
    def jitter_ms(self):
        """Alias para jitter"""
        return self.jitter
    
    def to_dict(self) -> dict:
        return {
            'download_speed': self.download_speed,
            'upload_speed': self.upload_speed,
            'latency': self.latency,
            'jitter': self.jitter,
            'packet_loss': self.packet_loss,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'server_info': self.server_info,
            'error_message': self.error_message
        }

@dataclass
class SurveyPoint:
    """Punto de medición en el site survey"""
    x: float
    y: float
    timestamp: datetime
    networks: List[NetworkData]
    iperf_results: Optional[IperfResults] = None
    notes: str = ""
    point_id: str = ""
    
    # Métricas calculadas
    avg_signal_strength: float = 0.0
    max_signal_strength: float = 0.0
    network_count: int = 0
    avg_snr: float = 0.0
    
    def __post_init__(self):
        if not self.point_id:
            self.point_id = f"point_{datetime.now().strftime('%H%M%S_%f')}"
        
        self.calculate_metrics()
    
    def calculate_metrics(self):
        """Calcula métricas del punto basadas en las redes detectadas"""
        if not self.networks:
            return
        
        self.network_count = len(self.networks)
        
        signals = [net.signal for net in self.networks]
        snr_values = [net.snr for net in self.networks if net.snr > 0]
        
        if signals:
            self.avg_signal_strength = sum(signals) / len(signals)
            self.max_signal_strength = max(signals)
        
        if snr_values:
            self.avg_snr = sum(snr_values) / len(snr_values)
    
    def get_network_by_ssid(self, ssid: str) -> Optional[NetworkData]:
        """Obtiene una red específica por SSID"""
        for network in self.networks:
            if network.ssid == ssid:
                return network
        return None
    
    def to_dict(self) -> dict:
        return {
            'x': self.x,
            'y': self.y,
            'timestamp': self.timestamp.isoformat(),
            'networks': [self._network_to_dict(net) for net in self.networks],
            'iperf_results': self.iperf_results.to_dict() if self.iperf_results else None,
            'notes': self.notes,
            'point_id': self.point_id,
            'avg_signal_strength': self.avg_signal_strength,
            'max_signal_strength': self.max_signal_strength,
            'network_count': self.network_count,
            'avg_snr': self.avg_snr
        }
    
    def _network_to_dict(self, network: NetworkData) -> dict:
        """Convierte NetworkData a diccionario"""
        return {
            'ssid': network.ssid,
            'bssid': network.bssid,
            'signal': network.signal,
            'frequency': network.frequency,
            'channel': network.channel,
            'security': network.security,
            'vendor': network.vendor,
            'quality': network.quality,
            'noise': network.noise,
            'snr': network.snr,
            'bandwidth': network.bandwidth
        }

@dataclass
class AccessPoint:
    """Información de un Access Point"""
    bssid: str
    ssid: str
    estimated_x: float = 0.0
    estimated_y: float = 0.0
    confidence: float = 0.0
    channel: int = 0
    vendor: str = "Unknown"
    frequency: int = 0
    security: str = "Unknown"
    max_signal: int = -100
    detection_points: List[str] = None
    
    def __post_init__(self):
        if self.detection_points is None:
            self.detection_points = []

@dataclass
class ProjectInfo:
    """Información del proyecto de site survey"""
    name: str = "Nuevo Proyecto"
    client_name: str = ""
    location: str = ""
    date_created: datetime = None
    date_modified: datetime = None
    description: str = ""
    floor_plan_path: str = ""
    scale_meters_per_pixel: float = 1.0
    survey_points: List[SurveyPoint] = None
    access_points: List[AccessPoint] = None
    calibration_points: List[tuple] = None
    
    def __post_init__(self):
        if self.date_created is None:
            self.date_created = datetime.now()
        if self.date_modified is None:
            self.date_modified = datetime.now()
        if self.survey_points is None:
            self.survey_points = []
        if self.access_points is None:
            self.access_points = []
        if self.calibration_points is None:
            self.calibration_points = []

@dataclass
class ServiceMonitorData:
    """Datos de monitoreo de servicios"""
    service_name: str
    latency: float
    status: str
    timestamp: datetime
    response_time: float = 0.0
    packet_loss: float = 0.0
    
    def to_dict(self) -> dict:
        return {
            'service_name': self.service_name,
            'latency': self.latency,
            'status': self.status,
            'timestamp': self.timestamp.isoformat(),
            'response_time': self.response_time,
            'packet_loss': self.packet_loss
        }

@dataclass
class APPosition:
    """Posición de un Access Point (alias para AccessPoint)"""
    bssid: str
    ssid: str
    x: float = 0.0
    y: float = 0.0
    confidence: float = 0.0
    
    def __post_init__(self):
        # Mantener compatibilidad con AccessPoint
        self.estimated_x = self.x
        self.estimated_y = self.y