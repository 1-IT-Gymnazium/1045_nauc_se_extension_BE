import firebase_admin
from firebase_admin import credentials, db
import bcrypt
import os

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

    def loginUser(self, name, password):
        try:
            res = self.user_ref.order_by_child("username").equal_to(name).get()
            if res:
                for user_id, user_data in res.items():
                    hash_pass = user_data.get("password")
                    if bcrypt.checkpw(password.encode(), hash_pass.encode()):
                        return True
                    else:
                        return False
            else:
                return False
        except Exception as e:
            return e

    def signupUser(self, name, email, password):
        try:
            existing_user = self.user_ref.order_by_child("email").equal_to(email).get()
            if existing_user:

                return False

            hash_pass = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

            users = self.user_ref.get()
            max_id = 0
            if users:
                for user_id, user_data in users.items():
                    try:
                        user_id_int = int(user_id)
                        if user_id_int > max_id:
                            max_id = user_id_int
                    except ValueError:
                        continue

            new_id = max_id + 1

            new_user_ref = self.user_ref.child(str(new_id)).set(
            {
                "name": name,
                "email": email,
                "password": hash_pass.decode("utf-8"),
                "level_id": 4
            })

            return True
        except Exception as e:
            return False
