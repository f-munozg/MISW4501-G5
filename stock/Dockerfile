FROM python:3.10-alpine

RUN apk add py3-pip \
    && pip install --upgrade pip

WORKDIR /app
COPY . /app/
    
RUN pip install -r ./requirements.txt

EXPOSE 5000

CMD ["python", "./app.py", "-p 5000","--host=0.0.0.0"]