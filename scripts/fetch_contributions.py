#!/usr/bin/env python3
"""Fetch the last year of contributions via GitHub GraphQL -> data/contributions.json"""
import json, os, urllib.request, datetime as dt
from pathlib import Path

USER = os.environ.get("GH_USER", "LuckysHorizon")
TOKEN = os.environ["GH_TOKEN"]
Q = """query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{
weeks{contributionDays{date contributionCount}}}}}}"""
req = urllib.request.Request(
    "https://api.github.com/graphql",
    data=json.dumps({"query": Q, "variables": {"login": USER}}).encode(),
    headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"})
data = json.load(urllib.request.urlopen(req))
weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
days = [{"date": d["date"], "count": d["contributionCount"]} for w in weeks for d in w["contributionDays"]]
out = Path(__file__).resolve().parent.parent / "data" / "contributions.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps({"updated": dt.datetime.utcnow().isoformat() + "Z", "days": days}))
print(f"saved {len(days)} days")
