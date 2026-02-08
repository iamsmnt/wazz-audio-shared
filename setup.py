"""
Wazz Audio Shared Library
Shared code between API service and Worker service
"""
from setuptools import setup, find_packages

setup(
    name="wazz-shared",
    version="1.0.0",
    description="Shared library for Wazz Audio services",
    author="Wazz Audio Team",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "sqlalchemy>=2.0.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "psycopg2-binary>=2.9.0",
        "boto3>=1.26.0",  # For S3/MinIO
        "python-dotenv>=1.0.0",
        "pika>=1.3.0",  # For RabbitMQ event publishing
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ]
    },
)
