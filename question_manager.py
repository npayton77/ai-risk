#!/usr/bin/env python3
"""
Question Manager - Main entry point for question management tasks
"""

import sys
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description="AI Risk Assessment Question Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python question_manager.py add          # Add a new question interactively
  python question_manager.py list         # List all questions
  python question_manager.py validate     # Validate question files
        """
    )
    
    parser.add_argument(
        'action',
        choices=['add', 'list', 'validate', 'help'],
        help='Action to perform'
    )
    
    args = parser.parse_args()
    
    if args.action == 'add':
        from add_question import QuestionBuilder
        builder = QuestionBuilder()
        builder.run()
    
    elif args.action == 'list':
        list_questions()
    
    elif args.action == 'validate':
        validate_questions()
    
    elif args.action == 'help':
        parser.print_help()

def list_questions():
    """List all questions in the system"""
    import yaml
    from pathlib import Path
    
    questions_dir = Path("questions")
    dimensions = ["autonomy", "oversight", "impact", "orchestration", "data_sensitivity"]
    
    print("AI Risk Assessment - Current Questions\n")
    
    total_questions = 0
    
    for dimension in dimensions:
        question_file = questions_dir / f"{dimension}.yaml"
        if not question_file.exists():
            continue
        
        with open(question_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
        
        dimension_key = f"{dimension}_questions"
        questions = data.get(dimension_key, {})
        
        print(f"📁 {dimension.upper()} ({len(questions)} questions)")
        
        for question_id, question_data in questions.items():
            title = question_data.get('title', 'No title')
            required = "Required" if question_data.get('required', False) else "Optional"
            options_count = len(question_data.get('options', {}))
            
            print(f"   └── {question_id}: {title}")
            print(f"       {required} • {options_count} options")
        
        total_questions += len(questions)
        print()
    
    print(f"Total: {total_questions} questions across {len(dimensions)} dimensions")

def validate_questions():
    """Validate question files for common issues"""
    import yaml
    from pathlib import Path
    
    print("Validating question files...\n")
    
    questions_dir = Path("questions")
    scoring_file = Path("scoring_flexible.yaml")
    
    errors = []
    warnings = []
    
    # Load scoring data
    try:
        with open(scoring_file, 'r', encoding='utf-8') as f:
            scoring_data = yaml.safe_load(f) or {}
    except Exception as e:
        errors.append(f"Cannot load scoring file: {e}")
        return
    
    dimensions = ["autonomy", "oversight", "impact", "orchestration", "data_sensitivity"]
    
    for dimension in dimensions:
        question_file = questions_dir / f"{dimension}.yaml"
        
        if not question_file.exists():
            warnings.append(f"Missing question file: {question_file}")
            continue
        
        # Load question data
        try:
            with open(question_file, 'r', encoding='utf-8') as f:
                question_data = yaml.safe_load(f) or {}
        except Exception as e:
            errors.append(f"Cannot load {question_file}: {e}")
            continue
        
        dimension_key = f"{dimension}_questions"
        questions = question_data.get(dimension_key, {})
        
        # Check each question
        for question_id, question in questions.items():
            # Check required fields
            if 'title' not in question:
                errors.append(f"{dimension}/{question_id}: Missing title")
            
            if 'options' not in question or not question['options']:
                errors.append(f"{dimension}/{question_id}: Missing options")
                continue
            
            # Check scoring exists
            scoring_questions = scoring_data.get('dimensions', {}).get(dimension, {}).get('questions', {})
            if question_id not in scoring_questions:
                warnings.append(f"{dimension}/{question_id}: No scoring configuration")
                continue
            
            # Check all options have scores
            question_scoring = scoring_questions[question_id].get('scoring', {})
            for option_key in question['options']:
                if option_key not in question_scoring:
                    errors.append(f"{dimension}/{question_id}: Option '{option_key}' has no score")
    
    # Report results
    if errors:
        print("Errors found:")
        for error in errors:
            print(f"   • {error}")
        print()
    
    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"   • {warning}")
        print()
    
    if not errors and not warnings:
        print("All question files are valid!")
    else:
        print(f"Validation complete: {len(errors)} errors, {len(warnings)} warnings")

if __name__ == "__main__":
    main()
