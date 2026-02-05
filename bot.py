import requests
import icalendar
from datetime import datetime, timezone
import json
import os

ICAL_URL = os.environ["https://auburn.instructure.com/feeds/calendars/user_woolTC1ifghVMuSSrH2xMXfnFWmN9R7lwrVPNKlp.ics"]
DISCORD_WEBHOOK = os.environ["https://discord.com/api/webhooks/1462163119160692941/GyyotPPKyCfPA64PJw10Gq3IsHJER-MplSkLH17wFQdQyYsrfRlmGagkkvzoW-Jecb17"]

data = requests.get(ICAL_URL).text
cal = icalendar.Calendar.from_ical(data)

now = datetime.now(timezone.utc)
messages = []

for event in cal.walk("VEVENT"):
    name = str(event.get("summary"))
    start = event.get("dtstart").dt

    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)

    if start > now:
        messages.append((start, name))

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
