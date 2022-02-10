from r_Scripts.modules import *

class facebookInformation:
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







    def facebookStart(self,phone):
        self.driver.get("https://www.facebook.com/login/identify")
        self.inputLineXPATH('//*[@id="identify_email"]', phone)
        self.clickLineNAME("did_submit")
        print(colored.yellow("\nSOCIAL MEDIA REPORTS"))
        try:
            name=WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[2]/div[1]/div/div[2]/form/div/div[2]/table/tbody/tr/td[2]/div/div[2]"))).text
            print(colored.blue("[+]")+colored.green(("This phone number is connected with a Facebook account")))
            if "+" in str(name):
                print(colored.red("[-]")+colored.magenta("Facebook Name Could Not Found For:")+colored.yellow(name))
            else:
                print(colored.blue("[+]")+colored.green("Facebook Name Has Found:")+colored.yellow(name))
        except:
            
            try:
                WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[2]/div[1]/div/div[2]/div/div/form/div/div[2]/div[1]/div[1]"))).text
                print(colored.red("[-]")+colored.magenta(("This phone number is")+colored.red(" not ")+colored.magenta("connected with a Facebook account")))
            except:
                #uiHeaderTitle
                if "Account disabled" in WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "uiHeaderTitle"))).text:
                    print(colored.red("[-]")+colored.magenta(("This phone number was")+colored.red(" connected ")+colored.magenta("with a Facebook account but the account is disabled")))
               
        self.driver.quit()


