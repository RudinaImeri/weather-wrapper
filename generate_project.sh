#!/bin/bash

mkdir -p app k8s

# app/main.py
cat <<EOL > app/main.py
from fastapi import FastAPI, HTTPException, Request
import requests
import aioredis
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from fastapi.responses import JSONResponse

API_KEY = "your_openweathermap_api_key"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

app = FastAPI()

redis = aioredis.from_url("redis://redis:6379", decode_responses=True)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

@app.get("/weather")
@limiter.limit("5/minute")
async def get_weather(request: Request, city: str):
    cache_key = f"weather:{city.lower()}"
    cached = await redis.get(cache_key)
    if cached:
        return JSONResponse(content={"source": "cache", "data": eval(cached)})
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    response = requests.get(BASE_URL, params=params)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error fetching data")
    data = response.json()
    await redis.set(cache_key, str(data), ex=600)
    return {"source": "api", "data": data}
EOL

# app/requirements.txt
cat <<EOL > app/requirements.txt
fastapi
uvicorn
requests
aioredis
slowapi
EOL

# Dockerfile
cat <<EOL > Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
EOL

# k8s/redis-deployment.yaml
cat <<EOL > k8s/redis-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7
        ports:
        - containerPort: 6379
---
apiVersion: v1
kind: Service
metadata:
  name: redis
spec:
  selector:
    app: redis
  ports:
  - port: 6379
EOL

# k8s/wrapper-deployment.yaml
cat <<EOL > k8s/wrapper-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: weather-wrapper
spec:
  replicas: 1
  selector:
    matchLabels:
      app: weather-wrapper
  template:
    metadata:
      labels:
        app: weather-wrapper
    spec:
      containers:
      - name: weather-wrapper
        image: your-dockerhub-username/weather-wrapper:latest
        ports:
        - containerPort: 8000
---
apiVersion: v1
kind: Service
metadata:
  name: weather-wrapper-service
spec:
  selector:
    app: weather-wrapper
  ports:
  - port: 80
    targetPort: 8000
EOL

# README.md
cat <<EOL > README.md
# Weather Wrapper with Redis Caching & Rate Limiting

This project is a FastAPI-based wrapper around OpenWeatherMap's API, deployed in Kubernetes with Redis caching and rate limiting.

## Setup

### 1. Build and Push Docker Image

\`\`\`bash
docker build -t your-dockerhub-username/weather-wrapper .
docker push your-dockerhub-username/weather-wrapper
\`\`\`

### 2. Deploy to Kubernetes

\`\`\`bash
kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/wrapper-deployment.yaml
\`\`\`

### 3. Access the Service

\`\`\`bash
kubectl port-forward svc/weather-wrapper-service 8080:80
curl "http://localhost:8080/weather?city=London"
\`\`\`

Replace \`your_openweathermap_api_key\` in \`main.py\`.
EOL

