import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def setup_driver():
    """Setup Chrome WebDriver with appropriate options"""
    chrome_options = Options()
    # Remove headless mode for debugging - you can add it back later if needed
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"Error setting up WebDriver: {e}")
        print("Please make sure ChromeDriver is installed and in your PATH")
        raise

def extract_company_profile_links(driver, url, max_links=5):
    """
    Extract company profile links from the Wanted homepage
    
    Args:
        driver: Selenium WebDriver instance
        url: The URL to access
        max_links: Maximum number of links to extract (default: 5)
    
    Returns:
        List of company profile URLs
    """
    print(f"Accessing URL: {url}")
    driver.get(url)
    
    # Wait for page to load
    time.sleep(3)
    
    company_links = []
    
    try:
        # Wait for AdCard elements to appear
        print(f"Looking for elements with class 'JobCard_JobCard__aVx71'...")
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "JobCard_JobCard__aVx71"))
        )
        
        # Find all AdCard elements
        ad_cards = driver.find_elements(By.CLASS_NAME, "JobCard_JobCard__aVx71")
        print(f"Found {len(ad_cards)} AdCard elements on the page")
        
        # Extract href from each AdCard
        for i, card in enumerate(ad_cards[:max_links], 1):
            try:
                # Find the anchor tag within the AdCard
                link_element = card.find_element(By.TAG_NAME, "a")
                href = link_element.get_attribute("href")
                
                # Handle relative URLs
                if href:
                    if href and not href.startswith("http"):
                        if href.startswith("/"):
                            href = "https://www.wanted.co.kr" + href
                        else:
                            href = "https://www.wanted.co.kr/" + href
                    
                    company_links.append(href)
                    print(f"  [{i}] Found link: {href}")
                else:
                    print(f"  [{i}] No href found in AdCard")
                    
            except NoSuchElementException:
                print(f"  [{i}] No anchor tag found in AdCard")
                continue
            except Exception as e:
                print(f"  [{i}] Error extracting link: {e}")
                continue
        
    except TimeoutException:
        print("Timeout: AdCard elements not found. The page might have a different structure.")
        print("Let me try to find any links on the page...")
        
        # Alternative: Try to find any links with common patterns
        try:
            all_links = driver.find_elements(By.TAG_NAME, "a")
            print(f"Found {len(all_links)} total links on the page")
            
            # Look for links that might be company profiles
            for link in all_links:
                href = link.get_attribute("href")
                if href and ("/wd/" in href or "/companies/" in href or "/ad/" in href):
                    if href not in company_links:
                        company_links.append(href)
                        if len(company_links) >= max_links:
                            break
        except Exception as e:
            print(f"Error in alternative link finding: {e}")
    
    return company_links

def extract_company_profile_data(driver, company_url):
    """
    Extract data from a company profile page
    
    Args:
        driver: Selenium WebDriver instance
        company_url: The company profile URL to visit
    
    Returns:
        Dictionary containing extracted data with keys:
        - url: The company profile URL
        - company_name: Value from data-company-name attribute
        - wds_17nsd6i_data: List of text from elements with class 'wds-17nsd6i' (max 3 items)
        - wds_h4ga6o_data: List of text from elements with class 'wds-h4ga6o' (max 3 items)
    """
    print(f"\n  Visiting: {company_url}")
    
    result = {
        'url': company_url,
        'company_name': None,  # data-company-name attribute value
        'wds_17nsd6i_data': [],  # Limit to 3 items
        'wds_h4ga6o_data': []    # Limit to 3 items
    }
    
    try:
        # Navigate to the company profile page
        driver.get(company_url)
        
        # Wait for page to load
        time.sleep(3)
        
        # Try to scroll down to load dynamic content
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        # Click the button to reveal content
        # The button has class 'wds-j7905l', and contains a div with class 'wds-n3z0cp'
        # When clicked, JavaScript reveals hidden content (toggles visibility, loads via AJAX, or expands section)
        button_clicked = False
        try:
            # Strategy 1: Find button by its actual class 'wds-j7905l'
            print(f"    Looking for button with class 'wds-j7905l'...")
            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "wds-j7905l"))
            )
            print(f"    Found button. Clicking...")
            
            # Scroll to button if needed to ensure it's visible
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
            time.sleep(1)
            
            # Check current state before clicking (for comparison)
            initial_elements_count = len(driver.find_elements(By.CLASS_NAME, "wds-17nsd6i")) + \
                                   len(driver.find_elements(By.CLASS_NAME, "wds-h4ga6o"))
            
            # Click the button
            button.click()
            button_clicked = True
            print(f"    Button clicked successfully.")
            
        except TimeoutException:
            # Strategy 2: Find button that contains an element with class 'wds-n3z0cp'
            print(f"    Button with class 'wds-j7905l' not found. Trying alternative method...")
            try:
                # Find the div with class 'wds-n3z0cp' and get its parent button
                div_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "wds-n3z0cp"))
                )
                # Find the parent button element
                button = div_element.find_element(By.XPATH, "./ancestor::button")
                print(f"    Found button via parent relationship. Clicking...")
                
                # Scroll to button if needed
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                time.sleep(1)
                
                # Check current state before clicking
                initial_elements_count = len(driver.find_elements(By.CLASS_NAME, "wds-17nsd6i")) + \
                                       len(driver.find_elements(By.CLASS_NAME, "wds-h4ga6o"))
                
                button.click()
                button_clicked = True
                print(f"    Button clicked successfully.")
                
            except Exception as e2:
                # Strategy 3: Try finding by button text "상세 정보 더 보기"
                print(f"    Alternative method failed. Trying to find by button text...")
                try:
                    button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(., '상세 정보 더 보기')]"))
                    )
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                    time.sleep(1)
                    
                    # Check current state before clicking
                    initial_elements_count = len(driver.find_elements(By.CLASS_NAME, "wds-17nsd6i")) + \
                                           len(driver.find_elements(By.CLASS_NAME, "wds-h4ga6o"))
                    
                    button.click()
                    button_clicked = True
                    print(f"    Button clicked successfully via text search.")
                except Exception as e3:
                    print(f"    Warning: Could not find or click the button using any method.")
                    print(f"    Error details: {e3}")
                    print(f"    Proceeding with data extraction anyway...")
                    initial_elements_count = 0
        
        except Exception as e:
            print(f"    Error clicking button: {e}")
            print(f"    Proceeding with data extraction anyway...")
            initial_elements_count = 0
        
        # Wait for content to load after clicking (if button was clicked)
        if button_clicked:
            print(f"    Waiting for content to appear after button click...")
            
            # Strategy 1: Wait for new elements to appear (if content is dynamically loaded)
            try:
                # Wait for at least one new element with the target classes to appear
                WebDriverWait(driver, 10).until(
                    lambda d: len(d.find_elements(By.CLASS_NAME, "wds-17nsd6i")) + 
                             len(d.find_elements(By.CLASS_NAME, "wds-h4ga6o")) > initial_elements_count
                )
                print(f"    Content has appeared (new elements detected).")
            except TimeoutException:
                # Strategy 2: Wait for elements to become visible (if content was hidden)
                try:
                    print(f"    Waiting for elements to become visible...")
                    # Check if any elements with target classes exist and are visible
                    WebDriverWait(driver, 5).until(
                        lambda d: any(
                            elem.is_displayed() for elem in 
                            (d.find_elements(By.CLASS_NAME, "wds-17nsd6i") + 
                             d.find_elements(By.CLASS_NAME, "wds-h4ga6o"))
                        )
                    )
                    print(f"    Content is now visible.")
                except TimeoutException:
                    # Strategy 3: Fallback - wait a short time for any delayed loading
                    print(f"    Using fallback wait for content loading...")
                    time.sleep(2)
            
            # Additional scroll after clicking to ensure all content is loaded
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            
            # Scroll back up a bit to ensure all elements are rendered
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(1)
        
        # Extract data-company-name attribute
        try:
            print(f"    Extracting data-company-name attribute...")
            company_name_element = driver.find_element(By.CSS_SELECTOR, "[data-company-name]")
            result['company_name'] = company_name_element.get_attribute("data-company-name")
            if result['company_name']:
                print(f"    Found company name: {result['company_name']}")
            else:
                print(f"    Warning: data-company-name attribute found but value is empty.")
        except NoSuchElementException:
            print(f"    Warning: Element with data-company-name attribute not found.")
        except Exception as e:
            print(f"    Error extracting data-company-name: {e}")
        
        # Extract data from elements with class 'wds-17nsd6i' (limit to 3 items)
        try:
            print(f"    Looking for elements with class 'wds-17nsd6i'...")
            elements_17nsd6i = driver.find_elements(By.CLASS_NAME, "wds-17nsd6i")
            print(f"    Found {len(elements_17nsd6i)} elements with class 'wds-17nsd6i'")
            
            count = 0
            for i, element in enumerate(elements_17nsd6i, 1):
                if count >= 3:  # Limit to 3 items
                    break
                try:
                    text = element.text.strip()
                    if text:  # Only add non-empty text
                        result['wds_17nsd6i_data'].append(text)
                        count += 1
                        print(f"      [{count}] Extracted: {text[:100]}..." if len(text) > 100 else f"      [{count}] Extracted: {text}")
                except Exception as e:
                    print(f"      [{i}] Error extracting text from element: {e}")
                    continue
            print(f"    Extracted {len(result['wds_17nsd6i_data'])} items from 'wds-17nsd6i' (max 3)")
        except Exception as e:
            print(f"    Error finding elements with class 'wds-17nsd6i': {e}")
        
        # Extract data from elements with class 'wds-h4ga6o' (get 2nd~4th items, total of 3)
        try:
            print(f"    Looking for elements with class 'wds-h4ga6o'...")
            elements_h4ga6o = driver.find_elements(By.CLASS_NAME, "wds-h4ga6o")
            print(f"    Found {len(elements_h4ga6o)} elements with class 'wds-h4ga6o'")
            
            # Skip the first element (index 0) and get 2nd~4th items (indices 1, 2, 3)
            count = 0
            for i, element in enumerate(elements_h4ga6o):
                if i < 1:  # Skip the first element (index 0)
                    continue
                if count >= 3:  # Limit to 3 items (2nd, 3rd, 4th)
                    break
                try:
                    text = element.text.strip()
                    if text:  # Only add non-empty text
                        result['wds_h4ga6o_data'].append(text)
                        count += 1
                        print(f"      [{count}] Extracted (item #{i+1}): {text[:100]}..." if len(text) > 100 else f"      [{count}] Extracted (item #{i+1}): {text}")
                except Exception as e:
                    print(f"      [{i+1}] Error extracting text from element: {e}")
                    continue
            print(f"    Extracted {len(result['wds_h4ga6o_data'])} items from 'wds-h4ga6o' (2nd~4th items, max 3)")
        except Exception as e:
            print(f"    Error finding elements with class 'wds-h4ga6o': {e}")
        
        # If no elements found, try using CSS selector as alternative
        if not result['wds_17nsd6i_data'] and not result['wds_h4ga6o_data']:
            print("    No elements found with class names. Trying CSS selector approach...")
            try:
                # Try finding by partial class name match
                all_elements = driver.find_elements(By.XPATH, "//*[contains(@class, 'wds-17nsd6i') or contains(@class, 'wds-h4ga6o')]")
                print(f"    Found {len(all_elements)} elements with partial class match")
                wds_h4ga6o_found_count = 0  # Track count of wds-h4ga6o elements found
                for element in all_elements:
                    try:
                        text = element.text.strip()
                        if text:
                            class_attr = element.get_attribute("class")
                            if 'wds-17nsd6i' in class_attr and len(result['wds_17nsd6i_data']) < 3:
                                result['wds_17nsd6i_data'].append(text)
                            if 'wds-h4ga6o' in class_attr:
                                wds_h4ga6o_found_count += 1
                                # Skip the first wds-h4ga6o element (get 2nd~4th)
                                if wds_h4ga6o_found_count > 1 and len(result['wds_h4ga6o_data']) < 3:
                                    result['wds_h4ga6o_data'].append(text)
                    except Exception as e:
                        continue
            except Exception as e:
                print(f"    Alternative search also failed: {e}")
        
    except Exception as e:
        print(f"    Error accessing company profile page: {e}")
        import traceback
        traceback.print_exc()
    
    return result

def main():
    """Main function - Extract company profile links and retrieve data from each"""
    url = input("Please enter the Wanted.co.kr URL you want to access: ").strip()
    
    if not url:
        print("No URL provided. Using default URL for testing...")
        url = "https://www.wanted.co.kr"
    
    print("=" * 60)
    print("Step 1: Extracting Top 5 Company Profile Links")
    print("=" * 60)
    
    driver = None
    all_extracted_data = []
    
    try:
        # Setup WebDriver
        driver = setup_driver()
        
        # Extract company profile links
        company_links = extract_company_profile_links(driver, url, max_links=5)
        
        # Display links found
        print("\n" + "=" * 60)
        print("RESULTS - Top 5 Company Profile Links")
        print("=" * 60)
        
        if company_links:
            for i, link in enumerate(company_links, 1):
                print(f"{i}. {link}")
            print(f"\nTotal links extracted: {len(company_links)}")
            
            # Step 2: Extract data from each company profile
            print("\n" + "=" * 60)
            print("Step 2: Extracting Data from Company Profiles")
            print("=" * 60)
            
            for i, company_url in enumerate(company_links, 1):
                print(f"\n[{i}/{len(company_links)}] Processing company profile {i}...")
                extracted_data = extract_company_profile_data(driver, company_url)
                all_extracted_data.append(extracted_data)
            
            # Display final results in table format
            print("\n" + "=" * 80)
            print("FINAL RESULTS - Extracted Data from All Company Profiles")
            print("=" * 80)
            
            # Prepare table data
            all_rows = []
            for data in all_extracted_data:
                # Get company name (data-company-name)
                company_name = data.get('company_name', 'N/A')
                
                # Get wds-17nsd6i data (column headers) - limit to 3
                headers_wds_17nsd6i = data.get('wds_17nsd6i_data', [])[:3]
                
                # Get wds-h4ga6o data (column values) - limit to 3
                values_wds_h4ga6o = data.get('wds_h4ga6o_data', [])[:3]
                
                # Create row: [기업명, value1, value2, value3]
                row = [company_name] + values_wds_h4ga6o
                all_rows.append({
                    'company_name': company_name,
                    'headers': headers_wds_17nsd6i,
                    'values': values_wds_h4ga6o,
                    'row': row
                })
            
            # Find maximum number of columns needed across all rows
            max_columns = 1  # At least '기업명' column
            all_headers = set()
            for row_data in all_rows:
                max_columns = max(max_columns, 1 + len(row_data['headers']))
                all_headers.update(row_data['headers'])
            
            # Use the first row's headers as standard, or combine unique headers
            # For simplicity, use first row's headers if available
            standard_headers = []
            if all_rows and all_rows[0]['headers']:
                standard_headers = all_rows[0]['headers']
            else:
                # Try to get headers from any row
                for row_data in all_rows:
                    if row_data['headers']:
                        standard_headers = row_data['headers']
                        break
            
            # Ensure we have at least max_columns - 1 headers
            while len(standard_headers) < max_columns - 1:
                standard_headers.append(f"Column {len(standard_headers) + 1}")
            
            # Print table header
            print("\n" + "-" * 80)
            header_row = ["기업명"] + standard_headers[:max_columns - 1]
            
            # Print header
            header_str = " | ".join(f"{h:30}" for h in header_row)
            print(header_str)
            print("-" * 80)
            
            # Print data rows
            for row_data in all_rows:
                row_values = [row_data['company_name'] or 'N/A']
                # Add wds-h4ga6o values (up to max_columns - 1)
                for i in range(max_columns - 1):
                    if i < len(row_data['values']):
                        value = str(row_data['values'][i])[:50]  # Truncate long values
                        row_values.append(value)
                    else:
                        row_values.append('')
                
                row_str = " | ".join(f"{str(v):30}" for v in row_values)
                print(row_str)
            
            print("-" * 80)
            
            # Create DataFrame
            print("\nCreating DataFrame...")
            df_data = []
            for row_data in all_rows:
                row_dict = {'기업명': row_data['company_name'] or 'N/A'}
                # Add columns with wds-17nsd6i as headers and wds-h4ga6o as values
                for i in range(max_columns - 1):
                    header = standard_headers[i] if i < len(standard_headers) else f"Column {i+1}"
                    value = row_data['values'][i] if i < len(row_data['values']) else ''
                    row_dict[header] = value
                df_data.append(row_dict)
            
            # Create DataFrame
            df = pd.DataFrame(df_data)
            
            # Display DataFrame info
            print(f"DataFrame created with shape: {df.shape}")
            print(f"Columns: {list(df.columns)}")
            
            # Save to Excel
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            excel_filename = f"wanted_company_data_{timestamp}.xlsx"
            print(f"\nSaving to Excel file: {excel_filename}")
            
            try:
                df.to_excel(excel_filename, index=False, engine='openpyxl')
                print(f"✓ Successfully saved to {excel_filename}")
            except Exception as e:
                print(f"✗ Error saving to Excel: {e}")
                print("Trying to install openpyxl...")
                import subprocess
                import sys
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "openpyxl"])
                    df.to_excel(excel_filename, index=False, engine='openpyxl')
                    print(f"✓ Successfully saved to {excel_filename}")
                except Exception as e2:
                    print(f"✗ Failed to save Excel file: {e2}")
                    print("Saving as CSV instead...")
                    csv_filename = f"wanted_company_data_{timestamp}.csv"
                    df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
                    print(f"✓ Saved as CSV: {csv_filename}")
            
            # Summary
            print("\n" + "=" * 80)
            print("SUMMARY")
            print("=" * 80)
            print(f"Total company profiles processed: {len(all_extracted_data)}")
            print(f"Companies with data-company-name: {sum(1 for d in all_extracted_data if d.get('company_name'))}")
            print(f"Companies with wds-17nsd6i data: {sum(1 for d in all_extracted_data if d.get('wds_17nsd6i_data'))}")
            print(f"Companies with wds-h4ga6o data: {sum(1 for d in all_extracted_data if d.get('wds_h4ga6o_data'))}")
            print(f"\nDataFrame saved to: {excel_filename}")
            
        else:
            print("No company profile links were found.")
            print("\nPossible reasons:")
            print("1. The page structure might have changed")
            print("2. The class name 'JobCard_JobCard__aVx71' might be different")
            print("3. The page might require additional scrolling or interaction")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            input("\nPress Enter to close the browser...")  # Keep browser open for inspection
            driver.quit()
            print("WebDriver closed.")

if __name__ == "__main__":
    main()

