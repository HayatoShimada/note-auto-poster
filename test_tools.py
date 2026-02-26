from google import genai
import os

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='今日 東京 天気',
    config={
        "tools": [{"google_search": {}}],
    },
)

print(response.text)
