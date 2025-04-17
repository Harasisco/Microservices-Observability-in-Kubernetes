# I have pick this image after scan it with trivy
FROM python:3.13-alpine

# Add a non-root user for more security
RUN adduser -D appuser
WORKDIR /home/appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY hash_service.py .

USER appuser

CMD ["python", "hash_service.py"]
