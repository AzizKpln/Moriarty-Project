from r_Scripts.modules import *
from pyvirtualdisplay import Display
class getLinks:
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



    def getLinksStart(self,phone):
        self.driver.get("https://www.duckduckgo.com")
        self.inputLineNAME("q", phone)
        self.clickLineXPATH("/html/body/div/div[2]/div/div[1]/div[2]/form/input[2]")
        print(colored.yellow("RELATED LINKS:"))
        for i in range(1,7):
            _xpath=f"/html/body/div[2]/div[5]/div[3]/div/div[1]/div[5]/div[{i}]/div/div[1]/div/a"
            
            try:
                link=WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, _xpath))).get_attribute("href")
                print(colored.green("[+] Link Found:"+link))
            except:
                break
        self.driver.quit()
		
                