# Gunakan image Python resmi yang ringan
FROM python:3.9-slim

# Atur working directory di dalam container
WORKDIR /app

# Install dependency utama
RUN pip install --no-cache-dir flask pymongo gunicorn

# Salin source code backend ke dalam container
COPY Resources/BE/app.py .

# Jalankan backend menggunakan Gunicorn dengan 9 workers (untuk 4 vCPU)
CMD ["gunicorn", "-w", "9", "-b", "0.0.0.0:5000", "app:app"]