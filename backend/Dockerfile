FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create required directories
RUN mkdir -p /app/storage/analysis_history

EXPOSE 5173

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5173", "--reload"]