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

def download_latest_driver():
    # get the latest chrome driver version number
    url = 'https://chromedriver.storage.googleapis.com/LATEST_RELEASE'
    response = requests.get(url)
    version_number = response.text
    
    # build the donwload url
    download_url = "https://chromedriver.storage.googleapis.com/" + version_number +"/chromedriver_win32.zip"
    
    # download the zip file using the url built above
    latest_driver_zip = wget.download(download_url,'chromedriver.zip')
    downloads = os.path.join(os.getenv('USERPROFILE'),'Downloads')
    # extract the zip file
    with zipfile.ZipFile(latest_driver_zip, 'r') as zip_ref:
        zip_ref.extractall(downloads) # you can specify the destination folder path here
    # delete the zip file downloaded above
    os.remove(latest_driver_zip)
    return os.path.join(downloads,'chromedriver.exe')
# download_latest_driver()
# downloads = os.path.join(os.getenv('USERPROFILE'),'Downloads')
# driver_path = os.path.join(downloads,'chromedriver.exe')

def get_chrome_options(*options):
    chrome_options = webdriver.ChromeOptions()
    for opt in options:
        chrome_options.add_argument(opt)
    return chrome_options
def default_options():
    # options = webdriver.ChromeOptions()
    # options.add_argument('--ignore-certificate-errors')
    # options.add_argument("--test-type")
    # options.add_argument("--headless")
    return get_chrome_options('--ignore-certificate-errors')
def start_driver():
    '''
    Initialize Chrome driver
    '''
    options = default_options()
    #options.binary_location = "/usr/bin/chromium"
    driver = webdriver.Chrome(options=options)
    return driver

class AmazonDriver(webdriver.Chrome):
    def __init__(self,chrome_options):
        super().__init__(options=chrome_options)
    def get_listing(self,asin):
        url = f'https://www.amazon.com/dp/{asin}'
        self.asin = asin
        self.get(url)
        self.continue_shopping()
    def continue_shopping(self):
        '''
        Click continue shopping button if present
        '''
        try:
            shopping_button = WebDriverWait(driver,3).until(EC.element_to_be_clickable((By.CLASS_NAME,'a-button-text')))
            if shopping_button.text == 'Continue shopping':
                shopping_button.click()
        except TimeoutException:
            pass
    def get_by_xpath(self,xpath):
        '''
        Get Text by XPATH
        '''
        return driver.find_element(By.XPATH,xpath).text
    def get_title(self):
        return self.find_element(By.ID,'title').text
    def get_price(self):
        classes = ["a-price-whole","a-price-fraction"]
        price = []
        for c in classes:
            price.append(self.find_element(By.CLASS_NAME,c).text)
        return '.'.join(price)
    def get_list_price(self):
        list_price = self.get_by_xpath('//*[@id="corePriceDisplay_desktop_feature_div"]/div[2]/span/span[1]/span[2]/span')
        return re.sub(r'[$,]','',list_price)
    def get_discount(self):
        return self.get_by_xpath('//*[@id="corePriceDisplay_desktop_feature_div"]/div[1]/span[2]')
    def get_raiting(self):
        return self.get_by_xpath('//*[@id="acrPopover"]/span[1]/a/span')
    def get_raiting_count(self):
        raitings = self.get_by_xpath('//*[@id="acrCustomerReviewText"]')
        try:
            raiting_count = re.search(r'(\d+)')[0]
            return raiting_count
        except:
            return raitings
    def get_ships_from(self):
        return self.get_by_xpath('//*[@id="fulfillerInfoFeature_feature_div"]/div[2]/div[1]/span')
    def get_sold_by(self):
        return self.get_by_xpath('//*[@id="merchantInfoFeature_feature_div"]/div[2]/div[1]/span')
    def get_bullet_points(self):
        bullet_elm = self.find_element(By.XPATH,'//*[@id="feature-bullets"]/ul')
        bullets = bullet_elm.find_elements(By.CLASS_NAME,'a-list-item')
        return [b.text for b in bullets]
    def get_product_overview(self):
        prod_ov = self.find_element(By.XPATH,'//*[@id="productOverview_feature_div"]/div')
        return prod_ov.text.split('\n')
    def get_product_details_tech_spec(self):
        # tech_spec_table = self.find_element(By.XPATH,'//*[@id="productDetails_techSpec_section_1"]')
        # tech_spec_table = driver.find_element(By.XPATH,'//*[@id="productDetails_techSpec_section_1"]/tbody')
        # print(tech_spec_table.text)
        tech_spec_key = 'prodDetSectionEntry'#"a-color-secondary a-size-base prodDetSectionEntry"
        tech_spec_val = 'prodDetAttrValue'# "a-size-base prodDetAttrValue"
        keys = driver.find_elements(By.CLASS_NAME,tech_spec_key)
        print(keys)
        values = driver.find_elements(By.CLASS_NAME,tech_spec_val)
        print(values)
        tech_specs= {}
        for i in range(len(keys)):
            try:
                tech_specs[keys[i].text] = values[i].text
            except IndexError:
                break
        return tech_specs
    def extract_data(self):
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
                    'product_overview' : self.get_product_overview}
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
    with open(f"{data['asin']}.json",'w') as fp:
        json.dump(data,fp)

def read_file(path):
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
    return data.values()
def parse_arguments():
    parser = argparse.ArgumentParser(description='Command line arguments to pass to AmazonDriver')
    parser.add_argument('-a','--asins',action='append',type='string')
    parser.add_argument('-f','--file',action='store',type='string',help='Must contain a single column of ASINs with the column header ASIN')
    parser.add_argument('-o','--options',action='append')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()
    if args.asin:
        options = default_options() if not args.options else get_chrome_options(args.options)
        with AmazonDriver(options) as driver:
            driver.implicitly_wait(3)
            for asin in args.asins:
                driver.get_listing(asin)
                data = driver.extract_data()
                save_data(data)
    


