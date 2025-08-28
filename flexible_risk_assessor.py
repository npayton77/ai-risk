"""
Enhanced AI Risk Assessor with Flexible Multi-Question Scoring
Supports multiple questions per dimension with weights and aggregation strategies
"""

import yaml
from dataclasses import dataclass
from typing import Dict, Any, List, Tuple, Optional
from statistics import mean
from questions_loader import QuestionsLoader

@dataclass
class RiskAssessment:
    workflow_name: str
    assessor: str
    autonomy: str
    oversight: str
    impact: str
    orchestration: str
    data_sensitivity: str
    risk_score: int
    risk_level: str
    recommendations: List[str]
    conditional_recommendations: List[str]
    dimension_scores: Dict[str, float]  # Individual dimension scores
    question_scores: Dict[str, Dict[str, float]]  # Detailed question scores
    responses: Dict[str, str]  # Reasoning responses for compatibility with report generator
    date: str = ""  # Assessment date for compatibility
    questions_config: Dict = None  # Questions configuration for report generation

class FlexibleAIRiskAssessor:
    def __init__(self, scoring_file: str = 'scoring_flexible.yaml', 
                 recommendations_file: str = 'recommendations.yaml', 
                 questions_dir: str = 'questions'):
        """Initialize with flexible YAML configuration files"""
        # Store paths for later reloads
        self.scoring_file = scoring_file
        self.recommendations_file = recommendations_file
        self.questions_dir = questions_dir
        # Initial load
        self.reload_configs()

    def reload_configs(self) -> None:
        """Reload YAML configs to pick up admin changes without restarting the app"""
        # Load scoring configuration
        with open(self.scoring_file, 'r', encoding='utf-8') as f:
            self.scoring_config = yaml.safe_load(f)
        
        # Load recommendations configuration
        with open(self.recommendations_file, 'r', encoding='utf-8') as f:
            self.recommendations_config = yaml.safe_load(f)
        
        # Load questions configuration (fresh each time)
        questions_loader = QuestionsLoader(self.questions_dir)
        self.questions_config = questions_loader.load_all_questions()
        
        # Extract configuration data
        self.dimension_config = self.scoring_config['dimensions']
        self.risk_thresholds = self.scoring_config['risk_thresholds']
        self.risk_styling = self.scoring_config['risk_styling']
        self.default_scoring = self.scoring_config.get('default_scoring', {})

    def calculate_question_score(self, dimension: str, question_id: str, answer: str) -> float:
        """Calculate score for a single question"""
        dimension_config = self.dimension_config.get(dimension, {})
        questions_config = dimension_config.get('questions', {})
        question_config = questions_config.get(question_id, {})
        
        # DEBUG: Show scoring lookup
        print(f"🔍 DEBUG - SCORING LOOKUP:")
        print(f"  Dimension: {dimension}")
        print(f"  Question ID: {question_id}")
        print(f"  Answer: {answer}")
        print(f"  Available questions in {dimension}: {list(questions_config.keys())}")
        print(f"  Question config found: {bool(question_config)}")
        if question_config:
            print(f"  Scoring options: {question_config.get('scoring', {})}")
        print(f"🔍 END DEBUG")
        
        # Get scoring for this specific question
        scoring = question_config.get('scoring', {})
        
        if answer in scoring:
            return scoring[answer]
        
        # Fall back to default scoring if available
        for scale_name, scale_scoring in self.default_scoring.items():
            if answer in scale_scoring:
                return scale_scoring[answer]
        
        # If no scoring found, return 0 (or could raise exception)
        print(f"Warning: No scoring found for {dimension}.{question_id}.{answer}")
        return 0.0

    def aggregate_dimension_scores(self, dimension: str, question_scores: Dict[str, float]) -> float:
        """Aggregate multiple question scores for a dimension"""
        dimension_config = self.dimension_config.get(dimension, {})
        aggregation = dimension_config.get('aggregation', 'max')
        questions_config = dimension_config.get('questions', {})
        
        # DEBUG: Show aggregation details
        print(f"\n🔍 DEBUG - AGGREGATING {dimension.upper()}:")
        print(f"  Question Scores: {question_scores}")
        print(f"  Aggregation Method: {aggregation}")
        print(f"  Questions Config: {questions_config}")
        
        if not question_scores:
            return 0.0
        
        if aggregation == 'sum':
            return sum(question_scores.values())
        
        elif aggregation == 'average':
            # Filter out reasoning fields
            actual_scores = [score for q_id, score in question_scores.items() if not q_id.endswith('_reasoning')]
            return mean(actual_scores) if actual_scores else 0.0
        
        elif aggregation == 'weighted_average':
            total_weighted_score = 0.0
            total_weight = 0.0
            
            for question_id, score in question_scores.items():
                # Skip reasoning fields - they shouldn't be included in scoring
                if question_id.endswith('_reasoning'):
                    print(f"    {question_id}: SKIPPED (reasoning field)")
                    continue
                    
                weight = questions_config.get(question_id, {}).get('weight', 1.0)
                total_weighted_score += score * weight
                total_weight += weight
                print(f"    {question_id}: score={score}, weight={weight}, weighted={score * weight}")
            
            final_score = total_weighted_score / total_weight if total_weight > 0 else 0.0
            print(f"  Final Score: {total_weighted_score}/{total_weight} = {final_score}")
            print(f"🔍 END DEBUG\n")
            return final_score
        
        elif aggregation == 'max':
            # Filter out reasoning fields and find maximum score
            actual_scores = [score for q_id, score in question_scores.items() if not q_id.endswith('_reasoning')]
            if actual_scores:
                max_score = max(actual_scores)
                print(f"  Maximum Score: {max_score}")
                print(f"🔍 END DEBUG\n")
                return max_score
            else:
                print(f"  No actual questions found, returning 0.0")
                print(f"🔍 END DEBUG\n")
                return 0.0
        
        elif aggregation == 'min':
            return min(question_scores.values())
        
        else:
            # Default to average
            return mean(question_scores.values())

    def calculate_flexible_risk_score(self, assessment_data: Dict[str, str]) -> Tuple[float, str, Dict[str, float], Dict[str, Dict[str, float]]]:
        """Calculate risk score using flexible multi-question system"""
        
        dimension_scores = {}
        question_scores = {}
        
        # Process each dimension
        for dimension in ['autonomy', 'oversight', 'impact', 'orchestration', 'data_sensitivity']:
            if dimension not in self.dimension_config:
                continue
                
            dimension_question_scores = {}
            
            # Get all questions for this dimension from the assessment data
            for key, value in assessment_data.items():
                # Check if this key belongs to this dimension
                if self.is_question_in_dimension(key, dimension):
                    score = self.calculate_question_score(dimension, key, value)
                    dimension_question_scores[key] = score
            
            # Aggregate scores for this dimension
            if dimension_question_scores:
                dimension_scores[dimension] = self.aggregate_dimension_scores(dimension, dimension_question_scores)
                question_scores[dimension] = dimension_question_scores
            else:
                dimension_scores[dimension] = 0.0
                question_scores[dimension] = {}
        
        # Calculate total risk score
        total_score = sum(dimension_scores.values())
        
        # Determine risk level
        risk_level = self.determine_risk_level(total_score)
        
        return total_score, risk_level, dimension_scores, question_scores

    def is_question_in_dimension(self, question_id: str, dimension: str) -> bool:
        """Check if a question belongs to a specific dimension"""
        # Ignore reasoning fields completely
        if question_id.endswith('_reasoning'):
            return False
        # First check if question is explicitly configured for this dimension in scoring
        dimension_config = self.dimension_config.get(dimension, {})
        questions_config = dimension_config.get('questions', {})
        if question_id in questions_config:
            return True
        
        # Fallback to old heuristic for backward compatibility
        if question_id.startswith(dimension):
            return True
            
        return False

    def determine_risk_level(self, score: float) -> str:
        """Determine risk level based on score"""
        # Round score for threshold comparison
        rounded_score = round(score)
        
        # DEBUG: Show risk calculation
        print(f"\n🔍 DEBUG - RISK LEVEL CALCULATION:")
        print(f"  Total Score: {score}")
        print(f"  Rounded Score: {rounded_score}")
        print(f"  Risk Thresholds: {self.risk_thresholds}")
        
        for level, config in self.risk_thresholds.items():
            print(f"  Checking {level}: {config['min']} <= {rounded_score} <= {config['max']} = {config['min'] <= rounded_score <= config['max']}")
            if config['min'] <= rounded_score <= config['max']:
                print(f"  ✅ Matched: {config['level']}")
                print(f"🔍 END DEBUG\n")
                return config['level']
        
        # Handle scores below the minimum threshold
        min_threshold = min(config['min'] for config in self.risk_thresholds.values())
        if rounded_score < min_threshold:
            print(f"  ✅ Score {rounded_score} below minimum threshold {min_threshold}, returning 'low'")
            print(f"🔍 END DEBUG\n")
            return 'low'
        
        print(f"  ❌ No threshold matched, returning 'unknown'")
        print(f"🔍 END DEBUG\n")
        return 'unknown'

    def get_recommendations(self, risk_level: str) -> List[str]:
        """Get base recommendations for risk level"""
        return self.recommendations_config.get('by_risk_level', {}).get(risk_level, [])

    def get_conditional_recommendations(self, assessment_data: Dict[str, str]) -> List[str]:
        """Get conditional recommendations based on specific answer combinations"""
        conditional_recs = []
        
        for condition_config in self.recommendations_config.get('conditional', []):
            condition = condition_config.get('condition', {})
            recommendation = condition_config.get('recommendation', '')
            
            # Check if all conditions are met
            condition_met = True
            for field, required_values in condition.items():
                user_value = assessment_data.get(field)
                if user_value not in required_values:
                    condition_met = False
                    break
            
            if condition_met and recommendation:
                conditional_recs.append(recommendation)
        
        return conditional_recs

    def assess_risk(self, workflow_name: str, assessor: str, **assessment_data) -> RiskAssessment:
        """Perform complete risk assessment with flexible scoring"""
        
        # Calculate risk using flexible system
        risk_score, risk_level, dimension_scores, question_scores = self.calculate_flexible_risk_score(assessment_data)
        
        # Get recommendations
        base_recommendations = self.get_recommendations(risk_level)
        conditional_recommendations = self.get_conditional_recommendations(assessment_data)
        
        return RiskAssessment(
            workflow_name=workflow_name,
            assessor=assessor,
            autonomy=assessment_data.get('autonomy', ''),
            oversight=assessment_data.get('oversight', ''),
            impact=assessment_data.get('impact', ''),
            orchestration=assessment_data.get('orchestration', ''),
            data_sensitivity=assessment_data.get('data_sensitivity', ''),
            risk_score=risk_score,
            risk_level=risk_level,
            recommendations=base_recommendations,
            conditional_recommendations=conditional_recommendations,
            dimension_scores=dimension_scores,
            question_scores=question_scores
        )

# Example usage and testing
if __name__ == "__main__":
    # Test the flexible scoring system
    assessor = FlexibleAIRiskAssessor()
    
    # Example with multiple autonomy questions
    test_data = {
        'autonomy': 'autonomous',
        'autonomy_scope': 'broad', 
        'autonomy_frequency': 'continuously',
        'oversight': 'minimal',
        'impact': 'external',
        'orchestration': 'hierarchical',
        'data_sensitivity': 'regulated'
    }
    
    assessment = assessor.assess_risk(
        workflow_name="Multi-Question Test",
        assessor="Flexible Scoring Test",
        **test_data
    )
    
    print(f"Risk Score: {assessment.risk_score}")
    print(f"Risk Level: {assessment.risk_level}")
    print(f"Dimension Scores: {assessment.dimension_scores}")
    print(f"Question Scores: {assessment.question_scores}") 