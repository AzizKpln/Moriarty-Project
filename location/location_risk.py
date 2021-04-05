#!/usr/bin/python3
import phonenumbers
from phonenumbers.timezone import time_zones_for_number
from phonenumbers import geocoder
from phonenumbers import carrier
from clint.textui import colored
def location(phone_number):
    number=phonenumbers.parse(phone_number,"EN")
    liste=time_zones_for_number(number)
    country=geocoder.description_for_number(number, "en")
    operator=carrier.name_for_number(number,"en")
    print(colored.green("[+]Country:"+str(country)))
    print(colored.green("[+]Time Zone:"+str(liste[0])))
    print(colored.green("[+]Carrier:"+str(operator)))
