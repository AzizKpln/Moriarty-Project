from r_Scripts.modules import *

class getOwnerSYNCME:
    def __init__(self):
        self._owner=None
        f=open("Moriarty/c_Version.moriarty","r")
        options=uc.ChromeOptions()
        display=Display(visible=0,size=(1024, 768))
        display.start()
        self.driver=uc.Chrome(options=options,version_main=f.read())
        
    @property
    def ownerOfNumber(self):
        return self._owner
    @ownerOfNumber.setter
    def ownerOfNumber(self,name):
        self._owner=name
    def inputLineXPATH(self,x,y):
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, x))).send_keys(y)
    def inputLineNAME(self,x,y):
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.NAME, x))).send_keys(y)
    def clickLineXPATH(self,x):
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, x))).click()
    def getNameByXPATH(self,x):
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, x))).text
    def fuckingMicr0s0ft(self,email,password):
        try:
            self.inputLineNAME("loginfmt", email)
            self.clickLineXPATH('//*[@id="idSIButton9"]')
            self.inputLineNAME("passwd", password)
            try:
                self.clickLineXPATH('/html/body/div/form[1]/div/div/div[2]/div[1]/div/div/div/div/div/div[3]/div/div[2]/div/div[4]/div[2]/div/div/div/div/input')
                self.clickLineXPATH('//*[@id="idBtn_Back"]')
            except:
                self.clickLineXPATH('//*[@id="idBtn_Back"]')
            
            try:
                self.clickLineXPATH('//*[@id="idBtn_Accept"]')
            except:
                pass
        except:
            if WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, 'iPageTitle'))).text == "Help us protect your account":
                print(colored.red("[-]Your email has to change. Please create/use another microsoft mail account to use this feature."))
            else:
                print(colored.red("[-]This feature cannot be used. Be sure you are giving correct email information"))
    def getName(self,phoneNumber,email,password):
        self.driver.get("https://sync.me/tr/search/?number="+phoneNumber)
        self.clickLineXPATH('/html/body/div[1]/section/div[3]/div/div/div[1]/div[2]/div')
        self.clickLineXPATH('/html/body/div[3]/div[2]/div[2]/div/div[2]/div[2]');time.sleep(1)
        self.driver.switch_to.window(self.driver.window_handles[1])
        self.fuckingMicr0s0ft(email, password)
        self.driver.switch_to.window(self.driver.window_handles[0])
        
        self.driver.quit()
    @staticmethod
    def NameDefined(value):
        getOwnerSYNCME.ownerOfNumber=value  

gOT=getOwnerSYNCME()


