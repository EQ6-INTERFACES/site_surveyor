#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🗃️ DATA MODELS - Site Surveyor Pro v16.0
Modelos de datos completos y ULTRA-COMPATIBLES v3
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid

@dataclass
class NetworkData:
    """Información de una red WiFi detectada - MEJORADO"""
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
        
        # Asegurar que los valores estén en rangos válidos
        self.signal = max(-120, min(-10, self.signal))
        self.quality = max(0, min(100, self.quality))
        self.snr = max(0, min(60, self.snr))
    
    @property
    def band(self) -> str:
        """Determina la banda (2.4GHz o 5GHz)"""
        return "5GHz" if self.frequency > 5000 else "2.4GHz"
    
    # Aliases para compatibilidad total
    @property
    def signal_strength(self) -> int:
        return self.signal
    
    @property
    def signal_quality(self) -> int:
        return self.quality
        
    @property
    def noise_floor(self) -> int:
        return self.noise
    
    @property
    def rssi(self) -> int:
        """Alias principal para signal"""
        return self.signal
    
    def get_signal_category(self) -> str:
        """Retorna categoría de calidad de señal"""
        if self.signal >= -50:
            return "Excelente"
        elif self.signal >= -60:
            return "Muy buena"
        elif self.signal >= -70:
            return "Buena"
        elif self.signal >= -80:
            return "Regular"
        else:
            return "Pobre"
    
    def to_dict(self) -> dict:
        """Convierte a diccionario para serialización"""
        return {
            'ssid': self.ssid,
            'bssid': self.bssid,
            'signal': self.signal,
            'frequency': self.frequency,
            'channel': self.channel,
            'security': self.security,
            'vendor': self.vendor,
            'quality': self.quality,
            'noise': self.noise,
            'snr': self.snr,
            'bandwidth': self.bandwidth
        }

class IperfResults:
    """Resultados de pruebas iPerf - MEJORADO"""
    
    def __init__(self):
        self.download_speed = 0.0
        self.upload_speed = 0.0  
        self.latency = 0.0
        self.jitter = 0.0
        self.packet_loss = 0.0
        self.test_duration = 3
        self.timestamp = None
        self.server_info = ""
        self.error_message = ""
        self.test_status = "completed"  # completed, failed, timeout
    
    # Propiedades para compatibilidad absoluta
    @property
    def download_mbps(self) -> float:
        return self.download_speed

    @property
    def upload_mbps(self) -> float:
        return self.upload_speed

    @property  
    def ping_ms(self) -> float:
        return self.latency
    
    @property
    def jitter_ms(self) -> float:
        return self.jitter
    
    @property
    def loss_percent(self) -> float:
        return self.packet_loss
    
    def is_valid(self) -> bool:
        """Verifica si los resultados son válidos"""
        return (self.test_status == "completed" and 
                self.download_speed >= 0 and 
                self.latency > 0 and 
                self.latency < 10000)
    
    def get_performance_grade(self) -> str:
        """Retorna calificación del rendimiento"""
        if not self.is_valid():
            return "Sin datos"
        
        if self.download_speed >= 100 and self.latency <= 20:
            return "Excelente"
        elif self.download_speed >= 50 and self.latency <= 50:
            return "Muy bueno"
        elif self.download_speed >= 25 and self.latency <= 100:
            return "Bueno"
        elif self.download_speed >= 10 and self.latency <= 200:
            return "Regular"
        else:
            return "Pobre"
    
    def to_dict(self) -> dict:
        return {
            'download_speed': self.download_speed,
            'upload_speed': self.upload_speed,
            'latency': self.latency,
            'jitter': self.jitter,
            'packet_loss': self.packet_loss,
            'test_duration': self.test_duration,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'server_info': self.server_info,
            'error_message': self.error_message,
            'test_status': self.test_status
        }

@dataclass
class SurveyPoint:
    """Punto de medición en el site survey - ULTRA-COMPATIBLE v3"""
    x: float
    y: float
    timestamp: datetime
    networks: List[NetworkData]
    iperf_results: Optional[IperfResults] = None
    notes: str = ""
    point_id: str = ""
    
    # Métricas calculadas (se actualizan automáticamente)
    avg_signal_strength: float = field(init=False, default=0.0)
    max_signal_strength: float = field(init=False, default=0.0)
    network_count: int = field(init=False, default=0)
    avg_snr: float = field(init=False, default=0.0)
    
    def __post_init__(self):
        if not self.point_id:
            # Generar ID único más legible
            timestamp_str = self.timestamp.strftime('%H%M%S')
            unique_id = str(uuid.uuid4())[:4]
            self.point_id = f"point_{timestamp_str}_{unique_id}"
        
        self.calculate_metrics()
    
    def calculate_metrics(self):
        """Calcula métricas del punto basadas en las redes detectadas"""
        if not self.networks:
            self.avg_signal_strength = 0.0
            self.max_signal_strength = 0.0
            self.network_count = 0
            self.avg_snr = 0.0
            return
        
        self.network_count = len(self.networks)
        
        # Señales
        signals = [net.signal for net in self.networks if hasattr(net, 'signal')]
        if signals:
            self.avg_signal_strength = sum(signals) / len(signals)
            self.max_signal_strength = max(signals)
        
        # SNR
        snr_values = [net.snr for net in self.networks if hasattr(net, 'snr') and net.snr > 0]
        if snr_values:
            self.avg_snr = sum(snr_values) / len(snr_values)
    
    # PROPIEDADES DE COMPATIBILIDAD ULTRA-COMPLETA
    @property
    def scan_data(self) -> List[NetworkData]:
        """Alias para networks (compatibilidad con ap_locator y otros módulos)"""
        return self.networks
    
    @property
    def strongest_network(self) -> Optional[NetworkData]:
        """Red con mejor señal (compatibilidad con heatmap y análisis)"""
        if not self.networks:
            return None
        return max(self.networks, key=lambda n: getattr(n, 'signal', -100))
    
    @property
    def weakest_network(self) -> Optional[NetworkData]:
        """Red con peor señal"""
        if not self.networks:
            return None
        return min(self.networks, key=lambda n: getattr(n, 'signal', -100))
    
    @property
    def band_2_4_networks(self) -> List[NetworkData]:
        """Redes en banda 2.4GHz"""
        return [net for net in self.networks if net.frequency < 5000]
    
    @property
    def band_5_networks(self) -> List[NetworkData]:
        """Redes en banda 5GHz"""
        return [net for net in self.networks if net.frequency >= 5000]
    
    def get_network_by_ssid(self, ssid: str) -> Optional[NetworkData]:
        """Obtiene una red específica por SSID"""
        for network in self.networks:
            if network.ssid == ssid:
                return network
        return None
    
    def get_network_by_bssid(self, bssid: str) -> Optional[NetworkData]:
        """Obtiene una red específica por BSSID"""
        for network in self.networks:
            if network.bssid == bssid:
                return network
        return None
    
    def get_networks_by_channel(self, channel: int) -> List[NetworkData]:
        """Obtiene todas las redes en un canal específico"""
        return [net for net in self.networks if net.channel == channel]
    
    def has_performance_data(self) -> bool:
        """Verifica si tiene datos de rendimiento válidos"""
        return self.iperf_results is not None and self.iperf_results.is_valid()
    
    def get_summary_stats(self) -> dict:
        """Retorna estadísticas resumidas del punto"""
        return {
            'point_id': self.point_id,
            'position': (self.x, self.y),
            'timestamp': self.timestamp,
            'network_count': self.network_count,
            'avg_signal': self.avg_signal_strength,
            'max_signal': self.max_signal_strength,
            'avg_snr': self.avg_snr,
            'has_performance_data': self.has_performance_data(),
            'strongest_ssid': self.strongest_network.ssid if self.strongest_network else None
        }
    
    def to_dict(self) -> dict:
        """Convierte a diccionario con TODA la información"""
        return {
            'x': self.x,
            'y': self.y,
            'timestamp': self.timestamp.isoformat(),
            'networks': [net.to_dict() for net in self.networks],
            'iperf_results': self.iperf_results.to_dict() if self.iperf_results else None,
            'notes': self.notes,
            'point_id': self.point_id,
            'avg_signal_strength': self.avg_signal_strength,
            'max_signal_strength': self.max_signal_strength,
            'network_count': self.network_count,
            'avg_snr': self.avg_snr,
            'summary_stats': self.get_summary_stats()
        }

@dataclass 
class AccessPoint:
    """Información de un Access Point detectado"""
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
    detection_points: List[str] = field(default_factory=list)
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    
    def __post_init__(self):
        if self.first_seen is None:
            self.first_seen = datetime.now()
        if self.last_seen is None:
            self.last_seen = datetime.now()
    
    @property
    def x(self) -> float:
        """Alias para estimated_x"""
        return self.estimated_x
    
    @property 
    def y(self) -> float:
        """Alias para estimated_y"""
        return self.estimated_y
    
    @property
    def band(self) -> str:
        """Banda de frecuencia"""
        return "5GHz" if self.frequency > 5000 else "2.4GHz"
    
    def update_position(self, x: float, y: float, confidence: float):
        """Actualiza posición y confianza"""
        self.estimated_x = x
        self.estimated_y = y
        self.confidence = confidence
        self.last_seen = datetime.now()
    
    def add_detection_point(self, point_id: str):
        """Agrega punto de detección"""
        if point_id not in self.detection_points:
            self.detection_points.append(point_id)
            self.last_seen = datetime.now()
    
    def to_dict(self) -> dict:
        return {
            'bssid': self.bssid,
            'ssid': self.ssid,
            'estimated_x': self.estimated_x,
            'estimated_y': self.estimated_y,
            'confidence': self.confidence,
            'channel': self.channel,
            'vendor': self.vendor,
            'frequency': self.frequency,
            'security': self.security,
            'max_signal': self.max_signal,
            'detection_points': self.detection_points,
            'first_seen': self.first_seen.isoformat() if self.first_seen else None,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None
        }

@dataclass
class ProjectInfo:
    """Información del proyecto de site survey"""
    name: str = "Nuevo Proyecto"
    client_name: str = ""
    location: str = ""
    date_created: Optional[datetime] = None
    date_modified: Optional[datetime] = None
    description: str = ""
    floor_plan_path: str = ""
    scale_meters_per_pixel: float = 1.0
    survey_points: List[SurveyPoint] = field(default_factory=list)
    access_points: List[AccessPoint] = field(default_factory=list) 
    calibration_points: List[tuple] = field(default_factory=list)
    project_id: str = ""
    
    def __post_init__(self):
        if self.date_created is None:
            self.date_created = datetime.now()
        if self.date_modified is None:
            self.date_modified = datetime.now()
        if not self.project_id:
            self.project_id = f"proj_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def update_modification_date(self):
        """Actualiza fecha de modificación"""
        self.date_modified = datetime.now()
    
    def get_project_stats(self) -> dict:
        """Retorna estadísticas del proyecto"""
        return {
            'total_survey_points': len(self.survey_points),
            'total_access_points': len(self.access_points),
            'has_floor_plan': bool(self.floor_plan_path),
            'is_calibrated': self.scale_meters_per_pixel != 1.0,
            'project_age_days': (datetime.now() - self.date_created).days if self.date_created else 0
        }

@dataclass
class ServiceMonitorData:
    """Datos de monitoreo de servicios"""
    service_name: str
    target_host: str
    latency: float
    status: str
    timestamp: datetime
    response_time: float = 0.0
    packet_loss: float = 0.0
    jitter: float = 0.0
    is_reachable: bool = True
    
    def __post_init__(self):
        # Asegurar coherencia de datos
        if not self.is_reachable:
            self.status = 'unreachable'
        elif self.latency > 1000:
            self.status = 'timeout'
        elif self.latency > 0:
            self.status = 'active'
    
    def get_health_status(self) -> str:
        """Retorna estado de salud del servicio"""
        if not self.is_reachable:
            return "Crítico"
        elif self.latency > 200:
            return "Degradado"
        elif self.latency > 100:
            return "Advertencia"
        else:
            return "Saludable"
    
    def to_dict(self) -> dict:
        return {
            'service_name': self.service_name,
            'target_host': self.target_host,
            'latency': self.latency,
            'status': self.status,
            'timestamp': self.timestamp.isoformat(),
            'response_time': self.response_time,
            'packet_loss': self.packet_loss,
            'jitter': self.jitter,
            'is_reachable': self.is_reachable,
            'health_status': self.get_health_status()
        }

# CLASE ADICIONAL para compatibilidad con análisis de APs
class APPosition:
    """Clase específica para posiciones de AP (compatible con APLocator)"""
    
    def __init__(self, bssid: str, ssid: str, x: float = 0.0, y: float = 0.0, 
                 confidence: float = 0.0, measurement_count: int = 0, 
                 avg_rssi: float = 0.0, status: str = 'estimated'):
        self.bssid = bssid
        self.ssid = ssid
        self.x = x
        self.y = y
        self.confidence = confidence
        self.measurement_count = measurement_count
        self.avg_rssi = avg_rssi
        self.status = status
        
        # Aliases para compatibilidad total
        self.estimated_x = x
        self.estimated_y = y
    
    def __repr__(self):
        return f"APPosition(ssid='{self.ssid}', pos=({self.x:.1f}, {self.y:.1f}), conf={self.confidence:.1%})"
    
    def to_dict(self) -> dict:
        return {
            'bssid': self.bssid,
            'ssid': self.ssid,
            'x': self.x,
            'y': self.y,
            'estimated_x': self.estimated_x,
            'estimated_y': self.estimated_y,
            'confidence': self.confidence,
            'measurement_count': self.measurement_count,
            'avg_rssi': self.avg_rssi,
            'status': self.status
        }

# Funciones utilitarias para conversión y compatibilidad
def survey_point_from_dict(data: dict) -> SurveyPoint:
    """Crea SurveyPoint desde diccionario"""
    networks = []
    for net_data in data.get('networks', []):
        network = NetworkData(
            ssid=net_data['ssid'],
            bssid=net_data['bssid'], 
            signal=net_data['signal'],
            frequency=net_data['frequency'],
            channel=net_data['channel'],
            security=net_data['security'],
            vendor=net_data.get('vendor', 'Unknown'),
            quality=net_data.get('quality', 0),
            noise=net_data.get('noise', -96),
            snr=net_data.get('snr', 0.0),
            bandwidth=net_data.get('bandwidth', '20MHz')
        )
        networks.append(network)
    
    # iPerf results si existen
    iperf_results = None
    if data.get('iperf_results'):
        iperf_results = IperfResults()
        iperf_data = data['iperf_results']
        iperf_results.download_speed = iperf_data.get('download_speed', 0)
        iperf_results.upload_speed = iperf_data.get('upload_speed', 0)
        iperf_results.latency = iperf_data.get('latency', 0)
        iperf_results.jitter = iperf_data.get('jitter', 0)
        iperf_results.packet_loss = iperf_data.get('packet_loss', 0)
        iperf_results.test_status = iperf_data.get('test_status', 'completed')
        if iperf_data.get('timestamp'):
            iperf_results.timestamp = datetime.fromisoformat(iperf_data['timestamp'])
    
    return SurveyPoint(
        x=data['x'],
        y=data['y'],
        timestamp=datetime.fromisoformat(data['timestamp']),
        networks=networks,
        iperf_results=iperf_results,
        notes=data.get('notes', ''),
        point_id=data.get('point_id', '')
    )

def access_point_from_dict(data: dict) -> AccessPoint:
    """Crea AccessPoint desde diccionario"""
    ap = AccessPoint(
        bssid=data['bssid'],
        ssid=data['ssid'],
        estimated_x=data.get('estimated_x', 0.0),
        estimated_y=data.get('estimated_y', 0.0),
        confidence=data.get('confidence', 0.0),
        channel=data.get('channel', 0),
        vendor=data.get('vendor', 'Unknown'),
        frequency=data.get('frequency', 0),
        security=data.get('security', 'Unknown'),
        max_signal=data.get('max_signal', -100),
        detection_points=data.get('detection_points', [])
    )
    
    if data.get('first_seen'):
        ap.first_seen = datetime.fromisoformat(data['first_seen'])
    if data.get('last_seen'):
        ap.last_seen = datetime.fromisoformat(data['last_seen'])
    
    return ap