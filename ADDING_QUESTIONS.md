# Adding Questions and Updating Scoring

This guide explains how to add new questions to the AI Risk Assessment tool and configure their scoring.

## Overview

The assessment tool uses a flexible scoring system that supports:
- Multiple questions per dimension (autonomy, oversight, impact, etc.)
- Weighted scoring for different question importance
- Various aggregation strategies (weighted average, sum, max, etc.)
- Automatic score calculation and risk level determination

## File Structure

The system uses separate YAML files for different configurations:

```
questions/
├── autonomy.yaml          # Autonomy dimension questions
├── oversight.yaml         # Oversight dimension questions
├── impact.yaml           # Impact dimension questions
├── orchestration.yaml    # Orchestration dimension questions
└── data_sensitivity.yaml # Data sensitivity dimension questions

scoring_flexible.yaml      # Flexible scoring configuration
recommendations.yaml      # Risk recommendations
```

## Adding a New Question

### Step 1: Add Question to Dimension File

Edit the appropriate dimension file in the `questions/` directory.

**Example: Adding a new autonomy question**

Edit `questions/autonomy.yaml`:

```yaml
autonomy_questions:
  # Existing questions...
  
  autonomy_scope:  # New question ID
    title: "Decision Scope: What range of decisions can the AI make?"
    help_text: "Consider the breadth of decisions the AI is authorized to make"
    required: true
    options:
      limited:
        title: "Limited Scope"
        description: "AI can only make very specific, predefined decisions"
      moderate:
        title: "Moderate Scope"
        description: "AI can make decisions within well-defined domains"
      broad:
        title: "Broad Scope"
        description: "AI can make decisions across multiple business areas"
      unlimited:
        title: "Unlimited Scope"
        description: "AI has no restrictions on decision-making domains"
    reasoning_prompt: "What factors determine the AI's decision scope? (Optional)"
```

### Step 2: Configure Scoring

Edit `scoring_flexible.yaml` to add scoring for the new question.

```yaml
dimensions:
  autonomy:
    aggregation: "weighted_average"
    questions:
      # Existing questions...
      
      autonomy_scope:  # Must match question ID from Step 1
        weight: 0.8    # Relative importance (0.1 to 2.0+)
        scoring:
          limited: 1
          moderate: 2
          broad: 3
          unlimited: 4
```

### Step 3: Test the Changes

The system automatically picks up new questions. Test by:

1. Running the application
2. Completing an assessment with the new question
3. Verifying the score calculation includes the new question

## Question Configuration Reference

### Question Structure

```yaml
question_id:
  title: "Question title displayed to users"
  help_text: "Additional context or instructions"
  required: true                    # Whether question is mandatory
  options:
    option_key:                     # Used in scoring configuration
      title: "Option Label"         # Displayed to users
      description: "Detailed explanation"
  reasoning_prompt: "Optional prompt for user reasoning"
```

### Scoring Structure

```yaml
dimensions:
  dimension_name:
    aggregation: "weighted_average"  # How to combine multiple questions
    questions:
      question_id:
        weight: 1.0                 # Question importance multiplier
        scoring:
          option_key: score_value   # Numeric score for each option
```

## Aggregation Strategies

Configure how multiple questions in a dimension are combined:

- **weighted_average**: Multiply each score by its weight, then average (recommended)
- **average**: Simple average of all question scores
- **sum**: Add all question scores together
- **max**: Use the highest score among questions
- **min**: Use the lowest score among questions

## Weight Guidelines

Use these weight ranges for different question types:

- **Core questions**: 1.0 (primary risk indicators)
- **Important supporting**: 0.8 (significant but secondary)
- **Contextual details**: 0.5-0.6 (provides nuance)
- **Optional information**: 0.3 (nice to have)

## Examples

### Adding Multiple Questions to One Dimension

```yaml
# questions/oversight.yaml
oversight_questions:
  oversight:
    title: "Primary Oversight Level"
    # ... existing configuration
  
  oversight_frequency:
    title: "Monitoring Frequency"
    options:
      continuous: { title: "Continuous", description: "Real-time monitoring" }
      hourly: { title: "Hourly", description: "Checked every hour" }
      daily: { title: "Daily", description: "Reviewed once per day" }
      weekly: { title: "Weekly", description: "Weekly oversight" }
  
  oversight_escalation:
    title: "Escalation Procedures"
    options:
      automatic: { title: "Automatic", description: "Issues auto-escalate" }
      manual: { title: "Manual", description: "Manual escalation required" }
      none: { title: "None", description: "No escalation process" }
```

```yaml
# scoring_flexible.yaml
dimensions:
  oversight:
    aggregation: "weighted_average"
    questions:
      oversight:
        weight: 1.0
        scoring: { continuous: 1, checkpoint: 2, exception: 3, minimal: 4 }
      
      oversight_frequency:
        weight: 0.7
        scoring: { continuous: 1, hourly: 2, daily: 3, weekly: 4 }
      
      oversight_escalation:
        weight: 0.5
        scoring: { automatic: 1, manual: 2, none: 4 }
```

### Adding a New Dimension

If you need an entirely new risk dimension:

1. Create new question file: `questions/new_dimension.yaml`
2. Add dimension configuration to `scoring_flexible.yaml`
3. Update the application code to recognize the new dimension

## Best Practices

### Question Design

- Use clear, specific titles
- Provide helpful descriptions for each option
- Order options from lowest to highest risk
- Keep option names short but descriptive

### Scoring Guidelines

- Use 1-4 scale for consistency with existing questions
- Ensure higher scores represent higher risk
- Consider the relative impact when setting weights
- Test score calculations with various combinations

### Validation

After adding questions:

1. Test all possible answer combinations
2. Verify risk level calculations are appropriate
3. Check that weighted averages make sense
4. Ensure the multi-step wizard displays correctly

## Common Patterns

### Binary Questions (Yes/No)

```yaml
has_human_review:
  title: "Is there human review of AI decisions?"
  options:
    yes: { title: "Yes", description: "Humans review AI decisions" }
    no: { title: "No", description: "No human review process" }

# Scoring
scoring: { yes: 1, no: 4 }
```

### Frequency-Based Questions

```yaml
update_frequency:
  title: "How often is the AI model updated?"
  options:
    daily: { title: "Daily", description: "Updated every day" }
    weekly: { title: "Weekly", description: "Updated weekly" }
    monthly: { title: "Monthly", description: "Updated monthly" }
    yearly: { title: "Yearly", description: "Updated annually" }

# Scoring (more frequent = lower risk)
scoring: { daily: 1, weekly: 2, monthly: 3, yearly: 4 }
```

### Scale Questions

```yaml
data_volume:
  title: "What volume of data does the AI process?"
  options:
    small: { title: "Small", description: "< 1GB per day" }
    medium: { title: "Medium", description: "1-100GB per day" }
    large: { title: "Large", description: "100GB-1TB per day" }
    massive: { title: "Massive", description: "> 1TB per day" }

# Scoring (more data = higher risk)
scoring: { small: 1, medium: 2, large: 3, massive: 4 }
```

## Troubleshooting

### Question Not Appearing
- Check YAML syntax is valid
- Ensure question ID is unique within the dimension
- Verify the dimension file is in the `questions/` directory

### Scoring Not Working
- Confirm question ID in scoring matches question file exactly
- Check that all option keys have corresponding scores
- Verify aggregation strategy is valid

### Unexpected Risk Levels
- Review weight assignments
- Check score ranges (typically 1-4)
- Test with known combinations to validate calculations

## Migration from Legacy System

If migrating from the original single-question system:

1. Current questions work without changes
2. Add new questions using the patterns above
3. Existing assessments remain valid
4. Gradually transition to more detailed questions as needed 