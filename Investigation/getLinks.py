import requests
from bs4 import BeautifulSoup

def printAll():
    return url

def getLinks_(phone_number):
    global url
    url=[]
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:84.0) Gecko/20100101 Firefox/84.0",
    }
    phone_number=phone_number.split("+")[1]
    page = requests.get(f'https://duckduckgo.com/html/?q={phone_number}', headers=headers).text
    soup = BeautifulSoup(page, 'html.parser').find_all("a", class_="result__url", href=True)
    for link in soup:
        if link['href'] == "":
            url.append("not found")
        else:
            url.append(link['href'])
        
