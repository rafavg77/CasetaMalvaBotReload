# CasetaMalvaBotReload

## Installation
```bash
sudo apt-get install git python3-pip python3-virtualenv python3-venv
git clone https://github.com/rafavg77/CasetaMalvaBotReload.git
cd CasetaMalvaBotReload.git
virtualenv venv
source venv/bin/activate
pip3 install -r requeriments.txt
cp CasetaMalvaBotReload/src/config/config_example.ini CasetaMalvaBotReload/src/config/config.ini
#edit de config.ini file with the params

cd systemd/
sudo cp bot-casetamagentareload.service /etc/systemd/system
sudo systemctl enable bot-casetamagentareload.service
sudo systemctl start bot-casetamagentareload.service
sudo systemctl status bot-casetamagentareload.service