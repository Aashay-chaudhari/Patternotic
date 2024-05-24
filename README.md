# Patternotic

#TO FIX
-> Make the model predict batches rather than 1 stock at a time
-> Clean the code, better modularize it


#Deploying to EC2

Environment set up:
sudo apt update -y
sudo apt upgrade -y

Install Node and Python:
curl -sL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
sudo npm install -g @angular/cli@14

sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-dev

Cloning Project from git
sudo apt install -y git
git clone https://github.com/Aashay-chaudhari/Patternotic.git
cd Patternotic

Set up the backend
cd backend
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
nohup gunicorn --bind 0.0.0.0:8000 app:app &


Set up the frontend
npm install
ng build --configuration production

Configure Nginx
sudo apt install -y nginx
sudo cp -r dist/* /var/www/html/
sudo systemctl start nginx
sudo nano /etc/nginx/sites-available/default
Copy contents of server.conf to the file.
sudo nginx -t
sudo systemctl reload nginx
