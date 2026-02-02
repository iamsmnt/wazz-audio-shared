# Quick Start Guide - Wazz Shared Library

Get up and running in 5 minutes!

## 1️⃣ Install (30 seconds)

```bash
# From your api-service or worker-service directory
pip install -e ../shared-lib
```

## 2️⃣ Configure (1 minute)

Create a `.env` file:

```bash
# Copy the example
cp ../shared-lib/.env.example .env
```

Edit `.env` with your settings:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/whazz_audio
USE_LOCAL_STORAGE=true
RABBITMQ_URL=amqp://guest:guest@localhost:5672//
```

## 3️⃣ Use in Your Code (2 minutes)

### Import Components

```python
from wazz_shared import (
    get_shared_settings,
    get_db,
    User,
    AudioProcessingJob
)
from wazz_shared.storage import get_storage_client
```

### Get Settings

```python
settings = get_shared_settings()
print(settings.database_url)
print(settings.max_file_size_mb)
```

### Use Database

```python
from fastapi import Depends
from sqlalchemy.orm import Session

@app.get("/users")
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

### Use Storage

```python
storage = get_storage_client()

# Upload file
storage.upload_file("/path/to/file.wav", "uploads/file.wav")

# Download file
storage.download_file("uploads/file.wav", "/tmp/file.wav")

# Check if exists
if storage.file_exists("uploads/file.wav"):
    print("File exists!")

# Delete file
storage.delete_file("uploads/file.wav")
```

## 4️⃣ Test (1 minute)

Run the example script:

```bash
cd ../shared-lib
python examples/usage_example.py
```

You should see:
```
=== Configuration Example ===
App Name: Whazz Audio
Database URL: postgresql://...
Using Local Storage: True

=== Storage Example ===
Uploaded file to: uploads/test_audio.txt
File exists: True
...
```

## 5️⃣ Verify Installation

Quick test:

```python
python -c "
from wazz_shared import get_shared_settings
settings = get_shared_settings()
print('✅ Shared library is working!')
print(f'App: {settings.app_name}')
"
```

## Common Tasks

### Upload a File

```python
from wazz_shared.storage import get_storage_client

storage = get_storage_client()

# From file path
storage.upload_file("/local/file.wav", "uploads/file.wav")

# From file object (FastAPI)
@app.post("/upload")
async def upload(file: UploadFile):
    storage.upload_fileobj(file.file, f"uploads/{file.filename}")
    return {"status": "uploaded"}
```

### Create a Database Record

```python
from wazz_shared.database import SessionLocal
from wazz_shared.models import AudioProcessingJob

db = SessionLocal()

job = AudioProcessingJob(
    filename="audio.wav",
    original_filename="my_audio.wav",
    file_size=1024000,
    status="pending"
)

db.add(job)
db.commit()
db.refresh(job)

print(f"Created job: {job.job_id}")
db.close()
```

### Query the Database

```python
from wazz_shared.database import SessionLocal
from wazz_shared.models import AudioProcessingJob

db = SessionLocal()

# Get all pending jobs
pending = db.query(AudioProcessingJob).filter(
    AudioProcessingJob.status == "pending"
).all()

print(f"Found {len(pending)} pending jobs")
db.close()
```

### Switch Storage Backend

Development (local filesystem):
```env
USE_LOCAL_STORAGE=true
```

Production (S3/MinIO):
```env
USE_LOCAL_STORAGE=false
S3_ENDPOINT_URL=http://minio:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
```

No code changes needed! The same API works for both.

## Troubleshooting

### "No module named 'wazz_shared'"

```bash
# Install the library
pip install -e ../shared-lib
```

### "Connection refused" (Database)

```bash
# Check if PostgreSQL is running
psql -h localhost -U postgres -d whazz_audio

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://user:pass@host:port/database
```

### Storage not working

```bash
# For local storage, check paths
USE_LOCAL_STORAGE=true

# For S3, check credentials
USE_LOCAL_STORAGE=false
S3_ENDPOINT_URL=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
```

## Next Steps

- 📖 Read the full [README.md](README.md)
- 🔧 Check [INSTALLATION.md](INSTALLATION.md) for advanced setup
- 📝 Review [examples/usage_example.py](examples/usage_example.py)
- 🎯 See [SUMMARY.md](SUMMARY.md) for complete overview

## That's It! 🎉

You're ready to use the shared library in both your API service and Worker service!

**Need help?** Check the documentation files listed above.
