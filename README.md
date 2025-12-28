# P2Pool Log Viewer API

A simple Docker-based Flask application for viewing P2Pool mining logs with a retro v0-style UI and RESTful APIs for miner controller software.

## Features

- 🎨 **Retro v0-style Terminal UI** - Green-on-black aesthetic
- 📁 **Volume-based Architecture**
  - `/config` - Read/write volume for application configuration
  - `/data` - Read-only volume for P2Pool logs
- 🔍 **Web Interface** - Browse and view log files with one page per log
- 🔌 **RESTful APIs** - Consume logs programmatically for miner controllers
- 🐳 **Docker Ready** - Easy deployment with Docker Compose

## Quick Start

### Option 1: Using Pre-built Image from GitHub

```bash
# Pull the latest image
docker pull ghcr.io/OWNER/p2pool-api:latest

# Run with docker-compose (update image in docker-compose.yml)
docker-compose up -d
```

### Option 2: Build Locally

#### 1. Clone or create the project structure

```bash
mkdir -p p2pool-logs config
```

#### 2. Build and run with Docker Compose

```bash
docker-compose up -d --build
```

### 3. Access the application

- **Web UI**: http://localhost:5000
- **API Status**: http://localhost:5000/api/status
- **Health Check**: http://localhost:5000/health

## Configuration

### Mount P2Pool Logs

Edit `docker-compose.yml` to point to your P2Pool logs:

```yaml
volumes:
  - /path/to/your/p2pool-logs:/data:ro
```

Or share logs from another container (see commented example in docker-compose.yml).

### Port Configuration

Change the exposed port in `docker-compose.yml`:

```yaml
ports:
  - "8080:5000"  # Access on port 8080
```

## API Endpoints

All API endpoints return JSON responses.

### List All Logs
```bash
GET /api/logs
```

**Response:**
```json
{
  "success": true,
  "logs": [
    {
      "name": "p2pool.log",
      "path": "/data/p2pool.log",
      "size": 1048576,
      "modified": "2025-12-28T10:30:00"
    }
  ],
  "count": 1
}
```

### Get Full Log Content
```bash
GET /api/log/{filename}
```

**Response:**
```json
{
  "success": true,
  "filename": "p2pool.log",
  "content": "log content here...",
  "lines": 1234
}
```

### Tail Log (Last N Lines)
```bash
GET /api/log/{filename}/tail
GET /api/log/{filename}/tail/50
```

**Response:**
```json
{
  "success": true,
  "filename": "p2pool.log",
  "lines": ["line 1", "line 2", "..."],
  "count": 50
}
```

### Search Log
```bash
GET /api/log/{filename}/search/{query}
```

**Response:**
```json
{
  "success": true,
  "filename": "p2pool.log",
  "query": "error",
  "matches": [
    {
      "line_number": 42,
      "content": "ERROR: Connection failed"
    }
  ],
  "count": 1
}
```

### System Status
```bash
GET /api/status
```

**Response:**
```json
{
  "success": true,
  "status": "online",
  "data_dir": "/data",
  "config_dir": "/config",
  "log_count": 5,
  "timestamp": "2025-12-28T10:30:00"
}
```

## Development

### Run locally without Docker

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATA_DIR=./p2pool-logs
export CONFIG_DIR=./config

# Run the app
python app.py
```

### Build Docker image manually

```bash
docker build -t p2pool-api .
docker run -d -p 5000:5000 \
  -v $(pwd)/config:/config \
  -v /path/to/p2pool-logs:/data:ro \
  p2pool-api
```

## Miner Controller Integration

Example Python code to integrate with miner controller:

```python
import requests

API_URL = "http://localhost:5000"

# Check if P2Pool is running
def check_p2pool_status():
    response = requests.get(f"{API_URL}/api/status")
    data = response.json()
    return data['status'] == 'online'

# Get recent logs
def get_recent_logs(filename, lines=100):
    response = requests.get(f"{API_URL}/api/log/{filename}/tail/{lines}")
    return response.json()

# Search for errors
def find_errors(filename):
    response = requests.get(f"{API_URL}/api/log/{filename}/search/error")
    return response.json()['matches']
```

## File Structure

```
p2pool-api/
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker image definition
├── docker-compose.yml    # Docker Compose configuration
├── templates/            # HTML templates
│   ├── base.html        # Base template with v0 styling
│   ├── index.html       # Log list page
│   └── log_view.html    # Individual log viewer
├── config/              # Application configuration (mounted)
└── p2pool-logs/         # P2Pool logs directory (mounted)
```

## License

MIT License - feel free to use and modify as needed.

## Docker Image

### Automated Builds

Docker images are automatically built and published to GitHub Container Registry on every push to main/master:

- **Latest**: `ghcr.io/OWNER/p2pool-api:latest`
- **Tagged releases**: `ghcr.io/OWNER/p2pool-api:v1.0.0`
- **Branch builds**: `ghcr.io/OWNER/p2pool-api:main`

Replace `OWNER` with your GitHub username or organization.

### Multi-Architecture Support

Images are built for:
- `linux/amd64` (x86_64)
- `linux/arm64` (ARM64/aarch64)

### Using Pre-built Images

Update your `docker-compose.yml`:

```yaml
services:
  p2pool-api:
    image: ghcr.io/OWNER/p2pool-api:latest
    # Remove the 'build: .' line
    container_name: p2pool-api
    # ... rest of configuration
```

## Contributing

Contributions welcome! This is a simple tool designed to be easily extended.
