from fastapi import APIRouter, Query
from datetime import date
import requests, random

router = APIRouter()

API_KEY = "513268ac6988204443cd651a5f22a362"  # ⚠️ Replace with your API key
BASE_URL = "https://v3.football.api-sports.io"
headers = {"x-apisports-key": API_KEY}

# ---------- Prediction pool ----------
PREDICTIONS_TIPS = [
    ("Home Win", "Home team is strong today, likely to win."),
    ("Away Win", "Away team is on a hot streak, might win."),
    ("Draw", "Both teams are equally matched."),
    ("Home Win", "Home team has advantage on home ground."),
    ("Away Win", "Away team scored more goals recently."),
    ("Draw", "Expect a tight game, likely a draw."),
    ("Home Win", "Strong defense from home team."),
    ("Away Win", "Away team is fast on counter-attacks."),
    ("Draw", "Both teams play cautiously."),
    ("Home Win", "Home team has better midfield control."),
    ("Away Win", "Away team has better attacking stats."),
    ("Draw", "History shows this fixture often ends in a draw."),
    ("Home Win", "Home team favored by fans."),
    ("Away Win", "Away team’s top scorer is in form."),
    ("Draw", "Game could end 1-1 or 0-0."),
    ("Home Win", "Home team likely to dominate possession."),
    ("Away Win", "Away team’s goalkeeper is strong."),
    ("Draw", "Defensive tactics expected from both teams."),
    ("Home Win", "Home team predicted to score first."),
    ("Away Win", "Away team predicted to score last."),
]

def _pick():
    pred, tip = random.choice(PREDICTIONS_TIPS)
    return pred, tip

# ---------- Fixtures ----------
@router.get("/fixtures")
def get_fixtures(date_str: str | None = None):
    if not date_str:
        date_str = date.today().isoformat()
    try:
        r = requests.get(f"{BASE_URL}/fixtures", headers=headers, params={"date": date_str}, timeout=20)
        r.raise_for_status()
        data = r.json().get("response", [])
    except Exception as e:
        print("Fixtures error:", e)
        data = [
            {
                "fixture": {"id": 1, "date": f"{date_str}T12:00:00Z"},
                "teams": {"home": {"name": "Team A"}, "away": {"name": "Team B"}},
                "league": {"name": "Test League"},
            }
        ]

    fixtures = [
        {
            "id": f["fixture"]["id"],
            "home": f["teams"]["home"]["name"],
            "away": f["teams"]["away"]["name"],
            "league": f["league"]["name"],
            "time": f["fixture"]["date"],
        }
        for f in data
    ]
    return {"fixtures": fixtures}

# ---------- Pre-match ----------
@router.get("/prematch")
def prematch_mock(
    home: str = Query(...),
    away: str = Query(...),
    match_time: str | None = Query(None),
):
    prediction, tip = _pick()
    return {
        "teams": f"{home} vs {away}",
        "time": match_time or date.today().isoformat(),
        "prePrediction": prediction,
        "tip": tip,
    }

# ---------- Live ----------
@router.get("/live")
def live_predictions():
    try:
        r = requests.get(f"{BASE_URL}/fixtures", headers=headers, params={"live": "all"}, timeout=20)
        r.raise_for_status()
        live = r.json().get("response", [])
    except Exception as e:
        print("Live fetch error:", e)
        live = []

    results = []
    for m in live:
        home = m["teams"]["home"]["name"]
        away = m["teams"]["away"]["name"]

        status = (m.get("fixture", {}).get("status", {}) or {})
        minute = status.get("elapsed") or 0

        score = m.get("goals") or {}
        home_goals = score.get("home", 0)
        away_goals = score.get("away", 0)

        pre, tip = _pick()

        results.append({
            "id": m["fixture"]["id"],
            "teams": f"{home} vs {away}",
            "minute": minute,
            "score": f"{home_goals} - {away_goals}",
            "time": m["fixture"]["date"],
            "prePrediction": pre,
            "tip": tip,
            "league": m["league"]["name"],
        })

    return {"live_matches": results}
