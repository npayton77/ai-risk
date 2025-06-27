#!/usr/bin/env python3
"""
AI Risk Assessment Web Application - Refactored Version
Web frontend for the AI risk assessment tool using YAML configuration
"""

from flask import Flask, render_template_string, request, jsonify, send_file, redirect, url_for
import json
import os
import yaml
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple
import tempfile
from template_generator import TemplateGenerator
from report_generator import ReportGenerator

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
        with open(scoring_file, 'r') as f:
            self.scoring_config = yaml.safe_load(f)
        
        with open(questions_file, 'r') as f:
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

    def generate_html_report(self, assessment: RiskAssessment) -> str:
        """Generate HTML report for the assessment using YAML styling configuration"""
        risk_style = self.risk_styling.get(assessment.overall_risk, self.risk_styling['medium'])
        # Calculate max possible score dynamically based on dimensions
        max_score = len(self.dimension_scores) * 4  # 4 is max score per dimension
        risk_percentage = (assessment.risk_score / max_score) * 100
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Risk Assessment Report - {assessment.workflow_name}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 2.2em;
            font-weight: 300;
        }}
        
        .header .subtitle {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .assessment-meta {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        
        .meta-item {{
            text-align: center;
        }}
        
        .meta-item .label {{
            font-size: 0.9em;
            color: #6c757d;
            margin-bottom: 5px;
        }}
        
        .meta-item .value {{
            font-size: 1.1em;
            font-weight: bold;
            color: #2c3e50;
        }}
        
        .risk-overview {{
            background: {risk_style['bg']};
            border: 3px solid {risk_style['border']};
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 30px;
            text-align: center;
        }}
        
        .risk-level {{
            font-size: 2.5em;
            font-weight: bold;
            color: {risk_style['color']};
            margin-bottom: 10px;
            text-transform: uppercase;
        }}
        
        .risk-score {{
            font-size: 1.3em;
            color: #2c3e50;
        }}
        
        .risk-gauge {{
            width: 200px;
            height: 100px;
            margin: 20px auto;
            position: relative;
        }}
        
        .gauge-bg {{
            width: 200px;
            height: 100px;
            border: 8px solid #e9ecef;
            border-bottom: none;
            border-radius: 100px 100px 0 0;
            position: relative;
        }}
        
        .gauge-fill {{
            width: 200px;
            height: 100px;
            border: 8px solid {risk_style['color']};
            border-bottom: none;
            border-radius: 100px 100px 0 0;
            position: absolute;
            top: 0;
            left: 0;
            clip: rect(0, {risk_percentage * 2}px, 100px, 0);
        }}
        
        .gauge-text {{
            position: absolute;
            top: 70px;
            left: 50%;
            transform: translateX(-50%);
            font-weight: bold;
            color: {risk_style['color']};
        }}
        
        .dimensions-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .dimension-card {{
            background: white;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        
        .dimension-card:hover {{
            transform: translateY(-5px);
        }}
        
        .dimension-title {{
            font-size: 1.2em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .dimension-value {{
            font-size: 1.1em;
            color: {risk_style['color']};
            font-weight: bold;
            text-transform: uppercase;
            margin-bottom: 10px;
        }}
        
        .dimension-description {{
            color: #6c757d;
            font-size: 0.9em;
        }}
        
        .recommendations {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 30px;
        }}
        
        .recommendations h3 {{
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 1.4em;
        }}
        
        .recommendation-item {{
            background: white;
            border-left: 4px solid {risk_style['color']};
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 0 8px 8px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .reasoning-section {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 25px;
        }}
        
        .reasoning-section h3 {{
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 1.4em;
        }}
        
        .reasoning-item {{
            margin-bottom: 15px;
            padding: 15px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .reasoning-item .question {{
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        }}
        
        .reasoning-item .answer {{
            color: #6c757d;
        }}
        
        .footer {{
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 15px;
            font-size: 0.9em;
        }}
        
        @media print {{
            body {{ background: white; }}
            .container {{ box-shadow: none; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>AI Risk Assessment Report</h1>
            <div class="subtitle">{assessment.workflow_name}</div>
        </div>
        
        <div class="content">
            <div class="assessment-meta">
                <div class="meta-item">
                    <div class="label">Assessed By</div>
                    <div class="value">{assessment.assessor}</div>
                </div>
                <div class="meta-item">
                    <div class="label">Assessment Date</div>
                    <div class="value">{assessment.date}</div>
                </div>
                <div class="meta-item">
                    <div class="label">Workflow Type</div>
                    <div class="value">AI {assessment.orchestration_type.title()} System</div>
                </div>
            </div>
            
            <div class="risk-overview">
                <div class="risk-level">{assessment.overall_risk} Risk</div>
                <div class="risk-score">Risk Score: {assessment.risk_score} / 16</div>
                <div class="risk-gauge">
                    <div class="gauge-bg"></div>
                    <div class="gauge-fill"></div>
                    <div class="gauge-text">{risk_percentage:.0f}%</div>
                </div>
            </div>
            
            <h2>Risk Assessment Dimensions</h2>
            <div class="dimensions-grid">
                <div class="dimension-card">
                    <div class="dimension-title">🎯 Autonomy Level</div>
                    <div class="dimension-value">{assessment.autonomy_level}</div>
                    <div class="dimension-description">
                        {self.get_dimension_description('autonomy', assessment.autonomy_level)}
                    </div>
                </div>
                
                <div class="dimension-card">
                    <div class="dimension-title">🔍 Human Oversight</div>
                    <div class="dimension-value">{assessment.oversight_level}</div>
                    <div class="dimension-description">
                        {self.get_dimension_description('oversight', assessment.oversight_level)}
                    </div>
                </div>
                
                <div class="dimension-card">
                    <div class="dimension-title">📊 Output Impact</div>
                    <div class="dimension-value">{assessment.impact_level}</div>
                    <div class="dimension-description">
                        {self.get_dimension_description('impact', assessment.impact_level)}
                    </div>
                </div>
                
                <div class="dimension-card">
                    <div class="dimension-title">🔧 Orchestration</div>
                    <div class="dimension-value">{assessment.orchestration_type}</div>
                    <div class="dimension-description">
                        {self.get_dimension_description('orchestration', assessment.orchestration_type)}
                    </div>
                </div>
            </div>
            
            <div class="recommendations">
                <h3>Recommended Actions</h3>
                {"".join([f'<div class="recommendation-item">{rec}</div>' for rec in assessment.recommendations])}
            </div>
            
            <div class="reasoning-section">
                <h3>Assessment Reasoning</h3>
                <div class="reasoning-item">
                    <div class="question">Autonomy Level Justification:</div>
                    <div class="answer">{assessment.responses.get('autonomy_reasoning', 'Not provided')}</div>
                </div>
                <div class="reasoning-item">
                    <div class="question">Oversight Level Justification:</div>
                    <div class="answer">{assessment.responses.get('oversight_reasoning', 'Not provided')}</div>
                </div>
                <div class="reasoning-item">
                    <div class="question">Impact Level Justification:</div>
                    <div class="answer">{assessment.responses.get('impact_reasoning', 'Not provided')}</div>
                </div>
                <div class="reasoning-item">
                    <div class="question">Orchestration Type Justification:</div>
                    <div class="answer">{assessment.responses.get('orchestration_reasoning', 'Not provided')}</div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            Generated by AI Risk Assessment Tool | {assessment.date}
        </div>
    </div>
</body>
</html>
        """
        
        return html_content

# Flask Web Application
app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Initialize components
template_generator = TemplateGenerator()
risk_assessor = AIRiskAssessor()
report_generator = ReportGenerator()

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
            'autonomy_reasoning': autonomy_reasoning,
            'oversight_reasoning': oversight_reasoning,
            'impact_reasoning': impact_reasoning,
            'orchestration_reasoning': orchestration_reasoning
        }
        
        # Add data sensitivity if it exists
        if data_sensitivity:
            responses_dict['data_sensitivity_reasoning'] = data_sensitivity_reasoning
        
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
        
        # Generate comprehensive HTML report
        html_report = report_generator.generate_comprehensive_report(assessment)
        
        # Save to temporary file for download
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8')
        temp_file.write(html_report)
        temp_file.close()
        
        # Store file path in session (simplified for demo)
        app.config['TEMP_REPORT_PATH'] = temp_file.name
        app.config['TEMP_REPORT_NAME'] = f'ai_risk_report_{workflow_name.replace(" ", "_")}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
        
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
        
        # Add download button to the report
        download_button = '''
        <div style="position: fixed; top: 20px; right: 20px; z-index: 1000;">
            <a href="#" onclick="downloadReport()" style="background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%); color: white; padding: 15px 25px; border-radius: 30px; text-decoration: none; font-weight: bold; box-shadow: 0 5px 15px rgba(0,0,0,0.2); transition: transform 0.3s ease;" onmouseover="this.style.transform='translateY(-3px)'" onmouseout="this.style.transform='translateY(0)'">
                📄 Download Report
            </a>
        </div>
        <script>
        function downloadReport() {
            // Create a downloadable version
            const htmlContent = document.documentElement.outerHTML;
            const blob = new Blob([htmlContent], { type: 'text/html' });
            const url = URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = `ai_risk_report_''' + assessment.workflow_name.replace(' ', '_') + '''_''' + datetime.now().strftime('%Y%m%d_%H%M%S') + '''.html`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
        </script>
        '''
        
        # Insert download button before closing body tag
        html_report = html_report.replace('</body>', download_button + '</body>')
        
        return html_report
        
    except Exception as e:
        return f"<html><body><h1>Error</h1><p>Failed to generate report: {str(e)}</p><a href='/'>Back to Assessment</a></body></html>"

@app.route('/download_report')
def download_report():
    """Download the generated HTML report"""
    try:
        report_path = app.config.get('TEMP_REPORT_PATH')
        report_name = app.config.get('TEMP_REPORT_NAME', f'ai_risk_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html')
        
        if report_path and os.path.exists(report_path):
            return send_file(
                report_path,
                as_attachment=True,
                download_name=report_name,
                mimetype='text/html'
            )
        else:
            return jsonify({'error': 'Report not found. Please generate an assessment first.'}), 404
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

@app.route('/api/assessment', methods=['POST'])
def api_assessment():
    """API endpoint for programmatic assessment"""
    return assess_risk()

if __name__ == '__main__':
    # Check for required files
    required_files = ['questions.yaml', 'scoring.yaml']
    for file in required_files:
        if not os.path.exists(file):
            print(f"Error: {file} not found. Please ensure all YAML configuration files are present.")
            exit(1)
    
    print("Starting AI Risk Assessment Web Application (Refactored)...")
    print("Configuration loaded from YAML files:")
    print("- questions.yaml: Questions and form structure")
    print("- scoring.yaml: Risk scoring and recommendations")
    print("Open your browser and go to: http://localhost:9000")
    app.run(debug=True, host='0.0.0.0', port=9000) 