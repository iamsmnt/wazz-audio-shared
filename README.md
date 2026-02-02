# Wazz Audio Shared Library

This package contains shared code used by both the **API Service** and **Worker Service** in the Wazz Audio application. It provides common database models, configuration, storage abstraction, and schemas.

## Purpose

The shared library enables:
- **Code Reusability**: Single source of truth for models and schemas
- **Consistency**: Both services use identical database schemas and configurations
- **Decoupling**: Services can be deployed independently while sharing core logic
- **Maintainability**: Update shared code in one place

## Installation

### For Development (Editable Mode)

Install the shared library in editable mode so changes are immediately reflected:

```bash
# From the api-service or worker-service directory
pip install -e ../shared-lib
```

### For Production

Install as a regular package:

```bash
pip install /path/to/shared-lib
```

Or add to your `requirements.txt`:

```txt
# In api-service/requirements.txt or worker-service/requirements.txt
-e ../shared-lib
```

## Components

### 1. Configuration (`config.py`)

Centralized configuration for all services using Pydantic settings.

**Usage:**

```python
from wazz_shared.config import get_shared_settings

settings = get_shared_settings()

# Access settings
print(settings.database_url)
print(settings.s3_bucket_name)
print(settings.max_file_size_mb)
```

**Environment Variables:**

All settings can be overridden via environment variables or `.env` file:

```env
# .env file
DATABASE_URL=postgresql://user:pass@localhost:5432/mydb
S3_ENDPOINT_URL=http://minio:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
USE_LOCAL_STORAGE=false
MAX_FILE_SIZE_MB=200
```

### 2. Database Models (`models.py`)

SQLAlchemy ORM models for all database tables.

**Available Models:**
- `User` - User accounts
- `TokenBlacklist` - Invalidated JWT tokens
- `GuestSession` - Guest user sessions
- `UserUsageStats` - Usage tracking
- `AudioProcessingJob` - Audio processing jobs

**Usage:**

```python
from wazz_shared.models import User, AudioProcessingJob
from wazz_shared.database import SessionLocal

db = SessionLocal()

# Query users
user = db.query(User).filter(User.email == "user@example.com").first()

# Create job
job = AudioProcessingJob(
    filename="audio.wav",
    user_id=user.id,
    status="pending"
)
db.add(job)
db.commit()
```

### 3. Database Connection (`database.py`)

Database session management and connection.

**Usage:**

```python
from wazz_shared.database import get_db, SessionLocal, Base, engine

# Create all tables
Base.metadata.create_all(bind=engine)

# Use in FastAPI dependency
from fastapi import Depends
from sqlalchemy.orm import Session

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

# Use directly in workers
db = SessionLocal()
try:
    # Do work
    job = db.query(AudioProcessingJob).first()
finally:
    db.close()
```

### 4. Storage Client (`storage.py`)

Unified interface for file storage supporting both local filesystem and S3/MinIO.

**Usage:**

```python
from wazz_shared.storage import get_storage_client
from wazz_shared.config import get_shared_settings

settings = get_shared_settings()
storage = get_storage_client(settings)

# Upload file
storage.upload_file('/path/to/audio.wav', 'uploads/audio.wav')

# Upload file object
with open('/path/to/audio.wav', 'rb') as f:
    storage.upload_fileobj(f, 'uploads/audio.wav')

# Download file
storage.download_file('uploads/audio.wav', '/tmp/audio.wav')

# Check existence
if storage.file_exists('uploads/audio.wav'):
    print("File exists!")

# Get file URL (presigned for S3, local path for filesystem)
url = storage.get_file_url('uploads/audio.wav', expiration=3600)

# Delete file
storage.delete_file('uploads/audio.wav')

# List files
files = storage.list_files(prefix='uploads/')
```

**Toggle Storage Backend:**

```python
# In .env or environment variables
USE_LOCAL_STORAGE=true   # Use local filesystem (development)
USE_LOCAL_STORAGE=false  # Use S3/MinIO (production)
```

### 5. Pydantic Schemas (`schemas.py`)

Request/response validation schemas.

**Usage:**

```python
from wazz_shared.schemas import (
    UserCreate,
    UserResponse,
    AudioUploadResponse,
    AudioJobStatusResponse
)

# Validate user creation
user_data = UserCreate(
    email="user@example.com",
    username="testuser",
    password="securepassword123"
)

# FastAPI response model
from fastapi import APIRouter

router = APIRouter()

@router.get("/jobs/{job_id}", response_model=AudioJobStatusResponse)
def get_job(job_id: str):
    # Returns validated response
    return job
```

## Project Structure

```
shared-lib/
├── setup.py                    # Package installation configuration
├── requirements.txt            # Package dependencies
├── README.md                   # This file
└── wazz_shared/               # Main package
    ├── __init__.py            # Package exports
    ├── config.py              # Shared configuration
    ├── database.py            # Database connection
    ├── models.py              # SQLAlchemy models
    ├── schemas.py             # Pydantic schemas
    └── storage.py             # Storage abstraction
```

## Configuration Guide

### Database Configuration

```python
# PostgreSQL (recommended for production)
DATABASE_URL=postgresql://user:pass@localhost:5432/wazz_audio

# Or set individual components
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=wazz_audio
```

### Storage Configuration

**Local Filesystem (Development):**

```env
USE_LOCAL_STORAGE=true
UPLOAD_DIR=./uploads
OUTPUT_DIR=./processed_audio
```

**S3/MinIO (Production):**

```env
USE_LOCAL_STORAGE=false
S3_ENDPOINT_URL=http://minio:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET_NAME=wazz-audio
S3_REGION=us-east-1
```

**AWS S3:**

```env
USE_LOCAL_STORAGE=false
S3_ENDPOINT_URL=  # Leave empty for AWS S3
S3_ACCESS_KEY=YOUR_AWS_ACCESS_KEY_ID
S3_SECRET_KEY=YOUR_AWS_SECRET_ACCESS_KEY
S3_BUCKET_NAME=wazz-audio-production
S3_REGION=us-east-1
S3_USE_SSL=true
```

### Message Broker Configuration

```env
RABBITMQ_URL=amqp://guest:guest@localhost:5672//
CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//
CELERY_RESULT_BACKEND=db+postgresql://postgres:postgres@localhost:5432/whazz_audio
```

## Usage in API Service

```python
# api-service/main.py
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from wazz_shared import get_db, get_shared_settings
from wazz_shared.models import User
from wazz_shared.schemas import UserResponse
from wazz_shared.storage import get_storage_client

app = FastAPI()
settings = get_shared_settings()
storage = get_storage_client(settings)

@app.get("/users", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@app.post("/upload")
async def upload_file(file: UploadFile, db: Session = Depends(get_db)):
    # Upload to storage
    storage.upload_fileobj(file.file, f"uploads/{file.filename}")

    # Create job record
    job = AudioProcessingJob(
        filename=file.filename,
        status="pending"
    )
    db.add(job)
    db.commit()

    return {"job_id": job.job_id}
```

## Usage in Worker Service

```python
# worker-service/tasks/audio_processing.py
from celery import Task
from wazz_shared.database import SessionLocal
from wazz_shared.models import AudioProcessingJob
from wazz_shared.config import get_shared_settings
from wazz_shared.storage import get_storage_client

settings = get_shared_settings()
storage = get_storage_client(settings)

@celery_app.task
def process_audio_task(job_id: str):
    db = SessionLocal()

    try:
        # Fetch job
        job = db.query(AudioProcessingJob).filter(
            AudioProcessingJob.job_id == job_id
        ).first()

        # Download from storage
        local_path = f"/tmp/{job.filename}"
        storage.download_file(job.input_file_path, local_path)

        # Process audio
        # ...

        # Upload result
        storage.upload_file(output_path, f"processed/{job.job_id}.wav")

        # Update job
        job.status = "completed"
        db.commit()

    finally:
        db.close()
```

## Development

### Running Tests

```bash
cd shared-lib
pip install -e ".[dev]"
pytest
```

### Making Changes

1. Make changes to shared library code
2. Both API and Worker services will automatically use the updated code (if installed in editable mode with `-e`)
3. Run tests to ensure compatibility
4. Update version in `setup.py` if needed

## Migration from Monolith

If you're migrating from a monolithic backend:

1. **Install shared library** in both services:
   ```bash
   pip install -e ../shared-lib
   ```

2. **Update imports** in API service:
   ```python
   # Old
   from models import User
   from database import get_db
   from config import get_settings

   # New
   from wazz_shared.models import User
   from wazz_shared.database import get_db
   from wazz_shared.config import get_shared_settings
   ```

3. **Update imports** in Worker service:
   ```python
   # Old
   from models import AudioProcessingJob
   from database import SessionLocal

   # New
   from wazz_shared.models import AudioProcessingJob
   from wazz_shared.database import SessionLocal
   ```

4. **Update storage** to use `StorageClient`:
   ```python
   # Old
   with open(file_path, 'wb') as f:
       shutil.copyfileobj(file.file, f)

   # New
   from wazz_shared.storage import get_storage_client
   storage = get_storage_client()
   storage.upload_fileobj(file.file, object_key)
   ```

## Best Practices

1. **Version Control**: Tag releases of shared library for production deployments
2. **Environment Variables**: Use `.env` files for local development, env vars for production
3. **Database Migrations**: Run migrations from API service (it owns the schema)
4. **Storage Toggle**: Use `USE_LOCAL_STORAGE=true` for development, `false` for production
5. **Logging**: Configure logging level via `LOG_LEVEL` environment variable

## Troubleshooting

### Import Errors

```bash
# Reinstall in editable mode
pip install -e ../shared-lib --force-reinstall
```

### Database Connection Issues

```python
# Test database connection
from wazz_shared.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    print(result.fetchone())
```

### S3 Connection Issues

```python
# Test S3 connection
from wazz_shared.storage import get_storage_client

storage = get_storage_client()
print(storage.list_files())
```

## License

This is a private internal library for the Wazz Audio project.
