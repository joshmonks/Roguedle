"""Builds games.json: top Steam roguelikes by reviews. Run weekly."""
import json, re, time, requests

TAGS = {1716: "Roguelike", 3959: "Roguelite", 1667: "Roguelike Deckbuilder"}
PAGES = 2              # 50 per page per tag
MAX_GAMES = 180        # appdetails allows ~200 requests / 5 min
GENRE_MAP = [("Deckbuilding", "Deckbuilder"), ("Tactical", "Tactical"),
             ("Platformer", "Platformer"), ("Twin Stick Shooter", "Shooter"),
             ("Shooter", "Shooter"), ("FPS", "Shooter"), ("Dungeon Crawler", "RPG"),
             ("RPG", "RPG"), ("Survival", "Survival"), ("Bullet Hell", "Survivors")]

def get(url, **params):
    for i in range(3):
        try:
            r = requests.get(url, params=params, timeout=30)
            r.raise_for_status()
            return r.json()
        except Exception:
            time.sleep(2 * (i + 1))
    return None

def app_ids():
    """Union of the three tags, interleaved so the cap keeps a balanced mix."""
    per_tag = {}
    for tag in TAGS:
        ids = []
        for p in range(PAGES):
            j = get("https://store.steampowered.com/search/results/", query="", start=p * 50,
                    count=50, infinite=1, category1=998, tags=tag, sort_by="Reviews_DESC")
            if j: ids += re.findall(r'data-ds-appid="(\d+)"', j["results_html"])
        per_tag[tag] = ids
    merged = [i for group in zip(*per_tag.values()) for i in group]
    merged += [i for ids in per_tag.values() for i in ids]
    deck = set(per_tag[1667])
    return list(dict.fromkeys(merged))[:MAX_GAMES], deck

def build(appid, is_deck=False):
    j = get("https://store.steampowered.com/api/appdetails", appids=appid, l="english", cc="us")
    d = (j or {}).get(appid, {}).get("data")
    if not d or not d.get("developers") or not d["release_date"].get("date"): return None
    year = re.search(r"\d{4}", d["release_date"]["date"])
    tags = (get("https://steamspy.com/api.php", request="appdetails", appid=appid) or {}).get("tags") or {}
    if not year: return None
    if d.get("is_free"): price = 0.0
    elif d.get("price_overview"): price = d["price_overview"]["initial"] / 100  # list price, ignores sales
    else: return None  # unreleased / no price
    return {
        "n": d["name"], "y": int(year.group()), "$": price,
        "s": "Deckbuilder" if is_deck else next((g for t, g in GENRE_MAP if t in tags), "Action"),
        "c": "Turn-based" if "Turn-Based" in tags or "Turn-Based Combat" in tags else "Real-time",
        "p": next((t.replace("Top-Down", "Top-down") for t in ["Isometric", "Top-Down", "3D", "2D"] if t in tags), "2D"),
        "o": "Yes" if any("Co-op" in c["description"] for c in d.get("categories", [])) else "No",
        "d": d["developers"][0]}

games = []
ids, deck_ids = app_ids()
for a in ids:
    g = build(a, a in deck_ids)
    if g: games.append(g)
    time.sleep(1.5)  # appdetails is rate-limited

if len(games) >= 40:  # don't overwrite a good file with a failed run
    json.dump(games, open("games.json", "w"), indent=1, ensure_ascii=False)
    print(f"wrote {len(games)} games")
else:
    raise SystemExit(f"only {len(games)} games; keeping old games.json")
