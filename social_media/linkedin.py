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
name=""
linkedin_load_balancer=False
def lnkd(phone_number):
    global name
    global linkedin_load_balancer
    linkedin_load_balancer=True
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('disable-infobars')
    options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36")
    loc=os.getcwd()
    driver = uc.Chrome(options=options)
    driver.get("https://www.linkedin.com/login")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "username"))).send_keys(phone_number)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "password"))).send_keys("sametcarleone")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/main/div[2]/div[1]/form/div[3]/button'))).click()
    try:
        name=WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "error-for-password"))).text
        if name == "That’s not the right password. Forgot password?":
            
            name=WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "error-for-password"))).text
            name="This Phone Number Is  Connected To A Linkedin Account!"
            print(colored.green("[+]")+colored.blue(name))
        else:
            name="This Phone Number Is Not Connected To Any Linkedin Account!"
            print(colored.magenta("[-]")+colored.red(name))
    except:
        name="This Phone Number Is Not Connected To Any Linkedin Account!"
        print(colored.magenta("[-]")+colored.red(name))
        

    linkedin_load_balancer=False
    driver.close()

