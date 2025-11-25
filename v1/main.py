import json
import time
import google.generativeai as genai
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class GoogleFormAutofill:
    def __init__(self, config_file='config.json', questions_file='questions_example_multisection.json'):
        """Initialize with config and questions files"""
        # Load config
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # Load questions
        with open(questions_file, 'r', encoding='utf-8') as f:
            self.questions_data = json.load(f)
        
        # Configure Gemini API
        genai.configure(api_key=self.config['gemini_api_key'])
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Initialize Chrome WebDriver
        from selenium.webdriver.chrome.service import Service
        service = Service(executable_path=self.config['chromedriver_path'])
        self.driver = webdriver.Chrome(service=service)
        self.wait = WebDriverWait(self.driver, 10)
    
    def get_gemini_response(self, prompt):
        """Call Gemini API to get answer"""
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return ""
    
    def fill_text_field(self, xpath, prompt):
        """Fill text field with data from Gemini"""
        try:
            element = self.wait.until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            answer = self.get_gemini_response(prompt)
            element.clear()
            element.send_keys(answer)
            print(f"✓ Filled: {answer}")
            time.sleep(0.5)
            return True
        except (TimeoutException, NoSuchElementException) as e:
            print(f"✗ Field not found with xpath: {xpath}")
            return False
    
    def fill_textarea(self, xpath, prompt):
        """Fill textarea with data from Gemini"""
        try:
            element = self.wait.until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            answer = self.get_gemini_response(prompt)
            element.clear()
            element.send_keys(answer)
            print(f"✓ Filled textarea: {answer[:50]}...")
            time.sleep(0.5)
            return True
        except (TimeoutException, NoSuchElementException) as e:
            print(f"✗ Textarea not found with xpath: {xpath}")
            return False
    
    def click_radio_or_checkbox(self, xpath):
        """Click radio button or checkbox"""
        try:
            element = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            element.click()
            print(f"✓ Clicked element")
            time.sleep(0.5)
            return True
        except (TimeoutException, NoSuchElementException) as e:
            print(f"✗ Element not found with xpath: {xpath}")
            return False
    
    def click_next_button(self):
        """Click Next button to go to next section"""
        try:
            next_selectors = [
                "//span[contains(text(), 'Next')]/..",
                "//span[contains(text(), 'Tiếp')]/..",
                "//div[@role='button' and contains(., 'Next')]",
                "//div[@role='button' and contains(., 'Tiếp')]"
            ]
            
            for selector in next_selectors:
                try:
                    next_btn = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    next_btn.click()
                    print("✓ Clicked Next button")
                    time.sleep(1.5)
                    return True
                except:
                    continue
            
            print("⚠ Next button not found")
            return False
            
        except Exception as e:
            print(f"⚠ Error clicking Next: {e}")
            return False
    
    def fill_form(self):
        """Fill entire form with multi-section support"""
        try:
            # Open Google Form
            print(f"Opening form: {self.questions_data['form_url']}")
            self.driver.get(self.questions_data['form_url'])
            time.sleep(self.config['wait_time'])
            
            current_section = 1
            sections = self.questions_data.get('sections', [self.questions_data.get('questions', [])])
            
            # If old format (no sections), convert to new format
            if 'questions' in self.questions_data and 'sections' not in self.questions_data:
                sections = [self.questions_data['questions']]
            
            for section_idx, section_questions in enumerate(sections, 1):
                print(f"\n{'='*60}")
                print(f"📄 SECTION {section_idx}/{len(sections)}")
                print(f"{'='*60}")
                
                # Process each question in section
                for idx, question in enumerate(section_questions, 1):
                    print(f"\n[Q{idx}/{len(section_questions)}] Processing: {question['type']}")
                    
                    if question['type'] == 'text':
                        self.fill_text_field(question['xpath'], question['prompt'])
                    
                    elif question['type'] == 'textarea':
                        self.fill_textarea(question['xpath'], question['prompt'])
                    
                    elif question['type'] in ['radio', 'checkbox']:
                        self.click_radio_or_checkbox(question['xpath'])
                    
                    elif question['type'] == 'scale':
                        # Handle matrix/scale questions
                        self.click_radio_or_checkbox(question['xpath'])
                
                # After finishing section, click Next or Submit
                if section_idx < len(sections):
                    print("\n🔄 Moving to next section...")
                    if not self.click_next_button():
                        print("⚠ Could not proceed to next section")
                        break
                else:
                    # Last section - submit form
                    print("\n🔍 Looking for Submit button...")
                    try:
                        submit_selectors = [
                            "//span[contains(text(), 'Submit')]/..",
                            "//span[contains(text(), 'Gửi')]/..",
                            "//div[@role='button' and contains(., 'Submit')]",
                            "//div[@role='button' and contains(., 'Gửi')]"
                        ]
                        
                        submit_clicked = False
                        for selector in submit_selectors:
                            try:
                                submit_btn = self.driver.find_element(By.XPATH, selector)
                                submit_btn.click()
                                print("✓ Form submitted!")
                                submit_clicked = True
                                break
                            except:
                                continue
                        
                        if not submit_clicked:
                            print("⚠ Submit button not found, please submit manually")
                        
                        time.sleep(3)
                        
                    except Exception as e:
                        print(f"⚠ Error submitting: {e}")
                        print("Please submit manually")
            
            print("\n✅ Complete!")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
        
        finally:
            # Wait a bit before closing
            time.sleep(5)
    
    def close(self):
        """Close browser"""
        self.driver.quit()
        print("Browser closed")


def main():
    """Main function"""
    print("=" * 60)
    print("🤖 GOOGLE FORM AUTOFILL WITH GEMINI AI")
    print("=" * 60)
    
    autofill = GoogleFormAutofill()
    
    try:
        autofill.fill_form()
    finally:
        autofill.close()


if __name__ == "__main__":
    main()
