lightblue=`tput setaf 14` 
green=`tput setaf 46`     
RED=`tput setaf 196`      
yellow=`tput setaf 11`    
purple=`tput setaf 129`   
reset=`tput sgr0` 
clear
if [ $(whoami) != "root" ];then
    sudo apt update && sudo apt full-upgrade -y 
    sudo apt install python3 -y && sudo apt install python3-pip -y
    pip3 install -r requirements.txt
    python3 -m playwright install 
    echo -e "${lightblue}[+]${green} Installation is finished. You can run 'run.sh' file now."
else
    echo -e "${RED}[-]Don't use Moriarty Project with root. \n[!]You have to use it with a normal account"
    exit
fi

