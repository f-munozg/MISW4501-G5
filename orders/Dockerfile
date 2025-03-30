FROM python:3.10-alpine

RUN apk add py3-pip \
    && pip install --upgrade pip

WORKDIR /app
COPY . /app/
    
RUN pip install -r ./requirements.txt

EXPOSE 5001

CMD ["python", "./application.py", "-p 5001","--host=0.0.0.0"]