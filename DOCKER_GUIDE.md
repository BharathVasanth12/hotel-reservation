# Docker/Podman Deployment Guide

## 📦 Build and Run Commands

### Using Docker

**1. Build the image:**
```bash
docker build -t hotel-reservation:latest .
```

**2. Run the container:**
```bash
docker run -d \
  --name hotel-reservation \
  -p 5001:5001 \
  -v $(pwd)/artifacts:/app/artifacts:ro \
  hotel-reservation:latest
```

**3. Using Docker Compose (Recommended):**
```bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

**4. Check running containers:**
```bash
docker ps
```

**5. View logs:**
```bash
docker logs -f hotel-reservation
```

**6. Stop and remove container:**
```bash
docker stop hotel-reservation
docker rm hotel-reservation
```

---

### Using Podman

**1. Build the image:**
```bash
podman build -t hotel-reservation:latest .
```

**2. Run the container:**
```bash
podman run -d \
  --name hotel-reservation \
  -p 5001:5001 \
  -v $(pwd)/artifacts:/app/artifacts:ro \
  hotel-reservation:latest
```

**3. Using Podman Compose:**
```bash
# Install podman-compose first
pip install podman-compose

# Start the application
podman-compose up -d

# View logs
podman-compose logs -f

# Stop the application
podman-compose down
```

**4. Check running containers:**
```bash
podman ps
```

**5. View logs:**
```bash
podman logs -f hotel-reservation
```

**6. Stop and remove container:**
```bash
podman stop hotel-reservation
podman rm hotel-reservation
```

---

## 🚀 Quick Start

### Option 1: Docker Compose (Easiest)
```bash
# Build and start
docker-compose up -d

# Access the app
open http://localhost:5001
```

### Option 2: Manual Build
```bash
# Build image
docker build -t hotel-reservation:latest .

# Run container
docker run -d -p 5001:5001 --name hotel-reservation hotel-reservation:latest

# Access the app
open http://localhost:5001
```

---

## 🔍 Troubleshooting

### Port Already in Use
```bash
# Find and kill process using port 5001
lsof -ti :5001 | xargs kill -9

# Or use a different port
docker run -d -p 8080:5001 --name hotel-reservation hotel-reservation:latest
```

### Container Won't Start
```bash
# Check logs
docker logs hotel-reservation

# Run interactively for debugging
docker run -it --rm hotel-reservation:latest /bin/bash
```

### Model Not Found
```bash
# Ensure artifacts/model/ exists and contains the model file
# Mount artifacts directory correctly:
docker run -d \
  -p 5001:5001 \
  -v $(pwd)/artifacts:/app/artifacts:ro \
  hotel-reservation:latest
```

---

## 🏗️ Advanced Usage

### Build with Custom Tag
```bash
docker build -t hotel-reservation:v1.0.0 .
```

### Run with Environment Variables
```bash
docker run -d \
  -p 5001:5001 \
  -e FLASK_ENV=production \
  -e DEBUG=False \
  hotel-reservation:latest
```

### Multi-Stage Build (Production)
```bash
# Build optimized image
docker build --target production -t hotel-reservation:prod .
```

### Save and Load Image
```bash
# Save image to file
docker save hotel-reservation:latest | gzip > hotel-reservation.tar.gz

# Load image from file
docker load < hotel-reservation.tar.gz
```

### Push to Registry
```bash
# Tag for Docker Hub
docker tag hotel-reservation:latest username/hotel-reservation:latest

# Push to Docker Hub
docker push username/hotel-reservation:latest
```

---

## 📊 Container Management

### View Container Stats
```bash
docker stats hotel-reservation
```

### Execute Commands in Running Container
```bash
# Access bash shell
docker exec -it hotel-reservation /bin/bash

# Check Python version
docker exec hotel-reservation python --version

# List files
docker exec hotel-reservation ls -la /app
```

### Health Check
```bash
# Check if container is healthy
docker inspect --format='{{.State.Health.Status}}' hotel-reservation

# Manual health check
curl http://localhost:5001/health
```

---

## 🧹 Cleanup

### Remove Containers
```bash
# Stop all running containers
docker stop $(docker ps -q)

# Remove stopped containers
docker rm $(docker ps -aq)

# Or use prune
docker container prune -f
```

### Remove Images
```bash
# Remove specific image
docker rmi hotel-reservation:latest

# Remove all unused images
docker image prune -a -f
```

### Complete Cleanup
```bash
# Remove everything (containers, images, volumes, networks)
docker system prune -a --volumes -f
```

---

## 📝 Build Arguments

### Custom Python Version
```dockerfile
# In Dockerfile, change:
FROM python:3.10-slim
```

```bash
docker build -t hotel-reservation:py310 .
```

---

## 🔐 Security Best Practices

1. **Run as non-root user** (add to Dockerfile):
```dockerfile
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser
```

2. **Scan for vulnerabilities**:
```bash
docker scan hotel-reservation:latest
```

3. **Use specific base image versions**:
```dockerfile
FROM python:3.9.18-slim
```

---

## 📦 Image Size Optimization

### Check image size:
```bash
docker images hotel-reservation
```

### Tips to reduce size:
- Use slim or alpine base images
- Multi-stage builds
- Remove build dependencies after installation
- Use .dockerignore effectively

---

## 🌐 Access the Application

Once running, access:
- **Web UI**: http://localhost:5001
- **Health Check**: http://localhost:5001/health
- **Prediction API**: http://localhost:5001/predict (POST)

---

## 📋 Requirements

- Docker 20.10+ or Podman 3.0+
- 2GB RAM minimum
- Python 3.9+ base image
- Trained model in `artifacts/model/` directory
