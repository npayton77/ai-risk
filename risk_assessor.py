#!/usr/bin/env python3
"""
Risk Assessment Logic for AI Risk Assessment Tool
Contains the core risk assessment algorithms and data structures
"""

import yaml
from dataclasses import dataclass
from typing import Dict, List, Tuple
from questions_loader import questions_loader

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
    def __init__(self, scoring_file: str = 'scoring.yaml', recommendations_file: str = 'recommendations.yaml', questions_dir: str = 'questions'):
        """Initialize with YAML configuration files"""
        # Load scoring configuration
        with open(scoring_file, 'r', encoding='utf-8') as f:
            self.scoring_config = yaml.safe_load(f)
        
        # Load recommendations configuration
        with open(recommendations_file, 'r', encoding='utf-8') as f:
            self.recommendations_config = yaml.safe_load(f)
        
        # Load questions configuration
        self.questions_config = questions_loader.load_all_questions()
        
        # Extract configuration data
        self.dimension_scores = self.scoring_config['scoring']['dimensions']
        self.risk_thresholds = self.scoring_config['scoring']['risk_thresholds']
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
    
    def _get_dimension_score(self, dimension: str, value: str) -> int:
        """Get numerical score for a dimension value"""
        if dimension in self.dimension_scores and value in self.dimension_scores[dimension]:
            return self.dimension_scores[dimension][value]
        return 0
    
    def _get_email_risk_summary(self, risk_level: str) -> str:
        """Get email-friendly risk summary"""
        summaries = {
            'low': 'This AI system presents minimal risk to your organization. Standard monitoring and review processes should be sufficient.',
            'medium': 'This AI system presents moderate risk requiring enhanced oversight and monitoring procedures.',
            'high': 'This AI system presents significant risk requiring comprehensive monitoring, clear escalation procedures, and dedicated oversight.',
            'critical': 'This AI system presents critical risk requiring extensive safeguards, formal approval processes, and continuous monitoring.'
        }
        return summaries.get(risk_level, 'Risk level assessment unavailable.') 