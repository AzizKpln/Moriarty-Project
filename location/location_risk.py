#!/usr/bin/python3
import phonenumbers
from phonenumbers.timezone import time_zones_for_number
from phonenumbers import geocoder
from phonenumbers import carrier
from clint.textui import colored
import sys
def location(phone_number):

    number=phonenumbers.parse(phone_number,"EN")
    liste=time_zones_for_number(number)
    country=geocoder.description_for_number(number, "en")
    operator=carrier.name_for_number(number,"en")
    if str(liste[0])=="Etc/Unknown":
        print(colored.red("[-] HMM: This phone number doesn't seem right. Please give a valid number to this tool."))
        sys.exit()
    print(colored.yellow("GENERAL INFORMATION ABOUT NUMBER"))
    print(colored.green("[+]Country:"+str(country)))
    print(colored.green("[+]Time Zone:"+str(liste[0])))
    print(colored.green("[+]Carrier:"+str(operator)))
