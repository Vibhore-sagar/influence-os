from fastapi import FastAPI, Depends, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
import httpx

from app.db import SessionLocal, engine, Base
from app.models import Post, Metrics, User
from app.services.scheduler import start_scheduler
from app.services.generation import derive_brand_voice, generate_post
from app.services.optimization import generate_hashtags, generate_hooks
from app.config import settings

from pydantic import BaseModel
from datetime import datetime, timedelta
from app.services.generation import generate_post
from app.services.optimization import generate_hashtags, generate_hooks
from app.models import Post


class PostIn(BaseModel):
    topic: str

class ScheduleIn(BaseModel):
    scheduled_at: str  # ISO date string: 'YYYY-MM-DD'

# Initialize FastAPI app
app = FastAPI(title="Influence OS")

# Allow frontend (React/Next.js) access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Start background scheduler
@app.on_event("startup")
def startup_event():
    start_scheduler()


# -------------------------------
# OAuth Login (LinkedIn Example)
# -------------------------------
router = APIRouter()

@router.get("/login/linkedin")
async def linkedin_login():
    return {
        "auth_url": (
            "https://www.linkedin.com/oauth/v2/authorization"
            f"?response_type=code&client_id={settings.LINKEDIN_CLIENT_ID}"
            f"&redirect_uri={settings.LINKEDIN_REDIRECT_URI}"
            "&scope=r_liteprofile r_emailaddress w_member_social"
        )
    }

@router.get("/auth/linkedin/callback")
async def linkedin_callback(code: str, db: Session = Depends(get_db)):
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.LINKEDIN_REDIRECT_URI,
        "client_id": settings.LINKEDIN_CLIENT_ID,
        "client_secret": settings.LINKEDIN_CLIENT_SECRET,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=data)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch access token")
        token_data = response.json()

    access_token = token_data["access_token"]
    expires_in = token_data.get("expires_in", 0)

    # Fetch user info from LinkedIn
    async with httpx.AsyncClient() as client:
        profile = await client.get(
            "https://api.linkedin.com/v2/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        email_resp = await client.get(
            "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))",
            headers={"Authorization": f"Bearer {access_token}"},
        )

    if profile.status_code != 200 or email_resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch user info")

    profile_data = profile.json()
    email_data = email_resp.json()

    user = User(
        li_person_urn=profile_data.get("id"),
        name=profile_data.get("localizedFirstName", "")
        + " "
        + profile_data.get("localizedLastName", ""),
        email=email_data["elements"][0]["handle~"]["emailAddress"],
        access_token=access_token,
        refresh_token=None,
        token_expires_at=str(datetime.utcnow() + timedelta(seconds=expires_in)),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "Login successful", "user_id": user.id}


# -------------------------------
# Analytics Routes
# -------------------------------
@router.get("/analytics", response_model=List[dict])
def get_analytics(db: Session = Depends(get_db)):
    metrics = db.query(Metrics).all()
    return [
        {
            "post_id": m.post_id,
            "likes": m.likes,
            "comments": m.comments,
            "shares": m.shares,
            "impressions": m.impressions,
        }
        for m in metrics
    ]


# -------------------------------
# Calendar Routes
# -------------------------------
@router.get("/calendar")
def get_calendar(db: Session = Depends(get_db)):
    posts = db.query(Post).all()
    return [
        {
            "id": p.id,
            "title": p.title,
            "scheduled_at": p.scheduled_at,
            "status": p.status,
        }
        for p in posts
    ]


# -------------------------------
# Post Generation Routes
# -------------------------------
@router.post("/posts/generate")
def generate_new_post(payload: PostIn, db: Session = Depends(get_db)):
    topic = payload.topic

    # Generate base content
    title, body, _ = generate_post(topic, {"tone": "helpful"})

    # Optimization: candidates + best, and hook variants
    candidates, best_tags = generate_hashtags(topic)
    hooks = generate_hooks(topic)

    post = Post(
        title=title,
        body=body,
        hashtags=",".join(best_tags),        # final chosen hashtags
        hashtags_raw=",".join(candidates),   # all candidates
        hooks="||".join(hooks),              # A/B hooks (split by '||')
        created_at=datetime.utcnow().isoformat(),
        status="draft",
    )
    db.add(post)
    db.commit()
    db.refresh(post)

    return {
        "id": post.id,
        "title": post.title,
        "body": post.body,
        "hashtags": best_tags,
        "hooks": hooks,
    }

@router.get("/posts/{post_id}/details")
def post_details(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return {
        "id": post.id,
        "title": post.title,
        "body": post.body,
        "hooks": post.hooks.split("||") if post.hooks else [],
        "hashtags_raw": post.hashtags_raw.split(",") if post.hashtags_raw else [],
        "hashtags_final": post.hashtags.split(",") if post.hashtags else [],
        "scheduled_at": post.scheduled_at,
        "status": post.status,
    }


from datetime import date

@router.post("/posts/schedule/{post_id}")
def schedule_post(post_id: int, payload: ScheduleIn, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # validate ISO date (YYYY-MM-DD)
    try:
        # ensure it's a valid date
        _ = date.fromisoformat(payload.scheduled_at)
    except ValueError:
        raise HTTPException(status_code=400, detail="scheduled_at must be YYYY-MM-DD")

    post.scheduled_at = payload.scheduled_at
    post.status = "scheduled"
    db.commit()
    return {"message": "Post scheduled", "post_id": post_id, "scheduled_at": payload.scheduled_at}
@router.get("/analytics/summary")
def get_analytics_summary(db: Session = Depends(get_db)):
    metrics = db.query(Metrics).all()
    totals = {
        "likes": sum(m.likes for m in metrics),
        "comments": sum(m.comments for m in metrics),
        "shares": sum(m.shares for m in metrics),
        "impressions": sum(m.impressions for m in metrics),
    }

    # find best post by engagement
    best = None
    if metrics:
        best_metric = max(metrics, key=lambda m: (m.likes + m.comments + m.shares))
        post = db.query(Post).filter(Post.id == best_metric.post_id).first()
        if post:
            best = {
                "id": post.id,
                "title": post.title,
                "engagement": best_metric.likes + best_metric.comments + best_metric.shares
            }

    return {"totals": totals, "best_post": best}


@router.post("/strategy/plan")
def generate_strategy_plan(topic: str, db: Session = Depends(get_db)):
    """
    Generate a 7-day posting strategy with auto-scheduled posts.
    """
    today = datetime.utcnow()
    posts_out = []

    for i in range(7):
        date = today + timedelta(days=i)

        # Generate base post
        title, body, tags = generate_post(topic, {"tone": "helpful"})
        candidates, best_tags = generate_hashtags(topic)
        hooks = generate_hooks(topic)

        post = Post(
            title=title,
            body=body,
            hashtags=",".join(best_tags),
            hashtags_raw=",".join(candidates),
            hooks="||".join(hooks),
            created_at=today.isoformat(),
            scheduled_at=date.date().isoformat(),
            status="scheduled",
        )
        db.add(post)
        db.commit()
        db.refresh(post)

        posts_out.append({
            "id": post.id,
            "title": post.title,
            "scheduled_at": post.scheduled_at,
            "hooks": hooks,
            "hashtags": best_tags
        })

    return {"message": "7-day strategy created", "posts": posts_out}
@router.post("/linkedin/post")
async def linkedin_post(post_id: int, db: Session = Depends(get_db)):
    """
    Publish a post to LinkedIn using saved access token.
    """
    # Get post
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Get user with token (for now pick first user, later tie posts to user)
    user = db.query(User).first()
    if not user or not user.access_token:
        raise HTTPException(status_code=403, detail="User not authenticated")

    # Build LinkedIn API payload
    text = f"{post.title}\n\n{post.body}\n\n{' '.join(post.hashtags.split(','))}"

    payload = {
        "author": f"urn:li:person:{user.li_person_urn}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }

    # Call LinkedIn API
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://api.linkedin.com/v2/ugcPosts",
            headers={"Authorization": f"Bearer {user.access_token}",
                     "X-Restli-Protocol-Version": "2.0.0",
                     "Content-Type": "application/json"},
            json=payload,
        )

    if resp.status_code != 201:
        raise HTTPException(status_code=400, detail=f"LinkedIn post failed: {resp.text}")

    # Mark as posted
    post.status = "posted"
    db.commit()

    return {"message": "Post published to LinkedIn", "post_id": post.id}

from collections import defaultdict

@router.get("/analytics/trends")
def get_trends(db: Session = Depends(get_db)):
    """
    Returns daily aggregated metrics for line chart.
    """
    metrics = db.query(Metrics).all()
    posts = {p.id: p for p in db.query(Post).all()}

    daily = defaultdict(lambda: {"likes": 0, "comments": 0, "shares": 0, "impressions": 0})

    for m in metrics:
        post = posts.get(m.post_id)
        if not post or not post.created_at:
            continue
        date = post.created_at[:10]  # YYYY-MM-DD
        daily[date]["likes"] += m.likes
        daily[date]["comments"] += m.comments
        daily[date]["shares"] += m.shares
        daily[date]["impressions"] += m.impressions

    return [{"date": d, **vals} for d, vals in sorted(daily.items())]
@router.get("/analytics/posts")
def get_post_metrics(db: Session = Depends(get_db)):
    """
    Returns per-post engagement rate and status comparison.
    """
    posts = db.query(Post).all()
    metrics = db.query(Metrics).all()
    metrics_by_post = {m.post_id: m for m in metrics}

    out = []
    for p in posts:
        m = metrics_by_post.get(p.id)
        if not m:
            continue
        engagement = (m.likes + m.comments + m.shares) / max(1, m.impressions)
        out.append({
            "id": p.id,
            "title": p.title,
            "status": p.status,
            "engagement_rate": round(engagement, 3),
            "likes": m.likes,
            "comments": m.comments,
            "shares": m.shares,
            "impressions": m.impressions,
        })
    return out

# Register all routes under API router
app.include_router(router)
