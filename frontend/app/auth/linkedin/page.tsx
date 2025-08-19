"use client";
import { useState } from "react";

const API = "http://localhost:8000";

export default function LinkedInAuthPage() {
    const [authUrl, setAuthUrl] = useState<string | null>(null);

    async function getAuthUrl() {
        const r = await fetch(API + "/auth/linkedin/login");
        const j = await r.json();
        setAuthUrl(j.auth_url);
        window.location.href = j.auth_url; // redirect user to LinkedIn
    }

    return (
        <div>
            <h2>Connect LinkedIn</h2>
            <p>This will open LinkedIn for login & consent.</p>
            <button onClick={getAuthUrl}>Continue with LinkedIn</button>
            {authUrl && <p>Redirecting…</p>}
        </div>
    );
}
