import os
import gradio as gr
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from google import genai  # Gemini SDK

# -----------------------------
# ENVIRONMENT VARIABLES (Hugging Face Secrets)
# -----------------------------
MONGO_URI = os.getenv("MONGO_URI")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not MONGO_URI or not GOOGLE_API_KEY:
    raise Exception("Please set MONGO_URI and GOOGLE_API_KEY as Secrets!")

# -----------------------------
# GENERATIVE API SETUP
# -----------------------------
MODEL = "gemini-2.5-flash"
client_gemini = genai.Client(api_key=GOOGLE_API_KEY)

# -----------------------------
# MONGODB SETUP
# -----------------------------
client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
db = client["personal_memory"]
users_collection = db["users"]

try:
    client.admin.command("ping")
    print("✅ MongoDB connected.")
except Exception as e:
    print("❌ MongoDB connection failed:", e)
    raise e

# -----------------------------
# MEMORY FUNCTIONS
# -----------------------------
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

# -----------------------------
# GENERATIVE API CALL
# -----------------------------
def generate_text_with_api(prompt):
    try:
        response = client_gemini.models.generate_content(
            model=MODEL,
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"API Error: {e}"

# -----------------------------
# CHAT FUNCTION
# -----------------------------
def chat(username, query):
    memory_list = get_user_memory(username)
    memory_text = "\n".join(memory_list) if memory_list else "No memory yet."
    
    prompt = f"""
You are a helpful assistant.
The user's name is {username}.

Here is what you remember about the user:
{memory_text}

The user just said:
{query}

Based on this information, provide a helpful and relevant response. If the user stated a new fact, acknowledge it.
"""
    answer = generate_text_with_api(prompt)

    new_fact_keywords = ["i love", "my", "i am", "i like", "i have", "my name is"]
    if any(query.lower().strip().startswith(k) for k in new_fact_keywords):
        update_user_memory(username, query)

    return answer

# -----------------------------
# GRADIO INTERFACE
# -----------------------------
iface = gr.Interface(
    fn=chat,
    inputs=[gr.Textbox(label="Username"), gr.Textbox(label="Your Message")],
    outputs="text",
    title="🧠 Personal Memory Chatbot",
    description="A chatbot that remembers what you tell it using MongoDB and answers via Google Gemini 2.5 API."
)

iface.launch()
