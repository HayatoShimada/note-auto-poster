import os
from dotenv import load_dotenv
from llm_generator import ContentGenerator

load_dotenv('.env.local')

gemini_api_key = os.environ.get("GEMINI_API_KEY")
content_generator = ContentGenerator(api_key=gemini_api_key)

theme = "海外の古着屋スタッフやインフルエンサーを取り入れた着こなしアイデア"
instructions = "画像メインで"

title, md_content = content_generator.generate_article(theme, instructions)
print("TITLE:", title)
print("---")
print(md_content)
