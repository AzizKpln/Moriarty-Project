import phonenumbers
from phonenumbers.timezone import time_zones_for_number
from phonenumbers import geocoder
from phonenumbers import carrier
import sys
from datetime import datetime
import pytz

def location(phone_number):
    try:
        global number,liste,country,operator,errNumber,currentTime
        number=phonenumbers.parse(phone_number,"EN")
        liste=time_zones_for_number(number)
        country=geocoder.description_for_number(number, "en")
        operator=carrier.name_for_number(number,"en")
        if str(liste[0])=="Etc/Unknown":
            errNumber="False"
            currentTime=None
        else:errNumber="True";IST = pytz.timezone(str(liste[0]));datetime_ist = datetime.now(IST);currentTime=datetime_ist.strftime('%Y:%m:%d %H:%M:%S')
    except:
        errNumber="False"
        currentTime=None
        country=None
        operator=None
        liste=[None]
    
def returnCountry():
    return str(country)
def returnTimeZone():
    return str(liste[0])
def returnOperator():
    return str(operator)
def return_errNumber_():
    return errNumber
def returnCurrentTime():
    return currentTime
