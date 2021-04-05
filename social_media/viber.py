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
def viber(phone_number):

    options = webdriver.ChromeOptions()
    #options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('disable-infobars')
    options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36")
    loc=os.getcwd()
    serv=Service("%s/path/chromedriver"%loc)
    driver = webdriver.Chrome(options=options,service=serv)
    driver.get("https://account.viber.com/en/login")
    #/html/body/div/div/div[3]/section/div/div[1]/div[2]/div/div[3]/form/div[1]/div[2]/div/input[1]
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div[1]/div[2]/div/div[3]/form/div[1]/div[2]/div/input[1]'))).clear()
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div[1]/div[2]/div/div[3]/form/div[1]/div[2]/div/input[1]'))).send_keys(phone_number)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div/div[3]/section/div/div[1]/div[2]/div/div[3]/form/div[2]/div[1]/input"))).send_keys("thiswill123notbeyourpasswordihope")
    #/html/body/div[1]/section/main/article/div[2]/div[1]/div/form/div[4]/button
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div/div[3]/section/div/div[1]/div[2]/div/div[3]/form/div[3]/button"))).click()
    try:
        name=WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div/div[3]/section/div/div[1]/div[2]/div/div[3]/form/div[1]/div[2]/div[2]"))).text
        if name=="The number you entered doesn't appear to be valid. Please check the number and try again.":
            country_code=phone_number[3::]
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div/div[3]/section/div/div[1]/div[2]/div/div[3]/form/div[1]/div[2]/div/input[1]"))).send_keys(country_code)
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div/div[3]/section/div/div[1]/div[2]/div/div[3]/form/div[2]/div[1]/input"))).send_keys("thiswill123notbeyourpasswordihope")
            #/html/body/div[1]/section/main/article/div[2]/div[1]/div/form/div[4]/button
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div/div[3]/section/div/div[1]/div[2]/div/div[3]/form/div[3]/button"))).click()
            name=WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div/div[3]/section/div/div[1]/div[2]/div/div[3]/form/div[1]/div[2]/div[2]"))).text
            if name=="The number you entered doesn't appear to be valid. Please check the number and try again.":
                country_code=phone_number[4::]
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div/div[3]/section/div/div[1]/div[2]/div/div[3]/form/div[1]/div[2]/div/input[1]"))).send_keys(country_code)
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div/div[3]/section/div/div[1]/div[2]/div/div[3]/form/div[2]/div[1]/input"))).send_keys("thiswill123notbeyourpasswordihope")
                #/html/body/div[1]/section/main/article/div[2]/div[1]/div/form/div[4]/button
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div/div[3]/section/div/div[1]/div[2]/div/div[3]/form/div[3]/button"))).click()
                name=WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div/div[3]/section/div/div[1]/div[2]/div/div[3]/form/div[1]/div[2]/div[2]"))).text
            elif name=="Your phone number or password was incorrect. Please try again.":
                print(colored.red("[-]This Phone Number Is Not Connected To Any Viber Account!"))
                with open("output/social_media_results.txt","a+") as file:
                    file.write("\n[-]This Phone Number Is Not Connected To Any Viber Account!"+"\n--------------------------------------------------------------")

            else:
                print(colored.green("[+]This Phone Number Is Connected To A Viber Account!"))
                with open("output/social_media_results.txt","a+") as file:
                    file.write("\n[+]This Phone Number Is Connected To A Viber Account!"+"\n--------------------------------------------------------------")

        elif name=="Your phone number or password was incorrect. Please try again.":
            print(colored.red("[-]This Phone Number Is Not Connected To Any Viber Account!"))
            with open("output/social_media_results.txt","a+") as file:
                file.write("\n[-]This Phone Number Is Not Connected To Any Viber Account!"+"\n--------------------------------------------------------------")

        else:
            print(colored.green("[+]This Phone Number Is Connected To A Viber Account!"))
            with open("output/social_media_results.txt","a+") as file:
                file.write("\n[+]This Phone Number Is Connected To A Viber Account!"+"\n--------------------------------------------------------------")


    except:
        pass
