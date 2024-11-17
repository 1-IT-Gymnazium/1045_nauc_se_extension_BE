from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import pipeline
from bs4 import BeautifulSoup
import requests
from db.database import Database

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})

db_conn = Database()
translator = pipeline("translation", model="Helsinki-NLP/opus-mt-en-cs")


@app.route("/scrape", methods=["GET"])
def scrape_website():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.get_text()
        return jsonify({"text": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/translate", methods=["POST"])
def translate_text():
    data = request.get_json()
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "No text provided."}), 400

    try:
        translated_text = translator(text, max_length=256)[0]["translation_text"]
        return jsonify({"translated_text": translated_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/loginuser", methods=["POST"])
def login_user():
    data = request.get_json()
    name = data.get("name")
    password = data.get("password")
    if not name or not password:
        return jsonify({"error": "Username and password required."}), 400

    user_exists = db_conn.loginUser(name, password)
    if user_exists == "true":
        return jsonify(name), 200

    elif (user_exists == "false-password"):
        return jsonify({"error": "password"}), 401

    elif (user_exists == "false-username"):
        return jsonify({"error": "password"}), 000

    return jsonify({"error": "password"}), 401


@app.route("/signupuser", methods=["POST"])
def signup_user():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    level = data.get("level")
    password = data.get("password")

    if not name or not email or not password or not  password:
        print("Missing username, email, or password")
        return jsonify({"error": "Username, email, and password are required."}), 400

    res = db_conn.signupUser(name, email, level, password)

    if res == "email-error":
        print(f"Email {email} is already used.")
        return jsonify({"error": "Email is already used."}), 400
    elif res == "username-error":
        print(f"Username {name} is already taken.")  # Debug log
        return jsonify({"error": "Username is already taken."}), 400
    elif res:
        return jsonify({"message": "Signup successful!"}), 200
    else:
        print("Signup failed")  # Debug log
        return jsonify({"error": "Signup failed."}), 500


if __name__ == "__main__":
    app.run(debug=True)

