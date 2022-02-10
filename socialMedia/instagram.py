from r_Scripts.modules import *
from pyvirtualdisplay import Display


class instagramInformation:
    def __init__(self):
        f=open("Moriarty/c_Version.moriarty","r")
        
        options=uc.ChromeOptions()
        display=Display(visible=0,size=(1600, 1024))
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



    def instagramStart(self,phone):
        self.driver.get("https://www.instagram.com")
        self.inputLineNAME("username",phone)
        self.inputLineNAME("password",phone)
        
        try:
            self.clickLineXPATH("/html/body/div[1]/section/main/article/div[2]/div[1]/div/form/div/div[3]/button") #xpath change
        except:
        
            try:
                self.clickLineXPATH("/html/body/div[1]/section/main/article/div[2]/div[1]/div/form/div/div[3]/button/div/") #xpath change
            except:
                pass
        error_result=WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, "slfErrorAlert"))).text
        try:
            if error_result=="Sorry, your password was incorrect. Please double-check your password.":
                print(colored.blue("[+]")+colored.green(("This phone number is connected with an Instagram account")))
            else:
                print(colored.red("[-]")+colored.magenta(("This phone number is")+colored.red(" not ")+colored.magenta("connected with an Instagram account")))
        except:
            print(colored.red("[-]This feature needs an update. Please contact with developer soon."))
        self.driver.quit()