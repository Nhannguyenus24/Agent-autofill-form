from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Khởi tạo Chrome
driver = webdriver.Chrome(executable_path="path/to/chromedriver")

# Mở Google Form
driver.get("https://docs.google.com/forms/d/e/ID_FORM/viewform")

time.sleep(2)  # đợi form load

# Điền text field
name_field = driver.find_element(By.XPATH, '//input[@type="text"]')
name_field.send_keys("Nguyen Nhan")

# Chọn radio button
radio = driver.find_element(By.XPATH, '//div[@role="radio"]')
radio.click()

# Submit form
submit_btn = driver.find_element(By.XPATH, '//span[text()="Submit"]/..')
submit_btn.click()

time.sleep(2)
driver.quit()
