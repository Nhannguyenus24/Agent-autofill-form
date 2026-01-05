# 🤖 Smart Google Form Autofill V2

Auto-fill Google Forms with AI-generated answers using Gemini API.

## ✨ Features

- **Auto-Detection**: Automatically detects all form fields (text, email, textarea, radio, checkbox, matrix)
- **AI-Powered**: Uses Gemini AI to generate contextually appropriate answers
- **No Configuration**: No need to manually define questions - analyzes form structure dynamically
- **Multi-Section Support**: Handles multi-page forms automatically

## 📋 Requirements

- Python 3.7+
- Chrome Browser
- Gemini API Key

## 🔧 Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Get ChromeDriver
- Download from: https://chromedriver.chromium.org/
- Extract and note the path

### 3. Get Gemini API Key
- Visit: https://makersuite.google.com/app/apikey
- Create a new API key
- Copy it

### 4. Configure

Edit `config.json`:
```json
{
  "gemini_api_key": "YOUR_GEMINI_API_KEY_HERE",
  "chromedriver_path": "path/to/chromedriver",
  "wait_time": 2
}
```

## 🚀 Usage

```bash
python main.py
```

Then enter the Google Form URL when prompted.

## 📝 How It Works

1. Opens the Google Form
2. Analyzes the form structure to detect all questions and their types
3. For each question, asks Gemini AI for the most appropriate answer
4. Fills the form with AI-generated answers
5. Clicks Next to go to next section (if multi-page)
6. Submits the form when complete

## 🎯 Supported Question Types

- ✅ Text Input
- ✅ Email Input
- ✅ Textarea
- ✅ Radio Buttons (single choice)
- ✅ Checkboxes (multiple choice)
- ✅ Rating Scale
- ✅ Matrix/Grid Questions

## ⚙️ Configuration

| Parameter | Description |
|-----------|-------------|
| `gemini_api_key` | Your Gemini API key |
| `chromedriver_path` | Path to ChromeDriver executable |
| `wait_time` | Wait time before starting form (seconds) |

## 🐛 Troubleshooting

**ChromeDriver version mismatch**
- Ensure ChromeDriver version matches your Chrome browser version

**Gemini API errors**
- Verify your API key is correct and has quota available

**Form not detected**
- Some forms may have non-standard HTML - check if form opens correctly in browser

## 📄 Files

- `main.py` - Main application
- `config.json` - Configuration file
- `requirements.txt` - Python dependencies
- `README.md` - This file

## ⚠️ Disclaimer

Use responsibly and only with permission. Respect form creators' intentions and Google Forms terms of service.

## 📧 Support

For issues or questions, create an issue or reach out.
