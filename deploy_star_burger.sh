# deploy_star_burger.sh
#!/bin/bash
set -euxo pipefail

# cd /opt/star-burger

# Загрузка переменных окружения из файла .env (если он существует)
if [ -f .env ]; then
source .env
fi

# Обновление кода репозитория
echo "Updating repository code..."
cd /opt/star-burger
git pull origin master

source ./venv/bin/activate

# Установка библиотек Python
echo "Installing Python libraries..."
pip3 install -r requirements.txt --assume-yes

# Накат миграций
echo "Applying database migrations..."
/opt/inspection/venv/bin/python3 manage.py migrate --noinput # Применение миграций без интерактивного ввода

# Пересборка статики Django
echo "Collecting Django static files..."
/opt/inspection/venv/bin/python3 manage.py collectstatic --noinput

systemctl daemon-reload
systemctl reload getip.service
systemctl reload nginx.service

# Уведомление об успешном завершении деплоя
echo "Deployment completed successfully."

# В случае ошибки, завершение выполнения скрипта
set -e
# Отправка сообщения в Rollbar
echo "Sending deployment message to Rollbar..."
send_to_rollbar "Deployment completed successfully."

# В случае ошибки, отправка сообщения в Rollbar и завершение выполнения скрипта
set -e
trap 'send_to_rollbar "Deployment failed."' ERR
