import csv
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

class GoogleMapScraper:
    def __init__(self):
        self.output_file_name = "google_map_business_data.csv"
        self.headless = False
        self.driver = None
        self.unique_check = []

    def config_driver(self):
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument("--headless")
            options.add_argument('--ignore-ssl-errors=yes')
            options.add_argument('--ignore-certificate-errors')

        s = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=s, options=options)
        self.driver = driver

    def load_companies(self, url):
        print("Getting business info", url)
        self.driver.get(url)
        time.sleep(5)
        panel_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[4]'
        scrollable_div = self.driver.find_element(By.XPATH, panel_xpath)
        
        flag = True
        i = 0
        while flag:
            print(f"Scrolling to page {i + 2}")
            self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + 6500', scrollable_div)
            time.sleep(2)

            if "You've reached the end of the list." in self.driver.page_source:
                flag = False

            self.get_business_info()
            i += 1

    def get_business_info(self):
        # Add a wait time before starting to scrape the business info
        WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'jJc9Ad')))
        
        try:
            for business in self.driver.find_elements(By.CLASS_NAME, 'jJc9Ad'):
                name = business.find_element(By.CLASS_NAME, 'd4r55').text
                review = business.find_element(By.CLASS_NAME, 'wiI7pd').text
                
                # Adding waits before getting rating and date elements
                rating_element = WebDriverWait(business, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'fzvQIb')))
                rating = rating_element.text
                
                date_element = WebDriverWait(business, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'xRkPPb')))
                date = date_element.text.split(", ")[1]

                print(name)
                print(date)

                unique_id = "".join([name, rating, review, date])
                if unique_id not in self.unique_check:
                    data = [name, rating, review, date]
                    self.save_data(data)
                    self.unique_check.append(unique_id)

                    print(unique_id)
                    
        except NoSuchElementException as e:
            print(f"An error occurred: {e}")

    def save_data(self, data):
        header = ['ID','Client_Name','Rating','Reviews','Date']
        file_exists = os.path.isfile(self.output_file_name)
        with open(self.output_file_name, 'a', newline='', encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            if not file_exists:
                writer.writerow(header)
            writer.writerow([len(self.unique_check)] + data)


url = " "


business_scraper = GoogleMapScraper()
business_scraper.config_driver()
business_scraper.load_companies(url)
