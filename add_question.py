#!/usr/bin/env python3
"""
Interactive CLI tool for adding questions to the AI Risk Assessment system.
Makes it easy to add new questions without manually editing YAML files.
"""

import os
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_header(text: str):
    """Print a colored header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}🎯 {text}{Colors.END}")

def print_success(text: str):
    """Print a success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text: str):
    """Print an error message"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text: str):
    """Print a warning message"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def get_input(prompt: str, default: str = None) -> str:
    """Get user input with optional default"""
    if default:
        full_prompt = f"{Colors.CYAN}{prompt}{Colors.END} [{default}]: "
    else:
        full_prompt = f"{Colors.CYAN}{prompt}{Colors.END}: "
    
    result = input(full_prompt).strip()
    return result if result else default

def get_choice(prompt: str, choices: List[str]) -> str:
    """Get user choice from a list of options"""
    print(f"\n{Colors.CYAN}{prompt}{Colors.END}")
    for i, choice in enumerate(choices, 1):
        print(f"  {i}. {choice}")
    
    while True:
        try:
            choice_num = int(input(f"{Colors.CYAN}Select (1-{len(choices)}){Colors.END}: "))
            if 1 <= choice_num <= len(choices):
                return choices[choice_num - 1]
            else:
                print_error(f"Please enter a number between 1 and {len(choices)}")
        except ValueError:
            print_error("Please enter a valid number")

def get_float(prompt: str, default: float = None, min_val: float = None, max_val: float = None) -> float:
    """Get a float input with validation"""
    while True:
        try:
            result = get_input(prompt, str(default) if default else None)
            value = float(result)
            
            if min_val is not None and value < min_val:
                print_error(f"Value must be at least {min_val}")
                continue
            if max_val is not None and value > max_val:
                print_error(f"Value must be at most {max_val}")
                continue
                
            return value
        except (ValueError, TypeError):
            print_error("Please enter a valid number")

def get_int(prompt: str, default: int = None, min_val: int = None, max_val: int = None) -> int:
    """Get an integer input with validation"""
    while True:
        try:
            result = get_input(prompt, str(default) if default else None)
            value = int(result)
            
            if min_val is not None and value < min_val:
                print_error(f"Value must be at least {min_val}")
                continue
            if max_val is not None and value > max_val:
                print_error(f"Value must be at most {max_val}")
                continue
                
            return value
        except (ValueError, TypeError):
            print_error("Please enter a valid number")

class QuestionBuilder:
    """Interactive question builder for the AI Risk Assessment system"""
    
    def __init__(self):
        self.dimensions = ["autonomy", "oversight", "impact", "orchestration", "data_sensitivity"]
        self.questions_dir = Path("questions")
        self.scoring_file = Path("scoring_flexible.yaml")
        
        # Validate files exist
        if not self.questions_dir.exists():
            print_error(f"Questions directory not found: {self.questions_dir}")
            sys.exit(1)
            
        if not self.scoring_file.exists():
            print_error(f"Scoring file not found: {self.scoring_file}")
            sys.exit(1)
    
    def load_yaml_file(self, file_path: Path) -> Dict[str, Any]:
        """Load a YAML file safely"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print_error(f"Error loading {file_path}: {e}")
            sys.exit(1)
    
    def save_yaml_file(self, file_path: Path, data: Dict[str, Any]):
        """Save data to a YAML file safely"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False, indent=2)
        except Exception as e:
            print_error(f"Error saving {file_path}: {e}")
            sys.exit(1)
    
    def validate_question_id(self, question_id: str, dimension: str) -> bool:
        """Validate that question ID is unique and well-formed"""
        # Check format
        if not question_id.replace('_', '').replace('-', '').isalnum():
            print_error("Question ID must contain only letters, numbers, underscores, and hyphens")
            return False
        
        # Check if already exists in dimension
        question_file = self.questions_dir / f"{dimension}.yaml"
        if question_file.exists():
            data = self.load_yaml_file(question_file)
            dimension_key = f"{dimension}_questions"
            if dimension_key in data and question_id in data[dimension_key]:
                print_error(f"Question ID '{question_id}' already exists in {dimension} dimension")
                return False
        
        return True
    
    def collect_question_data(self) -> Dict[str, Any]:
        """Collect all question data interactively"""
        print_header("AI Risk Assessment - Question Builder")
        print("This tool will help you add a new question to the assessment system.")
        print("All files will be updated automatically.")
        
        # Select dimension
        dimension = get_choice("Select dimension", self.dimensions).lower()
        
        # Get question ID
        while True:
            question_id = get_input("Question ID (e.g., 'decision_speed', 'review_frequency')")
            if not question_id:
                print_error("Question ID is required")
                continue
            if self.validate_question_id(question_id, dimension):
                break
        
        # Get question details
        title = get_input("Question title (displayed to users)")
        while not title:
            print_error("Question title is required")
            title = get_input("Question title (displayed to users)")
        
        help_text = get_input("Help text (optional, provides additional context)", "")
        required = get_choice("Is this question required?", ["Yes", "No"]) == "Yes"
        
        # Collect options
        print_header("Question Options")
        print("Add the answer options for this question. Each option needs:")
        print("- Key: Short identifier (e.g., 'low', 'high', 'never', 'always')")
        print("- Title: Display name for users")
        print("- Description: Detailed explanation")
        print("- Risk Score: 1-4 (1=lowest risk, 4=highest risk)")
        
        options = {}
        option_scores = {}
        
        while True:
            option_num = len(options) + 1
            print(f"\n{Colors.BOLD}Option {option_num}:{Colors.END}")
            
            option_key = get_input("Option key (e.g., 'low', 'medium', 'high')")
            if not option_key:
                if len(options) == 0:
                    print_error("At least one option is required")
                    continue
                else:
                    break
            
            if option_key in options:
                print_error(f"Option key '{option_key}' already exists")
                continue
            
            option_title = get_input("Option title (displayed to users)")
            if not option_title:
                print_error("Option title is required")
                continue
            
            option_description = get_input("Option description (detailed explanation)", "")
            risk_score = get_int("Risk score (1=lowest risk, 4=highest risk)", min_val=1, max_val=4)
            
            options[option_key] = {
                "title": option_title,
                "description": option_description
            }
            option_scores[option_key] = risk_score
            
            print_success(f"Added option: {option_key} -> {option_title} (score: {risk_score})")
            
            if len(options) >= 2:
                add_more = get_choice("Add another option?", ["Yes", "No"]) == "Yes"
                if not add_more:
                    break
        
        # Get reasoning prompt
        reasoning_prompt = get_input("Reasoning prompt (optional, asks user to explain their choice)", "")
        
        # Get question weight
        print_header("Question Scoring")
        print("Weight determines how important this question is relative to others in the dimension:")
        print("- 1.0: Core question (primary risk indicator)")
        print("- 0.8: Important supporting question")
        print("- 0.5-0.6: Contextual details")
        print("- 0.3: Optional information")
        
        weight = get_float("Question weight", default=1.0, min_val=0.1, max_val=3.0)
        
        return {
            "dimension": dimension,
            "question_id": question_id,
            "title": title,
            "help_text": help_text,
            "required": required,
            "options": options,
            "reasoning_prompt": reasoning_prompt,
            "weight": weight,
            "scoring": option_scores
        }
    
    def add_question_to_dimension_file(self, question_data: Dict[str, Any]):
        """Add question to the appropriate dimension YAML file"""
        dimension = question_data["dimension"]
        question_file = self.questions_dir / f"{dimension}.yaml"
        
        # Load existing data
        data = self.load_yaml_file(question_file)
        
        # Ensure the dimension questions key exists
        dimension_key = f"{dimension}_questions"
        if dimension_key not in data:
            data[dimension_key] = {}
        
        # Add the new question
        question_entry = {
            "title": question_data["title"],
            "required": question_data["required"],
            "options": question_data["options"]
        }
        
        if question_data["help_text"]:
            question_entry["help_text"] = question_data["help_text"]
        
        if question_data["reasoning_prompt"]:
            question_entry["reasoning_prompt"] = question_data["reasoning_prompt"]
        
        data[dimension_key][question_data["question_id"]] = question_entry
        
        # Save the file
        self.save_yaml_file(question_file, data)
        print_success(f"Updated {question_file}")
    
    def add_question_to_scoring_file(self, question_data: Dict[str, Any]):
        """Add question scoring to the flexible scoring file"""
        # Load existing scoring data
        scoring_data = self.load_yaml_file(self.scoring_file)
        
        # Ensure dimensions structure exists
        if "dimensions" not in scoring_data:
            scoring_data["dimensions"] = {}
        
        dimension = question_data["dimension"]
        if dimension not in scoring_data["dimensions"]:
            scoring_data["dimensions"][dimension] = {
                "aggregation": "weighted_average",
                "questions": {}
            }
        
        if "questions" not in scoring_data["dimensions"][dimension]:
            scoring_data["dimensions"][dimension]["questions"] = {}
        
        # Add the question scoring
        scoring_data["dimensions"][dimension]["questions"][question_data["question_id"]] = {
            "weight": question_data["weight"],
            "scoring": question_data["scoring"]
        }
        
        # Save the file
        self.save_yaml_file(self.scoring_file, scoring_data)
        print_success(f"Updated {self.scoring_file}")
    
    def display_summary(self, question_data: Dict[str, Any]):
        """Display a summary of the added question"""
        print_header("Question Added Successfully!")
        
        print(f"{Colors.BOLD}Dimension:{Colors.END} {question_data['dimension']}")
        print(f"{Colors.BOLD}Question ID:{Colors.END} {question_data['question_id']}")
        print(f"{Colors.BOLD}Title:{Colors.END} {question_data['title']}")
        print(f"{Colors.BOLD}Required:{Colors.END} {question_data['required']}")
        print(f"{Colors.BOLD}Weight:{Colors.END} {question_data['weight']}")
        
        print(f"\n{Colors.BOLD}Options:{Colors.END}")
        for key, option in question_data['options'].items():
            score = question_data['scoring'][key]
            print(f"  {key}: {option['title']} (risk score: {score})")
        
        print(f"\n{Colors.BOLD}Files Updated:{Colors.END}")
        print(f"  ✅ questions/{question_data['dimension']}.yaml")
        print(f"  ✅ scoring_flexible.yaml")
        
        print(f"\n{Colors.GREEN}🎉 Ready to test! Run your Flask app and try the new question.{Colors.END}")
    
    def run(self):
        """Run the interactive question builder"""
        try:
            question_data = self.collect_question_data()
            
            # Confirm before making changes
            print_header("Confirmation")
            print("About to add this question:")
            print(f"- Dimension: {question_data['dimension']}")
            print(f"- ID: {question_data['question_id']}")
            print(f"- Title: {question_data['title']}")
            print(f"- Options: {len(question_data['options'])}")
            
            confirm = get_choice("Proceed with adding this question?", ["Yes", "No"])
            if confirm != "Yes":
                print("Cancelled.")
                return
            
            # Add the question
            self.add_question_to_dimension_file(question_data)
            self.add_question_to_scoring_file(question_data)
            
            # Show summary
            self.display_summary(question_data)
            
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Cancelled by user.{Colors.END}")
        except Exception as e:
            print_error(f"Unexpected error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    builder = QuestionBuilder()
    builder.run()
