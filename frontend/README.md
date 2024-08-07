# Frontend Admin for Gstreamer

### Settings:
1. install dependencies:
```bash
pip install -r requirements.txt
```

2. Изменить путь в .env-файле:
```
CONFIGS_ROOT_FOLDER="[absolute path to the folder: /backend/]"
MAIN_PROJECT_ROOT_FOLDER="[absolute path to the root folder]"
```
**Пример**:
CONFIGS_ROOT_FOLDER="/home/antuanuran/Desktop/Projects_work/02.07_Release/SPHERE-SA/backend"

3. run:
```bash
python manage.py runserver
```

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


Длинный способ:
```
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```
```bash
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```
```bash
sudo docker activate hello-world
```


