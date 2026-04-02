from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import pymysql
import shutil
import uuid
import os
import hashlib
import json
import jwt
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, UPLOAD_DIR, ALLOWED_ORIGINS

app = FastAPI(title="Love Letter", version="2.0.0")

# JWT secret
JWT_SECRET = "diary_secret_key_2024"
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 720  # 30 days

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for uploads
UPLOAD_DIR.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


def get_db():
    return pymysql.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER,
        password=DB_PASSWORD, database=DB_NAME,
        charset="utf8mb4", cursorclass=pymysql.cursors.DictCursor,
    )


def init_db():
    conn = pymysql.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER,
        password=DB_PASSWORD, charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
                "DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        conn.commit()
    finally:
        conn.close()

    conn = get_db()
    try:
        with conn.cursor() as cursor:
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS letter_users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    nickname VARCHAR(100) DEFAULT '',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            # Create tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS letter_messages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nickname VARCHAR(100) NOT NULL DEFAULT '익명',
                    content TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    mood VARCHAR(50) DEFAULT 'love',
                    likes INT DEFAULT 0,
                    user_id INT DEFAULT NULL,
                    is_private TINYINT(1) DEFAULT 0
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS letter_photos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    filename VARCHAR(255) NOT NULL,
                    caption VARCHAR(500) DEFAULT '',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    likes INT DEFAULT 0,
                    comments_count INT DEFAULT 0,
                    user_id INT DEFAULT NULL,
                    is_private TINYINT(1) DEFAULT 0
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS letter_photo_likes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    photo_id INT NOT NULL,
                    user_hash VARCHAR(64) NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY uk_photo_user (photo_id, user_hash)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS letter_comments (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    photo_id INT NOT NULL,
                    nickname VARCHAR(100) NOT NULL DEFAULT '익명',
                    content TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    likes INT DEFAULT 0
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS letter_msg_likes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    message_id INT NOT NULL,
                    user_hash VARCHAR(64) NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY uk_msg_user (message_id, user_hash)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            # Migrate: add missing columns to existing tables
            for col_def in [
                ("letter_messages", "likes", "INT DEFAULT 0"),
                ("letter_messages", "mood", "VARCHAR(50) DEFAULT 'love'"),
                ("letter_messages", "user_id", "INT DEFAULT NULL"),
                ("letter_messages", "is_private", "TINYINT(1) DEFAULT 0"),
                ("letter_photos", "likes", "INT DEFAULT 0"),
                ("letter_photos", "comments_count", "INT DEFAULT 0"),
                ("letter_photos", "user_id", "INT DEFAULT NULL"),
                ("letter_photos", "is_private", "TINYINT(1) DEFAULT 0"),
                ("letter_photos", "location", "VARCHAR(255) DEFAULT ''"),
            ]:
                try:
                    cursor.execute(f"ALTER TABLE `{col_def[0]}` ADD COLUMN `{col_def[1]}` {col_def[2]}")
                except Exception:
                    pass  # Column already exists

        conn.commit()
    finally:
        conn.close()


@app.on_event("startup")
def startup():
    init_db()


def fmt_time(dt):
    if dt:
        return dt.strftime("%Y-%m-%d %H:%M")
    return ""


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def create_token(user_id, username):
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_current_user(token: str = Form(None)):
    if not token:
        return None
    payload = decode_token(token)
    if payload:
        return {"user_id": payload["user_id"], "username": payload["username"]}
    return None


# ============ Auth API ============

@app.post("/api/auth/register")
def register(username: str = Form(""), password: str = Form(""), nickname: str = Form("")):
    if not username.strip() or not password.strip():
        raise HTTPException(status_code=400, detail="Username and password required")
    if len(password) < 3:
        raise HTTPException(status_code=400, detail="Password too short")
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM letter_users WHERE username=%s", (username.strip(),))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Username already exists")
            cursor.execute(
                "INSERT INTO letter_users (username, password_hash, nickname) VALUES (%s, %s, %s)",
                (username.strip(), hash_password(password), nickname.strip() or username.strip())
            )
            user_id = cursor.lastrowid
        conn.commit()
        token = create_token(user_id, username.strip())
        return {"code": 200, "token": token, "user": {"id": user_id, "username": username.strip(), "nickname": nickname.strip() or username.strip()}}
    finally:
        conn.close()


@app.post("/api/auth/login")
def login(username: str = Form(""), password: str = Form("")):
    if not username.strip() or not password.strip():
        raise HTTPException(status_code=400, detail="Username and password required")
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM letter_users WHERE username=%s", (username.strip(),))
            user = cursor.fetchone()
            if not user or user["password_hash"] != hash_password(password):
                raise HTTPException(status_code=401, detail="Invalid credentials")
            token = create_token(user["id"], user["username"])
        return {"code": 200, "token": token, "user": {"id": user["id"], "username": user["username"], "nickname": user["nickname"]}}
    finally:
        conn.close()


@app.get("/api/auth/me")
def get_me(token: str = ""):
    if not token:
        return {"code": 401, "message": "Not logged in"}
    payload = decode_token(token)
    if not payload:
        return {"code": 401, "message": "Invalid token"}
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, username, nickname, created_at FROM letter_users WHERE id=%s", (payload["user_id"],))
            user = cursor.fetchone()
            if user:
                user["created_at"] = fmt_time(user["created_at"])
        return {"code": 200, "user": user}
    finally:
        conn.close()


# ============ Messages API ============

@app.get("/api/messages")
def get_messages(token: str = ""):
    user = None
    if token:
        user = decode_token(token)
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            if user:
                # Logged in: show all public + own private
                cursor.execute(
                    "SELECT m.*, u.nickname as author_name FROM letter_messages m "
                    "LEFT JOIN letter_users u ON m.user_id = u.id "
                    "WHERE m.is_private = 0 OR m.user_id = %s ORDER BY m.created_at DESC",
                    (user["user_id"],)
                )
            else:
                # Not logged in: show only public
                cursor.execute(
                    "SELECT m.*, u.nickname as author_name FROM letter_messages m "
                    "LEFT JOIN letter_users u ON m.user_id = u.id "
                    "WHERE m.is_private = 0 ORDER BY m.created_at DESC"
                )
            messages = cursor.fetchall()
            for msg in messages:
                msg["created_at"] = fmt_time(msg["created_at"])
        return {"code": 200, "data": messages}
    finally:
        conn.close()


@app.post("/api/messages")
def create_message(nickname: str = Form("익명"), content: str = Form(""), mood: str = Form("love"),
                   token: str = Form(None), is_private: int = Form(0)):
    if not content.strip():
        raise HTTPException(status_code=400, detail="Content required")
    user_id = None
    if token:
        payload = decode_token(token)
        if payload:
            user_id = payload["user_id"]
            conn2 = get_db()
            try:
                with conn2.cursor() as c2:
                    c2.execute("SELECT nickname FROM letter_users WHERE id=%s", (user_id,))
                    u = c2.fetchone()
                    if u and u["nickname"]:
                        nickname = u["nickname"]
            finally:
                conn2.close()
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO letter_messages (nickname, content, mood, user_id, is_private) VALUES (%s, %s, %s, %s, %s)",
                (nickname.strip(), content.strip(), mood, user_id, is_private)
            )
        conn.commit()
        return {"code": 200, "message": "💌"}
    finally:
        conn.close()


@app.put("/api/messages/{message_id}")
def update_message(message_id: int, content: str = Form(""), mood: str = Form(None),
                   is_private: int = Form(None), token: str = Form("")):
    if not token:
        raise HTTPException(status_code=401, detail="Login required")
    user = decode_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM letter_messages WHERE id=%s AND user_id=%s", (message_id, user["user_id"]))
            msg = cursor.fetchone()
            if not msg:
                raise HTTPException(status_code=403, detail="Not your message")
            updates = []
            params = []
            if content.strip():
                updates.append("content=%s")
                params.append(content.strip())
            if mood is not None:
                updates.append("mood=%s")
                params.append(mood)
            if is_private is not None:
                updates.append("is_private=%s")
                params.append(is_private)
            if updates:
                params.append(message_id)
                cursor.execute(f"UPDATE letter_messages SET {', '.join(updates)} WHERE id=%s", params)
        conn.commit()
        return {"code": 200, "message": "Updated"}
    finally:
        conn.close()


@app.delete("/api/messages/{message_id}")
def delete_message(message_id: int, token: str = Form("")):
    if not token:
        raise HTTPException(status_code=401, detail="Login required")
    user = decode_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM letter_messages WHERE id=%s AND user_id=%s", (message_id, user["user_id"]))
            if not cursor.fetchone():
                raise HTTPException(status_code=403, detail="Not your message")
            cursor.execute("DELETE FROM letter_messages WHERE id=%s", (message_id,))
            cursor.execute("DELETE FROM letter_msg_likes WHERE message_id=%s", (message_id,))
        conn.commit()
        return {"code": 200, "message": "Deleted"}
    finally:
        conn.close()


@app.post("/api/messages/{message_id}/like")
def like_message(message_id: int, user_hash: str = Form("default")):
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM letter_msg_likes WHERE message_id=%s AND user_hash=%s",
                (message_id, user_hash)
            )
            existing = cursor.fetchone()
            if existing:
                cursor.execute(
                    "DELETE FROM letter_msg_likes WHERE message_id=%s AND user_hash=%s",
                    (message_id, user_hash)
                )
                cursor.execute(
                    "UPDATE letter_messages SET likes=GREATEST(likes-1,0) WHERE id=%s",
                    (message_id,)
                )
                liked = False
            else:
                cursor.execute(
                    "INSERT INTO letter_msg_likes (message_id, user_hash) VALUES (%s, %s)",
                    (message_id, user_hash)
                )
                cursor.execute(
                    "UPDATE letter_messages SET likes=likes+1 WHERE id=%s",
                    (message_id,)
                )
                liked = True
        conn.commit()
        return {"code": 200, "liked": liked}
    finally:
        conn.close()


# ============ Photos API ============

@app.get("/api/photos")
def get_photos(token: str = ""):
    user = None
    if token:
        user = decode_token(token)
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            if user:
                cursor.execute(
                    "SELECT p.*, u.nickname as author_name FROM letter_photos p "
                    "LEFT JOIN letter_users u ON p.user_id = u.id "
                    "WHERE p.is_private = 0 OR p.user_id = %s ORDER BY p.created_at DESC",
                    (user["user_id"],)
                )
            else:
                cursor.execute(
                    "SELECT p.*, u.nickname as author_name FROM letter_photos p "
                    "LEFT JOIN letter_users u ON p.user_id = u.id "
                    "WHERE p.is_private = 0 ORDER BY p.created_at DESC"
                )
            photos = cursor.fetchall()
            for photo in photos:
                photo["created_at"] = fmt_time(photo["created_at"])
                cursor.execute(
                    "SELECT * FROM letter_comments WHERE photo_id=%s ORDER BY created_at DESC LIMIT 3",
                    (photo["id"],)
                )
                photo["recent_comments"] = cursor.fetchall()
                for c in photo["recent_comments"]:
                    c["created_at"] = fmt_time(c["created_at"])
        return {"code": 200, "data": photos}
    finally:
        conn.close()


@app.post("/api/photos")
def upload_photo(file: UploadFile = File(...), caption: str = Form(""),
                 token: str = Form(None), is_private: int = Form(0),
                 location: str = Form("")):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Image only")
    ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = UPLOAD_DIR / filename
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    user_id = None
    if token:
        payload = decode_token(token)
        if payload:
            user_id = payload["user_id"]
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO letter_photos (filename, caption, user_id, is_private, location) VALUES (%s, %s, %s, %s, %s)",
                (filename, caption.strip(), user_id, is_private, location.strip())
            )
        conn.commit()
        return {"code": 200, "message": "📸", "data": {"filename": filename}}
    finally:
        conn.close()


@app.post("/api/photos/{photo_id}/like")
def like_photo(photo_id: int, user_hash: str = Form("default")):
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM letter_photo_likes WHERE photo_id=%s AND user_hash=%s",
                (photo_id, user_hash)
            )
            existing = cursor.fetchone()
            if existing:
                cursor.execute(
                    "DELETE FROM letter_photo_likes WHERE photo_id=%s AND user_hash=%s",
                    (photo_id, user_hash)
                )
                cursor.execute(
                    "UPDATE letter_photos SET likes=GREATEST(likes-1,0) WHERE id=%s",
                    (photo_id,)
                )
                liked = False
            else:
                cursor.execute(
                    "INSERT INTO letter_photo_likes (photo_id, user_hash) VALUES (%s, %s)",
                    (photo_id, user_hash)
                )
                cursor.execute(
                    "UPDATE letter_photos SET likes=likes+1 WHERE id=%s",
                    (photo_id,)
                )
                liked = True
            cursor.execute("SELECT likes FROM letter_photos WHERE id=%s", (photo_id,))
            row = cursor.fetchone()
            likes_count = row["likes"] if row else 0
        conn.commit()
        return {"code": 200, "liked": liked, "likes": likes_count}
    finally:
        conn.close()


# ============ Comments API ============

@app.get("/api/photos/{photo_id}/comments")
def get_comments(photo_id: int):
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM letter_comments WHERE photo_id=%s ORDER BY created_at DESC",
                (photo_id,)
            )
            comments = cursor.fetchall()
            for c in comments:
                c["created_at"] = fmt_time(c["created_at"])
        return {"code": 200, "data": comments}
    finally:
        conn.close()


@app.post("/api/photos/{photo_id}/comments")
def add_comment(photo_id: int, nickname: str = Form("익명"), content: str = Form("")):
    if not content.strip():
        raise HTTPException(status_code=400, detail="Content required")
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO letter_comments (photo_id, nickname, content) VALUES (%s, %s, %s)",
                (photo_id, nickname.strip() or "익명", content.strip())
            )
            cursor.execute(
                "UPDATE letter_photos SET comments_count=comments_count+1 WHERE id=%s",
                (photo_id,)
            )
        conn.commit()
        return {"code": 200, "message": "💬"}
    finally:
        conn.close()


@app.delete("/api/photos/{photo_id}")
def delete_photo(photo_id: int, token: str = Form("")):
    if not token:
        raise HTTPException(status_code=401, detail="Login required")
    user = decode_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM letter_photos WHERE id = %s AND user_id = %s", (photo_id, user["user_id"]))
            photo = cursor.fetchone()
            if not photo:
                raise HTTPException(status_code=403, detail="Not your photo")
            filepath = UPLOAD_DIR / photo["filename"]
            if filepath.exists():
                filepath.unlink()
            cursor.execute("DELETE FROM letter_photos WHERE id = %s", (photo_id,))
            cursor.execute("DELETE FROM letter_photo_likes WHERE photo_id = %s", (photo_id,))
            cursor.execute("DELETE FROM letter_comments WHERE photo_id = %s", (photo_id,))
        conn.commit()
        return {"code": 200, "message": "Deleted"}
    finally:
        conn.close()


@app.put("/api/photos/{photo_id}")
def update_photo(photo_id: int, caption: str = Form(None), is_private: int = Form(None), token: str = Form("")):
    if not token:
        raise HTTPException(status_code=401, detail="Login required")
    user = decode_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM letter_photos WHERE id=%s AND user_id=%s", (photo_id, user["user_id"]))
            if not cursor.fetchone():
                raise HTTPException(status_code=403, detail="Not your photo")
            updates = []
            params = []
            if caption is not None:
                updates.append("caption=%s")
                params.append(caption.strip())
            if is_private is not None:
                updates.append("is_private=%s")
                params.append(is_private)
            if updates:
                params.append(photo_id)
                cursor.execute(f"UPDATE letter_photos SET {', '.join(updates)} WHERE id=%s", params)
        conn.commit()
        return {"code": 200, "message": "Updated"}
    finally:
        conn.close()


# ============ Stats ============

@app.get("/api/stats")
def get_stats():
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as total FROM letter_photos")
            photos = cursor.fetchone()["total"]
            cursor.execute("SELECT COUNT(*) as total FROM letter_messages")
            messages = cursor.fetchone()["total"]
            cursor.execute("SELECT COALESCE(SUM(likes),0) as total FROM letter_photos")
            total_likes = cursor.fetchone()["total"]
        return {"code": 200, "data": {"photos": photos, "messages": messages, "total_likes": total_likes}}
    finally:
        conn.close()


@app.get("/api/health")
def health_check():
    return {"code": 200, "message": "I'm here for you 💕"}
