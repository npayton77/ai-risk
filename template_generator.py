#!/usr/bin/env python3
"""
Template Generator for AI Risk Assessment
Generates HTML templates dynamically from YAML configuration
"""

import yaml
from typing import Dict, Any
from questions_loader import questions_loader

class TemplateGenerator:
    def __init__(self, questions_dir: str = 'questions'):
        """Initialize with questions configuration from directory"""
        self.config = questions_loader.load_all_questions()
    
    def generate_assessment_form(self) -> str:
        """Generate the main assessment form HTML"""
        # Generate basic fields HTML
        basic_fields_html = ""
        for field_name, field_config in self.config['basic_fields'].items():
            required_attr = "required" if field_config['required'] else ""
            basic_fields_html += f'''
                <div class="form-group">
                    <label for="{field_name}">{field_config['label']} {'*' if field_config['required'] else ''}</label>
                    <input type="{field_config['type']}" id="{field_name}" name="{field_name}" {required_attr}>
                </div>
            '''
        
        # Generate question sections HTML
        questions_html = ""
        for question_key, question_config in self.config['questions'].items():
            required_attr = "*" if question_config['required'] else ""
            
            # Generate radio options
            radio_options_html = ""
            for option_key, option_config in question_config['options'].items():
                radio_options_html += f'''
                    <div class="radio-option" onclick="selectRadio('{question_key}', '{option_key}')">
                        <input type="radio" name="{question_key}" value="{option_key}" id="{question_key}_{option_key}">
                        <div class="radio-checkmark"></div>
                        <div class="radio-content">
                            <div class="radio-title">{option_config['title']}</div>
                            <div class="radio-description">{option_config['description']}</div>
                        </div>
                    </div>
                '''
            
            questions_html += f'''
                <div class="form-group">
                    <label>{question_config['title']} {required_attr}</label>
                    <div class="help-text">
                        {question_config['help_text']}
                    </div>
                    <div class="radio-group">
                        {radio_options_html}
                    </div>
                    <textarea name="{question_key}_reasoning" placeholder="{question_config['reasoning_prompt']}"></textarea>
                </div>
            '''
        
        return self._get_full_template(basic_fields_html + questions_html)
    
    def _get_full_template(self, form_content: str) -> str:
        """Get the complete HTML template with styles and scripts"""
        return f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Risk Assessment Tool</title>
    <link rel="icon" type="image/svg+xml" href="/favicon.ico">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 24px;
            text-align: center;
        }}
        
        .header h1 {{
            margin: 0 0 8px 0;
            font-size: 1.8em;
            font-weight: 400;
        }}
        
        .header .subtitle {{
            font-size: 1em;
            opacity: 0.9;
        }}
        
        .form-container {{
            padding: 32px;
        }}
        
        .form-group {{
            margin-bottom: 25px;
        }}
        
        .form-group label {{
            display: block;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 6px;
            font-size: 1em;
        }}
        
        .form-group input,
        .form-group textarea {{
            width: 100%;
            padding: 10px 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 0.95em;
            transition: border-color 0.3s ease;
        }}
        
        .form-group input:focus,
        .form-group textarea:focus {{
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
        }}
        
        .form-group textarea {{
            height: 70px;
            resize: vertical;
        }}
        
        .radio-group {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 8px;
            margin-top: 8px;
        }}
        
        .radio-option {{
            background: #fff;
            border: 1px solid #ddd;
            border-radius: 6px;
            padding: 12px 16px;
            cursor: pointer;
            transition: all 0.2s ease;
            position: relative;
            display: flex;
            align-items: flex-start;
            gap: 12px;
        }}
        
        .radio-option:hover {{
            border-color: #bbb;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        
        .radio-option.selected {{
            border-color: #27ae60;
            background: #f8fff8;
            box-shadow: 0 2px 8px rgba(39, 174, 96, 0.15);
        }}
        
        .radio-option input[type="radio"] {{
            position: absolute;
            opacity: 0;
            width: 0;
            height: 0;
        }}
        
        .radio-checkmark {{
            width: 20px;
            height: 20px;
            border: 2px solid #ddd;
            border-radius: 50%;
            background: #fff;
            position: relative;
            flex-shrink: 0;
            margin-top: 2px;
            transition: all 0.2s ease;
        }}
        
        .radio-option.selected .radio-checkmark {{
            border-color: #27ae60;
            background: #27ae60;
        }}
        
        .radio-checkmark::after {{
            content: "✓";
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: white;
            font-size: 12px;
            font-weight: bold;
            opacity: 0;
            transition: opacity 0.2s ease;
        }}
        
        .radio-option.selected .radio-checkmark::after {{
            opacity: 1;
        }}
        
        .radio-content {{
            flex: 1;
        }}
        
        .radio-title {{
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 3px;
            font-size: 0.95em;
        }}
        
        .radio-option.selected .radio-title {{
            color: #27ae60;
        }}
        
        .radio-description {{
            color: #6c757d;
            font-size: 0.85em;
            line-height: 1.3;
        }}
        
        .help-text {{
            background: #f8f9fa;
            border-left: 3px solid #667eea;
            padding: 10px 12px;
            margin: 8px 0 12px 0;
            border-radius: 0 4px 4px 0;
            font-size: 0.85em;
            color: #555;
        }}
        
        .submit-btn {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 32px;
            border: none;
            border-radius: 6px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            display: block;
            margin: 32px auto 0;
        }}
        
        .submit-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }}
        
        .submit-btn:disabled {{
            opacity: 0.7;
            cursor: not-allowed;
            transform: none;
        }}
        
        .loading {{
            display: none;
            text-align: center;
            padding: 40px;
        }}
        
        .spinner {{
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        .result {{
            display: none;
            text-align: center;
            padding: 40px;
        }}
        
        .result.success {{
            color: #27ae60;
        }}
        
        .result.error {{
            color: #e74c3c;
        }}
        
        .download-btn {{
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
        }}
        
        .download-btn:hover {{
            transform: translateY(-2px);
        }}
        
        @media (max-width: 768px) {{
            .form-container {{
                padding: 20px;
            }}
            
            .radio-group {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>AI Risk Assessment Tool</h1>
            <div class="subtitle">Evaluate AI workflow patterns and determine risk levels</div>
        </div>
        
        <div class="form-container">
            <form id="assessmentForm" method="POST" action="/assess">
                {form_content}
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
        function selectRadio(groupName, value) {{
            // Remove selected class from all options in this group
            document.querySelectorAll(`input[name="${{groupName}}"]`).forEach(radio => {{
                radio.parentElement.classList.remove('selected');
            }});
            
            // Add selected class to clicked option
            document.getElementById(`${{groupName}}_${{value}}`).parentElement.classList.add('selected');
            document.getElementById(`${{groupName}}_${{value}}`).checked = true;
        }}
        
        document.getElementById('assessmentForm').addEventListener('submit', function(e) {{
            // Validate required fields
            const requiredFields = ['workflow_name', 'assessor', 'autonomy', 'oversight', 'impact', 'orchestration'];
            let isValid = true;
            
            for (let field of requiredFields) {{
                const input = document.querySelector(`[name="${{field}}"]`);
                if (field === 'workflow_name' || field === 'assessor') {{
                    if (!input.value.trim()) {{
                        isValid = false;
                        input.style.borderColor = '#e74c3c';
                    }} else {{
                        input.style.borderColor = '#e9ecef';
                    }}
                }} else {{
                    if (!document.querySelector(`input[name="${{field}}"]:checked`)) {{
                        isValid = false;
                        // Highlight the radio group
                        document.querySelector(`input[name="${{field}}"]`).closest('.form-group').style.borderLeft = '4px solid #e74c3c';
                    }} else {{
                        document.querySelector(`input[name="${{field}}"]`).closest('.form-group').style.borderLeft = 'none';
                    }}
                }}
            }}
            
            if (!isValid) {{
                e.preventDefault();
                alert('Please fill in all required fields');
                return;
            }}
            
            // Show loading animation while form submits
            const submitBtn = document.getElementById('submitBtn');
            const loading = document.getElementById('loading');
            
            submitBtn.disabled = true;
            loading.style.display = 'block';
            
            // Form will submit normally for redirect handling
        }});
    </script>
</body>
</html>
        ''' 