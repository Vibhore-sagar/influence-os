"use client";
import { useState } from "react";

const API = "http://localhost:8000";

export default function ComposerPage() {
  const [topic, setTopic] = useState("");
  const [resp, setResp] = useState<any>(null);
  const [details, setDetails] = useState<any>(null);

  async function generate() {
    const r = await fetch(API + "/posts/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic }),
    });
    const j = await r.json();
    setResp(j);

    // Fetch detailed info (hooks, hashtags, etc.)
    const d = await fetch(API + `/posts/${j.id}/details`);
    setDetails(await d.json());
  }

  async function addMetrics() {
    if (!resp?.id) return;
    await fetch(API + `/metrics/${resp.id}/ingest`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        likes: 10,
        comments: 5,
        shares: 2,
        impressions: 100,
      }),
    });
    alert("Sample metrics added!");
  }
  async function publishReal() {
    if (!resp?.id) return;
    const r = await fetch(API + "/linkedin/post", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ post_id: resp.id }),
    });
    const j = await r.json();
    alert(j.message || "Failed to publish");
  }


  async function publishMock() {
    if (!resp?.id) return;
    const text = `${resp.title}\n\n${resp.body}\n\n${details?.hashtags_final.join(" ")}`;
    const r = await fetch(API + "/linkedin/mock_post", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ post_id: resp.id, text }),
    });
    const j = await r.json();
    alert(j.ok ? "✅ Mock published! (No real LinkedIn call)" : "❌ Failed");
  }

  return (
    <div>
      <h2>Post Composer</h2>
      <input
        value={topic}
        onChange={(e) => setTopic(e.target.value)}
        placeholder="Enter topic"
      />
      <button onClick={generate}>Generate Post</button>

      {resp && (
        <div style={{ marginTop: "20px" }}>
          <h3>{resp.title}</h3>
          <p>{resp.body}</p>
          <p>
            <b>Final Hashtags:</b> {details?.hashtags_final.join(" ")}
          </p>

          <h4>Hook Variants (A/B)</h4>
          <ul>
            {details?.hooks.map((h: string, i: number) => (
              <li key={i}>{h}</li>
            ))}
          </ul>

          <h4>Other Candidate Hashtags</h4>
          <p>{details?.hashtags_raw.join(" ")}</p>

          <button onClick={addMetrics}>Add Sample Metrics</button>
          <button onClick={publishMock}>Publish to LinkedIn (mock)</button>
          <button onClick={publishReal}>Publish to LinkedIn (real)</button>

        </div>
      )}
    </div>
  );
}
