FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create directory for data volume
RUN mkdir -p /data

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]
