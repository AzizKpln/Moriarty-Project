from r_Scripts.modules import *
from pyvirtualdisplay import Display


class googleInformation:
    def __init__(self):
        f=open("Moriarty/c_Version.moriarty","r")
        
        options=uc.ChromeOptions()
        display=Display(visible=0,size=(1024, 768))
        display.start()
        self.driver=uc.Chrome(options=options,version_main=f.read())


    


    def inputLineXPATH(self,x,y):
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, x))).send_keys(y)
    def inputLineNAME(self,x,y):
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.NAME, x))).send_keys(y)
    def clickLineNAME(self,x):
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.NAME, x))).click()
    def clickLineXPATH(self,x):
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, x))).click()




    def googleStart(self,phone):
        self.driver.get("https://accounts.google.com/ServiceLogin/signinchooser?passive=1209600&continue=https%3A%2F%2Faccounts.google.com%2F&followup=https%3A%2F%2Faccounts.google.com%2F&hl=en&flowName=GlifWebSignIn&flowEntry=ServiceLogin")
       	
        try:
            self.inputLineXPATH('//*[@id="identifierId"]', phone)
            self.clickLineXPATH("/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[2]/div/div[1]/div/div/button")
            self.clickLineXPATH('//*[@id="password"]/div[1]/div/div[1]/input')
            print(colored.blue("[+]")+colored.green(("This phone number is connected with a Google account")))
			
        except:
            
            try:
                self.clickLineXPATH("/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[1]/div/form/span/section/div/div/div[1]/div/div[2]/div[2]/div")
                print(colored.red("[-]")+colored.magenta(("This phone number is")+colored.red(" not ")+colored.magenta("connected with a Google account")))
            except: 
                print(colored.red("[-]This feature needs an update. Please contact with developer soon."))
        self.driver.quit()




