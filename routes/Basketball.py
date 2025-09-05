# routes/basketball.py
from fastapi import APIRouter, Query
from datetime import date
import requests, random

router = APIRouter()

API_KEY = "513268ac6988204443cd651a5f22a362"  # ⚠️ Use your own API key
BASE_URL = "https://v1.basketball.api-sports.io"   # Basketball API base
headers = {"x-apisports-key": API_KEY}

# ---------- Prediction pool ----------
PREDICTIONS_TIPS = [
    ("Home Win", "Home team is dominating the paint."),
    ("Away Win", "Away team is hot from 3-point line."),
    ("Draw", "Tight defense, close match expected."),
    ("Home Win", "Home crowd advantage will help."),
    ("Away Win", "Away team’s point guard is in top form."),
    ("Draw", "Expect overtime potential."),
    ("Home Win", "Home team rebounds better."),
    ("Away Win", "Away team has more fast-break points."),
    ("Home Win", "Star player likely to score 30+ points."),
    ("Away Win", "Bench depth gives away team the edge."),
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
        r = requests.get(
            f"{BASE_URL}/games",
            headers=headers,
            params={"date": date_str},
            timeout=20
        )
        r.raise_for_status()
        data = r.json().get("response", [])
    except Exception as e:
        print("Basketball fixtures error:", e)
        data = [
            {
                "id": 1,
                "date": f"{date_str}T19:00:00Z",
                "teams": {"home": {"name": "Lakers"}, "away": {"name": "Warriors"}},
                "league": {"name": "NBA"},
            }
        ]

    fixtures = [
        {
            "id": g["id"],
            "home": g["teams"]["home"]["name"],
            "away": g["teams"]["away"]["name"],
            "league": g.get("league", {}).get("name", "Unknown League"),
            "time": g["date"],
        }
        for g in data
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
        r = requests.get(
            f"{BASE_URL}/games",
            headers=headers,
            params={"live": "all"},
            timeout=20
        )
        r.raise_for_status()
        live = r.json().get("response", [])
    except Exception as e:
        print("Basketball live fetch error:", e)
        live = []

    results = []
    for g in live:
        home = g["teams"]["home"]["name"]
        away = g["teams"]["away"]["name"]

        status = g.get("status", {}) or {}
        quarter = status.get("quarter", "Q1")

        score = g.get("scores", {}) or {}
        home_points = score.get("home", {}).get("points", 0)
        away_points = score.get("away", {}).get("points", 0)

        pre, tip = _pick()

        results.append({
            "id": g["id"],
            "teams": f"{home} vs {away}",
            "quarter": quarter,
            "score": f"{home_points} - {away_points}",
            "time": g["date"],
            "prePrediction": pre,
            "tip": tip,
            "league": g.get("league", {}).get("name", "Unknown League"),
        })

    return {"live_matches": results}
