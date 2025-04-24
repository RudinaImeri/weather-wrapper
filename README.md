# Weather Wrapper & Frontend

This repository contains:

- **`app/`**: A FastAPI-based Python wrapper around the Open-Meteo and Nominatim (OpenStreetMap) APIs.
- **`frontend/`**: A static HTML + Leaflet + Bootstrap frontend served by NGINX.
- **`k8s/`**: Kubernetes manifests for deploying both the wrapper and frontend.
- **`Dockerfile`**: Builds the FastAPI wrapper.
- **`docker-compose.yml`**: Brings up both wrapper and frontend locally via Docker Compose.

---

## Features

- **Geocoding**: `/geocode?city=...` returns `{latitude, longitude}` via Nominatim.
- **Current-hour weather**: `/weather?latitude=..&longitude=..` returns a single data point from Open-Meteo.
- **Interactive map**: Frontend shows point on a Leaflet map and displays temperature.

---

## Prerequisites

- Docker & Docker Compose
- (Optional) Kubernetes cluster (Docker Desktop Kubernetes, Minikube, or kind)
- `kubectl` (if using Kubernetes)

---

## Local Development (Docker Compose)

1. **Clone** this repo:
   ```bash
   git clone <repo-url>
   cd weather-wrapper
   ```

2. **Build & start**:
   ```bash
   docker-compose up --build -d
   ```

3. **Access**:
   - FastAPI docs:  `http://localhost:8080/docs`
   - Frontend UI:   `http://localhost:8081`

4. **Stop**:
   ```bash
   docker-compose down
   ```

---

## Standalone Docker (no Compose)

### Wrapper

```bash
# Build wrapper image
docker build -t <yourhub>/weather-wrapper:latest .
# Run wrapper
docker run -d -p 8080:80 --name weather-wrapper <yourhub>/weather-wrapper:latest
```

### Frontend

```bash
cd frontend
docker build -t <yourhub>/weather-frontend:latest .
# Run frontend
docker run -d -p 8081:80 --name weather-frontend <yourhub>/weather-frontend:latest
```

Then browse:
- `http://localhost:8080/docs`
- `http://localhost:8081`

---

## Kubernetes Deployment

1. **Ensure** your `kubectl` context is pointed at a running cluster:
   ```bash
   kubectl config use-context docker-desktop   # or minikube
   kubectl get nodes
   ```

2. **Build & push** images to a registry (Docker Hub, etc.):
   ```bash
   docker build -t <yourhub>/weather-wrapper:latest .
   docker push <yourhub>/weather-wrapper:latest

   cd frontend
   docker build -t <yourhub>/weather-frontend:latest .
   docker push <yourhub>/weather-frontend:latest
   cd ..
   ```

3. **Apply manifests**:
   ```bash
   kubectl apply -f k8s/wrapper-deployment.yaml
   kubectl apply -f k8s/wrapper-service.yaml
   kubectl apply -f k8s/frontend-deployment.yaml
   kubectl apply -f k8s/frontend-service.yaml
   ```

4. **Verify**:
   ```bash
   kubectl get pods,svc
   ```

5. **Access**:
   - Wrapper API:  `http://<NODE_IP>:30080/docs`
   - Frontend UI:  `http://<NODE_IP>:30081`

---

## Project Structure

```
weather-wrapper/
├── app/
│   ├── main.py            # FastAPI wrapper + endpoints
│   └── requirements.txt
├── frontend/
│   ├── index.html         # Static client
│   └── Dockerfile
├── k8s/
│   ├── wrapper-deployment.yaml
│   ├── wrapper-service.yaml
│   ├── frontend-deployment.yaml
│   └── frontend-service.yaml
├── Dockerfile             # Builds FastAPI wrapper
└── docker-compose.yml     # Compose for wrapper + frontend
```

---

## End-to-End Flow

1. **User** enters a city in the frontend.
2. Frontend calls **`/geocode`** → gets lat/lon.
3. Frontend updates Leaflet map marker.
4. Frontend calls **`/weather`** → gets current-hour temperature.
5. Frontend displays temperature and timestamp.

---

## Contributing

Adrian Bytyqi, Rudina Imeri, Eron Ramadani