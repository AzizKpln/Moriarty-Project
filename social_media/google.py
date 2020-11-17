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
google_load_balancer=False
def gg(phone_number):
	global name
	global google_load_balancer
	google_load_balancer=True
	options = webdriver.ChromeOptions()
	options.add_argument('--headless')
	options.add_argument('--no-sandbox')
	options.add_argument('disable-infobars')
	options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
	options.add_argument("--lang=en")
	prefs = {
		"translate_whitelists": {"ru":"en"},
		"translate":{"enabled":"true"}
	}
	options.add_experimental_option("prefs", prefs)
	options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36")
	loc=os.getcwd()
	driver = uc.Chrome(options=options)
	driver.get("https://accounts.google.com/signin/v2/identifier?passive=1209600&continue=https%3A%2F%2Faccounts.google.com%2F&followup=https%3A%2F%2Faccounts.google.com%2F&hl=en&flowName=GlifWebSignIn&flowEntry=ServiceLogin")
	#//*[@id="lang-chooser"]/div[1]/div[1]/div[9]
	#/html/body/div[1]/div[1]/footer/div/div/div[2]/div[9]
	#/html/body/div[1]/div[1]/footer/div/div/div[2]/div[9]
   
	WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[1]/div/form/span/section/div/div/div[1]/div/div[1]/div/div[1]/input"))).send_keys(phone_number)

	WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[2]/div/div[1]/div"))).click()
	try:
		name=WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[1]/div/form/span/section/div/div/div[1]/div/div[2]/div[2]/div"))).text
		if name=="Enter a valid email or phone number" or "Couldn't find your Google Account" in name:
			name="This Phone Number Is Not Connected To Any G00gle Account!"
			print(colored.magenta("[-]")+colored.red(name))
			print(colored.magenta("[-]")+colored.red("This Phone Number Is Connected To A Y0utube Account!"))
            

		else:
			name="This Phone Number Is Connected To A G00gle Account!"
			print(colored.green("[+]")+colored.blue(name))
			print(colored.green("[+]")+colored.blue("This Phone Number Is Connected To A Y0utube Account!"))
          
        
	except:
		name="This Phone Number Is Connected To A G00gle Account!"
		print(colored.green("[+]")+colored.blue(name))
		print(colored.green("[+]")+colored.blue("This Phone Number Is Connected To A Y0utube Account!"))
        
	google_load_balancer=False
     
       

