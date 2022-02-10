#!/usr/bin/python3


import undetected_chromedriver.v2 as uc
import sys
import os
from clint.textui import colored
import getpass
from OutlookAccount.outlook import run
from banners.installation_banner import *
class Moriarty_Project:
	def __init__(self):
		###########USAGE CHECK#################
		self.usageCountdown()
		#######################################
		
		try:
			if sys.argv[1]=="-h" or sys.argv[1]=="--help":
				self.__help__()
				sys.exit()
			elif sys.argv[1]=="-pn" or sys.argv[1]=="--phone-number":
				run()
				self.phoneNumber=sys.argv[2]
				self.getLoginInfoQuick()
			elif sys.argv[1]=="--no-social-media" and sys.argv[2]=="-pn" or sys.argv[2]=="--phone-number":
				run()
				self.phoneNumber=sys.argv[3]
				self.getLoginInfoQuick()
			elif sys.argv[1]=="-rf" or sys.argv[1]=="--run-fast" and sys.argv[2]=="-pn" or sys.argv[2]=="--phone-number":
				self.phoneNumber=sys.argv[3]
				self.getLoginInfoQuick()
			elif sys.argv[1]=="--no-social-media" and sys.argv[2]=="-rf" or sys.argv[2]=="--run-fast" and sys.argv[3]=="-pn" or sys.argv[3]=="--phone-number":
				self.phoneNumber=sys.argv[4]
				self.getLoginInfoQuick()
			else:
				print(colored.red("[-]Wrong Usage! Please use -h parameter to get help."))
				sys.exit()
		except IndexError:
			print(colored.red("[-]Wrong Usage! Please use -h parameter to get help."))
			sys.exit()
			
		
		
	def __help__(self):
		import __help__
		
	def getLoginInfoQuick(self):
		with open("OutlookAccount/username.moriarty","r") as username:self.username=username.read()
		with open("OutlookAccount/password.moriarty","r") as password:self.password=password.read()
	def startChrome(self):
		try:
			f=open("Moriarty/c_Version.moriarty","r")
			self.driver=uc.Chrome(version_main=f.read())
		except FileNotFoundError:
			os.system("cd Moriarty && bash c_V.sh && cd ..")
			f=open("Moriarty/c_Version.moriarty","r")
			self.driver=uc.Chrome(version_main=f.read())
	
	#phone number information
	def phoneInfo(self):
		from location import location_risk
		try:
			location_risk.location(self.phoneNumber)
		except:
			print(colored.red("[-]Wrong Usage! Please use -h parameter to get help."))
			sys.exit()
	#find owner of number from truecaller
	def getOwnerTruecaller(self):
		from r_Scripts.ownerTruecaller import getOwnerTRUECALLER
		try:
			
			getOwnerTRUECALLER().getName(self.phoneNumber,self.username,self.password)
			ownerName=getOwnerTRUECALLER().ownerOfNumber
			print(colored.green("\nOwner Name 1 - ")+colored.blue(ownerName))
		except:
			pass

	#find owner of number from snycme
	def getOwnerSyncME(self):
		from r_Scripts.ownerSyncME import getOwnerSYNCME
		try:
			getOwnerSYNCME().getName(self.phoneNumber,self.username,self.password)
			ownerName=getOwnerSYNCME().ownerOfNumber
			print(colored.green("Owner Name 2 - ")+colored.blue(ownerName))
		except:
			pass
	
	#Social Media Functions
	def getFacebookInfo(self):
		from socialMedia.facebook import facebookInformation
		facebookInformation().facebookStart(self.phoneNumber)
	def getGoogleInfo(self):
		from socialMedia.google import googleInformation
		googleInformation().googleStart(self.phoneNumber)
	def getInstagramInfo(self):
		from socialMedia.instagram import instagramInformation
		instagramInformation().instagramStart(self.phoneNumber) 
	def getLinkedinInfo(self):
		from socialMedia.linkedin import linkedinInformation
		linkedinInformation().linkedinStart(self.phoneNumber)  
	def getMicrosoftInfo(self):
		from socialMedia.microsoft import microsoftInformation
		microsoftInformation().microsoftStart(self.phoneNumber)  
	def getYandexInfo(self):
		from socialMedia.yandex import yandexInformation
		yandexInformation().yandexStart(self.phoneNumber)

	# Links related with the number
	def getLinks(self):
		from DeepInfo.deep_info1 import getLinks
		getLinks().getLinksStart(self.phoneNumber)

	# Spam, Report, Lookup, comments
	def unkownphone_(self):
		from DeepInfo.deep_info2 import unkownphone
		unkownphone().unkownphoneStart(self.phoneNumber)
	def whocallsme_(self):
		from DeepInfo.deep_info3 import whocallsme
		whocallsme().whocallsmeStart(self.phoneNumber)
	def spamcalls_(self):
		from DeepInfo.risks import spamcalls
		spamcalls().spamcallsStart(self.phoneNumber)

	def usageCountdown(self):
		
		try:
			f=open("Moriarty/CountDownID.moriarty","r")
			cDownID=f.read()
			f1=open("Moriarty/CountDownID.moriarty","w")
			if "3" in cDownID:
				cDownID="0"
				f1.write(cDownID)
				print(colored.yellow("[*] INFO: Looks like now you're running this tool X3. Microsoft Mail and IP change highly suggested. \n[*] INFO: Please use a new microsoft mail and reset your modem. Then re-run this tool."))
				sys.exit()
			else:
				cDownID1=int(cDownID)+1
				f1.write(str(cDownID1))
		except FileNotFoundError:
			print("here countdown")
			f1=open("Moriarty/CountDownID.moriarty","w");f1.write("0")
	def run(self):
		print(colored.blue("\n[*] This Process May Take A While. Please Do Not Interrupt The Process"))
		print(colored.yellow("\nNote: The tool won't work properly if you didn't give correct email information"))
		self.phoneInfo()
		self.spamcalls_()
		self.getOwnerTruecaller()
		self.getOwnerSyncME()
		self.getFacebookInfo()
		self.getInstagramInfo()
		self.getLinkedinInfo()
		self.getGoogleInfo()
		self.getMicrosoftInfo()
		self.getYandexInfo()
		self.getLinks()
		self.unkownphone_()
		self.whocallsme_()
		
	def run1(self):
		print(colored.blue("\n[*] This Process May Take A While. Please Do Not Interrupt The Process"))
		print(colored.yellow("\nNote: The tool won't work properly if you didn't give correct email information"))
		self.phoneInfo()
		self.spamcalls_()
		self.getOwnerTruecaller()
		self.getOwnerSyncME()
		self.getLinks()
		self.unkownphone_()
		self.whocallsme_()
		

		
MP=Moriarty_Project()
if "--no-social-media" in sys.argv:
	MP.run1()
else:
	MP.run()
