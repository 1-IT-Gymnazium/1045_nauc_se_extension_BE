# import firebase_admin
# from firebase_admin import credentials, db, auth
# import bcrypt
# import os
# from utils.password_security import check_password
# from utils.scrape_text import scrape_text_utils
# from firebase_admin.exceptions import FirebaseError

# class Database:
#     def __init__(self):
#         base_dir = os.path.dirname(os.path.abspath(__file__))
#         cred_path = os.path.join(base_dir, "../config/firebaseKey.json")

#         if not firebase_admin._apps:
#             cred = credentials.Certificate(cred_path)
#             firebase_admin.initialize_app(cred,
#             {
#                 "databaseURL": "https://naucse-a8142-default-rtdb.europe-west1.firebasedatabase.app"
#             })

#         self.user_ref = db.reference("users")
#         self.words_ref = db.reference("words")
#         self.word_bank_ref = db.reference("users_word_bank")

#     def loginUser(self, name, password):
#         try:
#             res = self.user_ref.order_by_child("name").equal_to(name).get()
#             if res:
#                 for user_id, user_data in res.items():
#                     hash_pass = user_data.get("password")
#                     level_id = user_data.get("level_id")
#                     if hash_pass and bcrypt.checkpw(password.encode("utf-8"), hash_pass.encode("utf-8")):
#                         return {"id": user_id, "name": user_data.get("name"), "level": user_data.get("level_id")}
#                     else:
#                         return "false-password"
#             else:
#                 return "false-username"
#         except Exception as e:
#             print(f"Error during login: {e}")
#             return "false-error"

#     def signupUser(self, name, email, level, password):
#         try:

#             if not check_password(password):
#                 return {"error": "password-security-low"}

#             try:
#                 existing_email_user = self.user_ref.order_by_child("email").equal_to(email).get()
#                 if existing_email_user:
#                     return {"error": "email-used"}
#             except FirebaseError as e:
#                 return {"error": "firebase-email-error"}

#             try:
#                 existing_name_user = self.user_ref.order_by_child("name").equal_to(name).get()
#                 if existing_name_user:
#                     return {"error": "username-used"}
#             except FirebaseError as e:
#                 return {"error": "firebase-username-error"}

#             try:
#                 hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
#             except Exception as e:
#                 return {"error": "password-hashing-error"}

#             try:
#                 new_user_ref = self.user_ref.push({
#                     "name": name,
#                     "email": email,
#                     "password": hashed_password,
#                     "level_id": level,
#                 })
#                 user_id = new_user_ref.key
#             except FirebaseError as e:
#                 return {"error": "user-creation-error"}

#             try:
#                 self.word_bank_ref.push({
#                     "users_id": user_id,
#                     "words_id": []
#                 })
#             except FirebaseError as e:
#                 return {"error": "word-bank-creation-error"}

#             return {"success": "Signup successful!"}

#         except Exception as e:
#             return {"error": f"unexpected-error: {str(e)}"}



#     def checkUser(self, user_id):
#         try:
#             print(f"Attempting to fetch user with ID: {user_id}")
#             user = auth.get_user(user_id)
#             print(f"User found: {user.uid}")
#             return "true"
#         except auth.UserNotFoundError as e:
#             print(f"Error fetching user: {e}")
#             return "false-user-not-found"
#         except FirebaseError as e:
#             print(f"Error fetching user: {e}")
#             return "false-error"


#     def filter_words(self, user_level, web_url, user_id):
#         try:
#             web_words = scrape_text_utils(web_url)
#             if not web_words:
#                 return {"error": "No words found in the provided URL."}


#             all_words_data = self.words_ref.order_by_child("name").get()
#             if not all_words_data:
#                 return {"error": "No word data found in the database."}

#             valid_words = {
#                 word_data['name']: int(word_data['level'])
#                 for word_data in all_words_data.values()
#             }
#             filtered_words = {
#                 word: valid_words[word]
#                 for word in web_words if word in valid_words and valid_words[word] > int(user_level)
#             }

#             return filtered_words

#         except Exception as e:
#             print(f"Filtering error: {e}")
#             return {"error": str(e)}


#     def add_word_to_bank(self, user_id, word_id):
#         try:
#             # Query the database for the user's word bank
#             word_bank_query = self.word_bank_ref.order_by_child("users_id").equal_to(user_id).get()

#             if word_bank_query:
#                 # Loop through the results to update the correct word bank
#                 for doc_id, doc_data in word_bank_query.items():
#                     word_bank_ref = self.word_bank_ref.child(doc_id)
#                     words_id = doc_data.get('words_id', [])

#                     # Check if 'words_id' is not a list, initialize it to an empty list
#                     if not isinstance(words_id, list):
#                         words_id = []

#                     # Add word_id to the list if it's not already there
#                     if word_id not in words_id:
#                         words_id.append(word_id)
#                         word_bank_ref.update({
#                             "words_id": words_id
#                         })
#                     else:
#                         return "Word already exists in user's word bank."
#                 return "Word added successfully!"
#             else:
#                 return "User's word bank not found."
#         except Exception as e:
#             print(f"Error adding word: {e}")
#             return "Failed to add word."


#     def check_word_id(self, word):
#         try:
#             # Query the database for the word
#             result = self.words_ref.order_by_child("name").equal_to(word).get()

#             # Check if any results are returned
#             if result:
#                 # Since you expect only one result, get the first (and only) key
#                 word_id = next(iter(result.keys()))  # Extract the key (ID)
#                 return word_id
#             else:
#                 return False
#         except Exception as e:
#             print(f"Error checking word: {e}")
#             return False


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
        self.word_bank_ref = db.reference("users_word_bank")

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

            if not check_password(password):
                return {"error": "password-security-low"}

            try:
                existing_email_user = self.user_ref.order_by_child("email").equal_to(email).get()
                if existing_email_user:
                    return {"error": "email-used"}
            except FirebaseError as e:
                return {"error": "firebase-email-error"}

            try:
                existing_name_user = self.user_ref.order_by_child("name").equal_to(name).get()
                if existing_name_user:
                    return {"error": "username-used"}
            except FirebaseError as e:
                return {"error": "firebase-username-error"}

            try:
                hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            except Exception as e:
                return {"error": "password-hashing-error"}

            try:
                new_user_ref = self.user_ref.push({
                    "name": name,
                    "email": email,
                    "password": hashed_password,
                    "level_id": level,
                })
                user_id = new_user_ref.key
            except FirebaseError as e:
                return {"error": "user-creation-error"}

            try:
                self.word_bank_ref.push({
                    "users_id": user_id,
                    "words_id": []
                })
            except FirebaseError as e:
                return {"error": "word-bank-creation-error"}

            return {"success": "Signup successful!"}

        except Exception as e:
            return {"error": f"unexpected-error: {str(e)}"}



    def checkUser(self, user_id):
        try:
            user = self.user_ref.child(user_id).get()
            return True
        except auth.UserNotFoundError as e:
            return "false-user-not-found"
        except FirebaseError as e:
            return "false-error"


    def filter_words(self, user_level, web_url, user_id):
        try:
            # Step 1: Scrape words from the web URL
            web_words = scrape_text_utils(web_url)
            if not web_words:
                return {"error": "No words found in the provided URL."}

            # Step 2: Get the user's known words from the word bank
            known_words = self.get_user_word_bank(user_id)
            if isinstance(known_words, dict) and "error" in known_words:
                return known_words

            all_words_data = self.words_ref.get()
            if not all_words_data:
                return {"error": "No word data found in the database."}

            # Step 4: Filter out the words the user already knows from the valid words
            valid_words = {
                word_data['name']: int(word_data['level'])
                for word_id, word_data in all_words_data.items()
                if word_data['name'] not in known_words  # Exclude known words
            }

            filtered_words = {
                word: valid_words[word]
                for word in web_words
                if word in valid_words and valid_words[word] > int(user_level)
            }

            return filtered_words

        except Exception as e:
            return {"error": str(e)}


    def get_user_word_bank(self, user_id):
        try:
            user_word_bank = self.word_bank_ref.order_by_child("users_id").equal_to(user_id).get()

            if not user_word_bank:
                return {"error": "No words found in the user's word bank."}

            user_word_ids = set()
            for word_bank_entry in user_word_bank.values():
                words = word_bank_entry.get('words_id', [])
                if isinstance(words, list):
                    user_word_ids.update(words)
                else:
                    user_word_ids.add(words)

            all_words_data = self.words_ref.get()
            if not all_words_data:
                return {"error": "No word data found in the database."}

            known_words = [
                word_data['name']
                for word_id, word_data in all_words_data.items()
                if word_id in user_word_ids
            ]

            return known_words

        except Exception as e:
            print(f"Error retrieving user's known words: {e}")
            return {"error": str(e)}



    def add_word_to_bank(self, user_id, word_id):
        try:
            # Query the database for the user's word bank
            word_bank_query = self.word_bank_ref.order_by_child("users_id").equal_to(user_id).get()

            if word_bank_query:
                # Loop through the results to update the correct word bank
                for doc_id, doc_data in word_bank_query.items():
                    word_bank_ref = self.word_bank_ref.child(doc_id)
                    words_id = doc_data.get('words_id', [])

                    # Check if 'words_id' is not a list, initialize it to an empty list
                    if not isinstance(words_id, list):
                        words_id = []

                    # Add word_id to the list if it's not already there
                    if word_id not in words_id:
                        words_id.append(word_id)
                        word_bank_ref.update({
                            "words_id": words_id
                        })
                    else:
                        return "Word already exists in user's word bank."
                return "Word added successfully!"
            else:
                return "User's word bank not found."
        except Exception as e:
            print(f"Error adding word: {e}")
            return "Failed to add word."

    def remove_word_from_bank(self, user_id, word_id):
        try:
            word_bank_query = self.word_bank_ref.order_by_child("users_id").equal_to(user_id).get()

            if not word_bank_query:
                return {"error": "User's word bank not found."}

            for doc_id, doc_data in word_bank_query.items():
                word_bank_ref = self.word_bank_ref.child(doc_id)
                words_id = doc_data.get('words_id', [])

                if not isinstance(words_id, list):
                    words_id = []

                if word_id in words_id:
                    words_id.remove(word_id)
                    word_bank_ref.update({"words_id": words_id})
                    print(f"After removal: {words_id}")
                    return {"message": "Word removed successfully."}
                else:
                    return {"error": "Word not found in user's word bank."}

            return {"error": "User's word bank not found."}

        except Exception as e:
            return {"error": f"Failed to remove word. Error: {str(e)}"}




    def check_word_id(self, word):
        try:
            # Query the database for the word
            result = self.words_ref.order_by_child("name").equal_to(word).get()

            # Check if any results are returned
            if result:
                # Since you expect only one result, get the first (and only) key
                word_id = next(iter(result.keys()))  # Extract the key (ID)
                return word_id
            else:
                return False
        except Exception as e:
            print(f"Error checking word: {e}")
            return False
