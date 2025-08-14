#!/usr/bin/env python3
"""
Questions Loader for AI Risk Assessment
Loads questions from individual YAML files in the questions directory
"""

import os
import yaml
from typing import Dict, Any

class QuestionsLoader:
    def __init__(self, questions_dir: str = 'questions'):
        """Initialize with questions directory path"""
        self.questions_dir = questions_dir
        
    def load_all_questions(self) -> Dict[str, Any]:
        """
        Load all questions from individual YAML files and combine them
        Returns the same structure as the original questions.yaml
        """
        combined_config = {
            'questions': {},
            'basic_fields': {
                'workflow_name': {
                    'label': 'Workflow/System Name',
                    'type': 'text',
                    'required': True,
                    'placeholder': ''
                },
                'assessor': {
                    'label': 'Assessor Name', 
                    'type': 'text',
                    'required': True,
                    'placeholder': ''
                }
            }
        }
        
        # Define the expected question types and their file mappings
        question_files = {
            'autonomy': 'autonomy.yaml',
            'oversight': 'oversight.yaml', 
            'impact': 'impact.yaml',
            'orchestration': 'orchestration.yaml',
            'data_sensitivity': 'data_sensitivity.yaml'
        }
        
        for question_key, filename in question_files.items():
            file_path = os.path.join(self.questions_dir, filename)
            
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content = yaml.safe_load(f)
                    
                    # Extract the question configuration from the file
                    # The file structure is: {question_key}_questions: {question_key}: {...}
                    top_level_key = f"{question_key}_questions"
                    
                    if top_level_key in file_content:
                        # Load all questions from this dimension
                        dimension_questions = file_content[top_level_key]
                        for q_id, q_config in dimension_questions.items():
                            # Add dimension metadata to each question
                            q_config['_dimension'] = question_key
                            combined_config['questions'][q_id] = q_config
                    else:
                        print(f"Warning: Expected structure not found in {filename}")
                        
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
            else:
                print(f"Warning: Question file {filename} not found")
        
        return combined_config
    
    def get_question_config(self, question_key: str) -> Dict[str, Any]:
        """Get configuration for a specific question"""
        all_questions = self.load_all_questions()
        return all_questions['questions'].get(question_key, {})
    
    def list_available_questions(self) -> list:
        """List all available question keys"""
        all_questions = self.load_all_questions()
        return list(all_questions['questions'].keys())

# Global instance for easy importing
questions_loader = QuestionsLoader() 