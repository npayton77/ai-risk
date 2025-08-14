#!/usr/bin/env python3
"""
Admin Interface for AI Risk Assessment System
Web-based admin panel for managing questions, scoring, and configuration
"""

import os
import yaml
import json
from pathlib import Path
from flask import Blueprint, render_template_string, request, jsonify, redirect, url_for, flash, session
from typing import Dict, List, Any, Optional
from datetime import datetime
from questions_loader import QuestionsLoader

class AdminInterface:
    """Web-based admin interface for question management"""
    
    def __init__(self):
        self.questions_dir = Path("questions")
        self.scoring_file = Path("scoring_flexible.yaml")
        self.dimensions = ["autonomy", "oversight", "impact", "orchestration", "data_sensitivity"]
        self.questions_loader = QuestionsLoader()
        
        # Create Flask Blueprint
        self.bp = Blueprint('admin', __name__, url_prefix='/admin')
        self._register_routes()
    
    def _register_routes(self):
        """Register all admin routes"""
        self.bp.route('/', methods=['GET'])(self.dashboard)
        self.bp.route('/questions', methods=['GET'])(self.questions_list)
        self.bp.route('/questions/add', methods=['GET', 'POST'])(self.add_question)
        self.bp.route('/questions/edit/<dimension>/<question_id>', methods=['GET', 'POST'])(self.edit_question)
        self.bp.route('/questions/delete/<dimension>/<question_id>', methods=['POST'])(self.delete_question)
        self.bp.route('/scoring', methods=['GET', 'POST'])(self.scoring_editor)
        self.bp.route('/validate', methods=['GET'])(self.validate_config)
        self.bp.route('/api/questions/<dimension>', methods=['GET'])(self.api_get_dimension_questions)
    
    def load_yaml_file(self, file_path: Path) -> Dict[str, Any]:
        """Load a YAML file safely"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            return {"error": str(e)}
    
    def save_yaml_file(self, file_path: Path, data: Dict[str, Any]) -> bool:
        """Save data to a YAML file safely"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False, indent=2)
            return True
        except Exception as e:
            flash(f"Error saving {file_path}: {e}", 'error')
            return False
    
    def get_all_questions(self) -> Dict[str, Dict[str, Any]]:
        """Get all questions organized by dimension"""
        all_questions = {}
        
        for dimension in self.dimensions:
            question_file = self.questions_dir / f"{dimension}.yaml"
            if question_file.exists():
                data = self.load_yaml_file(question_file)
                dimension_key = f"{dimension}_questions"
                all_questions[dimension] = data.get(dimension_key, {})
            else:
                all_questions[dimension] = {}
        
        return all_questions
    
    def get_scoring_config(self) -> Dict[str, Any]:
        """Get current scoring configuration"""
        if self.scoring_file.exists():
            return self.load_yaml_file(self.scoring_file)
        return {"dimensions": {}}
    
    def dashboard(self):
        """Admin dashboard - overview of the system"""
        all_questions = self.get_all_questions()
        scoring_config = self.get_scoring_config()
        
        # Calculate stats
        total_questions = sum(len(questions) for questions in all_questions.values())
        dimensions_with_questions = sum(1 for questions in all_questions.values() if questions)
        
        # Get recent activity (mock for now)
        recent_activity = [
            {"action": "System initialized", "timestamp": datetime.now(), "user": "Admin"}
        ]
        
        template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Risk Assessment - Admin Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            zoom: 0.75;
            transform-origin: top left;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 30px;
            text-align: center;
        }
        .header h1 { 
            color: #333; 
            margin-bottom: 10px;
            font-size: 2.5rem;
        }
        .header p { color: #666; font-size: 1.1rem; }
        
        .nav-links {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-top: 20px;
            flex-wrap: wrap;
        }
        .nav-links a {
            background: #667eea;
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        .nav-links a:hover {
            background: #5a6fd8;
            transform: translateY(-2px);
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            text-align: center;
        }
        .stat-number {
            font-size: 2.5rem;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }
        .stat-label {
            color: #666;
            font-size: 1.1rem;
        }
        
        .dimensions-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        .dimension-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }
        .dimension-header {
            display: flex;
            justify-content: between;
            align-items: center;
            margin-bottom: 15px;
        }
        .dimension-title {
            font-size: 1.3rem;
            font-weight: bold;
            color: #333;
            text-transform: capitalize;
        }
        .question-count {
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: bold;
        }
        .question-list {
            list-style: none;
            margin-top: 10px;
        }
        .question-list li {
            padding: 8px 0;
            border-bottom: 1px solid #eee;
            color: #666;
        }
        .question-list li:last-child { border-bottom: none; }
        
        .actions {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        .btn {
            padding: 8px 16px;
            border-radius: 6px;
            text-decoration: none;
            font-size: 0.9rem;
            font-weight: 500;
            border: none;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .btn-primary { background: #667eea; color: white; }
        .btn-secondary { background: #f8f9fa; color: #666; border: 1px solid #ddd; }
        .btn:hover { transform: translateY(-1px); }
        
        .alert {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .alert-info { background: #e3f2fd; color: #1976d2; border-left: 4px solid #2196f3; }
        
        @media (max-width: 768px) {
            .nav-links { flex-direction: column; align-items: center; }
            .stats-grid { grid-template-columns: 1fr; }
            .dimensions-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>AI Risk Assessment</h1>
            <p>Admin Dashboard</p>
            
            <div class="nav-links">
                <a href="{{ url_for('admin.questions_list') }}">Manage Questions</a>
                <a href="{{ url_for('admin.add_question') }}">Add Question</a>
                <a href="{{ url_for('admin.scoring_editor') }}">Scoring Config</a>
                <a href="{{ url_for('admin.validate_config') }}">Validate</a>
                <a href="{{ url_for('index') }}">Back to App</a>
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{{ total_questions }}</div>
                <div class="stat-label">Total Questions</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ dimensions_count }}</div>
                <div class="stat-label">Dimensions</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ dimensions_with_questions }}</div>
                <div class="stat-label">Active Dimensions</div>
            </div>
        </div>
        
        <div class="dimensions-grid">
            {% for dimension, questions in all_questions.items() %}
            <div class="dimension-card">
                <div class="dimension-header">
                    <div class="dimension-title">{{ dimension.replace('_', ' ').title() }}</div>
                    <div class="question-count">{{ questions|length }} questions</div>
                </div>
                
                {% if questions %}
                    <ul class="question-list">
                        {% for question_id, question_data in questions.items() %}
                        <li>{{ question_data.title[:50] }}{% if question_data.title|length > 50 %}...{% endif %}</li>
                        {% endfor %}
                    </ul>
                {% else %}
                    <p style="color: #999; font-style: italic;">No questions defined</p>
                {% endif %}
                
                <div class="actions">
                    <a href="{{ url_for('admin.add_question') }}?dimension={{ dimension }}" class="btn btn-primary">Add Question</a>
                    {% if questions %}
                    <a href="{{ url_for('admin.questions_list') }}#{{ dimension }}" class="btn btn-secondary">Edit Questions</a>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
        """
        
        return render_template_string(
            template,
            all_questions=all_questions,
            total_questions=total_questions,
            dimensions_count=len(self.dimensions),
            dimensions_with_questions=dimensions_with_questions,
            recent_activity=recent_activity
        )
    
    def questions_list(self):
        """List all questions with edit/delete options"""
        all_questions = self.get_all_questions()
        scoring_config = self.get_scoring_config()
        
        template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Question Management - Admin</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            zoom: 0.75;
            transform-origin: top left;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
        }
        .header h1 { color: #333; font-size: 2rem; }
        .header-actions { display: flex; gap: 15px; margin-top: 10px; }
        .btn {
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 500;
            border: none;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .btn-primary { background: #667eea; color: white; }
        .btn-secondary { background: #f8f9fa; color: #666; border: 1px solid #ddd; }
        .btn-danger { background: #dc3545; color: white; }
        .btn:hover { transform: translateY(-2px); }
        
        .dimension-section {
            background: white;
            margin-bottom: 30px;
            border-radius: 15px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .dimension-header {
            background: #667eea;
            color: white;
            padding: 20px 30px;
            font-size: 1.3rem;
            font-weight: bold;
            text-transform: capitalize;
        }
        .questions-table {
            width: 100%;
            border-collapse: collapse;
        }
        .questions-table th,
        .questions-table td {
            padding: 15px 30px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        .questions-table th {
            background: #f8f9fa;
            font-weight: 600;
            color: #333;
        }
        .questions-table tr:hover {
            background: #f8f9fa;
        }
        .question-title {
            font-weight: 500;
            color: #333;
            margin-bottom: 5px;
        }
        .question-meta {
            font-size: 0.9rem;
            color: #666;
        }
        .actions {
            display: flex;
            gap: 10px;
        }
        .btn-sm {
            padding: 6px 12px;
            font-size: 0.8rem;
        }
        .weight-badge {
            background: #e9ecef;
            color: #495057;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 500;
        }
        .no-questions {
            padding: 40px;
            text-align: center;
            color: #999;
            font-style: italic;
        }
        
        .flash-messages {
            margin-bottom: 20px;
        }
        .flash-message {
            padding: 12px 20px;
            border-radius: 8px;
            margin-bottom: 10px;
        }
        .flash-success { background: #d4edda; color: #155724; border-left: 4px solid #28a745; }
        .flash-error { background: #f8d7da; color: #721c24; border-left: 4px solid #dc3545; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Question Management</h1>
            <div class="header-actions">
                <a href="{{ url_for('admin.add_question') }}" class="btn btn-primary">Add Question</a>
                <a href="{{ url_for('admin.dashboard') }}" class="btn btn-secondary">Dashboard</a>
            </div>
        </div>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                <div class="flash-messages">
                    {% for category, message in messages %}
                        <div class="flash-message flash-{{ category }}">{{ message }}</div>
                    {% endfor %}
                </div>
            {% endif %}
        {% endwith %}
        
        {% for dimension, questions in all_questions.items() %}
        <div class="dimension-section" id="{{ dimension }}">
            <div class="dimension-header">
                {{ dimension.replace('_', ' ').title() }} 
                <span style="opacity: 0.8; font-weight: normal;">({{ questions|length }} questions)</span>
            </div>
            
            {% if questions %}
                <table class="questions-table">
                    <thead>
                        <tr>
                            <th>Question</th>
                            <th>Options</th>
                            <th>Weight</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for question_id, question_data in questions.items() %}
                        <tr>
                            <td>
                                <div class="question-title">{{ question_data.title }}</div>
                                <div class="question-meta">
                                    ID: {{ question_id }} • 
                                    {{ "Required" if question_data.get('required', False) else "Optional" }}
                                    {% if question_data.get('help_text') %}
                                    • Has help text
                                    {% endif %}
                                </div>
                            </td>
                            <td>
                                {{ question_data.options|length }} options
                                <div class="question-meta">
                                    {% for option_key in question_data.options.keys() %}
                                        {{ option_key }}{% if not loop.last %}, {% endif %}
                                    {% endfor %}
                                </div>
                            </td>
                            <td>
                                {% set weight = scoring_config.get('dimensions', {}).get(dimension, {}).get('questions', {}).get(question_id, {}).get('weight', 'N/A') %}
                                <span class="weight-badge">{{ weight }}</span>
                            </td>
                            <td>
                                <div class="actions">
                                    <a href="{{ url_for('admin.edit_question', dimension=dimension, question_id=question_id) }}" 
                                       class="btn btn-secondary btn-sm">Edit</a>
                                    <form method="POST" action="{{ url_for('admin.delete_question', dimension=dimension, question_id=question_id) }}" 
                                          style="display: inline;" 
                                          onsubmit="return confirm('Are you sure you want to delete this question?')">
                                        <button type="submit" class="btn btn-danger btn-sm">Delete</button>
                                    </form>
                                </div>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            {% else %}
                <div class="no-questions">
                    No questions defined for this dimension.
                    <br><br>
                    <a href="{{ url_for('admin.add_question') }}?dimension={{ dimension }}" class="btn btn-primary">Add First Question</a>
                </div>
            {% endif %}
        </div>
        {% endfor %}
    </div>
</body>
</html>
        """
        
        return render_template_string(
            template,
            all_questions=all_questions,
            scoring_config=scoring_config
        )
    
    def add_question(self):
        """Add a new question"""
        if request.method == 'POST':
            return self._handle_add_question_post()
        
        # GET request - show form
        selected_dimension = request.args.get('dimension', '')
        
        template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Add Question - Admin</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            zoom: 0.75;
            transform-origin: top left;
        }
        .container { max-width: 800px; margin: 0 auto; }
        .form-card {
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .form-header {
            text-align: center;
            margin-bottom: 40px;
        }
        .form-header h1 {
            color: #333;
            font-size: 2rem;
            margin-bottom: 10px;
        }
        .form-header p {
            color: #666;
            font-size: 1.1rem;
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        .form-label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        .form-control {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s ease;
        }
        .form-control:focus {
            outline: none;
            border-color: #667eea;
        }
        .form-text {
            margin-top: 5px;
            font-size: 0.9rem;
            color: #666;
        }
        
        .options-section {
            border: 2px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 25px;
        }
        .options-header {
            font-weight: 600;
            color: #333;
            margin-bottom: 15px;
            font-size: 1.1rem;
        }
        .option-row {
            display: grid;
            grid-template-columns: 1fr 2fr 1fr auto;
            gap: 15px;
            align-items: end;
            margin-bottom: 15px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        .option-row:last-child { margin-bottom: 0; }
        
        .btn {
            padding: 12px 24px;
            border-radius: 8px;
            border: none;
            font-weight: 500;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            text-align: center;
            transition: all 0.3s ease;
        }
        .btn-primary { background: #667eea; color: white; }
        .btn-secondary { background: #6c757d; color: white; }
        .btn-success { background: #28a745; color: white; }
        .btn-danger { background: #dc3545; color: white; }
        .btn:hover { transform: translateY(-2px); }
        
        .form-actions {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-top: 40px;
        }
        
        .checkbox-group {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .checkbox-group input[type="checkbox"] {
            width: auto;
            margin: 0;
        }
        
        @media (max-width: 768px) {
            .option-row {
                grid-template-columns: 1fr;
                gap: 10px;
            }
            .form-actions {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="form-card">
            <div class="form-header">
                <h1>Add New Question</h1>
                <p>Create a new question for the AI Risk Assessment</p>
            </div>
            
            <form method="POST" id="questionForm">
                <div class="form-group">
                    <label class="form-label" for="dimension">Dimension *</label>
                    <select name="dimension" id="dimension" class="form-control" required>
                        <option value="">Select a dimension</option>
                        {% for dim in dimensions %}
                        <option value="{{ dim }}" {{ 'selected' if dim == selected_dimension else '' }}>
                            {{ dim.replace('_', ' ').title() }}
                        </option>
                        {% endfor %}
                    </select>
                    <div class="form-text">Choose which risk dimension this question belongs to</div>
                </div>
                
                <div class="form-group">
                    <label class="form-label" for="question_id">Question ID *</label>
                    <input type="text" name="question_id" id="question_id" class="form-control" required
                           placeholder="e.g., decision_speed, review_frequency">
                    <div class="form-text">Unique identifier (lowercase, underscores only)</div>
                </div>
                
                <div class="form-group">
                    <label class="form-label" for="title">Question Title *</label>
                    <input type="text" name="title" id="title" class="form-control" required
                           placeholder="e.g., How quickly must the AI make decisions?">
                    <div class="form-text">The question text shown to users</div>
                </div>
                
                <div class="form-group">
                    <label class="form-label" for="help_text">Help Text</label>
                    <textarea name="help_text" id="help_text" class="form-control" rows="2"
                              placeholder="Optional additional context or instructions"></textarea>
                    <div class="form-text">Optional explanation to help users understand the question</div>
                </div>
                
                <div class="form-group">
                    <div class="checkbox-group">
                        <input type="checkbox" name="required" id="required" value="true" checked>
                        <label class="form-label" for="required">Required Question</label>
                    </div>
                    <div class="form-text">Whether users must answer this question</div>
                </div>
                
                <div class="options-section">
                    <div class="options-header">Answer Options *</div>
                    <div id="optionsContainer">
                        <div class="option-row">
                            <div>
                                <label class="form-label">Option Key *</label>
                                <input type="text" name="option_keys[]" class="form-control" placeholder="e.g., low" required>
                            </div>
                            <div>
                                <label class="form-label">Option Title *</label>
                                <input type="text" name="option_titles[]" class="form-control" placeholder="e.g., Low Risk" required>
                            </div>
                            <div>
                                <label class="form-label">Option Description</label>
                                <input type="text" name="option_descriptions[]" class="form-control" placeholder="e.g., Minimal risk to operations">
                            </div>
                            <div>
                                <label class="form-label">Risk Score (1-4) *</label>
                                <input type="number" name="option_scores[]" class="form-control" min="1" max="4" placeholder="1" required>
                            </div>
                            <div>
                                <button type="button" class="btn btn-danger" onclick="removeOption(this)">Remove</button>
                            </div>
                        </div>
                        <div class="option-row">
                            <div>
                                <input type="text" name="option_keys[]" class="form-control" placeholder="e.g., high" required>
                            </div>
                            <div>
                                <input type="text" name="option_titles[]" class="form-control" placeholder="e.g., High Risk" required>
                            </div>
                            <div>
                                <input type="text" name="option_descriptions[]" class="form-control" placeholder="e.g., Significant risk to operations">
                            </div>
                            <div>
                                <input type="number" name="option_scores[]" class="form-control" min="1" max="4" placeholder="4" required>
                            </div>
                            <div>
                                <button type="button" class="btn btn-danger" onclick="removeOption(this)">Remove</button>
                            </div>
                        </div>
                    </div>
                    <button type="button" class="btn btn-success" onclick="addOption()">Add Another Option</button>
                </div>
                
                <div class="form-group">
                    <label class="form-label" for="reasoning_prompt">Reasoning Prompt</label>
                    <input type="text" name="reasoning_prompt" id="reasoning_prompt" class="form-control"
                           placeholder="e.g., Why is this timeline appropriate for your use case?">
                    <div class="form-text">Optional prompt asking users to explain their choice</div>
                </div>
                
                <div class="form-group">
                    <label class="form-label" for="weight">Question Weight</label>
                    <input type="number" name="weight" id="weight" class="form-control" 
                           min="0.1" max="3.0" step="0.1" value="1.0">
                    <div class="form-text">Importance relative to other questions (1.0 = standard, 0.5 = less important, 1.5 = more important)</div>
                </div>
                
                <div class="form-actions">
                    <button type="submit" class="btn btn-primary">Create Question</button>
                    <a href="{{ url_for('admin.questions_list') }}" class="btn btn-secondary">Cancel</a>
                </div>
            </form>
        </div>
    </div>
    
    <script>
        function addOption() {
            const container = document.getElementById('optionsContainer');
            const newOption = document.createElement('div');
            newOption.className = 'option-row';
            newOption.innerHTML = `
                <div>
                    <input type="text" name="option_keys[]" class="form-control" placeholder="e.g., medium" required>
                </div>
                <div>
                    <input type="text" name="option_titles[]" class="form-control" placeholder="e.g., Medium Risk" required>
                </div>
                <div>
                    <input type="text" name="option_descriptions[]" class="form-control" placeholder="e.g., Moderate risk to operations">
                </div>
                <div>
                    <input type="number" name="option_scores[]" class="form-control" min="1" max="4" placeholder="2" required>
                </div>
                <div>
                    <button type="button" class="btn btn-danger" onclick="removeOption(this)">Remove</button>
                </div>
            `;
            container.appendChild(newOption);
        }
        
        function removeOption(button) {
            const optionsContainer = document.getElementById('optionsContainer');
            if (optionsContainer.children.length > 2) {
                button.closest('.option-row').remove();
            } else {
                alert('You must have at least 2 options.');
            }
        }
        
        // Auto-generate question ID from title
        document.getElementById('title').addEventListener('input', function(e) {
            const title = e.target.value;
            const questionId = title.toLowerCase()
                .replace(/[^a-z0-9\\s]/g, '')
                .replace(/\\s+/g, '_')
                .substring(0, 50);
            
            if (!document.getElementById('question_id').value) {
                document.getElementById('question_id').value = questionId;
            }
        });
    </script>
</body>
</html>
        """
        
        return render_template_string(
            template,
            dimensions=self.dimensions,
            selected_dimension=selected_dimension
        )
    
    def _handle_add_question_post(self):
        """Handle POST request for adding a question"""
        try:
            # Extract form data
            dimension = request.form.get('dimension')
            question_id = request.form.get('question_id')
            title = request.form.get('title')
            help_text = request.form.get('help_text', '').strip()
            required = request.form.get('required') == 'true'
            reasoning_prompt = request.form.get('reasoning_prompt', '').strip()
            weight = float(request.form.get('weight', 1.0))
            
            # Extract options
            option_keys = request.form.getlist('option_keys[]')
            option_titles = request.form.getlist('option_titles[]')
            option_descriptions = request.form.getlist('option_descriptions[]')
            option_scores = request.form.getlist('option_scores[]')
            
            # DEBUG: Log all submitted form data
            print(f"\nDEBUG - ADD QUESTION FORM DATA:")
            print(f"  Dimension: {dimension}")
            print(f"  Question ID: {question_id}")
            print(f"  Title: {title}")
            print(f"  Help Text: {help_text}")
            print(f"  Required: {required}")
            print(f"  Reasoning Prompt: {reasoning_prompt}")
            print(f"  Weight: {weight}")
            print(f"  Option Keys: {option_keys}")
            print(f"  Option Titles: {option_titles}")
            print(f"  Option Descriptions: {option_descriptions}")
            print(f"  Option Scores: {option_scores}")
            print(f"  Full Form Data: {dict(request.form)}")
            print(f"END DEBUG\n")
            
            # Validation
            if not all([dimension, question_id, title]) or len(option_keys) < 2:
                flash('Please fill in all required fields and provide at least 2 options.', 'error')
                return redirect(request.url)
            
            # Check if question ID already exists
            question_file = self.questions_dir / f"{dimension}.yaml"
            if question_file.exists():
                existing_data = self.load_yaml_file(question_file)
                dimension_key = f"{dimension}_questions"
                if dimension_key in existing_data and question_id in existing_data[dimension_key]:
                    flash(f'Question ID "{question_id}" already exists in {dimension} dimension.', 'error')
                    return redirect(request.url)
            
            # Build question data
            options = {}
            scoring = {}
            
            for key, title_text, desc_text, score in zip(option_keys, option_titles, option_descriptions, option_scores):
                if key.strip() and title_text.strip():
                    options[key.strip()] = {
                        "title": title_text.strip(),
                        "description": desc_text.strip() if desc_text else ""
                    }
                    scoring[key.strip()] = int(score)
            
            # DEBUG: Log what options and scoring structures get created
            print(f"DEBUG - OPTIONS STRUCTURE CREATED: {options}")
            print(f"DEBUG - SCORING STRUCTURE CREATED: {scoring}")
            
            # Add question to dimension file
            self._add_question_to_dimension_file(dimension, question_id, {
                'title': title,
                'help_text': help_text,
                'required': required,
                'options': options,
                'reasoning_prompt': reasoning_prompt
            })
            
            # Add scoring configuration
            self._add_question_to_scoring_file(dimension, question_id, weight, scoring)
            
            flash(f'Question "{title}" added successfully to {dimension} dimension!', 'success')
            return redirect(url_for('admin.questions_list'))
            
        except Exception as e:
            flash(f'Error adding question: {str(e)}', 'error')
            return redirect(request.url)
    
    def _add_question_to_dimension_file(self, dimension: str, question_id: str, question_data: Dict[str, Any]):
        """Add question to dimension YAML file"""
        question_file = self.questions_dir / f"{dimension}.yaml"
        
        # Load existing data
        data = self.load_yaml_file(question_file) if question_file.exists() else {}
        
        # Ensure dimension questions key exists
        dimension_key = f"{dimension}_questions"
        if dimension_key not in data:
            data[dimension_key] = {}
        
        # Clean question data (remove empty fields)
        clean_question_data = {
            "title": question_data["title"],
            "required": question_data["required"],
            "options": question_data["options"]
        }
        
        if question_data.get("help_text"):
            clean_question_data["help_text"] = question_data["help_text"]
        
        if question_data.get("reasoning_prompt"):
            clean_question_data["reasoning_prompt"] = question_data["reasoning_prompt"]
        
        # Add question
        data[dimension_key][question_id] = clean_question_data
        
        # Save file
        self.save_yaml_file(question_file, data)
    
    def _add_question_to_scoring_file(self, dimension: str, question_id: str, weight: float, scoring: Dict[str, int]):
        """Add question scoring to flexible scoring file"""
        scoring_data = self.get_scoring_config()
        
        # Ensure structure exists
        if "dimensions" not in scoring_data:
            scoring_data["dimensions"] = {}
        
        if dimension not in scoring_data["dimensions"]:
            scoring_data["dimensions"][dimension] = {
                "aggregation": "weighted_average",
                "questions": {}
            }
        
        if "questions" not in scoring_data["dimensions"][dimension]:
            scoring_data["dimensions"][dimension]["questions"] = {}
        
        # Add question scoring
        scoring_data["dimensions"][dimension]["questions"][question_id] = {
            "weight": weight,
            "scoring": scoring
        }
        
        # Save file
        self.save_yaml_file(self.scoring_file, scoring_data)
    
    def edit_question(self, dimension: str, question_id: str):
        """Edit an existing question"""
        if request.method == 'POST':
            return self._handle_edit_question_post(dimension, question_id)
        
        # GET request - load existing question data and show form
        question_file = self.questions_dir / f"{dimension}.yaml"
        if not question_file.exists():
            flash(f'Dimension file {dimension}.yaml not found', 'error')
            return redirect(url_for('admin.questions_list'))
        
        # Load question data
        data = self.load_yaml_file(question_file)
        dimension_key = f"{dimension}_questions"
        
        if dimension_key not in data or question_id not in data[dimension_key]:
            flash(f'Question "{question_id}" not found in {dimension} dimension', 'error')
            return redirect(url_for('admin.questions_list'))
        
        question_data = data[dimension_key][question_id]
        
        # Load scoring data
        scoring_config = self.get_scoring_config()
        scoring_data = scoring_config.get('dimensions', {}).get(dimension, {}).get('questions', {}).get(question_id, {})
        
        template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Edit Question - Admin</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            zoom: 0.75;
            transform-origin: top left;
        }
        .container { max-width: 800px; margin: 0 auto; }
        .form-card {
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .form-header {
            text-align: center;
            margin-bottom: 40px;
        }
        .form-header h1 {
            color: #333;
            font-size: 2rem;
            margin-bottom: 10px;
        }
        .form-header p {
            color: #666;
            font-size: 1.1rem;
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        .form-label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        .form-control {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s ease;
        }
        .form-control:focus {
            outline: none;
            border-color: #667eea;
        }
        .form-text {
            margin-top: 5px;
            font-size: 0.9rem;
            color: #666;
        }
        
        .options-section {
            border: 2px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 25px;
        }
        .options-header {
            font-weight: 600;
            color: #333;
            margin-bottom: 15px;
            font-size: 1.1rem;
        }
        .option-row {
            display: grid;
            grid-template-columns: 1fr 2fr 1fr auto;
            gap: 15px;
            align-items: end;
            margin-bottom: 15px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        .option-row:last-child { margin-bottom: 0; }
        
        .btn {
            padding: 12px 24px;
            border-radius: 8px;
            border: none;
            font-weight: 500;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            text-align: center;
            transition: all 0.3s ease;
        }
        .btn-primary { background: #667eea; color: white; }
        .btn-secondary { background: #6c757d; color: white; }
        .btn-success { background: #28a745; color: white; }
        .btn-danger { background: #dc3545; color: white; }
        .btn:hover { transform: translateY(-2px); }
        
        .form-actions {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-top: 40px;
        }
        
        .checkbox-group {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .checkbox-group input[type="checkbox"] {
            width: auto;
            margin: 0;
        }
        
        .alert {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .alert-info { background: #e3f2fd; color: #1976d2; border-left: 4px solid #2196f3; }
        
        @media (max-width: 768px) {
            .option-row {
                grid-template-columns: 1fr;
                gap: 10px;
            }
            .form-actions {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="form-card">
            <div class="form-header">
                <h1>Edit Question</h1>
                <p>Modify question in {{ dimension.replace('_', ' ').title() }} dimension</p>
            </div>
            
            <div class="alert alert-info">
                <strong>Editing:</strong> {{ question_id }} in {{ dimension }} dimension
            </div>
            
            <form method="POST" id="questionForm">
                <input type="hidden" name="original_question_id" value="{{ question_id }}">
                
                <div class="form-group">
                    <label class="form-label" for="dimension">Dimension</label>
                    <select name="dimension" id="dimension" class="form-control" disabled>
                        <option value="{{ dimension }}" selected>{{ dimension.replace('_', ' ').title() }}</option>
                    </select>
                    <input type="hidden" name="dimension" value="{{ dimension }}">
                    <div class="form-text">Dimension cannot be changed when editing</div>
                </div>
                
                <div class="form-group">
                    <label class="form-label" for="question_id">Question ID</label>
                    <input type="text" name="question_id" id="question_id" class="form-control" 
                           value="{{ question_id }}" readonly style="background-color: #f8f9fa;">
                    <div class="form-text">Question ID cannot be changed when editing</div>
                </div>
                
                <div class="form-group">
                    <label class="form-label" for="title">Question Title *</label>
                    <input type="text" name="title" id="title" class="form-control" required
                           value="{{ question_data.title }}">
                    <div class="form-text">The question text shown to users</div>
                </div>
                
                <div class="form-group">
                    <label class="form-label" for="help_text">Help Text</label>
                    <textarea name="help_text" id="help_text" class="form-control" rows="2">{{ question_data.get('help_text', '') }}</textarea>
                    <div class="form-text">Optional explanation to help users understand the question</div>
                </div>
                
                <div class="form-group">
                    <div class="checkbox-group">
                        <input type="checkbox" name="required" id="required" value="true" {{ 'checked' if question_data.get('required', False) else '' }}>
                        <label class="form-label" for="required">Required Question</label>
                    </div>
                    <div class="form-text">Whether users must answer this question</div>
                </div>
                
                <div class="options-section">
                    <div class="options-header">Answer Options *</div>
                    <div id="optionsContainer">
                        {% for option_key, option_data in question_data.options.items() %}
                        <div class="option-row">
                            <div>
                                <label class="form-label">Option Key *</label>
                                <input type="text" name="option_keys[]" class="form-control" 
                                       value="{{ option_key }}" required>
                            </div>
                            <div>
                                <label class="form-label">Option Title *</label>
                                <input type="text" name="option_titles[]" class="form-control" 
                                       value="{{ option_data.title }}" required>
                            </div>
                            <div>
                                <label class="form-label">Risk Score (1-4) *</label>
                                <input type="number" name="option_scores[]" class="form-control" min="1" max="4" 
                                       value="{{ scoring_data.get('scoring', {}).get(option_key, 1) }}" required>
                            </div>
                            <div>
                                <button type="button" class="btn btn-danger" onclick="removeOption(this)">Remove</button>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                    <button type="button" class="btn btn-success" onclick="addOption()">Add Another Option</button>
                </div>
                
                <div class="form-group">
                    <label class="form-label" for="reasoning_prompt">Reasoning Prompt</label>
                    <input type="text" name="reasoning_prompt" id="reasoning_prompt" class="form-control"
                           value="{{ question_data.get('reasoning_prompt', '') }}">
                    <div class="form-text">Optional prompt asking users to explain their choice</div>
                </div>
                
                <div class="form-group">
                    <label class="form-label" for="weight">Question Weight</label>
                    <input type="number" name="weight" id="weight" class="form-control" 
                           min="0.1" max="3.0" step="0.1" value="{{ scoring_data.get('weight', 1.0) }}">
                    <div class="form-text">Importance relative to other questions (1.0 = standard)</div>
                </div>
                
                <div class="form-actions">
                    <button type="submit" class="btn btn-primary">Update Question</button>
                    <a href="{{ url_for('admin.questions_list') }}" class="btn btn-secondary">Cancel</a>
                </div>
            </form>
        </div>
    </div>
    
    <script>
        function addOption() {
            const container = document.getElementById('optionsContainer');
            const newOption = document.createElement('div');
            newOption.className = 'option-row';
            newOption.innerHTML = `
                <div>
                    <input type="text" name="option_keys[]" class="form-control" placeholder="e.g., medium" required>
                </div>
                <div>
                    <input type="text" name="option_titles[]" class="form-control" placeholder="e.g., Medium Risk" required>
                </div>
                <div>
                    <input type="text" name="option_descriptions[]" class="form-control" placeholder="e.g., Moderate risk to operations">
                </div>
                <div>
                    <input type="number" name="option_scores[]" class="form-control" min="1" max="4" placeholder="2" required>
                </div>
                <div>
                    <button type="button" class="btn btn-danger" onclick="removeOption(this)">Remove</button>
                </div>
            `;
            container.appendChild(newOption);
        }
        
        function removeOption(button) {
            const optionsContainer = document.getElementById('optionsContainer');
            if (optionsContainer.children.length > 2) {
                button.closest('.option-row').remove();
            } else {
                alert('You must have at least 2 options.');
            }
        }
    </script>
</body>
</html>
        """
        
        return render_template_string(
            template,
            dimension=dimension,
            question_id=question_id,
            question_data=question_data,
            scoring_data=scoring_data
        )
    
    def _handle_edit_question_post(self, dimension: str, question_id: str):
        """Handle POST request for editing a question"""
        try:
            # Extract form data
            original_question_id = request.form.get('original_question_id')
            title = request.form.get('title')
            help_text = request.form.get('help_text', '').strip()
            required = request.form.get('required') == 'true'
            reasoning_prompt = request.form.get('reasoning_prompt', '').strip()
            weight = float(request.form.get('weight', 1.0))
            
            # Extract options
            option_keys = request.form.getlist('option_keys[]')
            option_titles = request.form.getlist('option_titles[]')
            option_scores = request.form.getlist('option_scores[]')
            
            # DEBUG: Log all submitted form data
            print(f"\nDEBUG - EDIT QUESTION FORM DATA:")
            print(f"  Dimension: {dimension}")
            print(f"  Question ID: {question_id}")
            print(f"  Original Question ID: {original_question_id}")
            print(f"  Title: {title}")
            print(f"  Help Text: {help_text}")
            print(f"  Required: {required}")
            print(f"  Reasoning Prompt: {reasoning_prompt}")
            print(f"  Weight: {weight}")
            print(f"  Option Keys: {option_keys}")
            print(f"  Option Titles: {option_titles}")
            print(f"  Option Scores: {option_scores}")
            print(f"  Full Form Data: {dict(request.form)}")
            print(f"END DEBUG\n")
            
            # Validation
            if not all([dimension, question_id, title]) or len(option_keys) < 2:
                flash('Please fill in all required fields and provide at least 2 options.', 'error')
                return redirect(request.url)
            
            # Build question data
            options = {}
            scoring = {}
            
            for key, title_text, score in zip(option_keys, option_titles, option_scores):
                if key.strip() and title_text.strip():
                    options[key.strip()] = {
                        "title": title_text.strip(),
                        "description": ""  # Could be enhanced later
                    }
                    scoring[key.strip()] = int(score)
            
            # Update question in dimension file
            self._update_question_in_dimension_file(dimension, question_id, {
                'title': title,
                'help_text': help_text,
                'required': required,
                'options': options,
                'reasoning_prompt': reasoning_prompt
            })
            
            # Update scoring configuration
            self._update_question_in_scoring_file(dimension, question_id, weight, scoring)
            
            flash(f'Question "{title}" updated successfully!', 'success')
            return redirect(url_for('admin.questions_list'))
            
        except Exception as e:
            flash(f'Error updating question: {str(e)}', 'error')
            return redirect(request.url)
    
    def _update_question_in_dimension_file(self, dimension: str, question_id: str, question_data: Dict[str, Any]):
        """Update question in dimension YAML file"""
        question_file = self.questions_dir / f"{dimension}.yaml"
        
        # Load existing data
        data = self.load_yaml_file(question_file) if question_file.exists() else {}
        
        # Ensure dimension questions key exists
        dimension_key = f"{dimension}_questions"
        if dimension_key not in data:
            data[dimension_key] = {}
        
        # Clean question data (remove empty fields)
        clean_question_data = {
            "title": question_data["title"],
            "required": question_data["required"],
            "options": question_data["options"]
        }
        
        if question_data.get("help_text"):
            clean_question_data["help_text"] = question_data["help_text"]
        
        if question_data.get("reasoning_prompt"):
            clean_question_data["reasoning_prompt"] = question_data["reasoning_prompt"]
        
        # Update question
        data[dimension_key][question_id] = clean_question_data
        
        # Save file
        self.save_yaml_file(question_file, data)
    
    def _update_question_in_scoring_file(self, dimension: str, question_id: str, weight: float, scoring: Dict[str, int]):
        """Update question scoring in flexible scoring file"""
        scoring_data = self.get_scoring_config()
        
        # Ensure structure exists
        if "dimensions" not in scoring_data:
            scoring_data["dimensions"] = {}
        
        if dimension not in scoring_data["dimensions"]:
            scoring_data["dimensions"][dimension] = {
                "aggregation": "weighted_average",
                "questions": {}
            }
        
        if "questions" not in scoring_data["dimensions"][dimension]:
            scoring_data["dimensions"][dimension]["questions"] = {}
        
        # Update question scoring
        scoring_data["dimensions"][dimension]["questions"][question_id] = {
            "weight": weight,
            "scoring": scoring
        }
        
        # Save file
        self.save_yaml_file(self.scoring_file, scoring_data)
    
    def delete_question(self, dimension: str, question_id: str):
        """Delete a question"""
        try:
            # Remove from dimension file
            question_file = self.questions_dir / f"{dimension}.yaml"
            if question_file.exists():
                data = self.load_yaml_file(question_file)
                dimension_key = f"{dimension}_questions"
                if dimension_key in data and question_id in data[dimension_key]:
                    del data[dimension_key][question_id]
                    self.save_yaml_file(question_file, data)
            
            # Remove from scoring file
            scoring_data = self.get_scoring_config()
            if ("dimensions" in scoring_data and 
                dimension in scoring_data["dimensions"] and
                "questions" in scoring_data["dimensions"][dimension] and
                question_id in scoring_data["dimensions"][dimension]["questions"]):
                del scoring_data["dimensions"][dimension]["questions"][question_id]
                self.save_yaml_file(self.scoring_file, scoring_data)
            
            flash(f'Question "{question_id}" deleted successfully!', 'success')
        except Exception as e:
            flash(f'Error deleting question: {str(e)}', 'error')
        
        return redirect(url_for('admin.questions_list'))
    
    def scoring_editor(self):
        """Scoring configuration editor"""
        flash('Scoring editor coming soon!', 'info')
        return redirect(url_for('admin.dashboard'))
    
    def validate_config(self):
        """Validate all configuration files"""
        flash('Validation functionality coming soon!', 'info')
        return redirect(url_for('admin.dashboard'))
    
    def api_get_dimension_questions(self, dimension: str):
        """API endpoint to get questions for a dimension"""
        question_file = self.questions_dir / f"{dimension}.yaml"
        if question_file.exists():
            data = self.load_yaml_file(question_file)
            dimension_key = f"{dimension}_questions"
            return jsonify(data.get(dimension_key, {}))
        return jsonify({})

# Create the admin interface instance
admin_interface = AdminInterface()
