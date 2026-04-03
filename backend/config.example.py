import json
from pathlib import Path

# Database configuration
DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "your_username"
DB_PASSWORD = "your_password"
DB_NAME = "love_letter"

# Upload configuration
UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# CORS
ALLOWED_ORIGINS = [
    "http://genhwa.online",
    "https://genhwa.online",

    # 本地开发可以保留
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
