import requests
import icalendar
from datetime import datetime, timezone
import json
import os

ICAL_URL = os.environ["ICAL_URL"]
DISCORD_WEBHOOK = os.environ["DISCORD_WEBHOOK"]

data = requests.get(ICAL_URL).text
cal = icalendar.Calendar.from_ical(data)

now = datetime.now(timezone.utc)
messages = []

for event in cal.walk("VEVENT"):
    name = str(event.get("summary"))
    start = event.get("dtstart").dt

# Handle all-day events (date vs datetime)
if isinstance(start, datetime):
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
else:
    # Convert date → datetime at midnight UTC
    start = datetime.combine(start, datetime.min.time(), tzinfo=timezone.utc)


    delta = start - now
event_id = name + str(start)

if 23*3600 < delta.total_seconds() < 24*3600:
    if event_id in seen:
        continue
    seen.add(event_id)


messages.sort()

for start, name in messages[:5]:
    payload = {
        "embeds": [{
            "title": name,
            "description": "Upcoming Canvas event",
            "fields": [
                {"name": "Time", "value": start.strftime("%Y-%m-%d %H:%M UTC")}
            ],
            "color": 3447003
        }]
    }
    requests.post(DISCORD_WEBHOOK, json=payload)
