### Install Docker on ubuntu

git clone https://github.com/antuanuran/deploy_front_js.git

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
sudo apt install python3-venv python3-pip 
```

```bash
docker pull antuanuran/telegram 
```

```bash
docker pull antuanuran/onvif 
```

```bash
docker pull antuanuran/metadata 
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
python3 manage.py runserver 0.0.0.0:8000
```

Gunicorn:
[Unit]
Description=Service Razvertka
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/root/razvertivanie
ExecStart=/root/razvertivanie/venv/bin/gunicorn --workers 1 --bind unix:/root/razvertivanie/news/project.sock news.wsgi:application

[Install]
WantedBy=multi-user.target
