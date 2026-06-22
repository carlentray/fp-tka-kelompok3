FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .

CMD ["gunicorn", "-w", "8", "-k", "gthread", "--threads", "4", \
     "-b", "0.0.0.0:5000", "--timeout", "30", "app:app"]