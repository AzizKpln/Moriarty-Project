import requests
from bs4 import BeautifulSoup
def printAll():
    return situationSpam,explanation,numberType

def spamMain(phone_number):
    global situationSpam,explanation,numberType
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
    }
    phone_number=phone_number.split("+")[1]
    reqToServer=requests.get(f"https://spamcalls.net/en/number/{phone_number}",headers=headers)
    source = BeautifulSoup(reqToServer.content,"lxml")
    situationSpam=source.select('a[href="#ratings"]')
    numberType=source.select('a[href="#estimates"]')
    explanation=source.select('a[href="#solution"]')
    if situationSpam!=[]:situationSpam=situationSpam[0].text
    else:situationSpam="User reports for the phone number are not (no longer) available."

    if explanation!=[]:explanation=explanation[0].text
    else:explanation="No Explanation"

    if numberType!=[]:numberType=numberType[0].text
    else:numberType="No numberType"


