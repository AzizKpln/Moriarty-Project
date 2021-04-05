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
twitter_load_balancer=False
def tw(phone_number):
	global name
	global twitter_load_balancer
	twitter_load_balancer=True
	options = webdriver.ChromeOptions()
	options.add_argument('--headless')
	options.add_argument('--no-sandbox')
	options.add_argument('disable-infobars')
	options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
	options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36")
	loc=os.getcwd()
	driver = uc.Chrome(options=options)
	driver.get("https://twitter.com/login/")
	WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "session[username_or_email]"))).send_keys(phone_number)
	WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "session[password]"))).send_keys("ihopeitsnotyourpasswordtygodtyjesus")
	WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div/div/div[2]/main/div/div/div[2]/form/div/div[3]/div/div'))).click()

	#/html/body/div[1]/div[3]/div[1]/div/div/form/div/div[2]/ul/li[1]/div/table/tbody/tr/td[1]/div/div/div/div[2]/div[1]
	try:
		time.sleep(5)
		name=WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div/div/div[2]/main/div/div/div[1]/div/div/div/div/div/div'))).text
		
		if name=="The phone number and password you entered did not match our records. Please double-check and try again.":
			name="This Phone Number Is Not Connected To Any Twitter Account!"
			print(colored.magenta("[-]")+colored.red(name))

		else:
			name="This Phone Number Is Connected To A Twitter Account!"
			print(colored.green("[+]")+colored.blue(name))
			
	

		driver.close()
	except:
		pass
	twitter_load_balancer=False
