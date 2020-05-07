#!/usr/bin/python3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.chrome.service import Service
import requests
import subprocess
import time
import os
from bs4 import BeautifulSoup
import sys
from clint.textui import colored
import optparse
from clint.textui import colored

def lnkd(phone_number):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('disable-infobars')
    options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36")
    loc=os.getcwd()
    serv=Service("%s/path/chromedriver"%loc)
    driver = webdriver.Chrome(options=options,service=serv)
    driver.get("https://www.linkedin.com/login")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/main/div[2]/form/div[1]/input"))).send_keys(phone_number)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/main/div[2]/form/div[2]/input"))).send_keys("sametcarleone")
    time.sleep(2)

    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app__container"]/main/div[2]/form/div[3]/button'))).click()
        name=WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/main/div[2]/form/div[2]/div"))).text
        print(colored.green("[+]This Phone Number Is  Connected To A Linkedin Account!"))
        with open("output/social_media_results.txt","a+") as file:
            file.write("\n[+]This Phone Number Is Connected To A Linkedin Account!"+"\n--------------------------------------------------------------")

    except:
        print(colored.red("[-]This Phone Number Is Not Connected To Any Linkedin Account!"))
        with open("output/social_media_results.txt","a+") as file:
            file.write("\n[-]This Phone Number Is Not Connected To Any Linkedin Account!"+"\n--------------------------------------------------------------")
