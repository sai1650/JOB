from fastapi.testclient import TestClient
from app.main import app
import io
client = TestClient(app)
files = {"file": ("resume.txt", io.BytesIO(b"Alice\nSkills: Python, SQL"), "text/plain")}
resp = client.post('/api/resume/upload', files=files, data={'name':'Alice','email':'alice@example.com'})
print('STATUS', resp.status_code)
print('TEXT', resp.text)
try:
    print('JSON:', resp.json())
except Exception as e:
    print('INVALID JSON:', e)
