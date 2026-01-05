"""
Smart Google Form Autofill with Gemini AI - Version 2
Auto-detects form structure and fills with AI-generated answers
"""

import json
import time
import google.generativeai as genai
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class SmartGoogleFormAutofill:
    """Smart form autofill using Gemini AI"""
    
    def __init__(self, config_file='config.json'):
        """Initialize with config file"""
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        genai.configure(api_key=self.config['gemini_api_key'])
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        from selenium.webdriver.chrome.service import Service
        service = Service(executable_path=self.config['chromedriver_path'])
        self.driver = webdriver.Chrome(service=service)
        self.wait = WebDriverWait(self.driver, 10)
        self.form_structure = []
        self.answer_history = []  # Store Q&A pairs for context
    
    def extract_form_structure(self):
        """Extract all questions and options from form"""
        print("\n🔍 Analyzing form structure...")
        
        try:
            questions = self.driver.find_elements(By.CSS_SELECTOR, "div[role='listitem']")
            form_data = []
            
            for idx, question_elem in enumerate(questions, 1):
                try:
                    try:
                        question_text = question_elem.find_element(By.CSS_SELECTOR, ".M7eMe").text
                    except Exception as e:
                        print(f"⚠ Q{idx}: Cannot find question - {type(e).__name__}")
                        continue
                    
                    if not question_text:
                        continue
                    
                    question_info = {
                        "index": idx,
                        "question": question_text,
                        "type": None,
                        "options": [],
                        "element": question_elem
                    }
                    
                    # Detect matrix/grid questions (multiple radiogroups)
                    radiogroups = question_elem.find_elements(By.CSS_SELECTOR, "div[role='radiogroup']")
                    if len(radiogroups) > 1:
                        question_info["type"] = "matrix"
                        question_info["rows"] = []
                        
                        for row in radiogroups:
                            try:
                                row_label = row.get_attribute("aria-label")
                                row_options = row.find_elements(By.CSS_SELECTOR, "div[role='radio']")
                                
                                if row_label and row_options:
                                    question_info["rows"].append({
                                        "label": row_label,
                                        "options": row_options
                                    })
                            except Exception as e:
                                print(f"   ⚠ Matrix row error: {str(e)[:50]}")
                        
                        if question_info["rows"]:
                            form_data.append(question_info)
                        continue
                    
                    # Detect radio buttons
                    radio_options = question_elem.find_elements(By.CSS_SELECTOR, "div[role='radio']")
                    if radio_options:
                        question_info["type"] = "radio"
                        for option in radio_options:
                            option_text = option.get_attribute("data-value")
                            if not option_text:
                                try:
                                    option_text = option.find_element(By.CSS_SELECTOR, ".aDTYNe").text
                                except:
                                    option_text = option.text
                            if option_text:
                                question_info["options"].append({
                                    "text": option_text,
                                    "element": option
                                })
                        form_data.append(question_info)
                        continue
                    
                    # Detect checkboxes
                    checkbox_options = question_elem.find_elements(By.CSS_SELECTOR, "div[role='checkbox']")
                    if checkbox_options:
                        question_info["type"] = "checkbox"
                        for option in checkbox_options:
                            option_text = option.get_attribute("aria-label")
                            if not option_text:
                                try:
                                    option_text = option.find_element(By.CSS_SELECTOR, ".aDTYNe").text
                                except:
                                    option_text = option.text
                            if option_text:
                                question_info["options"].append({
                                    "text": option_text,
                                    "element": option
                                })
                        form_data.append(question_info)
                        continue
                    
                    # Detect text input
                    text_inputs = question_elem.find_elements(By.CSS_SELECTOR, "input[type='text']")
                    if text_inputs:
                        question_info["type"] = "text"
                        form_data.append(question_info)
                        continue
                    
                    # Detect email input
                    email_inputs = question_elem.find_elements(By.CSS_SELECTOR, "input[type='email']")
                    if email_inputs:
                        question_info["type"] = "email"
                        form_data.append(question_info)
                        continue
                    
                    # Detect textarea
                    textareas = question_elem.find_elements(By.CSS_SELECTOR, "textarea")
                    if textareas:
                        question_info["type"] = "textarea"
                        form_data.append(question_info)
                        continue
                    
                    # Detect dropdown/select
                    selects = question_elem.find_elements(By.CSS_SELECTOR, "select")
                    if selects:
                        question_info["type"] = "dropdown"
                        select_elem = selects[0]
                        options_elem = select_elem.find_elements(By.TAG_NAME, "option")
                        for opt in options_elem:
                            opt_text = opt.text.strip()
                            if opt_text and opt_text.lower() != "choose":
                                question_info["options"].append({
                                    "text": opt_text,
                                    "value": opt.get_attribute("value"),
                                    "element": opt
                                })
                        form_data.append(question_info)
                        continue
                    
                    # Detect date input
                    date_inputs = question_elem.find_elements(By.CSS_SELECTOR, "input[type='date']")
                    if date_inputs:
                        question_info["type"] = "date"
                        form_data.append(question_info)
                        continue
                    
                    # Detect time input
                    time_inputs = question_elem.find_elements(By.CSS_SELECTOR, "input[type='time']")
                    if time_inputs:
                        question_info["type"] = "time"
                        form_data.append(question_info)
                        continue
                    
                    # Detect number input
                    number_inputs = question_elem.find_elements(By.CSS_SELECTOR, "input[type='number']")
                    if number_inputs:
                        question_info["type"] = "number"
                        form_data.append(question_info)
                        continue
                    
                    # Detect telephone input
                    tel_inputs = question_elem.find_elements(By.CSS_SELECTOR, "input[type='tel']")
                    if tel_inputs:
                        question_info["type"] = "tel"
                        form_data.append(question_info)
                        continue
                    
                except Exception as e:
                    print(f"⚠ Error parsing Q{idx}: {type(e).__name__}")
                    continue
            
            return form_data
            
        except Exception as e:
            print(f"❌ Error extracting form: {e}")
            return []
    
    def build_context_string(self):
        """Build context string from answer history"""
        if not self.answer_history:
            return ""
        
        context = "\n📋 Form Context (Previous Answers):\n"
        for qa in self.answer_history[-10:]:  # Keep last 10 Q&A for context
            context += f"Q: {qa['question'][:80]}...\nA: {qa['answer']}\n\n"
        return context
    
    def ask_gemini_for_choice(self, question_text, options, question_type):
        """Ask Gemini for answer or choice with context"""
        context = self.build_context_string()
        
        if question_type in ["text", "email", "textarea"]:
            prompt = f"""You are filling out a Google Form intelligently.
{context}
Current Question: {question_text}

Provide a realistic, concise answer in Vietnamese if the form is in Vietnamese, else in English.
For dates, use YYYY format.
Make answer consistent with previous context if applicable.
Answer only, no explanation."""
            
        elif question_type == "radio":
            options_text = "\n".join([f"{i+1}. {opt['text']}" for i, opt in enumerate(options)])
            prompt = f"""You are filling out a Google Form intelligently.
{context}
Current Question: {question_text}

Options:
{options_text}

Choose the MOST APPROPRIATE option considering previous answers for consistency.
Respond with ONLY the number (1, 2, 3, etc.)."""
            
        elif question_type == "checkbox":
            options_text = "\n".join([f"{i+1}. {opt['text']}" for i, opt in enumerate(options)])
            prompt = f"""You are filling out a Google Form intelligently.
{context}
Current Question: {question_text}

Options:
{options_text}

Choose appropriate options for consistency with previous answers.
Respond with comma-separated numbers (e.g., "1,3,4").
Only numbers, no explanation."""
            
        elif question_type in ["scale", "matrix"]:
            prompt = f"""You are filling out a Google Form intelligently.
{context}
Current Question: {question_text}

This is a rating scale (1-5: 1=lowest, 5=highest).
Choose an appropriate rating consistent with previous answers.
Respond with ONLY the number.
Generally prefer positive ratings (4-5) unless context suggests otherwise."""
        
        elif question_type == "dropdown":
            options_text = "\n".join([f"{i+1}. {opt['text']}" for i, opt in enumerate(options)])
            prompt = f"""You are filling out a Google Form intelligently.
{context}
Current Question: {question_text}

Dropdown Options:
{options_text}

Choose the MOST APPROPRIATE option from the dropdown.
Respond with ONLY the option number (1, 2, 3, etc.)."""
        
        elif question_type == "date":
            prompt = f"""You are filling out a Google Form intelligently.
{context}
Current Question: {question_text}

This is a date field. Provide a realistic date.
Respond with ONLY the date in YYYY-MM-DD format (e.g., 2024-01-15).
Choose a reasonable date relevant to the context if possible."""
        
        elif question_type == "time":
            prompt = f"""You are filling out a Google Form intelligently.
{context}
Current Question: {question_text}

This is a time field. Provide a realistic time.
Respond with ONLY the time in HH:MM format using 24-hour time (e.g., 14:30).
Choose a reasonable time relevant to the context if possible."""
        
        elif question_type == "number":
            prompt = f"""You are filling out a Google Form intelligently.
{context}
Current Question: {question_text}

This is a numeric field. Provide a realistic number.
Respond with ONLY the number, no text.
Choose a reasonable value relevant to the context if possible."""
        
        elif question_type == "tel":
            prompt = f"""You are filling out a Google Form intelligently.
{context}
Current Question: {question_text}

This is a telephone/phone number field. Provide a realistic phone number.
Respond with ONLY the phone number in a standard format (e.g., +1-XXX-XXX-XXXX or XXXXXXXXXX).
Choose a reasonable number relevant to the context if possible."""
        
        elif question_type in ["scale", "matrix"]:
            prompt = f"""You are filling out a Google Form intelligently.
{context}
Current Question: {question_text}

This is a rating scale (1-5: 1=lowest, 5=highest).
Choose an appropriate rating consistent with previous answers.
Respond with ONLY the number.
Generally prefer positive ratings (4-5) unless context suggests otherwise."""
        
        else:
            return None
        
        try:
            response = self.model.generate_content(prompt)
            answer = response.text.strip()
            print(f"   🤖 Gemini: {answer}")
            return answer
        except Exception as e:
            print(f"   ⚠ Gemini error: {e}")
            return None
    
    def fill_question(self, question_info):
        """Fill a single question"""
        print(f"\n📝 Q{question_info['index']}: {question_info['question'][:60]}...")
        print(f"   Type: {question_info['type']}")
        
        try:
            if question_info['type'] in ['text', 'email']:
                answer = self.ask_gemini_for_choice(
                    question_info['question'],
                    [],
                    question_info['type']
                )
                if answer:
                    input_elem = question_info['element'].find_element(By.CSS_SELECTOR, "input")
                    input_elem.clear()
                    input_elem.send_keys(answer)
                    print(f"   ✓ Filled: {answer}")
                    # Store in history
                    self.answer_history.append({
                        "question": question_info['question'],
                        "answer": answer,
                        "type": question_info['type']
                    })
                    time.sleep(0.5)
                    return True
            
            elif question_info['type'] == 'textarea':
                answer = self.ask_gemini_for_choice(
                    question_info['question'],
                    [],
                    'textarea'
                )
                if answer:
                    textarea_elem = question_info['element'].find_element(By.CSS_SELECTOR, "textarea")
                    textarea_elem.clear()
                    textarea_elem.send_keys(answer)
                    print(f"   ✓ Filled: {answer[:50]}...")
                    # Store in history
                    self.answer_history.append({
                        "question": question_info['question'],
                        "answer": answer,
                        "type": "textarea"
                    })
                    time.sleep(0.5)
                    return True
            
            elif question_info['type'] == 'radio':
                choice = self.ask_gemini_for_choice(
                    question_info['question'],
                    question_info['options'],
                    'radio'
                )
                if choice and choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(question_info['options']):
                        selected_option = question_info['options'][idx]
                        selected_option['element'].click()
                        print(f"   ✓ Selected: {selected_option['text']}")
                        # Store in history
                        self.answer_history.append({
                            "question": question_info['question'],
                            "answer": selected_option['text'],
                            "type": "radio"
                        })
                        time.sleep(0.5)
                        return True
            
            elif question_info['type'] == 'checkbox':
                choices = self.ask_gemini_for_choice(
                    question_info['question'],
                    question_info['options'],
                    'checkbox'
                )
                if choices:
                    selected = []
                    for choice in choices.split(','):
                        choice = choice.strip()
                        if choice.isdigit():
                            idx = int(choice) - 1
                            if 0 <= idx < len(question_info['options']):
                                selected_option = question_info['options'][idx]
                                selected_option['element'].click()
                                selected.append(selected_option['text'])
                                time.sleep(0.3)
                    
                    if selected:
                        print(f"   ✓ Selected: {', '.join(selected)}")
                        # Store in history
                        self.answer_history.append({
                            "question": question_info['question'],
                            "answer": ", ".join(selected),
                            "type": "checkbox"
                        })
                        return True
            
            elif question_info['type'] == 'matrix':
                print(f"   📊 Matrix with {len(question_info['rows'])} rows")
                ratings = []
                
                for row_idx, row in enumerate(question_info['rows'], 1):
                    try:
                        rating = self.ask_gemini_for_choice(
                            f"{question_info['question']} - {row['label']}",
                            [],
                            'scale'
                        )
                        
                        if rating and rating.isdigit():
                            idx = int(rating) - 1
                            if 0 <= idx < len(row['options']):
                                row['options'][idx].click()
                                print(f"   ✓ Row {row_idx}: {row['label'][:40]} → {rating}")
                                ratings.append(f"{row['label']}: {rating}")
                                time.sleep(0.3)
                        
                    except Exception as e:
                        print(f"   ✗ Row {row_idx} error: {str(e)[:60]}")
                
                # Store in history
                if ratings:
                    self.answer_history.append({
                        "question": question_info['question'],
                        "answer": "; ".join(ratings),
                        "type": "matrix"
                    })
                return True
            
            elif question_info['type'] == 'dropdown':
                choice = self.ask_gemini_for_choice(
                    question_info['question'],
                    question_info['options'],
                    'dropdown'
                )
                if choice and choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(question_info['options']):
                        select_elem = question_info['element'].find_element(By.CSS_SELECTOR, "select")
                        from selenium.webdriver.support.select import Select
                        Select(select_elem).select_by_index(idx)
                        selected_text = question_info['options'][idx]['text']
                        print(f"   ✓ Selected: {selected_text}")
                        # Store in history
                        self.answer_history.append({
                            "question": question_info['question'],
                            "answer": selected_text,
                            "type": "dropdown"
                        })
                        time.sleep(0.5)
                        return True
            
            elif question_info['type'] == 'date':
                answer = self.ask_gemini_for_choice(
                    question_info['question'],
                    [],
                    'date'
                )
                if answer:
                    date_input = question_info['element'].find_element(By.CSS_SELECTOR, "input[type='date']")
                    date_input.send_keys(answer)
                    print(f"   ✓ Filled date: {answer}")
                    # Store in history
                    self.answer_history.append({
                        "question": question_info['question'],
                        "answer": answer,
                        "type": "date"
                    })
                    time.sleep(0.5)
                    return True
            
            elif question_info['type'] == 'time':
                answer = self.ask_gemini_for_choice(
                    question_info['question'],
                    [],
                    'time'
                )
                if answer:
                    time_input = question_info['element'].find_element(By.CSS_SELECTOR, "input[type='time']")
                    time_input.send_keys(answer)
                    print(f"   ✓ Filled time: {answer}")
                    # Store in history
                    self.answer_history.append({
                        "question": question_info['question'],
                        "answer": answer,
                        "type": "time"
                    })
                    time.sleep(0.5)
                    return True
            
            elif question_info['type'] == 'number':
                answer = self.ask_gemini_for_choice(
                    question_info['question'],
                    [],
                    'number'
                )
                if answer:
                    number_input = question_info['element'].find_element(By.CSS_SELECTOR, "input[type='number']")
                    number_input.clear()
                    number_input.send_keys(answer)
                    print(f"   ✓ Filled number: {answer}")
                    # Store in history
                    self.answer_history.append({
                        "question": question_info['question'],
                        "answer": answer,
                        "type": "number"
                    })
                    time.sleep(0.5)
                    return True
            
            elif question_info['type'] == 'tel':
                answer = self.ask_gemini_for_choice(
                    question_info['question'],
                    [],
                    'tel'
                )
                if answer:
                    tel_input = question_info['element'].find_element(By.CSS_SELECTOR, "input[type='tel']")
                    tel_input.clear()
                    tel_input.send_keys(answer)
                    print(f"   ✓ Filled phone: {answer}")
                    # Store in history
                    self.answer_history.append({
                        "question": question_info['question'],
                        "answer": answer,
                        "type": "tel"
                    })
                    time.sleep(0.5)
                    return True
            
        except Exception as e:
            print(f"   ✗ Error: {str(e)[:100]}")
            return False
        
        return False
    
    def click_next_or_submit(self):
        """Click Next or Submit button"""
        try:
            # Next/Continue button selectors (various languages & variations)
            next_selectors = [
                "//span[contains(text(), 'Next')]/..",
                "//span[contains(text(), 'next')]/..",
                "//span[contains(text(), 'Tiếp')]/..",
                "//span[contains(text(), 'Continue')]/..",
                "//span[contains(text(), 'continue')]/..",
                "//span[contains(text(), 'Tiếp tục')]/..",
                "//span[contains(text(), 'Next page')]/..",
                "//span[contains(text(), 'Forward')]/..",
                "//span[contains(text(), 'forward')]/..",
                "//button[contains(text(), 'Next')]",
                "//button[contains(text(), 'next')]",
                "//button[contains(text(), 'Continue')]",
                "//button[contains(text(), 'continue')]",
                "//a[contains(text(), 'Next')]",
                "//a[contains(text(), 'Continue')]",
            ]
            
            for selector in next_selectors:
                try:
                    btn = self.driver.find_element(By.XPATH, selector)
                    if btn.is_displayed() and btn.is_enabled():
                        btn.click()
                        print("\n➡️  Clicked Next/Continue")
                        time.sleep(2)
                        return "next"
                except:
                    continue
            
            # Submit/Send button selectors (various languages & variations)
            submit_selectors = [
                "//span[contains(text(), 'Submit')]/..",
                "//span[contains(text(), 'submit')]/..",
                "//span[contains(text(), 'Gửi')]/..",
                "//span[contains(text(), 'Send')]/..",
                "//span[contains(text(), 'send')]/..",
                "//span[contains(text(), 'Finish')]/..",
                "//span[contains(text(), 'finish')]/..",
                "//span[contains(text(), 'OK')]/..",
                "//span[contains(text(), 'ok')]/..",
                "//span[contains(text(), 'Done')]/..",
                "//span[contains(text(), 'done')]/..",
                "//span[contains(text(), 'Xác nhận')]/..",
                "//span[contains(text(), 'Gửi phản hồi')]/..",
                "//button[contains(text(), 'Submit')]",
                "//button[contains(text(), 'submit')]",
                "//button[contains(text(), 'Send')]",
                "//button[contains(text(), 'Finish')]",
                "//button[contains(text(), 'OK')]",
                "//a[contains(text(), 'Submit')]",
                "//a[contains(text(), 'Send')]",
            ]
            
            for selector in submit_selectors:
                try:
                    btn = self.driver.find_element(By.XPATH, selector)
                    if btn.is_displayed() and btn.is_enabled():
                        btn.click()
                        print("\n✅ Clicked Submit")
                        time.sleep(3)
                        return "submit"
                except:
                    continue
            
            print("\n⚠ No Next/Submit button found")
            return None
            
        except Exception as e:
            print(f"\n⚠ Error clicking button: {e}")
            return None
    
    def fill_form_smart(self, form_url):
        """Fill entire form by analyzing structure"""
        try:
            print(f"🌐 Opening form: {form_url}")
            self.driver.get(form_url)
            time.sleep(self.config['wait_time'])
            
            section = 1
            while True:
                print(f"\n{'='*60}")
                print(f"📄 SECTION {section}")
                print(f"{'='*60}")
                if self.answer_history:
                    print(f"📝 Current history: {len(self.answer_history)} Q&A pairs")
                
                form_data = self.extract_form_structure()
                
                if not form_data:
                    print("⚠ No questions found")
                    break
                
                print(f"\n✓ Found {len(form_data)} questions")
                
                for question in form_data:
                    self.fill_question(question)
                
                action = self.click_next_or_submit()
                
                if action == "submit":
                    print("\n🎉 Form submitted successfully!")
                    break
                elif action == "next":
                    section += 1
                    time.sleep(1.5)
                else:
                    break
            
            print("\n✅ Process complete!")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
        
        finally:
            time.sleep(5)
    
    def close(self):
        """Close browser and show summary"""
        if self.answer_history:
            print("\n" + "="*60)
            print("📊 FORM SUBMISSION SUMMARY")
            print("="*60)
            print(f"Total answers provided: {len(self.answer_history)}")
            for idx, qa in enumerate(self.answer_history, 1):
                print(f"\n{idx}. {qa['question'][:70]}...")
                print(f"   Answer: {qa['answer'][:80]}")
        
        self.driver.quit()
        print("\nBrowser closed")


def main():
    """Main function"""
    print("=" * 60)
    print("🤖 SMART GOOGLE FORM AUTOFILL V2")
    print("=" * 60)
    print("\n✨ Features:")
    print("  • Auto-detects all form questions")
    print("  • AI chooses best answers with Gemini")
    print("  • No manual configuration needed")
    print("=" * 60)
    
    form_url = input("\n📝 Enter Google Form URL: ").strip()
    
    if not form_url:
        print("❌ No URL provided")
        return
    
    autofill = SmartGoogleFormAutofill()
    
    try:
        autofill.fill_form_smart(form_url)
    finally:
        autofill.close()


if __name__ == "__main__":
    main()
