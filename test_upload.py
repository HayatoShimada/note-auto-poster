import os
import requests
import re
from note_api import NoteAPIClient
from dotenv import load_dotenv

load_dotenv('.env.local')

client = NoteAPIClient(cookies=os.environ.get('NOTE_COOKIES'))

image_url = "https://images.unsplash.com/photo-1512436991641-6745cdb1723f?w=800&q=80"
print(f"Downloading {image_url}...")
resp = requests.get(image_url)
with open('temp_test.jpg', 'wb') as f:
    f.write(resp.content)

print("Uploading to note...")
note_img_url = client.upload_image('temp_test.jpg')
print(f"Uploaded! URL: {note_img_url}")

if note_img_url:
    test_body = f"""<p>画像アップロードからのテスト</p>
<figure><img src="{note_img_url}" alt="fashion" /></figure>
<p>そのままのimgタグテスト</p>
<img src="{note_img_url}" alt="fashion" />
"""
    id, key = client.create_article('Upload Test', test_body)
    print("Created article", id)

