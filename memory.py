from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from config import MONGO_URI

client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
db = client["personal_memory"]
users_collection = db["users"]

try:
    client.admin.command("ping")
    print("✅ MongoDB connected.")
except Exception as e:
    print("❌ MongoDB connection failed:", e)
    raise e

def get_user_memory(username):
    if not username.strip():
        return ["System Note: username is blank."]
    user = users_collection.find_one({"username": username})
    if user:
        return user.get("memory", [])
    else:
        users_collection.insert_one({"username": username, "memory": []})
        return []

def update_user_memory(username, new_fact):
    if not username.strip():
        return
    users_collection.update_one(
        {"username": username},
        {"$push": {"memory": new_fact}},
        upsert=True
    )
