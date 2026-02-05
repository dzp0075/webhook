import requests
import icalendar
from datetime import datetime, timezone
import json
import os

ICAL_URL = os.environ["ICAL_URL"]
DISCORD_WEBHOOK = os.environ["DISCORD_WEBHOOK"]
SEEN_FILE = "seen.json"

TARGET_CLASS = "COMP-4710"

REMINDER_WINDOWS = [
    (23*3600, 24*3600, "📅 24 hour reminder"),
    (55*60, 65*60, "⏰ 1 hour reminder"),
    (8*60, 12*60, "🚨 10 minute reminder"),
]

try:
    with open(SEEN_FILE, "r") as f:
        seen = set(json.load(f))
except:
    seen = set()

data = requests.get(ICAL_URL).text
cal = icalendar.Calendar.from_ical(data)

now = datetime.now(timezone.utc)

for event in cal.walk("VEVENT"):
    name = str(event.get("summary"))
    start = event.get("dtstart").dt

    course_text = str(event.get("location", "")) + str(event.get("description", ""))
    if TARGET_CLASS not in course_text:
        continue

    if isinstance(start, datetime):
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
    else:
        start = datetime.combine(start, datetime.min.time(), tzinfo=timezone.utc)

    delta = start - now
    seconds = delta.total_seconds()

    event_base_id = name + str(start)

    for min_s, max_s, label in REMINDER_WINDOWS:
        event_id = event_base_id + label

        if min_s < seconds < max_s:
            if event_id in seen:
                continue

            seen.add(event_id)

            payload = {
                "embeds": [{
                    "title": name,
                    "description": label,
                    "fields": [
                        {"name": "Course", "value": TARGET_CLASS},
                        {"name": "Time", "value": start.strftime("%Y-%m-%d %H:%M UTC")}
                    ],
                    "color": 3447003
                }]
            }
            requests.post(DISCORD_WEBHOOK, json=payload)

with open(SEEN_FILE, "w") as f:
    json.dump(list(seen), f)
