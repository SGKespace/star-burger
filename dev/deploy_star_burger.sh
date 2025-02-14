# проверяем депплой
# deploy_star_burger.sh
#!/bin/bash
clear
set -euxo pipefail
# В случае ошибки, отправка сообщения в Rollbar и завершение выполнения скрипта
trap 'send_to_rollbar "Deployment failed."' ERR

cd /opt/star-burger

# Загрузка переменных окружения из файла .env (если он существует)
if [ -f .env ]; then
source .env
fi

# Функция для отправки сообщения в Rollbar
send_to_rollbar() {
  local ACCESS_TOKEN="$ROLLBAR_TOKEN"
  local MESSAGE="$1"
  curl -X POST \
    -H "Content-Type: application/json" \
    -d "{\"access_token\": \"$ACCESS_TOKEN\", \"data\": {\"body\": {\"message\": {\"body\": \"$MESSAGE\"}}}}" \
    https://api.rollbar.com/api/1/item/
}

# Проверка наличия токена доступа Rollbar
if [ -z "$ROLLBAR_TOKEN" ]; then
  echo "Error: ROLLBAR_TOKEN is not set. Please set the environment variable."
  exit 1
fi

# Обновление кода репозитория
echo "Updating repository code..."
cd /opt/star-burger
git pull --rebase origin
git rev-parse HEAD

source ./venv/bin/activate

# Установка библиотек Python
echo "Installing Python libraries..."
pip3 install -r requirements.txt 

# Накат миграций
echo "Applying database migrations..."
python3 manage.py migrate --noinput

# Пересборка статики Django
echo "Collecting Django static files..."
python3 manage.py collectstatic --noinput

systemctl reload getip.service
systemctl reload nginx.service

# Отправка сообщения в Rollbar
echo "Sending deployment message to Rollbar..."
gh_hash=`git rev-parse HEAD`
send_to_rollbar "Deployment completed successfully. $gh_hash"
