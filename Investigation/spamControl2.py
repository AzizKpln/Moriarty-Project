import requests
from bs4 import BeautifulSoup
def returnValue():
    return com
def getSpam(phone_number):
    global com
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
    }
    try:
        print(phone_number)
        phone_number=phone_number.split("+")[1]
        
        reqToServer=requests.get(f"https://www.unknownphone.com/phone/{phone_number}",headers=headers)
        print("here2")
        source = BeautifulSoup(reqToServer.content,"lxml")
        com=source.select('#content > div > main > section.user-scam-detected > div > p > mark > strong:nth-child(2)')[0].text
      
    except:
        com="No spam info found"
        
