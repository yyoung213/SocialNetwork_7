import time
import pandas as pd
import re
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

def extract_company_profile_links(driver, url, max_links=30):
    """
    Extract company profile links from the Wanted homepage
    
    Args:
        driver: Selenium WebDriver instance
        url: The URL to access
        max_links: Maximum number of links to extract (default: 30)
    
    Returns:
        List of company profile URLs
    """
    print(f"Accessing URL: {url}")
    driver.get(url)
    time.sleep(3)
    
    company_links = []
    
    try:
        # Wait for initial JobCard elements to appear
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "JobCard_JobCard__aVx71"))
        )
        
        # Scroll and load more content until we have enough links
        print(f"Scrolling to load more companies (target: {max_links} links)...")
        scroll_attempts = 0
        max_scroll_attempts = 10  # Maximum number of scroll attempts
        last_count = 0
        no_change_count = 0
        
        while len(company_links) < max_links and scroll_attempts < max_scroll_attempts:
            # Get current JobCard elements
            ad_cards = driver.find_elements(By.CLASS_NAME, "JobCard_JobCard__aVx71")
            current_count = len(ad_cards)
            
            print(f"  Scroll attempt {scroll_attempts + 1}: Found {current_count} JobCard elements")
            
            # Extract links from newly loaded cards
            for i, card in enumerate(ad_cards, 1):
                if len(company_links) >= max_links:
                    break
                    
                try:
                    link_element = card.find_element(By.TAG_NAME, "a")
                    href = link_element.get_attribute("href")
                    
                    if href:
                        # Handle relative URLs
                        if not href.startswith("http"):
                            if href.startswith("/"):
                                href = "https://www.wanted.co.kr" + href
                            else:
                                href = "https://www.wanted.co.kr/" + href
                        
                        # Add link if not already in list
                        if href not in company_links:
                            company_links.append(href)
                            if len(company_links) <= max_links:
                                print(f"    [{len(company_links)}/{max_links}] Found link: {href}")
                            
                except (NoSuchElementException, Exception):
                    continue
            
            # Check if we have enough links
            if len(company_links) >= max_links:
                print(f"  ✓ Collected {len(company_links)} links. Stopping scroll.")
                break
            
            # Check if new content was loaded
            if current_count == last_count:
                no_change_count += 1
                if no_change_count >= 2:  # If no change for 2 consecutive scrolls, stop
                    print(f"  ⚠ No new content loaded. Stopping scroll.")
                    break
            else:
                no_change_count = 0
                last_count = current_count
            
            # Scroll down to load more content
            # Scroll to the last visible card to trigger loading
            if ad_cards:
                try:
                    # Scroll to the last card
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", ad_cards[-1])
                    time.sleep(1)
                    
                    # Additional scroll to ensure trigger
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)  # Wait for new content to load
                except Exception as e:
                    print(f"  Warning: Error during scroll: {e}")
            
            scroll_attempts += 1
        
        # Final extraction to ensure we have all links
        if len(company_links) < max_links:
            print(f"  Final extraction: Collecting remaining links...")
            ad_cards = driver.find_elements(By.CLASS_NAME, "JobCard_JobCard__aVx71")
            for card in ad_cards:
                if len(company_links) >= max_links:
                    break
                try:
                    link_element = card.find_element(By.TAG_NAME, "a")
                    href = link_element.get_attribute("href")
                    if href:
                        if not href.startswith("http"):
                            if href.startswith("/"):
                                href = "https://www.wanted.co.kr" + href
                            else:
                                href = "https://www.wanted.co.kr/" + href
                        if href not in company_links:
                            company_links.append(href)
                except:
                    continue
        
        print(f"\nTotal unique links collected: {len(company_links)}")
        
    except TimeoutException:
        print("Timeout: JobCard elements not found.")
        print("Trying alternative method...")
        
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
    
    # Limit to max_links
    return company_links[:max_links]

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
        - category_data: Dictionary with keys '주요업무', '자격요건', '우대사항' and their corresponding values
    """
    print(f"\n  Visiting: {company_url}")
    
    result = {
        'url': company_url,
        'company_name': None,  # data-company-name attribute value
        'category_data': {}  # Dictionary: {'주요업무': value, '자격요건': value, '우대사항': value}
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
        button_clicked = False
        try:
            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "wds-j7905l"))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
            time.sleep(1)
            
            initial_elements_count = len(driver.find_elements(By.CLASS_NAME, "wds-17nsd6i")) + \
                                   len(driver.find_elements(By.CLASS_NAME, "wds-h4ga6o"))
            
            button.click()
            button_clicked = True
            print(f"    Button clicked successfully.")
            
        except Exception as e:
            print(f"    Warning: Could not find or click the button: {e}")
            initial_elements_count = 0
        
        # Wait for content to load after clicking
        if button_clicked:
            try:
                WebDriverWait(driver, 10).until(
                    lambda d: len(d.find_elements(By.CLASS_NAME, "wds-17nsd6i")) + 
                             len(d.find_elements(By.CLASS_NAME, "wds-h4ga6o")) > initial_elements_count
                )
                print(f"    Content loaded successfully.")
            except TimeoutException:
                time.sleep(2)  # Fallback wait
            
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(1)
        
        # Extract company name
        try:
            company_name_element = driver.find_element(By.CSS_SELECTOR, "[data-company-name]")
            result['company_name'] = company_name_element.get_attribute("data-company-name")
            if result['company_name']:
                print(f"    Found company name: {result['company_name']}")
        except Exception:
            pass
        
        # Extract data using content-based paired extraction with early exit optimization
        # Target categories to extract
        target_categories = {'주요업무', '자격요건', '우대사항'}  # Use set for O(1) lookup
        found_categories = set()  # Track which categories we've found
        
        # Get all elements of both classes
        elements_17nsd6i = driver.find_elements(By.CLASS_NAME, "wds-17nsd6i")
        elements_h4ga6o = driver.find_elements(By.CLASS_NAME, "wds-h4ga6o")
        
        print(f"    Found {len(elements_17nsd6i)} 'wds-17nsd6i' elements")
        print(f"    Found {len(elements_h4ga6o)} 'wds-h4ga6o' elements")
        
        # Extract pairs based on content matching - process sequentially with early exit
        # Use JavaScript to find the corresponding wds-h4ga6o element for each matching wds-17nsd6i
        for label_element in elements_17nsd6i:
            # Early exit: if we've found all target categories, stop processing
            if found_categories == target_categories:
                print(f"    ✓ All target categories found. Stopping early.")
                break
            
            label_text = label_element.text.strip()
            
            # Check if this label matches one of our target categories
            if label_text in target_categories:
                # Skip if we've already found this category
                if label_text in found_categories:
                    continue
                
                # Find the corresponding value element (wds-h4ga6o) using JavaScript
                # This finds the closest wds-h4ga6o element that appears after this label in the DOM
                value_text = driver.execute_script("""
                    var label = arguments[0];
                    var allH4ga6o = document.getElementsByClassName('wds-h4ga6o');
                    var labelRect = label.getBoundingClientRect();
                    var closest = null;
                    var minDistance = Infinity;
                    
                    for (var i = 0; i < allH4ga6o.length; i++) {
                        var h4Rect = allH4ga6o[i].getBoundingClientRect();
                        // Check if h4ga6o is below the label (appears after in DOM)
                        if (h4Rect.top >= labelRect.top) {
                            // Calculate distance (prefer elements that are close vertically)
                            var distance = Math.abs(h4Rect.top - labelRect.bottom);
                            if (distance < minDistance) {
                                minDistance = distance;
                                closest = allH4ga6o[i];
                            }
                        }
                    }
                    return closest ? closest.textContent.trim() : null;
                """, label_element)
                
                # If we found a value, store the pair
                if value_text:
                    result['category_data'][label_text] = value_text
                    found_categories.add(label_text)  # Mark this category as found
                    print(f"    ✓ Extracted pair: '{label_text}' -> {len(value_text)} chars")
                else:
                    print(f"    ⚠ Could not find corresponding value for '{label_text}'")
        
        print(f"    Extracted {len(result['category_data'])} category pairs")
        
    except Exception as e:
        print(f"    Error accessing company profile page: {e}")
        import traceback
        traceback.print_exc()
    
    return result

def preprocess_text_data(result_df):
    """
    Preprocess text data in the DataFrame
    
    Args:
        result_df: pandas DataFrame with columns ['기업명', '주요업무', '자격요건', '우대사항']
    
    Returns:
        pandas DataFrame with preprocessed text data
    """
    # Create a copy to avoid modifying original
    df = result_df.copy()
    
    # Columns to preprocess (exclude '기업명' as it's already clean)
    text_columns = ['주요업무', '자격요건', '우대사항']
    
    for col in text_columns:
        if col not in df.columns:
            continue
        
        # Convert to string and handle NaN
        df[col] = df[col].astype(str)
        
        # Apply preprocessing to each cell
        df[col] = df[col].apply(lambda x: preprocess_single_text(x))
    
    return df

def preprocess_single_text(text):
    """
    Preprocess a single text string
    
    Args:
        text: String to preprocess
    
    Returns:
        Preprocessed string
    """
    # Handle NaN and None
    if pd.isna(text) or text == 'nan' or text == 'None':
        return ''
    
    # Convert to string if not already
    text = str(text)
    
    # 1. Handle NaN string representation
    if text.lower() in ['nan', 'none', 'null']:
        return ''
    
    # 2. Remove leading and trailing whitespace
    text = text.strip()
    
    # 3. Normalize multiple spaces to single space
    text = re.sub(r' +', ' ', text)
    
    # 4. Normalize line breaks and tabs
    text = re.sub(r'[\r\n\t]+', ' ', text)
    
    # 5. Normalize bullet points
    # Replace various bullet point styles with standard bullet
    text = re.sub(r'^(\d+)\.\s*', r'• ', text, flags=re.MULTILINE)  # "1. " -> "• "
    text = re.sub(r'^(\d+)\)\s*', r'• ', text, flags=re.MULTILINE)  # "1) " -> "• "
    text = re.sub(r'^■\s*', '• ', text, flags=re.MULTILINE)  # "■ " -> "• "
    text = re.sub(r'^\*\s*', '• ', text, flags=re.MULTILINE)  # "* " -> "• "
    text = re.sub(r'^·\s*', '• ', text, flags=re.MULTILINE)  # "· " -> "• "
    
    # 6. Normalize bullet point separators in the middle of text
    # Replace "  • " or " • " patterns with consistent " • "
    text = re.sub(r'\s+•\s+', ' • ', text)
    
    # 7. Add space after bullet if missing
    text = re.sub(r'•([^\s])', r'• \1', text)
    
    # 8. Normalize multiple spaces again (after bullet processing)
    text = re.sub(r' +', ' ', text)
    
    # 9. Add period at the end if missing (for better readability)
    # Only if text is not empty and doesn't end with punctuation
    if text and not re.search(r'[.!?。]$', text):
        # Don't add period if it ends with bullet point
        if not text.endswith('•'):
            text = text.rstrip() + '.'
    
    # 10. Final strip
    text = text.strip()
    
    return text

def main():
    """Main function - Extract company profile links and retrieve data from each"""
    url = input("Please enter the Wanted.co.kr URL you want to access: ").strip()
    
    if not url:
        print("No URL provided. Using default URL for testing...")
        url = "https://www.wanted.co.kr"
    
    print("=" * 60)
    print("Step 1: Extracting Top 30 Company Profile Links")
    print("=" * 60)
    
    driver = None
    all_extracted_data = []
    
    try:
        # Setup WebDriver
        driver = setup_driver()
        
        # Extract company profile links
        company_links = extract_company_profile_links(driver, url, max_links=30)
        
        # Display links found
        print("\n" + "=" * 60)
        print("RESULTS - Top 30 Company Profile Links")
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
            
            # Prepare table data with fixed columns: ['기업명', '주요업무', '자격요건', '우대사항']
            standard_headers = ['주요업무', '자격요건', '우대사항']
            
            # Prepare table data
            all_rows = []
            for data in all_extracted_data:
                # Get company name
                company_name = data.get('company_name', 'N/A')
                
                # Get category data dictionary
                category_data = data.get('category_data', {})
                
                # Create row with fixed structure
                row_dict = {
                    'company_name': company_name,
                    '주요업무': category_data.get('주요업무', ''),
                    '자격요건': category_data.get('자격요건', ''),
                    '우대사항': category_data.get('우대사항', '')
                }
                all_rows.append(row_dict)
            
            # Print table header
            print("\n" + "-" * 80)
            header_row = ["기업명"] + standard_headers
            header_str = " | ".join(f"{h:30}" for h in header_row)
            print(header_str)
            print("-" * 80)
            
            # Print data rows
            for row_data in all_rows:
                row_values = [row_data['company_name'] or 'N/A']
                for header in standard_headers:
                    value = str(row_data.get(header, ''))[:50]  # Truncate long values
                    row_values.append(value)
                
                row_str = " | ".join(f"{str(v):30}" for v in row_values)
                print(row_str)
            
            print("-" * 80)
            
            # Create DataFrame
            print("\nCreating DataFrame...")
            df_data = []
            for row_data in all_rows:
                row_dict = {
                    '기업명': row_data['company_name'] or 'N/A',
                    '주요업무': row_data.get('주요업무', ''),
                    '자격요건': row_data.get('자격요건', ''),
                    '우대사항': row_data.get('우대사항', '')
                }
                df_data.append(row_dict)
            
            # Create DataFrame
            result_df = pd.DataFrame(df_data)
            
            # Preprocess text data
            print("\nPreprocessing text data...")
            result_df = preprocess_text_data(result_df)
            print("✓ Text preprocessing completed")
            
            # Display DataFrame info
            print(f"\nDataFrame created with shape: {result_df.shape}")
            print(f"Columns: {list(result_df.columns)}")
            
            # Summary
            print("\n" + "=" * 80)
            print("SUMMARY")
            print("=" * 80)
            print(f"Total company profiles processed: {len(all_extracted_data)}")
            print(f"Companies with data-company-name: {sum(1 for d in all_extracted_data if d.get('company_name'))}")
            print(f"Companies with category data: {sum(1 for d in all_extracted_data if d.get('category_data'))}")
            print(f"Companies with '주요업무': {sum(1 for d in all_extracted_data if d.get('category_data', {}).get('주요업무'))}")
            print(f"Companies with '자격요건': {sum(1 for d in all_extracted_data if d.get('category_data', {}).get('자격요건'))}")
            print(f"Companies with '우대사항': {sum(1 for d in all_extracted_data if d.get('category_data', {}).get('우대사항'))}")
            print(f"\nDataFrame stored in variable: result_df")
            
            # Ask user if they want to save to Excel
            print("\n" + "=" * 80)
            save_option = input("Do you want to save result_df to Excel file? (y/n): ").strip().lower()
            
            if save_option == 'y' or save_option == 'yes':
                try:
                    from ExcelExtraction import save_to_excel
                    filename = save_to_excel(result_df)
                    if filename:
                        print(f"\n✓ Data successfully saved to: {filename}")
                except ImportError:
                    print("\n⚠ Warning: Could not import ExcelExtraction module.")
                    print("  You can manually save using: from ExcelExtraction import save_to_excel")
                except Exception as e:
                    print(f"\n⚠ Error saving to Excel: {e}")
            else:
                print("\nSkipping Excel export. You can save later using:")
                print("  from ExcelExtraction import save_to_excel")
                print("  save_to_excel(result_df)")
            
            return result_df
            
        else:
            print("No company profile links were found.")
            print("\nPossible reasons:")
            print("1. The page structure might have changed")
            print("2. The class name 'JobCard_JobCard__aVx71' might be different")
            print("3. The page might require additional scrolling or interaction")
            return None
        
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    finally:
        if driver:
            input("\nPress Enter to close the browser...")  # Keep browser open for inspection
            driver.quit()
            print("WebDriver closed.")

if __name__ == "__main__":
    main()

