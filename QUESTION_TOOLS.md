# Question Management Tools

These tools make it super easy to add new questions to your AI Risk Assessment system without manually editing YAML files!

## Quick Start

### Linux/macOS
```bash
# Activate your virtual environment first
source venv/bin/activate

# Add a new question interactively
python question_manager.py add

# List all current questions
python question_manager.py list

# Validate question configuration
python question_manager.py validate
```

### Windows
**Option 1: Double-click batch files**
- `add-question.bat` - Add new questions
- `list-questions.bat` - List all questions  
- `validate-questions.bat` - Validate configuration

**Option 2: Command Prompt**
```cmd
# Activate virtual environment
venv\Scripts\activate.bat

# Add a new question interactively
python question_manager.py add

# List all current questions
python question_manager.py list

# Validate question configuration
python question_manager.py validate
```

**Option 3: PowerShell**
```powershell
# Run PowerShell script
.\add-question.ps1

# Or manually activate and run
venv\Scripts\Activate.ps1
python question_manager.py add
```

## Adding a New Question (Interactive)

Run the interactive question builder:

```bash
python question_manager.py add
```

The tool will guide you through:

1. **Select dimension** (autonomy, oversight, impact, orchestration, data_sensitivity)
2. **Question details** (ID, title, help text, required/optional)
3. **Answer options** (key, title, description, risk score 1-4)
4. **Weighting** (how important this question is, 0.1-3.0)

### Example Session

```
🎯 AI Risk Assessment - Question Builder

Select dimension:
1. autonomy
2. oversight
3. impact
4. orchestration
5. data_sensitivity
> 1

Question ID (e.g., 'decision_speed', 'review_frequency'): decision_timeline
Question title (displayed to users): How quickly must the AI make decisions?
Help text (optional, provides additional context): Consider time pressure and urgency requirements

Is this question required?
1. Yes
2. No
> 1

🎯 Question Options
Add the answer options for this question...

Option 1:
Option key (e.g., 'low', 'medium', 'high'): immediate
Option title (displayed to users): Immediate (< 1 second)
Option description (detailed explanation): Real-time decisions with no delay
Risk score (1=lowest risk, 4=highest risk): 4

Option 2:
Option key: minutes
Option title: Within Minutes
Option description: Decisions made within a few minutes
Risk score: 2

Add another option?
1. Yes
2. No
> 2

Reasoning prompt (optional): Why is this timeline appropriate for your use case?

🎯 Question Scoring
Question weight [1.0]: 0.8

✅ Question added successfully!
```

## What Gets Updated Automatically

When you add a question, the tool updates:

- ✅ `questions/{dimension}.yaml` - Adds the question structure
- ✅ `scoring_flexible.yaml` - Adds scoring configuration
- ✅ Validates everything works together

## Question Management Commands

### List Questions
```bash
python question_manager.py list
```
Shows all questions across all dimensions with counts and details.

### Validate Configuration
```bash
python question_manager.py validate
```
Checks for common issues:
- Missing question files
- Questions without scoring
- Options without scores
- Required fields missing

## Manual Tools (Advanced)

If you prefer the direct approach, you can also use:

```bash
# Direct interactive question builder
python add_question.py
```

## Best Practices

### Question Design
- **Clear titles** - Users should immediately understand what you're asking
- **Helpful descriptions** - Each option should explain what it means
- **Logical ordering** - Order options from lowest to highest risk
- **Consistent scoring** - Use 1-4 scale (1=low risk, 4=high risk)

### Weighting Guidelines
- **1.0** - Core questions (primary risk indicators)
- **0.8** - Important supporting questions
- **0.5-0.6** - Contextual details that provide nuance
- **0.3** - Optional information, nice to have

### Question IDs
- Use lowercase with underscores: `decision_speed`
- Be descriptive but concise: `review_frequency` not `freq`
- Avoid special characters except underscore and hyphen

## Examples

### Binary Question (Yes/No)
```
Question: Does the AI have access to external APIs?
Options:
- yes: "Yes" (score: 3)
- no: "No" (score: 1)
```

### Scale Question
```
Question: How much data does the AI process daily?
Options:
- small: "< 1GB" (score: 1)
- medium: "1-100GB" (score: 2) 
- large: "100GB-1TB" (score: 3)
- massive: "> 1TB" (score: 4)
```

### Frequency Question
```
Question: How often is the AI model retrained?
Options:
- continuous: "Continuously" (score: 1)
- weekly: "Weekly" (score: 2)
- monthly: "Monthly" (score: 3)
- yearly: "Yearly or less" (score: 4)
```

## Troubleshooting

### "Question ID already exists"
- Choose a different, unique ID for your question
- Check existing questions with: `python question_manager.py list`

### "Module not found" errors
**Linux/macOS:**
- Make sure you've activated the virtual environment: `source venv/bin/activate`

**Windows:**
- Make sure you've activated the virtual environment: `venv\Scripts\activate.bat`
- Or use the provided batch files which handle activation automatically

### PowerShell execution policy errors (Windows)
If you get "execution of scripts is disabled" error:
```powershell
# Run this once as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then you can run the script
.\add-question.ps1
```

### Virtual environment not found
**Linux/macOS:**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Windows:**
```cmd
# Create virtual environment  
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

### Questions not appearing in assessment
- Run validation: `python question_manager.py validate`
- Check that both question and scoring files were updated
- Restart your Flask application to pick up changes

## What's Different from Before?

**Before:** 😫
1. Manually edit `questions/autonomy.yaml`
2. Manually edit `scoring_flexible.yaml`
3. Ensure IDs match exactly between files
4. Hope you didn't make syntax errors
5. Test manually

**Now:** 😊
1. Run `python question_manager.py add`
2. Answer the prompts
3. Everything is updated automatically!

The tools handle all the YAML formatting, validation, and cross-file coordination for you.
