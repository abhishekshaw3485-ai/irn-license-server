from flask import Flask, request, jsonify
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)

FILE = "users.xlsx"

def load_users():
    try:
        return pd.read_excel(FILE)
    except:
        df = pd.DataFrame(columns=["email","plan","expiry","usage"])
        df.to_excel(FILE, index=False)
        return df

def save_users(df):
    df.to_excel(FILE, index=False)

# 🔥 ADD CORS HEADERS
@app.after_request
def add_cors_headers(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    resp.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    return resp

@app.route("/", methods=["GET"])
def home():
    return "IRN License Server is Running"

@app.route("/check_license", methods=["POST","OPTIONS"])
def check_license():
    if request.method == "OPTIONS":
        return "", 200

    email = request.json.get("email")
    df = load_users()

    user = df[df["email"] == email]

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

@app.route("/increment_usage", methods=["POST","OPTIONS"])
def increment_usage():
    if request.method == "OPTIONS":
        return "", 200

    email = request.json.get("email")
    df = load_users()

    if email in df["email"].values:
        df.loc[df.email == email, "usage"] += 1
    else:
        df.loc[len(df)] = [email,"free","2099-01-01",1]

    save_users(df)
    return jsonify({"status":"ok"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
