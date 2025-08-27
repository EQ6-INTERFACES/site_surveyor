# analysis/heatmap.py - MEJORADO con soporte para SSID específico y métricas
import numpy as np
from PIL import Image
from scipy.interpolate import Rbf, griddata
from matplotlib.colors import LinearSegmentedColormap
from typing import List, Optional, Tuple
from core.data_models import SurveyPoint

class HeatmapGenerator:
    """Generador de mapas de calor para WiFi MEJORADO"""
    
    def __init__(self):
        # Mapas de colores mejorados
        self.colormap_rssi = self._create_rssi_colormap()
        self.colormap_speed = self._create_speed_colormap() 
        self.colormap_latency = self._create_latency_colormap()
    
    def _create_rssi_colormap(self):
        """Crea mapa de colores específico para RSSI"""
        # Azul (malo) -> Rojo (regular) -> Amarillo (bueno) -> Verde (excelente)
        colors = [
            (0.0, "#2196F3"),   # -90+ dBm: Azul (muy malo)
            (0.33, "#F44336"),  # -80 dBm: Rojo (malo) 
            (0.66, "#FFC107"),  # -70 dBm: Amarillo (bueno)
            (1.0, "#4CAF50")    # -60+ dBm: Verde (excelente)
        ]
        return LinearSegmentedColormap.from_list("wifi_rssi", colors)
    
    def _create_speed_colormap(self):
        """Mapa de colores para velocidad (invertido - más rápido es mejor)"""
        colors = [
            (0.0, "#F44336"),   # 0 Mbps: Rojo (malo)
            (0.33, "#FFC107"),  # 25 Mbps: Amarillo (regular)
            (0.66, "#8BC34A"),  # 50 Mbps: Verde claro (bueno)
            (1.0, "#4CAF50")    # 100+ Mbps: Verde (excelente)
        ]
        return LinearSegmentedColormap.from_list("wifi_speed", colors)
    
    def _create_latency_colormap(self):
        """Mapa de colores para latencia (invertido - menos latencia es mejor)"""
        colors = [
            (1.0, "#F44336"),   # 200+ ms: Rojo (muy malo)
            (0.66, "#FF9800"),  # 100 ms: Naranja (malo)
            (0.33, "#FFC107"),  # 50 ms: Amarillo (regular)
            (0.0, "#4CAF50")    # 0 ms: Verde (excelente)
        ]
        return LinearSegmentedColormap.from_list("wifi_latency", colors)
    
    def generate(self, survey_points: List[SurveyPoint], width: int, height: int,
                 target_bssid: Optional[str] = None, metric: str = "rssi") -> Image.Image:
        """
        Genera heatmap para métrica específica y red específica
        
        Args:
            survey_points: Lista de puntos de medición
            width: Ancho del heatmap en píxeles
            height: Alto del heatmap en píxeles  
            target_bssid: BSSID específico a analizar (None para la red más fuerte)
            metric: Métrica a visualizar ('rssi', 'snr', 'download', 'upload', 'ping', 'jitter')
        """
        
        print(f"🗺️ Generando heatmap: {metric}" + (f" para {target_bssid}" if target_bssid else " (todas las redes)"))
        
        # Extraer puntos y valores
        points = []
        for point in survey_points:
            value = self._extract_metric_value(point, target_bssid, metric)
            if value is not None:
                points.append((point.x, point.y, value))
        
        print(f"🔍 Procesando {len(points)} puntos con datos válidos")
        
        if len(points) < 3:
            print("⚠️ Insuficientes puntos para generar heatmap")
            return Image.new('RGBA', (width, height), (0, 0, 0, 0))
        
        # Determinar rangos y configuración
        min_val, max_val, invert_colors = self._get_metric_ranges(points, metric)
        
        print(f"📊 Rango de valores: {min_val:.1f} - {max_val:.1f}")
        
        # Generar heatmap
        return self._generate_heatmap(points, width, height, min_val, max_val, metric)
    
    def _extract_metric_value(self, point: SurveyPoint, target_bssid: Optional[str], 
                             metric: str) -> Optional[float]:
        """Extrae valor de métrica del punto para BSSID específico o mejor señal"""
        
        # Métricas de iPerf
        if metric in ["download", "upload", "ping", "jitter"]:
            iperf = getattr(point, 'iperf_results', None)
            if not iperf:
                return None
                
            if metric == "download":
                return getattr(iperf, 'download_speed', None)
            elif metric == "upload":
                return getattr(iperf, 'upload_speed', None)
            elif metric == "ping":
                latency = getattr(iperf, 'latency', None)
                return latency if latency and latency < 999 else None
            elif metric == "jitter":
                return getattr(iperf, 'jitter', None)
        
        # Métricas de WiFi (RSSI, SNR)
        networks = getattr(point, 'networks', [])
        if not networks:
            return None
        
        target_network = None
        
        if target_bssid:
            # Buscar red específica por BSSID
            for network in networks:
                if network.bssid == target_bssid:
                    target_network = network
                    break
        else:
            # Usar red con mejor señal
            target_network = max(networks, key=lambda n: getattr(n, 'signal', -100))
        
        if not target_network:
            return None
        
        if metric == "rssi":
            return getattr(target_network, 'signal', None)
        elif metric == "snr":
            return getattr(target_network, 'snr', None)
        
        return None
    
    def _get_metric_ranges(self, points: List[Tuple], metric: str) -> Tuple[float, float, bool]:
        """Obtiene rangos apropiados para la métrica"""
        values = [p[2] for p in points]
        
        if not values:
            return 0, 1, False
        
        min_val = min(values)
        max_val = max(values)
        
        # Rangos específicos por métrica con valores reales si están disponibles
        if metric == "rssi":
            # Usar rango estándar de RSSI pero ajustar según datos reales
            range_min = min(-95, min_val - 5)
            range_max = max(-30, max_val + 5)
            return range_min, range_max, False
            
        elif metric == "snr":
            range_min = max(0, min_val - 2)
            range_max = min(60, max_val + 5)
            return range_min, range_max, False
            
        elif metric in ["download", "upload"]:
            range_min = 0
            range_max = max(100, max_val * 1.2)
            return range_min, range_max, False
            
        elif metric in ["ping", "jitter"]:
            range_min = 0
            range_max = min(300, max_val * 1.3)
            return range_min, range_max, True  # Invertir colores (menos es mejor)
            
        else:
            # Rango dinámico basado en datos
            padding = (max_val - min_val) * 0.1
            return min_val - padding, max_val + padding, False
    
    def _generate_heatmap(self, points: List[Tuple], width: int, height: int,
                         min_val: float, max_val: float, metric: str) -> Image.Image:
        """Genera el heatmap usando interpolación mejorada"""
        
        x_coords, y_coords, values = zip(*points)
        
        # Verificar rangos válidos
        if max_val <= min_val:
            max_val = min_val + 1
        
        # Crear grid de alta resolución para interpolación suave
        grid_resolution_x = min(width//2, 200)  # Resolución adaptativa
        grid_resolution_y = min(height//2, 200)
        
        x_grid = np.linspace(0, width, grid_resolution_x)
        y_grid = np.linspace(0, height, grid_resolution_y)
        grid_x, grid_y = np.meshgrid(x_grid, y_grid)
        
        try:
            # Usar interpolación griddata que es más robusta
            points_array = np.column_stack((x_coords, y_coords))
            grid_z = griddata(points_array, values, (grid_x, grid_y), method='cubic', fill_value=np.nan)
            
            # Rellenar NaN con interpolación linear
            nan_mask = np.isnan(grid_z)
            if nan_mask.any():
                grid_z_linear = griddata(points_array, values, (grid_x, grid_y), method='linear', fill_value=min_val)
                grid_z[nan_mask] = grid_z_linear[nan_mask]
            
            # Fallback a nearest para cualquier NaN restante
            nan_mask = np.isnan(grid_z)
            if nan_mask.any():
                grid_z_nearest = griddata(points_array, values, (grid_x, grid_y), method='nearest')
                grid_z[nan_mask] = grid_z_nearest[nan_mask]
            
        except Exception as e:
            print(f"⚠️ Error con interpolación griddata: {e}, usando RBF")
            try:
                # Fallback a RBF
                rbfi = Rbf(x_coords, y_coords, values, function='linear', smooth=0.5)
                grid_z = rbfi(grid_x, grid_y)
            except Exception as e2:
                print(f"❌ Error con RBF: {e2}, creando heatmap simple")
                return self._create_fallback_heatmap(points, width, height, min_val, max_val, metric)
        
        # Normalizar valores
        grid_z_clipped = np.clip(grid_z, min_val, max_val)
        normalized_grid = (grid_z_clipped - min_val) / (max_val - min_val)
        
        # Aplicar colormap según métrica
        cmap = self._get_colormap_for_metric(metric)
        
        # Invertir si es necesario (para latencia)
        if metric in ["ping", "jitter"]:
            normalized_grid = 1.0 - normalized_grid
        
        # Generar colores RGBA
        colored_grid_rgba = cmap(normalized_grid)
        colored_grid_rgba = (colored_grid_rgba * 255).astype(np.uint8)
        
        # Crear máscara alpha más sofisticada
        alpha_channel = self._create_advanced_alpha_mask(grid_x, grid_y, x_coords, y_coords, width, height)
        
        # Aplicar alpha
        colored_grid_rgba[:, :, 3] = alpha_channel
        
        # Crear imagen y redimensionar con interpolación de alta calidad
        heatmap_img = Image.fromarray(colored_grid_rgba, 'RGBA')
        
        # Redimensionar usando LANCZOS para máxima calidad
        final_img = heatmap_img.resize((width, height), Image.Resampling.LANCZOS)
        
        print(f"✅ Heatmap generado exitosamente ({width}x{height})")
        return final_img
    
    def _get_colormap_for_metric(self, metric: str):
        """Retorna el colormap apropiado para la métrica"""
        if metric in ["rssi", "snr"]:
            return self.colormap_rssi
        elif metric in ["download", "upload"]:
            return self.colormap_speed
        elif metric in ["ping", "jitter"]:
            return self.colormap_latency
        else:
            return self.colormap_rssi  # Por defecto
    
    def _create_advanced_alpha_mask(self, grid_x: np.ndarray, grid_y: np.ndarray,
                                   x_coords: Tuple, y_coords: Tuple, 
                                   img_width: int, img_height: int) -> np.ndarray:
        """Crea máscara alpha avanzada con gradiente suave"""
        
        alpha_channel = np.zeros_like(grid_x, dtype=np.uint8)
        
        # Calcular influencia máxima basada en dispersión de puntos
        max_influence = min(img_width, img_height) / 4
        
        # Calcular distancia mínima para cada punto de la grilla
        for i in range(grid_x.shape[0]):
            for j in range(grid_x.shape[1]):
                gx, gy = grid_x[i, j], grid_y[i, j]
                
                # Distancia al punto de medición más cercano
                min_dist = float('inf')
                for px, py in zip(x_coords, y_coords):
                    dist = np.sqrt((gx - px)**2 + (gy - py)**2)
                    min_dist = min(min_dist, dist)
                
                # Calcular alpha con gradiente suave
                if min_dist < max_influence:
                    # Función suave para transición alpha
                    alpha_factor = 1 - (min_dist / max_influence)**2
                    alpha = int(255 * alpha_factor * 0.85)  # 85% opacidad máxima
                    alpha_channel[i, j] = max(60, alpha)  # Alpha mínimo de 60
                else:
                    # Área con poca confianza
                    alpha_channel[i, j] = 20
        
        return alpha_channel
    
    def _create_fallback_heatmap(self, points: List[Tuple], width: int, height: int,
                                min_val: float, max_val: float, metric: str) -> Image.Image:
        """Crea heatmap simple como fallback mejorado"""
        
        img_array = np.zeros((height, width, 4), dtype=np.uint8)
        
        # Radio de influencia adaptativo
        radius = min(width, height) // 6
        
        for x, y, value in points:
            # Normalizar valor
            if max_val > min_val:
                normalized_value = (value - min_val) / (max_val - min_val)
            else:
                normalized_value = 0.5
            
            # Invertir para latencia
            if metric in ["ping", "jitter"]:
                normalized_value = 1 - normalized_value
            
            # Determinar color basado en valor normalizado
            if normalized_value >= 0.75:
                color = [76, 175, 80]    # Verde (excelente)
            elif normalized_value >= 0.5:
                color = [139, 195, 74]   # Verde claro (bueno)
            elif normalized_value >= 0.25:
                color = [255, 193, 7]    # Amarillo (regular)
            else:
                color = [244, 67, 54]    # Rojo (malo)
            
            # Dibujar círculo de influencia con gradiente
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    px, py = int(x + dx), int(y + dy)
                    
                    if 0 <= px < width and 0 <= py < height:
                        dist = np.sqrt(dx*dx + dy*dy)
                        
                        if dist <= radius:
                            # Gradiente suave
                            alpha_factor = max(0, 1 - (dist / radius)**2)
                            alpha = int(255 * alpha_factor * 0.7)
                            
                            # Mezcla con color existente
                            current_alpha = img_array[py, px, 3]
                            if alpha > current_alpha:
                                blend_factor = alpha / 255.0
                                img_array[py, px, :3] = (
                                    np.array(color) * blend_factor + 
                                    img_array[py, px, :3] * (1 - blend_factor)
                                ).astype(np.uint8)
                                img_array[py, px, 3] = max(current_alpha, alpha)
        
        return Image.fromarray(img_array, 'RGBA')
    
    def get_metric_info(self, metric: str) -> dict:
        """Retorna información sobre la métrica para la leyenda"""
        metric_info = {
            'rssi': {
                'name': 'Señal WiFi',
                'unit': 'dBm',
                'ranges': ['-90', '-70', '-50', '-30'],
                'labels': ['Pobre', 'Regular', 'Bueno', 'Excelente'],
                'colors': ['#2196F3', '#F44336', '#FFC107', '#4CAF50']
            },
            'snr': {
                'name': 'Relación Señal/Ruido',
                'unit': 'dB',
                'ranges': ['0', '15', '30', '45+'],
                'labels': ['Malo', 'Regular', 'Bueno', 'Excelente'],
                'colors': ['#2196F3', '#F44336', '#FFC107', '#4CAF50']
            },
            'download': {
                'name': 'Velocidad Descarga',
                'unit': 'Mbps',
                'ranges': ['0', '25', '50', '100+'],
                'labels': ['Lento', 'Regular', 'Bueno', 'Excelente'],
                'colors': ['#F44336', '#FFC107', '#8BC34A', '#4CAF50']
            },
            'upload': {
                'name': 'Velocidad Subida',
                'unit': 'Mbps',
                'ranges': ['0', '10', '25', '50+'],
                'labels': ['Lento', 'Regular', 'Bueno', 'Excelente'],
                'colors': ['#F44336', '#FFC107', '#8BC34A', '#4CAF50']
            },
            'ping': {
                'name': 'Latencia',
                'unit': 'ms',
                'ranges': ['0', '50', '100', '200+'],
                'labels': ['Excelente', 'Bueno', 'Regular', 'Malo'],
                'colors': ['#4CAF50', '#FFC107', '#FF9800', '#F44336']
            },
            'jitter': {
                'name': 'Jitter',
                'unit': 'ms',
                'ranges': ['0', '5', '20', '50+'],
                'labels': ['Excelente', 'Bueno', 'Regular', 'Malo'],
                'colors': ['#4CAF50', '#FFC107', '#FF9800', '#F44336']
            }
        }
        
        return metric_info.get(metric, metric_info['rssi'])