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

@app.route("/scrape", methods=["POST"])
def scrape_website():
    try:
        data = request.get_json()
        url = data.get("url")
        level_user = data.get("level")
        user_id = data.get("user_id")

        if not url or not level_user:
            return jsonify({"error": "URL and user level are required."}), 400

        res = db_conn.filter_words(level_user, url, user_id)

        return jsonify(res)

    except Exception as e:
        print(f"Error during scraping: {e}")
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

    if res.get("error"):
        error_code = res["error"]
        error_messages = {
            "email-used": "This email is already in use.",
            "username-used": "This username is already taken.",
            "password-security-low": "Password does not meet security requirements.",
            "firebase-email-error": "Error checking email availability. Please try again.",
            "firebase-username-error": "Error checking username availability. Please try again.",
            "password-hashing-error": "Error hashing the password. Please try again.",
            "user-creation-error": "Error creating user. Please try again.",
            "word-bank-creation-error": "Error creating word bank entry. Please try again.",
        }
        return jsonify({"error": error_messages.get(error_code, "An unexpected error occurred.")}), 400

    return jsonify({"message": "Signup successful!"}), 200



@app.route("/checkuser", methods=["GET"])
def check_user():
    data = request.get_json()
    id_user = data.get("id")
    res = db_conn.checkUser(id_user)
    if res == "true":
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"error": res}), 400

@app.route("/remove", methods=["GET"])
def removes():
    user_result = db_conn.remove_word_db()
    return user_result


@app.route("/addwordbank", methods=["POST"])
def addWordsUser():
    data = request.get_json();
    id_user = data.get("id");
    word_name = data.get("word")
    word_id = db_conn.check_word_id(word_name);
    user_words = db_conn.add_word_to_bank(id_user, word_id)
    return user_words

@app.route("/checkword", methods=["GET"])
def checkWord():
    # Get the word from the query parameters
    word = request.args.get("word")
    if not word:
        return jsonify({"error": "No word provided"}), 400

    result = db_conn.check_word(word)
    return jsonify(result)



if __name__ == "__main__":
    app.run(debug=True)
