FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
RUN useradd -r -u 1001 appuser
USER appuser
EXPOSE 8085
CMD ["python", "app.py"]