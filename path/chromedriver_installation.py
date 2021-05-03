import requests,string,subprocess,re
from bs4 import BeautifulSoup
class auto_chromedriver_installer:
	def __init__(self):
		self.url_file = 'https://chromedriver.storage.googleapis.com/'
		self.file_name = 'chromedriver_linux64.zip'
	def check_chromium(self):
		version_chromium=subprocess.check_output(["chromium","--version"]).decode().split(" ")
		for j in version_chromium:
			for i in string.digits:
				if i in j:
					self.current_chromium_version=j
	def chromedriver_version(self):
		self.check_chromium()
		self.current_chromedriver_version=self.current_chromium_version.split(".")
		self.current_chromedriver_version=self.current_chromedriver_version[0]+"."+self.current_chromedriver_version[1]+"."+self.current_chromedriver_version[2]
		print(self.current_chromedriver_version)
	def parseTheWeb(self):
		self.chromedriver_version()
		r = requests.get('https://chromedriver.chromium.org/downloads')
		source=BeautifulSoup(r.content,"html.parser")
		self.findVersion=source.find("div").text
		self.findVersion=self.findVersion.split(self.current_chromedriver_version)
		self.get_version=re.search("\d\d",self.findVersion[1]).group(0)
		self.current_chromedriver_version=self.current_chromedriver_version+"."+self.get_version
	def install(self):
		self.parseTheWeb()
		file = requests.get(self.url_file + self.current_chromedriver_version + '/' + self.file_name)
		print(self.url_file + self.current_chromedriver_version + '/' + self.file_name)
		with open(self.file_name, "wb") as code:
			code.write(file.content)

aci=auto_chromedriver_installer()
aci.install()

