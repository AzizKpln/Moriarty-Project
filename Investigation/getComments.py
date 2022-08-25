import requests
from bs4 import BeautifulSoup
def printAll():
    return comment
def getComments_(phone_number):
    global comment,comment_
    comment=[]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
    }
    try:
        phone_number=phone_number.split("+")[1]
        reqToServer=requests.get(f"https://www.unknownphone.com/phone/{phone_number}",headers=headers)
        source = BeautifulSoup(reqToServer.content,"lxml")
        for i in range(1,10):
            try:
                comment_=source.select(f'#content > div > main > section.comments > ul > li:nth-child({i}) > article > div')[0].text
                comment.append(comment_)
            except:
                pass
        if comment==[]:
            comment_="No comment for this number"
            comment.append(comment_) 
    except:
        comment_="No comment for this number"
        comment.append(comment_) 
