from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from datetime import datetime, date
from app.db import SessionLocal
from app.models import Post

def check_and_publish():
    """Check DB for due posts and auto-publish them (mock)."""
    db: Session = SessionLocal()
    try:
        today = date.today()
        due_posts = (
            db.query(Post)
            .filter(Post.status == "scheduled")
            .all()
        )
        for p in due_posts:
            if not p.scheduled_at:
                continue
            # robust parse: expect 'YYYY-MM-DD' (we validate in API)
            try:
                scheduled = date.fromisoformat(p.scheduled_at[:10])
            except Exception:
                continue
            if scheduled <= today:
                print(f"[Scheduler] Auto-publishing post {p.id}: {p.title}")
                p.status = "posted"
                db.add(p)
        db.commit()
    finally:
        db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_and_publish, IntervalTrigger(seconds=30))
    scheduler.start()
    print("[Scheduler] Started background job.")
    return scheduler
