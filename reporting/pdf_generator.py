#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📄 PDF GENERATOR - Site Surveyor Pro v16.0
Generador de reportes PDF completo y funcional
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
    """Generador de reportes PDF completo y funcional"""
    
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
        Genera reporte PDF completo
        
        Returns:
            str: Ruta del archivo PDF generado
        """
        
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"site_survey_report_{timestamp}.pdf"
        
        try:
            print(f"📄 Generando reporte PDF: {output_path}")
            
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
                story.extend(self._create_survey_points_table(survey_points))
                story.append(Spacer(1, 20))
            
            # Lista de redes detectadas
            if networks:
                story.extend(self._create_networks_table(networks))
                story.append(Spacer(1, 20))
            
            # Análisis y recomendaciones
            story.extend(self._create_analysis_section(survey_points, networks))
            
            # Construir PDF
            doc.build(story)
            
            print(f"✅ Reporte PDF generado exitosamente: {output_path}")
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
            "<b>Site Surveyor Pro v16.0</b><br/>Análisis Profesional de Redes WiFi",
            self.styles['Normal']
        )
        elements.append(company_info)
        elements.append(Spacer(1, 40))
        
        # Información del proyecto
        project_name = project_info.get('name', 'Proyecto sin nombre')
        client_name = project_info.get('client_name', 'Cliente no especificado')
        location = project_info.get('location', 'Ubicación no especificada')
        
        project_table_data = [
            ['Proyecto:', project_name],
            ['Cliente:', client_name],
            ['Ubicación:', location],
            ['Fecha:', datetime.now().strftime("%d/%m/%Y")],
            ['Hora:', datetime.now().strftime("%H:%M:%S")],
            ['Generado por:', 'Site Surveyor Pro v16.0']
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
            "recopilados usando Site Surveyor Pro v16.0.</i>",
            self.styles['Normal']
        )
        elements.append(disclaimer)
        
        return elements
    
    def _create_executive_summary(self, survey_points: List, networks: List) -> List:
        """Crea el resumen ejecutivo"""
        elements = []
        
        elements.append(Paragraph("RESUMEN EJECUTIVO", self.styles['CustomHeading']))
        
        # Estadísticas generales
        total_points = len(survey_points)
        total_networks = len(networks)
        
        # Calcular métricas promedio
        avg_rssi = 0
        avg_speed_down = 0
        avg_speed_up = 0
        
        if survey_points:
            rssi_values = []
            speed_down_values = []
            speed_up_values = []
            
            for point in survey_points:
                if hasattr(point, 'avg_signal_strength') and point.avg_signal_strength:
                    rssi_values.append(point.avg_signal_strength)
                
                if hasattr(point, 'iperf_results') and point.iperf_results:
                    if hasattr(point.iperf_results, 'download_speed'):
                        speed_down_values.append(point.iperf_results.download_speed)
                    if hasattr(point.iperf_results, 'upload_speed'):
                        speed_up_values.append(point.iperf_results.upload_speed)
            
            avg_rssi = sum(rssi_values) / len(rssi_values) if rssi_values else 0
            avg_speed_down = sum(speed_down_values) / len(speed_down_values) if speed_down_values else 0
            avg_speed_up = sum(speed_up_values) / len(speed_up_values) if speed_up_values else 0
        
        # Crear tabla de resumen
        summary_data = [
            ['Métrica', 'Valor'],
            ['Total de puntos medidos', f"{total_points}"],
            ['Total de redes detectadas', f"{total_networks}"],
            ['RSSI promedio', f"{avg_rssi:.1f} dBm" if avg_rssi else "N/A"],
            ['Velocidad descarga promedio', f"{avg_speed_down:.1f} Mbps" if avg_speed_down else "N/A"],
            ['Velocidad subida promedio', f"{avg_speed_up:.1f} Mbps" if avg_speed_up else "N/A"],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_survey_points_table(self, survey_points: List) -> List:
        """Crea la tabla de puntos de medición"""
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
                network_count = len(getattr(point, 'networks', []))
                
                # RSSI promedio y máximo
                avg_rssi = getattr(point, 'avg_signal_strength', 0)
                max_rssi = getattr(point, 'max_signal_strength', 0)
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
    
    def _create_networks_table(self, networks: List) -> List:
        """Crea la tabla de redes detectadas"""
        elements = []
        
        elements.append(Paragraph("REDES WiFi DETECTADAS", self.styles['CustomHeading']))
        
        # Limitar a las primeras 20 redes para no hacer el reporte muy largo
        display_networks = networks[:20]
        
        network_data = [['SSID', 'Canal', 'Banda', 'Seguridad', 'RSSI', 'Fabricante']]
        
        for net in display_networks:
            try:
                ssid = getattr(net, 'ssid', 'Unknown')[:25]  # Truncar SSID largo
                channel = str(getattr(net, 'channel', 0))
                
                # Determinar banda
                freq = getattr(net, 'frequency', 2400)
                band = "5GHz" if freq > 5000 else "2.4GHz"
                
                security = getattr(net, 'security', 'Unknown')[:15]
                signal = getattr(net, 'signal', 0)
                vendor = getattr(net, 'vendor', 'Unknown')[:15]
                
                network_data.append([
                    ssid,
                    channel,
                    band,
                    security,
                    f"{signal} dBm",
                    vendor
                ])
            except Exception as e:
                print(f"⚠️ Error procesando red: {e}")
                continue
        
        networks_table = Table(network_data, colWidths=[1.5*inch, 0.6*inch, 0.6*inch, 1*inch, 0.8*inch, 1*inch])
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
        
        if len(networks) > 20:
            note = Paragraph(
                f"<i>Nota: Se muestran las primeras 20 redes de un total de {len(networks)} detectadas.</i>",
                self.styles['Normal']
            )
            elements.append(Spacer(1, 10))
            elements.append(note)
        
        return elements
    
    def _create_analysis_section(self, survey_points: List, networks: List) -> List:
        """Crea la sección de análisis y recomendaciones"""
        elements = []
        
        elements.append(Paragraph("ANÁLISIS Y RECOMENDACIONES", self.styles['CustomHeading']))
        
        # Análisis de cobertura
        analysis_text = []
        analysis_text.append("Análisis de Cobertura:")
        
        if survey_points:
            # Analizar distribución de RSSI
            rssi_values = []
            for point in survey_points:
                if hasattr(point, 'avg_signal_strength') and point.avg_signal_strength:
                    rssi_values.append(point.avg_signal_strength)
            
            if rssi_values:
                excellent_count = len([x for x in rssi_values if x >= -50])
                good_count = len([x for x in rssi_values if -70 <= x < -50])
                fair_count = len([x for x in rssi_values if -80 <= x < -70])
                poor_count = len([x for x in rssi_values if x < -80])
                
                analysis_text.append(f"• Puntos con señal excelente (≥-50 dBm): {excellent_count}")
                analysis_text.append(f"• Puntos con señal buena (-50 a -70 dBm): {good_count}")
                analysis_text.append(f"• Puntos con señal regular (-70 a -80 dBm): {fair_count}")
                analysis_text.append(f"• Puntos con señal pobre (<-80 dBm): {poor_count}")
        
        analysis_text.append("")
        analysis_text.append("Análisis de Canales:")
        
        if networks:
            # Analizar uso de canales
            channel_usage = {}
            for net in networks:
                if hasattr(net, 'channel'):
                    channel = net.channel
                    channel_usage[channel] = channel_usage.get(channel, 0) + 1
            
            most_used_channels = sorted(channel_usage.items(), key=lambda x: x[1], reverse=True)[:5]
            analysis_text.append("• Canales más utilizados:")
            for channel, count in most_used_channels:
                analysis_text.append(f"  - Canal {channel}: {count} redes")
        
        analysis_text.append("")
        analysis_text.append("Recomendaciones:")
        analysis_text.append("• Considere ajustar la potencia de transmisión en áreas con baja cobertura")
        analysis_text.append("• Evalúe la posibilidad de agregar puntos de acceso en zonas con señal pobre")
        analysis_text.append("• Optimice la selección de canales para reducir interferencias")
        analysis_text.append("• Realice mediciones periódicas para monitorear el rendimiento")
        
        analysis_paragraph = Paragraph("<br/>".join(analysis_text), self.styles['Normal'])
        elements.append(analysis_paragraph)
        
        return elements
    
    def generate_simple_report(self, data: Dict[str, Any], output_path: str = None) -> str:
        """Genera un reporte simple con datos básicos"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"simple_report_{timestamp}.pdf"
        
        try:
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            story = []
            
            # Título
            story.append(Paragraph("WiFi Site Survey - Reporte Simple", self.styles['CustomTitle']))
            story.append(Spacer(1, 20))
            
            # Información básica
            info_text = f"""
            <b>Proyecto:</b> {data.get('project_name', 'Sin nombre')}<br/>
            <b>Fecha:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}<br/>
            <b>Ubicación:</b> {data.get('location', 'No especificada')}<br/>
            <b>Total de puntos:</b> {data.get('total_points', 0)}<br/>
            <b>Total de redes:</b> {data.get('total_networks', 0)}<br/>
            """
            
            story.append(Paragraph(info_text, self.styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Resumen
            summary_text = """
            Este reporte contiene un resumen básico del site survey WiFi realizado.
            Para obtener información más detallada, genere el reporte completo desde
            la aplicación Site Surveyor Pro.
            """
            
            story.append(Paragraph("Resumen", self.styles['CustomHeading']))
            story.append(Paragraph(summary_text, self.styles['Normal']))
            
            # Construir PDF
            doc.build(story)
            return output_path
            
        except Exception as e:
            print(f"❌ Error generando reporte simple: {e}")
            return ""