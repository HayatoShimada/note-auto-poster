import requests
import json
import os
from note_api import NoteAPIClient

client = NoteAPIClient(cookies=os.environ.get('NOTE_COOKIES', 'a7bf958ba112c79233dae8283944dc82'))

test_body = """<p>画像テスト</p>
<img src="https://images.unsplash.com/photo-1512436991641-6745cdb1723f" alt="fashion" />
"""

print("Creating note with img tag...")
id, key = client.create_article('Image Tag Test', test_body)
print('Created:', id)

if id:
    url = f'https://note.com/api/v1/text_notes/draft_save?id={id}'
    headers = {'Content-Type': 'application/json'}
    data = {
        'name': 'Image Tag Test',
        'body': test_body,
    }
    r = client._request('POST', url, headers=headers, json=data)
    print('Draft save returned:', r)
