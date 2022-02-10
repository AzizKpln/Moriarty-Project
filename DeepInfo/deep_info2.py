from r_Scripts.modules import *
from pyvirtualdisplay import Display
class unkownphone:
    def __init__(self):
        f=open("Moriarty/c_Version.moriarty","r")
        
        options=uc.ChromeOptions()
        display=Display(visible=0,size=(1024, 768))
        display.start()
        self.driver=uc.Chrome(options=options,version_main=f.read())


    



    def unkownphoneStart(self,phone):
        phone=phone.split("+")
        print(colored.yellow("\nCOMMENTS AND SPAM RISK"))
        self.driver.get("https://www.unknownphone.com/phone/"+str(phone[1]))
        try:
            d=WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, "content"))).text
            if "nobody has reported" in d:
                print(colored.red("[!]No info on ")+colored.magenta("unkownphone")+colored.red(" about this number"))
            else:
                d=WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "phone_summary"))).text
                print(colored.green("[+]Some Information Found On ")+colored.blue("Unkownphone\n"))
                print(colored.yellow(d)+"\n")
                print(colored.green("[*]Please visit ") +colored.magenta("https://www.unknownphone.com/phone/"+str(phone[1])) + colored.green(" To get more information."))
        except:
            print("GEEEEEEEEEEEEERIIIIIIIIIIIIIIIIIIIIII")
            print(colored.red("[-]This feature needs an update. Please contact with developer soon."))
        self.driver.quit()