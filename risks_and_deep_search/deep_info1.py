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
from clint.textui import colored
import undetected_chromedriver as uc

def deep_one(phone_number):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('disable-infobars')
    options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36")
    loc = os.getcwd()
    driver = uc.Chrome(options=options)
    driver.get("https://www.duckduckgo.com/")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div[2]/div/div[1]/div[2]/form/input[1]"))).send_keys(phone_number)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div[2]/div/div[1]/div[2]/form/input[2]'))).click()
    try:
        for x in range(0,30):
            xpath='//*[@id="r1-%s"]/div/div[1]/div/a'%x
            name=WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath))).text
            print(colored.green("[+]This Link Could Be Relevant With Your Number:"), end="")
            print(colored.blue(name))
    except:
        pass
