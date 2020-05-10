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
from social_media import facebook
from social_media import instagram
from social_media import twitter
from social_media import google
from social_media import linkedin
from social_media import microsoft
from social_media import viber
from social_media import yandex
from location import location_risk
from banners import cool_text
from risks_and_deep_search import risks
from risks_and_deep_search import deep_info1
from risks_and_deep_search import deep_info2
from risks_and_deep_search import deep_info3
from send_sms import sms
from owner import owner_sync
def get_arguments():
    parser=optparse.OptionParser()
    parser.add_option("-m",dest="mail_address",help="Give The Gmail Address",action="store")
    parser.add_option("-p",dest="mail_password",help="Give The Gmail Password",action="store")
    parser.add_option("-n",dest="phone_number",help="Give The Phone Number Information",action="store")
    (options,arguments)=parser.parse_args()
    if not options.phone_number or not options.mail_address or not options.phone_number:
        parser.error("Please Use '-h' Parameter To Get Help!")
    else:
        return options
def c_text():
    cool_text.cool_t()
def name(phone_number,username,password):

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('disable-infobars')
    options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36")
    loc=os.getcwd()
    serv=Service("%s/path/chromedriver"%loc)
    driver = webdriver.Chrome(options=options,service=serv)
    driver.get("https://www.truecaller.com")
    print(colored.blue("[!]This Will Take A While Please Wait <3"))
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/nav/div/form/input"))).send_keys(phone_number)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/nav/div/form/button"))).click()
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/main/div/a[1]"))).click()
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[1]/div/form/span/section/div/div/div[1]/div/div[1]/div/div[1]/input"))).send_keys(username)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[2]/div/div[1]/div"))).click()
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[1]/div/form/span/section/div/div/div[1]/div[1]/div/div/div/div/div[1]/div/div[1]/input"))).send_keys(password)

    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[2]/div/div[1]/div"))).click()
    try:

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="submit_approve_access"]'))).click()
    except:
        try:
            name=WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/main/div/div[1]/div[1]/header'))).text
            name=name.split("Add")
            name=name[0]
            if "Is the name correct?" in name:
                name=name.split("Is")
                name=name[0]
            if name=="" or name==" ":
                print(colored.red("[-]Recaptcha Error Please Change Your Ip And Try To Use The Tool Again"))
            print(colored.green("[+]This Phone Number Belongs To:%s"%str(name)))
            with open("output/owner_of_number.txt","a+") as file:
                file.write("\n[+]This Phone Number Belongs To:%s"%str(name)+"\n--------------------------------------------------------------")

        except:
            try:
                print(colored.red("[-]",end=""))
                res=WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/main/div/div[1]/div/h3'))).text

                if res=="No result found":
                    print(colored.red("No Name Found For This Number!"))
                    with open("output/owner_of_number.txt","a+") as file:
                        file.write("\n[-]No Name Found For This Number!"+"\n--------------------------------------------------------------")

                elif res=="Search limit exceeded":
                    print(colored.red("Search Limit Exceeded Please Use Another Gmail Account To Solve This Error!"))

            except:
                print(colored.red("[-]This Gmail Account Requires A Phone Number\n[-]Please Use Another Fake Gmail Account Without Phone Number To Solve This Error.\n[-]Or You Can Wait For 5-10 Min And You Can Try To Run The Script Again"))
    try:
        name=WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/main/div/div[1]/div[1]/header'))).text

        name=name.split("Add")
        name=name[0]
        if "Is the name correct?" in name:
            name=name.split("Is")
            name=name[0]
        if name=="" or name==" ":
            print(colored.red("[-]Recaptcha Error Please Change Your Ip And Try To Use The Tool Again"))
        return_option="[+]This Phone Number Belongs To:%s"%str(name)
        print(colored.green(return_option))
        with open("output/owner_of_number.txt","a+") as file:
            file.write("[+]This Phone Number Belongs To:%s"%str(name)+"\n--------------------------------------------------------------")

    except:
        try:
            print(colored.red("[-]",end=""))
            res=WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/main/div/div[1]/div/h3'))).text
            if res=="No result found":
                print(colored.red("No Name Found For This Number!"))
                with open("output/owner_of_number.txt","a+") as file:
                    file.write("\n[-]No Name Found For This Number!"+"\n--------------------------------------------------------------")

            elif res=="Search limit exceeded":
                print("Search Limit Exceeded Please Use Another Gmail Account To Solve This Error!")

        except:
            pass

def facebook_phone(phone_number):
    facebook.fb(phone_number)
def instagram_phone(phone_number):
    instagram.inst(phone_number)
def twitter_phone(phone_number):
    twitter.tw(phone_number)
def google_phone(phone_number):
    google.gg(phone_number)
def linkedin_phone(phone_number):
    linkedin.lnkd(phone_number)
def microsoft_phone(phone_number):
    microsoft.microsoft(phone_number)
def viber_phone(phone_number):
    viber.viber(phone_number)
def location_risk_number(phone_number):
    location_risk.location(phone_number)
def yandex_phone(phone_number):
    yandex.yandex(phone_number)
def risk_level(phone_number):
    risks.r_level(phone_number)
def deep_info_one(phone_number):
    deep_info1.deep_one(phone_number)
def deep_info_two(phone_number):
    deep_info2.deep_two(phone_number)
def deep_info_three(phone_number):
    deep_info3.deep_three(phone_number)
def sms_go():
    msg=input(colored.yellow("Enter Your Message:"))
    amazon_key=input(colored.yellow("Input Your Amazon Key Here:"))
    secret_key=input(colored.yellow("Input Your Amazon Access Key Here:"))
    sms.sms_send(options.phone_number,msg,amazon_key,secret_key)
def sync(phone_number):
    owner_sync.sync(phone_number)
options=get_arguments()


c_text()
with open("output/comments1.txt","w+") as file:
    file.write("****************************************\nTHANK YOU FOR USING MORIARTY!\nYOU CAN SUPPORT ME WITH FOLLOWING MY SOCIAL MEDIA ACCOUNTS!\nFACEBOOK:https://www.facebook.com/aziz.kaplan.96387\nINSTAGRAM:https://www.instagram.com/aziz.kpln/\nGITHUB:https://www.github.com/AzizKpln\nYOUTUBE:CyberSploitable TR\n****************************************")
with open("output/comments2.txt","w+") as file:
    file.write("****************************************\nTHANK YOU FOR USING MORIARTY!\nYOU CAN SUPPORT ME WITH FOLLOWING MY SOCIAL MEDIA ACCOUNTS!\nFACEBOOK:https://www.facebook.com/aziz.kaplan.96387\nINSTAGRAM:https://www.instagram.com/aziz.kpln/\nGITHUB:https://www.github.com/AzizKpln\nYOUTUBE:CyberSploitable TR\n****************************************")
with open("output/location_operator.txt","w+") as file:
    file.write("****************************************\nTHANK YOU FOR USING MORIARTY!\nYOU CAN SUPPORT ME WITH FOLLOWING MY SOCIAL MEDIA ACCOUNTS!\nFACEBOOK:https://www.facebook.com/aziz.kaplan.96387\nINSTAGRAM:https://www.instagram.com/aziz.kpln/\nGITHUB:https://www.github.com/AzizKpln\nYOUTUBE:CyberSploitable TR\n****************************************")
with open("output/social_media_results.txt","w+") as file:
    file.write("****************************************\nTHANK YOU FOR USING MORIARTY!\nYOU CAN SUPPORT ME WITH FOLLOWING MY SOCIAL MEDIA ACCOUNTS!\nFACEBOOK:https://www.facebook.com/aziz.kaplan.96387\nINSTAGRAM:https://www.instagram.com/aziz.kpln/\nGITHUB:https://www.github.com/AzizKpln\nYOUTUBE:CyberSploitable TR\n****************************************")
with open("output/owner_of_number.txt","w+") as file:
    file.write("****************************************\nTHANK YOU FOR USING MORIARTY!\nYOU CAN SUPPORT ME WITH FOLLOWING MY SOCIAL MEDIA ACCOUNTS!\nFACEBOOK:https://www.facebook.com/aziz.kaplan.96387\nINSTAGRAM:https://www.instagram.com/aziz.kpln/\nGITHUB:https://www.github.com/AzizKpln\nYOUTUBE:CyberSploitable TR\n****************************************")
os.system("clear")

print(colored.blue("Owner Name/Number Information:\n"))
name(options.phone_number,options.mail_address,options.mail_password)
try:
    sync(options.phone_number)
except:
    print(colored.red("[-]Recaptcha Error Please Reset Your Modem Or Change Your Ip Address."))

try:
    location_risk_number(options.phone_number)
except:
    print(colored.red("[-]Unknown Phone Number"))
try:
    risk_level(options.phone_number)
except:
    print(colored.red("[-]Unkown Number Risk Level"))
print(colored.yellow("-"*50))
print(colored.blue("\nAccounts For The Number:\n"))
facebook_phone(options.phone_number)
instagram_phone(options.phone_number)
twitter_phone(options.phone_number)
google_phone(options.phone_number)
linkedin_phone(options.phone_number)
microsoft_phone(options.phone_number)
viber_phone(options.phone_number)
yandex_phone(options.phone_number)
print(colored.yellow("-"*50))
print(colored.blue("\nDeep Search:\n"))
deep_info_one(options.phone_number)
deep_info_two(options.phone_number)
deep_info_three(options.phone_number)
print(colored.yellow("-"*50))
a=input(colored.blue("[?]Do You Want To Send Sms To This Number? [Don't Use It For Disturbing People]\n->"))
if a=="y" or a=="yes" or a=="Y" or a=="YES":
    try:
        sms_go()
        print(colored.green("[+]Sms Sent Successully!"))
    except:
        print(colored.yellow("-"*35))
        print(colored.red("\n[-]Sms Could Not Sent To This Number!"))
        print(colored.yellow("[!]This Error Could Be Because Of Aws Keys."))
        print(colored.yellow("[!]Please Register To Amazon Aws And Get Keys."))
        print(colored.yellow("[!]https://www.youtube.com/watch?v=5oBHvl1hurE This Video Will Help You If Don't Know How To Use Aws."))
        print(colored.yellow("\n-"*35))
