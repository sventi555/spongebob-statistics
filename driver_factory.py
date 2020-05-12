from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_driver(headless=True):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless')

    driver = webdriver.Chrome(options=chrome_options)
    return driver
