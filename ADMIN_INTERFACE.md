# 🎯 AI Risk Assessment - Admin Interface

A clean, professional web-based admin interface for managing questions, scoring, and configuration without touching YAML files!

## 🚀 **Quick Access**

**From your main app:**
- Look for the "⚙️ Admin" link in the top-right corner of any assessment page
- Or go directly to: `http://localhost:9000/admin`

## 📋 **Admin Features**

### **Dashboard** (`/admin`)
- Overview of all questions by dimension
- Quick stats (total questions, dimensions)
- Quick access to all admin functions
- Visual dimension cards showing question counts

### **Question Management** (`/admin/questions`)
- **List All Questions**: View all questions across dimensions with edit/delete options
- **Add Questions**: Professional form-based question builder
- **Edit Questions**: Modify existing questions (coming soon)
- **Delete Questions**: Remove questions with confirmation

### **Question Builder** (`/admin/questions/add`)
- **Visual Form**: No more YAML editing!
- **Auto-completion**: Question ID auto-generated from title
- **Dynamic Options**: Add/remove answer options on the fly
- **Live Validation**: Prevents common mistakes
- **Weight Configuration**: Set question importance visually

## 🎨 **What Makes This Better**

### **Before** (CLI Tools) 😫
- Platform-specific scripts (.sh, .bat, .ps1)
- Terminal/command line friction
- No visual feedback
- Hard to share with team
- Can't see context while editing

### **Now** (Web Admin) 😊
- ✅ **Universal** - Works on any OS with browser
- ✅ **Visual** - See existing questions while adding new ones
- ✅ **Professional** - Clean, modern interface
- ✅ **Integrated** - Same app, same styling
- ✅ **User-friendly** - Forms with validation and help text
- ✅ **Team-friendly** - Easy to share access

## 🖥️ **Screenshots & Walkthrough**

### **Admin Dashboard**
Beautiful overview with:
- Total question counts
- Dimension cards showing questions
- Quick action buttons
- Modern gradient design

### **Question List**
Professional table showing:
- Question titles and metadata
- Answer option counts
- Question weights
- Edit/delete actions per question

### **Add Question Form**
Intuitive form with:
- Dimension selector
- Auto-generated question IDs
- Dynamic option management
- Weight sliders
- Live preview

## 🔧 **How to Use**

### **Adding a New Question**

1. **Go to Admin**: Click "⚙️ Admin" or visit `/admin`
2. **Click "Add Question"** from dashboard or questions list
3. **Fill the Form**:
   - Select dimension (autonomy, oversight, etc.)
   - Enter question title (ID auto-generated)
   - Add help text (optional)
   - Set required/optional
   - Add answer options with risk scores
   - Set question weight
4. **Submit**: Question automatically added to both YAML files!

### **Managing Existing Questions**

1. **Go to Questions List**: `/admin/questions`
2. **Browse by Dimension**: Each dimension shows its questions
3. **Edit/Delete**: Use action buttons on each question
4. **Quick Stats**: See question counts and weights

### **Validating Configuration**

1. **Dashboard**: Shows overview of system health
2. **Validation** (coming soon): Real-time config validation
3. **Error Reporting**: Clear messages for any issues

## 🛠️ **Technical Details**

### **Integration**
- **Flask Blueprint**: Cleanly integrated with main app
- **Same Session**: Uses existing Flask session management
- **Consistent Styling**: Matches your app's design language
- **No Database**: Still uses your existing YAML files

### **File Updates**
When you add/edit questions, the admin interface automatically updates:
- `questions/{dimension}.yaml` - Question definitions
- `scoring_flexible.yaml` - Scoring configurations

### **Security**
- Same security model as your main app
- No authentication yet (add if needed)
- Input validation and sanitization
- Safe YAML file handling

## 🚧 **Coming Soon**

### **Edit Questions**
- Modify existing questions in-place
- Update scoring and weights
- Bulk editing capabilities

### **Scoring Editor**
- Visual scoring configuration
- Drag-and-drop question weights
- Risk threshold adjustments

### **Validation Dashboard**
- Real-time configuration validation
- Visual error reporting
- Suggestions for improvements

### **Advanced Features**
- Question templates and presets
- Bulk import/export
- Change history tracking
- User access controls

## 🎯 **Best Practices**

### **Question Design**
- **Clear Titles**: Users should immediately understand the question
- **Helpful Descriptions**: Each option should explain what it means
- **Logical Ordering**: Order options from low to high risk
- **Consistent Scoring**: Use 1-4 scale consistently

### **Weighting**
- **1.0**: Core questions (primary risk indicators)
- **0.8**: Important supporting questions
- **0.5-0.6**: Contextual details
- **0.3**: Optional information

## 💡 **Tips**

1. **Use the Admin Link**: Always visible in the top-right of assessment pages
2. **Preview Questions**: The list view shows how questions will appear
3. **Check Weights**: Higher weights = more important questions
4. **Test Changes**: Run an assessment after adding questions
5. **Backup**: Your YAML files are automatically updated but consider backups

## 🔧 **Troubleshooting**

### **Admin Link Not Visible**
- Make sure you've restarted your Flask app after adding the admin interface
- Check that the admin blueprint is registered

### **Questions Not Saving**
- Check file permissions on `questions/` directory and `scoring_flexible.yaml`
- Look for error messages in the admin interface
- Ensure YAML syntax is valid

### **Can't Access Admin**
- Go directly to `/admin` URL
- Check that Flask app is running
- Look for any Python import errors

---

**Enjoy your new professional admin interface!** 🎉

No more command-line tools, no more manual YAML editing - just clean, visual question management through your web browser.
