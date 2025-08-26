#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .pdf_generator import PDFReportGenerator

# Crear alias para compatibilidad
ReportGenerator = PDFReportGenerator

__all__ = [
    'ReportGenerator',
    'PDFReportGenerator'
]