#!/usr/bin/env python3
"""
PDF Generator for AI Risk Assessment Reports
Converts HTML reports to professional PDF documents
"""

import os
import tempfile
from typing import Any
import yaml
from datetime import datetime

# Try to import WeasyPrint, fall back gracefully if not available
WEASYPRINT_AVAILABLE = False
try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError) as e:
    print(f"WeasyPrint not available: {e}")
    print("PDF generation will use fallback method")

class PDFGenerator:
    def __init__(self, scoring_file: str = 'scoring.yaml'):
        """Initialize PDF generator with configuration"""
        with open(scoring_file, 'r', encoding='utf-8') as f:
            self.scoring_config = yaml.safe_load(f)
        
        self.risk_styling = self.scoring_config['risk_styling']
        self.weasyprint_available = WEASYPRINT_AVAILABLE

    def generate_pdf_report(self, assessment: Any, html_content: str) -> bytes:
        """
        Generate PDF from HTML report content
        Returns PDF as bytes for download or email attachment
        """
        if not self.weasyprint_available:
            # Fallback: Return HTML content as bytes with instructions
            fallback_html = self._create_fallback_html(assessment, html_content)
            return fallback_html.encode('utf-8')
        
        try:
            # Create PDF-optimized CSS
            pdf_css = self._get_pdf_css(assessment)
            
            # Clean HTML for PDF generation
            pdf_html = self._prepare_html_for_pdf(html_content)
            
            # Generate PDF
            html_doc = HTML(string=pdf_html, base_url='.')
            css_doc = CSS(string=pdf_css)
            
            # Create PDF bytes
            pdf_bytes = html_doc.write_pdf(stylesheets=[css_doc])
            
            return pdf_bytes
            
        except Exception as e:
            raise Exception(f"PDF generation failed: {str(e)}")

    def save_pdf_to_file(self, assessment: Any, html_content: str, filename: str = None) -> str:
        """
        Save PDF to file and return file path
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = assessment.workflow_name.replace(' ', '_').replace('/', '_')
            extension = '.html' if not self.weasyprint_available else '.pdf'
            filename = f'ai_risk_report_{safe_name}_{timestamp}{extension}'
        
        content_bytes = self.generate_pdf_report(assessment, html_content)
        
        # Save to temporary file
        mode = 'w' if not self.weasyprint_available else 'wb'
        encoding = 'utf-8' if not self.weasyprint_available else None
        
        temp_file = tempfile.NamedTemporaryFile(
            mode=mode, 
            suffix='.html' if not self.weasyprint_available else '.pdf', 
            delete=False,
            encoding=encoding
        )
        
        if not self.weasyprint_available:
            temp_file.write(content_bytes.decode('utf-8'))
        else:
            temp_file.write(content_bytes)
        
        temp_file.close()
        
        return temp_file.name

    def _create_fallback_html(self, assessment: Any, html_content: str) -> str:
        """Create print-optimized HTML when PDF generation isn't available"""
        fallback_notice = '''
        <div style="background: #fff3cd; border: 2px solid #ffc107; padding: 20px; margin: 20px 0; border-radius: 10px; text-align: center;">
            <h3 style="color: #856404; margin: 0 0 10px 0;">📄 Print-Ready Report</h3>
            <p style="color: #856404; margin: 0; font-size: 14px;">
                <strong>PDF generation requires additional system libraries.</strong><br>
                This is a print-optimized HTML version. Use your browser's "Print to PDF" feature for a PDF copy.
            </p>
        </div>
        '''
        
        # Add print CSS for better formatting
        print_css = '''
        <style media="print">
            body { background: white !important; }
            .container { box-shadow: none !important; }
            @page { margin: 1cm; }
            .no-print { display: none !important; }
        </style>
        '''
        
        # Insert notice and print CSS
        html_content = html_content.replace('<body>', f'<body>{fallback_notice}')
        html_content = html_content.replace('</head>', f'{print_css}</head>')
        
        # Remove interactive elements
        html_content = html_content.replace('onmouseover=', 'data-mouseover=')
        html_content = html_content.replace('onmouseout=', 'data-mouseout=')
        html_content = html_content.replace('onclick=', 'data-onclick=')
        
        return html_content

    def _prepare_html_for_pdf(self, html_content: str) -> str:
        """Prepare HTML content for PDF generation"""
        # Remove interactive elements that don't work in PDF
        html_content = html_content.replace('onmouseover=', 'data-mouseover=')
        html_content = html_content.replace('onmouseout=', 'data-mouseout=')
        html_content = html_content.replace('onclick=', 'data-onclick=')
        
        # Remove download button (not needed in PDF)
        import re
        html_content = re.sub(r'<div[^>]*position:\s*fixed[^>]*>.*?</div>', '', html_content, flags=re.DOTALL)
        
        return html_content

    def _get_pdf_css(self, assessment: Any) -> str:
        """Generate PDF-specific CSS styling"""
        risk_style = self.risk_styling.get(assessment.overall_risk, self.risk_styling['medium'])
        
        return f"""
        @page {{
            size: A4;
            margin: 1cm;
            @bottom-center {{
                content: "AI Risk Assessment Report | Page " counter(page) " of " counter(pages);
                font-size: 10px;
                color: #666;
            }}
        }}
        
        body {{
            font-family: 'Helvetica', 'Arial', sans-serif;
            font-size: 12px;
            line-height: 1.4;
            color: #333;
            margin: 0;
        }}
        
        .report-container {{
            max-width: none;
            margin: 0;
            box-shadow: none;
        }}
        
        .report-header {{
            background: {risk_style['color']} !important;
            color: white !important;
            padding: 20px;
            text-align: center;
            break-inside: avoid;
        }}
        
        .report-title {{
            font-size: 24px;
            font-weight: bold;
            margin: 0 0 10px 0;
        }}
        
        .report-subtitle {{
            font-size: 16px;
            opacity: 0.9;
            margin: 0;
        }}
        
        .risk-overview {{
            page-break-inside: avoid;
            background: {risk_style['bg']} !important;
            border: 2px solid {risk_style['color']} !important;
            padding: 20px;
            margin: 20px 0;
            text-align: center;
        }}
        
        .risk-level {{
            font-size: 20px;
            font-weight: bold;
            color: {risk_style['color']} !important;
            margin-bottom: 10px;
        }}
        
        .section-title {{
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            margin: 20px 0 15px 0;
            border-bottom: 2px solid {risk_style['color']};
            padding-bottom: 5px;
        }}
        
        .dimensions-grid {{
            display: block;
        }}
        
        .dimension-card {{
            page-break-inside: avoid;
            background: white;
            border: 1px solid #ddd;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid {risk_style['color']};
        }}
        
        .recommendation-item {{
            page-break-inside: avoid;
            background: white;
            border-left: 4px solid {risk_style['color']};
            padding: 12px;
            margin: 8px 0;
            display: flex;
            align-items: flex-start;
            gap: 12px;
        }}
        
        .reasoning-section {{
            page-break-inside: avoid;
            background: #f8f9fa;
            padding: 20px;
            margin: 20px 0;
        }}
        
        .reasoning-card {{
            page-break-inside: avoid;
            background: white;
            border: 1px solid #ddd;
            padding: 15px;
            margin: 10px 0;
        }}
        
        .reasoning-question {{
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 8px;
        }}
        
        .reasoning-answer {{
            color: #555;
            font-style: italic;
            padding: 8px;
            background: #f9f9f9;
            border-left: 3px solid {risk_style['color']};
        }}
        
        /* Hide interactive elements */
        [data-mouseover], [data-onclick] {{
            pointer-events: none;
        }}
        
        /* Print-specific adjustments */
        .report-footer {{
            background: #2c3e50 !important;
            color: white !important;
            padding: 15px;
            text-align: center;
            page-break-inside: avoid;
        }}
        """

    def get_system_requirements_info(self) -> str:
        """Get information about system requirements for PDF generation"""
        return """
        # WeasyPrint System Requirements
        
        WeasyPrint requires system libraries for full PDF generation. 
        
        ## macOS Installation:
        ```bash
        # Install system libraries using Homebrew
        brew install pango glib gdk-pixbuf libffi
        
        # Then reinstall WeasyPrint
        pip uninstall weasyprint
        pip install weasyprint
        ```
        
        ## Ubuntu/Debian:
        ```bash
        sudo apt-get install build-essential python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
        ```
        
        ## Current Status:
        WeasyPrint Available: {}
        Fallback Mode: Print-optimized HTML
        """.format("Yes" if self.weasyprint_available else "No") 