import json
import time
import google.generativeai as genai
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class SmartGoogleFormAutofill:
    def __init__(self, config_file='config.json'):
        """Initialize with config file only - no questions file needed"""
        # Load config
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # Configure Gemini API
        genai.configure(api_key=self.config['gemini_api_key'])
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Initialize Chrome WebDriver
        from selenium.webdriver.chrome.service import Service
        service = Service(executable_path=self.config['chromedriver_path'])
        self.driver = webdriver.Chrome(service=service)
        self.wait = WebDriverWait(self.driver, 10)
        
        self.form_structure = []
    
    def extract_form_structure(self):
        """Extract all questions and options from the current form page"""
        print("\n🔍 Analyzing form structure...")
        
        try:
            # Find all question containers
            questions = self.driver.find_elements(By.CSS_SELECTOR, "div[role='listitem']")
            
            form_data = []
            
            for idx, question_elem in enumerate(questions, 1):
                try:
                    # Get question text
                    try:
                        question_text = question_elem.find_element(By.CSS_SELECTOR, ".M7eMe").text
                    except Exception as e:
                        print(f"⚠ Q{idx}: Cannot find question text - {type(e).__name__}: {str(e)[:80]}")
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
                    
                    # Detect question type and get options
                    
                    # Check for matrix/grid questions FIRST (multiple radiogroups)
                    radiogroups = question_elem.find_elements(By.CSS_SELECTOR, "div[role='radiogroup']")
                    if len(radiogroups) > 1:
                        # This is a matrix question (grid with multiple rows)
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
                                print(f"   ⚠ Error parsing matrix row: {str(e)[:50]}")
                        
                        if question_info["rows"]:
                            form_data.append(question_info)
                        continue
                    
                    # Check for radio buttons (single choice)
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
                    
                    # Check for checkboxes
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
                    
                    # Check for text input (after radio/checkbox to avoid "Other" field confusion)
                    text_inputs = question_elem.find_elements(By.CSS_SELECTOR, "input[type='text']")
                    if text_inputs:
                        question_info["type"] = "text"
                        form_data.append(question_info)
                        continue
                    
                    # Check for email input
                    email_inputs = question_elem.find_elements(By.CSS_SELECTOR, "input[type='email']")
                    if email_inputs:
                        question_info["type"] = "email"
                        form_data.append(question_info)
                        continue
                    
                    # Check for textarea
                    textareas = question_elem.find_elements(By.CSS_SELECTOR, "textarea")
                    if textareas:
                        question_info["type"] = "textarea"
                        form_data.append(question_info)
                        continue
                    
                except Exception as e:
                    import traceback
                    print(f"⚠ Error parsing question {idx}:")
                    print(f"   Type: {type(e).__name__}")
                    print(f"   Message: {str(e)[:100]}")
                    print(f"   Details: {traceback.format_exc()[:200]}")
                    continue
            
            return form_data
            
        except Exception as e:
            print(f"❌ Error extracting form: {e}")
            return []
    
    def ask_gemini_for_choice(self, question_text, options, question_type):
        """Ask Gemini to choose the best option or generate content"""
        
        if question_type in ["text", "email", "textarea"]:
            # Generate content
            prompt = f"""You are filling out a Google Form survey. 
Question: {question_text}

Please provide a realistic and appropriate answer in Vietnamese if the question is in Vietnamese, otherwise in English.
Keep it concise and natural. For years, use format YYYY.
Just give the answer, no explanation."""
            
        elif question_type == "radio":
            # Choose one option
            options_text = "\n".join([f"{i+1}. {opt['text']}" for i, opt in enumerate(options)])
            prompt = f"""You are filling out a Google Form survey.
Question: {question_text}

Available options:
{options_text}

Choose the MOST APPROPRIATE option by responding with ONLY the option number (1, 2, 3, etc.).
No explanation needed, just the number."""
            
        elif question_type == "checkbox":
            # Choose multiple options
            options_text = "\n".join([f"{i+1}. {opt['text']}" for i, opt in enumerate(options)])
            prompt = f"""You are filling out a Google Form survey.
Question: {question_text}

Available options:
{options_text}

Choose ONE OR MORE appropriate options. Respond with comma-separated numbers (e.g., "1,3,4").
Just the numbers, no explanation."""
            
        elif question_type in ["scale", "matrix"]:
            # Choose rating
            prompt = f"""You are filling out a Google Form survey.
Question: {question_text}

This is a rating scale question (typically 1-5 where 1=lowest, 5=highest).
Choose an appropriate rating number. Respond with ONLY the number.
Generally lean towards positive ratings (4 or 5) unless the question suggests otherwise."""
        
        else:
            return None
        
        try:
            response = self.model.generate_content(prompt)
            answer = response.text.strip()
            print(f"   🤖 Gemini suggests: {answer}")
            return answer
        except Exception as e:
            print(f"   ⚠ Gemini error: {e}")
            return None
    
    def fill_question(self, question_info):
        """Fill a single question based on Gemini's suggestion"""
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
                        time.sleep(0.5)
                        
                        # Check if this is "Other" option that needs text input
                        if selected_option['text'] == '__other_option__' or 'Other' in selected_option['text']:
                            try:
                                # Find the text input field that appears after clicking Other
                                time.sleep(0.5)
                                other_input = question_info['element'].find_element(By.CSS_SELECTOR, "input[type='text']")
                                
                                # Ask Gemini for custom text
                                other_text = self.ask_gemini_for_choice(
                                    f"{question_info['question']} (Other option - provide specific answer)",
                                    [],
                                    'text'
                                )
                                
                                if other_text:
                                    other_input.clear()
                                    other_input.send_keys(other_text)
                                    print(f"   ✓ Other text filled: {other_text}")
                                    time.sleep(0.5)
                            except Exception as e:
                                print(f"   ⚠ Could not fill Other text: {str(e)[:50]}")
                        
                        return True
            
            elif question_info['type'] == 'checkbox':
                choices = self.ask_gemini_for_choice(
                    question_info['question'],
                    question_info['options'],
                    'checkbox'
                )
                if choices:
                    selected = []
                    has_other = False
                    
                    for choice in choices.split(','):
                        choice = choice.strip()
                        if choice.isdigit():
                            idx = int(choice) - 1
                            if 0 <= idx < len(question_info['options']):
                                selected_option = question_info['options'][idx]
                                selected_option['element'].click()
                                selected.append(selected_option['text'])
                                
                                # Check if this is Other option
                                if selected_option['text'] == '__other_option__' or 'Other' in selected_option['text']:
                                    has_other = True
                                
                                time.sleep(0.3)
                    
                    if selected:
                        print(f"   ✓ Selected: {', '.join(selected)}")
                        
                        # Fill Other text if needed
                        if has_other:
                            try:
                                time.sleep(0.5)
                                other_input = question_info['element'].find_element(By.CSS_SELECTOR, "input[type='text']")
                                
                                other_text = self.ask_gemini_for_choice(
                                    f"{question_info['question']} (Other option - provide specific answer)",
                                    [],
                                    'text'
                                )
                                
                                if other_text:
                                    other_input.clear()
                                    other_input.send_keys(other_text)
                                    print(f"   ✓ Other text filled: {other_text}")
                                    time.sleep(0.5)
                            except Exception as e:
                                print(f"   ⚠ Could not fill Other text: {str(e)[:50]}")
                        
                        return True
            
            elif question_info['type'] == 'scale':
                rating = self.ask_gemini_for_choice(
                    question_info['question'],
                    question_info['options'],
                    'scale'
                )
                if rating and rating.isdigit():
                    # Find option with matching value
                    for opt in question_info['options']:
                        if opt['value'] == rating:
                            opt['element'].click()
                            print(f"   ✓ Rated: {rating}")
                            time.sleep(0.5)
                            return True
            
            elif question_info['type'] == 'matrix':
                # Fill all rows with ratings
                print(f"   📊 Matrix with {len(question_info['rows'])} rows")
                
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
                                print(f"   ✓ Row {row_idx}/{len(question_info['rows'])}: {row['label'][:40]} → {rating}")
                                time.sleep(0.3)
                            else:
                                print(f"   ⚠ Row {row_idx}: Rating {rating} out of range (1-{len(row['options'])})")
                        else:
                            print(f"   ⚠ Row {row_idx}: Invalid rating from Gemini: {rating}")
                            
                    except Exception as e:
                        print(f"   ✗ Row {row_idx} error: {type(e).__name__} - {str(e)[:60]}")
                        continue
                
                return True
            
        except Exception as e:
            print(f"   ✗ Error filling question: {str(e)[:100]}")
            return False
        
        return False
    
    def click_next_or_submit(self):
        """Click Next or Submit button"""
        try:
            # Try Next button first
            next_selectors = [
                "//span[contains(text(), 'Next')]/..",
                "//span[contains(text(), 'Tiếp')]/..",
            ]
            
            for selector in next_selectors:
                try:
                    btn = self.driver.find_element(By.XPATH, selector)
                    btn.click()
                    print("\n➡️  Clicked Next")
                    time.sleep(2)
                    return "next"
                except:
                    continue
            
            # Try Submit button
            submit_selectors = [
                "//span[contains(text(), 'Submit')]/..",
                "//span[contains(text(), 'Gửi')]/..",
            ]
            
            for selector in submit_selectors:
                try:
                    btn = self.driver.find_element(By.XPATH, selector)
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
        """Smart fill entire form by analyzing structure"""
        try:
            print(f"🌐 Opening form: {form_url}")
            self.driver.get(form_url)
            time.sleep(self.config['wait_time'])
            
            section = 1
            while True:
                print(f"\n{'='*60}")
                print(f"📄 SECTION {section}")
                print(f"{'='*60}")
                
                # Extract current page structure
                form_data = self.extract_form_structure()
                
                if not form_data:
                    print("⚠ No questions found on this page")
                    break
                
                print(f"\n✓ Found {len(form_data)} questions")
                
                # Fill each question
                for question in form_data:
                    self.fill_question(question)
                
                # Try to proceed to next section or submit
                action = self.click_next_or_submit()
                
                if action == "submit":
                    print("\n🎉 Form submitted successfully!")
                    break
                elif action == "next":
                    section += 1
                    time.sleep(1.5)
                else:
                    print("\n⚠ Reached end of form or manual action needed")
                    break
            
            print("\n✅ Process complete!")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
        
        finally:
            time.sleep(5)
    
    def close(self):
        """Close browser"""
        self.driver.quit()
        print("Browser closed")


def main():
    """Main function for V2"""
    print("=" * 60)
    print("🤖 SMART GOOGLE FORM AUTOFILL V2 - AI POWERED")
    print("=" * 60)
    print("\n✨ Version 2 Features:")
    print("  • Auto-detects all form questions")
    print("  • AI chooses best answers")
    print("  • No manual question configuration needed")
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
