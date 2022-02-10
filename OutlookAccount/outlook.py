#junk code
from clint.textui import colored
import getpass, os
import sys
def run():
    print(colored.green("In order to use this tool, you must have a microsoft account. \nThis account will be used in login progresses. \nYou don't have to issue your real microsoft mail, you can generate a fake account for this tool."))
    print(colored.blue("\n[?]~ Do you have a microsoft mail account?[y/n]\n"))
    ask=input(colored.green("Moriarty-Project")+colored.blue("@")+colored.yellow(str(getpass.getuser()))+colored.red("[-]"))
    if ask.upper()!="Y" and ask.upper()!="YES":
    	os.system("clear")
    	print(colored.green("Please Generate one from https://outlook.live.com/owa/"))
    	sys.exit()
    os.system("clear")
    print(colored.green("Please Input Your Outlook Mail - AnAccountForMoriarty@outlook.com\n"))
    username=input(colored.green("Moriarty-Project")+colored.blue("@")+colored.yellow(str(getpass.getuser()))+colored.red("[-]"))
    if not "@outlook.com" in username and not "@hotmail.com" in username:
        os.system("clear")
        print(colored.red("[-]This Email Is Not Valid"))
        sys.exit() 
    with open("OutlookAccount/username.moriarty","w") as un:un.write(username)
    os.system("clear")
    print(colored.green("Please Input Your Password\n"))
    password=getpass.getpass()
    if password=="" or password==" ":
        os.system("clear")
        print(colored.red("[-]You didn't give a password"))
        sys.exit()
    with open("OutlookAccount/password.moriarty","w") as pw:pw.write(password)
    os.system("clear")
    print(colored.green("Your login information is saved in:OutlookAccount/ \nYou don't have to enter an email address anymore.\nYou can use this command to run the tool instantly: "+colored.magenta("python3 Moriarty.py -rf -pn <phone-number>")))
    print(colored.green("\nPress enter to continue"))
    username=input(colored.green("Moriarty-Project")+colored.blue("@")+colored.yellow(str(getpass.getuser()))+colored.red("[-]"))
