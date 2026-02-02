# Installation Guide - Wazz Shared Library

## Quick Start

### Step 1: Install the Package

From your API service or Worker service directory:

```bash
# Navigate to your service directory
cd /path/to/api-service
# or
cd /path/to/worker-service

# Install shared library in editable mode
pip install -e ../shared-lib
```

**Why `-e` (editable mode)?**
- Changes to shared library are immediately reflected
- No need to reinstall after updates
- Perfect for development

### Step 2: Verify Installation

```bash
python -c "from wazz_shared import get_shared_settings; print('Success!')"
```

### Step 3: Configure Environment

Copy the example environment file:

```bash
cp ../shared-lib/.env.example .env
```

Edit `.env` with your settings:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/whazz_audio
USE_LOCAL_STORAGE=true
RABBITMQ_URL=amqp://guest:guest@localhost:5672//
```

### Step 4: Test the Library

Run the example script:

```bash
cd ../shared-lib
python examples/usage_example.py
```

## Installation for Different Scenarios

### For Development (Recommended)

Install in editable mode so you can modify the shared code:

```bash
# From api-service/
pip install -e ../shared-lib

# From worker-service/
pip install -e ../shared-lib
```

### For Production (Docker)

In your Dockerfile:

```dockerfile
# Copy shared library
COPY shared-lib /shared-lib

# Install shared library
RUN pip install /shared-lib

# Or for editable mode in Docker:
RUN pip install -e /shared-lib
```

### For CI/CD

In your CI pipeline:

```bash
# Install shared library before running tests
pip install -e ./shared-lib
pip install -r api-service/requirements.txt
pytest api-service/tests
```

## Updating Requirements

When you update the shared library, ensure both services reinstall:

```bash
# Force reinstall
pip install -e ../shared-lib --force-reinstall --no-deps

# Or uninstall and reinstall
pip uninstall wazz-shared -y
pip install -e ../shared-lib
```

## Troubleshooting

### Import Error: "No module named 'wazz_shared'"

```bash
# Check if installed
pip list | grep wazz-shared

# If not found, install it
pip install -e ../shared-lib
```

### Import Error: "cannot import name 'X' from 'wazz_shared'"

The `__init__.py` might not export that component. Check:

```python
# In wazz_shared/__init__.py
__all__ = [
    "SharedSettings",
    "get_shared_settings",
    # ... add your import here
]
```

### Database Connection Error

```bash
# Test database connection
python -c "
from wazz_shared.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT 1'))
    print('Database connected!', result.fetchone())
"
```

### Storage Client Error

```bash
# Test storage client
python -c "
from wazz_shared.storage import get_storage_client
storage = get_storage_client()
print('Storage type:', 'Local' if storage.use_local else 'S3/MinIO')
"
```

## Requirements Installation Order

Install in this order to avoid conflicts:

```bash
# 1. Install shared library
pip install -e ../shared-lib

# 2. Install service-specific requirements
pip install -r requirements.txt
```

## Using with Poetry

If using Poetry for dependency management:

```toml
# In pyproject.toml
[tool.poetry.dependencies]
wazz-shared = {path = "../shared-lib", develop = true}
```

Then run:

```bash
poetry install
```

## Using with pipenv

```bash
# Add to Pipfile
pipenv install -e ../shared-lib
```

## Verifying Installation

Create a test script:

```python
# test_install.py
from wazz_shared import (
    get_shared_settings,
    Base,
    User,
    AudioProcessingJob,
    get_storage_client
)

print("✓ Config imported")
print("✓ Database imported")
print("✓ Models imported")
print("✓ Storage imported")

settings = get_shared_settings()
print(f"✓ Settings loaded: {settings.app_name}")

print("\n✅ All imports successful!")
```

Run it:

```bash
python test_install.py
```

## Next Steps

After installation:

1. **Configure environment**: Copy `.env.example` to `.env` and update values
2. **Create database**: Run migrations to create tables
3. **Test storage**: Verify local or S3 storage is accessible
4. **Run examples**: Try `python examples/usage_example.py`
5. **Update your code**: Replace old imports with `wazz_shared` imports

## Common Installation Patterns

### API Service + Worker Service Setup

```bash
# Project structure
wazz-audio/
├── shared-lib/
├── api-service/
└── worker-service/

# Install in API service
cd api-service
pip install -e ../shared-lib
pip install -r requirements.txt

# Install in Worker service
cd ../worker-service
pip install -e ../shared-lib
pip install -r requirements.txt
```

### Docker Compose Setup

```yaml
# docker-compose.yml
services:
  api:
    build:
      context: .
      dockerfile: api-service/Dockerfile
    volumes:
      - ./shared-lib:/shared-lib  # Mount for development

  worker:
    build:
      context: .
      dockerfile: worker-service/Dockerfile
    volumes:
      - ./shared-lib:/shared-lib  # Mount for development
```

## Maintenance

### Checking Installed Version

```bash
pip show wazz-shared
```

### Upgrading Dependencies

```bash
cd shared-lib
pip install --upgrade -r requirements.txt
```

### Testing After Changes

```bash
cd shared-lib
pytest  # If you have tests
```

## Getting Help

- Check the main [README.md](README.md) for usage examples
- Review [examples/usage_example.py](examples/usage_example.py)
- Ensure environment variables are set correctly (see `.env.example`)
