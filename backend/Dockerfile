FROM python:3.10.6 as static
WORKDIR /usr/app/backend
COPY . .
RUN mkdir -p /usr/app/staticfiles/assets
RUN mkdir -p /usr/app/staticfiles/bundles
RUN pip3 install -r requirements.txt
RUN python3 manage.py collectstatic --noinput

FROM static  as gunicorn
WORKDIR /usr/app/backend
RUN pip install gunicorn
CMD ["gunicorn", "--access-logfile", "-", "--workers", "3", "--bind", "0.0.0.0:8080", "star_burger.wsgi:application"]
