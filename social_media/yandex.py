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
name=""
yandex_load_balancer=False
def yandex(phone_number):
    global name
    global yandex_load_balancer
    yandex_load_balancer=True
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('disable-infobars')
    options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36")
    loc=os.getcwd()
    driver = uc.Chrome(options=options)
    driver.get("https://passport.yandex.com/auth/add")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "login"))).send_keys(phone_number)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div/div/div[2]/div/div/div[2]/div[3]/div/div/div/div[1]/form/div[3]/button'))).click()

    #/html/body/div[1]/div[3]/div[1]/div/div/form/div/div[2]/ul/li[1]/div/table/tbody/tr/td[1]/div/div/div/div[2]/div[1]
    try:

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, 'passwd'))).click()

        name="This Phone Number Is Connected To A Yandex Account!"
        print(colored.green("[+]")+colored.blue(name))
       

    except:
        name="This Phone Number Is Not Connected To Any Yandex Account!"
        print(colored.magenta("[-]")+colored.red(name))
    yandex_load_balancer=False
    driver.quit()

