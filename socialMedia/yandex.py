from r_Scripts.modules import *
from pyvirtualdisplay import Display


class yandexInformation:
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



    def yandexStart(self,phone):
        self.driver.get("https://passport.yandex.com/")
        self.inputLineNAME("login", phone)
        self.clickLineXPATH("/html/body/div/div/div[2]/div[2]/div/div/div[2]/div[3]/div/div/div/div[1]/form/div[3]/button")
        try:
            try:
                self.inputLineNAME("passwd", phone)
                print(colored.blue("[+]")+colored.green(("This phone number is connected with a Yandex account")))
            except:
                
                self.clickLineXPATH("/html/body/div/div/div[2]/div[2]/div/div/div[2]/div[3]/div/div/form/div/div[2]/div/span/input")
                print(colored.red("[-]")+colored.magenta(("This phone number is")+colored.red(" not ")+colored.magenta("connected with a Yandex account")))
        except:
            try:
                error_result=WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div/div[2]/div[2]/div/div/div[2]/div[3]/div/div/div/div[1]/form/div[1]/div[3]"))).text
                print(colored.red("[-]")+colored.magenta(("This phone number is")+colored.red(" not ")+colored.magenta("connected with a Yandex account")))
            except:
                print(colored.red("[-]This feature needs an update. Please contact with developer soon."))
        self.driver.quit()