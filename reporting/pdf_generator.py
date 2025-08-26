#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📄 PDF GENERATOR - Site Surveyor Pro v16.0
Generador de reportes PDF MEJORADO v2
"""

from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.platypus import PageBreak, KeepTogether
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import tempfile

class PDFReportGenerator:
    """Generador de reportes PDF MEJORADO v2"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Configura estilos personalizados"""
        # Estilo para títulos principales
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=18,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        # Estilo para subtítulos
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading1'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkgreen
        ))
        
    def generate_report(self, 
                       survey_points: List = None,
                       networks: List = None, 
                       project_info: Dict[str, Any] = None,
                       output_path: str = None) -> str:
        """
        Genera reporte PDF completo MEJORADO
        
        Returns:
            str: Ruta del archivo PDF generado
        """
        
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"site_survey_report_{timestamp}.pdf"
        
        try:
            print(f"📄 Generando reporte PDF MEJORADO: {output_path}")
            
            # Valores por defecto si no se proporcionan
            survey_points = survey_points or []
            networks = networks or []
            project_info = project_info or {}
            
            # Crear documento
            doc = SimpleDocTemplate(
                output_path, 
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            story = []
            
            # Portada
            story.extend(self._create_cover_page(project_info))
            story.append(PageBreak())
            
            # Resumen ejecutivo
            story.extend(self._create_executive_summary(survey_points, networks))
            story.append(Spacer(1, 20))
            
            # Tabla de puntos de medición
            if survey_points:
                story.extend(self._create_survey_points_table_v2(survey_points))
                story.append(Spacer(1, 20))
            
            # Lista de redes detectadas
            if networks:
                story.extend(self._create_networks_table_v2(networks))
                story.append(Spacer(1, 20))
            
            # Análisis y recomendaciones
            story.extend(self._create_analysis_section_v2(survey_points, networks))
            
            # Construir PDF
            doc.build(story)
            
            print(f"✅ Reporte PDF MEJORADO generado exitosamente: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ Error generando reporte PDF: {e}")
            import traceback
            traceback.print_exc()
            return ""
    
    def _create_cover_page(self, project_info: Dict[str, Any]) -> List:
        """Crea la página de portada"""
        elements = []
        
        # Título principal
        title = Paragraph("REPORTE DE SITE SURVEY WiFi", self.styles['CustomTitle'])
        elements.append(title)
        elements.append(Spacer(1, 30))
        
        # Logo/Información de la empresa (placeholder)
        company_info = Paragraph(
            "<b>Site Surveyor Pro v15.1</b><br/>Análisis Profesional de Redes WiFi",
            self.styles['Normal']
        )
        elements.append(company_info)
        elements.append(Spacer(1, 40))
        
        # Información del proyecto
        project_name = project_info.get('name', 'Proyecto sin nombre')
        client_name = project_info.get('client_name', 'Cliente no especificado')
        location = project_info.get('location', project_info.get('site_name', 'Ubicación no especificada'))
        
        project_table_data = [
            ['Proyecto:', project_name],
            ['Cliente:', client_name],
            ['Ubicación:', location],
            ['Fecha:', datetime.now().strftime("%d/%m/%Y")],
            ['Hora:', datetime.now().strftime("%H:%M:%S")],
            ['Generado por:', 'Site Surveyor Pro v15.1']
        ]
        
        project_table = Table(project_table_data, colWidths=[2*inch, 4*inch])
        project_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(project_table)
        elements.append(Spacer(1, 50))
        
        # Disclaimer
        disclaimer = Paragraph(
            "<i>Este reporte contiene información técnica sobre la cobertura y "
            "rendimiento de las redes WiFi en el área analizada. Los datos fueron "
            "recopilados usando Site Surveyor Pro v15.1.</i>",
            self.styles['Normal']
        )
        elements.append(disclaimer)
        
        return elements
    
    def _create_executive_summary(self, survey_points: List, networks: List) -> List:
        """Crea el resumen ejecutivo MEJORADO"""
        elements = []
        
        elements.append(Paragraph("RESUMEN EJECUTIVO", self.styles['CustomHeading']))
        
        # Estadísticas generales
        total_points = len(survey_points)
        total_networks = len(networks)
        
        # Calcular métricas promedio
        avg_rssi = 0
        avg_speed_down = 0
        avg_speed_up = 0
        avg_latency = 0
        
        if survey_points:
            rssi_values = []
            speed_down_values = []
            speed_up_values = []
            latency_values = []
            
            for point in survey_points:
                # Verificar si tiene avg_signal_strength
                if hasattr(point, 'avg_signal_strength') and point.avg_signal_strength:
                    rssi_values.append(point.avg_signal_strength)
                elif hasattr(point, 'networks') and point.networks:
                    # Calcular promedio de señal manualmente
                    signals = [net.signal for net in point.networks if hasattr(net, 'signal')]
                    if signals:
                        rssi_values.append(sum(signals) / len(signals))
                
                # iPerf results
                if hasattr(point, 'iperf_results') and point.iperf_results:
                    iperf = point.iperf_results
                    if hasattr(iperf, 'download_speed') and iperf.download_speed:
                        speed_down_values.append(iperf.download_speed)
                    if hasattr(iperf, 'upload_speed') and iperf.upload_speed:
                        speed_up_values.append(iperf.upload_speed)
                    if hasattr(iperf, 'latency') and iperf.latency:
                        latency_values.append(iperf.latency)
            
            avg_rssi = sum(rssi_values) / len(rssi_values) if rssi_values else 0
            avg_speed_down = sum(speed_down_values) / len(speed_down_values) if speed_down_values else 0
            avg_speed_up = sum(speed_up_values) / len(speed_up_values) if speed_up_values else 0
            avg_latency = sum(latency_values) / len(latency_values) if latency_values else 0
        
        # Crear tabla de resumen
        summary_data = [
            ['Métrica', 'Valor', 'Evaluación'],
            ['Total de puntos medidos', f"{total_points}", "✅" if total_points >= 3 else "⚠️"],
            ['Total de redes detectadas', f"{total_networks}", "✅" if total_networks > 0 else "❌"],
            ['RSSI promedio', f"{avg_rssi:.1f} dBm" if avg_rssi else "N/A", 
             "✅" if avg_rssi > -70 else "⚠️" if avg_rssi > -80 else "❌" if avg_rssi else "N/A"],
            ['Velocidad descarga promedio', f"{avg_speed_down:.1f} Mbps" if avg_speed_down else "N/A",
             "✅" if avg_speed_down > 50 else "⚠️" if avg_speed_down > 10 else "❌" if avg_speed_down else "N/A"],
            ['Velocidad subida promedio', f"{avg_speed_up:.1f} Mbps" if avg_speed_up else "N/A",
             "✅" if avg_speed_up > 10 else "⚠️" if avg_speed_up > 5 else "❌" if avg_speed_up else "N/A"],
            ['Latencia promedio', f"{avg_latency:.1f} ms" if avg_latency else "N/A",
             "✅" if avg_latency < 50 else "⚠️" if avg_latency < 100 else "❌" if avg_latency else "N/A"],
        ]
        
        summary_table = Table(summary_data, colWidths=[2.5*inch, 1.5*inch, 1*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_survey_points_table_v2(self, survey_points: List) -> List:
        """Crea la tabla de puntos de medición MEJORADA"""
        elements = []
        
        elements.append(Paragraph("PUNTOS DE MEDICIÓN", self.styles['CustomHeading']))
        
        # Crear datos de la tabla
        table_data = [['#', 'Posición (x,y)', 'Redes', 'RSSI Prom.', 'RSSI Max', 'Descarga', 'Subida', 'Ping']]
        
        for i, point in enumerate(survey_points, 1):
            try:
                # Extraer datos de manera segura
                pos_x = getattr(point, 'x', 0)
                pos_y = getattr(point, 'y', 0)
                position = f"({int(pos_x)}, {int(pos_y)})"
                
                # Número de redes
                networks = getattr(point, 'networks', [])
                network_count = len(networks)
                
                # RSSI promedio y máximo
                if hasattr(point, 'avg_signal_strength'):
                    avg_rssi = point.avg_signal_strength
                    max_rssi = getattr(point, 'max_signal_strength', 0)
                elif networks:
                    signals = [net.signal for net in networks if hasattr(net, 'signal')]
                    avg_rssi = sum(signals) / len(signals) if signals else 0
                    max_rssi = max(signals) if signals else 0
                else:
                    avg_rssi = max_rssi = 0
                
                avg_rssi_str = f"{avg_rssi:.1f}" if avg_rssi else "N/A"
                max_rssi_str = f"{max_rssi:.1f}" if max_rssi else "N/A"
                
                # Datos de iPerf
                iperf = getattr(point, 'iperf_results', None)
                if iperf:
                    download_str = f"{getattr(iperf, 'download_speed', 0):.1f}"
                    upload_str = f"{getattr(iperf, 'upload_speed', 0):.1f}"
                    ping_str = f"{getattr(iperf, 'latency', 0):.1f}"
                else:
                    download_str = upload_str = ping_str = "N/A"
                
                table_data.append([
                    str(i),
                    position,
                    str(network_count),
                    avg_rssi_str,
                    max_rssi_str,
                    download_str,
                    upload_str,
                    ping_str
                ])
                
            except Exception as e:
                print(f"⚠️ Error procesando punto {i}: {e}")
                table_data.append([str(i), "Error", "0", "N/A", "N/A", "N/A", "N/A", "N/A"])
        
        # Crear tabla
        points_table = Table(table_data, colWidths=[0.4*inch, 1*inch, 0.6*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.6*inch])
        points_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(points_table)
        
        return elements
    
    def _create_networks_table_v2(self, networks: List) -> List:
        """Crea la tabla de redes detectadas MEJORADA"""
        elements = []
        
        elements.append(Paragraph("REDES WiFi DETECTADAS", self.styles['CustomHeading']))
        
        # Limitar a las primeras 25 redes para no hacer el reporte muy largo
        display_networks = networks[:25]
        
        network_data = [['SSID', 'Canal', 'Banda', 'Seguridad', 'RSSI', 'Calidad']]
        
        for net in display_networks:
            try:
                ssid = getattr(net, 'ssid', 'Unknown')[:20]  # Truncar SSID largo
                channel = str(getattr(net, 'channel', 0))
                
                # Determinar banda
                freq = getattr(net, 'frequency', 2400)
                band = "5GHz" if freq > 5000 else "2.4GHz"
                
                security = getattr(net, 'security', 'Unknown')[:12]
                signal = getattr(net, 'signal', 0)
                
                # Calidad de señal
                if signal >= -50:
                    quality = "Excelente"
                elif signal >= -60:
                    quality = "Muy buena"
                elif signal >= -70:
                    quality = "Buena"
                elif signal >= -80:
                    quality = "Regular"
                else:
                    quality = "Pobre"
                
                network_data.append([
                    ssid,
                    channel,
                    band,
                    security,
                    f"{signal} dBm",
                    quality
                ])
            except Exception as e:
                print(f"⚠️ Error procesando red: {e}")
                continue
        
        networks_table = Table(network_data, colWidths=[1.3*inch, 0.5*inch, 0.6*inch, 0.9*inch, 0.7*inch, 0.8*inch])
        networks_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(networks_table)
        
        if len(networks) > 25:
            note = Paragraph(
                f"<i>Nota: Se muestran las primeras 25 redes de un total de {len(networks)} detectadas.</i>",
                self.styles['Normal']
            )
            elements.append(Spacer(1, 10))
            elements.append(note)
        
        return elements
    
    def _create_analysis_section_v2(self, survey_points: List, networks: List) -> List:
        """Crea la sección de análisis y recomendaciones MEJORADA"""
        elements = []
        
        elements.append(Paragraph("ANÁLISIS TÉCNICO Y RECOMENDACIONES", self.styles['CustomHeading']))
        
        # Análisis de cobertura
        analysis_text = []
        analysis_text.append("<b>1. Análisis de Cobertura WiFi:</b>")
        
        if survey_points:
            # Analizar distribución de RSSI
            all_signals = []
            for point in survey_points:
                networks = getattr(point, 'networks', [])
                for net in networks:
                    if hasattr(net, 'signal'):
                        all_signals.append(net.signal)
            
            if all_signals:
                excellent_count = len([x for x in all_signals if x >= -50])
                good_count = len([x for x in all_signals if -70 <= x < -50])
                fair_count = len([x for x in all_signals if -80 <= x < -70])
                poor_count = len([x for x in all_signals if x < -80])
                total_measurements = len(all_signals)
                
                analysis_text.append(f"• Mediciones con señal excelente (≥-50 dBm): {excellent_count} ({excellent_count/total_measurements*100:.1f}%)")
                analysis_text.append(f"• Mediciones con señal buena (-50 a -70 dBm): {good_count} ({good_count/total_measurements*100:.1f}%)")
                analysis_text.append(f"• Mediciones con señal regular (-70 a -80 dBm): {fair_count} ({fair_count/total_measurements*100:.1f}%)")
                analysis_text.append(f"• Mediciones con señal pobre (<-80 dBm): {poor_count} ({poor_count/total_measurements*100:.1f}%)")
        
        analysis_text.append("")
        analysis_text.append("<b>2. Análisis de Canales y Bandas:</b>")
        
        if networks:
            # Analizar uso de canales
            channel_usage = {}
            band_usage = {"2.4GHz": 0, "5GHz": 0}
            
            for net in networks:
                if hasattr(net, 'channel'):
                    channel = net.channel
                    channel_usage[channel] = channel_usage.get(channel, 0) + 1
                
                if hasattr(net, 'frequency'):
                    band = "5GHz" if net.frequency > 5000 else "2.4GHz"
                    band_usage[band] += 1
            
            # Distribución por bandas
            total_networks = len(networks)
            analysis_text.append(f"• Redes en 2.4GHz: {band_usage['2.4GHz']} ({band_usage['2.4GHz']/total_networks*100:.1f}%)")
            analysis_text.append(f"• Redes en 5GHz: {band_usage['5GHz']} ({band_usage['5GHz']/total_networks*100:.1f}%)")
            
            # Canales más utilizados
            most_used_channels = sorted(channel_usage.items(), key=lambda x: x[1], reverse=True)[:5]
            analysis_text.append("• Canales más utilizados:")
            for channel, count in most_used_channels:
                analysis_text.append(f"  - Canal {channel}: {count} redes")
        
        analysis_text.append("")
        analysis_text.append("<b>3. Análisis de Rendimiento:</b>")
        
        # Analizar rendimiento iPerf
        if survey_points:
            speed_tests = []
            latency_tests = []
            
            for point in survey_points:
                iperf = getattr(point, 'iperf_results', None)
                if iperf:
                    if hasattr(iperf, 'download_speed') and iperf.download_speed > 0:
                        speed_tests.append(iperf.download_speed)
                    if hasattr(iperf, 'latency') and iperf.latency > 0:
                        latency_tests.append(iperf.latency)
            
            if speed_tests:
                avg_speed = sum(speed_tests) / len(speed_tests)
                min_speed = min(speed_tests)
                max_speed = max(speed_tests)
                analysis_text.append(f"• Velocidad promedio: {avg_speed:.1f} Mbps")
                analysis_text.append(f"• Velocidad mínima: {min_speed:.1f} Mbps")
                analysis_text.append(f"• Velocidad máxima: {max_speed:.1f} Mbps")
            
            if latency_tests:
                avg_latency = sum(latency_tests) / len(latency_tests)
                analysis_text.append(f"• Latencia promedio: {avg_latency:.1f} ms")
        
        analysis_text.append("")
        analysis_text.append("<b>4. Recomendaciones Técnicas:</b>")
        analysis_text.append("• Considere optimizar la ubicación de APs en áreas con señal pobre (<-80 dBm)")
        analysis_text.append("• Evalúe migrar más dispositivos a la banda de 5GHz para reducir congestión")
        analysis_text.append("• Implemente balanceador de carga entre canales para optimizar rendimiento")
        analysis_text.append("• Considere upgrade de equipos si las velocidades están por debajo de 50 Mbps")
        analysis_text.append("• Realice site surveys periódicos para monitorear cambios en el entorno RF")
        analysis_text.append("• Documente la configuración actual para futuras referencias y troubleshooting")
        
        analysis_paragraph = Paragraph("<br/>".join(analysis_text), self.styles['Normal'])
        elements.append(analysis_paragraph)
        
        return elements