from pydantic import BaseModel
import os

class Settings(BaseModel):
    LINKEDIN_CLIENT_ID: str = os.getenv("LINKEDIN_CLIENT_ID", "")
    LINKEDIN_CLIENT_SECRET: str = os.getenv("LINKEDIN_CLIENT_SECRET", "")
    # Must exactly match what you register on LinkedIn
    LINKEDIN_REDIRECT_URI: str = os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:3000/auth/linkedin/callback")
    # scopes: r_liteprofile r_emailaddress; w_member_social is restricted (we won't use it for real posting)
    LINKEDIN_SCOPES: str = "r_liteprofile r_emailaddress"

settings = Settings()
