FROM python:3.9.0-buster
COPY *.py /app/
COPY requirements.txt /app/
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python3", "app.py", "config.json"]