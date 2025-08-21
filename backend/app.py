from flask import Flask, jsonify, request, Response, g
from flask_cors import CORS
from datetime import datetime, timedelta

# Work in both run modes:
#   python -m backend.app   (recommended)
#   (fallback) python backend\app.py
try:
    from backend.soclib.db import init_db, SessionLocal, Event, Alert, User
    from backend.soclib.pipeline import Pipeline
    from backend.soclib.parsers import ssh_auth, nginx, ufw, dns, apache, apache_error
    from backend.soclib.auth import require_auth, issue_token, verify_password, hash_password, limiter, audit
    from backend.settings import load_config
except ImportError:
    from soclib.db import init_db, SessionLocal, Event, Alert, User
    from soclib.pipeline import Pipeline
    from soclib.parsers import ssh_auth, nginx, ufw, dns, apache, apache_error
    from soclib.auth import require_auth, issue_token, verify_password, hash_password, limiter, audit
    from settings import load_config

app = Flask(__name__)
CORS(app)
limiter.init_app(app)
init_db()

pipeline = Pipeline()

@app.get("/api/health")
def health():
    return {"ok": True, "time": datetime.utcnow().isoformat()}

@app.post("/api/login")
def login():
    data = request.json or {}
    email = data.get("email")
    pw = data.get("password")
    with SessionLocal() as s:
        u = s.query(User).filter(User.email == email, User.active == True).first()
        if u and verify_password(pw, u.password_hash):
            tok = issue_token(u)
            audit(email, "login", "user")
            return {"token": tok, "role": u.role}
    return {"error": "invalid credentials"}, 401

@app.post("/api/users")
@require_auth(["admin"])
def create_user():
    data = request.json or {}
    with SessionLocal() as s:
        u = User(
            email=data["email"],
            password_hash=hash_password(data["password"]),
            role=data.get("role", "analyst"),
        )
        s.add(u)
        s.commit()
        audit(g.user["email"], "create_user", data["email"])
        return {"ok": True, "id": u.id}

@app.get("/api/logs")
@require_auth()
def get_logs():
    limit = int(request.args.get("limit", 100))
    offset = int(request.args.get("offset", 0))
    source = request.args.get("source")
    ip = request.args.get("ip")
    since = request.args.get("since")
    until = request.args.get("until")
    with SessionLocal() as s:
        q = s.query(Event)
        if source:
            q = q.filter(Event.source_type == source)
        if ip:
            q = q.filter(Event.src_ip == ip)
        if since:
            try:
                q = q.filter(Event.ts >= datetime.fromisoformat(since.replace("Z", "+00:00")))
            except Exception:
                pass
        if until:
            try:
                q = q.filter(Event.ts <= datetime.fromisoformat(until.replace("Z", "+00:00")))
            except Exception:
                pass
        rows = q.order_by(Event.ts.desc()).offset(offset).limit(limit).all()
        return jsonify(
            [
                {
                    "id": r.id,
                    "ts": r.ts.isoformat(),
                    "host": r.host,
                    "src_ip": r.src_ip,
                    "dst_port": r.dst_port,
                    "status": r.status,
                    "source_type": r.source_type,
                    "http_path": r.http_path,
                    "fields": r.fields,
                }
                for r in rows
            ]
        )

@app.get("/api/alerts")
@require_auth()
def get_alerts():
    status = request.args.get("status")
    ip = request.args.get("ip")
    since = request.args.get("since")
    limit = int(request.args.get("limit", 100))
    offset = int(request.args.get("offset", 0))
    with SessionLocal() as s:
        q = s.query(Alert)
        if status:
            q = q.filter(Alert.status == status)
        if ip:
            q = q.filter(Alert.src_ip == ip)
        if since:
            try:
                q = q.filter(Alert.ts >= datetime.fromisoformat(since.replace("Z", "+00:00")))
            except Exception:
                pass
        rows = q.order_by(Alert.ts.desc()).offset(offset).limit(limit).all()
        return jsonify(
            [
                {
                    "id": r.id,
                    "ts": r.ts.isoformat(),
                    "type": r.type,
                    "severity": r.severity,
                    "src_ip": r.src_ip,
                    "details": r.details,
                    "status": r.status,
                    "incident_id": r.incident_id,
                }
                for r in rows
            ]
        )

@app.post("/api/alerts/<int:aid>/status")
@require_auth(["admin", "analyst"])
def set_alert_status(aid):
    new = (request.json or {}).get("status")
    with SessionLocal() as s:
        a = s.get(Alert, aid)
        if not a:
            return {"error": "not found"}, 404
        a.status = new
        s.commit()
        audit(g.user["email"], "set_alert_status", f"alert:{aid}", {"status": new})
        return {"ok": True}

@app.get("/api/stream")
@require_auth()
def stream():
    def gen():
        import time
        i = 0
        while True:
            i += 1
            yield f'data: {{"type":"ping","i":{i}}}\n\n'
            time.sleep(5)
    return Response(gen(), mimetype="text/event-stream")

@app.post("/api/ingest/demo")
@require_auth()
def ingest_demo():
    data = request.json or {}
    source = data.get("source")
    host = data.get("host", "demo-host")
    line = data.get("line", "")
    parser = {
        "ssh_auth": ssh_auth.parse_line,
        "nginx": nginx.parse_line,
        "ufw": ufw.parse_line,
        "dns": dns.parse_line,
        "apache": apache.parse_line,
        "apache_error": apache_error.parse_line,
    }.get(source)
    if not parser:
        return {"error": "unknown source"}, 400
    e = parser(line, host)
    if e:
        pipeline.handle_event(e)
        return {"ok": True}
    return {"ok": False, "reason": "no match"}

@app.get("/api/stats")
@require_auth()
def stats():
    with SessionLocal() as s:
        total_events = s.query(Event).count()
        total_alerts = s.query(Alert).count()
        cutoff = datetime.utcnow() - timedelta(hours=24)
        ssh_failed_24h = (
            s.query(Event)
            .filter(Event.source_type == "ssh_auth", Event.status == "ssh_failed", Event.ts >= cutoff)
            .count()
        )
        return {
            "total_events": total_events,
            "total_alerts": total_alerts,
            "ssh_failed_last_24h": ssh_failed_24h,
        }

if __name__ == "__main__":
    import os
    # ensure admin exists
    with SessionLocal() as s:
        if not s.query(User).filter(User.email == os.getenv("ADMIN_EMAIL", "admin@example.com")).first():
            s.add(
                User(
                    email=os.getenv("ADMIN_EMAIL", "admin@example.com"),
                    password_hash=hash_password(os.getenv("ADMIN_PASSWORD", "ChangeMe!123")),
                    role="admin",
                )
            )
            s.commit()
    app.run(port=int(os.getenv("PORT", "8000")), debug=True)
