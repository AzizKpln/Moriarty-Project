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
microsoft_load_balancer=False
def microsoft(phone_number):
	global name
	global microsoft_load_balancer
	microsoft_load_balancer=True
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
	driver.get("https://login.live.com/")

	try:
		WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, 'loginfmt'))).send_keys(phone_number)
		WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/form[1]/div/div/div[2]/div/div/div[1]/div[2]/div[2]/div/div/div/div[4]/div/div/div/div/input"))).click()
		#/html/body/div/form[1]/div/div/div[1]/div[2]/div[2]/div/div[2]/div/div[2]/div/div[2]/input
		WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "passwd"))).send_keys("QWKEQĞPWEQWE")
		WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/form[1]/div/div/div[2]/div/div/div[1]/div[2]/div[2]/div/div[2]/div/div[3]/div[2]/div/div/div/div/input"))).click()
		name=WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "passwordError"))).text
		if name=="Your account or password is incorrect. If you don't remember your password, reset it now.":
			name="This Phone Number Is Connected To A Micr0s0ft Account!"
			print(colored.green("[+]")+colored.blue(name))
		else:
			name="This Phone Number Is Not Connected To Any Micr0s0ft Account!"
			print(colored.magenta("[-]")+colored.red(name))
			



	except:
		name="This Phone Number Is Not Connected To Any Micr0s0ft Account!"
		print(colored.magenta("[-]")+colored.red(name))
	microsoft_load_balancer=False
	driver.close()
