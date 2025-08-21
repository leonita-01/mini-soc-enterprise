# backend/soclib/auth.py
import time
import os
from flask import request, jsonify, g
from functools import wraps
from passlib.hash import bcrypt
import jwt
from ..settings import get_jwt_secret, get_api_key
from .db import SessionLocal, User, Audit
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Use memory in dev (no warning); override with env RATELIMIT_STORAGE_URI, e.g. redis://127.0.0.1:6379/0
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per minute"],
    storage_uri=os.getenv("RATELIMIT_STORAGE_URI", "memory://"),
)

def audit(actor, action, resource, details=None):
    with SessionLocal() as s:
        s.add(Audit(actor=actor or "anonymous", action=action, resource=resource, details=details or {}))
        s.commit()

def issue_token(user: User):
    payload = {"sub": user.email, "role": user.role, "iat": int(time.time()), "exp": int(time.time()) + 86400}
    return jwt.encode(payload, get_jwt_secret(), algorithm="HS256")

def require_auth(roles=None):
    roles = roles or []
    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if request.path == "/api/health":
                return fn(*args, **kwargs)
            apikey = request.headers.get("X-API-Key")
            if apikey and apikey == get_api_key():
                g.user = {"email": "apikey", "role": "admin"}
                return fn(*args, **kwargs)
            auth = request.headers.get("Authorization", "")
            if auth.startswith("Bearer "):
                token = auth.split(" ", 1)[1]
                try:
                    data = jwt.decode(token, get_jwt_secret(), algorithms=["HS256"])
                    g.user = {"email": data["sub"], "role": data.get("role", "viewer")}
                    if roles and g.user["role"] not in roles:
                        return jsonify({"error": "forbidden"}), 403
                    return fn(*args, **kwargs)
                except Exception:
                    return jsonify({"error": "unauthorized"}), 401
            return jsonify({"error": "unauthorized"}), 401
        return wrapper
    return deco

def hash_password(pw): return bcrypt.hash(pw)
def verify_password(pw, ph): return bcrypt.verify(pw, ph)
