import os
from note_api import NoteAPIClient

cookies = os.environ.get('NOTE_COOKIES', 'a7bf958ba112c79233dae8283944dc82')
client = NoteAPIClient(cookies=cookies)

# 1. Create Draft
print("1. Create draft...")
id, key = client.create_article('Test API Body Save', '<h1>Hello</h1><p>Test body initial</p>')
print('Created:', id, key)

if id:
    # 2. Try to save draft explicitly
    print("\n2. Execute draft_save...")
    url = f'https://note.com/api/v1/text_notes/draft_save?id={id}'
    headers = {'Content-Type': 'application/json'}
    data = {
        'name': 'Test API Body Save',
        'body': '<h1>Hello</h1><p>Test body modified via draft_save</p>',
    }
    r = client._request('POST', url, headers=headers, json=data)
    print('Draft save returned:', r)
