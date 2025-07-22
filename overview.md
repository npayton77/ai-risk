# AI Risk Assessment Web Application - Technical Overview

## 📋 Application Description

The AI Risk Assessment Web Application is a comprehensive tool designed to evaluate and score the risk levels associated with AI implementations in business workflows. The application provides a structured questionnaire-based assessment that generates detailed reports with risk scores, recommendations, and visual analytics.

## 🎯 Core Purpose

- **Risk Evaluation**: Assess AI implementations across multiple dimensions (Autonomy, Oversight, Impact, Orchestration, Data Sensitivity)
- **Scoring System**: Calculate numerical risk scores (1-20 scale) based on weighted responses
- **Report Generation**: Create comprehensive, visually appealing HTML reports with actionable recommendations
- **Configuration Management**: Allow non-technical users to modify questions and scoring without code changes

## 🏗️ Architecture Overview

### Modular Design
The application follows a clean separation of concerns with distinct modules:

```
web/
├── app_refactored.py          # Main Flask application
├── template_generator.py      # Dynamic form generation
├── report_generator.py        # Comprehensive report creation
├── questions.yaml            # Assessment questions configuration
├── scoring.yaml              # Risk scoring and styling configuration
├── requirements.txt          # Python dependencies
└── venv/                     # Virtual environment
```

## 🔧 Technical Components

### 1. Main Application (`app_refactored.py`)
- **Framework**: Flask web framework
- **Core Classes**:
  - `AIRiskAssessor`: Handles risk calculation and recommendation logic
  - `RiskAssessment`: Dataclass for structured assessment storage
- **Key Features**:
  - YAML configuration loading with UTF-8 encoding
  - Session-based report storage using unique session IDs
  - HTTP redirect flow for seamless user experience
  - Port configuration (default: 9000)

### 2. Template Generator (`template_generator.py`)
- **Purpose**: Dynamically generates HTML assessment forms from YAML configuration
- **Key Features**:
  - Responsive CSS design with professional styling
  - Interactive radio button selection with visual feedback
  - Green selection states with checkmark indicators
  - Form validation and loading animations
  - Compact, professional UI scaling

### 3. Report Generator (`report_generator.py`)
- **Purpose**: Creates comprehensive, visually appealing HTML reports
- **Key Features**:
  - Individual dimension risk color coding
  - Interactive risk gauge with accurate needle positioning
  - Executive summary generation
  - Responsive grid layouts
  - Print-friendly styling
  - Download functionality

### 4. Configuration Files

#### `questions.yaml`
```yaml
questions:
  autonomy:
    title: "🎯 Autonomy Level: How much decision-making power does the AI have?"
    help_text: "Consider who makes the final decisions in your workflow"
    required: true
    options:
      tool:
        title: "Tool"
        description: "AI provides recommendations only - humans always decide"
    reasoning_prompt: "Why did you choose this level? (Optional)"
```

#### `scoring.yaml`
```yaml
scoring:
  dimensions:
    autonomy:
      tool: 1
      assistant: 2
      agent: 3
      autonomous: 4
  risk_thresholds:
    - min_score: 5
      max_score: 8
      level: "low"
risk_styling:
  low:
    color: "#27ae60"
    bg: "#e6f3e6"
    border: "#27ae60"
    emoji: "LOW"
```

## 🎨 User Interface Features

### Form Interface
- **Professional Design**: Compact, modern styling with reduced padding/margins
- **Interactive Elements**: Radio buttons with green selection states and checkmarks
- **Visual Feedback**: Hover effects, transitions, and loading animations
- **Responsive Layout**: Works on desktop, tablet, and mobile devices

### Report Interface
- **Risk Overview**: Large, prominent risk level display with color coding
- **Risk Gauge**: Semi-circular gauge with accurate needle positioning
- **Dimension Cards**: Individual risk assessment for each dimension with color-coded scores
- **Recommendations**: Prioritized, actionable recommendations based on risk combinations
- **Executive Summary**: AI-generated summary of key risk factors

## 📊 Risk Assessment Logic

### Scoring Dimensions (1-4 scale each)
1. **Autonomy Level**: Decision-making power of AI (Tool → Assistant → Agent → Autonomous)
2. **Human Oversight**: Level of human supervision (Continuous → Checkpoint → Exception → Minimal)
3. **Output Impact**: Business impact of AI decisions (Informational → Operational → Strategic → External)
4. **Orchestration**: AI system complexity (Single → Sequential → Parallel → Hierarchical)
5. **Data Sensitivity**: Data classification level (Public → Internal → Confidential → Regulated)

### Risk Calculation
- **Total Score Range**: 5-20 (sum of all dimensions)
- **Risk Levels**: Low (5-8), Medium (9-13), High (14-17), Critical (18-20)
- **Individual Dimension Risk**: Each dimension scored independently for color coding

### Recommendation Engine
- **Base Recommendations**: Standard recommendations per risk level
- **Conditional Recommendations**: Dynamic recommendations based on specific dimension combinations
- **Priority Flagging**: High-priority recommendations for critical combinations

## 🛠️ Technical Implementation Details

### Dependencies
```txt
Flask==3.1.1
PyYAML==6.0.1
Jinja2==3.1.6
Werkzeug==3.1.3
```

### Key Technical Decisions
1. **YAML Configuration**: Externalized all questions and scoring to allow non-developer modifications
2. **UTF-8 Encoding**: Explicit encoding handling for cross-platform compatibility (Windows/macOS/Linux)
3. **Session-based Storage**: Temporary assessment storage using unique session IDs
4. **Redirect Flow**: POST → Redirect → GET pattern for better user experience
5. **Modular Architecture**: Separated concerns into distinct, reusable modules

### Cross-Platform Compatibility
- **Encoding**: All YAML files opened with explicit UTF-8 encoding
- **Virtual Environment**: Isolated Python environment for consistent dependencies
- **Path Handling**: Relative paths for portability across operating systems

## 🚀 Deployment & Usage

### Local Development Setup
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run application
python app_refactored.py
```

### Application Flow
1. **Assessment Form**: User completes multi-dimensional risk questionnaire
2. **Risk Calculation**: System calculates scores and determines risk level
3. **Report Generation**: Comprehensive HTML report created with visualizations
4. **Report Display**: User redirected to beautiful report page
5. **Download Option**: Optional PDF-style download available

## 🔄 Maintenance & Extensibility

### Adding New Questions
1. Edit `questions.yaml` to add new dimensions or options
2. Update `scoring.yaml` to include scoring for new options
3. No code changes required

### Modifying Risk Thresholds
1. Edit `risk_thresholds` in `scoring.yaml`
2. Adjust `min_score`, `max_score`, and `level` values
3. Update corresponding `risk_styling` if needed

### Customizing Recommendations
1. Modify `recommendations.by_risk_level` for base recommendations
2. Add new `conditional` rules for specific dimension combinations
3. Use logical operators for complex conditions

## 🎯 Future Enhancement Opportunities

- **Database Integration**: Replace session-based storage with persistent database
- **User Authentication**: Add user accounts and assessment history
- **API Endpoints**: RESTful API for integration with other systems
- **Advanced Analytics**: Trend analysis and comparative reporting
- **Export Formats**: PDF, Excel, and other export options
- **Multi-language Support**: Internationalization for global deployment

## 📝 Notes for Developers

- **Emoji Handling**: Remove emojis from YAML files for Windows compatibility
- **Port Configuration**: Default port 9000, easily configurable in `app_refactored.py`
- **Debug Mode**: Enabled by default for development, disable for production
- **File Structure**: Maintain modular structure for easy maintenance and testing 