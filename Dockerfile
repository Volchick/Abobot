FROM python
WORKDIR /app
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ app/
RUN mkdir -p /app/logs
CMD ["python", "-m", "app.main"]