
__author__ = 'Aziz Kaplan'



import os
from gevent.pywsgi import WSGIServer
from flask import Flask, render_template,request,redirect,url_for
import re
from Investigation.FindOwner import main
from Investigation.FindOwner2 import main1
import Investigation.FindOwner
import Investigation.general
from Investigation.spamControl import spamMain
import Investigation.spamControl2
from Investigation.socialMedia1 import faceMain
from Investigation.socialMedia2 import instaMain
from Investigation.socialMedia3 import twMain
from Investigation.socialMedia4 import goMain
from Investigation.socialMedia5 import micMain
from Investigation.getLinks import getLinks_
from Investigation.getComments import getComments_
from Investigation.getComments2 import _getComments2_

import asyncio
import time
import threading
import sys
app = Flask(__name__)
get_comments="Not Provided"
get_links="Not Provided"
spam_risk="Not Provided"
social_media="Not Provided"
find_owner="Not Provided"
runall="Not Provided"
redirectionMicrosoft=False
redirectionMicrosoftFailed=False
email=""
password="" #chill man. It's needed for trucaller and sync.me. Your password is safe. :D
phoneNumberOwner=""
phoneNumberOwner1=""
tupleOutput=False
def threadFunction(functionName,*args):
    loop=asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(functionName(args,))
    except TypeError:
        loop.run_until_complete(functionName(args[0],args[1],args[2]))
def getValueFunction(func):
    global valueName
    global tupleOutput
    while True:
        try:
            valueName=func()
            if type(valueName).__name__=="tuple":
                tupleOutput=True
            elif type(valueName).__name__=="str":
                tupleOutput=False
            break
        except:
            tupleOutput=None
            continue
def bye():
    os.system("killall -9 python3")
@app.route("/MicrosoftMail",methods=["POST","GET"])
def microsoftMail():
    global find_owner,redirectionMicrosoftFailed,email,password
    if request.method=="POST":
        find_owner="Added"
        email=request.form["email"]
        password=request.form["password"]
        if "@gmail.com" in email:
            return redirect(url_for("success"))
        else:
            return render_template("unkownMail.html")
    try:
        if phone_number!="":            
            return render_template("findOwnerEmailPassword.html")
             
        else:
            return render_template("failed.html")
    except:
        redirectionMicrosoftFailed=True
        return redirect(url_for("index"))
@app.route("/success",methods=["POST","GET"])
def success():
    if request.method=="GET":
        global redirectionMicrosoft
        redirectionMicrosoft=True
        return redirect(url_for("index"))
@app.route("/investigationErr",methods=["GET"])
def investigationErr():
    threading.Thread(target=bye).start()
    return render_template("resultErr.html",phone_number=phone_number)
@app.route("/investigation",methods=["GET"])
def investigation():
   
    return render_template("result.html",
        phoneNumberOwner=phoneNumberOwner,
        phoneNumberOwner1=phoneNumberOwner1,
        phone_number=phone_number,
        timeZone=timeZone,
        country=country,
        operator=operator,
        errNumber=errNumber,
        currentTime=currentTime,
        social_media=social_media,
        find_owner=find_owner,
        faceResult=faceResult,
        instaResult=instaResult,
        twResult=twResult,
        goResult=goResult,
        micResult=micResult,
        get_links=get_links,
        spam_risk=spam_risk,
        spamGet=spamGet,
        links=links,
   
        get_comments=get_comments,
        comments=comments,
        comments2=comments2,
        situationSpam=situationSpam,
        explanation=explanation,
        numberType=numberType
        
        )
@app.route("/",methods=["POST","GET"])
def index():
    global get_comments,get_links,spam_risk,social_media,find_owner,phone_number,comments2,runall
    if request.method=="GET":
        if redirectionMicrosoft==True:
            return render_template("findOwnerSuccess.html",phone_number=phone_number)
        if redirectionMicrosoftFailed==True:
            return render_template("failed.html")
        return render_template("index.html")
    if request.method=="POST":
        command=request.form["in"]
        if command=="help":
            return render_template("help.html")
        elif command[0:15]=="add PhoneNumber":
          
            phone_number=str("+"+re.search("\d+",command).group(0))
            return render_template("phoneNumberSuccess.html",phone_number=phone_number)
        elif command[0:21]=="add feature FindOwner":
            try:
                if email!="" or password!="":
                    find_owner="Added"
                    return render_template("findOwnerSuccess.html",phone_number=phone_number)
                else:
                    
                    return redirect(url_for("microsoftMail"))
            except:
                return render_template("failed.html")
        elif command[0:23]=="add feature SocialMedia":
            social_media="Added"
            try:
                return render_template("socialMediaSuccess.html",phone_number=phone_number)
            except:
                return render_template("failed.html")
        elif command[0:20]=="add feature GetLinks":
            get_links="Added"
            try:
                return render_template("GetLinksSuccess.html",phone_number=phone_number)
            except:
                return render_template("failed.html")
        elif command[0:20]=="add feature SpamRisk":
            spam_risk="Added"
            try:
                return render_template("SpamRiskSuccess.html",phone_number=phone_number)
            except:
                return render_template("failed.html")
        elif command[0:23]=="add feature GetComments":
            get_comments="Added"
            try:
                return render_template("GetCommentsSuccess.html",phone_number=phone_number)
            except:
                return render_template("failed.html")
        elif command[0:12]=="show options":
            try:
                return render_template("showoptions.html",phone_number=phone_number,social_media=social_media,get_links=get_links,spam_risk=spam_risk,find_owner=find_owner,get_comments=get_comments)
            except:
                phone_number="Not Provided"
                return render_template("showoptions.html",phone_number=phone_number,social_media=social_media,get_links=get_links,spam_risk=spam_risk,find_owner=find_owner,get_comments=get_comments)
        elif command[0:20]=="add feature *":
            runall="Added"
            social_media="Added"
            spam_risk="Added"
            get_comments="Added"
            get_links="Added"
            try:
                if email!="" or password!="":
                    find_owner="Added"
                    return render_template("featureAll.html",phone_number=phone_number)
                else:
                    return redirect(url_for("microsoftMail"))
            except:
                return render_template("failed.html")
        elif command[0:3]=="run":
            global country,operator,timeZone,errNumber,currentTime,comments,comments2
            Investigation.general.location(phone_number)
            country=Investigation.general.returnCountry()
            operator=Investigation.general.returnOperator()
            timeZone=Investigation.general.returnTimeZone()
            errNumber=Investigation.general.return_errNumber_()
            currentTime=Investigation.general.returnCurrentTime()
            if errNumber!="False":
                threading.Thread(target=runScripts).start()  
                time.sleep(2) 
                return redirect(url_for("investigation"))
            else:
                return redirect(url_for("investigationErr"))
        else:
            return render_template("unkownCommand.html")
def featureOnProgress():
    global instaResult,twResult,goResult,micResult,links,comments2,comments,faceResult,spam_risk,situationSpam,explanation,numberType,spamGet
    global phoneNumberOwner,phoneNumberOwner1
    if spam_risk=="Added":
        spamGet="Feature On Progress"
        situationSpam="Feature On Progress"
        explanation="Feature On Progress"
        numberType="Feature On Progress"
    else:
        spamGet="Feature Not Selected"
        situationSpam="Feature Not Selected"
        explanation="Feature Not Selected"
        numberType="Feature Not Selected"
    if social_media=="Added":
        faceResult="Feature On Progress"
        instaResult="Feature On Progress"
        twResult="Feature On Progress"
        goResult="Feature On Progress"
        micResult="Feature On Progress"
    else:
        faceResult="Feature Not Selected"
        instaResult="Feature Not Selected"
        twResult="Feature Not Selected"
        goResult="Feature Not Selected"
        micResult="Feature Not Selected"
    if get_links=="Added":
        links="Feature On Progress"
    else:
        links="Feature Not Selected"
    if get_comments=="Added":
        comments="Feature On Progress";comments2="Feature On Progress"
    else:
        comments="Feature Not Selected";comments2="Feature Not Selected"
    if find_owner=="Added":
        phoneNumberOwner="Feature On Progress"
        phoneNumberOwner1="Feature On Progress"
    else:
        phoneNumberOwner="Feature Not Selected";phoneNumberOwner1="Feature Not Selected"
def runScripts():
    global get_comments,get_links,spam_risk,social_media,find_owner,phone_number,runall,faceResult,links,phoneNumberOwner
    global situationSpam,explanation,numberType,spamGet,comments2,instaResult,twResult,goResult,micResult,phoneNumberOwner1
    #some features are being ran in threads while others aren't. This is designed for low system devices that are using moriarty project.
    if errNumber!="False":
        featureOnProgress()
        
        if spam_risk=="Added":
            Investigation.spamControl2.getSpam(phone_number)
            spamGet=Investigation.spamControl2.returnValue()
            spamMain(phone_number)
            situationSpam,explanation,numberType=Investigation.spamControl.printAll()
        if get_comments=="Added":
            getComments_(phone_number)
            threading.Thread(target=_getComments_).start()
            _getComments2_(phone_number)
            comments2=Investigation.getComments2.printAll()
        if get_links=="Added":
            getLinks_(phone_number)
            links=Investigation.getLinks.printAll()
        if find_owner=="Added":
            threadFunction(main,phone_number,email,password)
            phoneNumberOwner=Investigation.FindOwner.printName()
            threadFunction(main1,phone_number,email,password)
            phoneNumberOwner1=Investigation.FindOwner2.printName()
        if social_media=="Added":
            threadFunction(faceMain,phone_number);faceResult=Investigation.socialMedia1.printAll()
            threadFunction(instaMain,phone_number);instaResult=Investigation.socialMedia2.printAll()
            threadFunction(twMain,phone_number);twResult=Investigation.socialMedia3.printAll()
            threadFunction(goMain,phone_number);goResult=Investigation.socialMedia4.printAll()
            threadFunction(micMain,phone_number);micResult=Investigation.socialMedia5.printAll()
          

        
        
def _getComments_():
    global comments
    while True:
        try:
            comments=Investigation.getComments.printAll()
            break
        except:
            comments="Feature On Progress"
            continue
def socialMedia1():
    global faceResult
    while True:
        try:
            faceResult=Investigation.socialMedia1.printAll()
        except:
            faceResult="Feature On Progress"
            continue
def socialMedia2():
    global instaResult
    while True:
        try:
            instaResult=Investigation.socialMedia2.printAll()
        except:
            instaResult="Feature On Progress"
            continue
def socialMedia3():
    global twResult
    while True:
        try:
            twResult=Investigation.socialMedia3.printAll()
        except:
            twResult="Feature On Progress"
            continue
def socialMedia4():
    global goResult
    while True:
        try:
            goResult=Investigation.socialMedia4.printAll()
        except:
            goResult="Feature On Progress"
            continue  
def socialMedia5():
    global micResult
    while True:
        try:
            micResult=Investigation.socialMedia5.printAll()
        except:
            micResult="Feature On Progress"
            continue  
if __name__ == "__main__":
    import subprocess
    app.run(str(subprocess.check_output("hostname -I | awk '{print $1}'",shell=True).decode().strip()),8080,debug=True)
    
