import requests
from bs4 import BeautifulSoup
def printAll():
    return comment
def _getComments2_(phone_number):
    global comment
    comment=[]
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:84.0) Gecko/20100101 Firefox/84.0",
    }
    phone_number=phone_number.split("+")[1]
    reqToServer = requests.get(f"https://spamcalls.net/en/number/{phone_number}", headers=headers)
    source = BeautifulSoup(reqToServer.content,"lxml")
    comment_=source.select(f'p[lang="en"]')
    for i in comment_:
        comment.append(i.text)
    if comment==[]:
        comment.append("No comment for this number")
    print(comment_)