from selenium import webdriver
from selenium.common.exceptions import (NoSuchElementException,
                                        TimeoutException, WebDriverException, UnexpectedAlertPresentException,
                                       ElementClickInterceptedException, ElementNotInteractableException)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
# from time import sleep
# from datetime import date, datetime, timedelta
import os
import re
# import shutil
import json
# import glob
import requests
import wget
import zipfile
import argparse
import platform


def download_latest_driver():
    """
    Download and extract the latest compatible ChromeDriver for Windows, macOS, or Linux.
    Returns the full path to the driver executable.
    """
    # Detect OS and architecture
    system = platform.system()
    machine = platform.machine()

    if system == "Windows":
        platform_key = "win32"
        driver_name = "chromedriver.exe"
    elif system == "Darwin":
        if machine == "arm64":
            platform_key = "mac-arm64"
        else:
            platform_key = "mac-x64"
        driver_name = "chromedriver"
    elif system == "Linux":
        platform_key = "linux64"
        driver_name = "chromedriver"
    else:
        raise Exception(f"Unsupported platform: {system}")

    # Get latest ChromeDriver version
    version_url = "https://chromedriver.storage.googleapis.com/LATEST_RELEASE"
    version = requests.get(version_url).text.strip()
    download_url = f"https://chromedriver.storage.googleapis.com/{version}/chromedriver_{platform_key}.zip"

    print(f"⬇️ Downloading ChromeDriver {version} for {platform_key}...")

    zip_path = "chromedriver.zip"
    wget.download(download_url, zip_path)

    # Choose destination folder
    home = os.path.expanduser("~")
    dest_dir = os.path.join(home, "chromedriver_bin")
    os.makedirs(dest_dir, exist_ok=True)

    # Extract
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(dest_dir)
    os.remove(zip_path)

    # Make executable (Unix)
    driver_path = os.path.join(dest_dir, driver_name)
    if system != "Windows":
        os.chmod(driver_path, 0o755)

    print(f"\n✅ ChromeDriver saved to: {driver_path}")
    return driver_path


def get_chrome_options(*options):
    '''
    Create ChromeOptions adding any arguments
    '''
    chrome_options = webdriver.ChromeOptions()
    for opt in options:
        chrome_options.add_argument(opt)
    return chrome_options

import random

USER_AGENTS = [
    # Windows - Chrome
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.202 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.78 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.33 Safari/537.36",

    # macOS - Chrome
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.202 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.78 Safari/537.36",

    # Linux - Chrome
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.33 Safari/537.36"
]

def default_options(proxy=None):
    '''
    Default ChromeOptions with stealth anti-detection settings
    '''
    chrome_options = webdriver.ChromeOptions()

    # Random realistic user agent
    user_agent = random.choice(USER_AGENTS)
    chrome_options.add_argument(f'user-agent={user_agent}')

    # Stealth options
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # Optional: Proxy setup
    if proxy:
        chrome_options.add_argument(f'--proxy-server=http://{proxy}')

    # Optional headless for CI
    # chrome_options.add_argument("--headless=new")

    return chrome_options

def enable_stealth(driver):
    '''
    Inject JavaScript to evade detection of Selenium
    '''
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.navigator.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
        """
    })

def start_driver():
    '''
    Initialize Chrome driver
    '''
    options = default_options()
    #options.binary_location = "/usr/bin/chromium"
    driver = webdriver.Chrome(options=options)
    enable_stealth(driver)
    return driver

class AmazonDriver(webdriver.Chrome):
    def __init__(self,chrome_options):
        '''
        ChromeDriver configured to get relevant product listing information from an Amazon listing.
        '''
        super().__init__(options=chrome_options)
        enable_stealth(self)
    def get_listing(self,asin):
        url = f'https://www.amazon.com/dp/{asin}'
        self.asin = asin
        self.get(url)
        self.continue_shopping()
    def is_captcha_page(self):
        print("⚠️ CAPTCHA detected! Try again later or switch proxy.")
        return None
    def continue_shopping(self):
        '''
        Click continue shopping button if present
        '''
        try:
            shopping_button = WebDriverWait(self,3).until(EC.element_to_be_clickable((By.CLASS_NAME,'a-button-text')))
            if shopping_button.text == 'Continue shopping':
                shopping_button.click()
        except TimeoutException:
            pass
    def get_by_xpath(self,xpath):
        '''
        Get Text by XPATH
        '''
        return self.find_element(By.XPATH,xpath).text
    def get_title(self):
        '''
        Get the product title
        '''
        return self.find_element(By.ID,'title').text
    def get_price(self):
        '''
        Get the price of the product
        '''
        classes = ["a-price-whole","a-price-fraction"]
        price = []
        for c in classes:
            price.append(self.find_element(By.CLASS_NAME,c).text)
        return '.'.join(price)
    def get_list_price(self):
        '''
        Get the list price / MSRP
        '''
        list_price = self.get_by_xpath('//*[@id="corePriceDisplay_desktop_feature_div"]/div[2]/span/span[1]/span[2]/span')
        return re.sub(r'[$,]','',list_price)
    def get_discount(self):
        '''
        Get the discount
        '''
        return self.get_by_xpath('//*[@id="corePriceDisplay_desktop_feature_div"]/div[1]/span[2]')
    def get_raiting(self):
        '''
        Get the raiting
        '''
        return self.get_by_xpath('//*[@id="acrPopover"]/span[1]/a/span')
    def get_raiting_count(self):
        '''
        Get the number of raitings
        '''
        raitings = self.get_by_xpath('//*[@id="acrCustomerReviewText"]')
        try:
            raiting_count = re.search(r'(\d+)')[0]
            return raiting_count
        except:
            return raitings
    def get_ships_from(self):
        '''
        Get the ships from provider
        '''
        return self.get_by_xpath('//*[@id="fulfillerInfoFeature_feature_div"]/div[2]/div[1]/span')
    def get_sold_by(self):
        '''
        Get the seller name
        '''
        return self.get_by_xpath('//*[@id="merchantInfoFeature_feature_div"]/div[2]/div[1]/span')
    def get_bullet_points(self):
        '''
        Get the feature bullet points
        '''
        bullet_elm = self.find_element(By.XPATH,'//*[@id="feature-bullets"]/ul')
        bullets = bullet_elm.find_elements(By.CLASS_NAME,'a-list-item')
        return [b.text for b in bullets]
    def get_product_overview(self):
        '''
        Get the product overview
        '''
        prod_ov = self.find_element(By.XPATH,'//*[@id="productOverview_feature_div"]/div')
        return prod_ov.text.split('\n')
    def get_product_details_tech_spec(self):
        '''
        Get the product details technical specifications
        '''
        tech_spec_key = 'prodDetSectionEntry'#"a-color-secondary a-size-base prodDetSectionEntry"
        tech_spec_val = 'prodDetAttrValue'# "a-size-base prodDetAttrValue"
        keys = self.find_elements(By.CLASS_NAME,tech_spec_key)
        print(keys)
        values = self.find_elements(By.CLASS_NAME,tech_spec_val)
        print(values)
        tech_specs= {}
        for i in range(len(keys)):
            try:
                tech_specs[keys[i].text] = values[i].text
            except IndexError:
                break
        return tech_specs
    def extract_data(self) -> dict:
        '''
        Get relevant listing data
        '''
        functions = {'asin':self.asin,
                    'title':self.get_title,
                    'price':self.get_price,
                    'list_price':self.get_list_price,
                    'discount':self.get_discount,
                    'raiting':self.get_raiting,
                    'raiting_count':self.get_raiting_count,
                    'ships_from':self.get_ships_from,
                    'sold_by' : self.get_sold_by,
                    'bullet_points' : self.get_bullet_points,
                    'product_overview' : self.get_product_overview,
                    'product_details_tech_spec' : self.get_product_details_tech_spec}
        data = {}
        for key,func in functions.items():
            try:
                result = func()
                data[key] = result
            except Exception as e:
                print(e)
                pass
        return data

def save_data(data):
    '''
    Save product listing data as the {ASIN}.json
    '''
    with open(f"{data['asin']}.json",'w') as fp:
        json.dump(data,fp)

        
def read_file(path) -> list:
    '''
    Read file from path accepting these file types '.csv','.txt','.xlsx','.json'
    returning a list of asins
    '''
    exts = ['.csv','.txt','.xlsx','.json']
    ext = os.path.splitext(path)[1]
    if not ext in exts:
        raise Exception("File type cannot be read")
    ext_index = exts.index(ext)
    if ext_index < 2:
        with open(path,'r',) as f:
            char = '\t' if 'txt' in ext else ','
            return [l.rstrip(char) for l in f.read()]
    elif ext_index == 2:
        from pandas import read_excel
        df = read_excel(path)
        return df.values.tolist()
    with open(path,'r') as f:
        data = json.load(f)
    return list(data.values())
def main(args):
    '''
    Main function getting each listing
    '''
    options = default_options(proxy=args.proxy) if not args.options else get_chrome_options(args.options)
    with AmazonDriver(options) as driver:
        driver.implicitly_wait(3)
        asins = args.asins if args.asins else read_file(args.file)
        for asin in asins:
            driver.get_listing(asin)
            data = driver.extract_data()
            save_data(data)
def parse_arguments():
    '''
    Parse command line arguments
    '''
    parser = argparse.ArgumentParser(description='Command line arguments to pass to AmazonDriver')
    parser.add_argument('-a','--asins',action='append',type='string')
    parser.add_argument('-f','--file',action='store',type='string',help='Must contain a single column of ASINs with the column header ASIN')
    parser.add_argument('-o','--options',action='append')
    parser.add_argument('--proxy', type=str, help='Proxy in user:pass@ip:port or ip:port format')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()
    main(args)
    


