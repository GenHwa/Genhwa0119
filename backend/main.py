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
    allow_origins=ALLOWED_ORIGINS,  # 来自 config.py
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
                    phone VARCHAR(50) DEFAULT '',
                    email VARCHAR(100) DEFAULT '',
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
                    likes INT DEFAULT 0,
                    user_id INT DEFAULT NULL,
                    avatar VARCHAR(255) DEFAULT ''
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
            # Follows table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS letter_follows (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    follower_id INT NOT NULL,
                    following_id INT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY uk_follow (follower_id, following_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            # Bookmarks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS letter_bookmarks (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    photo_id INT NOT NULL,
                    user_id INT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY uk_bookmark (photo_id, user_id)
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
                ("letter_users", "avatar", "VARCHAR(255) DEFAULT ''"),
                ("letter_users", "phone", "VARCHAR(50) DEFAULT ''"),
                ("letter_users", "email", "VARCHAR(100) DEFAULT ''"),
                ("letter_comments", "user_id", "INT DEFAULT NULL"),
                ("letter_comments", "avatar", "VARCHAR(255) DEFAULT ''"),
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
        return {"code": 200, "token": token, "user": {"id": user_id, "username": username.strip(), "nickname": nickname.strip() or username.strip(), "avatar": ""}}
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
        return {"code": 200, "token": token, "user": {"id": user["id"], "username": user["username"], "nickname": user["nickname"], "avatar": user.get("avatar", "")}}
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
            cursor.execute("SELECT id, username, nickname, avatar, created_at FROM letter_users WHERE id=%s", (payload["user_id"],))
            user = cursor.fetchone()
            if user:
                user["created_at"] = fmt_time(user["created_at"])
        return {"code": 200, "user": user}
    finally:
        conn.close()


@app.post("/api/auth/avatar")
def upload_avatar(file: UploadFile = File(...), token: str = Form("")):
    if not token:
        raise HTTPException(status_code=401, detail="Login required")
    user = decode_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Image only")
    ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    filename = f"avatar_{user['user_id']}_{uuid.uuid4().hex[:8]}{ext}"
    filepath = UPLOAD_DIR / filename
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE letter_users SET avatar=%s WHERE id=%s", (filename, user["user_id"]))
        conn.commit()
        return {"code": 200, "message": "Avatar updated", "filename": filename}
    finally:
        conn.close()


@app.put("/api/auth/profile")
def update_profile(nickname: str = Form(None), phone: str = Form(None),
                   email: str = Form(None), token: str = Form("")):
    if not token:
        raise HTTPException(status_code=401, detail="Login required")
    user = decode_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            updates = []
            params = []
            if nickname is not None:
                updates.append("nickname=%s")
                params.append(nickname.strip())
            if phone is not None:
                updates.append("phone=%s")
                params.append(phone.strip())
            if email is not None:
                updates.append("email=%s")
                params.append(email.strip())
            if updates:
                params.append(user["user_id"])
                cursor.execute(f"UPDATE letter_users SET {', '.join(updates)} WHERE id=%s", params)
        conn.commit()
        # Fetch updated user
        cursor.execute("SELECT id, username, nickname, phone, email, avatar, created_at FROM letter_users WHERE id=%s", (user["user_id"],))
        updated_user = cursor.fetchone()
        if updated_user:
            updated_user["created_at"] = fmt_time(updated_user["created_at"])
        return {"code": 200, "message": "Profile updated", "user": updated_user}
    finally:
        conn.close()


@app.put("/api/auth/password")
def change_password(old_password: str = Form(""), new_password: str = Form(""), token: str = Form("")):
    if not token:
        raise HTTPException(status_code=401, detail="Login required")
    user = decode_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    if not old_password or not new_password:
        raise HTTPException(status_code=400, detail="Password required")
    if len(new_password) < 3:
        raise HTTPException(status_code=400, detail="Password too short")
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT password_hash FROM letter_users WHERE id=%s", (user["user_id"],))
            db_user = cursor.fetchone()
            if not db_user or db_user["password_hash"] != hash_password(old_password):
                raise HTTPException(status_code=400, detail="Incorrect old password")
            cursor.execute("UPDATE letter_users SET password_hash=%s WHERE id=%s", (hash_password(new_password), user["user_id"]))
        conn.commit()
        return {"code": 200, "message": "Password changed"}
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
                    "SELECT m.*, u.nickname as author_name, u.avatar as author_avatar FROM letter_messages m "
                    "LEFT JOIN letter_users u ON m.user_id = u.id "
                    "WHERE m.is_private = 0 OR m.user_id = %s ORDER BY m.created_at DESC",
                    (user["user_id"],)
                )
            else:
                # Not logged in: show only public
                cursor.execute(
                    "SELECT m.*, u.nickname as author_name, u.avatar as author_avatar FROM letter_messages m "
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
            cursor.execute("SELECT * FROM letter_messages WHERE id=%s", (message_id,))
            msg = cursor.fetchone()
            if not msg:
                raise HTTPException(status_code=404, detail="Message not found")
            if "genhwa" not in user.get("username", "") and msg["user_id"] != user["user_id"]:
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
            cursor.execute("SELECT id, user_id FROM letter_messages WHERE id=%s", (message_id,))
            msg_row = cursor.fetchone()
            if not msg_row:
                raise HTTPException(status_code=404, detail="Message not found")
            if "genhwa" not in user.get("username", "") and msg_row["user_id"] != user["user_id"]:
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
def get_photos(token: str = "", page: int = 1, limit: int = 10, feed: str = "all"):
    """
    feed: 'all' = all photos, 'following' = only following users' photos
    page & limit: pagination support
    """
    user = None
    if token:
        user = decode_token(token)
    offset = (page - 1) * limit
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            if feed == "following" and user:
                # Only photos from users that current user follows
                cursor.execute(
                    "SELECT p.*, u.nickname as author_name, u.avatar as author_avatar FROM letter_photos p "
                    "INNER JOIN letter_follows f ON p.user_id = f.following_id AND f.follower_id = %s "
                    "LEFT JOIN letter_users u ON p.user_id = u.id "
                    "WHERE p.is_private = 0 "
                    "ORDER BY p.created_at DESC LIMIT %s OFFSET %s",
                    (user["user_id"], limit, offset)
                )
            elif user:
                cursor.execute(
                    "SELECT p.*, u.nickname as author_name, u.avatar as author_avatar FROM letter_photos p "
                    "LEFT JOIN letter_users u ON p.user_id = u.id "
                    "WHERE p.is_private = 0 OR p.user_id = %s ORDER BY p.created_at DESC LIMIT %s OFFSET %s",
                    (user["user_id"], limit, offset)
                )
            else:
                cursor.execute(
                    "SELECT p.*, u.nickname as author_name, u.avatar as author_avatar FROM letter_photos p "
                    "LEFT JOIN letter_users u ON p.user_id = u.id "
                    "WHERE p.is_private = 0 ORDER BY p.created_at DESC LIMIT %s OFFSET %s",
                    (limit, offset)
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
                # Check if current user bookmarked this photo
                if user:
                    cursor.execute(
                        "SELECT id FROM letter_bookmarks WHERE photo_id=%s AND user_id=%s",
                        (photo["id"], user["user_id"])
                    )
                    photo["is_bookmarked"] = cursor.fetchone() is not None
                else:
                    photo["is_bookmarked"] = False
            has_more = len(photos) == limit
        return {"code": 200, "data": photos, "has_more": has_more}
    finally:
        conn.close()


@app.get("/api/photos/my")
def get_my_photos(token: str = ""):
    if not token:
        return {"code": 200, "data": []}
    user = decode_token(token)
    if not user:
        return {"code": 200, "data": []}
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT p.*, u.nickname as author_name, u.avatar as author_avatar FROM letter_photos p "
                "LEFT JOIN letter_users u ON p.user_id = u.id "
                "WHERE p.user_id = %s ORDER BY p.created_at DESC",
                (user["user_id"],)
            )
            photos = cursor.fetchall()
            for photo in photos:
                photo["created_at"] = fmt_time(photo["created_at"])
        return {"code": 200, "data": photos}
    finally:
        conn.close()


@app.get("/api/messages/my")
def get_my_messages(token: str = ""):
    if not token:
        return {"code": 200, "data": []}
    user = decode_token(token)
    if not user:
        return {"code": 200, "data": []}
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT m.*, u.nickname as author_name, u.avatar as author_avatar FROM letter_messages m "
                "LEFT JOIN letter_users u ON m.user_id = u.id "
                "WHERE m.user_id = %s ORDER BY m.created_at DESC",
                (user["user_id"],)
            )
            msgs = cursor.fetchall()
            for m in msgs:
                m["created_at"] = fmt_time(m["created_at"])
        return {"code": 200, "data": msgs}
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
def add_comment(photo_id: int, nickname: str = Form("익명"), content: str = Form(""), token: str = Form(None)):
    if not content.strip():
        raise HTTPException(status_code=400, detail="Content required")
    user_id = None
    user_avatar = None
    if token:
        payload = decode_token(token)
        if payload:
            user_id = payload["user_id"]
            conn2 = get_db()
            try:
                with conn2.cursor() as c2:
                    c2.execute("SELECT nickname, avatar FROM letter_users WHERE id=%s", (user_id,))
                    u = c2.fetchone()
                    if u:
                        if u["nickname"]:
                            nickname = u["nickname"]
                        user_avatar = u.get("avatar") or None
            finally:
                conn2.close()
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO letter_comments (photo_id, nickname, content, user_id, avatar) VALUES (%s, %s, %s, %s, %s)",
                (photo_id, nickname.strip() or "익명", content.strip(), user_id, user_avatar or "")
            )
            comment_id = cursor.lastrowid
            cursor.execute(
                "UPDATE letter_photos SET comments_count=comments_count+1 WHERE id=%s",
                (photo_id,)
            )
        conn.commit()
        return {"code": 200, "message": "💬", "comment_id": comment_id}
    finally:
        conn.close()


@app.put("/api/comments/{comment_id}")
def update_comment(comment_id: int, content: str = Form(""), token: str = Form("")):
    if not token:
        raise HTTPException(status_code=401, detail="Login required")
    user = decode_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    if not content.strip():
        raise HTTPException(status_code=400, detail="Content required")
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM letter_comments WHERE id=%s", (comment_id,))
            comment = cursor.fetchone()
            if not comment:
                raise HTTPException(status_code=404, detail="Comment not found")
            # Check if user owns this comment by checking username match
            cursor.execute("SELECT username FROM letter_users WHERE id=%s", (user["user_id"],))
            db_user = cursor.fetchone()
            if not db_user or db_user["username"] != comment["nickname"]:
                raise HTTPException(status_code=403, detail="Not your comment")
            cursor.execute("UPDATE letter_comments SET content=%s WHERE id=%s", (content.strip(), comment_id))
        conn.commit()
        return {"code": 200, "message": "Updated"}
    finally:
        conn.close()


@app.delete("/api/comments/{comment_id}")
def delete_comment(comment_id: int, token: str = Form("")):
    if not token:
        raise HTTPException(status_code=401, detail="Login required")
    user = decode_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM letter_comments WHERE id=%s", (comment_id,))
            comment = cursor.fetchone()
            if not comment:
                raise HTTPException(status_code=404, detail="Comment not found")
            # Check if user owns this comment
            cursor.execute("SELECT username FROM letter_users WHERE id=%s", (user["user_id"],))
            db_user = cursor.fetchone()
            if not db_user or db_user["username"] != comment["nickname"]:
                raise HTTPException(status_code=403, detail="Not your comment")
            cursor.execute("DELETE FROM letter_comments WHERE id=%s", (comment_id,))
            cursor.execute("UPDATE letter_photos SET comments_count=GREATEST(comments_count-1,0) WHERE id=%s", (comment["photo_id"],))
        conn.commit()
        return {"code": 200, "message": "Deleted"}
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
            cursor.execute("SELECT * FROM letter_photos WHERE id = %s", (photo_id,))
            photo = cursor.fetchone()
            if not photo:
                raise HTTPException(status_code=404, detail="Photo not found")
            if "genhwa" not in user.get("username", "") and photo["user_id"] != user["user_id"]:
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


# ============ Bookmarks API ============

@app.post("/api/photos/{photo_id}/bookmark")
def toggle_bookmark(photo_id: int, token: str = Form("")):
    if not token:
        raise HTTPException(status_code=401, detail="Login required")
    user = decode_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM letter_bookmarks WHERE photo_id=%s AND user_id=%s",
                (photo_id, user["user_id"])
            )
            existing = cursor.fetchone()
            if existing:
                cursor.execute(
                    "DELETE FROM letter_bookmarks WHERE photo_id=%s AND user_id=%s",
                    (photo_id, user["user_id"])
                )
                bookmarked = False
            else:
                cursor.execute(
                    "INSERT INTO letter_bookmarks (photo_id, user_id) VALUES (%s, %s)",
                    (photo_id, user["user_id"])
                )
                bookmarked = True
        conn.commit()
        return {"code": 200, "bookmarked": bookmarked}
    finally:
        conn.close()


@app.get("/api/bookmarks")
def get_bookmarks(token: str = "", page: int = 1, limit: int = 10):
    if not token:
        return {"code": 200, "data": [], "has_more": False}
    user = decode_token(token)
    if not user:
        return {"code": 200, "data": [], "has_more": False}
    offset = (page - 1) * limit
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT p.*, u.nickname as author_name, u.avatar as author_avatar, b.created_at as bookmarked_at "
                "FROM letter_bookmarks b "
                "JOIN letter_photos p ON b.photo_id = p.id "
                "LEFT JOIN letter_users u ON p.user_id = u.id "
                "WHERE b.user_id = %s "
                "ORDER BY b.created_at DESC LIMIT %s OFFSET %s",
                (user["user_id"], limit, offset)
            )
            photos = cursor.fetchall()
            for photo in photos:
                photo["created_at"] = fmt_time(photo["created_at"])
                photo["is_bookmarked"] = True
                cursor.execute(
                    "SELECT * FROM letter_comments WHERE photo_id=%s ORDER BY created_at DESC LIMIT 3",
                    (photo["id"],)
                )
                photo["recent_comments"] = cursor.fetchall()
                for c in photo["recent_comments"]:
                    c["created_at"] = fmt_time(c["created_at"])
            has_more = len(photos) == limit
        return {"code": 200, "data": photos, "has_more": has_more}
    finally:
        conn.close()


# ============ Stories API ============

@app.get("/api/stories")
def get_stories(token: str = ""):
    """获取所有未过期的 stories，按用户分组"""
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """SELECT s.id, s.user_id, s.filename, s.caption, s.created_at,
                          u.username, u.nickname, u.avatar
                   FROM letter_stories s
                   JOIN letter_users u ON s.user_id = u.id
                   WHERE s.expires_at > NOW()
                   ORDER BY s.created_at DESC""")
            rows = cursor.fetchall()
            if not rows:
                return {"code": 200, "data": []}
            # 按用户分组
            users_map = {}
            for r in rows:
                uid = r["user_id"]
                if uid not in users_map:
                    users_map[uid] = {
                        "user_id": uid,
                        "username": r["username"],
                        "nickname": r["nickname"],
                        "avatar": r["avatar"],
                        "stories": [],
                    }
                users_map[uid]["stories"].append({
                    "id": r["id"],
                    "filename": r["filename"],
                    "caption": r["caption"],
                    "created_at": str(r["created_at"]),
                })
            return {"code": 200, "data": list(users_map.values())}
    finally:
        conn.close()


@app.post("/api/stories")
def upload_story(file: UploadFile = File(...), caption: str = Form(""),
                 token: str = Form("")):
    if not token:
        raise HTTPException(status_code=401, detail="Login required")
    user = decode_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Image only")
    ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    filename = f"story_{uuid.uuid4().hex}{ext}"
    filepath = UPLOAD_DIR / filename
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            # 删除该用户旧的未过期 stories（INS 只保留最近一条）
            cursor.execute(
                "DELETE FROM letter_stories WHERE user_id=%s AND expires_at > NOW()",
                (user["user_id"],)
            )
            # 如果有旧文件也删除
            cursor.execute(
                "SELECT filename FROM letter_stories WHERE user_id=%s",
                (user["user_id"],)
            )
            # 插入新 story，24小时后过期
            cursor.execute(
                "INSERT INTO letter_stories (user_id, filename, caption, expires_at) VALUES (%s, %s, %s, DATE_ADD(NOW(), INTERVAL 24 HOUR))",
                (user["user_id"], filename, caption.strip())
            )
        conn.commit()
        return {"code": 200, "message": "Story uploaded", "data": {"filename": filename}}
    finally:
        conn.close()


@app.delete("/api/stories/{story_id}")
def delete_story(story_id: int, token: str = Form("")):
    if not token:
        raise HTTPException(status_code=401, detail="Login required")
    user = decode_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM letter_stories WHERE id=%s", (story_id,))
            story = cursor.fetchone()
            if not story:
                raise HTTPException(status_code=404, detail="Story not found")
            if "genhwa" not in user.get("username", "") and story["user_id"] != user["user_id"]:
                raise HTTPException(status_code=403, detail="Not your story")
            filepath = UPLOAD_DIR / story["filename"]
            if filepath.exists():
                filepath.unlink()
            cursor.execute("DELETE FROM letter_stories WHERE id=%s", (story_id,))
        conn.commit()
        return {"code": 200, "message": "Deleted"}
    finally:
        conn.close()


@app.put("/api/photos/{photo_id}")
def update_photo(photo_id: int, caption: str = Form(None), is_private: int = Form(None),
                 token: str = Form(""), file: UploadFile = File(None)):
    if not token:
        raise HTTPException(status_code=401, detail="Login required")
    user = decode_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, filename FROM letter_photos WHERE id=%s", (photo_id,))
            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Photo not found")
            if "genhwa" not in user.get("username", "") and row["user_id"] != user["user_id"]:
                raise HTTPException(status_code=403, detail="Not your photo")
            updates = []
            params = []
            if caption is not None:
                updates.append("caption=%s")
                params.append(caption.strip())
            if is_private is not None:
                updates.append("is_private=%s")
                params.append(is_private)
            # Handle file replacement
            if file and file.content_type and file.content_type.startswith("image/"):
                old_photo = cursor.execute("SELECT filename FROM letter_photos WHERE id=%s", (photo_id,))
                old_row = cursor.fetchone()
                ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
                new_filename = f"{uuid.uuid4().hex}{ext}"
                filepath = UPLOAD_DIR / new_filename
                with open(filepath, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                updates.append("filename=%s")
                params.append(new_filename)
                # Delete old file
                if old_row:
                    old_path = UPLOAD_DIR / old_row["filename"]
                    if old_path.exists():
                        old_path.unlink()
            if updates:
                params.append(photo_id)
                cursor.execute(f"UPDATE letter_photos SET {', '.join(updates)} WHERE id=%s", params)
        conn.commit()
        return {"code": 200, "message": "Updated"}
    finally:
        conn.close()


# ============ Search API (photos & messages) ============

@app.get("/api/photos/search")
def search_photos(q: str = "", token: str = ""):
    if not q.strip():
        return {"code": 200, "data": []}
    user = None
    if token:
        user = decode_token(token)
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            term = f"%{q.strip()}%"
            if user:
                cursor.execute(
                    "SELECT p.*, u.nickname as author_name, u.avatar as author_avatar FROM letter_photos p "
                    "LEFT JOIN letter_users u ON p.user_id = u.id "
                    "WHERE (p.caption LIKE %s OR u.nickname LIKE %s) AND (p.is_private = 0 OR p.user_id = %s) "
                    "ORDER BY p.created_at DESC LIMIT 20",
                    (term, term, user["user_id"])
                )
            else:
                cursor.execute(
                    "SELECT p.*, u.nickname as author_name, u.avatar as author_avatar FROM letter_photos p "
                    "LEFT JOIN letter_users u ON p.user_id = u.id "
                    "WHERE (p.caption LIKE %s OR u.nickname LIKE %s) AND p.is_private = 0 "
                    "ORDER BY p.created_at DESC LIMIT 20",
                    (term, term)
                )
            photos = cursor.fetchall()
            for photo in photos:
                photo["created_at"] = fmt_time(photo["created_at"])
        return {"code": 200, "data": photos}
    finally:
        conn.close()


@app.get("/api/messages/search")
def search_messages(q: str = "", token: str = ""):
    if not q.strip():
        return {"code": 200, "data": []}
    user = None
    if token:
        user = decode_token(token)
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            term = f"%{q.strip()}%"
            if user:
                cursor.execute(
                    "SELECT m.*, u.nickname as author_name, u.avatar as author_avatar FROM letter_messages m "
                    "LEFT JOIN letter_users u ON m.user_id = u.id "
                    "WHERE (m.content LIKE %s OR m.nickname LIKE %s) AND (m.is_private = 0 OR m.user_id = %s) "
                    "ORDER BY m.created_at DESC LIMIT 20",
                    (term, term, user["user_id"])
                )
            else:
                cursor.execute(
                    "SELECT m.*, u.nickname as author_name, u.avatar as author_avatar FROM letter_messages m "
                    "LEFT JOIN letter_users u ON m.user_id = u.id "
                    "WHERE (m.content LIKE %s OR m.nickname LIKE %s) AND m.is_private = 0 "
                    "ORDER BY m.created_at DESC LIMIT 20",
                    (term, term)
                )
            msgs = cursor.fetchall()
            for m in msgs:
                m["created_at"] = fmt_time(m["created_at"])
        return {"code": 200, "data": msgs}
    finally:
        conn.close()


# ============ Follow API ============

@app.post("/api/users/{user_id}/follow")
def follow_user(user_id: int, token: str = Form("")):
    if not token:
        raise HTTPException(status_code=401, detail="Login required")
    user = decode_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    if user["user_id"] == user_id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM letter_follows WHERE follower_id=%s AND following_id=%s",
                (user["user_id"], user_id)
            )
            existing = cursor.fetchone()
            if existing:
                cursor.execute(
                    "DELETE FROM letter_follows WHERE follower_id=%s AND following_id=%s",
                    (user["user_id"], user_id)
                )
                followed = False
            else:
                cursor.execute(
                    "INSERT INTO letter_follows (follower_id, following_id) VALUES (%s, %s)",
                    (user["user_id"], user_id)
                )
                followed = True
        conn.commit()
        return {"code": 200, "followed": followed}
    finally:
        conn.close()


@app.get("/api/users/{user_id}/follow/status")
def get_follow_status(user_id: int, token: str = ""):
    """Check if current user follows target user, and get follow stats"""
    is_following = False
    if token:
        user = decode_token(token)
        if user and user["user_id"] != user_id:
            conn = get_db()
            try:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT id FROM letter_follows WHERE follower_id=%s AND following_id=%s",
                        (user["user_id"], user_id)
                    )
                    is_following = cursor.fetchone() is not None
            finally:
                conn.close()
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as cnt FROM letter_follows WHERE follower_id=%s", (user_id,))
            following_count = cursor.fetchone()["cnt"]
            cursor.execute("SELECT COUNT(*) as cnt FROM letter_follows WHERE following_id=%s", (user_id,))
            followers_count = cursor.fetchone()["cnt"]
            cursor.execute("SELECT COUNT(*) as cnt FROM letter_photos WHERE user_id=%s AND is_private=0", (user_id,))
            posts_count = cursor.fetchone()["cnt"]
        return {"code": 200, "data": {"is_following": is_following, "following_count": following_count, "followers_count": followers_count, "posts_count": posts_count}}
    finally:
        conn.close()


# ============ Stats ============

@app.get("/api/users/search")
def search_users(q: str = ""):
    if not q.strip():
        return {"code": 200, "data": []}
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            search_term = f"%{q.strip()}%"
            cursor.execute(
                "SELECT id, username, nickname, avatar, created_at FROM letter_users "
                "WHERE username LIKE %s OR nickname LIKE %s ORDER BY created_at DESC LIMIT 20",
                (search_term, search_term)
            )
            users = cursor.fetchall()
            for u in users:
                u["created_at"] = fmt_time(u["created_at"])
        return {"code": 200, "data": users}
    finally:
        conn.close()


@app.get("/api/users/{user_id}/photos")
def get_user_photos(user_id: int, token: str = ""):
    user = None
    if token:
        user = decode_token(token)
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            if user:
                cursor.execute(
                    "SELECT p.*, u.nickname as author_name, u.avatar as author_avatar FROM letter_photos p "
                    "LEFT JOIN letter_users u ON p.user_id = u.id "
                    "WHERE p.user_id = %s AND (p.is_private = 0 OR p.user_id = %s) ORDER BY p.created_at DESC",
                    (user_id, user["user_id"])
                )
            else:
                cursor.execute(
                    "SELECT p.*, u.nickname as author_name, u.avatar as author_avatar FROM letter_photos p "
                    "LEFT JOIN letter_users u ON p.user_id = u.id "
                    "WHERE p.user_id = %s AND p.is_private = 0 ORDER BY p.created_at DESC",
                    (user_id,)
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


@app.get("/api/bookmarks/count")
def get_bookmark_count(token: str = ""):
    if not token:
        return {"code": 200, "count": 0}
    user = decode_token(token)
    if not user:
        return {"code": 200, "count": 0}
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as cnt FROM letter_bookmarks WHERE user_id=%s", (user["user_id"],))
            count = cursor.fetchone()["cnt"]
        return {"code": 200, "count": count}
    finally:
        conn.close()


@app.get("/api/health")
def health_check():
    return {"code": 200, "message": "I'm here for you 💕"}
