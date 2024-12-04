from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import pipeline
from bs4 import BeautifulSoup
import requests
from db.database import Database
import re

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})

db_conn = Database()
translator = pipeline("translation", model="Helsinki-NLP/opus-mt-en-cs")

@app.route("/scrape", methods=["GET"])
def scrape_website():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    print(f"Received URL: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        clean_text = soup.get_text(separator=" ", strip=True)
        clean_text = " ".join(clean_text.split())

        return jsonify({"text": clean_text})
    except Exception as e:
        print(f"Error occurred: {str(e)}")
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

    user_result = db_conn.loginUser(name, password)
    if isinstance(user_result, dict):
        return jsonify({"id": user_result["id"], "name": user_result["name"], "level": user_result["level"]}), 200
    elif user_result == "false-password":
        return jsonify({"error": "Incorrect password."}), 401
    elif user_result == "false-username":
        return jsonify({"error": "Username not found."}), 404
    else:
        return jsonify({"error": "An error occurred during login."}), 500

@app.route("/signupuser", methods=["POST"])
def signup_user():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    level = data.get("level")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"error": "Username, email, and password are required."}), 400

    res = db_conn.signupUser(name, email, level, password)

    if res == "email-error":
        return jsonify({"error": "Email is already used."}), 400
    elif res == "username-error":
        return jsonify({"error": "Username is already taken."}), 400
    elif res:
        return jsonify({"message": "Signup successful!"}), 200
    else:
        return jsonify({"error": "Signup failed."}), 500

@app.route("/filter-words", methods=["POST"])
def filter_words():
    try:
        data = request.get_json()
        text = data.get("text", "")
        user_level = "4"
        if not text or user_level is None:
            return jsonify({"error": "Invalid input. 'text' and 'user_level' are required."}), 400

        print(text)
        # cleaned_words = [
        #     re.sub(r"[^a-zA-Z0-9\s]", "", word).lower() for word in text.split()
        # ]

        # highlighted_words = db_conn.filterWords(cleaned_words, int(user_level))
        # print(highlighted_words)

        return jsonify({"highlighted_words": highlighted_words}), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500


@app.route("/checkuser", methods=["GET"])
def check_user():
    data = request.get_json()
    id_user = data.get("id")
    res = db_conn.checkUser(id_user)
    return res



if __name__ == "__main__":
    app.run(debug=True)
