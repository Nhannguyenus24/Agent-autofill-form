# 🤖 Google Form Autofill với Gemini AI

Chương trình tự động điền Google Form sử dụng Selenium và Gemini AI để tạo câu trả lời thông minh.

## 📋 Yêu cầu

- Python 3.7+
- Chrome Browser
- ChromeDriver
- Gemini API Key

## 🔧 Cài đặt

1. **Cài đặt thư viện:**
```bash
pip install -r requirements.txt
```

2. **Tải ChromeDriver:**
   - Tải từ: https://chromedriver.chromium.org/
   - Đặt vào thư mục dự án hoặc đường dẫn hệ thống

3. **Lấy Gemini API Key:**
   - Truy cập: https://makersuite.google.com/app/apikey
   - Tạo API key mới
   - Copy API key

## ⚙️ Cấu hình

### 1. File `config.json`

```json
{
  "gemini_api_key": "YOUR_GEMINI_API_KEY_HERE",
  "chromedriver_path": "path/to/chromedriver.exe",
  "wait_time": 2
}
```

Thay thế:
- `YOUR_GEMINI_API_KEY_HERE` bằng API key của bạn
- `path/to/chromedriver.exe` bằng đường dẫn đến ChromeDriver

### 2. File `questions.json`

```json
{
  "form_url": "https://docs.google.com/forms/d/e/YOUR_FORM_ID/viewform",
  "questions": [
    {
      "type": "text",
      "xpath": "//input[@type='text' and @aria-labelledby='i1']",
      "prompt": "Tạo một tên người Việt Nam ngẫu nhiên"
    }
  ]
}
```

**Các loại câu hỏi hỗ trợ:**

- `text`: Text field đơn giản
- `textarea`: Text area (câu trả lời dài)
- `radio`: Radio button (chọn 1)
- `checkbox`: Checkbox (chọn nhiều)

**Cách lấy XPath:**

1. Mở Google Form trong Chrome
2. Nhấn F12 để mở DevTools
3. Click vào icon "Select element"
4. Click vào trường cần lấy XPath
5. Right-click vào element trong DevTools → Copy → Copy XPath

## 🚀 Chạy chương trình

```bash
python main.py
```

## 📝 Ví dụ sử dụng

### Ví dụ 1: Form đăng ký khóa học

```json
{
  "form_url": "https://docs.google.com/forms/d/e/1FAIpQLSc.../viewform",
  "questions": [
    {
      "type": "text",
      "xpath": "//input[@aria-label='Họ và tên']",
      "prompt": "Tạo một tên người Việt Nam"
    },
    {
      "type": "text",
      "xpath": "//input[@type='email']",
      "prompt": "Tạo một email ngẫu nhiên"
    },
    {
      "type": "textarea",
      "xpath": "//textarea[@aria-label='Lý do tham gia']",
      "prompt": "Viết 2-3 câu về lý do muốn học lập trình Python"
    },
    {
      "type": "radio",
      "xpath": "//div[@data-value='18-25 tuổi']",
      "prompt": null,
      "action": "click"
    }
  ]
}
```

## 🎯 Tính năng

✅ Tự động điền text field với AI  
✅ Tự động điền textarea với câu trả lời dài  
✅ Tự động click radio button  
✅ Tự động click checkbox  
✅ Tự động submit form  
✅ Xử lý lỗi thông minh  

## ⚠️ Lưu ý

- Chỉ sử dụng cho mục đích hợp pháp và có sự đồng ý
- Không spam hoặc lạm dụng Google Forms
- Kiểm tra XPath trước khi chạy
- API Gemini có giới hạn requests

## 🐛 Xử lý lỗi thường gặp

**Lỗi: ChromeDriver version không khớp**
```
Tải đúng phiên bản ChromeDriver với Chrome browser của bạn
```

**Lỗi: Không tìm thấy element**
```
Kiểm tra lại XPath trong file questions.json
```

**Lỗi: Gemini API key không hợp lệ**
```
Kiểm tra lại API key trong config.json
```

## 📄 Cấu trúc dự án

```
Autofill-googleform/
├── main.py              # File chính
├── config.json          # Cấu hình API và ChromeDriver
├── questions.json       # Định nghĩa câu hỏi form
├── requirements.txt     # Thư viện Python
├── README.md           # File này
└── python.py           # Demo cũ (có thể xóa)
```

## 🤝 Đóng góp

Mọi đóng góp đều được chào đón! Hãy tạo Pull Request hoặc Issue.

## 📧 Liên hệ

Nếu có câu hỏi, vui lòng tạo Issue trên GitHub.
