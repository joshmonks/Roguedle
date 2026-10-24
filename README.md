# Roguedle

Daily "guess the roguelike" game. Static site on GitHub Pages, global stats in Firebase Firestore, game list refreshed weekly from Steam by GitHub Actions.

## Setup
1. **Firebase**: create a project, then enable **Firestore** (production mode) and **Authentication > Anonymous**.
2. Register a **web app** in Project settings and paste its config into `firebase-config.js`.
3. Authentication > Settings > **Authorized domains**: add `<your-username>.github.io`.
4. Deploy the rules: `npm i -g firebase-tools && firebase login && firebase deploy --only firestore:rules --project <id>` (or paste `firestore.rules` into the console).
5. **GitHub**: push to `main`, then Settings > Pages > Source: **GitHub Actions**.

## How it works
- Daily answer = hash of the UTC date indexed into `games.json` (sorted by name).
- Stats: `days/{date}` holds `count` and `total`; `days/{date}/players/{uid}` makes each anonymous user count once. Rules only allow counters to move by exactly one player's guesses.
- `build_games.py` rebuilds `games.json` weekly (top games by reviews for Steam tags 1716 Roguelike, 3959 Roguelite and 1667 Roguelike Deckbuilder, via store search + appdetails + SteamSpy; capped at 180). Games in the deckbuilder tag get the Deckbuilder genre. Failed runs keep the old file.
- Run locally with `python -m http.server` (add `localhost` to authorized domains, which is on by default).

## Columns
Year, Price (USD list price, ignores sales), Genre, Combat, View, Co-op, Developer. Year is amber within 2 years; price within $5. Arrows point toward the answer. Seed prices in `games.json` are approximate until the first weekly refresh.
