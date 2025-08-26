# core/config.py
import json
import os
from pathlib import Path
from typing import Dict, Any

class Config:
    """Configuración simplificada del sistema"""
    
    DEFAULT_CONFIG = {
        'wifi': {
            'scan_interval': 15,
            'scan_timeout': 2.0,
            'min_rssi': -95,
            'noise_floor': -96
        },
        'heatmap': {
            'interpolation': 'cubic',
            'alpha': 0.7,
            'colormap': 'RdYlGn'
        },
        'ap_localization': {
            'min_observations': 3,
            'path_loss_exponent': 3.0,
            'reference_rssi': -40
        },
        'ui': {
            'theme': 'dark',
            'window_size': (1400, 900),
            'font_size': 9
        },
        'iperf': {
            'enabled': True,
            'test_duration': 3,
            'server_auto_start': True
        }
    }
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                    return {**self.DEFAULT_CONFIG, **user_config}
            except:
                pass
        return self.DEFAULT_CONFIG.copy()
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        try:
            return self.config.get(section, {}).get(key, default)
        except:
            return default
    
    def save(self) -> bool:
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except:
            return False
    
    def update(self, section: str, key: str, value: Any) -> None:
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value