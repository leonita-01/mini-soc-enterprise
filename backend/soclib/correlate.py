from datetime import timedelta
from .db import SessionLocal, Alert, Incident
def correlate(alert: Alert, window_minutes=10):
    with SessionLocal() as s:
        cutoff = alert.ts - timedelta(minutes=window_minutes)
        existing = s.query(Incident).join(Alert).filter(Alert.src_ip==alert.src_ip, Alert.ts>=cutoff).order_by(Incident.id.desc()).first()
        if existing:
            alert.incident_id = existing.id; s.commit(); return existing.id
        inc = Incident(summary=f"Activity from {alert.src_ip}")
        s.add(inc); s.commit()
        alert.incident_id = inc.id; s.commit()
        return inc.id
