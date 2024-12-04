import firebase_admin
from firebase_admin import credentials, db
import bcrypt
import os
from services.chech_password import check_password


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

    def filterWords(self, cleaned_words, user_level):
        try:
            user_level = int(user_level)
            filtered_words = {}
            db_results = self.words_ref.get()

            if not db_results:
                print("No data found in the database.")
                return {}

            for word in cleaned_words:
                word_lower = word.lower().strip()

                for unique_id, word_data in db_results.items():
                    if not isinstance(word_data, dict):
                        continue

                    db_word = word_data.get("name", "").lower().strip()
                    db_level = int(word_data.get("level", 0))

                    # Check if the word is in the database and the level is higher
                    if word_lower == db_word and db_level > user_level:
                        filtered_words[word] = {"level": db_level}  # Add to dict
                        break

            print("Filtered Words:", filtered_words)
            return filtered_words
        except Exception as e:
            print(f"Error in filterWords: {e}")
            return {}

    def checkUser(self, user_id):
        try :
            user = auth.get_user(user_id)

            return "true"

        except firebase_admin.auth.AuthError as e:
            print(f"Error fetching user: {e}")
            return "false"
