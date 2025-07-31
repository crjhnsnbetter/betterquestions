FROM python:3.10
WORKDIR /app
ARG NOCACHE
RUN echo "🧼 Busting cache: $NOCACHE"
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
RUN echo "🧪 This is a fresh Docker build — Dockerfile was used"
CMD ["python", "webapp.py"]

