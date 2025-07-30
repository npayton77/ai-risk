# AI Risk Assessment Tool - Project Overview

## What This Project Does

The AI Risk Assessment Tool is a web-based application that helps organizations evaluate the risk level of their AI implementations. Users answer questions across five key dimensions (autonomy, oversight, impact, orchestration, and data sensitivity), and the system calculates an overall risk score with tailored recommendations.

**Key Features:**
- Multi-step wizard interface for guided assessments
- Flexible scoring system supporting multiple questions per dimension
- Weighted question importance and configurable aggregation
- Risk-based recommendations with conditional logic
- HTML report generation with email functionality
- Modular, YAML-driven configuration

## Architecture Overview

The application is built using **Flask (Python)** with a modular design that separates concerns across multiple files and configuration systems.

### Core Components

1. **Web Application** (`app_refactored.py`) - Flask routes and request handling
2. **Risk Assessment Logic** (`risk_assessor.py`) - Core scoring algorithms
3. **Question Management** (`questions_loader.py`) - Dynamic question loading
4. **Report Generation** (`report_generator.py`) - HTML report creation
5. **Multi-Step Interface** (`multistep_template_generator.py`) - Wizard UI generation
6. **Configuration Files** - YAML-based settings for questions, scoring, and recommendations

### User Experience Flow

```
Home Page → Step 1 (Basic Info) → Step 2 (Autonomy) → Step 3 (Oversight) 
→ Step 4 (Impact) → Step 5 (Orchestration) → Step 6 (Data Sensitivity) 
→ Final Report with Recommendations
```

## File Structure and Purpose

### Core Application Files

**`app_refactored.py`** (387 lines)
- Main Flask application with routes
- Multi-step wizard logic and session management
- Integration point for all other components
- Handles form validation and assessment generation

**`risk_assessor.py`** (116 lines)
- `RiskAssessment` dataclass for result storage
- `AIRiskAssessor` class with core scoring logic
- Risk level calculation and recommendation retrieval
- Integrates with YAML configuration files

**`questions_loader.py`** (83 lines)
- `QuestionsLoader` class for dynamic question loading
- Combines individual question files into unified structure
- Maintains backward compatibility with original format

### UI Generation

**`template_generator.py`**
- Generates single-page assessment form (legacy interface)
- HTML form creation with question rendering
- Maintains compatibility for single-page workflow

**`multistep_template_generator.py`**
- Creates multi-step wizard interface
- Progress tracking and navigation
- Per-step validation and styling
- Modern responsive design

**`report_generator.py`** (810 lines)
- Comprehensive HTML report generation
- Risk visualization and styling
- Detailed recommendations and explanations
- Email-ready formatting

### Supporting Modules

**`email_handlers.py`**
- Email content generation (complete and summary reports)
- Integration with recommendation system
- HTML and plain text formatting

**`static_pages.py`**
- System information and status pages
- Email configuration help
- Feature overview and documentation

### Advanced Features

**`flexible_risk_assessor.py`** (230+ lines)
- Next-generation scoring system
- Supports multiple questions per dimension
- Weighted aggregation strategies
- Backward compatible with current system

## Configuration System

The application uses a **YAML-driven configuration** approach for maximum flexibility:

### Question Configuration (`questions/` directory)

Each risk dimension has its own YAML file:

- **`autonomy.yaml`** - AI decision-making power questions
- **`oversight.yaml`** - Human monitoring and control questions  
- **`impact.yaml`** - Scope and consequence questions
- **`orchestration.yaml`** - AI system complexity questions
- **`data_sensitivity.yaml`** - Data privacy and compliance questions

**Structure Example:**
```yaml
dimension_questions:
  question_id:
    title: "Question displayed to user"
    help_text: "Additional context"
    required: true
    options:
      option_key:
        title: "Option Label"
        description: "Detailed explanation"
    reasoning_prompt: "Optional reasoning prompt"
```

### Scoring Configuration (`scoring.yaml`)

**Current System:**
```yaml
scoring:
  dimensions:
    autonomy:
      tool: 1      # Lowest risk
      assistant: 2
      agent: 3
      autonomous: 4  # Highest risk
```

**Flexible System (`scoring_flexible.yaml`):**
```yaml
dimensions:
  autonomy:
    aggregation: "weighted_average"
    questions:
      autonomy:
        weight: 1.0
        scoring: { tool: 1, assistant: 2, agent: 3, autonomous: 4 }
      autonomy_scope:
        weight: 0.8
        scoring: { limited: 1, moderate: 2, broad: 3, unlimited: 4 }
```

### Recommendations (`recommendations.yaml`)

```yaml
by_risk_level:
  low: ["Standard review processes", "Clear escalation paths"]
  medium: ["Regular audits", "Confidence thresholds"]
  high: ["Real-time monitoring", "Circuit breakers"]
  critical: ["Sandboxed testing", "Formal verification"]

conditional:
  - condition: { autonomy: ["autonomous"], oversight: ["minimal"] }
    recommendation: "HIGH PRIORITY: Increase oversight"
```

## Key Concepts

### Risk Scoring

1. **Questions** have multiple choice answers
2. **Answers** map to numeric scores (typically 1-4, low to high risk)
3. **Dimensions** aggregate question scores (5 dimensions total)
4. **Risk Level** determined by total score (Low/Medium/High/Critical)
5. **Recommendations** based on risk level and specific conditions

### Session Management

The multi-step wizard uses Flask sessions to persist user input:
- Each step validates and stores answers
- Session data accumulated across steps
- Final validation ensures all required fields present
- Session cleared when starting new assessment

### Modular Design Benefits

- **Separation of Concerns**: Logic, UI, and configuration separated
- **Easy Maintenance**: Changes isolated to specific components
- **Extensibility**: New questions/dimensions added via YAML
- **Testing**: Individual components can be tested independently
- **Flexibility**: Multiple interfaces (single-page, multi-step) supported

## Recent Evolution

### Version History

**Original Design:**
- Monolithic `app_refactored.py` (757 lines)
- Single `questions.yaml` file
- Embedded recommendations in scoring file
- Single-page interface only

**Current Design:**
- Modular architecture (6 core files)
- Individual question files per dimension
- Separate recommendations configuration
- Multi-step wizard interface
- Flexible scoring system for extensibility

### Key Refactoring Achievements

1. **Modularization**: Broke 757-line monolith into focused components
2. **Question Separation**: Individual YAML files for each dimension
3. **Recommendation Extraction**: Dedicated configuration file
4. **Multi-Step Interface**: Modern wizard with progress tracking
5. **Flexible Scoring**: Support for multiple questions per dimension
6. **PDF Removal**: Simplified to HTML-only reports

## Development Workflow

### Adding New Questions

1. Edit appropriate file in `questions/` directory
2. Add scoring configuration to `scoring.yaml` (or `scoring_flexible.yaml`)
3. Test the changes - system automatically picks up new questions
4. See `ADDING_QUESTIONS.md` for detailed instructions

### Modifying Recommendations

1. Edit `recommendations.yaml`
2. Add risk level recommendations or conditional logic
3. No code changes required - loaded dynamically

### UI Customization

- **Multi-step**: Modify `multistep_template_generator.py`
- **Single-page**: Modify `template_generator.py`
- **Reports**: Modify `report_generator.py`
- **Styling**: CSS embedded in template generators

## Technical Details

### Dependencies

- **Flask**: Web framework
- **PyYAML**: Configuration file parsing
- **Python 3.13**: Runtime environment
- **Virtual Environment**: Dependency isolation

### Scoring Algorithm

```python
# Basic scoring (current)
score = sum(dimension_scores for each dimension)
risk_level = determine_level_from_thresholds(score)

# Flexible scoring (future)
for dimension in dimensions:
    question_scores = [score_question(q) for q in dimension.questions]
    weighted_scores = [score * weight for score, weight in zip(question_scores, weights)]
    dimension_score = aggregate(weighted_scores, strategy)
total_score = sum(dimension_scores)
```

### Session Architecture

```python
# Session structure
session['assessment_data'] = {
    'workflow_name': 'user input',
    'assessor': 'user input', 
    'autonomy': 'selected option',
    'autonomy_reasoning': 'optional text',
    # ... other dimensions
}
```

## Testing and Validation

### Manual Testing

1. Run application: `source venv/bin/activate && python app_refactored.py`
2. Navigate to `http://localhost:9000`
3. Complete assessment through multi-step wizard
4. Verify report generation and recommendations

### Automated Testing

The system includes Playwright automation for testing:
- Form completion simulation
- Report generation verification
- Multi-step navigation testing

## Future Enhancements

### Flexible Scoring System

The `flexible_risk_assessor.py` demonstrates next-generation capabilities:
- Multiple questions per dimension
- Weighted importance scoring
- Configurable aggregation strategies
- Backward compatibility with current system

### Potential Extensions

- **Database Storage**: Persist assessments and historical data
- **User Management**: Multi-user access and organization management
- **API Interface**: Programmatic access to assessment functionality
- **Advanced Analytics**: Trend analysis and comparative reporting
- **Custom Dimensions**: User-defined risk categories

## Getting Started as a Developer

1. **Understand the Flow**: Review this overview and trace a user journey
2. **Explore Configuration**: Examine YAML files to understand data structure
3. **Read Core Logic**: Start with `risk_assessor.py` for scoring logic
4. **Test Changes**: Use the application to validate modifications
5. **Reference Documentation**: See `ADDING_QUESTIONS.md` for common tasks

The codebase is designed for maintainability and extensibility. Most customizations can be achieved through YAML configuration changes without touching Python code. 