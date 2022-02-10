from r_Scripts.modules import *
from pyvirtualdisplay import Display
class whocallsme:
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



    def whocallsmeStart(self,phone):
        phone=phone.split("+")
        self.driver.get("https://whocallsme.com/Phone-Number.aspx/"+str(phone[1]))

        for i in range(1,5):
            _name=f"/html/body/div[1]/div/div[1]/div/div[2]/div[2]/ul/li[{i}]/div[2]/div[3]/div[1]/span"
            _comment=f"/html/body/div[1]/div/div[1]/div/div[2]/div[2]/ul/li[{i}]/div[3]"
            try:
                
                print(colored.magenta("[!] NAME:"+colored.green(WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, _name))).text)))
                print(colored.magenta("[!] Comment ID "+str(i)+":"+colored.green(WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, _comment))).text))+"\n")
                
            except:
                try:
                    print(colored.magenta("[!] NAME:"+colored.green(WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"/html/body/div[1]/div/div[1]/div/div[2]/div[2]/ul/li[{i+1}]/div[2]/div[3]/div[1]/span"))).text)))
                    print(colored.magenta("[!] Comment ID "+str(i)+":"+colored.green(WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"/html/body/div[1]/div/div[1]/div/div[2]/div[2]/ul/li[{i+1}]/div[3]"))).text)))
                    continue    
                except:
                    break
        print(colored.yellow("[*]You can also visit:")+colored.green("https://whocallsme.com/Phone-Number.aspx/"+str(phone[1])))
        self.driver.quit()
            
        
		
                