from flask import Flask, render_template, request, redirect, url_for
from db import players, matches, scorecards

app = Flask(__name__)

# ---------------- HOME ----------------
@app.route("/")
def index():
    all_matches = matches.find()
    return render_template("index.html", matches=all_matches)

# ---------------- ADD MATCH ----------------
@app.route("/add_match", methods=["GET", "POST"])
def add_match():
    if request.method == "POST":
        match = {
            "_id": request.form["match_id"],
            "team1": request.form["team1"],
            "team2": request.form["team2"],
            "venue": request.form["venue"],
            "winner": request.form["winner"]
        }
        matches.insert_one(match)
        return redirect(url_for("index"))
    

    return render_template("add_match.html")

# ---------------- SCORECARD ----------------
@app.route("/scorecard/<match_id>", methods=["GET", "POST"])
def scorecard(match_id):
    if request.method == "POST":
        entry = {
            "match_id": match_id,
            "format": request.form["format"],
            "player": request.form["player"],

            "runs": int(request.form["runs"]),
            "balls": int(request.form["balls"]),
            "not_out": int(request.form["not_out"]),
            "fours": int(request.form["fours"]),
            "sixes": int(request.form["sixes"]),

            "balls_bowled": int(request.form["balls_bowled"]),
            "runs_conceded": int(request.form["runs_conceded"]),
            "wickets": int(request.form["wickets"])
        }

        scorecards.insert_one(entry)
        return redirect(url_for("scorecard", match_id=match_id))

    data = scorecards.find({"match_id": match_id})
    return render_template("scorecard.html", data=data, match_id=match_id)


# ---------------- PLAYER STATS ----------------
from collections import defaultdict

@app.route("/player/<name>")
def player_stats(name):
    records = list(scorecards.find({"player": name}))

    formats = ["Test", "ODI", "T20", "Total"]
    stats = {}

    for fmt in formats:
        if fmt == "Total":
         fmt_records = records
        else:
         fmt_records = [r for r in records if r.get("format") == fmt]



                


        # ---------- BATTING ----------
        inns = 0
        not_outs = 0
        runs = 0
        balls = 0
        fours = 0
        sixes = 0
        hundreds = 0
        fifties = 0
        highest = 0

        # ---------- BOWLING ----------
        bowl_inns = 0
        balls_bowled = 0
        runs_conceded = 0
        wickets = 0
        best_bowling = 0
        four_w = 0
        five_w = 0

        # For 10w (Test only)
        match_wickets = defaultdict(int)

        for r in fmt_records:
            # -------- Batting --------
            inns += 1
            r_runs = r.get("runs", 0)
            r_balls = r.get("balls", 0)

            runs += r_runs
            balls += r_balls
            fours += r.get("fours", 0)
            sixes += r.get("sixes", 0)

            highest = max(highest, r_runs)

            if r.get("not_out", 0) == 1:
                not_outs += 1

            if r_runs >= 100:
                hundreds += 1
            elif r_runs >= 50:
                fifties += 1

            # -------- Bowling --------
            r_wickets = r.get("wickets", 0)
            r_balls_bowled = r.get("balls_bowled", 0)
            r_runs_conceded = r.get("runs_conceded", 0)

            if r_balls_bowled > 0:
                bowl_inns += 1
                balls_bowled += r_balls_bowled
                runs_conceded += r_runs_conceded
                wickets += r_wickets
                best_bowling = max(best_bowling, r_wickets)

                if r_wickets >= 4:
                    four_w += 1
                if r_wickets >= 5:
                    five_w += 1

                # For 10w logic
                match_wickets[r["match_id"]] += r_wickets

        ten_w = 0
        ten_w = 0
        if fmt == "Test" or fmt == "Total":
            ten_w = sum(1 for w in match_wickets.values() if w >= 10)


        batting_avg = runs / (inns - not_outs) if inns - not_outs > 0 else 0
        strike_rate = (runs / balls) * 100 if balls > 0 else 0

        bowling_avg = runs_conceded / wickets if wickets > 0 else 0
        economy = (runs_conceded / balls_bowled) * 6 if balls_bowled > 0 else 0
        bowling_sr = balls_bowled / wickets if wickets > 0 else 0

        stats[fmt] = {
            "inns": inns,
            "not_outs": not_outs,
            "runs": runs,
            "highest": highest,
            "average": round(batting_avg, 2),
            "balls": balls,
            "strike_rate": round(strike_rate, 2),
            "hundreds": hundreds,
            "fifties": fifties,
            "fours": fours,
            "sixes": sixes,

            "bowl_inns": bowl_inns,
            "balls_bowled": balls_bowled,
            "runs_conceded": runs_conceded,
            "wickets": wickets,
            "best_bowling": best_bowling,
            "bowling_avg": round(bowling_avg, 2),
            "economy": round(economy, 2),
            "bowling_sr": round(bowling_sr, 2),
            "four_w": four_w,
            "five_w": five_w,
            "ten_w": ten_w
        }

    return render_template(
        "player_stats.html",
        name=name,
        stats=stats
    )

@app.route("/delete_match/<match_id>", methods=["POST"])
def delete_match(match_id):
    # Delete all scorecards of this match
    scorecards.delete_many({"match_id": match_id})

    # Delete the match itself
    matches.delete_one({"_id": match_id})

    return redirect("/")



if __name__ == "__main__":
    app.run(debug=True)
