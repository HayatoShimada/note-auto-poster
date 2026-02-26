import os
import requests
from note_api import NoteAPIClient
from dotenv import load_dotenv

load_dotenv('.env.local')
client = NoteAPIClient(cookies=os.environ.get('NOTE_COOKIES'))

# URL for getting draft in v3 or v2 text_notes
# Let's try downloading the edit page or using API
url = 'https://note.com/api/v3/notes/148605175'
res = client._request('GET', url)
if res:
    print(res.get('data', {}).get('body'))
