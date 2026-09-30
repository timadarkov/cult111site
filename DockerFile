FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x ./deploy/entrypoint.sh \
    && useradd -m appuser

USER appuser

EXPOSE 8000

ENTRYPOINT ["./deploy/entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
