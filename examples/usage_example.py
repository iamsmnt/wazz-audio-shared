"""
Example usage of wazz_shared library

This file demonstrates how to use the shared library components.
Run this after installing the shared library:
    pip install -e /path/to/shared-lib
"""

from wazz_shared.config import get_shared_settings
from wazz_shared.database import SessionLocal, Base, engine
from wazz_shared.models import User, AudioProcessingJob
from wazz_shared.storage import get_storage_client
from wazz_shared.schemas import UserCreate, AudioUploadResponse
import uuid


def example_config():
    """Example: Using shared configuration"""
    print("\n=== Configuration Example ===")

    settings = get_shared_settings()

    print(f"App Name: {settings.app_name}")
    print(f"Database URL: {settings.database_url}")
    print(f"Using Local Storage: {settings.use_local_storage}")
    print(f"Max File Size: {settings.max_file_size_mb}MB")
    print(f"Allowed Formats: {settings.allowed_audio_formats}")


def example_database():
    """Example: Database operations"""
    print("\n=== Database Example ===")

    # Create tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created")

    # Create a session
    db = SessionLocal()

    try:
        # Create a user
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password_here",
            is_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Created user: {user.username} (ID: {user.id})")

        # Query users
        all_users = db.query(User).all()
        print(f"Total users: {len(all_users)}")

        # Create a job
        job = AudioProcessingJob(
            filename="test.wav",
            original_filename="original_test.wav",
            file_size=1024000,
            file_format="wav",
            input_file_path="uploads/test.wav",
            user_id=user.id,
            status="pending"
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        print(f"Created job: {job.job_id} (Status: {job.status})")

        # Query jobs
        pending_jobs = db.query(AudioProcessingJob).filter(
            AudioProcessingJob.status == "pending"
        ).all()
        print(f"Pending jobs: {len(pending_jobs)}")

    finally:
        db.close()


def example_storage():
    """Example: Storage operations"""
    print("\n=== Storage Example ===")

    settings = get_shared_settings()
    storage = get_storage_client(settings)

    # Create a test file
    test_content = b"This is a test audio file content"
    test_file_path = "/tmp/test_audio.txt"

    with open(test_file_path, 'wb') as f:
        f.write(test_content)

    # Upload file
    object_key = "uploads/test_audio.txt"
    storage.upload_file(test_file_path, object_key)
    print(f"Uploaded file to: {object_key}")

    # Check if file exists
    exists = storage.file_exists(object_key)
    print(f"File exists: {exists}")

    # Get file size
    if exists:
        size = storage.get_file_size(object_key)
        print(f"File size: {size} bytes")

    # Get file URL
    url = storage.get_file_url(object_key)
    print(f"File URL: {url}")

    # List files
    files = storage.list_files(prefix="uploads/")
    print(f"Files in uploads/: {files}")

    # Download file
    download_path = "/tmp/downloaded_audio.txt"
    storage.download_file(object_key, download_path)
    print(f"Downloaded file to: {download_path}")

    # Delete file
    storage.delete_file(object_key)
    print(f"Deleted file: {object_key}")

    # Verify deletion
    exists_after = storage.file_exists(object_key)
    print(f"File exists after deletion: {exists_after}")


def example_schemas():
    """Example: Pydantic schema validation"""
    print("\n=== Schema Example ===")

    # Create user schema
    user_data = UserCreate(
        email="newuser@example.com",
        username="newuser",
        password="securepassword123"
    )
    print(f"Valid user data: {user_data.model_dump()}")

    # Try invalid data
    try:
        invalid_user = UserCreate(
            email="invalid-email",  # Invalid email format
            username="ab",  # Too short
            password="short"  # Too short
        )
    except Exception as e:
        print(f"Validation error (expected): {str(e)[:100]}...")

    # Audio upload response schema
    response = AudioUploadResponse(
        job_id=str(uuid.uuid4()),
        status="pending",
        filename="audio.wav",
        original_filename="my_audio.wav",
        file_size=1024000,
        file_format="wav",
        created_at="2024-01-18T10:00:00",
        expires_at="2024-01-19T10:00:00",
        message="Upload successful"
    )
    print(f"Audio upload response: {response.model_dump_json()[:100]}...")


def main():
    """Run all examples"""
    print("=" * 60)
    print("Wazz Shared Library - Usage Examples")
    print("=" * 60)

    try:
        example_config()
        example_storage()
        example_schemas()
        # example_database()  # Uncomment if you have a database running

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
