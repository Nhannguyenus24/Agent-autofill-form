# 🤖 Google Form Autofill with Gemini AI

Automatically fill Google Forms using Selenium and Gemini AI to generate smart answers.

## 📋 Requirements

- Python 3.7+
- Chrome Browser
- ChromeDriver
- Gemini API Key

## 🔧 Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Download ChromeDriver:**
   - Download from: https://chromedriver.chromium.org/
   - Place in project folder or system path

3. **Get Gemini API Key:**
   - Visit: https://makersuite.google.com/app/apikey
   - Create a new API key
   - Copy the API key

## ⚙️ Configuration

### 1. File `config.json`

```json
{
  "gemini_api_key": "YOUR_GEMINI_API_KEY_HERE",
  "chromedriver_path": "path/to/chromedriver.exe",
  "wait_time": 2
}
```

Replace:
- `YOUR_GEMINI_API_KEY_HERE` with your API key
- `path/to/chromedriver.exe` with the path to ChromeDriver

### 2. File `questions.json`

```json
{
  "form_url": "https://docs.google.com/forms/d/e/YOUR_FORM_ID/viewform",
  "questions": [
    {
      "type": "text",
      "xpath": "//input[@type='text' and @aria-labelledby='i1']",
      "prompt": "Generate a random Vietnamese name"
    }
  ]
}
```

**Supported question types:**

- `text`: Simple text field
- `textarea`: Text area (long answer)
- `radio`: Radio button (single choice)
- `checkbox`: Checkbox (multiple choice)

**How to get XPath:**

1. Open Google Form in Chrome
2. Press F12 to open DevTools
3. Click "Select element" icon
4. Click on the field to get XPath
5. Right-click element in DevTools → Copy → Copy XPath

## 🚀 Running the Program

```bash
python main.py
```

## 📝 Usage Examples

### Example 1: Course registration form

```json
{
  "form_url": "https://docs.google.com/forms/d/e/1FAIpQLSc.../viewform",
  "questions": [
    {
      "type": "text",
      "xpath": "//input[@aria-label='Name']",
      "prompt": "Generate a Vietnamese name"
    },
    {
      "type": "text",
      "xpath": "//input[@type='email']",
      "prompt": "Generate a random email"
    },
    {
      "type": "textarea",
      "xpath": "//textarea[@aria-label='Why are you joining']",
      "prompt": "Write 2-3 sentences about wanting to learn Python programming"
    },
    {
      "type": "radio",
      "xpath": "//div[@data-value='18-25 years old']",
      "prompt": null,
      "action": "click"
    }
  ]
}
```

## 🎯 Features

✅ Auto-fill text fields with AI  
✅ Auto-fill textarea with long answers  
✅ Auto-click radio buttons  
✅ Auto-click checkboxes  
✅ Auto-submit form  
✅ Smart error handling  

## ⚠️ Notes

- Use only for lawful purposes with proper authorization
- Do not spam or abuse Google Forms
- Verify XPath before running
- Gemini API has rate limits

## 🐛 Troubleshooting

**Error: ChromeDriver version mismatch**
```
Download the correct ChromeDriver version matching your Chrome browser version
```

**Error: Element not found**
```
Verify the XPath in questions.json is correct
```

**Error: Gemini API key invalid**
```
Verify your API key in config.json
```

## 📄 Project Structure

```
Autofill-googleform/
├── main.py              # Main file
├── config.json          # API and ChromeDriver config
├── questions.json       # Form questions definition
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── python.py           # Old demo (can be deleted)
```

## 🤝 Contributing

All contributions are welcome! Please create Pull Requests or Issues.

## 📧 Contact

If you have questions, please create an Issue on GitHub.
