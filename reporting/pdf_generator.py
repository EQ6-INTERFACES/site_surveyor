#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📄 PDF GENERATOR - Site Surveyor Pro v16.0
Generador de reportes PDF PREMIUM con GRÁFICAS y DISEÑO MEJORADO
"""

from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.platypus import PageBreak, KeepTogether, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Rect, Circle, String
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics import renderPDF

import os
import io
import matplotlib
matplotlib.use('Agg')  # Backend no interactivo
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional
import tempfile

class PDFReportGenerator:
    """Generador de reportes PDF PREMIUM con gráficas y diseño profesional"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
        # Paleta de colores profesional
        self.colors = {
            'primary': colors.Color(0.2, 0.4, 0.8),      # Azul profesional
            'secondary': colors.Color(0.1, 0.6, 0.3),     # Verde
            'accent': colors.Color(0.8, 0.4, 0.1),        # Naranja
            'danger': colors.Color(0.8, 0.2, 0.2),        # Rojo
            'warning': colors.Color(0.9, 0.6, 0.1),       # Amarillo
            'success': colors.Color(0.2, 0.7, 0.3),       # Verde claro
            'dark': colors.Color(0.2, 0.2, 0.3),          # Gris oscuro
            'light': colors.Color(0.95, 0.95, 0.95),      # Gris claro
        }
        
    def _setup_custom_styles(self):
        """Configura estilos personalizados profesionales"""
        # Título principal
        self.styles.add(ParagraphStyle(
            name='MainTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.Color(0.2, 0.4, 0.8),
            fontName='Helvetica-Bold'
        ))
        
        # Subtítulos
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=15,
            spaceBefore=20,
            textColor=colors.Color(0.1, 0.3, 0.6),
            fontName='Helvetica-Bold',
            borderWidth=0,
            borderColor=colors.Color(0.1, 0.3, 0.6),
            borderPadding=5
        ))
        
        # Párrafos con mejor espaciado
        self.styles.add(ParagraphStyle(
            name='BodyText',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))
        
        # Texto destacado
        self.styles.add(ParagraphStyle(
            name='Highlight',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.Color(0.8, 0.4, 0.1),
            fontName='Helvetica-Bold'
        ))
        
    def generate_report(self, 
                       survey_points: List = None,
                       networks: List = None, 
                       project_info: Dict[str, Any] = None,
                       service_stats: List[Dict] = None,
                       output_path: str = None) -> str:
        """
        Genera reporte PDF PREMIUM con gráficas y análisis completo
        """
        
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"site_survey_premium_report_{timestamp}.pdf"
        
        try:
            print(f"📄 Generando reporte PDF PREMIUM: {output_path}")
            
            # Valores por defecto
            survey_points = survey_points or []
            networks = networks or []
            project_info = project_info or {}
            service_stats = service_stats or []
            
            # Crear documento con márgenes más elegantes
            doc = SimpleDocTemplate(
                output_path, 
                pagesize=A4,
                rightMargin=60,
                leftMargin=60,
                topMargin=60,
                bottomMargin=40
            )
            
            story = []
            
            # 1. Portada profesional
            story.extend(self._create_premium_cover(project_info))
            story.append(PageBreak())
            
            # 2. Resumen ejecutivo con KPIs
            story.extend(self._create_executive_dashboard(survey_points, networks, service_stats))
            story.append(PageBreak())
            
            # 3. Análisis de cobertura WiFi con gráficas
            if survey_points:
                story.extend(self._create_wifi_analysis_section(survey_points, networks))
                story.append(PageBreak())
            
            # 4. Análisis de servicios de red
            if service_stats:
                story.extend(self._create_services_analysis_section(service_stats))
                story.append(PageBreak())
            
            # 5. Detalles técnicos
            story.extend(self._create_technical_details_section(survey_points, networks))
            story.append(PageBreak())
            
            # 6. Recomendaciones y plan de acción
            story.extend(self._create_recommendations_section(survey_points, networks, service_stats))
            
            # Construir PDF
            doc.build(story)
            
            print(f"✅ Reporte PDF PREMIUM generado exitosamente: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ Error generando reporte PDF: {e}")
            import traceback
            traceback.print_exc()
            return ""
    
    def _create_premium_cover(self, project_info: Dict[str, Any]) -> List:
        """Crea una portada profesional y atractiva"""
        elements = []
        
        # Título principal con estilo
        title = Paragraph(
            "REPORTE DE SITE SURVEY<br/>ANÁLISIS PROFESIONAL DE REDES WiFi", 
            self.styles['MainTitle']
        )
        elements.append(title)
        elements.append(Spacer(1, 40))
        
        # Información de la empresa con diseño
        company_info = f"""
        <para align="center" fontSize="14" textColor="#2E5984">
        <b>Site Surveyor Pro v15.1</b><br/>
        <i>Soluciones Profesionales de Análisis de Red</i><br/>
        <font size="10">Reporte generado el {datetime.now().strftime("%d de %B de %Y")}</font>
        </para>
        """
        elements.append(Paragraph(company_info, self.styles['BodyText']))
        elements.append(Spacer(1, 60))
        
        # Información del proyecto en tabla elegante
        project_name = project_info.get('name', 'Proyecto sin nombre')
        client_name = project_info.get('client_name', 'Cliente no especificado')
        location = project_info.get('location', project_info.get('site_name', 'Ubicación no especificada'))
        
        project_data = [
            ['', ''],  # Fila vacía para espaciado
            ['PROYECTO:', project_name],
            ['CLIENTE:', client_name],
            ['UBICACIÓN:', location],
            ['FECHA ANÁLISIS:', datetime.now().strftime("%d/%m/%Y")],
            ['HORA GENERACIÓN:', datetime.now().strftime("%H:%M:%S")],
            ['VERSIÓN SOFTWARE:', 'Site Surveyor Pro v15.1'],
            ['', ''],  # Fila vacía para espaciado
        ]
        
        project_table = Table(project_data, colWidths=[2*inch, 4*inch])
        project_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 1), (0, 6), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('TEXTCOLOR', (0, 1), (0, 6), self.colors['primary']),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 1), (-1, 6), self.colors['light']),
            ('BOX', (0, 1), (-1, 6), 1, self.colors['primary']),
            ('INNERGRID', (0, 1), (-1, 6), 0.5, self.colors['primary']),
        ]))
        
        elements.append(project_table)
        elements.append(Spacer(1, 80))
        
        # Disclaimer profesional
        disclaimer = Paragraph(
            """<para align="justify" fontSize="10" textColor="#666666">
            <i>Este reporte contiene un análisis técnico detallado sobre la cobertura, rendimiento 
            y calidad de las redes WiFi en el área especificada. Los datos fueron recopilados 
            utilizando metodologías estándar de la industria con Site Surveyor Pro v15.1, 
            herramienta certificada para análisis profesional de redes inalámbricas.</i>
            </para>""",
            self.styles['BodyText']
        )
        elements.append(disclaimer)
        
        return elements
    
    def _create_executive_dashboard(self, survey_points: List, networks: List, service_stats: List) -> List:
        """Crea dashboard ejecutivo con KPIs y métricas clave"""
        elements = []
        
        elements.append(Paragraph("RESUMEN EJECUTIVO", self.styles['SectionTitle']))
        
        # KPIs principales
        kpis = self._calculate_kpis(survey_points, networks, service_stats)
        
        # Tabla de KPIs con colores
        kpi_data = [
            ['MÉTRICA', 'VALOR', 'ESTADO', 'OBJETIVO'],
            ['Puntos de medición', f"{kpis['total_points']}", 
             '✅ Completo' if kpis['total_points'] >= 10 else '⚠️ Básico', '≥ 10'],
            ['Cobertura promedio', f"{kpis['avg_rssi']:.1f} dBm", 
             self._get_rssi_status(kpis['avg_rssi']), '≥ -70 dBm'],
            ['Velocidad promedio', f"{kpis['avg_speed']:.1f} Mbps", 
             self._get_speed_status(kpis['avg_speed']), '≥ 50 Mbps'],
            ['Latencia de red', f"{kpis['avg_latency']:.1f} ms", 
             self._get_latency_status(kpis['avg_latency']), '≤ 50 ms'],
            ['Disponibilidad servicios', f"{kpis['service_uptime']:.1f}%", 
             self._get_uptime_status(kpis['service_uptime']), '≥ 99%'],
        ]
        
        kpi_table = Table(kpi_data, colWidths=[2*inch, 1*inch, 1.2*inch, 1*inch])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, self.colors['primary']),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(kpi_table)
        elements.append(Spacer(1, 30))
        
        # Crear gráfica de distribución de señal
        if survey_points:
            chart_image = self._create_signal_distribution_chart(survey_points)
            if chart_image:
                elements.append(Paragraph("Distribución de Calidad de Señal WiFi", self.styles['Highlight']))
                elements.append(chart_image)
                elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_wifi_analysis_section(self, survey_points: List, networks: List) -> List:
        """Sección de análisis WiFi con gráficas detalladas"""
        elements = []
        
        elements.append(Paragraph("ANÁLISIS DETALLADO DE COBERTURA WiFi", self.styles['SectionTitle']))
        
        # Análisis de canales
        if networks:
            elements.append(Paragraph("Distribución por Canales y Bandas", self.styles['Highlight']))
            
            # Gráfica de uso de canales
            channel_chart = self._create_channel_usage_chart(networks)
            if channel_chart:
                elements.append(channel_chart)
                elements.append(Spacer(1, 20))
            
            # Tabla de análisis de canales
            channel_analysis = self._analyze_channel_usage(networks)
            elements.append(Paragraph(channel_analysis, self.styles['BodyText']))
            elements.append(Spacer(1, 20))
        
        # Análisis temporal si hay múltiples puntos
        if len(survey_points) >= 5:
            elements.append(Paragraph("Tendencias de Rendimiento", self.styles['Highlight']))
            
            performance_chart = self._create_performance_trends_chart(survey_points)
            if performance_chart:
                elements.append(performance_chart)
                elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_services_analysis_section(self, service_stats: List[Dict]) -> List:
        """Sección de análisis de servicios de red"""
        elements = []
        
        elements.append(Paragraph("ANÁLISIS DE SERVICIOS DE RED", self.styles['SectionTitle']))
        
        if not service_stats:
            elements.append(Paragraph("No hay datos de servicios disponibles.", self.styles['BodyText']))
            return elements
        
        # Resumen de servicios
        elements.append(Paragraph("Estado de Servicios Monitoreados", self.styles['Highlight']))
        
        # Tabla de servicios
        service_data = [['SERVICIO', 'ESTADO', 'LATENCIA', 'PÉRD. PAQUETES', 'DISPONIBILIDAD']]
        
        for service in service_stats:
            status = '🟢 Activo' if service.get('status') == 'Active' else '🔴 Inactivo'
            latency = f"{service.get('current_latency', 0):.1f} ms"
            packet_loss = f"{service.get('packet_loss', 0):.1f}%"
            
            # Calcular disponibilidad
            total_pings = service.get('total_pings', 1)
            successful = service.get('successful_pings', 0)
            availability = (successful / total_pings * 100) if total_pings > 0 else 0
            
            service_data.append([
                service.get('service_name', 'N/A'),
                status,
                latency,
                packet_loss,
                f"{availability:.1f}%"
            ])
        
        service_table = Table(service_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch, 1*inch])
        service_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['secondary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, self.colors['secondary']),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(service_table)
        elements.append(Spacer(1, 20))
        
        # Gráfica de latencias de servicios
        latency_chart = self._create_service_latency_chart(service_stats)
        if latency_chart:
            elements.append(Paragraph("Comparativa de Latencias por Servicio", self.styles['Highlight']))
            elements.append(latency_chart)
            elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_technical_details_section(self, survey_points: List, networks: List) -> List:
        """Sección de detalles técnicos"""
        elements = []
        
        elements.append(Paragraph("DETALLES TÉCNICOS", self.styles['SectionTitle']))
        
        # Tabla detallada de puntos (primeros 15)
        if survey_points:
            elements.append(Paragraph("Puntos de Medición (Muestra)", self.styles['Highlight']))
            
            points_data = [['#', 'Posición', 'Redes', 'RSSI Prom.', 'Velocidad', 'Latencia']]
            
            for i, point in enumerate(survey_points[:15], 1):
                try:
                    networks_count = len(getattr(point, 'networks', []))
                    
                    # Calcular RSSI promedio
                    networks = getattr(point, 'networks', [])
                    if networks:
                        signals = [net.signal for net in networks if hasattr(net, 'signal')]
                        avg_rssi = sum(signals) / len(signals) if signals else 0
                    else:
                        avg_rssi = 0
                    
                    # Datos iPerf
                    iperf = getattr(point, 'iperf_results', None)
                    speed = f"{getattr(iperf, 'download_speed', 0):.1f}" if iperf else "N/A"
                    latency = f"{getattr(iperf, 'latency', 0):.1f}" if iperf else "N/A"
                    
                    points_data.append([
                        str(i),
                        f"({int(point.x)},{int(point.y)})",
                        str(networks_count),
                        f"{avg_rssi:.1f}" if avg_rssi else "N/A",
                        speed,
                        latency
                    ])
                except Exception as e:
                    points_data.append([str(i), "Error", "0", "N/A", "N/A", "N/A"])
            
            points_table = Table(points_data, colWidths=[0.4*inch, 1*inch, 0.6*inch, 0.8*inch, 0.8*inch, 0.8*inch])
            points_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.colors['dark']),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, self.colors['dark']),
                ('ALTERNATEROWCOLORS', (0, 1), (-1, -1), [colors.white, self.colors['light']]),
            ]))
            
            elements.append(points_table)
            elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_recommendations_section(self, survey_points: List, networks: List, service_stats: List) -> List:
        """Sección de recomendaciones y plan de acción"""
        elements = []
        
        elements.append(Paragraph("RECOMENDACIONES Y PLAN DE ACCIÓN", self.styles['SectionTitle']))
        
        recommendations = []
        
        # Análisis automático de problemas y recomendaciones
        if survey_points:
            # Analizar cobertura
            weak_coverage_areas = self._identify_weak_coverage(survey_points)
            if weak_coverage_areas > 0:
                recommendations.append({
                    'priority': 'Alta',
                    'issue': 'Áreas con cobertura débil detectadas',
                    'recommendation': f'Instalar {weak_coverage_areas} access points adicionales en las zonas identificadas',
                    'impact': 'Mejora significativa en cobertura y experiencia del usuario'
                })
        
        if networks:
            # Analizar congestión de canales
            congested_channels = self._identify_channel_congestion(networks)
            if congested_channels:
                recommendations.append({
                    'priority': 'Media',
                    'issue': f'Congestión detectada en canales: {", ".join(map(str, congested_channels))}',
                    'recommendation': 'Redistribuir APs a canales menos congestionados (1, 6, 11 en 2.4GHz)',
                    'impact': 'Reducción de interferencias y mejora en throughput'
                })
        
        if service_stats:
            # Analizar servicios con problemas
            problematic_services = [s for s in service_stats if s.get('current_latency', 0) > 100]
            if problematic_services:
                service_names = [s.get('service_name', 'N/A') for s in problematic_services]
                recommendations.append({
                    'priority': 'Media',
                    'issue': f'Latencia elevada en: {", ".join(service_names)}',
                    'recommendation': 'Verificar conectividad WAN y configuración de QoS',
                    'impact': 'Mejora en rendimiento de aplicaciones críticas'
                })
        
        # Recomendaciones generales
        recommendations.extend([
            {
                'priority': 'Baja',
                'issue': 'Monitoreo continuo',
                'recommendation': 'Implementar monitoreo 24/7 con alertas automáticas',
                'impact': 'Detección proactiva de problemas'
            },
            {
                'priority': 'Baja',
                'issue': 'Actualización de firmware',
                'recommendation': 'Mantener firmware de APs actualizado',
                'impact': 'Seguridad mejorada y nuevas características'
            }
        ])
        
        # Tabla de recomendaciones
        rec_data = [['PRIORIDAD', 'PROBLEMA IDENTIFICADO', 'RECOMENDACIÓN', 'IMPACTO ESPERADO']]
        
        # Ordenar por prioridad
        priority_order = {'Alta': 1, 'Media': 2, 'Baja': 3}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 99))
        
        for rec in recommendations:
            priority_color = {
                'Alta': '🔴 Alta',
                'Media': '🟡 Media',
                'Baja': '🟢 Baja'
            }.get(rec['priority'], rec['priority'])
            
            rec_data.append([
                priority_color,
                rec['issue'],
                rec['recommendation'],
                rec['impact']
            ])
        
        rec_table = Table(rec_data, colWidths=[0.8*inch, 2*inch, 2.2*inch, 2*inch])
        rec_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['accent']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, self.colors['accent']),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(rec_table)
        elements.append(Spacer(1, 30))
        
        # Conclusión
        conclusion = """
        <para align="justify">
        <b>Conclusión:</b> Este análisis proporciona una visión integral del estado actual 
        de la infraestructura WiFi. Las recomendaciones están priorizadas para maximizar 
        el impacto en la experiencia del usuario y el rendimiento de la red. Se recomienda 
        realizar un seguimiento en 30-60 días para evaluar la efectividad de las mejoras 
        implementadas.
        </para>
        """
        
        elements.append(Paragraph(conclusion, self.styles['BodyText']))
        
        return elements
    
    def _calculate_kpis(self, survey_points: List, networks: List, service_stats: List) -> Dict:
        """Calcula KPIs principales"""
        kpis = {
            'total_points': len(survey_points),
            'total_networks': len(networks),
            'avg_rssi': 0,
            'avg_speed': 0,
            'avg_latency': 0,
            'service_uptime': 0
        }
        
        if survey_points:
            # RSSI promedio
            all_signals = []
            for point in survey_points:
                networks = getattr(point, 'networks', [])
                for net in networks:
                    if hasattr(net, 'signal'):
                        all_signals.append(net.signal)
            
            kpis['avg_rssi'] = sum(all_signals) / len(all_signals) if all_signals else -100
            
            # Velocidad y latencia promedio
            speeds = []
            latencies = []
            for point in survey_points:
                iperf = getattr(point, 'iperf_results', None)
                if iperf:
                    if hasattr(iperf, 'download_speed') and iperf.download_speed > 0:
                        speeds.append(iperf.download_speed)
                    if hasattr(iperf, 'latency') and iperf.latency > 0:
                        latencies.append(iperf.latency)
            
            kpis['avg_speed'] = sum(speeds) / len(speeds) if speeds else 0
            kpis['avg_latency'] = sum(latencies) / len(latencies) if latencies else 0
        
        if service_stats:
            # Uptime promedio de servicios
            uptimes = []
            for service in service_stats:
                total = service.get('total_pings', 1)
                successful = service.get('successful_pings', 0)
                uptime = (successful / total * 100) if total > 0 else 0
                uptimes.append(uptime)
            
            kpis['service_uptime'] = sum(uptimes) / len(uptimes) if uptimes else 0
        
        return kpis
    
    def _get_rssi_status(self, rssi: float) -> str:
        """Retorna estado basado en RSSI"""
        if rssi >= -60:
            return '✅ Excelente'
        elif rssi >= -70:
            return '🟡 Bueno'
        elif rssi >= -80:
            return '🟠 Regular'
        else:
            return '🔴 Pobre'
    
    def _get_speed_status(self, speed: float) -> str:
        """Retorna estado basado en velocidad"""
        if speed >= 100:
            return '✅ Excelente'
        elif speed >= 50:
            return '🟡 Bueno'
        elif speed >= 25:
            return '🟠 Regular'
        else:
            return '🔴 Lento'
    
    def _get_latency_status(self, latency: float) -> str:
        """Retorna estado basado en latencia"""
        if latency <= 20:
            return '✅ Excelente'
        elif latency <= 50:
            return '🟡 Bueno'
        elif latency <= 100:
            return '🟠 Regular'
        else:
            return '🔴 Alto'
    
    def _get_uptime_status(self, uptime: float) -> str:
        """Retorna estado basado en uptime"""
        if uptime >= 99:
            return '✅ Excelente'
        elif uptime >= 95:
            return '🟡 Bueno'
        elif uptime >= 90:
            return '🟠 Regular'
        else:
            return '🔴 Crítico'
    
    def _create_signal_distribution_chart(self, survey_points: List):
        """Crea gráfica de distribución de señal"""
        try:
            # Recopilar datos de señal
            signals = []
            for point in survey_points:
                networks = getattr(point, 'networks', [])
                for net in networks:
                    if hasattr(net, 'signal'):
                        signals.append(net.signal)
            
            if not signals:
                return None
            
            # Crear gráfica con matplotlib
            plt.figure(figsize=(8, 5))
            plt.hist(signals, bins=20, color='#2E5984', alpha=0.7, edgecolor='black')
            plt.title('Distribución de Intensidad de Señal WiFi', fontsize=14, fontweight='bold')
            plt.xlabel('RSSI (dBm)', fontsize=12)
            plt.ylabel('Frecuencia', fontsize=12)
            plt.grid(True, alpha=0.3)
            
            # Líneas de referencia
            plt.axvline(-60, color='green', linestyle='--', label='Excelente')
            plt.axvline(-70, color='orange', linestyle='--', label='Bueno')
            plt.axvline(-80, color='red', linestyle='--', label='Mínimo')
            plt.legend()
            
            plt.tight_layout()
            
            # Guardar como imagen temporal
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
            img_buffer.seek(0)
            
            # Crear Image de ReportLab
            img = Image(img_buffer, width=6*inch, height=3.75*inch)
            
            plt.close()
            return img
            
        except Exception as e:
            print(f"Error creando gráfica de señal: {e}")
            return None
    
    def _create_channel_usage_chart(self, networks: List):
        """Crea gráfica de uso de canales"""
        try:
            # Contar uso de canales
            channel_usage = {}
            for net in networks:
                channel = getattr(net, 'channel', 0)
                channel_usage[channel] = channel_usage.get(channel, 0) + 1
            
            if not channel_usage:
                return None
            
            # Crear gráfica
            channels = list(channel_usage.keys())
            counts = list(channel_usage.values())
            
            plt.figure(figsize=(8, 4))
            bars = plt.bar(channels, counts, color='#1B4F72', alpha=0.8)
            plt.title('Distribución de Redes por Canal', fontsize=14, fontweight='bold')
            plt.xlabel('Canal', fontsize=12)
            plt.ylabel('Número de Redes', fontsize=12)
            plt.grid(True, alpha=0.3, axis='y')
            
            # Destacar canales recomendados
            for i, channel in enumerate(channels):
                if channel in [1, 6, 11]:  # Canales recomendados para 2.4GHz
                    bars[i].set_color('#27AE60')
            
            plt.tight_layout()
            
            # Guardar imagen
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
            img_buffer.seek(0)
            
            img = Image(img_buffer, width=6*inch, height=3*inch)
            plt.close()
            return img
            
        except Exception as e:
            print(f"Error creando gráfica de canales: {e}")
            return None
    
    def _create_performance_trends_chart(self, survey_points: List):
        """Crea gráfica de tendencias de rendimiento"""
        try:
            # Extraer datos temporales
            timestamps = []
            speeds = []
            latencies = []
            
            for point in survey_points:
                if hasattr(point, 'timestamp'):
                    timestamps.append(point.timestamp)
                    
                    iperf = getattr(point, 'iperf_results', None)
                    if iperf:
                        speeds.append(getattr(iperf, 'download_speed', 0))
                        latencies.append(getattr(iperf, 'latency', 0))
                    else:
                        speeds.append(0)
                        latencies.append(0)
            
            if not timestamps:
                return None
            
            # Crear gráfica
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))
            
            # Velocidad
            ax1.plot(range(len(speeds)), speeds, 'b-o', linewidth=2, markersize=4)
            ax1.set_title('Tendencia de Velocidad de Descarga', fontweight='bold')
            ax1.set_ylabel('Velocidad (Mbps)')
            ax1.grid(True, alpha=0.3)
            
            # Latencia
            ax2.plot(range(len(latencies)), latencies, 'r-s', linewidth=2, markersize=4)
            ax2.set_title('Tendencia de Latencia', fontweight='bold')
            ax2.set_ylabel('Latencia (ms)')
            ax2.set_xlabel('Punto de Medición')
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Guardar imagen
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
            img_buffer.seek(0)
            
            img = Image(img_buffer, width=6*inch, height=4.5*inch)
            plt.close()
            return img
            
        except Exception as e:
            print(f"Error creando gráfica de tendencias: {e}")
            return None
    
    def _create_service_latency_chart(self, service_stats: List):
        """Crea gráfica de latencias de servicios"""
        try:
            service_names = []
            latencies = []
            
            for service in service_stats:
                name = service.get('service_name', 'N/A')
                latency = service.get('avg_latency', 0)
                
                service_names.append(name)
                latencies.append(latency)
            
            if not service_names:
                return None
            
            # Crear gráfica de barras horizontales
            plt.figure(figsize=(8, 4))
            colors = ['#27AE60' if l < 50 else '#F39C12' if l < 100 else '#E74C3C' for l in latencies]
            
            bars = plt.barh(service_names, latencies, color=colors, alpha=0.8)
            plt.title('Latencia Promedio por Servicio', fontsize=14, fontweight='bold')
            plt.xlabel('Latencia (ms)', fontsize=12)
            plt.grid(True, alpha=0.3, axis='x')
            
            # Añadir valores en las barras
            for i, (bar, latency) in enumerate(zip(bars, latencies)):
                plt.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, 
                        f'{latency:.1f}ms', ha='left', va='center')
            
            plt.tight_layout()
            
            # Guardar imagen
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
            img_buffer.seek(0)
            
            img = Image(img_buffer, width=6*inch, height=3*inch)
            plt.close()
            return img
            
        except Exception as e:
            print(f"Error creando gráfica de servicios: {e}")
            return None
    
    def _analyze_channel_usage(self, networks: List) -> str:
        """Analiza el uso de canales"""
        channel_usage = {}
        band_usage = {'2.4GHz': 0, '5GHz': 0}
        
        for net in networks:
            channel = getattr(net, 'channel', 0)
            freq = getattr(net, 'frequency', 2400)
            
            channel_usage[channel] = channel_usage.get(channel, 0) + 1
            band = '5GHz' if freq > 5000 else '2.4GHz'
            band_usage[band] += 1
        
        analysis = f"""
        <b>Análisis de Canales:</b><br/>
        • Total de redes: {len(networks)}<br/>
        • Banda 2.4GHz: {band_usage['2.4GHz']} redes ({band_usage['2.4GHz']/len(networks)*100:.1f}%)<br/>
        • Banda 5GHz: {band_usage['5GHz']} redes ({band_usage['5GHz']/len(networks)*100:.1f}%)<br/><br/>
        
        <b>Canales más congestionados:</b><br/>
        """
        
        # Top 3 canales más usados
        sorted_channels = sorted(channel_usage.items(), key=lambda x: x[1], reverse=True)[:3]
        for channel, count in sorted_channels:
            analysis += f"• Canal {channel}: {count} redes<br/>"
        
        return analysis
    
    def _identify_weak_coverage(self, survey_points: List) -> int:
        """Identifica áreas con cobertura débil"""
        weak_areas = 0
        
        for point in survey_points:
            networks = getattr(point, 'networks', [])
            if networks:
                best_signal = max(net.signal for net in networks if hasattr(net, 'signal'))
                if best_signal < -80:
                    weak_areas += 1
        
        return weak_areas
    
    def _identify_channel_congestion(self, networks: List) -> List:
        """Identifica canales congestionados"""
        channel_usage = {}
        
        for net in networks:
            channel = getattr(net, 'channel', 0)
            freq = getattr(net, 'frequency', 2400)
            
            # Solo analizar 2.4GHz donde la congestión es más crítica
            if freq < 5000:
                channel_usage[channel] = channel_usage.get(channel, 0) + 1
        
        # Canales con más de 3 redes se consideran congestionados
        congested = [ch for ch, count in channel_usage.items() if count > 3]
        return congested