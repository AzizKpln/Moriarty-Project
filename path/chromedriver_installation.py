import requests,string,subprocess
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
		cv=self.current_chromium_version.split(".")
		if cv[0]=="81":
			self.current_chromedriver_version="81.0.4044.138"
		elif cv[0]=="83":
			self.current_chromedriver_version="83.0.4103.39"
		elif cv[0]=="84":
			self.current_chromedriver_version="84.0.4147.30"
		elif cv[0]=="85":
			self.current_chromedriver_version="85.0.4183.87"
		elif cv[0]=="86":
			self.current_chromedriver_version="86.0.4240.22"
		elif cv[0]=="87":
			self.current_chromedriver_version="87.0.4280.20"
		else:
			self.current_chromedriver_version=requests.get("https://chromedriver.storage.googleapis.com/LATEST_RELEASE").text
			
	def install(self):
		self.chromedriver_version()
		print(self.current_chromium_version)
		file = requests.get(self.url_file + self.current_chromedriver_version + '/' + self.file_name)
		with open(self.file_name, "wb") as code:
			code.write(file.content)

aci=auto_chromedriver_installer()
aci.install()

