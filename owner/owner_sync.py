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
from pyvirtualdisplay import Display

def sync(phone_number):
    display = Display(visible=0, size=(800, 600))
    display.start()

    options = webdriver.ChromeOptions()
    #options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('disable-infobars')
    options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36")
    loc=os.getcwd()
    options.add_extension(loc+"/extensions/extension_0_7_0_0.crx")
    loc=os.getcwd()
    serv=Service("%s/path/chromedriver"%loc)
    driver = webdriver.Chrome(options=options,service=serv)
    phone_number=phone_number.split("+")
    phone_number=phone_number[1]
    driver.get("https://sync.me/search/?number=%s"%(phone_number))
    time.sleep(2)

    #/html/body/div/div/div[1]


    WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR,"iframe[name^='a-'][src^='https://www.google.com/recaptcha/api2/anchor?']")))
    time.sleep(2)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="recaptcha-anchor"]/div[1]'))).click()
    time.sleep(1)
    driver.switch_to.default_content()
    WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR,"iframe[title='recaptcha challenge']")))
    time.sleep(2)
    try:
        while True:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button#solver-button"))).click()
            output=WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div/div[1]'))).text
            time.sleep(1)
            if output=="Multiple correct solutions required - please solve more.":
                driver.switch_to.default_content()
                WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR,"iframe[title='recaptcha challenge']")))
                time.sleep(2)
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button#solver-button"))).click()
                output=WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div/div[1]'))).text
            else:
                continue
    except:
        pass


    #/html/body/div[1]/main/div[2]/div[1]/figure/div/div/div[2]
    #/html/body/div[1]/main/div[2]/div[1]/figure/div/div/div[2]/a
    #/html/body/div[1]/main/div[2]/div[1]/figure/div/div/div[2]
    try:
        driver.switch_to.default_content()
        output1=WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/main/div[2]/div[1]/figure/div/div/div[2]'))).text
        if output1=="No match found":
            print(colored.red("[-]Owner Sync Name:"+output1))
        else:
            print(colored.green("[+]Owner Sync Name:"+output1))
    except:
        print(colored.red("[-]Recaptcha Error Please Change Your Ip Or Reset Your Modem And Try To Run It Again!"))


#
