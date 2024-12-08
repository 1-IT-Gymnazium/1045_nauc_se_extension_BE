import firebase_admin
from firebase_admin import credentials, db, auth
import bcrypt
import os
from utils.password_security import check_password
from utils.scrape_text import scrape_text_utils
from firebase_admin.exceptions import FirebaseError

class Database:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        cred_path = os.path.join(base_dir, "../config/firebaseKey.json")

        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred,
            {
                "databaseURL": "https://naucse-a8142-default-rtdb.europe-west1.firebasedatabase.app"
            })

        self.user_ref = db.reference("users")
        self.words_ref = db.reference("words")

    def loginUser(self, name, password):
        try:
            res = self.user_ref.order_by_child("name").equal_to(name).get()
            if res:
                for user_id, user_data in res.items():
                    hash_pass = user_data.get("password")
                    level_id = user_data.get("level_id")
                    if hash_pass and bcrypt.checkpw(password.encode("utf-8"), hash_pass.encode("utf-8")):
                        return {"id": user_id, "name": user_data.get("name"), "level": user_data.get("level_id")}
                    else:
                        return "false-password"
            else:
                return "false-username"
        except Exception as e:
            print(f"Error during login: {e}")
            return "false-error"

    def signupUser(self, name, email, level, password):
        try:
            check_password(password)

            existing_email_user = self.user_ref.order_by_child("email").equal_to(email).get()
            if existing_email_user:
                return "email-error"

            existing_name_user = self.user_ref.order_by_child("name").equal_to(name).get()
            if existing_name_user:
                return "username-error"

            hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

            new_user_ref = self.user_ref.push({
                "name": name,
                "email": email,
                "password": hashed_password,
                "level_id": level,
            })
            return "Signup successful!"
        except Exception as e:
            print(f"Error during signup: {e}")
            return "Signup failed."

    # def filter_words(self, user_level, web_url):
    #     try:

    #         web_words = scrape_text_utils(web_url)
    #         if not web_words:
    #             return {"error": "No words found in the provided URL."}

    #         filtered_words = {}
    #         for word in web_words:
    #             word_data = self.words_ref.order_by_child("name").equal_to(word).get()
    #             if word_data:
    #                 for key, value in word_data.items():
    #                     word_level = int(value.get("level", 0))
    #                     if word_level > int(user_level):
    #                         filtered_words[word] = word_level

    #         return filtered_words
    #     except Exception as e:
    #         print(f"Filtering error: {e}")
    #         return {"error": str(e)}


    def filter_words(self, user_level, web_url):
        try:
            # Scrape words from the website
            web_words = scrape_text_utils(web_url)
            if not web_words:
                return {"error": "No words found in the provided URL."}

            # Fetch all words from Firebase in one go
            all_words_data = self.words_ref.order_by_child("name").get()
            if not all_words_data:
                return {"error": "No word data found in the database."}

            # Prepare a mapping of valid words based on user level
            valid_words = {
                word_data['name']: int(word_data['level'])
                for word_data in all_words_data.values()
            }

            # Filter words from the web_words list using valid_words dictionary
            filtered_words = {
                word: valid_words[word]
                for word in web_words if word in valid_words and valid_words[word] > int(user_level)
            }

            return filtered_words

        except Exception as e:
            print(f"Filtering error: {e}")
            return {"error": str(e)}

    def checkUser(self, user_id):
        try:
            print(f"Attempting to fetch user with ID: {user_id}")
            user = auth.get_user(user_id)  # Ensure this is the correct UID
            print(f"User found: {user.uid}")
            return "true"
        except auth.UserNotFoundError as e:
            print(f"Error fetching user: {e}")
            return "false-user-not-found"
        except FirebaseError as e:
            print(f"Error fetching user: {e}")
            return "false-error"


    # def remove_word_db(self):
    #     try:
    #         # Fetch all word data from Firebase
    #         all_words_data = self.words_ref.order_by_child("name").get()
    #         if not all_words_data:
    #             return {"error": "No word data found in the database."}

    #         # Loop through all words and check their length
    #         for word_id, word_data in all_words_data.items():
    #             word_name = word_data.get('name', '').lower()  # Ensure case-insensitive comparison
    #             if len(word_name) == 1 and word_name not in ['a', 'i']:  # Exclude 'a' and 'i'
    #                 # Remove word from the database
    #                 self.words_ref.child(word_id).delete()  # Use delete() instead of remove()

    #         return {"success": "Single-character words (except 'a' and 'i') removed."}

    #     except Exception as e:
    #         print(f"Error removing words: {e}")
    #         return {"error": str(e)}

