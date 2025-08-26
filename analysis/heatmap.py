# analysis/heatmap.py
import numpy as np
from PIL import Image
from scipy.interpolate import Rbf
from matplotlib.colors import LinearSegmentedColormap
from typing import List, Optional, Tuple
from core.data_models import SurveyPoint

class HeatmapGenerator:
    """Generador de mapas de calor para WiFi"""
    
    def __init__(self):
        self.colormap_rssi = self._create_colormap(inverted=False)
        self.colormap_latency = self._create_colormap(inverted=True)
    
    def _create_colormap(self, inverted: bool = False):
        """Crea mapa de colores para WiFi"""
        if inverted:
            colors = [(0.0, "#4CAF50"), (0.33, "#FFC107"), (0.66, "#F44336"), (1.0, "#2196F3")]
        else:
            colors = [(0.0, "#2196F3"), (0.33, "#F44336"), (0.66, "#FFC107"), (1.0, "#4CAF50")]
        return LinearSegmentedColormap.from_list("wifi", colors)
    
    def generate(self, survey_points: List[SurveyPoint], width: int, height: int,
                 target_bssid: Optional[str] = None, metric: str = "rssi") -> Image.Image:
        """Genera heatmap para métrica específica"""
        
        # Extraer puntos y valores
        points = []
        for point in survey_points:
            value = self._extract_metric_value(point, target_bssid, metric)
            if value is not None:
                points.append((point.x, point.y, value))
        
        if len(points) < 3:
            return Image.new('RGBA', (width, height), (0, 0, 0, 0))
        
        # Determinar rangos
        min_val, max_val, invert = self._get_metric_ranges(points, metric)
        
        # Generar heatmap
        return self._generate_heatmap(points, width, height, min_val, max_val, invert)
    
    def _extract_metric_value(self, point: SurveyPoint, target_bssid: Optional[str], 
                             metric: str) -> Optional[float]:
        """Extrae valor de métrica del punto"""
        if metric == "rssi":
            if target_bssid:
                for network in point.scan_data:
                    if network.bssid == target_bssid:
                        return network.rssi
            elif point.strongest_network:
                return point.strongest_network.rssi
        
        elif metric == "snr":
            if target_bssid:
                for network in point.scan_data:
                    if network.bssid == target_bssid:
                        return network.snr
            elif point.strongest_network:
                return point.strongest_network.snr
        
        elif metric == "download" and point.iperf_results:
            return point.iperf_results.download_mbps
        
        elif metric == "upload" and point.iperf_results:
            return point.iperf_results.upload_mbps
        
        elif metric == "ping" and point.iperf_results:
            return point.iperf_results.ping_ms if point.iperf_results.ping_ms < 999 else None
        
        elif metric == "jitter" and point.iperf_results:
            return point.iperf_results.jitter_ms
        
        return None
    
    def _get_metric_ranges(self, points: List[Tuple], metric: str) -> Tuple[float, float, bool]:
        """Obtiene rangos apropiados para la métrica"""
        values = [p[2] for p in points]
        
        if metric == "rssi":
            return -90, -40, False
        elif metric == "snr":
            return 0, max(50, max(values) if values else 50), False
        elif metric in ["download", "upload"]:
            return 0, max(100, max(values) if values else 100), False
        elif metric in ["ping", "jitter"]:
            return 0, min(200, max(values) if values else 200), True
        else:
            return min(values), max(values), False
    
    def _generate_heatmap(self, points: List[Tuple], width: int, height: int,
                         min_val: float, max_val: float, invert: bool) -> Image.Image:
        """Genera el heatmap usando interpolación RBF"""
        x_coords, y_coords, values = zip(*points)
        
        # Verificar rangos válidos
        if max_val <= min_val:
            max_val = min_val + 1
        
        # Crear grid
        grid_resolution = min(100, max(width//4, height//4))
        x_grid = np.linspace(0, width, grid_resolution)
        y_grid = np.linspace(0, height, grid_resolution)
        grid_x, grid_y = np.meshgrid(x_grid, y_grid)
        
        try:
            # Interpolación RBF
            rbfi = Rbf(x_coords, y_coords, values, function='linear', smooth=0.1)
            grid_z = rbfi(grid_x, grid_y)
            
            # Normalizar valores
            grid_z_clipped = np.clip(grid_z, min_val, max_val)
            normalized_grid = (grid_z_clipped - min_val) / (max_val - min_val)
            
            # Aplicar colormap
            cmap = self.colormap_latency if invert else self.colormap_rssi
            colored_grid_rgb = (cmap(normalized_grid)[:, :, :3] * 255).astype(np.uint8)
            
            # Crear máscara alpha
            alpha_channel = self._create_alpha_mask(grid_x, grid_y, x_coords, y_coords)
            
            # Combinar RGB y alpha
            colored_grid_rgba = np.dstack((colored_grid_rgb, alpha_channel))
            
            # Crear imagen y redimensionar
            heatmap_img = Image.fromarray(colored_grid_rgba, 'RGBA')
            return heatmap_img.resize((width, height), Image.Resampling.LANCZOS)
            
        except Exception as e:
            print(f"Error generando heatmap: {e}")
            return self._create_fallback_heatmap(points, width, height, min_val, max_val, invert)
    
    def _create_alpha_mask(self, grid_x: np.ndarray, grid_y: np.ndarray,
                          x_coords: Tuple, y_coords: Tuple) -> np.ndarray:
        """Crea máscara alpha basada en distancia a puntos de medición"""
        alpha_channel = np.zeros_like(grid_x, dtype=np.uint8)
        
        for i in range(grid_x.shape[0]):
            for j in range(grid_x.shape[1]):
                gx, gy = grid_x[i, j], grid_y[i, j]
                
                min_dist = float('inf')
                for px, py in zip(x_coords, y_coords):
                    dist = np.sqrt((gx - px)**2 + (gy - py)**2)
                    min_dist = min(min_dist, dist)
                
                max_influence = (grid_x.max() - grid_x.min()) / 3
                if min_dist < max_influence:
                    alpha = int(255 * (1 - min_dist / max_influence) * 0.8)
                    alpha_channel[i, j] = max(80, alpha)
                else:
                    alpha_channel[i, j] = 30
        
        return alpha_channel
    
    def _create_fallback_heatmap(self, points: List[Tuple], width: int, height: int,
                                min_val: float, max_val: float, invert: bool) -> Image.Image:
        """Crea heatmap simple como fallback"""
        img_array = np.zeros((height, width, 4), dtype=np.uint8)
        
        for x, y, value in points:
            normalized_value = (value - min_val) / (max_val - min_val)
            if invert:
                normalized_value = 1 - normalized_value
            
            # Determinar color
            if normalized_value >= 0.75:
                color = [76, 175, 80]  # Verde
            elif normalized_value >= 0.5:
                color = [255, 193, 7]  # Amarillo
            elif normalized_value >= 0.25:
                color = [244, 67, 54]  # Rojo
            else:
                color = [33, 150, 243]  # Azul
            
            # Dibujar círculo de influencia
            radius = min(width, height) // 8
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    px, py = int(x + dx), int(y + dy)
                    if 0 <= px < width and 0 <= py < height:
                        dist = np.sqrt(dx*dx + dy*dy)
                        if dist <= radius:
                            alpha = int(255 * (1 - dist / radius) * 0.6)
                            current_alpha = img_array[py, px, 3]
                            if alpha > current_alpha:
                                img_array[py, px, :3] = color
                                img_array[py, px, 3] = alpha
        
        return Image.fromarray(img_array, 'RGBA')