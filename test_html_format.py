import requests
import json
import os
from note_api import NoteAPIClient

client = NoteAPIClient(cookies=os.environ.get('NOTE_COOKIES', 'a7bf958ba112c79233dae8283944dc82'))

test_body = """<p>これは段落です。</p>
<h2>これは見出し2です</h2>
<p>改行テスト<br>改行テスト</p>
<h3>これは見出し3です</h3>
<ul><li>リスト1</li><li>リスト2</li></ul>
"""

print("Creating note with various HTML tags...")
id, key = client.create_article('HTML Format Test', test_body)
print('Created:', id)

if id:
    url = f'https://note.com/api/v1/text_notes/draft_save?id={id}'
    headers = {'Content-Type': 'application/json'}
    data = {
        'name': 'HTML Format Test 2',
        'body': test_body,
    }
    r = client._request('POST', url, headers=headers, json=data)
    print('Draft save returned:', r)
