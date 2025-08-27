# analysis/ap_locator.py - CORREGIDO para funcionar correctamente
import numpy as np
from scipy.optimize import minimize
from typing import List, Tuple, Optional, Dict
from core.data_models import SurveyPoint

class APPosition:
    """Clase para representar posición de AP estimada"""
    def __init__(self, bssid: str, ssid: str, x: float, y: float, confidence: float = 0.0, 
                 measurement_count: int = 0, avg_rssi: float = 0.0, status: str = 'estimated'):
        self.bssid = bssid
        self.ssid = ssid
        self.x = x
        self.y = y
        self.estimated_x = x  # Para compatibilidad
        self.estimated_y = y  # Para compatibilidad
        self.confidence = confidence
        self.measurement_count = measurement_count
        self.avg_rssi = avg_rssi
        self.status = status

class APLocator:
    """Localización de Access Points usando multilateración CORREGIDA"""
    
    def __init__(self, pixels_per_meter: float = 10.0):
        self.pixels_per_meter = pixels_per_meter
        self.path_loss_exponent = 2.5  # Reducido para interior
        self.reference_rssi = -40  # RSSI a 1 metro
        self.reference_distance = 1.0  # metros
    
    def estimate_all_aps(self, survey_points: List[SurveyPoint]) -> Dict[str, APPosition]:
        """Estima posiciones de todos los APs detectados"""
        if not survey_points or not self.pixels_per_meter:
            print("❌ Sin puntos de survey o sin calibración")
            return {}
        
        print(f"🔍 Procesando {len(survey_points)} puntos de survey...")
        
        # Agrupar mediciones por BSSID
        ap_measurements = {}
        
        for point in survey_points:
            # Usar la propiedad networks (que es alias de scan_data)
            networks = getattr(point, 'networks', [])
            
            for network in networks:
                bssid = network.bssid
                if bssid not in ap_measurements:
                    ap_measurements[bssid] = {
                        'ssid': network.ssid,
                        'measurements': []
                    }
                
                ap_measurements[bssid]['measurements'].append({
                    'position': (point.x, point.y),
                    'rssi': network.signal,
                    'frequency': getattr(network, 'frequency', 2400)
                })
        
        print(f"📡 Encontrados {len(ap_measurements)} APs únicos")
        
        # Estimar posición de cada AP con al menos 3 mediciones
        estimated_aps = {}
        
        for bssid, data in ap_measurements.items():
            measurements = data['measurements']
            
            if len(measurements) < 3:
                print(f"⚠️ AP {data['ssid']} solo tiene {len(measurements)} mediciones (mínimo 3)")
                continue
            
            print(f"🔍 Estimando posición de {data['ssid']} con {len(measurements)} mediciones")
            
            try:
                position = self.estimate_ap_position(bssid, measurements)
                
                if position:
                    avg_rssi = np.mean([m['rssi'] for m in measurements])
                    confidence = self._calculate_confidence(measurements)
                    
                    ap_pos = APPosition(
                        bssid=bssid,
                        ssid=data['ssid'],
                        x=position[0],
                        y=position[1],
                        confidence=confidence,
                        measurement_count=len(measurements),
                        avg_rssi=avg_rssi,
                        status='estimated'
                    )
                    
                    estimated_aps[bssid] = ap_pos
                    print(f"✅ AP {data['ssid']} estimado en ({position[0]:.0f}, {position[1]:.0f}) con confianza {confidence:.1%}")
                else:
                    print(f"❌ No se pudo estimar posición de {data['ssid']}")
                    
            except Exception as e:
                print(f"❌ Error estimando {data['ssid']}: {e}")
                continue
        
        print(f"🎯 Total de APs estimados: {len(estimated_aps)}")
        return estimated_aps
    
    def estimate_ap_position(self, bssid: str, measurements: List[dict]) -> Optional[Tuple[float, float]]:
        """Estima la posición de un AP específico usando trilateración mejorada"""
        if len(measurements) < 3:
            return None
        
        # Filtrar outliers RSSI
        rssi_values = [m['rssi'] for m in measurements]
        rssi_mean = np.mean(rssi_values)
        rssi_std = np.std(rssi_values)
        
        # Solo filtrar si hay outliers extremos
        if rssi_std > 15:  # Solo filtrar si hay mucha variación
            filtered_measurements = [
                m for m in measurements 
                if abs(m['rssi'] - rssi_mean) <= 2 * rssi_std
            ]
            
            if len(filtered_measurements) >= 3:
                measurements = filtered_measurements
        
        # Convertir RSSI a distancias en píxeles
        positions = []
        distances = []
        
        for m in measurements:
            positions.append(m['position'])
            
            # Conversión mejorada RSSI a distancia
            distance_meters = self._rssi_to_distance_meters(m['rssi'])
            distance_pixels = distance_meters * self.pixels_per_meter
            
            # Limitar distancias extremas
            distance_pixels = max(10, min(distance_pixels, 1000))
            distances.append(distance_pixels)
        
        # Punto inicial usando centroide ponderado por señal
        weights = []
        for m in measurements:
            # Peso mayor para señales más fuertes
            weight = 10 ** (m['rssi'] / 20.0)  # Conversión logarítmica
            weights.append(max(0.1, weight))
        
        total_weight = sum(weights)
        
        if total_weight > 0:
            initial_x = sum(p[0] * w for p, w in zip(positions, weights)) / total_weight
            initial_y = sum(p[1] * w for p, w in zip(positions, weights)) / total_weight
        else:
            # Fallback al centroide simple
            initial_x = np.mean([p[0] for p in positions])
            initial_y = np.mean([p[1] for p in positions])
        
        # Optimización con múltiples intentos
        best_result = None
        best_error = float('inf')
        
        # Intentar desde diferentes puntos iniciales
        initial_positions = [
            (initial_x, initial_y),  # Centroide ponderado
            (np.mean([p[0] for p in positions]), np.mean([p[1] for p in positions])),  # Centroide simple
        ]
        
        # Agregar algunas posiciones aleatorias cerca del centroide
        for _ in range(3):
            noise_x = np.random.normal(0, 50)
            noise_y = np.random.normal(0, 50)
            initial_positions.append((initial_x + noise_x, initial_y + noise_y))
        
        for init_pos in initial_positions:
            try:
                result = minimize(
                    self._error_function,
                    init_pos,
                    args=(positions, distances),
                    method='L-BFGS-B',
                    options={'maxiter': 1000, 'ftol': 1e-9}
                )
                
                if result.success and result.fun < best_error:
                    best_result = result
                    best_error = result.fun
                    
            except Exception as e:
                continue
        
        if best_result and best_result.success:
            # Validar que la posición sea razonable
            x, y = best_result.x
            
            # Verificar que no esté demasiado lejos de todos los puntos de medición
            max_distance = max([
                np.sqrt((x - p[0])**2 + (y - p[1])**2) / self.pixels_per_meter
                for p in positions
            ])
            
            if max_distance < 200:  # Máximo 200 metros
                return (float(x), float(y))
        
        return None
    
    def _rssi_to_distance_meters(self, rssi: int) -> float:
        """Convierte RSSI a distancia en metros usando modelo de path loss"""
        if rssi >= self.reference_rssi:
            return self.reference_distance
        
        # Fórmula de path loss: RSSI = RSSI_ref - 10*n*log10(d/d_ref)
        # Resolviendo para d: d = d_ref * 10^((RSSI_ref - RSSI) / (10*n))
        
        rssi_diff = self.reference_rssi - rssi
        distance = self.reference_distance * (10 ** (rssi_diff / (10 * self.path_loss_exponent)))
        
        # Limitar distancia a valores razonables
        return min(max(distance, 0.5), 150.0)  # Entre 0.5 y 150 metros
    
    def _error_function(self, ap_pos: np.ndarray, measurement_points: List, distances: List) -> float:
        """Función de error para optimización - MEJORADA"""
        x, y = ap_pos
        total_error = 0
        
        for i, (point, expected_dist) in enumerate(zip(measurement_points, distances)):
            px, py = point
            actual_dist = np.sqrt((x - px)**2 + (y - py)**2)
            
            # Error cuadrático con peso
            error = (actual_dist - expected_dist)**2
            
            # Peso menor para distancias muy grandes (menos confiables)
            weight = 1.0 / (1.0 + expected_dist / (100 * self.pixels_per_meter))
            
            total_error += weight * error
        
        # Penalización por posiciones extremas (fuera del área razonable)
        # Asumir área de trabajo de 100x100 metros
        area_size = 100 * self.pixels_per_meter
        
        if abs(x) > area_size or abs(y) > area_size:
            total_error += 1000000  # Penalización grande
        
        return total_error
    
    def _calculate_confidence(self, measurements: List[dict]) -> float:
        """Calcula la confianza de la estimación basada en múltiples factores"""
        if len(measurements) < 3:
            return 0.0
        
        # Factor 1: Número de mediciones (más mediciones = mayor confianza)
        count_factor = min(1.0, len(measurements) / 8.0)
        
        # Factor 2: Consistencia de RSSI (menos variación = mayor confianza)
        rssi_values = [m['rssi'] for m in measurements]
        rssi_std = np.std(rssi_values)
        consistency_factor = max(0.0, 1.0 - (rssi_std / 25.0))
        
        # Factor 3: Distribución espacial (puntos más dispersos = mayor confianza)
        positions = [m['position'] for m in measurements]
        if len(positions) >= 4:
            # Calcular dispersión de puntos
            x_coords = [p[0] for p in positions]
            y_coords = [p[1] for p in positions]
            x_spread = max(x_coords) - min(x_coords)
            y_spread = max(y_coords) - min(y_coords)
            
            # Normalizar por píxeles per metro
            spread_meters = ((x_spread + y_spread) / 2) / self.pixels_per_meter
            spatial_factor = min(1.0, spread_meters / 20.0)  # 20 metros de dispersión = factor 1.0
        else:
            spatial_factor = 0.5
        
        # Factor 4: Calidad promedio de señal
        avg_rssi = np.mean(rssi_values)
        signal_factor = max(0.0, min(1.0, (avg_rssi + 100) / 40.0))  # -100 a -60 dBm
        
        # Combinación ponderada de factores
        confidence = (
            count_factor * 0.3 +
            consistency_factor * 0.3 +
            spatial_factor * 0.2 +
            signal_factor * 0.2
        )
        
        return max(0.0, min(1.0, confidence))
    
    def validate_position(self, position: Tuple[float, float], survey_points: List[SurveyPoint], 
                         bssid: str) -> Tuple[bool, str]:
        """Valida si una posición de AP es razonable"""
        measurements = []
        
        for point in survey_points:
            networks = getattr(point, 'networks', [])
            for network in networks:
                if network.bssid == bssid:
                    dx = point.x - position[0]
                    dy = point.y - position[1]
                    distance_px = np.sqrt(dx*dx + dy*dy)
                    distance_m = distance_px / self.pixels_per_meter
                    
                    # Calcular RSSI esperado
                    expected_rssi = self.reference_rssi - 10 * self.path_loss_exponent * np.log10(
                        max(distance_m / self.reference_distance, 0.1)
                    )
                    
                    actual_rssi = network.signal
                    
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
        
        # Criterios de validación más permisivos
        if avg_error > 25:
            return False, f"Error RSSI alto: {avg_error:.1f} dB"
        
        if max_distance > 150:
            return False, f"Distancia excesiva: {max_distance:.1f} m"
        
        return True, f"Posición válida (error: {avg_error:.1f} dB, dist máx: {max_distance:.1f} m)"
    
    def get_coverage_radius(self, bssid: str, position: Tuple[float, float], 
                           survey_points: List[SurveyPoint]) -> float:
        """Calcula radio de cobertura basado en mediciones reales"""
        if not position:
            return 50
        
        distances = []
        for point in survey_points:
            networks = getattr(point, 'networks', [])
            for network in networks:
                if network.bssid == bssid and network.signal >= -85:
                    dx = point.x - position[0]
                    dy = point.y - position[1]
                    distance_px = np.sqrt(dx*dx + dy*dy)
                    distances.append(distance_px)
        
        if distances:
            # Usar percentil 90 como radio de cobertura
            coverage_radius = np.percentile(distances, 90)
            return max(20, min(coverage_radius, 300))  # Entre 20 y 300 píxeles
        
        return 50  # Radio por defecto