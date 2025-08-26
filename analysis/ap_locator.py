# analysis/ap_locator.py
import numpy as np
from scipy.optimize import minimize
from typing import List, Tuple, Optional, Dict
from core.data_models import SurveyPoint, APPosition

class APLocator:
    """Localización de Access Points usando multilateración"""
    
    def __init__(self, pixels_per_meter: float = 10.0):
        self.pixels_per_meter = pixels_per_meter
        self.path_loss_exponent = 3.0
        self.reference_rssi = -40
    
    def estimate_all_aps(self, survey_points: List[SurveyPoint]) -> Dict[str, APPosition]:
        """Estima posiciones de todos los APs detectados"""
        if not survey_points or not self.pixels_per_meter:
            return {}
        
        # Agrupar mediciones por BSSID
        ap_measurements = {}
        for point in survey_points:
            for network in point.scan_data:
                if network.bssid not in ap_measurements:
                    ap_measurements[network.bssid] = {
                        'ssid': network.ssid,
                        'measurements': []
                    }
                ap_measurements[network.bssid]['measurements'].append({
                    'position': (point.x, point.y),
                    'rssi': network.rssi
                })
        
        # Estimar posición de cada AP con al menos 3 mediciones
        estimated_aps = {}
        for bssid, data in ap_measurements.items():
            if len(data['measurements']) >= 3:
                position = self.estimate_ap_position(bssid, data['measurements'])
                if position:
                    avg_rssi = np.mean([m['rssi'] for m in data['measurements']])
                    estimated_aps[bssid] = APPosition(
                        bssid=bssid,
                        ssid=data['ssid'],
                        position=position,
                        confidence=self._calculate_confidence(data['measurements']),
                        measurement_count=len(data['measurements']),
                        avg_rssi=avg_rssi,
                        status='estimated'
                    )
        
        return estimated_aps
    
    def estimate_ap_position(self, bssid: str, measurements: List[dict]) -> Optional[Tuple[float, float]]:
        """Estima la posición de un AP específico"""
        if len(measurements) < 3:
            return None
        
        # Filtrar outliers
        rssi_values = [m['rssi'] for m in measurements]
        mean_rssi = np.mean(rssi_values)
        std_rssi = np.std(rssi_values)
        
        filtered_measurements = [
            m for m in measurements 
            if abs(m['rssi'] - mean_rssi) <= 2 * std_rssi
        ]
        
        if len(filtered_measurements) < 3:
            filtered_measurements = measurements
        
        # Convertir RSSI a distancias
        points = []
        distances = []
        for m in filtered_measurements:
            points.append(m['position'])
            distances.append(self._rssi_to_distance(m['rssi']))
        
        # Punto inicial usando centroide ponderado
        weights = [1.0 / (1.0 + abs(m['rssi']) / 10.0) for m in filtered_measurements]
        total_weight = sum(weights)
        
        if total_weight > 0:
            initial_x = sum(p[0] * w for p, w in zip(points, weights)) / total_weight
            initial_y = sum(p[1] * w for p, w in zip(points, weights)) / total_weight
        else:
            initial_x = np.mean([p[0] for p in points])
            initial_y = np.mean([p[1] for p in points])
        
        # Optimización
        result = minimize(
            self._error_function,
            [initial_x, initial_y],
            args=(points, distances),
            method='L-BFGS-B',
            options={'maxiter': 1000}
        )
        
        if result.success:
            return (int(result.x[0]), int(result.x[1]))
        return None
    
    def _rssi_to_distance(self, rssi: int) -> float:
        """Convierte RSSI a distancia en píxeles"""
        distance_meters = 10 ** ((self.reference_rssi - rssi) / (10 * self.path_loss_exponent))
        distance_pixels = distance_meters * self.pixels_per_meter
        return min(distance_pixels, 500)  # Limitar a 500 píxeles
    
    def _error_function(self, ap_pos: np.ndarray, measurement_points: List, distances: List) -> float:
        """Función de error para optimización"""
        x, y = ap_pos
        total_error = 0
        
        for point, expected_dist in zip(measurement_points, distances):
            px, py = point
            actual_dist = np.sqrt((x - px)**2 + (y - py)**2)
            weight = 1.0 / (1.0 + expected_dist / 10.0)
            total_error += weight * (actual_dist - expected_dist)**2
        
        return total_error
    
    def _calculate_confidence(self, measurements: List[dict]) -> float:
        """Calcula la confianza de la estimación"""
        if len(measurements) < 3:
            return 0.0
        
        # Factores: cantidad de mediciones y consistencia de RSSI
        count_factor = min(1.0, len(measurements) / 10.0)
        
        rssi_values = [m['rssi'] for m in measurements]
        rssi_std = np.std(rssi_values)
        consistency_factor = max(0, 1.0 - (rssi_std / 20.0))
        
        return (count_factor * 0.5 + consistency_factor * 0.5)
    
    def validate_position(self, position: Tuple[float, float], survey_points: List[SurveyPoint], 
                         bssid: str) -> Tuple[bool, str]:
        """Valida si una posición de AP es razonable"""
        measurements = []
        
        for point in survey_points:
            for network in point.scan_data:
                if network.bssid == bssid:
                    dx = point.x - position[0]
                    dy = point.y - position[1]
                    distance_px = np.sqrt(dx*dx + dy*dy)
                    distance_m = distance_px / self.pixels_per_meter
                    
                    expected_rssi = self.reference_rssi - 10 * self.path_loss_exponent * np.log10(max(distance_m, 0.1))
                    actual_rssi = network.rssi
                    
                    measurements.append({
                        'distance_m': distance_m,
                        'expected_rssi': expected_rssi,
                        'actual_rssi': actual_rssi,
                        'error': abs(expected_rssi - actual_rssi)
                    })
        
        if not measurements:
            return False, "Sin mediciones para validar"
        
        avg_error = np.mean([m['error'] for m in measurements])
        max_distance = max([m['distance_m'] for m in measurements])
        
        if avg_error > 20:
            return False, f"Error RSSI alto: {avg_error:.1f} dB"
        
        if max_distance > 100:
            return False, f"Distancia excesiva: {max_distance:.1f} m"
        
        return True, f"Posición válida (error: {avg_error:.1f} dB)"
    
    def get_coverage_radius(self, bssid: str, position: Tuple[float, float], 
                           survey_points: List[SurveyPoint]) -> float:
        """Calcula radio de cobertura basado en mediciones reales"""
        if not position:
            return 50
        
        distances = []
        for point in survey_points:
            for network in point.scan_data:
                if network.bssid == bssid and network.rssi >= -85:
                    dx = point.x - position[0]
                    dy = point.y - position[1]
                    distance_px = np.sqrt(dx*dx + dy*dy)
                    distances.append(distance_px)
        
        if distances:
            return max(20, min(np.percentile(distances, 90), 200))
        return 50