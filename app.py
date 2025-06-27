#!/usr/bin/env python3
"""
AI Risk Assessment Web Application
Web frontend for the AI risk assessment tool
"""

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import json
import os
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple
import tempfile

# Import the risk assessment logic (reuse from previous tool)
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
    def __init__(self):
        # Risk scoring matrix (same as before)
        self.autonomy_scores = {
            "tool": 1,
            "assistant": 2,
            "agent": 3,
            "autonomous": 4
        }
        
        self.oversight_scores = {
            "continuous": 1,
            "checkpoint": 2,
            "exception": 3,
            "minimal": 4
        }
        
        self.impact_scores = {
            "informational": 1,
            "operational": 2,
            "strategic": 3,
            "external": 4
        }
        
        self.orchestration_scores = {
            "single": 1,
            "sequential": 2,
            "parallel": 3,
            "hierarchical": 4
        }
        
        # Risk level thresholds
        self.risk_thresholds = {
            (4, 7): "low",
            (8, 11): "medium", 
            (12, 14): "high",
            (15, 16): "critical"
        }

    def calculate_risk_score(self, autonomy: str, oversight: str, impact: str, orchestration: str) -> Tuple[int, str]:
        """Calculate overall risk score and level"""
        score = (
            self.autonomy_scores[autonomy] +
            self.oversight_scores[oversight] + 
            self.impact_scores[impact] +
            self.orchestration_scores[orchestration]
        )
        
        risk_level = "unknown"
        for (min_score, max_score), level in self.risk_thresholds.items():
            if min_score <= score <= max_score:
                risk_level = level
                break
        
        return score, risk_level

    def generate_recommendations(self, risk_level: str, autonomy: str, oversight: str, impact: str) -> List[str]:
        """Generate specific recommendations based on risk profile"""
        recommendations = []
        
        # Base recommendations by risk level
        if risk_level == "low":
            recommendations.extend([
                "Implement standard review processes for AI outputs",
                "Establish clear escalation paths for edge cases",
                "Maintain documentation of AI decisions and human overrides"
            ])
        elif risk_level == "medium":
            recommendations.extend([
                "Implement regular audits of AI decision quality",
                "Set up confidence thresholds for autonomous actions",
                "Establish fallback procedures for AI failures",
                "Monitor for model drift and performance degradation"
            ])
        elif risk_level == "high":
            recommendations.extend([
                "Implement comprehensive real-time monitoring",
                "Set up automatic circuit breakers for anomalous behavior",
                "Develop rapid rollback capabilities",
                "Assign dedicated AI oversight personnel",
                "Conduct regular stress testing"
            ])
        else:  # critical
            recommendations.extend([
                "Implement sandboxed testing environments",
                "Require formal verification of AI behavior",
                "Install emergency kill switches",
                "Conduct extensive simulation testing before deployment",
                "Consider if this risk level is acceptable for your organization"
            ])
        
        # Specific recommendations based on dimensions
        if autonomy in ["agent", "autonomous"] and oversight == "minimal":
            recommendations.append("HIGH PRIORITY: Increase human oversight given high autonomy level")
        
        if impact == "external" and oversight in ["exception", "minimal"]:
            recommendations.append("CRITICAL: External impact requires more frequent human review")
        
        if autonomy == "autonomous":
            recommendations.append("Consider implementing AI explainability tools")
        
        return recommendations

    def get_dimension_description(self, dimension: str, value: str) -> str:
        """Get description for dimension values"""
        descriptions = {
            'autonomy': {
                'tool': 'AI provides recommendations only',
                'assistant': 'AI executes tasks with human approval',
                'agent': 'AI acts independently within defined boundaries',
                'autonomous': 'AI manages entire workflows without oversight'
            },
            'oversight': {
                'continuous': 'Human involved in every step/decision',
                'checkpoint': 'Human reviews at defined intervals',
                'exception': 'Human intervention only for edge cases',
                'minimal': 'Periodic auditing and monitoring only'
            },
            'impact': {
                'informational': 'Data/insights only (reports, analysis)',
                'operational': 'Affects daily operations (scheduling, routing)',
                'strategic': 'Business-critical decisions (investments, hiring)',
                'external': 'Customer/regulatory impact (patient care, transactions)'
            },
            'orchestration': {
                'single': 'One AI system operating independently',
                'sequential': 'Chain of AI tasks in defined order',
                'parallel': 'Multiple AI systems working simultaneously',
                'hierarchical': 'AI systems managing other AI systems'
            }
        }
        return descriptions.get(dimension, {}).get(value, 'Unknown')

    def generate_html_report(self, assessment: RiskAssessment) -> str:
        """Generate HTML report for the assessment (same as before)"""
        # Risk level styling
        risk_styles = {
            "low": {"color": "#27ae60", "bg": "#e6f3e6", "border": "#27ae60"},
            "medium": {"color": "#f39c12", "bg": "#fff3cd", "border": "#f39c12"},
            "high": {"color": "#e74c3c", "bg": "#f8d7da", "border": "#e74c3c"},
            "critical": {"color": "#8e44ad", "bg": "#e2e3f3", "border": "#8e44ad"}
        }
        
        risk_style = risk_styles.get(assessment.overall_risk, risk_styles["medium"])
        
        # Generate risk gauge visualization
        risk_percentage = (assessment.risk_score / 16) * 100
        
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

# Initialize the risk assessor
risk_assessor = AIRiskAssessor()

@app.route('/')
def index():
    """Main assessment form page"""
    return render_template('assessment_form.html')

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
        
        # Get reasoning
        autonomy_reasoning = request.form.get('autonomy_reasoning', '').strip()
        oversight_reasoning = request.form.get('oversight_reasoning', '').strip()
        impact_reasoning = request.form.get('impact_reasoning', '').strip()
        orchestration_reasoning = request.form.get('orchestration_reasoning', '').strip()
        
        # Validate required fields
        if not all([workflow_name, assessor, autonomy, oversight, impact, orchestration]):
            return jsonify({'error': 'All fields are required'}), 400
        
        # Calculate risk
        risk_score, risk_level = risk_assessor.calculate_risk_score(
            autonomy, oversight, impact, orchestration
        )
        
        # Generate recommendations
        recommendations = risk_assessor.generate_recommendations(
            risk_level, autonomy, oversight, impact
        )
        
        # Create assessment object
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
            responses={
                'autonomy_reasoning': autonomy_reasoning,
                'oversight_reasoning': oversight_reasoning,
                'impact_reasoning': impact_reasoning,
                'orchestration_reasoning': orchestration_reasoning
            }
        )
        
        # Generate HTML report
        html_report = risk_assessor.generate_html_report(assessment)
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8')
        temp_file.write(html_report)
        temp_file.close()
        
        # Store file path for download
        session_data = {
            'assessment': asdict(assessment),
            'html_file': temp_file.name
        }
        
        return jsonify({
            'success': True,
            'assessment': asdict(assessment),
            'download_url': '/download_report'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download_report')
def download_report():
    """Download the generated HTML report"""
    # In a real app, you'd want to store this in session or database
    # For now, we'll generate a simple report
    return send_file(
        'temp_report.html',
        as_attachment=True,
        download_name=f'ai_risk_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
    )

@app.route('/api/assessment', methods=['POST'])
def api_assessment():
    """API endpoint for programmatic assessment"""
    return assess_risk()

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Create the HTML template
    template_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Risk Assessment Tool</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            margin: 0 0 10px 0;
            font-size: 2.2em;
            font-weight: 300;
        }
        
        .header .subtitle {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .form-container {
            padding: 40px;
        }
        
        .form-group {
            margin-bottom: 30px;
        }
        
        .form-group label {
            display: block;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 8px;
            font-size: 1.1em;
        }
        
        .form-group input,
        .form-group textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 1em;
            transition: border-color 0.3s ease;
        }
        
        .form-group input:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .form-group textarea {
            height: 80px;
            resize: vertical;
        }
        
        .radio-group {
            display: grid;
            grid-template-columns: 1fr;
            gap: 15px;
            margin-top: 10px;
        }
        
        .radio-option {
            background: #f8f9fa;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            padding: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
        }
        
        .radio-option:hover {
            border-color: #667eea;
            transform: translateY(-2px);
        }
        
        .radio-option.selected {
            border-color: #667eea;
            background: #e8f0fe;
        }
        
        .radio-option input[type="radio"] {
            position: absolute;
            opacity: 0;
            width: 0;
            height: 0;
        }
        
        .radio-title {
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
            font-size: 1.1em;
        }
        
        .radio-description {
            color: #6c757d;
            font-size: 0.95em;
            line-height: 1.4;
        }
        
        .help-text {
            background: #e8f0fe;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin: 15px 0;
            border-radius: 0 8px 8px 0;
            font-size: 0.9em;
            color: #2c3e50;
        }
        
        .submit-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 40px;
            border: none;
            border-radius: 50px;
            font-size: 1.1em;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.3s ease;
            display: block;
            margin: 40px auto 0;
        }
        
        .submit-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }
        
        .submit-btn:disabled {
            opacity: 0.7;
            cursor: not-allowed;
            transform: none;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 40px;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .result {
            display: none;
            text-align: center;
            padding: 40px;
        }
        
        .result.success {
            color: #27ae60;
        }
        
        .result.error {
            color: #e74c3c;
        }
        
        .download-btn {
            background: #27ae60;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 25px;
            font-size: 1em;
            font-weight: bold;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin-top: 20px;
            transition: transform 0.3s ease;
        }
        
        .download-btn:hover {
            transform: translateY(-2px);
        }
        
        @media (max-width: 768px) {
            .form-container {
                padding: 20px;
            }
            
            .radio-group {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>AI Risk Assessment Tool</h1>
            <div class="subtitle">Evaluate AI workflow patterns and determine risk levels</div>
        </div>
        
        <div class="form-container">
            <form id="assessmentForm">
                <!-- Basic Information -->
                <div class="form-group">
                    <label for="workflow_name">Workflow/System Name *</label>
                    <input type="text" id="workflow_name" name="workflow_name" required>
                </div>
                
                <div class="form-group">
                    <label for="assessor">Assessor Name *</label>
                    <input type="text" id="assessor" name="assessor" required>
                </div>
                
                <!-- Autonomy Level -->
                <div class="form-group">
                    <label>🎯 Autonomy Level: How much decision-making power does the AI have? *</label>
                    <div class="help-text">
                        Consider who makes the final decisions in your workflow
                    </div>
                    <div class="radio-group">
                        <div class="radio-option" onclick="selectRadio('autonomy', 'tool')">
                            <input type="radio" name="autonomy" value="tool" id="autonomy_tool">
                            <div class="radio-title">Tool</div>
                            <div class="radio-description">AI provides recommendations only - humans always decide</div>
                        </div>
                        <div class="radio-option" onclick="selectRadio('autonomy', 'assistant')">
                            <input type="radio" name="autonomy" value="assistant" id="autonomy_assistant">
                            <div class="radio-title">Assistant</div>
                            <div class="radio-description">AI executes tasks with human approval - humans approve each action</div>
                        </div>
                        <div class="radio-option" onclick="selectRadio('autonomy', 'agent')">
                            <input type="radio" name="autonomy" value="agent" id="autonomy_agent">
                            <div class="radio-title">Agent</div>
                            <div class="radio-description">AI acts independently within defined boundaries - humans monitor</div>
                        </div>
                        <div class="radio-option" onclick="selectRadio('autonomy', 'autonomous')">
                            <input type="radio" name="autonomy" value="autonomous" id="autonomy_autonomous">
                            <div class="radio-title">Autonomous</div>
                            <div class="radio-description">AI manages entire workflows without oversight - humans only audit periodically</div>
                        </div>
                    </div>
                    <textarea name="autonomy_reasoning" placeholder="Why did you choose this level? (Optional)"></textarea>
                </div>
                
                <!-- Human Oversight -->
                <div class="form-group">
                    <label>🔍 Human Oversight: What level of human involvement exists in the process? *</label>
                    <div class="help-text">
                        Consider when and how humans can intervene in the AI process
                    </div>
                    <div class="radio-group">
                        <div class="radio-option" onclick="selectRadio('oversight', 'continuous')">
                            <input type="radio" name="oversight" value="continuous" id="oversight_continuous">
                            <div class="radio-title">Continuous</div>
                            <div class="radio-description">Human involved in every step/decision - before every AI action</div>
                        </div>
                        <div class="radio-option" onclick="selectRadio('oversight', 'checkpoint')">
                            <input type="radio" name="oversight" value="checkpoint" id="oversight_checkpoint">
                            <div class="radio-title">Checkpoint</div>
                            <div class="radio-description">Human reviews at defined intervals - at milestones or batches</div>
                        </div>
                        <div class="radio-option" onclick="selectRadio('oversight', 'exception')">
                            <input type="radio" name="oversight" value="exception" id="oversight_exception">
                            <div class="radio-title">Exception</div>
                            <div class="radio-description">Human intervention only for edge cases - when AI confidence is low</div>
                        </div>
                        <div class="radio-option" onclick="selectRadio('oversight', 'minimal')">
                            <input type="radio" name="oversight" value="minimal" id="oversight_minimal">
                            <div class="radio-title">Minimal</div>
                            <div class="radio-description">Periodic auditing and monitoring only - monthly reports, annual audits</div>
                        </div>
                    </div>
                    <textarea name="oversight_reasoning" placeholder="Why did you choose this level? (Optional)"></textarea>
                </div>
                
                <!-- Output Impact -->
                <div class="form-group">
                    <label>📊 Output Impact: What is the consequence level of AI decisions/outputs? *</label>
                    <div class="help-text">
                        Think about the worst-case scenario if AI makes a mistake
                    </div>
                    <div class="radio-group">
                        <div class="radio-option" onclick="selectRadio('impact', 'informational')">
                            <input type="radio" name="impact" value="informational" id="impact_informational">
                            <div class="radio-title">Informational</div>
                            <div class="radio-description">Data/insights only - reports, analysis (embarrassing but fixable)</div>
                        </div>
                        <div class="radio-option" onclick="selectRadio('impact', 'operational')">
                            <input type="radio" name="impact" value="operational" id="impact_operational">
                            <div class="radio-title">Operational</div>
                            <div class="radio-description">Affects daily operations - scheduling, routing (disrupts business but contained)</div>
                        </div>
                        <div class="radio-option" onclick="selectRadio('impact', 'strategic')">
                            <input type="radio" name="impact" value="strategic" id="impact_strategic">
                            <div class="radio-title">Strategic</div>
                            <div class="radio-description">Business-critical decisions - investments, hiring (major business impact)</div>
                        </div>
                        <div class="radio-option" onclick="selectRadio('impact', 'external')">
                            <input type="radio" name="impact" value="external" id="impact_external">
                            <div class="radio-title">External</div>
                            <div class="radio-description">Customer/regulatory impact - patient care, financial transactions (affects public/regulators)</div>
                        </div>
                    </div>
                    <textarea name="impact_reasoning" placeholder="Why did you choose this level? (Optional)"></textarea>
                </div>
                
                <!-- Orchestration Type -->
                <div class="form-group">
                    <label>🔧 Orchestration: How are AI agents coordinated in this workflow? *</label>
                    <div class="help-text">
                        Consider the AI architecture and how multiple systems interact
                    </div>
                    <div class="radio-group">
                        <div class="radio-option" onclick="selectRadio('orchestration', 'single')">
                            <input type="radio" name="orchestration" value="single" id="orchestration_single">
                            <div class="radio-title">Single</div>
                            <div class="radio-description">One AI system operating independently - just one AI doing one job</div>
                        </div>
                        <div class="radio-option" onclick="selectRadio('orchestration', 'sequential')">
                            <input type="radio" name="orchestration" value="sequential" id="orchestration_sequential">
                            <div class="radio-title">Sequential</div>
                            <div class="radio-description">Chain of AI tasks in defined order - like LangChain (AI A → AI B → AI C)</div>
                        </div>
                        <div class="radio-option" onclick="selectRadio('orchestration', 'parallel')">
                            <input type="radio" name="orchestration" value="parallel" id="orchestration_parallel">
                            <div class="radio-title">Parallel</div>
                            <div class="radio-description">Multiple AI systems working simultaneously - like AutoGen collaboration</div>
                        </div>
                        <div class="radio-option" onclick="selectRadio('orchestration', 'hierarchical')">
                            <input type="radio" name="orchestration" value="hierarchical" id="orchestration_hierarchical">
                            <div class="radio-title">Hierarchical</div>
                            <div class="radio-description">AI systems managing other AI systems - Master AI controlling worker AIs</div>
                        </div>
                    </div>
                    <textarea name="orchestration_reasoning" placeholder="Why did you choose this type? (Optional)"></textarea>
                </div>
                
                <button type="submit" class="submit-btn" id="submitBtn">Generate Risk Assessment</button>
            </form>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>Analyzing risk profile and generating report...</p>
            </div>
            
            <div class="result" id="result">
                <div id="resultContent"></div>
            </div>
        </div>
    </div>
    
    <script>
        function selectRadio(groupName, value) {
            // Remove selected class from all options in this group
            document.querySelectorAll(`input[name="${groupName}"]`).forEach(radio => {
                radio.parentElement.classList.remove('selected');
            });
            
            // Add selected class to clicked option
            document.getElementById(`${groupName}_${value}`).parentElement.classList.add('selected');
            document.getElementById(`${groupName}_${value}`).checked = true;
        }
        
        document.getElementById('assessmentForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const submitBtn = document.getElementById('submitBtn');
            const loading = document.getElementById('loading');
            const result = document.getElementById('result');
            const resultContent = document.getElementById('resultContent');
            
            // Validate required fields
            const requiredFields = ['workflow_name', 'assessor', 'autonomy', 'oversight', 'impact', 'orchestration'];
            let isValid = true;
            
            for (let field of requiredFields) {
                const input = document.querySelector(`[name="${field}"]`);
                if (field === 'workflow_name' || field === 'assessor') {
                    if (!input.value.trim()) {
                        isValid = false;
                        input.style.borderColor = '#e74c3c';
                    } else {
                        input.style.borderColor = '#e9ecef';
                    }
                } else {
                    if (!document.querySelector(`input[name="${field}"]:checked`)) {
                        isValid = false;
                        // Highlight the radio group
                        document.querySelector(`input[name="${field}"]`).closest('.form-group').style.borderLeft = '4px solid #e74c3c';
                    } else {
                        document.querySelector(`input[name="${field}"]`).closest('.form-group').style.borderLeft = 'none';
                    }
                }
            }
            
            if (!isValid) {
                alert('Please fill in all required fields');
                return;
            }
            
            // Show loading
            submitBtn.disabled = true;
            loading.style.display = 'block';
            result.style.display = 'none';
            
            try {
                const formData = new FormData(this);
                const response = await fetch('/assess', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    const assessment = data.assessment;
                    const riskColors = {
                        'low': '#27ae60',
                        'medium': '#f39c12',
                        'high': '#e74c3c',
                        'critical': '#8e44ad'
                    };
                    
                    const riskEmojis = {
                        'low': '🟢',
                        'medium': '🟡',
                        'high': '🔴',
                        'critical': '🟣'
                    };
                    
                    resultContent.innerHTML = `
                        <h2>Assessment Complete!</h2>
                        <div style="margin: 30px 0; padding: 30px; background: rgba(255,255,255,0.9); border-radius: 15px; border: 3px solid ${riskColors[assessment.overall_risk]};">
                            <h3 style="color: ${riskColors[assessment.overall_risk]}; font-size: 2em; margin-bottom: 10px;">
                                ${riskEmojis[assessment.overall_risk]} ${assessment.overall_risk.toUpperCase()} RISK
                            </h3>
                            <p style="font-size: 1.2em; margin-bottom: 20px;">
                                Risk Score: ${assessment.risk_score} / 16
                            </p>
                            <p style="color: #6c757d;">
                                Workflow: <strong>${assessment.workflow_name}</strong><br>
                                Assessed by: <strong>${assessment.assessor}</strong><br>
                                Date: <strong>${assessment.date}</strong>
                            </p>
                        </div>
                        <p>Your detailed risk assessment report has been generated with specific recommendations for this risk level.</p>
                        <button class="download-btn" onclick="downloadReport()">📄 Download Full Report</button>
                        <button class="download-btn" onclick="location.reload()" style="background: #667eea; margin-left: 10px;">🔄 New Assessment</button>
                    `;
                    
                    result.className = 'result success';
                    result.style.display = 'block';
                    
                    // Store assessment data for download
                    window.assessmentData = data;
                    
                } else {
                    throw new Error(data.error || 'Assessment failed');
                }
                
            } catch (error) {
                resultContent.innerHTML = `
                    <h2>Error</h2>
                    <p style="color: #e74c3c;">Failed to generate assessment: ${error.message}</p>
                    <button class="download-btn" onclick="location.reload()" style="background: #e74c3c;">Try Again</button>
                `;
                result.className = 'result error';
                result.style.display = 'block';
            } finally {
                loading.style.display = 'none';
                submitBtn.disabled = false;
            }
        });
        
        function downloadReport() {
            if (window.assessmentData) {
                // Create and download the HTML report
                const assessment = window.assessmentData.assessment;
                const htmlContent = generateHTMLReport(assessment);
                
                const blob = new Blob([htmlContent], { type: 'text/html' });
                const url = URL.createObjectURL(blob);
                
                const a = document.createElement('a');
                a.href = url;
                a.download = `ai_risk_report_${assessment.workflow_name.replace(/[^a-z0-9]/gi, '_')}_${new Date().toISOString().slice(0,10)}.html`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                
                URL.revokeObjectURL(url);
            }
        }
        
        function generateHTMLReport(assessment) {
            // Generate comprehensive HTML report matching Python script quality
            const riskStyles = {
                "low": {"color": "#27ae60", "bg": "#e6f3e6", "border": "#27ae60"},
                "medium": {"color": "#f39c12", "bg": "#fff3cd", "border": "#f39c12"},
                "high": {"color": "#e74c3c", "bg": "#f8d7da", "border": "#e74c3c"},
                "critical": {"color": "#8e44ad", "bg": "#e2e3f3", "border": "#8e44ad"}
            };
            
            const riskStyle = riskStyles[assessment.overall_risk] || riskStyles.medium;
            const riskPercentage = (assessment.risk_score / 16) * 100;
            
            const dimensionDescriptions = {
                'autonomy': {
                    'tool': 'AI provides recommendations only',
                    'assistant': 'AI executes tasks with human approval',
                    'agent': 'AI acts independently within defined boundaries',
                    'autonomous': 'AI manages entire workflows without oversight'
                },
                'oversight': {
                    'continuous': 'Human involved in every step/decision',
                    'checkpoint': 'Human reviews at defined intervals',
                    'exception': 'Human intervention only for edge cases',
                    'minimal': 'Periodic auditing and monitoring only'
                },
                'impact': {
                    'informational': 'Data/insights only (reports, analysis)',
                    'operational': 'Affects daily operations (scheduling, routing)',
                    'strategic': 'Business-critical decisions (investments, hiring)',
                    'external': 'Customer/regulatory impact (patient care, transactions)'
                },
                'orchestration': {
                    'single': 'One AI system operating independently',
                    'sequential': 'Chain of AI tasks in defined order',
                    'parallel': 'Multiple AI systems working simultaneously',
                    'hierarchical': 'AI systems managing other AI systems'
                }
            };
            
            return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Risk Assessment Report - ${assessment.workflow_name}</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            margin: 0 0 10px 0;
            font-size: 2.2em;
            font-weight: 300;
        }
        
        .header .subtitle {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .content {
            padding: 30px;
        }
        
        .assessment-meta {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        
        .meta-item {
            text-align: center;
        }
        
        .meta-item .label {
            font-size: 0.9em;
            color: #6c757d;
            margin-bottom: 5px;
        }
        
        .meta-item .value {
            font-size: 1.1em;
            font-weight: bold;
            color: #2c3e50;
        }
        
        .risk-overview {
            background: ${riskStyle.bg};
            border: 3px solid ${riskStyle.border};
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 30px;
            text-align: center;
        }
        
        .risk-level {
            font-size: 2.5em;
            font-weight: bold;
            color: ${riskStyle.color};
            margin-bottom: 10px;
            text-transform: uppercase;
        }
        
        .risk-score {
            font-size: 1.3em;
            color: #2c3e50;
        }
        
        .risk-gauge {
            width: 200px;
            height: 100px;
            margin: 20px auto;
            position: relative;
        }
        
        .gauge-bg {
            width: 200px;
            height: 100px;
            border: 8px solid #e9ecef;
            border-bottom: none;
            border-radius: 100px 100px 0 0;
            position: relative;
        }
        
        .gauge-fill {
            width: 200px;
            height: 100px;
            border: 8px solid ${riskStyle.color};
            border-bottom: none;
            border-radius: 100px 100px 0 0;
            position: absolute;
            top: 0;
            left: 0;
            clip: rect(0, ${riskPercentage * 2}px, 100px, 0);
        }
        
        .gauge-text {
            position: absolute;
            top: 70px;
            left: 50%;
            transform: translateX(-50%);
            font-weight: bold;
            color: ${riskStyle.color};
        }
        
        .dimensions-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .dimension-card {
            background: white;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        
        .dimension-card:hover {
            transform: translateY(-5px);
        }
        
        .dimension-title {
            font-size: 1.2em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .dimension-value {
            font-size: 1.1em;
            color: ${riskStyle.color};
            font-weight: bold;
            text-transform: uppercase;
            margin-bottom: 10px;
        }
        
        .dimension-description {
            color: #6c757d;
            font-size: 0.9em;
        }
        
        .recommendations {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 30px;
        }
        
        .recommendations h3 {
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 1.4em;
        }
        
        .recommendation-item {
            background: white;
            border-left: 4px solid ${riskStyle.color};
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 0 8px 8px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .reasoning-section {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 25px;
        }
        
        .reasoning-section h3 {
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 1.4em;
        }
        
        .reasoning-item {
            margin-bottom: 15px;
            padding: 15px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .reasoning-item .question {
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        }
        
        .reasoning-item .answer {
            color: #6c757d;
        }
        
        .footer {
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 15px;
            font-size: 0.9em;
        }
        
        @media print {
            body { background: white; }
            .container { box-shadow: none; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>AI Risk Assessment Report</h1>
            <div class="subtitle">${assessment.workflow_name}</div>
        </div>
        
        <div class="content">
            <div class="assessment-meta">
                <div class="meta-item">
                    <div class="label">Assessed By</div>
                    <div class="value">${assessment.assessor}</div>
                </div>
                <div class="meta-item">
                    <div class="label">Assessment Date</div>
                    <div class="value">${assessment.date}</div>
                </div>
                <div class="meta-item">
                    <div class="label">Workflow Type</div>
                    <div class="value">AI ${assessment.orchestration_type.charAt(0).toUpperCase() + assessment.orchestration_type.slice(1)} System</div>
                </div>
            </div>
            
            <div class="risk-overview">
                <div class="risk-level">${assessment.overall_risk} Risk</div>
                <div class="risk-score">Risk Score: ${assessment.risk_score} / 16</div>
                <div class="risk-gauge">
                    <div class="gauge-bg"></div>
                    <div class="gauge-fill"></div>
                    <div class="gauge-text">${Math.round(riskPercentage)}%</div>
                </div>
            </div>
            
            <h2>Risk Assessment Dimensions</h2>
            <div class="dimensions-grid">
                <div class="dimension-card">
                    <div class="dimension-title">🎯 Autonomy Level</div>
                    <div class="dimension-value">${assessment.autonomy_level}</div>
                    <div class="dimension-description">
                        ${dimensionDescriptions.autonomy[assessment.autonomy_level] || 'Unknown'}
                    </div>
                </div>
                
                <div class="dimension-card">
                    <div class="dimension-title">🔍 Human Oversight</div>
                    <div class="dimension-value">${assessment.oversight_level}</div>
                    <div class="dimension-description">
                        ${dimensionDescriptions.oversight[assessment.oversight_level] || 'Unknown'}
                    </div>
                </div>
                
                <div class="dimension-card">
                    <div class="dimension-title">📊 Output Impact</div>
                    <div class="dimension-value">${assessment.impact_level}</div>
                    <div class="dimension-description">
                        ${dimensionDescriptions.impact[assessment.impact_level] || 'Unknown'}
                    </div>
                </div>
                
                <div class="dimension-card">
                    <div class="dimension-title">🔧 Orchestration</div>
                    <div class="dimension-value">${assessment.orchestration_type}</div>
                    <div class="dimension-description">
                        ${dimensionDescriptions.orchestration[assessment.orchestration_type] || 'Unknown'}
                    </div>
                </div>
            </div>
            
            <div class="recommendations">
                <h3>Recommended Actions</h3>
                ${assessment.recommendations.map(rec => `<div class="recommendation-item">${rec}</div>`).join('')}
            </div>
            
            <div class="reasoning-section">
                <h3>Assessment Reasoning</h3>
                <div class="reasoning-item">
                    <div class="question">Autonomy Level Justification:</div>
                    <div class="answer">${assessment.responses?.autonomy_reasoning || 'Not provided'}</div>
                </div>
                <div class="reasoning-item">
                    <div class="question">Oversight Level Justification:</div>
                    <div class="answer">${assessment.responses?.oversight_reasoning || 'Not provided'}</div>
                </div>
                <div class="reasoning-item">
                    <div class="question">Impact Level Justification:</div>
                    <div class="answer">${assessment.responses?.impact_reasoning || 'Not provided'}</div>
                </div>
                <div class="reasoning-item">
                    <div class="question">Orchestration Type Justification:</div>
                    <div class="answer">${assessment.responses?.orchestration_reasoning || 'Not provided'}</div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            Generated by AI Risk Assessment Tool | ${assessment.date}
        </div>
    </div>
</body>
</html>`;
        }
    </script>
</body>
</html>
    """
    
    # Write template file
    with open('templates/assessment_form.html', 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print("Starting AI Risk Assessment Web Application...")
    print("Open your browser and go to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)