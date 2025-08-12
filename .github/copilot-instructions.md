# Copilot Instructions - CryptUSBee

## 🏗️ Architecture Overview

CryptUSBee is a **triple-factor authentication system** using USB tokens with RSA encryption. The architecture follows a **microservices pattern** with 5 Docker containers:

- **nginx**: Reverse proxy (port 80)
- **app**: Flask web interface (port 5000) 
- **api**: FastAPI backend (port 8000)
- **mongodb**: NoSQL for encrypted user data
- **postgres**: SQL for validation keys and organization data

## 🔑 Key Components

### Authentication Flow
The system implements **3-factor security**: "What I know" (password) + "What I have" (USB token) + "What I am" (biometric - optional).

**USB Token Creation Process** (`api/keys_creation/key_create.py`):
1. Generate RSA 2048-bit key pairs
2. Encrypt unique identifier with public key
3. Store keys on USB with specific folder structure: `KEY_FOLDER/IDENTIFIER_FILE` and `PUBLIC_KEY_FILE`

### Service Architecture
- **Interface Service** (`interface/application.py`): Flask app with Blueprint routing
- **API Service** (`api/back_workers.py`): FastAPI with health checks
- **Routes Pattern**: Separate blueprints for `home`, `admin`, and `links` in `interface/routes/`

## 🛠️ Development Workflows

### Container Management
```bash
# Start all services
docker-compose up -d

# Check health status
docker-compose ps

# View logs
docker-compose logs -f [service_name]
```

### Testing
```bash
# Run tests with pytest
python -m pytest api/tests/

# Specific test file
python -m pytest api/tests/test_key_create.py
```

### CI/CD Pipeline
GitHub Actions workflow (`.github/workflows/python-app.yml`) runs on `main` and `Interfaces_fonctions` branches:
- Python 3.12 setup
- Dependency installation from `requirements.txt`
- Flake8 linting with specific error codes: E9,F63,F7,F82
- Docker container validation

## 📁 Project Conventions

### File Structure Patterns
- **Routes**: Blueprint pattern with dedicated static/template folders per route type
- **Environment Variables**: Docker Compose uses `.env` for database credentials
- **Health Checks**: All services implement `/health` endpoints for container orchestration
- **Dependencies**: Separate `requirements.txt` (root) and `interface/requirements-app.txt`

### Code Patterns
- **Type Hints**: Consistent use of `typing` module (e.g., `Dict[str, Any]`, `List[Dict[str, Any]]`)
- **Error Handling**: Cross-platform USB detection with `psutil` fallback
- **Network Detection**: IP-based local network detection (`192.168.*`) in Flask `before_request`
- **Session Management**: Flask sessions with `g.need_connection` pattern

### Database Strategy
- **MongoDB**: Encrypted user tokens and sensitive data
- **PostgreSQL**: Organization keys and validation data
- **Dual Database Pattern**: SQL for structured validation, NoSQL for encrypted blobs

## 🔧 Integration Points

### Container Dependencies
Services use `depends_on` with health conditions:
```yaml
depends_on:
  mongodb:
    condition: service_healthy
  postgres:
    condition: service_healthy
```

### Cross-Service Communication
- Nginx proxies requests to Flask (5000) and FastAPI (8000)
- API and Interface share network (`bee-net`)
- Volume mounts for development: `./api:/usr/src/api` and `./interface:/app`

### USB Integration
USB detection uses `psutil.disk_partitions()` with filesystem type checking (`vfat`, `exfat`, `ntfs`) and removable media detection.

## 🚨 Security Considerations

When working with cryptographic components:
- RSA keys are 2048-bit minimum
- Use `Crypto.Cipher.PKCS1_OAEP` for encryption
- USB label matching for device identification
- Environment variables for sensitive database credentials
