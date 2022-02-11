

python3 banners/installation_banner.py
sudo apt-get update && sudo apt-get install python3-pip -y
sudo apt-get install chromium -y
cd Moriarty/ && echo $(chromium --version | cut -d "." -f 1 | sed -e 's/.*[^0-9]\([0-9]\+\)[^0-9]*$/\1/') > c_Version.moriarty && cd ../

unzip chromedriver_linux64.zip
rm -r chromedriver_linux64.zip
cp chromedriver path/
cp chromedriver risks_and_deep_search/
cp chromedriver social_media/
sudo apt-get install figlet
pip3 install colored
pip3 install boto3
pip3 install -r requirements.txt
sudo chown -R $(who | cut -d " " -f 1):$(who | cut -d " " -f 1) *
