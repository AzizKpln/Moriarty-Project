from r_Scripts.modules import *
from pyvirtualdisplay import Display


class linkedinInformation:
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



    def linkedinStart(self,phone):
        self.driver.get("https://www.linkedin.com")
        try:
            self.inputLineNAME("session_key", phone)
            self.inputLineNAME("session_password",phone)
            self.clickLineXPATH("/html/body/main/section[1]/div/div/form/button")
            try:
                error_result=WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, "error-for-password"))).text
            except:
                try:
                    error_result=WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, "error-for-username"))).text
                    print(colored.red("[-]")+colored.magenta(("This phone number is")+colored.red(" not ")+colored.magenta("connected with a Linkedin account")))
                except:
                    pass
            if error_result=="That’s not the right password. Forgot password?":
                print(colored.blue("[+]")+colored.green(("This phone number is connected with a Twitter account")))
            else:
                print(colored.red("[-]")+colored.magenta(("This phone number is")+colored.red(" not ")+colored.magenta("connected with a Linkedin account")))
        except:
            pass
        self.driver.quit()