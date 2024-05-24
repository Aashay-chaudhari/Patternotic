# Patternotic

#TO FIX
-> Make the model predict batches rather than 1 stock at a time
-> Clean the code, better modularize it


#Install python on EC2: 

sudo apt-get update
sudo apt-get upgrade
sudo apt-get install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.12
curl -sS https://bootstrap.pypa.io/get-pip.py | sudo python3.12
python3.12 --version
pip3.12 --version
sudo apt-get install python3.12-venv
python3.12 -m venv myenv
source myenv/bin/activate