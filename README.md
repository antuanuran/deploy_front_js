### Install Docker on ubuntu

Короткий способ:
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
systemctl start docker
curl -L "https://github.com/docker/compose/releases/download/1.26.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
docker version
docker-compose --version
```

 ```bash
sudo apt upgrade
sudo apt install python3-venv python3-pip 
```

1. Переходим во Фронтенд
 ```bash
cd ../frontend
```

2. install dependencies:
```bash
pip install -r requirements.txt
```

3. run:
```bash
python manage.py runserver
```
