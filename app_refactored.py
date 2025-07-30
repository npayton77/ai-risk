#!/usr/bin/env python3
"""
AI Risk Assessment Web Application - Refactored Version
Web frontend for the AI risk assessment tool using YAML configuration
"""

from flask import Flask, render_template_string, request, jsonify, send_file, redirect, url_for, Response
import json
import os
import yaml
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple
import tempfile
from template_generator import TemplateGenerator
from report_generator import ReportGenerator
from pdf_generator import PDFGenerator
from email_sender import EmailSender
from questions_loader import questions_loader
from risk_assessor import RiskAssessment, AIRiskAssessor
from email_handlers import generate_complete_email_report, generate_short_email_report
from static_pages import generate_system_info_page, generate_email_info_page
# Flask Web Application
app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Initialize components
template_generator = TemplateGenerator()
risk_assessor = AIRiskAssessor()
report_generator = ReportGenerator()
pdf_generator = PDFGenerator()
email_sender = EmailSender()

@app.route('/favicon.ico')
def favicon():
    """Serve the custom favicon"""
    try:
        with open('static_favicon.svg', 'r') as f:
            svg_content = f.read()
        return Response(svg_content, mimetype='image/svg+xml')
    except FileNotFoundError:
        # Fallback to a simple data URI favicon if file is missing
        return Response('', status=404)

@app.route('/')
def index():
    """Main assessment form page - now generated dynamically from YAML"""
    html_content = template_generator.generate_assessment_form()
    return render_template_string(html_content)

@app.route('/assess', methods=['POST'])
def assess_risk():
    """Process the risk assessment form"""
    try:
        # Get form data
        workflow_name = request.form.get('workflow_name', '').strip()
        assessor = request.form.get('assessor', '').strip()
        
        autonomy = request.form.get('autonomy')
        oversight = request.form.get('oversight')
        impact = request.form.get('impact')
        orchestration = request.form.get('orchestration')
        data_sensitivity = request.form.get('data_sensitivity')
        
        # Get reasoning
        autonomy_reasoning = request.form.get('autonomy_reasoning', '').strip()
        oversight_reasoning = request.form.get('oversight_reasoning', '').strip()
        impact_reasoning = request.form.get('impact_reasoning', '').strip()
        orchestration_reasoning = request.form.get('orchestration_reasoning', '').strip()
        data_sensitivity_reasoning = request.form.get('data_sensitivity_reasoning', '').strip()
        
        # Validate required fields - check if data_sensitivity is required
        required_fields = [workflow_name, assessor, autonomy, oversight, impact, orchestration]
        if 'data_sensitivity' in risk_assessor.dimension_scores:
            required_fields.append(data_sensitivity)
        
        if not all(required_fields):
            return jsonify({'error': 'All fields are required'}), 400
        
        # Calculate risk
        risk_score, risk_level = risk_assessor.calculate_risk_score(
            autonomy, oversight, impact, orchestration, data_sensitivity
        )
        
        # Generate recommendations
        recommendations = risk_assessor.generate_recommendations(
            risk_level, autonomy, oversight, impact, data_sensitivity
        )
        
        # Create assessment object
        responses_dict = {
            'autonomy_reasoning': autonomy_reasoning or 'Not provided',
            'oversight_reasoning': oversight_reasoning or 'Not provided',
            'impact_reasoning': impact_reasoning or 'Not provided',
            'orchestration_reasoning': orchestration_reasoning or 'Not provided'
        }
        
        # Add data sensitivity if it exists
        if data_sensitivity:
            responses_dict['data_sensitivity_reasoning'] = data_sensitivity_reasoning or 'Not provided'
        
        assessment = RiskAssessment(
            workflow_name=workflow_name,
            assessor=assessor,
            date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            autonomy_level=autonomy,
            oversight_level=oversight,
            impact_level=impact,
            orchestration_type=orchestration,
            overall_risk=risk_level,
            risk_score=risk_score,
            recommendations=recommendations,
            responses=responses_dict
        )
        
        # Add data sensitivity level to assessment if it exists
        if data_sensitivity:
            assessment.data_sensitivity_level = data_sensitivity
        
        # Store assessment in session for the report page
        session_id = f"assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(assessment.workflow_name) % 10000}"
        app.config[session_id] = assessment
        
        # Redirect to the beautiful report page instead of returning JSON
        return redirect(f'/report/{session_id}')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/report/<session_id>')
def view_report(session_id):
    """Display the beautiful report directly in the browser"""
    try:
        # Get assessment from stored session
        assessment = app.config.get(session_id)
        if not assessment:
            return redirect('/')  # Redirect to home if session not found
        
        # Generate the beautiful HTML report
        html_report = report_generator.generate_comprehensive_report(assessment)
        
        # Add modern action buttons to the report
        # Check if PDF generation is available
        pdf_available = pdf_generator.weasyprint_available
        download_label = "📄 Download PDF" if pdf_available else "📄 Download Report"
        download_title = "Download as PDF" if pdf_available else "Download as HTML (use browser Print to PDF)"
        
        # Enhanced email functionality with multiple options
        
        action_buttons = f'''
        <div style="position: fixed; top: 20px; right: 20px; z-index: 1000; display: flex; flex-direction: column; gap: 10px;">
            <button onclick="downloadPDF()" title="{download_title}" style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); color: white; padding: 12px 20px; border: none; border-radius: 25px; cursor: pointer; font-weight: bold; box-shadow: 0 4px 15px rgba(231,76,60,0.3); transition: all 0.3s ease; font-size: 14px;" onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 20px rgba(231,76,60,0.4)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 15px rgba(231,76,60,0.3)'">
                {download_label}
            </button>
            
            <!-- Email Dropdown -->
            <div class="email-dropdown" style="position: relative;">
                <button onclick="toggleEmailMenu()" style="background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); color: white; padding: 12px 20px; border: none; border-radius: 25px; cursor: pointer; font-weight: bold; box-shadow: 0 4px 15px rgba(52,152,219,0.3); transition: all 0.3s ease; font-size: 14px; display: flex; align-items: center; gap: 8px;" onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 20px rgba(52,152,219,0.4)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 15px rgba(52,152,219,0.3)'">
                    📧 Email Report <span id="email-arrow">▼</span>
                </button>
                <div id="email-menu" style="position: absolute; top: 100%; right: 0; background: white; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.2); overflow: hidden; min-width: 250px; z-index: 1001; display: none;">
                    <button onclick="quickEmail()" style="width: 100%; padding: 15px; border: none; background: white; text-align: left; cursor: pointer; border-bottom: 1px solid #eee; transition: background 0.2s;" onmouseover="this.style.background='#f8f9fa'" onmouseout="this.style.background='white'">
                        <strong>📧 Quick Email</strong><br>
                        <small style="color: #666;">Send short summary via email client</small>
                    </button>
                    <button onclick="downloadForEmail()" style="width: 100%; padding: 15px; border: none; background: white; text-align: left; cursor: pointer; transition: background 0.2s;" onmouseover="this.style.background='#f8f9fa'" onmouseout="this.style.background='white'">
                        <strong>📎 Download for Attachment</strong><br>
                        <small style="color: #666;">Download HTML file to attach to email</small>
                    </button>
                </div>
            </div>
            
            <button onclick="location.href='/'" style="background: linear-gradient(135deg, #27ae60 0%, #229954 100%); color: white; padding: 12px 20px; border: none; border-radius: 25px; cursor: pointer; font-weight: bold; box-shadow: 0 4px 15px rgba(39,174,96,0.3); transition: all 0.3s ease; font-size: 14px;" onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 20px rgba(39,174,96,0.4)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 15px rgba(39,174,96,0.3)'">
                🔄 New Assessment
            </button>
        </div>
        
        <script>
        function downloadPDF() {{
            window.location.href = '/download_pdf/{session_id}';
        }}
        
        function toggleEmailMenu() {{
            const menu = document.getElementById('email-menu');
            const arrow = document.getElementById('email-arrow');
            if (menu.style.display === 'none' || menu.style.display === '') {{
                menu.style.display = 'block';
                arrow.textContent = '▲';
            }} else {{
                menu.style.display = 'none';
                arrow.textContent = '▼';
            }}
        }}
        
        // Close email menu when clicking outside
        document.addEventListener('click', function(event) {{
            const dropdown = document.querySelector('.email-dropdown');
            if (!dropdown.contains(event.target)) {{
                document.getElementById('email-menu').style.display = 'none';
                document.getElementById('email-arrow').textContent = '▼';
            }}
        }});
        
        async function quickEmail() {{
            try {{
                // Close the menu
                document.getElementById('email-menu').style.display = 'none';
                document.getElementById('email-arrow').textContent = '▼';
                
                // Fetch the short email report content
                const response = await fetch('/email_content_short/{session_id}');
                const emailContent = await response.text();
                
                const subject = encodeURIComponent('AI Risk Assessment Report - {assessment.workflow_name}');
                const body = encodeURIComponent(emailContent);

                const mailtoUrl = `mailto:?subject=${{subject}}&body=${{body}}`;
                
                // Open default mail client
                window.location.href = mailtoUrl;
            }} catch (error) {{
                console.error('Error generating email content:', error);
                alert('Error generating email content. Please try again.');
            }}
        }}
        
        function downloadForEmail() {{
            // Close the menu
            document.getElementById('email-menu').style.display = 'none';
            document.getElementById('email-arrow').textContent = '▼';
            
            // Download HTML file for email attachment
            window.location.href = '/download_html/{session_id}';
        }}
        </script>'''
        
        # Insert action buttons before closing body tag
        html_report = html_report.replace('</body>', action_buttons + '</body>')
        
        return html_report
        
    except Exception as e:
        return f"<html><body><h1>Error</h1><p>Failed to generate report: {str(e)}</p><a href='/'>Back to Assessment</a></body></html>"

@app.route('/download_pdf/<session_id>')
def download_pdf(session_id):
    """Download the risk assessment report as PDF or fallback HTML"""
    try:
        assessment = app.config.get(session_id)
        if not assessment:
            return jsonify({'error': 'Assessment not found'}), 404
        
        # Generate HTML report
        html_report = report_generator.generate_comprehensive_report(assessment)
        
        # Generate PDF or fallback HTML
        content_bytes = pdf_generator.generate_pdf_report(assessment, html_report)
        
        # Create filename and MIME type based on availability
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = assessment.workflow_name.replace(' ', '_').replace('/', '_')
        
        if pdf_generator.weasyprint_available:
            filename = f'ai_risk_report_{safe_name}_{timestamp}.pdf'
            mimetype = 'application/pdf'
        else:
            filename = f'ai_risk_report_{safe_name}_{timestamp}.html'
            mimetype = 'text/html'
        
        return Response(
            content_bytes,
            mimetype=mimetype,
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
        
    except Exception as e:
        return jsonify({'error': f'Report generation failed: {str(e)}'}), 500

# Email content endpoints
@app.route('/email_content/<session_id>')
def get_email_content(session_id):
    """Get the complete email report content for a specific assessment"""
    try:
        assessment = app.config.get(session_id)
        if not assessment:
            return "Assessment not found", 404
        
        email_content = generate_complete_email_report(assessment, session_id, risk_assessor)
        return email_content, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    except Exception as e:
        return f"Error generating email content: {str(e)}", 500

@app.route('/email_content_short/<session_id>')
def get_email_content_short(session_id):
    """Get the short email report content for mailto: links"""
    try:
        assessment = app.config.get(session_id)
        if not assessment:
            return "Assessment not found", 404
        
        email_content = generate_short_email_report(assessment, session_id, risk_assessor)
        return email_content, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    except Exception as e:
        return f"Error generating email content: {str(e)}", 500

@app.route('/download_html/<session_id>')
def download_html(session_id):
    """Download the complete HTML report for email attachment"""
    try:
        assessment = app.config.get(session_id)
        if not assessment:
            return jsonify({'error': 'Assessment not found'}), 404
        
        # Generate the complete HTML report
        html_report = report_generator.generate_comprehensive_report(assessment)
        
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = assessment.workflow_name.replace(' ', '_').replace('/', '_')
        filename = f'ai_risk_report_{safe_name}_{timestamp}.html'
        
        return Response(
            html_report,
            mimetype='text/html',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
        
    except Exception as e:
        return jsonify({'error': f'HTML report generation failed: {str(e)}'}), 500

@app.route('/api/assessment', methods=['POST'])
def api_assessment():
    """API endpoint for programmatic assessment"""
    return assess_risk()

@app.route('/email_info')
def email_info_page():
    """Display information about the simplified email functionality"""
    return generate_email_info_page()

@app.route('/system_info')
def system_info_page():
    """Display system information and PDF setup instructions"""
    return generate_system_info_page(pdf_generator)

if __name__ == '__main__':
    # Check for required files and directories
    required_files = ['scoring.yaml']
    for file in required_files:
        if not os.path.exists(file):
            print(f"Error: {file} not found. Please ensure all YAML configuration files are present.")
            exit(1)
    
    # Check for questions directory and required question files
    questions_dir = 'questions'
    required_question_files = ['autonomy.yaml', 'oversight.yaml', 'impact.yaml', 'orchestration.yaml', 'data_sensitivity.yaml']
    
    if not os.path.exists(questions_dir):
        print(f"Error: {questions_dir} directory not found. Please ensure the questions directory exists.")
        exit(1)
    
    for question_file in required_question_files:
        question_path = os.path.join(questions_dir, question_file)
        if not os.path.exists(question_path):
            print(f"Warning: {question_path} not found. Some questions may not be available.")
    
    # Test loading questions to ensure they're valid
    try:
        questions_config = questions_loader.load_all_questions()
        print(f"✅ Successfully loaded {len(questions_config['questions'])} question categories from {questions_dir}/ directory")
    except Exception as e:
        print(f"Error: Failed to load questions from {questions_dir}/ directory: {e}")
        exit(1)
    
    print("Starting AI Risk Assessment Web Application (Enhanced)...")
    print("Configuration loaded from YAML files:")
    print("- questions/ directory: Individual question files for each assessment dimension")
    print("- scoring.yaml: Risk scoring and recommendations")
    print("New features:")
    print(f"{'✅' if pdf_generator.weasyprint_available else '⚠️'} PDF report generation: {'Enabled' if pdf_generator.weasyprint_available else 'Fallback mode (HTML)'}")
    print("📧 Email report functionality (mailto: links)")
    print("🎨 Modern UI enhancements")
    print("Open your browser and go to: http://localhost:9000")
    print("System info: http://localhost:9000/system_info")
    print("Email info: http://localhost:9000/email_info")
    app.run(debug=True, host='0.0.0.0', port=9000) 