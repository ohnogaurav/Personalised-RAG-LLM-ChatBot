from google import genai
from config import GOOGLE_API_KEY, MODEL

client_gemini = genai.Client(api_key=GOOGLE_API_KEY)

def generate_text(prompt):
    try:
        response = client_gemini.models.generate_content(
            model=MODEL,
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"API Error: {e}"
