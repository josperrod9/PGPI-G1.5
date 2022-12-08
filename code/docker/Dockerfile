FROM python:3.10.6-alpine3.15
 
RUN apk add --no-cache git

WORKDIR /PGPI

RUN git clone https://github.com/josperrod9/PGPI-G1.5.git .

WORKDIR /PGPI/code

RUN pip install -r requirements.txt

RUN python3 ./manage.py collectstatic --noinput

CMD ["python3", "manage.py","runserver", "0.0.0.0:8000","--noreload"]