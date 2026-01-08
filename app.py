from flask import Flask, request, jsonify
import pandas as pd
from datetime import datetime

app = Flask(__name__)

def load():
    return pd.read_excel("users.xlsx")

def save(df):
    df.to_excel("users.xlsx", index=False)

@app.route("/check_license", methods=["POST"])
def check_license():
    email = request.json["email"]
    df = load()

    user = df[df.email == email]

    if user.empty:
        return jsonify({"plan":"free","usage":0,"limit":50})

    expiry = pd.to_datetime(user.iloc[0]["expiry"])

    if expiry < datetime.today():
        return jsonify({"plan":"expired"})

    return jsonify({
        "plan": user.iloc[0]["plan"],
        "usage": int(user.iloc[0]["usage"]),
        "limit":50
    })

@app.route("/increment_usage", methods=["POST"])
def inc():
    email = request.json["email"]
    df = load()

    if email in df.email.values:
        df.loc[df.email==email, "usage"] += 1
    else:
        df.loc[len(df)] = [email,"free","2099-01-01",1]

    save(df)
    return {"status":"ok"}

app.run()
