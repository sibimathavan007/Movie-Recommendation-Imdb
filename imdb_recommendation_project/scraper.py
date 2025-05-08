from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time

# Setup Chrome driver
options = Options()
options.add_argument("--start-maximized")

driver_path = r"C:\Users\HP\Downloads\imdb_recommendation_project\chromedriver.exe"
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=options)

url = "https://www.imdb.com/search/title/?year=2024&genres=drama&sort=year,desc"
driver.get(url)

# Wait for movie results to load
WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.CLASS_NAME, "ipc-metadata-list-summary-item"))
)

movies = []
movie_items = driver.find_elements(By.CLASS_NAME, "ipc-metadata-list-summary-item")

for item in movie_items[:10]:  # <-- LIMIT to 10 movies
    try:
        title_element = item.find_element(By.CLASS_NAME, "ipc-title__text")
        title = title_element.text.strip()

        link_element = item.find_element(By.TAG_NAME, "a")
        movie_link = link_element.get_attribute("href")

        # Open movie detail page in new tab
        driver.execute_script("window.open(arguments[0]);", movie_link)
        driver.switch_to.window(driver.window_handles[1])

        # Wait and scrape storyline
        try:
            storyline_elem = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//span[@data-testid='plot-xl']"))
            )
            storyline = storyline_elem.text.strip()
        except:
            storyline = "N/A"

        movies.append([title, storyline])
        print(f"🎬 {title}\n📖 {storyline}\n")

        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    except Exception as e:
        print(f"❌ Error processing a movie: {e}")
        continue

# Save to CSV
csv_file = "movies_2024.csv"
with open(csv_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Movie Name", "Storyline"])
    writer.writerows(movies)

print("\n✅ Final CSV saved successfully.")
driver.quit()
