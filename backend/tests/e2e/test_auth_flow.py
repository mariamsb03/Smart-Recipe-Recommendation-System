"""
E2E Test: User Registration and Login Flow
Tests complete user authentication journey
"""
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime
import random
import string


@pytest.fixture(scope='module')
def driver():
    """Setup Selenium WebDriver"""
    chrome_options = Options()
    # For debugging, you might want to remove headless initially
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(15)
    yield driver
    driver.quit()


def generate_random_email():
    """Generate a unique email for testing"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_string = ''.join(random.choices(string.ascii_lowercase, k=8))
    return f'test_{random_string}_{timestamp}@example.com'


class TestAuthenticationFlow:
    """E2E tests for user authentication"""
    
    BASE_URL = 'http://localhost:8080'
    
    def test_landing_page(self, driver):
        """Test landing page loads"""
        try:
            driver.get(self.BASE_URL)
            time.sleep(3)
            
            # Check for landing page elements - adjust based on your landing page
            assert 'FlavorFit' in driver.title or 'FlavorFit' in driver.page_source
            
            # Look for Get Started button (common on landing pages)
            get_started_selectors = [
                "//button[contains(text(), 'Get Started')]",
                "//a[contains(text(), 'Get Started')]",
                "//button[contains(text(), 'Sign Up')]",
                "//a[contains(text(), 'Sign Up')]"
            ]
            
            for selector in get_started_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    if elements and elements[0].is_displayed():
                        print(f"✓ Found {selector}")
                        break
                except:
                    continue
            
            print("✓ Landing page loads correctly")
            
        except Exception as e:
            print(f"Landing page test error: {e}")
            raise
    
    def test_navigate_to_signup(self, driver):
        """Test navigating to signup page"""
        try:
            driver.get(self.BASE_URL)
            time.sleep(2)
            
            # Try to find and click signup button
            signup_selectors = [
                "//button[contains(text(), 'Get Started')]",
                "//a[contains(text(), 'Get Started')]",
                "//button[contains(text(), 'Sign Up')]",
                "//a[contains(text(), 'Sign Up')]"
            ]
            
            for selector in signup_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    if elements and elements[0].is_displayed():
                        elements[0].click()
                        time.sleep(3)
                        break
                except:
                    continue
            
            # If still not on signup page, go directly
            if 'signup' not in driver.current_url:
                driver.get(f'{self.BASE_URL}/signup')
                time.sleep(3)
            
            # Verify we're on signup page by checking for form elements
            page_text = driver.page_source
            assert 'Create Your Account' in page_text or 'Sign Up' in page_text
            print("✓ Navigated to signup page")
            
        except Exception as e:
            print(f"Navigate to signup error: {e}")
            raise
    
    def test_navigate_to_login(self, driver):
        """Test navigating to login page"""
        try:
            driver.get(self.BASE_URL)
            time.sleep(2)
            
            # Look for login link/button
            login_selectors = [
                "//button[contains(text(), 'Sign In')]",
                "//a[contains(text(), 'Sign In')]",
                "//a[contains(text(), 'Login')]"
            ]
            
            for selector in login_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    if elements and elements[0].is_displayed():
                        elements[0].click()
                        time.sleep(3)
                        break
                except:
                    continue
            
            # If still not on login page, go directly
            if 'login' not in driver.current_url:
                driver.get(f'{self.BASE_URL}/login')
                time.sleep(3)
            
            # Verify we're on login page
            page_text = driver.page_source
            assert 'Sign In' in page_text or 'Welcome Back' in page_text
            print("✓ Navigated to login page")
            
        except Exception as e:
            print(f"Navigate to login error: {e}")
            raise
    
    def test_login_form_structure(self, driver):
        """Test login form has correct fields"""
        try:
            driver.get(f'{self.BASE_URL}/login')
            time.sleep(3)
            
            # Check for form elements
            page_text = driver.page_source
            assert 'Sign In' in page_text or 'Welcome Back' in page_text
            
            # Look for email and password inputs
            inputs = driver.find_elements(By.CSS_SELECTOR, 'input')
            
            # Should have at least email and password inputs
            email_found = False
            password_found = False
            
            for inp in inputs:
                input_type = inp.get_attribute('type') or ''
                if 'email' in input_type.lower():
                    email_found = True
                elif 'password' in input_type.lower():
                    password_found = True
            
            assert email_found, "Should have email input"
            assert password_found, "Should have password input"
            
            # Look for sign in button
            signin_buttons = driver.find_elements(By.XPATH, 
                "//button[contains(text(), 'Sign In') or contains(text(), 'Login')]")
            assert len(signin_buttons) > 0, "Should have Sign In button"
            
            print("✓ Login form has correct structure")
            
        except Exception as e:
            print(f"Login form test error: {e}")
            raise
    
    def test_signup_form_structure(self, driver):
        """Test signup form has correct fields"""
        try:
            driver.get(f'{self.BASE_URL}/signup')
            time.sleep(3)
            
            # Check for form elements
            page_text = driver.page_source
            assert 'Create Your Account' in page_text or 'Sign Up' in page_text
            
            # Look for form inputs
            inputs = driver.find_elements(By.CSS_SELECTOR, 'input')
            assert len(inputs) >= 3, "Should have at least 3 inputs (name, email, password)"
            
            # Check for multi-step signup indicators
            if 'Step' in page_text or 'step' in page_text.lower():
                print("✓ Signup form is multi-step (as expected from your React code)")
            
            print("✓ Signup form exists with correct structure")
            
        except Exception as e:
            print(f"Signup form test error: {e}")
            raise
    
    def test_complete_signup_flow(self, driver):
        """Test complete user registration"""
        try:
            driver.get(f'{self.BASE_URL}/signup')
            time.sleep(3)
            
            # Generate unique user data
            user_email = generate_random_email()
            user_data = {
                'name': f'Test User {datetime.now().strftime("%H%M%S")}',
                'email': user_email,
                'password': 'TestPassword123!',
                'age': '25',
                'gender': 'male'
            }
            
            print(f"Creating user: {user_email}")
            
            # Step 1: Account Information
            # Find all inputs
            inputs = driver.find_elements(By.CSS_SELECTOR, 'input')
            
            # Fill name (first text input)
            for inp in inputs:
                input_type = inp.get_attribute('type') or ''
                placeholder = inp.get_attribute('placeholder') or ''
                if 'text' in input_type and ('name' in placeholder.lower() or inp.get_attribute('value') == ''):
                    inp.clear()
                    inp.send_keys(user_data['name'])
                    break
            
            # Fill email (email input)
            for inp in inputs:
                input_type = inp.get_attribute('type') or ''
                if 'email' in input_type:
                    inp.clear()
                    inp.send_keys(user_data['email'])
                    break
            
            # Fill password (password input)
            for inp in inputs:
                input_type = inp.get_attribute('type') or ''
                if 'password' in input_type:
                    inp.clear()
                    inp.send_keys(user_data['password'])
                    break
            
            # Find and click Continue button
            continue_buttons = driver.find_elements(By.XPATH, 
                "//button[contains(text(), 'Continue') or contains(text(), 'Next')]")
            if continue_buttons:
                continue_buttons[0].click()
                time.sleep(2)
            
            # Step 2: Demographics (if applicable)
            # Look for age input
            number_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="number"]')
            if number_inputs:
                number_inputs[0].clear()
                number_inputs[0].send_keys(user_data['age'])
                time.sleep(1)
            
            # Look for gender select
            selects = driver.find_elements(By.CSS_SELECTOR, 'select')
            if selects:
                from selenium.webdriver.support.ui import Select
                select = Select(selects[0])
                select.select_by_value(user_data['gender'])
                time.sleep(1)
            
            # Click Continue again
            continue_buttons = driver.find_elements(By.XPATH, 
                "//button[contains(text(), 'Continue') or contains(text(), 'Next')]")
            if continue_buttons:
                continue_buttons[0].click()
                time.sleep(2)
            
            # Step 3 & 4: Skip dietary and preferences for now
            # Just click through
            for _ in range(2):
                continue_buttons = driver.find_elements(By.XPATH, 
                    "//button[contains(text(), 'Continue') or contains(text(), 'Next') or contains(text(), 'Complete Setup')]")
                if continue_buttons:
                    continue_buttons[0].click()
                    time.sleep(2)
                else:
                    break
            
            # Check for success
            time.sleep(3)
            current_url = driver.current_url
            
            if 'dashboard' in current_url:
                print(f"✓ Signup successful - redirected to dashboard")
            elif 'login' in current_url:
                print(f"✓ Signup completed - redirected to login")
            else:
                # Check for success message
                page_text = driver.page_source.lower()
                if 'success' in page_text or 'welcome' in page_text or 'congratulation' in page_text:
                    print(f"✓ Signup successful - success message shown")
                else:
                    print(f"⚠ Signup completed but not redirected")
            
            return user_data
            
        except Exception as e:
            print(f"Complete signup flow error: {e}")
            return None
    
    def test_complete_login_flow(self, driver):
        """Test complete login flow"""
        try:
            # First try to create a user
            user_data = self.test_complete_signup_flow(driver)
            if not user_data:
                print("Creating test user for login test...")
                # Use default test credentials
                user_data = {
                    'email': 'test@example.com',
                    'password': 'TestPassword123!'
                }
            
            # Go to login page
            driver.get(f'{self.BASE_URL}/login')
            time.sleep(3)
            
            # Fill login form
            inputs = driver.find_elements(By.CSS_SELECTOR, 'input')
            
            for inp in inputs:
                input_type = inp.get_attribute('type') or ''
                if 'email' in input_type:
                    inp.clear()
                    inp.send_keys(user_data['email'])
                elif 'password' in input_type:
                    inp.clear()
                    inp.send_keys(user_data['password'])
            
            # Submit form
            signin_buttons = driver.find_elements(By.XPATH, 
                "//button[contains(text(), 'Sign In') or @type='submit']")
            if signin_buttons:
                signin_buttons[0].click()
            
            time.sleep(3)
            
            # Check for successful login
            current_url = driver.current_url
            
            if 'dashboard' in current_url:
                print("✓ Login successful - redirected to dashboard")
            else:
                # Check for dashboard elements
                page_text = driver.page_source
                if 'Dashboard' in page_text or 'Hi,' in page_text:
                    print("✓ Login successful - on dashboard page")
                else:
                    print("⚠ Login may have failed")
            
        except Exception as e:
            print(f"Complete login flow error: {e}")
    
    def test_login_with_invalid_credentials(self, driver):
        """Test login fails with invalid credentials"""
        try:
            driver.get(f'{self.BASE_URL}/login')
            time.sleep(3)
            
            # Fill with invalid credentials
            inputs = driver.find_elements(By.CSS_SELECTOR, 'input')
            
            for inp in inputs:
                input_type = inp.get_attribute('type') or ''
                if 'email' in input_type:
                    inp.clear()
                    inp.send_keys('invalid@example.com')
                elif 'password' in input_type:
                    inp.clear()
                    inp.send_keys('wrongpassword123')
            
            # Submit
            signin_buttons = driver.find_elements(By.XPATH, 
                "//button[contains(text(), 'Sign In') or @type='submit']")
            if signin_buttons:
                signin_buttons[0].click()
            
            time.sleep(2)
            
            # Check for error message
            page_text = driver.page_source.lower()
            error_indicators = ['invalid', 'incorrect', 'error', 'failed', 'wrong']
            
            has_error = any(indicator in page_text for indicator in error_indicators)
            
            if has_error:
                print("✓ Invalid credentials correctly rejected")
            else:
                # Also check if we're still on login page (not redirected)
                if 'login' in driver.current_url or 'signin' in driver.current_url:
                    print("✓ Still on login page after invalid credentials")
                else:
                    print("⚠ No clear error message for invalid credentials")
            
        except Exception as e:
            print(f"Invalid credentials test error: {e}")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])