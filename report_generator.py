#!/usr/bin/env python3
"""
Report Generator for AI Risk Assessment
Creates beautiful, comprehensive HTML reports
"""

import yaml
from typing import Dict, Any
from dataclasses import dataclass
from datetime import datetime
from questions_loader import questions_loader

class ReportGenerator:
    def __init__(self, scoring_file: str = 'scoring.yaml', questions_dir: str = 'questions'):
        """Initialize with configuration files"""
        with open(scoring_file, 'r') as f:
            self.scoring_config = yaml.safe_load(f)
        
        self.questions_config = questions_loader.load_all_questions()
        
        self.risk_styling = self.scoring_config['risk_styling']
        self.dimension_scores = self.scoring_config['scoring']['dimensions']

    def get_dimension_description(self, dimension: str, value: str) -> str:
        """Get description for dimension values"""
        questions = self.questions_config['questions']
        if dimension in questions and value in questions[dimension]['options']:
            return questions[dimension]['options'][value]['description']
        return 'Unknown'

    def get_dimension_title(self, dimension: str) -> str:
        """Get title for dimension"""
        dimension_titles = {
            'autonomy': '🎯 Autonomy Level',
            'oversight': '🔍 Human Oversight', 
            'impact': '📊 Output Impact',
            'orchestration': '🔧 Orchestration',
            'data_sensitivity': '🔒 Data Sensitivity'
        }
        return dimension_titles.get(dimension, dimension.title())

    def get_individual_risk_level(self, score: int) -> str:
        """Get risk level for individual dimension score (1-4 scale)"""
        if score == 1:
            return "low"
        elif score == 2:
            return "medium"
        elif score == 3:
            return "high"
        elif score == 4:
            return "critical"
        return "medium"  # fallback

    def generate_comprehensive_report(self, assessment: Any) -> str:
        """Generate a comprehensive, beautiful HTML report"""
        risk_style = self.risk_styling.get(assessment.overall_risk, self.risk_styling['medium'])
        
        # Calculate max possible score dynamically
        max_score = len(self.dimension_scores) * 4
        risk_percentage = (assessment.risk_score / max_score) * 100
        
        # Generate dimension cards
        dimension_cards = ""
        dimension_data = {
            'autonomy': assessment.autonomy_level,
            'oversight': assessment.oversight_level,
            'impact': assessment.impact_level,
            'orchestration': assessment.orchestration_type
        }
        
        # Add data sensitivity if it exists
        if hasattr(assessment, 'data_sensitivity_level') and assessment.data_sensitivity_level:
            dimension_data['data_sensitivity'] = assessment.data_sensitivity_level

        for dimension, value in dimension_data.items():
            if dimension in self.dimension_scores and value in self.dimension_scores[dimension]:
                score = self.dimension_scores[dimension][value]
                # Get individual risk level and color for this dimension
                individual_risk = self.get_individual_risk_level(score)
                individual_style = self.risk_styling.get(individual_risk, self.risk_styling['medium'])
                
                dimension_cards += f'''
                                <div class="dimension-card">
                <div class="dimension-header">
                    <div class="dimension-title">{self.get_dimension_title(dimension)}</div>
                    <div class="dimension-score" style="background: {individual_style['color']};">{score}/4</div>
                </div>
                <div class="dimension-value" style="color: {individual_style['color']};">{value.upper()}</div>
                        <div class="dimension-description">
                            {self.get_dimension_description(dimension, value)}
                        </div>
                        <div class="score-bar">
                            <div class="score-fill" style="width: {(score/4)*100}%; background: {individual_style['color']};"></div>
                        </div>
                    </div>
                '''

        # Generate recommendations
        recommendations_html = ""
        for i, rec in enumerate(assessment.recommendations):
            priority_class = "high-priority" if "HIGH PRIORITY" in rec or "CRITICAL" in rec else "normal-priority"
            recommendations_html += f'''
                <div class="recommendation-item {priority_class}">
                    <div class="recommendation-number">{i+1}</div>
                    <div class="recommendation-text">{rec}</div>
                </div>
            '''

        # Generate reasoning cards
        reasoning_cards = ""
        reasoning_data = {
            'Autonomy Level': assessment.responses.get('autonomy_reasoning', 'Not provided'),
            'Oversight Level': assessment.responses.get('oversight_reasoning', 'Not provided'),
            'Impact Level': assessment.responses.get('impact_reasoning', 'Not provided'),
            'Orchestration Type': assessment.responses.get('orchestration_reasoning', 'Not provided')
        }
        
        if 'data_sensitivity_reasoning' in assessment.responses:
            reasoning_data['Data Sensitivity'] = assessment.responses.get('data_sensitivity_reasoning', 'Not provided')

        for question, answer in reasoning_data.items():
            reasoning_cards += f'''
                <div class="reasoning-card">
                    <div class="reasoning-question">{question} Justification:</div>
                    <div class="reasoning-answer">{answer if answer else 'Not provided'}</div>
                </div>
            '''

        # Risk assessment summary
        risk_summary = self._get_risk_summary(assessment.overall_risk)
        
        # Generate executive summary
        exec_summary = self._generate_executive_summary(assessment)

        html_content = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Risk Assessment Report - {assessment.workflow_name}</title>
    <link rel="icon" type="image/svg+xml" href="/favicon.ico">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #2c3e50;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .report-container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .report-header {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 40px;
            border-radius: 20px 20px 0 0;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        
        .report-title {{
            font-size: 3em;
            font-weight: 300;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .report-subtitle {{
            font-size: 1.4em;
            opacity: 0.9;
            font-weight: 300;
        }}
        
        .report-meta {{
            background: white;
            padding: 30px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 30px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .meta-card {{
            text-align: center;
            padding: 20px;
            border-radius: 15px;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border: 2px solid transparent;
            transition: all 0.3s ease;
        }}
        
        .meta-card:hover {{
            border-color: {risk_style['color']};
            transform: translateY(-5px);
        }}
        
        .meta-label {{
            font-size: 0.9em;
            color: #6c757d;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .meta-value {{
            font-size: 1.3em;
            font-weight: bold;
            color: #2c3e50;
        }}
        
        .risk-overview {{
            background: {risk_style['bg']};
            border: 4px solid {risk_style['border']};
            border-radius: 20px;
            padding: 40px;
            margin: 30px 0;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}
        
        .risk-overview::before {{
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            animation: shimmer 3s ease-in-out infinite;
        }}
        
        @keyframes shimmer {{
            0%, 100% {{ transform: rotate(0deg); }}
            50% {{ transform: rotate(180deg); }}
        }}
        
        .risk-badge {{
            display: inline-flex;
            align-items: center;
            gap: 15px;
            background: rgba(255,255,255,0.9);
            padding: 20px 40px;
            border-radius: 50px;
            margin-bottom: 30px;
            position: relative;
            z-index: 1;
        }}
        
        .risk-emoji {{
            font-size: 3em;
        }}
        
        .risk-level {{
            font-size: 2.5em;
            font-weight: bold;
            color: {risk_style['color']};
            text-transform: uppercase;
        }}
        
        .risk-score {{
            font-size: 1.5em;
            color: #2c3e50;
            margin-bottom: 20px;
            position: relative;
            z-index: 1;
        }}
        
        .risk-gauge {{
            width: 280px;
            height: 140px;
            margin: 20px auto;
            position: relative;
            z-index: 1;
        }}
        
        .gauge-container {{
            position: relative;
            width: 280px;
            height: 140px;
        }}
        
        .gauge-bg {{
            width: 280px;
            height: 140px;
            border: 8px solid #f0f0f0;
            border-bottom: none;
            border-radius: 140px 140px 0 0;
            position: absolute;
            background: transparent;
        }}
        
        .gauge-track {{
            width: 280px;
            height: 140px;
            position: absolute;
            border-radius: 140px 140px 0 0;
            overflow: hidden;
        }}
        
        .gauge-track::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: conic-gradient(from 180deg, #27ae60 0deg, #f39c12 90deg, #e74c3c 180deg);
            border-radius: 140px 140px 0 0;
            opacity: 0.3;
        }}
        
        .gauge-fill {{
            width: 280px;
            height: 140px;
            position: absolute;
            top: 0;
            left: 0;
            border-radius: 140px 140px 0 0;
            overflow: hidden;
        }}
        
        .gauge-fill::after {{
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 4px;
            height: 120px;
            background: {risk_style['color']};
            transform-origin: bottom center;
            transform: translate(-50%, -100%) rotate({-90 + (risk_percentage * 180 / 100)}deg);
            border-radius: 2px;
            box-shadow: 0 0 10px {risk_style['color']};
        }}
        
        .gauge-center {{
            position: absolute;
            top: 120px;
            left: 50%;
            transform: translateX(-50%);
            width: 16px;
            height: 16px;
            background: {risk_style['color']};
            border-radius: 50%;
            box-shadow: 0 0 8px {risk_style['color']};
        }}
        
        .gauge-text {{
            position: absolute;
            top: 100px;
            left: 50%;
            transform: translateX(-50%);
            font-weight: bold;
            font-size: 1.2em;
            color: {risk_style['color']};
            text-align: center;
        }}
        
        .executive-summary {{
            background: white;
            border-radius: 20px;
            padding: 40px;
            margin: 30px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        .section-title {{
            font-size: 2.2em;
            margin-bottom: 30px;
            color: #2c3e50;
            border-bottom: 3px solid {risk_style['color']};
            padding-bottom: 15px;
        }}
        
        .summary-grid {{
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 40px;
            align-items: start;
        }}
        
        .summary-text {{
            font-size: 1.1em;
            line-height: 1.8;
            color: #4a5568;
        }}
        
        .risk-indicators {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 15px;
            padding: 25px;
        }}
        
        .indicator {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid #dee2e6;
        }}
        
        .indicator:last-child {{
            border-bottom: none;
        }}
        
        .indicator-label {{
            font-weight: 600;
            color: #495057;
        }}
        
        .indicator-value {{
            font-weight: bold;
            color: {risk_style['color']};
        }}
        
        .dimensions-section {{
            background: white;
            border-radius: 20px;
            padding: 40px;
            margin: 30px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        .dimensions-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 25px;
            margin-top: 30px;
        }}
        
        .dimension-card {{
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            border: 2px solid #e9ecef;
            border-radius: 15px;
            padding: 25px;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}
        
        .dimension-card:hover {{
            transform: translateY(-8px);
            box-shadow: 0 15px 35px rgba(0,0,0,0.15);
            border-color: {risk_style['color']};
        }}
        
        .dimension-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        
        .dimension-title {{
            font-size: 1.3em;
            font-weight: bold;
            color: #2c3e50;
        }}
        
        .dimension-score {{
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
        }}
        
        .dimension-value {{
            font-size: 1.4em;
            font-weight: bold;
            color: {risk_style['color']};
            text-transform: uppercase;
            margin-bottom: 15px;
            letter-spacing: 1px;
        }}
        
        .dimension-description {{
            color: #6c757d;
            line-height: 1.6;
            margin-bottom: 20px;
        }}
        
        .score-bar {{
            width: 100%;
            height: 8px;
            background: #e9ecef;
            border-radius: 4px;
            overflow: hidden;
        }}
        
        .score-fill {{
            height: 100%;
            border-radius: 4px;
            transition: width 0.8s ease;
        }}
        
        .recommendations-section {{
            background: white;
            border-radius: 20px;
            padding: 40px;
            margin: 30px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        .recommendation-item {{
            display: flex;
            align-items: flex-start;
            gap: 20px;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 15px;
            border-left: 5px solid {risk_style['color']};
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            transition: all 0.3s ease;
        }}
        
        .recommendation-item:hover {{
            transform: translateX(10px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        }}
        
        .recommendation-item.high-priority {{
            border-left-color: #e74c3c;
            background: linear-gradient(135deg, #fff5f5 0%, #fed7d7 100%);
        }}
        
        .recommendation-number {{
            background: {risk_style['color']};
            color: white;
            width: 35px;
            height: 35px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            flex-shrink: 0;
        }}
        
        .high-priority .recommendation-number {{
            background: #e74c3c;
        }}
        
        .recommendation-text {{
            flex: 1;
            line-height: 1.6;
            color: #4a5568;
            font-weight: 500;
        }}
        
        .reasoning-section {{
            background: white;
            border-radius: 20px;
            padding: 40px;
            margin: 30px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        .reasoning-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 25px;
            margin-top: 30px;
        }}
        
        .reasoning-card {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 15px;
            padding: 25px;
            border: 2px solid transparent;
            transition: all 0.3s ease;
        }}
        
        .reasoning-card:hover {{
            border-color: {risk_style['color']};
            transform: translateY(-5px);
        }}
        
        .reasoning-question {{
            font-size: 1.1em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .reasoning-question::before {{
            content: "💭";
            font-size: 1.2em;
        }}
        
        .reasoning-answer {{
            color: #4a5568;
            line-height: 1.6;
            font-style: italic;
            padding: 15px;
            background: white;
            border-radius: 10px;
            border-left: 4px solid {risk_style['color']};
        }}
        
        .report-footer {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            text-align: center;
            padding: 30px;
            border-radius: 0 0 20px 20px;
            box-shadow: 0 -5px 15px rgba(0,0,0,0.1);
        }}
        
        .footer-content {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 20px;
        }}
        
        .footer-logo {{
            font-size: 1.2em;
            font-weight: bold;
        }}
        
        .footer-timestamp {{
            font-size: 0.9em;
            opacity: 0.8;
        }}
        
        @media print {{
            body {{ background: white; }}
            .report-container {{ padding: 0; }}
            .report-header, .report-footer {{ background: #2c3e50 !important; }}
        }}
        
        @media (max-width: 768px) {{
            .report-title {{ font-size: 2em; }}
            .summary-grid {{ grid-template-columns: 1fr; }}
            .dimensions-grid {{ grid-template-columns: 1fr; }}
            .reasoning-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="report-container">
        <!-- Header -->
        <div class="report-header">
            <div class="report-title">AI Risk Assessment Report</div>
            <div class="report-subtitle">{assessment.workflow_name}</div>
        </div>
        
        <!-- Meta Information -->
        <div class="report-meta">
            <div class="meta-card">
                <div class="meta-label">Assessed By</div>
                <div class="meta-value">{assessment.assessor}</div>
            </div>
            <div class="meta-card">
                <div class="meta-label">Assessment Date</div>
                <div class="meta-value">{assessment.date}</div>
            </div>
            <div class="meta-card">
                <div class="meta-label">Workflow Type</div>
                <div class="meta-value">AI {assessment.orchestration_type.title()} System</div>
            </div>
            <div class="meta-card">
                <div class="meta-label">Report ID</div>
                <div class="meta-value">RA-{datetime.now().strftime("%Y%m%d-%H%M%S")}</div>
            </div>
        </div>
        
        <!-- Risk Overview -->
        <div class="risk-overview">
            <div class="risk-badge">

                <span class="risk-level">{assessment.overall_risk} Risk</span>
            </div>
            <div class="risk-score">Risk Score: {assessment.risk_score} / {max_score}</div>
            <div class="risk-gauge">
                <div class="gauge-container">
                    <div class="gauge-track"></div>
                    <div class="gauge-bg"></div>
                    <div class="gauge-fill"></div>
                    <div class="gauge-center"></div>
                    <div class="gauge-text">{risk_percentage:.0f}%</div>
                </div>
            </div>
        </div>
        
        <!-- Executive Summary -->
        <div class="executive-summary">
            <h2 class="section-title">Executive Summary</h2>
            <div class="summary-grid">
                <div class="summary-text">
                    {exec_summary}
                </div>
                <div class="risk-indicators">
                    <div class="indicator">
                        <span class="indicator-label">Risk Level</span>
                        <span class="indicator-value">{assessment.overall_risk.upper()}</span>
                    </div>
                    <div class="indicator">
                        <span class="indicator-label">Total Score</span>
                        <span class="indicator-value">{assessment.risk_score}/{max_score}</span>
                    </div>
                    <div class="indicator">
                        <span class="indicator-label">Recommendations</span>
                        <span class="indicator-value">{len(assessment.recommendations)}</span>
                    </div>
                    <div class="indicator">
                        <span class="indicator-label">Dimensions</span>
                        <span class="indicator-value">{len(dimension_data)}</span>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Risk Assessment Dimensions -->
        <div class="dimensions-section">
            <h2 class="section-title">Risk Assessment Dimensions</h2>
            <div class="dimensions-grid">
                {dimension_cards}
            </div>
        </div>
        
        <!-- Recommendations -->
        <div class="recommendations-section">
            <h2 class="section-title">Recommended Actions</h2>
            {recommendations_html}
        </div>
        
        <!-- Assessment Reasoning -->
        <div class="reasoning-section">
            <h2 class="section-title">Assessment Reasoning</h2>
            <div class="reasoning-grid">
                {reasoning_cards}
            </div>
        </div>
        
        <!-- Footer -->
        <div class="report-footer">
            <div class="footer-content">
                <div class="footer-logo">🤖 AI Risk Assessment Tool</div>
                <div class="footer-timestamp">Generated on {assessment.date}</div>
            </div>
            <div style="text-align: center; margin-top: 20px;">
                <a href="/" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 30px; border-radius: 25px; text-decoration: none; font-weight: bold; display: inline-block; transition: transform 0.3s ease;" onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
                    🔄 New Assessment
                </a>
            </div>
        </div>
    </div>
</body>
</html>
        '''
        
        return html_content

    def _get_risk_summary(self, risk_level: str) -> str:
        """Get risk level summary description"""
        summaries = {
            'low': 'This AI system presents minimal risk to your organization. Standard monitoring and review processes should be sufficient.',
            'medium': 'This AI system presents moderate risk requiring enhanced oversight and monitoring procedures.',
            'high': 'This AI system presents significant risk requiring comprehensive monitoring, clear escalation procedures, and dedicated oversight.',
            'critical': 'This AI system presents critical risk requiring extensive safeguards, formal approval processes, and continuous monitoring.'
        }
        return summaries.get(risk_level, 'Risk level assessment unavailable.')

    def _generate_executive_summary(self, assessment: Any) -> str:
        """Generate executive summary based on assessment"""
        # Determine key risk factors
        high_risk_factors = []
        if hasattr(assessment, 'autonomy_level') and assessment.autonomy_level in ['agent', 'autonomous']:
            high_risk_factors.append('high autonomy')
        if hasattr(assessment, 'impact_level') and assessment.impact_level in ['strategic', 'external']:
            high_risk_factors.append('significant impact potential')
        if hasattr(assessment, 'oversight_level') and assessment.oversight_level in ['exception', 'minimal']:
            high_risk_factors.append('limited human oversight')
        
        summary = f"The '{assessment.workflow_name}' AI system has been assessed as <strong>{assessment.overall_risk.upper()} RISK</strong> "
        summary += f"with a score of {assessment.risk_score} out of {len(self.dimension_scores) * 4}. "
        
        if high_risk_factors:
            summary += f"Key risk factors include: {', '.join(high_risk_factors)}. "
        
        summary += f"This assessment has generated {len(assessment.recommendations)} specific recommendations "
        summary += "to help mitigate identified risks and ensure safe deployment. "
        
        if assessment.overall_risk in ['high', 'critical']:
            summary += "<strong>Immediate attention and enhanced safeguards are strongly recommended before deployment.</strong>"
        elif assessment.overall_risk == 'medium':
            summary += "Regular monitoring and implementation of recommended safeguards is advised."
        else:
            summary += "Standard monitoring procedures should be sufficient for this risk level."
            
        return summary 