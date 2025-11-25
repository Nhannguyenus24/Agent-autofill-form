# Google Form Autofill - Version Comparison

## 📦 Version 1 (Manual Configuration)

### Location
All V1 files backed up in `v1/` folder

### How it works
1. Manually configure `questions.json` with XPath for each question
2. Manually write prompts for Gemini
3. Run script to fill form

### Pros
- ✅ Full control over each answer
- ✅ Can customize prompts for specific questions
- ✅ Reliable if XPath is correct

### Cons
- ❌ Requires manual XPath extraction
- ❌ Time-consuming setup
- ❌ Breaks if form structure changes
- ❌ Need separate config for each form

### Usage
```bash
cd v1
python main.py
```

---

## 🚀 Version 2 (Smart AI-Powered)

### Location
`main_v2.py` in root folder

### How it works
1. **Auto-detects** all questions on form
2. **Auto-identifies** question types (text, radio, checkbox, scale, etc.)
3. **Asks Gemini AI** to choose best answers
4. **Auto-navigates** through multiple sections
5. **Auto-submits** when done

### Pros
- ✅ Zero manual configuration needed
- ✅ Works with any Google Form
- ✅ AI makes intelligent choices
- ✅ Adapts to form structure changes
- ✅ Just provide URL and run

### Cons
- ⚠️ Less control over specific answers
- ⚠️ AI choices may not always be perfect
- ⚠️ More API calls to Gemini (more cost)

### Usage
```bash
python main_v2.py
```
Then enter form URL when prompted.

---

## 🎯 When to Use Which Version?

### Use V1 if:
- You need precise control over answers
- You're filling the same form repeatedly
- You want consistent answers every time
- You have time to configure XPath

### Use V2 if:
- You need to fill many different forms
- You want quick setup (no configuration)
- You trust AI to make good choices
- Form structure might change

---

## 🔄 Key Differences

| Feature | V1 | V2 |
|---------|----|----|
| Configuration | Manual JSON | None needed |
| XPath Setup | Required | Auto-detected |
| Question Detection | Manual | Automatic |
| Answer Generation | Prompted | AI-decided |
| Multi-form Support | One config per form | Universal |
| Setup Time | 10-30 min | 0 min |
| Flexibility | High | Very High |
| Consistency | 100% | ~90% |

---

## 🛠️ Technical Details

### V2 Smart Detection

**Question Types Detected:**
- Text input (`input[type='text']`)
- Email input (`input[type='email']`)
- Text area (`textarea`)
- Radio buttons (`div[role='radio']`)
- Checkboxes (`div[role='checkbox']`)
- Scale ratings (1-5)
- Matrix questions (multiple rows)

**AI Decision Making:**
- For text: Generates appropriate content
- For radio: Chooses best single option
- For checkbox: Selects relevant options
- For scale: Picks reasonable rating (tends 4-5)
- For matrix: Rates each row intelligently

### V2 Workflow

```
1. Open form URL
   ↓
2. Analyze page → Extract all questions
   ↓
3. For each question:
   - Detect type
   - Ask Gemini for answer
   - Fill form element
   ↓
4. Click "Next" or "Submit"
   ↓
5. Repeat from step 2 until done
```

---

## 💡 Examples

### V1 Example
```json
{
  "form_url": "...",
  "sections": [[
    {
      "type": "radio",
      "xpath": "//div[@data-value='Option 1']",
      "prompt": null
    }
  ]]
}
```

### V2 Example
```bash
$ python main_v2.py
Enter Google Form URL: https://forms.gle/xxxxx

🔍 Analyzing form structure...
✓ Found 10 questions

📝 Q1: What is your name?
   Type: text
   🤖 Gemini suggests: Nguyễn Văn An
   ✓ Filled: Nguyễn Văn An

📝 Q2: Choose your university
   Type: radio
   🤖 Gemini suggests: 1
   ✓ Selected: Trường ĐH thuộc ĐHQG

...
```

---

## 🚀 Recommendation

**Start with V2** for quick testing and most use cases.

**Switch to V1** if you need:
- Specific answers for important forms
- Repeated submissions with same data
- Fine-tuned control
