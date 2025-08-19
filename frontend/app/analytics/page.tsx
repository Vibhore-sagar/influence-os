"use client";
import useSWR from "swr";
import {
    ResponsiveContainer,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    Tooltip,
    CartesianGrid,
    PieChart,
    Pie,
    Cell,
    Legend,
    LineChart,
    Line
} from "recharts";

const API = "http://localhost:8000";
const fetcher = (url: string) => fetch(url).then(r => r.json());

const COLORS = ["#8884d8", "#82ca9d", "#ffc658", "#ff8042"];

export default function AnalyticsPage() {
    const { data } = useSWR(API + "/analytics/summary", fetcher);
    const { data: trends } = useSWR(API + "/analytics/trends", fetcher);
    const { data: posts } = useSWR(API + "/analytics/posts", fetcher);

    if (!data) return <p>Loading...</p>;

    const totals = [
        { name: "Likes", value: data.totals.likes },
        { name: "Comments", value: data.totals.comments },
        { name: "Shares", value: data.totals.shares },
        { name: "Impressions", value: data.totals.impressions },
    ];

    return (
        <div>
            <h2>📊 Analytics Dashboard</h2>

            {/* Totals */}
            <h3>Totals</h3>
            <ResponsiveContainer width="100%" height={300}>
                <BarChart data={totals}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="value" fill="#8884d8" />
                </BarChart>
            </ResponsiveContainer>

            {/* Engagement Breakdown */}
            <h3>Engagement Breakdown</h3>
            <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                    <Pie
                        data={totals}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        outerRadius={100}
                        dataKey="value"
                    >
                        {totals.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                </PieChart>
            </ResponsiveContainer>

            {/* Best Post */}
            <h3>Best Post</h3>
            {data.best_post ? (
                <div style={{ padding: "12px", border: "1px solid #ddd", borderRadius: "8px", marginTop: "12px" }}>
                    <b>{data.best_post.title}</b>
                    <p>Engagement: {data.best_post.engagement}</p>
                </div>
            ) : (
                <p>No posts yet.</p>
            )}

            {/* Trends Over Time */}
            <h3>📈 Trends Over Time</h3>
            {trends && (
                <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={trends}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="likes" stroke="#8884d8" />
                        <Line type="monotone" dataKey="comments" stroke="#82ca9d" />
                        <Line type="monotone" dataKey="shares" stroke="#ffc658" />
                        <Line type="monotone" dataKey="impressions" stroke="#ff8042" />
                    </LineChart>
                </ResponsiveContainer>
            )}

            {/* Per-Post Engagement Table */}
            <h3>🔍 Post Engagement</h3>
            {posts && (
                <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "12px" }}>
                    <thead>
                        <tr>
                            <th style={{ border: "1px solid #ddd", padding: "8px" }}>Title</th>
                            <th style={{ border: "1px solid #ddd", padding: "8px" }}>Status</th>
                            <th style={{ border: "1px solid #ddd", padding: "8px" }}>Engagement Rate</th>
                            <th style={{ border: "1px solid #ddd", padding: "8px" }}>Likes</th>
                            <th style={{ border: "1px solid #ddd", padding: "8px" }}>Comments</th>
                            <th style={{ border: "1px solid #ddd", padding: "8px" }}>Shares</th>
                            <th style={{ border: "1px solid #ddd", padding: "8px" }}>Impressions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {posts.map((p: any) => (
                            <tr key={p.id}>
                                <td style={{ border: "1px solid #ddd", padding: "8px" }}>{p.title}</td>
                                <td style={{ border: "1px solid #ddd", padding: "8px" }}>{p.status}</td>
                                <td style={{ border: "1px solid #ddd", padding: "8px" }}>{p.engagement_rate}</td>
                                <td style={{ border: "1px solid #ddd", padding: "8px" }}>{p.likes}</td>
                                <td style={{ border: "1px solid #ddd", padding: "8px" }}>{p.comments}</td>
                                <td style={{ border: "1px solid #ddd", padding: "8px" }}>{p.shares}</td>
                                <td style={{ border: "1px solid #ddd", padding: "8px" }}>{p.impressions}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    );
}
