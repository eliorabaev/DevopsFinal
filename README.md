# URL Shortener with Production Monitoring

A production-ready URL shortener service with comprehensive monitoring infrastructure. Built with FastAPI and deployed on Render, featuring real-time metrics collection through Prometheus and visualization via Grafana.

## 🎯 What is this?

This project demonstrates a **hybrid cloud architecture** where a URL shortener API runs in production (Render) while monitoring infrastructure operates locally, providing real-time insights into service performance, alerts, and system health.

**Live Service:** [https://url-shortener-latest-gccb.onrender.com](https://url-shortener-latest-gccb.onrender.com)

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Using the Service](#-using-the-service)
- [Monitoring Dashboard](#-monitoring-dashboard)
- [Development Setup](#-development-setup)
- [API Documentation](#-api-documentation)
- [CI/CD Pipeline](#-cicd-pipeline)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)

## ✨ Features

### Core Functionality
- **URL Shortening**: Create short, memorable URLs from long links
- **Custom Codes**: Use personalized short codes for branded links  
- **Instant Redirects**: Fast 301 redirects to original destinations
- **Real-time Stats**: Track creation and redirect metrics

### Production Infrastructure
- **Cloud Deployment**: Hosted on Render with automatic deployments
- **Monitoring Stack**: Prometheus + Grafana + Node Exporter
- **Alert System**: Proactive notifications for service issues
- **Performance Tracking**: Request duration, success rates, and throughput

### DevOps Features
- **CI/CD Pipeline**: Automated testing and deployment via GitHub Actions
- **Docker Containerization**: Consistent environments across development and production
- **Health Checks**: Built-in service monitoring and availability checks
- **Hybrid Architecture**: Production service + local monitoring infrastructure

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────┐
│   Prometheus    │───▶│ URL Shortener│───▶│   Grafana   │
│  (localhost)    │    │   (Render)   │    │ (localhost) │
└─────────────────┘    └──────────────┘    └─────────────┘
```

### Components

| Component | Location | Purpose |
|-----------|----------|---------|
| **URL Shortener API** | Render Cloud | Core service handling URL creation and redirects |
| **Prometheus** | Local Docker | Metrics collection and storage |
| **Grafana** | Local Docker | Data visualization and dashboards |
| **Node Exporter** | Local Docker | System metrics monitoring |

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Git
- Python 3.11+ (for local development)

### 1. Clone and Setup
```bash
git clone https://github.com/eliorabaev/DevopsFinal.git
cd DevopsFinal
```

### 2. Start Monitoring Stack
```bash
docker-compose up -d
```

### 3. Access Services
- **Grafana Dashboard**: http://localhost:3000
- **Prometheus**: http://localhost:9090  
- **Production API**: https://url-shortener-latest-gccb.onrender.com

## 📡 Using the Service

### Create a Short URL

**Basic URL shortening:**
```bash
curl -X POST "https://url-shortener-latest-gccb.onrender.com/shorten" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.google.com"}'
```

**Response:**
```json
{
  "short_url": "https://url-shortener-latest-gccb.onrender.com/WTWlVB",
  "original_url": "https://www.google.com/",
  "short_code": "WTWlVB"
}
```

**Custom short code:**
```bash
curl -X POST "https://url-shortener-latest-gccb.onrender.com/shorten" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.github.com", "custom_code": "github"}'
```

### Use a Short URL

Simply visit the short URL in your browser or use curl:
```bash
curl -L "https://url-shortener-latest-gccb.onrender.com/github"
```

### Check Service Stats
```bash
curl "https://url-shortener-latest-gccb.onrender.com/stats"
```

**Response:**
```json
{
  "total_urls": 15,
  "total_redirects": 42,
  "total_urls_created": 15
}
```

## 📊 Monitoring Dashboard

### Accessing Grafana
1. Open http://localhost:3000
2. Default credentials: `admin` / `admin`
3. Navigate to the "URL Shortener" dashboard

### Key Metrics
- **Service Availability**: Real-time uptime monitoring
- **Request Volume**: URLs created and redirects per minute
- **Response Times**: Performance percentiles (50th, 95th)
- **Error Rates**: Failed requests and alerts
- **System Resources**: CPU, memory, and disk usage

### Alert Categories
- **Service Health**: API downtime or slow responses
- **Business Logic**: Unusual traffic patterns or errors
- **System Resources**: High CPU/memory usage on monitoring host
- **Render-Specific**: Cold start detection and inactivity warnings

## 🛠️ Development Setup

### Local API Development
```bash
# Navigate to app directory
cd app

# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Testing
```bash
# Run tests
pytest app/tests/ -v

# With coverage
pytest app/tests/ --cov=app
```

### Docker Development
```bash
# Build image
docker build -t url-shortener ./app

# Run container
docker run -p 8000:8000 url-shortener
```

## 📚 API Documentation

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API information and health check |
| `POST` | `/shorten` | Create a new short URL |
| `GET` | `/{short_code}` | Redirect to original URL |
| `GET` | `/stats` | Service statistics |
| `GET` | `/metrics` | Prometheus metrics |

### Interactive Documentation
Visit the live API documentation: [https://url-shortener-latest-gccb.onrender.com/docs](https://url-shortener-latest-gccb.onrender.com/docs)

### Request/Response Examples

**Create URL Request:**
```json
{
  "url": "https://www.example.com/very/long/path?param=value",
  "custom_code": "example"  // Optional
}
```

**Success Response (200):**
```json
{
  "short_url": "https://url-shortener-latest-gccb.onrender.com/example",
  "original_url": "https://www.example.com/very/long/path?param=value",
  "short_code": "example"
}
```

**Error Response (400):**
```json
{
  "detail": "Custom code already exists"
}
```

## 🔄 CI/CD Pipeline

### Automated Workflow
1. **Pull Request**: Triggers CI pipeline
   - Code formatting check (Black)
   - Linting (Flake8)  
   - Unit tests (Pytest)
   - Docker image build

2. **Merge to Main**: Triggers CD pipeline
   - Build and push Docker image to Docker Hub
   - Trigger Render deployment via webhook
   - Service automatically updates with new version

### Pipeline Configuration
- **CI**: `.github/workflows/ci.yml`
- **CD**: `.github/workflows/cd.yml`
- **Deployment**: Render auto-deploy from Docker Hub

### Required Secrets
```
DOCKERHUB_USERNAME    # Docker Hub credentials
DOCKERHUB_TOKEN       # Docker Hub access token
RENDER_DEPLOY_HOOK    # Render deployment webhook URL
```

## 🔧 Troubleshooting

### Common Issues

**Service is Down (Render)**
- Check Render dashboard for service status
- Verify deployment logs in Render console
- Service may be sleeping (free tier) - make a request to wake it up

**Monitoring Not Working**
```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs prometheus
docker-compose logs grafana

# Restart services
docker-compose restart
```

**No Data in Grafana**
1. Verify Prometheus is scraping: http://localhost:9090/targets
2. Check if URL shortener service is accessible
3. Confirm Prometheus configuration in `monitoring/prometheus/prometheus.yml`

**High Response Times**
- Render free tier may experience cold starts
- Check Grafana dashboard for service performance
- Monitor CPU/memory usage on local machine

### Health Checks
```bash
# Test API connectivity
curl "https://url-shortener-latest-gccb.onrender.com/"

# Check Prometheus metrics
curl "http://localhost:9090/-/healthy"

# Verify Grafana
curl "http://localhost:3000/api/health"
```

### Log Locations
- **Application Logs**: Render dashboard
- **Prometheus Logs**: `docker-compose logs prometheus`
- **Grafana Logs**: `docker-compose logs grafana`

## 🙏 Acknowledgments


- **Saar Salhov** ([@saarsalhov](https://github.com/saarsalhov)) the best DevOps mentor. Thank you for everything!

---

**Live Demo:** Try the service at [https://url-shortener-latest-gccb.onrender.com](https://url-shortener-latest-gccb.onrender.com)