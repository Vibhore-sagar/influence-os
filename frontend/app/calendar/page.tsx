"use client";
import useSWR from "swr";

const API = "http://localhost:8000";
const fetcher = (url: string) => fetch(url).then(r => r.json());

export default function CalendarPage() {
    const { data } = useSWR(API + "/calendar", fetcher);

    if (!data) return <p>Loading...</p>;

    // Group posts by date
    const grouped: Record<string, any[]> = {};
    data.forEach((p: any) => {
        if (!p.scheduled_at) return;
        const date = p.scheduled_at.slice(0, 10); // YYYY-MM-DD
        if (!grouped[date]) grouped[date] = [];
        grouped[date].push(p);
    });

    // Build calendar for current month
    const now = new Date();
    const year = now.getFullYear();
    const month = now.getMonth(); // 0-based
    const firstDay = new Date(year, month, 1).getDay(); // weekday offset
    const daysInMonth = new Date(year, month + 1, 0).getDate();

    const days: (number | null)[] = [];
    for (let i = 0; i < firstDay; i++) days.push(null);
    for (let d = 1; d <= daysInMonth; d++) days.push(d);

    return (
        <div>
            <h2 className="text-xl font-bold mb-4">
                Calendar – {now.toLocaleString("default", { month: "long" })} {year}
            </h2>

            <div className="grid grid-cols-7 gap-2 border p-2">
                {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map(day => (
                    <div key={day} className="font-semibold text-center">{day}</div>
                ))}

                {days.map((d, idx) => {
                    const dateStr = d ? `${year}-${String(month + 1).padStart(2, "0")}-${String(d).padStart(2, "0")}` : "";
                    const posts = grouped[dateStr] || [];
                    return (
                        <div key={idx} className="border h-24 p-1 text-sm">
                            {d && <div className="font-bold">{d}</div>}
                            {posts.map(p => (
                                <div
                                    key={p.id}
                                    className={`mt-1 p-1 rounded text-white text-xs ${p.status === "posted" ? "bg-green-500" : "bg-yellow-500"
                                        }`}
                                >
                                    {p.title}
                                </div>
                            ))}
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
