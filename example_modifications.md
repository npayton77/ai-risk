# 🎯 AI Risk Assessment - Configuration Examples

## 🚀 What We Just Did

I just showed you how to add a **new question dimension** (`data_sensitivity`) by:
1. Adding it to `questions.yaml` 
2. Adding scoring to `scoring.yaml`
3. The app automatically picked it up!

---

## 📝 **Common Modifications**

### 1. **Change Question Text**
```yaml
# In questions.yaml
autonomy:
  title: "🎯 NEW: How much independence does your AI have?"  # ← Changed this
  help_text: "Think about decision-making authority"        # ← And this
```

### 2. **Add New Answer Options**
```yaml
# In questions.yaml
autonomy:
  options:
    tool: { title: "Tool", description: "..." }
    assistant: { title: "Assistant", description: "..." }
    agent: { title: "Agent", description: "..." }
    autonomous: { title: "Autonomous", description: "..." }
    # 👇 Add new option
    superintelligent:
      title: "Superintelligent"
      description: "AI exceeds human capabilities in all domains"
```

```yaml
# In scoring.yaml - add corresponding score
autonomy:
  tool: 1
  assistant: 2
  agent: 3
  autonomous: 4
  superintelligent: 5  # 👈 New scoring
```

### 3. **Adjust Risk Thresholds**
```yaml
# In scoring.yaml
risk_thresholds:
  - min_score: 5
    max_score: 10      # 👈 Make "low" range bigger
    level: "low"
  - min_score: 11
    max_score: 15
    level: "medium"    # 👈 Compress other ranges
```

### 4. **Add Industry-Specific Recommendations**
```yaml
# In scoring.yaml
conditional:
  - condition:
      impact: ["external"]
      data_sensitivity: ["regulated"]
    recommendation: "🏥 HEALTHCARE: Requires HIPAA compliance review"
  
  - condition:
      orchestration: ["hierarchical"]
      autonomy: ["autonomous"]
    recommendation: "🤖 AI-MANAGING-AI: Implement recursive monitoring systems"
```

### 5. **Change Risk Level Colors**
```yaml
# In scoring.yaml
risk_styling:
  low:
    color: "#2ecc71"     # 👈 Different green
    emoji: "✅"          # 👈 Different emoji
  critical:
    color: "#8b0000"     # 👈 Dark red instead of purple
    emoji: "☠️"         # 👈 Skull emoji!
```

---

## 🎨 **Complete New Question Example**

Let's say you want to add "**Deployment Environment**":

### Step 1: Add to `questions.yaml`
```yaml
deployment_environment:
  title: "🌐 Deployment: Where will this AI system run?"
  help_text: "Consider the technical environment and access controls"
  required: true
  options:
    local:
      title: "Local/On-Premise"
      description: "Runs on company-controlled infrastructure"
    private_cloud:
      title: "Private Cloud"
      description: "Dedicated cloud environment (AWS VPC, etc.)"
    public_cloud:
      title: "Public Cloud"
      description: "Shared cloud infrastructure with standard security"
    edge:
      title: "Edge/Mobile"
      description: "Runs on user devices or edge computing nodes"
  reasoning_prompt: "What security controls exist in this environment?"
```

### Step 2: Add scoring to `scoring.yaml`
```yaml
deployment_environment:
  local: 1           # Most secure
  private_cloud: 2   # Pretty secure
  public_cloud: 3    # Less secure
  edge: 4           # Least secure
```

### Step 3: Add specific recommendations
```yaml
conditional:
  - condition:
      deployment_environment: ["edge"]
      data_sensitivity: ["confidential", "regulated"]
    recommendation: "🚨 EDGE DEPLOYMENT RISK: Sensitive data on user devices requires encryption and remote wipe capabilities"
```

**That's it!** Restart the app and the new question appears automatically.

---

## 🔧 **Pro Tips**

### **Make Temporary Changes**
```bash
# Save backup first
cp scoring.yaml scoring.yaml.backup

# Make your changes
# Test them out
# Restore if needed
cp scoring.yaml.backup scoring.yaml
```

### **Quick Test Different Scoring**
```yaml
# Try making autonomy matter more
autonomy:
  tool: 1
  assistant: 3      # 👈 Jump from 2 to 3
  agent: 6          # 👈 Jump from 3 to 6  
  autonomous: 10    # 👈 Jump from 4 to 10
```

### **Industry-Specific Versions**
- `questions_healthcare.yaml`
- `questions_finance.yaml` 
- `scoring_conservative.yaml`
- `scoring_startup.yaml`

Just change the filename in `app_refactored.py`!

---

## 🎯 **The Power**: No Code Changes Needed!

✅ **Before**: Edit Python → Test → Debug → Deploy  
✅ **After**: Edit YAML → Restart app → Done!

**Business users can now manage the assessment without developers!** 🚀 