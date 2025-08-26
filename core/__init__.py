#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 CORE INIT - Site Surveyor Pro v16.0
Inicialización del módulo core
"""

from .config import Config
from .scanner import WiFiScanner  # ← Corregido: scanner.py no wifi_scanner.py
from .data_models import (
    SurveyPoint, 
    NetworkData, 
    ProjectInfo, 
    IperfResults,
    AccessPoint,
    ServiceMonitorData,
    APPosition
)

# Exportar todas las clases principales
__all__ = [
    'Config',
    'WiFiScanner', 
    'SurveyPoint',
    'NetworkData',
    'ProjectInfo',
    'IperfResults',  # ← Esta era la que faltaba causando el error
    'AccessPoint',
    'ServiceMonitorData',
    'APPosition'  # ← Nueva clase agregada
]

# Información de versión
__version__ = "16.0"
__author__ = "Site Surveyor Pro Team"