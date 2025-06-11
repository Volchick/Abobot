FROM python
WORKDIR /app
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app /app/app
CMD ["python", "app/main.py"]