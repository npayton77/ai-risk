#!/usr/bin/env python3
"""
AI Risk Assessment Web Application - Refactored Version
Web frontend for the AI risk assessment tool using YAML configuration
"""

from flask import Flask, render_template_string, request, jsonify, send_file, redirect, url_for, Response, session
import json
import os
import yaml
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple
import tempfile
from template_generator import TemplateGenerator
from report_generator import ReportGenerator

from email_sender import EmailSender
from questions_loader import questions_loader
from risk_assessor import RiskAssessment as OriginalRiskAssessment, AIRiskAssessor
from flexible_risk_assessor import RiskAssessment as FlexibleRiskAssessment, FlexibleAIRiskAssessor
from email_handlers import generate_complete_email_report, generate_short_email_report
from static_pages import generate_system_info_page, generate_email_info_page
from multistep_template_generator import MultiStepTemplateGenerator
from admin_interface import admin_interface
# Flask Web Application
app = Flask(__name__)
app.secret_key = 'ai-risk-assessment-secret-key-2024'  # Change this in production

# Configure session settings
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialize components
template_generator = TemplateGenerator()
multistep_generator = MultiStepTemplateGenerator()
risk_assessor = AIRiskAssessor()  # Keep old one for backward compatibility
flexible_risk_assessor = FlexibleAIRiskAssessor()  # New flexible assessor
report_generator = ReportGenerator()

email_sender = EmailSender()

# Register admin interface blueprint
app.register_blueprint(admin_interface.bp)

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
    """Redirect to step 1 of the multi-step assessment"""
    # Clear any existing session data for fresh start
    session.clear()
    return redirect('/step/1')

@app.route('/step/<int:step_number>', methods=['GET', 'POST'])
def step_handler(step_number):
    """Handle multi-step assessment flow"""
    try:
        # Validate step number
        if step_number < 1 or step_number > multistep_generator.total_steps:
            return redirect('/step/1')
        
        # Initialize session data if needed
        if 'assessment_data' not in session:
            session['assessment_data'] = {}
        
        # Ensure session is marked as modified
        session.modified = True
        
        if request.method == 'GET':
            # Display the step
            html_content = multistep_generator.generate_step_page(
                step_number, 
                session.get('assessment_data', {}),
                session.pop('step_errors', None)
            )
            return html_content
        
        elif request.method == 'POST':
            # Process the step submission
            return process_step_submission(step_number)
            
    except Exception as e:
        return f"<html><body><h1>Error</h1><p>Step processing failed: {str(e)}</p><a href='/step/1'>Start Over</a></body></html>"

def process_step_submission(step_number):
    """Process form submission for a specific step"""
    errors = {}
    step_key = multistep_generator.steps[step_number - 1]['key']
    

    
    # Validate and store step data
    if step_key == 'basic_info':
        # Process basic information
        workflow_name = request.form.get('workflow_name', '').strip()
        assessor = request.form.get('assessor', '').strip()
        
        if not workflow_name:
            errors['workflow_name'] = 'Workflow/System name is required'
        if not assessor:
            errors['assessor'] = 'Assessor name is required'
        
        if not errors:
            session['assessment_data']['workflow_name'] = workflow_name
            session['assessment_data']['assessor'] = assessor
            session.modified = True

    
    else:
        # Process question step - handle multiple questions per step
        # Get current step configuration from template generator
        current_config = multistep_generator.get_current_config()
        
        # Find all questions that belong to this step/dimension
        step_questions = []
        for question_id, question_config in current_config['questions'].items():
            if question_config.get('_dimension') == step_key:
                step_questions.append(question_id)
        
        # Process each question in this step
        step_has_answers = False
        for question_id in step_questions:
            question_value = request.form.get(question_id, '').strip()
            reasoning_value = request.form.get(f'{question_id}_reasoning', '').strip()
            
            if question_value:
                session['assessment_data'][question_id] = question_value
                session['assessment_data'][f'{question_id}_reasoning'] = reasoning_value
                step_has_answers = True
        
        # Validate that at least one question was answered
        if not step_has_answers:
            errors[step_key] = 'Please answer at least one question'
        
        if not errors:
            session.modified = True

    
    # Handle validation errors
    if errors:
        session['step_errors'] = errors
        return redirect(f'/step/{step_number}')
    
    # Move to next step or generate report
    if step_number < multistep_generator.total_steps:
        return redirect(f'/step/{step_number + 1}')
    else:
        # Final step - generate the assessment report
        return generate_final_assessment()

def generate_final_assessment():
    """Generate the final assessment report from session data"""
    try:
        assessment_data = session.get('assessment_data', {})
        
<<<<<<< HEAD
=======
        # Always reload configs to reflect latest admin changes
        flexible_risk_assessor.reload_configs()
        
        # DEBUG: Log all assessment data
        print(f"\n🔍 DEBUG - FINAL ASSESSMENT DATA:")
        for key, value in assessment_data.items():
            print(f"  {key}: {value}")
        print(f"🔍 END DEBUG\n")
        
>>>>>>> questions4
        # Validate basic required data
        basic_required = ['workflow_name', 'assessor']
        missing_basic = [field for field in basic_required if not assessment_data.get(field)]
        if missing_basic:
            session['step_errors'] = {field: 'This field is required' for field in missing_basic}
            return redirect('/step/1')
        
        # Extract basic form data
        workflow_name = assessment_data['workflow_name']
        assessor = assessment_data['assessor']
        
        # Use flexible risk assessor to handle multiple questions per dimension
        risk_score, risk_level, dimension_scores, question_scores = flexible_risk_assessor.calculate_flexible_risk_score(assessment_data)
        
        # Generate recommendations using the flexible assessor
        recommendations = flexible_risk_assessor.get_recommendations(risk_level)
        conditional_recommendations = flexible_risk_assessor.get_conditional_recommendations(assessment_data)
        # Combine both types of recommendations
        all_recommendations = recommendations + conditional_recommendations
        
        # Create assessment object with all responses from assessment_data
        responses_dict = {}
        
        # Extract ALL fields from assessment_data (answers and reasoning)
        for key, value in assessment_data.items():
            if key not in ['workflow_name', 'assessor']:  # Exclude meta fields
                responses_dict[key] = value.strip() if value else 'Not provided'
        
        # Extract primary dimension values for backward compatibility with reports
        # Use the primary question for each dimension (the one matching the dimension name)
        autonomy = assessment_data.get('autonomy', 'unknown')
        oversight = assessment_data.get('oversight', 'unknown')  
        impact = assessment_data.get('impact', 'unknown')
        orchestration = assessment_data.get('orchestration', 'unknown')
        data_sensitivity = assessment_data.get('data_sensitivity', 'unknown')
        
        # Get questions config for report generation
        questions_config = multistep_generator.get_current_config()
        
        # Create FlexibleRiskAssessment with the new structure
        assessment = FlexibleRiskAssessment(
            workflow_name=workflow_name,
            assessor=assessor,
            autonomy=autonomy,
            oversight=oversight,
            impact=impact,
            orchestration=orchestration,
            data_sensitivity=data_sensitivity,
            risk_score=risk_score,
            risk_level=risk_level,
            recommendations=all_recommendations,
            conditional_recommendations=conditional_recommendations,
            dimension_scores=dimension_scores,
            question_scores=question_scores,
            responses=responses_dict,
            date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            questions_config=questions_config
        )
        
        # Store assessment in session for the report page
        session_id = f"assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(assessment.workflow_name) % 10000}"
        app.config[session_id] = assessment
        
        # Clear the session data
        session.pop('assessment_data', None)
        session.pop('step_errors', None)
        
        # Redirect to the beautiful report page
        return redirect(f'/report/{session_id}')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/assess', methods=['POST'])
def assess_risk():
    """Legacy route - redirect to step-based flow"""
    return redirect('/step/1')

# Keep the original single-page route for backward compatibility
@app.route('/single-page')
def single_page_assessment():
    """Legacy single-page assessment form"""
    html_content = template_generator.generate_assessment_form()
    return render_template_string(html_content)

@app.route('/single-page/assess', methods=['POST'])
def single_page_assess_risk():
    """Process the legacy single-page risk assessment form"""
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
        
        assessment = OriginalRiskAssessment(
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
        
        assessment = OriginalRiskAssessment(
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
        action_buttons = f'''
        <div style="position: fixed; top: 20px; right: 20px; z-index: 1000; display: flex; flex-direction: column; gap: 10px;">
            
            <!-- Email Dropdown -->
            <div class="email-dropdown" style="position: relative;">
                <button onclick="toggleEmailMenu()" style="background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); color: white; padding: 12px 20px; border: none; border-radius: 25px; cursor: pointer; font-weight: bold; box-shadow: 0 4px 15px rgba(52,152,219,0.3); transition: all 0.3s ease; font-size: 14px; display: flex; align-items: center; gap: 8px;" onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 20px rgba(52,152,219,0.4)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 15px rgba(52,152,219,0.3)'">
                    Email Report <span id="email-arrow">▼</span>
                </button>
                <div id="email-menu" style="position: absolute; top: 100%; right: 0; background: white; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.2); overflow: hidden; min-width: 250px; z-index: 1001; display: none;">
                    <button onclick="quickEmail()" style="width: 100%; padding: 15px; border: none; background: white; text-align: left; cursor: pointer; border-bottom: 1px solid #eee; transition: background 0.2s;" onmouseover="this.style.background='#f8f9fa'" onmouseout="this.style.background='white'">
                        <strong>Quick Email</strong><br>
                        <small style="color: #666;">Send short summary via email client</small>
                    </button>
                    <button onclick="downloadForEmail()" style="width: 100%; padding: 15px; border: none; background: white; text-align: left; cursor: pointer; transition: background 0.2s;" onmouseover="this.style.background='#f8f9fa'" onmouseout="this.style.background='white'">
                        <strong>Download for Attachment</strong><br>
                        <small style="color: #666;">Download HTML file to attach to email</small>
                    </button>
                </div>
            </div>
            
            <button onclick="location.href='/'" style="background: linear-gradient(135deg, #27ae60 0%, #229954 100%); color: white; padding: 12px 20px; border: none; border-radius: 25px; cursor: pointer; font-weight: bold; box-shadow: 0 4px 15px rgba(39,174,96,0.3); transition: all 0.3s ease; font-size: 14px;" onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 20px rgba(39,174,96,0.4)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 15px rgba(39,174,96,0.3)'">
                New Assessment
            </button>
        </div>
        
        <script>
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
    """Display system information"""
    return generate_system_info_page()

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
        print(f"Successfully loaded {len(questions_config['questions'])} question categories from {questions_dir}/ directory")
    except Exception as e:
        print(f"Error: Failed to load questions from {questions_dir}/ directory: {e}")
        exit(1)
    
    print("Starting AI Risk Assessment Web Application (Multi-Step Wizard)...")
    print("Configuration loaded from YAML files:")
    print("- questions/ directory: Individual question files for each assessment dimension")
    print("- scoring.yaml: Risk scoring and recommendations")
    print("✨ New Multi-Step Wizard Features:")
    print("Step-by-step guided assessment")
    print("Progress tracking with visual indicators")
    print("Session-based data persistence")
    print("Forward/backward navigation")
    print("Per-step validation")
    print("Other features:")
    print("HTML report generation: Enabled")
    print("Email report functionality (mailto: links)")
    print("Modern UI enhancements")
    print("")
    print("Multi-Step Assessment: http://localhost:9000")
    print("Legacy Single-Page: http://localhost:9000/single-page")  
    print("System info: http://localhost:9000/system_info")
    print("Email info: http://localhost:9000/email_info")
    app.run(debug=True, host='0.0.0.0', port=9000) 