import click
from datetime import datetime, timedelta
from soclib.db import SessionLocal, Event, Alert
@click.group() ; def cli(): pass
@cli.command() ; @click.option("--days", default=30)
def purge(days):
    cutoff = datetime.utcnow() - timedelta(days=days)
    with SessionLocal() as s:
        s.query(Event).filter(Event.ts<cutoff).delete()
        s.query(Alert).filter(Alert.ts<cutoff).delete()
        s.commit()
    print("Purged older than", days, "days")
if __name__ == "__main__": cli()
