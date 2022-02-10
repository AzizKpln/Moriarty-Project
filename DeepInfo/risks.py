from r_Scripts.modules import *
from pyvirtualdisplay import Display
class spamcalls:
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



    def spamcallsStart(self,phone):
        phone=phone.split("+")
        self.driver.get("https://spamcalls.net/en/number/"+str(phone[1]))
        try:
            user_reports=WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[1]/div/p[1]"))).text
            spam_risk=WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[1]/div/div[1]/div[1]/div/h3/strong"))).text 
            if user_reports=="No User Reports":
                print(colored.yellow("[*] No one reported this number on https://spamcalls.net/"))
                #print(colored.yellow("[!] Spam Risk:")+colored.green("Low"))
            else:
                print(colored.yellow("[!] This number has "+user_reports+" on https://spamcalls.net/\n"))
                if str(spam_risk.split("\n")[1])!="Low":
                    print(colored.yellow("[!] Spam Risk:")+colored.red("High"))
                elif str(spam_risk.split("\n")[1])=="Low":
                    print(colored.yellow("[*] No one reported this number on https://spamcalls.net/"))
                    #print(colored.yellow("[!] Spam Risk:")+colored.green("Low"))
        except:
            try:
                spam_risk=WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[1]/div/div[2]/div[1]/div/div[1]/span[2]"))).text 
                user_reports=WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[1]/div/div[2]/div[1]/div/div[2]/span[2]"))).text
                if str(spam_risk.split("\n")[1])!="Low":
                    print(colored.yellow("[!] Spam Risk:")+colored.red("High"))
                elif str(spam_risk.split("\n")[1])=="Low":
                    print(colored.yellow("[*] No one reported this number on https://spamcalls.net/"))
                    #print(colored.yellow("[!] Spam Risk:")+colored.green("Low"))
                print(colored.yellow("[!] This number has "+user_reports+" on https://spamcalls.net/\n"))

				
            except:

                spam_risk=WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[1]/div/div[2]/div[1]/div/div[1]/h4"))).text
                
                user_reports=WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[1]/div/div[2]/div[1]/div/div[1]/h3/span"))).text
                if spam_risk=="High":
                    print(colored.yellow("[!] Spam Risk:")+colored.red("High"))
                    
                print(colored.yellow("[!] This number has "+user_reports+" on https://spamcalls.net/"))
				

				#print(spam_risk)

        self.driver.quit()#time.sleep(1234)
		
                