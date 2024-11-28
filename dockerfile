FROM python:3.13-alpine

WORKDIR /app

COPY ./requirements.txt .

ADD . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]