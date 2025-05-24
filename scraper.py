from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (TimeoutException, 
                                      NoSuchElementException,
                                      InvalidSessionIdException,
                                      WebDriverException)
from webdriver_manager.chrome import ChromeDriverManager
import csv
import time
import random

# Configuration
MAX_MOVIES = 4000
CSV_FILE = "imdb_2024_movies.csv"
LOAD_MORE_SELECTOR = "button.ipc-see-more__button"
BASE_URL = "https://www.imdb.com/search/title/?title_type=feature&release_date=2024-01-01,2024-12-31&count=250"
MAX_RETRIES = 3
RETRY_DELAY = 5

def setup_driver():
    """Configure Chrome with anti-detection settings"""
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def human_like_scroll(driver):
    """Simulate human scrolling patterns"""
    for _ in range(random.randint(2, 4)):
        scroll_height = random.randint(500, 1500)
        driver.execute_script(f"window.scrollBy(0, {scroll_height});")
        time.sleep(random.uniform(0.5, 1.5))

def safe_click(driver, element):
    """Click with multiple fallback strategies"""
    try:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", element)
        time.sleep(1)
        ActionChains(driver).move_to_element(element).click().perform()
        return True
    except Exception as e:
        print(f"⚠️ Click failed (method 1): {str(e)[:100]}")
        try:
            driver.execute_script("arguments[0].click();", element)
            return True
        except Exception as e:
            print(f"⚠️ Click failed (method 2): {str(e)[:100]}")
            return False

def check_session(driver):
    """Verify if session is still valid"""
    try:
        driver.execute_script("return document.readyState;")
        return True
    except:
        return False

def recover_session(driver, url):
    """Attempt to recover a broken session"""
    try:
        driver.refresh()
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".ipc-metadata-list-summary-item"))
        )
        return True
    except:
        try:
            driver.quit()
            driver = setup_driver()
            driver.get(url)
            return True
        except:
            return False

def extract_movie_data(driver, container):
    """Robust data extraction with error recovery"""
    try:
        if not check_session(driver):
            if not recover_session(driver, BASE_URL):
                raise InvalidSessionIdException("Session recovery failed")

        # Title extraction
        title = container.find_element(By.CSS_SELECTOR, ".ipc-title__text").text
        title = title.split('. ', 1)[-1].strip()
        
        # Storyline extraction with fallbacks
        storyline = "No description available"
        for selector in [".ipc-html-content-inner-div", 
                        ".ipc-html-content--base",
                        ".sc-466bb6c-0"]:
            try:
                text = container.find_element(By.CSS_SELECTOR, selector).text.strip()
                if text: 
                    storyline = text
                    break
            except:
                continue
                
        return title, storyline
        
    except Exception as e:
        print(f"⚠️ Extraction error: {str(e)[:100]}")
        return None, None

def save_progress(movies, filename):
    """Periodically save results"""
    try:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Title", "Storyline"])
            writer.writerows(movies)
        print(f"💾 Saved {len(movies)} movies")
    except Exception as e:
        print(f"❌ Save failed: {str(e)}")

def scrape_page(driver):
    """Scrape all movies on current page"""
    try:
        WebDriverWait(driver, 25).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".ipc-metadata-list-summary-item"))
        )
        human_like_scroll(driver)
        
        containers = driver.find_elements(By.CSS_SELECTOR, ".ipc-metadata-list-summary-item")
        return containers
    except Exception as e:
        print(f"⚠️ Page scrape failed: {str(e)[:100]}")
        return []

def main():
    attempt = 0
    driver = None
    all_movies = []
    
    while attempt < MAX_RETRIES:
        try:
            print(f"\n=== Attempt {attempt + 1}/{MAX_RETRIES} ===")
            driver = setup_driver()
            driver.get(BASE_URL)
            time.sleep(3)
            
            while len(all_movies) < MAX_MOVIES:
                # Scrape current page
                containers = scrape_page(driver)
                if not containers:
                    break
                    
                # Process movies
                new_movies = []
                for container in containers:
                    title, storyline = extract_movie_data(driver, container)
                    if title and title not in [m[0] for m in all_movies]:
                        new_movies.append([title, storyline])
                
                if new_movies:
                    all_movies.extend(new_movies)
                    print(f"✅ Added {len(new_movies)} | Total: {len(all_movies)}")
                    
                    # Periodic save
                    if len(all_movies) % 250 == 0:
                        save_progress(all_movies, CSV_FILE)
                else:
                    print("⚠️ No new movies found")
                
                # Pagination
                if len(all_movies) >= MAX_MOVIES:
                    break
                    
                try:
                    button = WebDriverWait(driver, 15).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, LOAD_MORE_SELECTOR))
                    )
                    if not safe_click(driver, button):
                        raise Exception("Click failed")
                    time.sleep(random.uniform(2, 4))
                except:
                    print("🚫 Pagination failed")
                    break
            
            # Success - exit retry loop
            break
            
        except (InvalidSessionIdException, WebDriverException) as e:
            print(f"🚨 Session crash: {str(e)[:100]}")
            attempt += 1
            if driver: driver.quit()
            time.sleep(RETRY_DELAY)
            
        except Exception as e:
            print(f"❌ Critical error: {str(e)}")
            break
            
    # Final save
    save_progress(all_movies, CSV_FILE)
    if driver: driver.quit()
    print(f"\n🎬 Completed with {len(all_movies)} movies")

if __name__ == "__main__":
    main()