FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY docker_test.py .

EXPOSE 8000

CMD ["uvicorn", "docker_test:app", "--host", "0.0.0.0", "--port", "8000"]
