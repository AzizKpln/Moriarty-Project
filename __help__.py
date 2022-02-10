from clint.textui import colored
print(colored.green("[*] Commands And Arguments"))

print(colored.yellow("python3 Moriarty.py -pn <phone_number>")+colored.green(" # Use this if you're running this tool for the first time"))
print(colored.yellow("python3 Moriarty.py -rf -pn <phone_number>")+colored.green(" # Use this if you've run this tool before."))

print(colored.yellow("\n -pn == --phone-number and -rf == --run-fast"))
print(colored.yellow("\n [!] if you add --no-social-media argument in your command, you won't recieve any reports on social media"))
print(colored.yellow("\npython3 Moriarty.py --no-social-media -rf  -pn <phone_number>"))
print(colored.yellow("python3 Moriarty.py --no-social-media -pn <phone_number>"))
