FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

COPY . .

# Chạy với Gunicorn thay vì Flask dev server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]