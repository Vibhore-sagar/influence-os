"use client";
import { useEffect, useState } from "react";
import { Calendar, dateFnsLocalizer } from "react-big-calendar";
import format from "date-fns/format";
import parse from "date-fns/parse";
import startOfWeek from "date-fns/startOfWeek";
import getDay from "date-fns/getDay";
import "react-big-calendar/lib/css/react-big-calendar.css";

const API = "http://localhost:8000";

const locales = {
    "en-US": require("date-fns/locale/en-US"),
};
const localizer = dateFnsLocalizer({ format, parse, startOfWeek, getDay, locales });

export default function CalendarPage() {
    const [events, setEvents] = useState<any[]>([]);

    useEffect(() => {
        fetch(API + "/calendar")
            .then(r => r.json())
            .then(data => {
                setEvents(
                    data.map((p: any) => ({
                        id: p.id,
                        title: p.title,
                        start: new Date(p.scheduled_at),
                        end: new Date(p.scheduled_at),
                    }))
                );
            });
    }, []);

    async function generatePlan() {
        const r = await fetch(API + "/strategy/plan", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ focus: "AI & Tech Strategy" })
        });
        const j = await r.json();
        alert("Plan generated!");
        window.location.reload();
    }

    return (
        <div>
            <h2>Content Calendar</h2>
            <button onClick={generatePlan}>Generate 2-Week Plan</button>
            <Calendar
                localizer={localizer}
                events={events}
                startAccessor="start"
                endAccessor="end"
                style={{ height: 600, margin: "20px" }}
            />
        </div>
    );
}
