FROM python:latest

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

# -u is needed for docker container printing logs
CMD ["python", "-u", "app.py"]