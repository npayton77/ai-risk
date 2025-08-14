#!/usr/bin/env python3
"""
Multi-Step Template Generator for AI Risk Assessment
Creates step-by-step wizard pages for better user experience
"""

from typing import Dict, Any, List
from questions_loader import questions_loader

class MultiStepTemplateGenerator:
    def __init__(self):
        """Initialize with questions configuration"""
        # Don't cache questions at init - load them fresh each time
        # self.config = questions_loader.load_all_questions()
        
        # Define the step order and configuration
        self.steps = [
            {'key': 'basic_info', 'title': 'Assessment Information', 'subtitle': 'Basic details about your assessment'},
            {'key': 'autonomy', 'title': 'Autonomy Level', 'subtitle': 'How much decision-making power does the AI have?'},
            {'key': 'oversight', 'title': 'Human Oversight', 'subtitle': 'What level of human involvement exists?'},
            {'key': 'impact', 'title': 'Output Impact', 'subtitle': 'What are the consequences of AI decisions?'},
            {'key': 'orchestration', 'title': 'Orchestration', 'subtitle': 'How are AI agents coordinated?'},
            {'key': 'data_sensitivity', 'title': 'Data Sensitivity', 'subtitle': 'What type of data does the AI process?'}
        ]
        
        self.total_steps = len(self.steps)
    
    def get_current_config(self):
        """Get fresh questions configuration (reloads from files each time)"""
        return questions_loader.load_all_questions()

    def generate_step_page(self, step_number: int, session_data: Dict = None, errors: Dict = None) -> str:
        """Generate HTML for a specific step"""
        if step_number < 1 or step_number > self.total_steps:
            raise ValueError(f"Step number must be between 1 and {self.total_steps}")
        
        step_config = self.steps[step_number - 1]
        step_key = step_config['key']
        
        # Generate step content based on step type
        if step_key == 'basic_info':
            content = self._generate_basic_info_content(session_data, errors)
        else:
            content = self._generate_dimension_content(step_key, session_data, errors)
        
        # Generate navigation buttons
        nav_buttons = self._generate_navigation_buttons(step_number)
        
        # Generate progress indicator
        progress_bar = self._generate_progress_bar(step_number)
        
        return self._get_step_template(step_config, content, nav_buttons, progress_bar, step_number)

    def _generate_basic_info_content(self, session_data: Dict = None, errors: Dict = None) -> str:
        """Generate basic information form content"""
        workflow_value = session_data.get('workflow_name', '') if session_data else ''
        assessor_value = session_data.get('assessor', '') if session_data else ''
        
        workflow_error = errors.get('workflow_name', '') if errors else ''
        assessor_error = errors.get('assessor', '') if errors else ''
        
        return f'''
            <div class="step-content">
                <div class="form-group">
                    <label for="workflow_name">Workflow/System Name *</label>
                    <input type="text" id="workflow_name" name="workflow_name" value="{workflow_value}" required 
                           class="{'error' if workflow_error else ''}" placeholder="e.g., Customer Support Chatbot">
                    {f'<div class="error-message">{workflow_error}</div>' if workflow_error else ''}
                </div>
                
                <div class="form-group">
                    <label for="assessor">Assessor Name *</label>
                    <input type="text" id="assessor" name="assessor" value="{assessor_value}" required 
                           class="{'error' if assessor_error else ''}" placeholder="Your name">
                    {f'<div class="error-message">{assessor_error}</div>' if assessor_error else ''}
                </div>
                
                <div class="info-box">
                    <h4>Welcome to the AI Risk Assessment</h4>
                    <p>This assessment will guide you through 5 key dimensions to evaluate your AI system's risk level:</p>
                    <ul>
                        <li><strong>Autonomy:</strong> Decision-making independence</li>
                        <li><strong>Oversight:</strong> Human involvement level</li>
                        <li><strong>Impact:</strong> Consequence severity</li>
                        <li><strong>Orchestration:</strong> System coordination</li>
                        <li><strong>Data Sensitivity:</strong> Information protection needs</li>
                    </ul>
                </div>
            </div>
        '''
    
    def _generate_dimension_content(self, dimension_key: str, session_data: Dict = None, errors: Dict = None) -> str:
        """Generate content for all questions in a dimension"""
        config = self.get_current_config()
        
        # Find all questions that belong to this dimension
        dimension_questions = []
        for question_id, question_config in config['questions'].items():
            # Check if this question belongs to the current dimension using metadata
            if question_config.get('_dimension') == dimension_key:
                dimension_questions.append((question_id, question_config))
        
        if not dimension_questions:
            return '<div class="error">No questions found for this dimension</div>'
        
        # Generate content for all questions in this dimension
        content_parts = []
        for question_id, question_config in dimension_questions:
            question_content = self._generate_single_question_content(question_id, question_config, session_data, errors)
            content_parts.append(question_content)
        
        # Join all questions with some spacing
        return '<div class="dimension-questions">' + ''.join(content_parts) + '</div>'

    def _generate_single_question_content(self, question_id: str, question_config: Dict, session_data: Dict = None, errors: Dict = None) -> str:
        """Generate content for a single question"""
        selected_value = session_data.get(question_id, '') if session_data else ''
        reasoning_value = session_data.get(f'{question_id}_reasoning', '') if session_data else ''
        
        question_error = errors.get(question_id, '') if errors else ''
        
        # Generate radio options
        radio_options_html = ""
        for option_key, option_config in question_config.get('options', {}).items():
            checked = 'checked' if selected_value == option_key else ''
            selected_class = 'selected' if selected_value == option_key else ''
            
            radio_options_html += f'''
                <div class="radio-option {selected_class}" onclick="selectRadio('{question_id}', '{option_key}')">
                    <input type="radio" name="{question_id}" value="{option_key}" id="{question_id}_{option_key}" {checked}>
                    <div class="radio-checkmark"></div>
                    <div class="radio-content">
                        <div class="radio-title">{option_config.get('title', option_key)}</div>
                        <div class="radio-description">{option_config.get('description', '')}</div>
                    </div>
                </div>
            '''
        
        # Generate reasoning section if specified
        reasoning_html = ""
        reasoning_prompt = question_config.get('reasoning_prompt', '')
        if reasoning_prompt:
            reasoning_html = f'''
                <div class="reasoning-section">
                    <label for="{question_id}_reasoning">{reasoning_prompt}</label>
                    <textarea name="{question_id}_reasoning" id="{question_id}_reasoning" 
                            placeholder="{reasoning_prompt}">{reasoning_value}</textarea>
                </div>
            '''
        
        # Generate help text if present
        help_text_html = ""
        help_text = question_config.get('help_text', '')
        if help_text:
            help_text_html = f'<div class="help-text">{help_text}</div>'
        
        # Generate error message if present
        error_html = ""
        if question_error:
            error_html = f'<div class="error-message">{question_error}</div>'
        
        # Build the complete question HTML
        question_title = question_config.get('title', question_id)
        
        return f'''
            <div class="question-container" data-question="{question_id}">
                <div class="question-header">
                    <h3 class="question-title">{question_title}</h3>
                    {help_text_html}
                </div>
                
                {error_html}
                
                <div class="radio-group">
                    {radio_options_html}
                </div>
                
                {reasoning_html}
            </div>
        '''

    def _generate_question_content(self, question_key: str, session_data: Dict = None, errors: Dict = None) -> str:
        """Generate content for a question step"""
        config = self.get_current_config()
        if question_key not in config['questions']:
            return '<div class="error">Question configuration not found</div>'
        
        question_config = config['questions'][question_key]
        selected_value = session_data.get(question_key, '') if session_data else ''
        reasoning_value = session_data.get(f'{question_key}_reasoning', '') if session_data else ''
        
        question_error = errors.get(question_key, '') if errors else ''
        
        # Generate radio options
        radio_options_html = ""
        for option_key, option_config in question_config['options'].items():
            checked = 'checked' if selected_value == option_key else ''
            selected_class = 'selected' if selected_value == option_key else ''
            
            radio_options_html += f'''
                <div class="radio-option {selected_class}" onclick="selectRadio('{question_key}', '{option_key}')">
                    <input type="radio" name="{question_key}" value="{option_key}" id="{question_key}_{option_key}" {checked}>
                    <div class="radio-checkmark"></div>
                    <div class="radio-content">
                        <div class="radio-title">{option_config['title']}</div>
                        <div class="radio-description">{option_config['description']}</div>
                    </div>
                </div>
            '''
        
        return f'''
            <div class="step-content">
                <div class="question-section">
                    <div class="help-text">
                        {question_config['help_text']}
                    </div>
                    
                    <div class="radio-group">
                        {radio_options_html}
                    </div>
                    
                    {f'<div class="error-message">{question_error}</div>' if question_error else ''}
                    
                    <div class="reasoning-section">
                        <label for="{question_key}_reasoning">Reasoning (Optional)</label>
                        <textarea name="{question_key}_reasoning" id="{question_key}_reasoning" 
                                placeholder="{question_config['reasoning_prompt']}">{reasoning_value}</textarea>
                    </div>
                </div>
            </div>
        '''

    def _generate_navigation_buttons(self, step_number: int) -> str:
        """Generate navigation buttons based on current step"""
        buttons = []
        
        # Back button (not on first step)
        if step_number > 1:
            buttons.append('''
                <button type="button" class="nav-btn back-btn" onclick="goBack()">
                    ← Previous Step
                </button>
            ''')
        
        # Next/Generate button
        if step_number < self.total_steps:
            buttons.append('''
                <button type="submit" class="nav-btn next-btn">
                    Next Step →
                </button>
            ''')
        else:
            buttons.append('''
                <button type="submit" class="nav-btn generate-btn">
                    Generate Risk Assessment
                </button>
            ''')
        
        return f'<div class="navigation-buttons">{"".join(buttons)}</div>'

    def _generate_progress_bar(self, step_number: int) -> str:
        """Generate progress indicator"""
        progress_percentage = (step_number / self.total_steps) * 100
        
        steps_html = ""
        for i in range(1, self.total_steps + 1):
            status = "completed" if i < step_number else ("current" if i == step_number else "upcoming")
            step_config = self.steps[i - 1]
            
            steps_html += f'''
                <div class="progress-step {status}">
                    <div class="step-number">{i}</div>
                    <div class="step-label">{step_config['title'].split()[0]}</div>
                </div>
            '''
        
        return f'''
            <div class="progress-container">
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {progress_percentage}%"></div>
                </div>
                <div class="progress-steps">
                    {steps_html}
                </div>
                <div class="progress-text">
                    Step {step_number} of {self.total_steps}
                </div>
            </div>
        '''

    def _get_step_template(self, step_config: Dict, content: str, nav_buttons: str, progress_bar: str, step_number: int) -> str:
        """Get the complete HTML template for a step"""
        return f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{step_config['title']} - AI Risk Assessment</title>
    <link rel="icon" type="image/svg+xml" href="/favicon.ico">
    <style>
        {self._get_step_styles()}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{step_config['title']}</h1>
            <div class="subtitle">{step_config['subtitle']}</div>
            <div class="admin-link">
                <a href="/admin" style="color: #667eea; text-decoration: none; font-size: 0.9rem; opacity: 0.7;">Admin</a>
            </div>
        </div>
        
        {progress_bar}
        
        <div class="form-container">
            <form id="stepForm" method="POST" action="/step/{step_number}">
                {content}
                {nav_buttons}
            </form>
        </div>
    </div>
    
    <script>
        {self._get_step_scripts()}
    </script>
</body>
</html>
        '''

    def _get_step_styles(self) -> str:
        """Get CSS styles for step pages"""
        return '''
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
            zoom: 0.75;
            transform-origin: top left;
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
        
        .subtitle {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .progress-container {
            background: #f8f9fa;
            padding: 25px;
            border-bottom: 1px solid #e9ecef;
        }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #e9ecef;
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 20px;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 4px;
            transition: width 0.3s ease;
        }
        
        .progress-steps {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .progress-step {
            display: flex;
            flex-direction: column;
            align-items: center;
            flex: 1;
            position: relative;
        }
        
        .step-number {
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 0.9em;
            margin-bottom: 5px;
        }
        
        .step-label {
            font-size: 0.8em;
            text-align: center;
            font-weight: 500;
        }
        
        .progress-step.completed .step-number {
            background: #27ae60;
            color: white;
        }
        
        .progress-step.current .step-number {
            background: #667eea;
            color: white;
        }
        
        .progress-step.upcoming .step-number {
            background: #e9ecef;
            color: #6c757d;
        }
        
        .progress-text {
            text-align: center;
            font-weight: 600;
            color: #495057;
        }
        
        .form-container {
            padding: 40px;
        }
        
        .step-content {
            margin-bottom: 30px;
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        .form-group label {
            display: block;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 8px;
            font-size: 1.1em;
        }
        
        .form-group input {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 1em;
            transition: border-color 0.3s ease;
        }
        
        .form-group input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .form-group input.error {
            border-color: #e74c3c;
        }
        
        .error-message {
            color: #e74c3c;
            font-size: 0.9em;
            margin-top: 5px;
            font-weight: 500;
        }
        
        .info-box {
            background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
            border-radius: 10px;
            padding: 25px;
            margin-top: 20px;
        }
        
        .info-box h4 {
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 1.2em;
        }
        
        .info-box ul {
            margin-left: 20px;
            line-height: 1.6;
        }
        
        .help-text {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 15px 20px;
            margin-bottom: 25px;
            border-radius: 0 8px 8px 0;
            font-size: 1em;
            color: #495057;
            line-height: 1.6;
        }
        
        .radio-group {
            display: grid;
            grid-template-columns: 1fr;
            gap: 12px;
            margin-bottom: 20px;
        }
        
        .radio-option {
            background: #fff;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            padding: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            display: flex;
            align-items: flex-start;
            gap: 15px;
        }
        
        .radio-option:hover {
            border-color: #adb5bd;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }
        
        .radio-option.selected {
            border-color: #667eea;
            background: linear-gradient(135deg, #f8f9ff 0%, #f0f4ff 100%);
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.15);
        }
        
        .radio-option input[type="radio"] {
            position: absolute;
            opacity: 0;
            width: 0;
            height: 0;
        }
        
        .radio-checkmark {
            width: 24px;
            height: 24px;
            border: 2px solid #e9ecef;
            border-radius: 50%;
            background: #fff;
            position: relative;
            flex-shrink: 0;
            margin-top: 2px;
            transition: all 0.3s ease;
        }
        
        .radio-option.selected .radio-checkmark {
            border-color: #667eea;
            background: #667eea;
        }
        
        .radio-checkmark::after {
            content: "✓";
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: white;
            font-size: 14px;
            font-weight: bold;
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        
        .radio-option.selected .radio-checkmark::after {
            opacity: 1;
        }
        
        .radio-content {
            flex: 1;
        }
        
        .radio-title {
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 5px;
            font-size: 1.1em;
        }
        
        .radio-option.selected .radio-title {
            color: #667eea;
        }
        
        .radio-description {
            color: #6c757d;
            line-height: 1.4;
            font-size: 0.95em;
        }
        
        .reasoning-section {
            margin-top: 25px;
        }
        
        .reasoning-section label {
            display: block;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 8px;
        }
        
        .reasoning-section textarea {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 0.95em;
            font-family: inherit;
            line-height: 1.5;
            height: 100px;
            resize: vertical;
            transition: border-color 0.3s ease;
        }
        
        .reasoning-section textarea:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .navigation-buttons {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 40px;
            gap: 20px;
        }
        
        .nav-btn {
            padding: 15px 30px;
            border: none;
            border-radius: 25px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .back-btn {
            background: #6c757d;
            color: white;
        }
        
        .back-btn:hover {
            background: #5a6268;
            transform: translateY(-2px);
        }
        
        .next-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin-left: auto;
        }
        
        .next-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        }
        
        .generate-btn {
            background: linear-gradient(135deg, #27ae60 0%, #229954 100%);
            color: white;
            margin-left: auto;
            font-size: 1.1em;
            padding: 18px 35px;
        }
        
        .generate-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(39, 174, 96, 0.3);
        }
        
        @media (max-width: 768px) {
            .form-container {
                padding: 25px;
            }
            
            .progress-steps {
                flex-wrap: wrap;
                gap: 10px;
            }
            
            .navigation-buttons {
                flex-direction: column;
                gap: 15px;
            }
            
            .nav-btn {
                width: 100%;
                justify-content: center;
            }
        }
        
        /* Styles for multiple questions per step */
        .dimension-questions {
            display: flex;
            flex-direction: column;
            gap: 30px;
        }
        
        .question-container {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 25px;
            border-left: 4px solid #667eea;
        }
        
        .question-header {
            margin-bottom: 20px;
        }
        
        .question-title {
            color: #2c3e50;
            font-size: 1.3em;
            font-weight: 600;
            margin-bottom: 10px;
        }
        
        .question-container .help-text {
            background: #e3f2fd;
            color: #1976d2;
            padding: 12px 16px;
            border-radius: 8px;
            font-size: 0.95em;
            border-left: 3px solid #2196f3;
        }
        
        .question-container .radio-group {
            margin-top: 20px;
        }
        
        .question-container .reasoning-section {
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
        }
        '''

    def _get_step_scripts(self) -> str:
        """Get JavaScript for step functionality"""
        return '''
        function selectRadio(groupName, value) {
            // Remove selected class from all options in this group
            document.querySelectorAll(`input[name="${groupName}"]`).forEach(radio => {
                radio.parentElement.classList.remove('selected');
            });
            
            // Add selected class to clicked option
            const selectedOption = document.getElementById(`${groupName}_${value}`);
            if (selectedOption) {
                selectedOption.parentElement.classList.add('selected');
                selectedOption.checked = true;
            }
        }
        
        function goBack() {
            // Go to previous step
            const currentUrl = window.location.pathname;
            const currentStep = parseInt(currentUrl.split('/').pop());
            if (currentStep > 1) {
                window.location.href = `/step/${currentStep - 1}`;
            }
        }
        
        // Form validation
        document.getElementById('stepForm').addEventListener('submit', function(e) {
            const currentUrl = window.location.pathname;
            const currentStep = parseInt(currentUrl.split('/').pop());
            
            // Validate based on current step
            let isValid = true;
            let errorMessage = '';
            
            if (currentStep === 1) {
                // Validate basic info
                const workflowName = document.getElementById('workflow_name');
                const assessor = document.getElementById('assessor');
                
                if (!workflowName.value.trim()) {
                    workflowName.classList.add('error');
                    isValid = false;
                    errorMessage = 'Please enter a workflow/system name.';
                }
                
                if (!assessor.value.trim()) {
                    assessor.classList.add('error');
                    isValid = false;
                    errorMessage = 'Please enter your name as the assessor.';
                }
            } else {
                // Validate question selection
                const radioInputs = document.querySelectorAll('input[type="radio"]');
                const radioGroups = {};
                
                radioInputs.forEach(input => {
                    if (!radioGroups[input.name]) {
                        radioGroups[input.name] = false;
                    }
                    if (input.checked) {
                        radioGroups[input.name] = true;
                    }
                });
                
                for (const [groupName, hasSelection] of Object.entries(radioGroups)) {
                    if (!hasSelection) {
                        isValid = false;
                        errorMessage = 'Please select an option before proceeding.';
                        break;
                    }
                }
            }
            
            if (!isValid) {
                e.preventDefault();
                alert(errorMessage);
            }
        });
        
        // Clear error styling on input
        document.querySelectorAll('input').forEach(input => {
            input.addEventListener('input', function() {
                this.classList.remove('error');
            });
        });
        ''' 