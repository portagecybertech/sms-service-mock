# 1. Base image
FROM python:3.11-slim

# 2. Set working directory inside container
WORKDIR /app

# 3. Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy app code
COPY app.py .

# 5. Expose port (optional but good practice)
EXPOSE 8000

# 6. Run the app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
