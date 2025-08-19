"use client";
import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";

const API = "http://localhost:8000";

export default function LinkedInCallbackPage() {
    const params = useSearchParams();
    const code = params.get("code");
    const state = params.get("state");
    const [result, setResult] = useState<any>(null);
    const [err, setErr] = useState<any>(null);

    useEffect(() => {
        async function go() {
            if (!code) return;
            try {
                const r = await fetch(`${API}/auth/linkedin/callback?code=${encodeURIComponent(code)}&state=${encodeURIComponent(state || "demo123")}`);
                const j = await r.json();
                setResult(j);
            } catch (e: any) {
                setErr(e);
            }
        }
        go();
    }, [code, state]);

    return (
        <div>
            <h2>LinkedIn Callback</h2>
            {!code && <p>Missing code.</p>}
            {err && <pre>{String(err)}</pre>}
            {result && (
                <>
                    <p>Linked ✅</p>
                    <pre>{JSON.stringify(result, null, 2)}</pre>
                    <a href="/composer">Go to Composer →</a>
                </>
            )}
        </div>
    );
}
