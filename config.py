import os

MONGO_URI = os.getenv("MONGO_URI")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not MONGO_URI or not GOOGLE_API_KEY:
    raise Exception("Please set MONGO_URI and GOOGLE_API_KEY as environment variables!")

MODEL = "gemini-2.5-flash"
