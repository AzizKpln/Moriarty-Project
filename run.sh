clear
echo "Moriarty Project Remastered V4.1.1"
echo "Github:https://github.com/AzizKpln/Moriarty-Project"
echo -e "Linkedin:https://www.linkedin.com/in/aziz-k-074604170/\n"

echo "Project is currently running. If your browser not showing up,"
echo -e "Please go to this link: http://$(hostname -I | awk '{print $1}'):8080\n"

echo "Press CTRL+C to kill the webserver."
bash startBrowser.sh &
python3 MoriartyProject.py &> /dev/null


