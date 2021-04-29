#!/usr/bin/python3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.chrome.service import Service
import subprocess
import time
import os
from bs4 import BeautifulSoup
import sys
from clint.textui import colored
import optparse
import undetected_chromedriver as uc

def deep_two(phone_number):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('disable-infobars')
    options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36")
    loc = os.getcwd()
    driver = uc.Chrome(options=options)
    driver.get("https://www.unknownphone.com/")
    
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "num"))).send_keys(phone_number)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'search_submit'))).click()
    #/html/body/div[1]/div/div[1]/div[3]/div[2]/div[4]
    try:
        blocked=WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div[1]/div[3]/div[2]/div[4]/strong'))).text
        print(colored.red("[!]This Phone Number Is Blocked On unknownphone.com It Could Be A SCAM!"))
     
        time.sleep(3)

    except:

     
        time.sleep(3)
    try:
        for x in range(1,10):
            xpath='/html/body/div[1]/div/div[1]/ul/li[%s]/div/div/div/div[1]/p'%x
            name=WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath))).text
            print(colored.green("[+]Comments About This Number:"),end="")
            print(colored.blue(name))
            
    except:
        pass
