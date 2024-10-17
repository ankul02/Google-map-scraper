import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

class GoogleMapScraper:
    def __init__(self, chrome_browser_path, chrome_driver_path):
        self.chrome_browser_path = chrome_browser_path
        self.chrome_driver_path = chrome_driver_path
        self.chrome_options = Options()
        self.chrome_options.binary_location = self.chrome_browser_path
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--disable-hardware-acceleration")
        self.chrome_options.add_argument("--disable-accelerated-2d-canvas")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--disable-webgl")
        self.chrome_options.add_argument("--enable-logging")
        self.chrome_options.add_argument("--v=1")
        self.chrome_service = Service(executable_path=self.chrome_driver_path)
        self.driver = webdriver.Chrome(service=self.chrome_service, options=self.chrome_options)

    def search(self, query):
        self.driver.get("https://www.google.com/maps/")
        time.sleep(2)
        search_box = self.driver.find_element(By.ID, 'searchboxinput')
        search_box.send_keys(query)
        search_button = self.driver.find_element(By.XPATH, '//*[@id="searchbox-searchbutton"]/span')
        search_button.click()
        time.sleep(5)  # Wait for the search results to load

    def scroll_results(self):
        flag = True
        i = 0
        while flag:
            scrollable_div = self.driver.find_element(By.XPATH, '//*[@role="feed"]')
            self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
            time.sleep(2)  # Wait for new results to load
            if "You've reached the end of the list." in self.driver.page_source:
                flag = False
            i += 1

    def scrape_data(self):
        results = self.driver.find_elements(By.CLASS_NAME, 'hfpxzc')
        scraped_data = []

        for index, result in enumerate(results):
            try:
                result.click()  # Click on the result
                time.sleep(5)  # Wait for details to load

                # Extract Name
                try:
                    name = self.driver.find_element(By.XPATH, '//*[@class="DUwDvf lfPIob"]').text
                except:
                    name = "N/A"

                # Extract Phone
                try:
                    phone_button = self.driver.find_element(By.XPATH, '//*[@class="CsEnBe" and contains(@aria-label, "Phone")]')
                    phone_number = phone_button.get_attribute('aria-label').replace("Phone: ", "")
                except:
                    phone_number = "N/A"

                # Extract Website
                try:
                    website_button = self.driver.find_element(By.XPATH, '//*[@class="CsEnBe" and contains(@aria-label, "Website")]')
                    website_url = website_button.get_attribute('aria-label').replace("Website: ", "")
                except:
                    website_url = "N/A"

                # Extract Address
                try:
                    address_button = self.driver.find_element(By.XPATH, '//*[@class="CsEnBe" and contains(@aria-label, "Address")]')
                    address = address_button.get_attribute('aria-label').replace("Address: ", "")
                except:
                    address = "N/A"

                # Append the scraped data
                scraped_data.append({
                    'Name': name,
                    'Phone': phone_number,
                    'Website': website_url,
                    'Address': address
                })

                # Go back to the results page
                self.driver.execute_script("window.history.go(-1)")
                time.sleep(5)  # Wait for the results page to load again

            except Exception as e:
                print(f"Error clicking or scraping result {index + 1}: {str(e)}")
        
        return scraped_data

    def save_to_csv(self, data, filename):
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")

    def close(self):
        self.driver.quit()


# Usage example:
chrome_browser_path = r"D:\\my_work\\python\\google_map_scraper\\chrome-win64\\chrome.exe"
chrome_driver_path = r"D:\\my_work\\python\\google_map_scraper\\chromedriver-win64\\chromedriver.exe"

scraper = GoogleMapScraper(chrome_browser_path, chrome_driver_path)

search_query = "restaurants in kashipur uttakahand"
scraper.search(search_query)
scraper.scroll_results()

# Scrape the data and save it to a CSV
data = scraper.scrape_data()
scraper.save_to_csv(data, 'scraped_google_maps_data.csv')

# Close the driver
scraper.close()
