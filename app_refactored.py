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

# Import the risk assessment logic
@dataclass
class RiskAssessment:
    """Stores the complete risk assessment results"""
    workflow_name: str
    assessor: str
    date: str
    autonomy_level: str
    oversight_level: str
    impact_level: str
    orchestration_type: str
    overall_risk: str
    risk_score: int
    recommendations: List[str]
    responses: Dict[str, str]

class AIRiskAssessor:
    def __init__(self, scoring_file: str = 'scoring.yaml', questions_file: str = 'questions.yaml'):
        """Initialize with YAML configuration files"""
        with open(scoring_file, 'r', encoding='utf-8') as f:
            self.scoring_config = yaml.safe_load(f)
        
        with open(questions_file, 'r', encoding='utf-8') as f:
            self.questions_config = yaml.safe_load(f)
        
        # Extract scoring data from YAML
        self.dimension_scores = self.scoring_config['scoring']['dimensions']
        self.risk_thresholds = self.scoring_config['scoring']['risk_thresholds']
        self.recommendations_config = self.scoring_config['recommendations']
        self.risk_styling = self.scoring_config['risk_styling']

    def calculate_risk_score(self, autonomy: str, oversight: str, impact: str, orchestration: str, data_sensitivity: str = None) -> Tuple[int, str]:
        """Calculate overall risk score and level using YAML configuration"""
        score = (
            self.dimension_scores['autonomy'][autonomy] +
            self.dimension_scores['oversight'][oversight] + 
            self.dimension_scores['impact'][impact] +
            self.dimension_scores['orchestration'][orchestration]
        )
        
        # Add data sensitivity if provided
        if data_sensitivity and 'data_sensitivity' in self.dimension_scores:
            score += self.dimension_scores['data_sensitivity'][data_sensitivity]
        
        # Determine risk level from thresholds
        risk_level = "unknown"
        for threshold in self.risk_thresholds:
            if threshold['min_score'] <= score <= threshold['max_score']:
                risk_level = threshold['level']
                break
        
        return score, risk_level

    def generate_recommendations(self, risk_level: str, autonomy: str, oversight: str, impact: str, data_sensitivity: str = None) -> List[str]:
        """Generate specific recommendations based on risk profile using YAML configuration"""
        recommendations = []
        
        # Base recommendations by risk level
        base_recommendations = self.recommendations_config['by_risk_level'].get(risk_level, [])
        recommendations.extend(base_recommendations)
        
        # Conditional recommendations
        for condition_rule in self.recommendations_config['conditional']:
            condition = condition_rule['condition']
            matches = True
            
            # Check if current assessment matches the condition
            current_values = {
                'autonomy': autonomy,
                'oversight': oversight,
                'impact': impact
            }
            if data_sensitivity:
                current_values['data_sensitivity'] = data_sensitivity
            
            for dimension, required_values in condition.items():
                if current_values.get(dimension) not in required_values:
                    matches = False
                    break
            
            if matches:
                recommendations.append(condition_rule['recommendation'])
        
        return recommendations

    def get_dimension_description(self, dimension: str, value: str) -> str:
        """Get description for dimension values from YAML configuration"""
        questions = self.questions_config['questions']
        if dimension in questions and value in questions[dimension]['options']:
            return questions[dimension]['options'][value]['description']
        return 'Unknown'
    
    def _get_dimension_score(self, dimension: str, value: str) -> int:
        """Get numerical score for a dimension value"""
        if dimension in self.dimension_scores and value in self.dimension_scores[dimension]:
            return self.dimension_scores[dimension][value]
        return 0
    
    def _get_email_risk_summary(self, risk_level: str) -> str:
        """Get email-friendly risk summary"""
        summaries = {
            'low': 'This AI system presents minimal risk to your organization. Standard monitoring and review processes should be sufficient.',
            'medium': 'This AI system presents moderate risk requiring enhanced oversight and monitoring procedures.',
            'high': 'This AI system presents significant risk requiring comprehensive monitoring, clear escalation procedures, and dedicated oversight.',
            'critical': 'This AI system presents critical risk requiring extensive safeguards, formal approval processes, and continuous monitoring.'
        }
        return summaries.get(risk_level, 'Risk level assessment unavailable.')

# Flask Web Application
app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Initialize components
template_generator = TemplateGenerator()
risk_assessor = AIRiskAssessor()
report_generator = ReportGenerator()
pdf_generator = PDFGenerator()
email_sender = EmailSender()

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

def generate_complete_email_report(assessment, session_id):
    """Generate a complete email report with all assessment details"""
    # Get data sensitivity info if available
    data_sensitivity_info = ""
    if hasattr(assessment, 'data_sensitivity_level') and assessment.data_sensitivity_level:
        ds_score = risk_assessor._get_dimension_score('data_sensitivity', assessment.data_sensitivity_level)
        ds_desc = risk_assessor.get_dimension_description('data_sensitivity', assessment.data_sensitivity_level)
        data_sensitivity_info = f"""
🔒 DATA SENSITIVITY: {assessment.data_sensitivity_level.upper()} ({ds_score}/4)
   Description: {ds_desc}"""
    
    # Get data sensitivity reasoning if available
    ds_reasoning = ""
    if 'data_sensitivity_reasoning' in assessment.responses:
        ds_reasoning = f"""
🔒 Data Sensitivity Reasoning:
   {assessment.responses.get('data_sensitivity_reasoning', 'Not provided')}"""

    return f"""Hi there,

Please find the AI Risk Assessment Report for "{assessment.workflow_name}" below.

=============================================================
                   AI RISK ASSESSMENT REPORT                
=============================================================

Assessment Details:
• Workflow/System: {assessment.workflow_name}
• Assessed by: {assessment.assessor}
• Date: {assessment.date}
• Report ID: RA-{datetime.now().strftime('%Y%m%d')}-{hash(assessment.workflow_name) % 10000}

=============================================================
                        RISK OVERVIEW                      
=============================================================

🎯 RISK LEVEL: {assessment.overall_risk.upper()} RISK
📊 Risk Score: {assessment.risk_score}/20 ({int((assessment.risk_score/20)*100)}%)

Risk Summary:
{risk_assessor._get_email_risk_summary(assessment.overall_risk)}

=============================================================
                    RISK ASSESSMENT DIMENSIONS            
=============================================================

🎯 AUTONOMY LEVEL: {assessment.autonomy_level.upper()} ({risk_assessor._get_dimension_score('autonomy', assessment.autonomy_level)}/4)
   Description: {risk_assessor.get_dimension_description('autonomy', assessment.autonomy_level)}

🔍 HUMAN OVERSIGHT: {assessment.oversight_level.upper()} ({risk_assessor._get_dimension_score('oversight', assessment.oversight_level)}/4)
   Description: {risk_assessor.get_dimension_description('oversight', assessment.oversight_level)}

📊 OUTPUT IMPACT: {assessment.impact_level.upper()} ({risk_assessor._get_dimension_score('impact', assessment.impact_level)}/4)
   Description: {risk_assessor.get_dimension_description('impact', assessment.impact_level)}

🔧 ORCHESTRATION: {assessment.orchestration_type.upper()} ({risk_assessor._get_dimension_score('orchestration', assessment.orchestration_type)}/4)
   Description: {risk_assessor.get_dimension_description('orchestration', assessment.orchestration_type)}{data_sensitivity_info}

=============================================================
                     RECOMMENDED ACTIONS                   
=============================================================

{chr(10).join([f"📋 {i+1}. {rec}" for i, rec in enumerate(assessment.recommendations)])}

=============================================================
                    ASSESSMENT REASONING                   
=============================================================

🎯 Autonomy Level Reasoning:
   {assessment.responses.get('autonomy_reasoning', 'Not provided')}

🔍 Oversight Level Reasoning:
   {assessment.responses.get('oversight_reasoning', 'Not provided')}

📊 Impact Level Reasoning:
   {assessment.responses.get('impact_reasoning', 'Not provided')}

🔧 Orchestration Type Reasoning:
   {assessment.responses.get('orchestration_reasoning', 'Not provided')}{ds_reasoning}

=============================================================

📎 For the interactive version with charts and visualizations:
   View online: http://localhost:9000/report/{session_id}
   Download: http://localhost:9000/download_pdf/{session_id}

Best regards,
{assessment.assessor}

---
Generated by AI Risk Assessment Tool
{datetime.now().strftime('%B %d, %Y at %I:%M %p')}
"""

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
        
# No need to generate email content here - we'll fetch it via AJAX
        
        action_buttons = f'''
        <div style="position: fixed; top: 20px; right: 20px; z-index: 1000; display: flex; flex-direction: column; gap: 10px;">
            <button onclick="downloadPDF()" title="{download_title}" style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); color: white; padding: 12px 20px; border: none; border-radius: 25px; cursor: pointer; font-weight: bold; box-shadow: 0 4px 15px rgba(231,76,60,0.3); transition: all 0.3s ease; font-size: 14px;" onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 20px rgba(231,76,60,0.4)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 15px rgba(231,76,60,0.3)'">
                {download_label}
            </button>
            <button onclick="emailReport()" style="background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); color: white; padding: 12px 20px; border: none; border-radius: 25px; cursor: pointer; font-weight: bold; box-shadow: 0 4px 15px rgba(52,152,219,0.3); transition: all 0.3s ease; font-size: 14px;" onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 20px rgba(52,152,219,0.4)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 15px rgba(52,152,219,0.3)'">
                📧 Email Report
            </button>
            <button onclick="location.href='/'" style="background: linear-gradient(135deg, #27ae60 0%, #229954 100%); color: white; padding: 12px 20px; border: none; border-radius: 25px; cursor: pointer; font-weight: bold; box-shadow: 0 4px 15px rgba(39,174,96,0.3); transition: all 0.3s ease; font-size: 14px;" onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 20px rgba(39,174,96,0.4)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 15px rgba(39,174,96,0.3)'">
                🔄 New Assessment
            </button>
        </div>
        
        <script>
        function downloadPDF() {{
            window.location.href = '/download_pdf/{session_id}';
        }}
        
        async function emailReport() {{
            try {{
                // Fetch the complete email report content
                const response = await fetch('/email_content/{session_id}');
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

# Email content endpoint
@app.route('/email_content/<session_id>')
def get_email_content(session_id):
    """Get the complete email report content for a specific assessment"""
    try:
        assessment = app.config.get(session_id)
        if not assessment:
            return "Assessment not found", 404
        
        email_content = generate_complete_email_report(assessment, session_id)
        return email_content, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    except Exception as e:
        return f"Error generating email content: {str(e)}", 500

@app.route('/api/assessment', methods=['POST'])
def api_assessment():
    """API endpoint for programmatic assessment"""
    return assess_risk()

@app.route('/email_info')
def email_info_page():
    """Display information about the simplified email functionality"""
    
    html_content = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Email Functionality - AI Risk Assessment Tool</title>
        <style>
            body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin: 0; padding: 20px; min-height: 100vh; }
            .container { max-width: 800px; margin: 0 auto; background: white; border-radius: 15px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
            h1 { color: #2c3e50; text-align: center; margin-bottom: 30px; }
            .info-box { background: #f8f9fa; border-radius: 10px; padding: 20px; margin: 20px 0; }
            .success-box { border-left: 4px solid #27ae60; background: #d4edda; }
            .btn { background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); color: white; padding: 12px 25px; border: none; border-radius: 25px; cursor: pointer; font-weight: bold; text-decoration: none; display: inline-block; margin: 10px; }
            .feature-list { list-style: none; padding: 0; }
            .feature-item { padding: 10px; margin: 5px 0; border-radius: 8px; display: flex; align-items: center; gap: 10px; background: #e8f5e8; color: #2d5a2d; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📧 Email Functionality</h1>
            
            <div class="info-box success-box">
                <h3>✅ Simple & User-Friendly Email</h3>
                <p>Our email functionality uses your default mail client - <strong>no complex setup required!</strong></p>
                <p>When you click "📧 Email Report", it will:</p>
                <ul class="feature-list">
                    <li class="feature-item">✅ Open your default mail app (Outlook, Mail, Gmail, etc.)</li>
                    <li class="feature-item">✅ Pre-fill the subject with the assessment name</li>
                    <li class="feature-item">✅ Include a professional email body with key findings</li>
                    <li class="feature-item">✅ Provide links to view and download the report</li>
                </ul>
            </div>
            
            <div class="info-box">
                <h3>How It Works</h3>
                <p><strong>1. Generate your risk assessment report</strong></p>
                <p><strong>2. Click "📧 Email Report"</strong> - your mail client opens automatically</p>
                <p><strong>3. Add recipient email addresses</strong> and send!</p>
                
                <p><strong>What's included in the email:</strong></p>
                <ul>
                    <li>📊 Assessment summary (risk level, score, assessor)</li>
                    <li>🔗 Direct link to view the report online</li>
                    <li>📄 Link to download the report file</li>
                    <li>📋 Top 3 key recommendations</li>
                    <li>✉️ Professional formatting</li>
                </ul>
            </div>
            
            <div class="info-box">
                <h3>🎯 Benefits</h3>
                <ul>
                    <li><strong>Zero Configuration:</strong> Works with any email client</li>
                    <li><strong>Privacy First:</strong> No credentials or SMTP setup needed</li>
                    <li><strong>Universal Compatibility:</strong> Works on all operating systems</li>
                    <li><strong>Professional Output:</strong> Formatted, ready-to-send emails</li>
                </ul>
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <a href="/" class="btn">🔄 Back to Assessment Tool</a>
            </div>
        </div>
    </body>
    </html>
    '''
    
    return html_content

@app.route('/system_info')
def system_info_page():
    """Display system information and PDF setup instructions"""
    pdf_info = pdf_generator.get_system_requirements_info()
    
    html_content = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>System Information - AI Risk Assessment Tool</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin: 0; padding: 20px; min-height: 100vh; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; border-radius: 15px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }}
            h1 {{ color: #2c3e50; text-align: center; margin-bottom: 30px; }}
            .status-box {{ background: #f8f9fa; border-radius: 10px; padding: 20px; margin: 20px 0; }}
            .status-good {{ border-left: 4px solid #27ae60; background: #d4edda; }}
            .status-warning {{ border-left: 4px solid #ffc107; background: #fff3cd; }}
            pre {{ background: #2c3e50; color: #ecf0f1; padding: 20px; border-radius: 8px; overflow-x: auto; font-size: 14px; }}
            .btn {{ background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); color: white; padding: 12px 25px; border: none; border-radius: 25px; cursor: pointer; font-weight: bold; text-decoration: none; display: inline-block; margin: 10px; }}
            .feature-list {{ list-style: none; padding: 0; }}
            .feature-item {{ padding: 10px; margin: 5px 0; border-radius: 8px; display: flex; align-items: center; gap: 10px; }}
            .feature-enabled {{ background: #d4edda; color: #155724; }}
            .feature-fallback {{ background: #fff3cd; color: #856404; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔧 System Information</h1>
            
            <div class="status-box {'status-good' if pdf_generator.weasyprint_available else 'status-warning'}">
                <h3>PDF Generation Status</h3>
                <ul class="feature-list">
                    <li class="feature-item {'feature-enabled' if pdf_generator.weasyprint_available else 'feature-fallback'}">
                        {'✅' if pdf_generator.weasyprint_available else '⚠️'} 
                        WeasyPrint PDF Generation: {'Enabled' if pdf_generator.weasyprint_available else 'Fallback Mode'}
                    </li>
                    <li class="feature-item feature-enabled">
                        ✅ HTML Report Generation: Enabled
                    </li>
                                         <li class="feature-item feature-enabled">
                         ✅ Email Functionality: Enabled (uses default mail client)
                     </li>
                    <li class="feature-item feature-enabled">
                        ✅ Risk Assessment: Enabled
                    </li>
                </ul>
            </div>
            
            {"<div class='status-box status-warning'><h3>PDF Setup Instructions</h3><pre>" + pdf_info + "</pre></div>" if not pdf_generator.weasyprint_available else ""}
            
            <div class="status-box">
                <h3>Current Features</h3>
                <p><strong>✨ Available Now:</strong></p>
                <ul>
                    <li>📊 Comprehensive AI Risk Assessment</li>
                    <li>🎨 Beautiful HTML Reports</li>
                    <li>📧 Email Report Delivery</li>
                    <li>{'📄 PDF Generation' if pdf_generator.weasyprint_available else '📄 HTML Download (Print to PDF)'}</li>
                    <li>🔄 Dynamic YAML Configuration</li>
                    <li>📱 Mobile-Responsive Design</li>
                </ul>
            </div>
            
                         <div style="text-align: center; margin-top: 30px;">
                 <a href="/" class="btn">🔄 Back to Assessment Tool</a>
                 <a href="/email_info" class="btn">📧 Email Info</a>
             </div>
        </div>
    </body>
    </html>
    '''
    
    return html_content

if __name__ == '__main__':
    # Check for required files
    required_files = ['questions.yaml', 'scoring.yaml']
    for file in required_files:
        if not os.path.exists(file):
            print(f"Error: {file} not found. Please ensure all YAML configuration files are present.")
            exit(1)
    
    print("Starting AI Risk Assessment Web Application (Enhanced)...")
    print("Configuration loaded from YAML files:")
    print("- questions.yaml: Questions and form structure")
    print("- scoring.yaml: Risk scoring and recommendations")
    print("New features:")
    print(f"{'✅' if pdf_generator.weasyprint_available else '⚠️'} PDF report generation: {'Enabled' if pdf_generator.weasyprint_available else 'Fallback mode (HTML)'}")
    print("📧 Email report functionality (mailto: links)")
    print("🎨 Modern UI enhancements")
    print("Open your browser and go to: http://localhost:9000")
    print("System info: http://localhost:9000/system_info")
    print("Email info: http://localhost:9000/email_info")
    app.run(debug=True, host='0.0.0.0', port=9000) 