"use client";
import { useState } from "react";
const API = "http://localhost:8000";

export default function Onboarding() {
  const [about, setAbout] = useState("");
  const [resp, setResp] = useState<any>(null);

  async function submit() {
    const r = await fetch(API + "/profile/ingest", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ about })
    });
    setResp(await r.json());
  }

  return (
    <div>
      <h2>Onboarding</h2>
      <textarea value={about} onChange={e => setAbout(e.target.value)} rows={5} style={{ width: "100%" }} />
      <button onClick={submit}>Submit</button>
      {resp && <pre>{JSON.stringify(resp, null, 2)}</pre>}
    </div>
  );
}
