import requests
import json
import os

BASE = "http://127.0.0.1:8000"

print('health ->', requests.get(f"{BASE}/api/health").text)

# create temp resume
content = "John Doe\nExperience: Python, FastAPI, PyTorch\nSkills: Machine Learning, NLP\n"
fn = 'temp_resume.txt'
with open(fn, 'w', encoding='utf-8') as f:
    f.write(content)

with open(fn, 'rb') as fh:
    files = {'file': fh}
    res = requests.post(f"{BASE}/api/resume/upload", files=files, data={'name':'John Doe','email':'john@example.com'})
print('upload status', res.status_code)
print(res.text)
if res.status_code != 200:
    raise SystemExit('upload failed')

cid = res.json().get('candidate_id')
print('candidate id', cid)

# create interview
payload = {'candidate_id': cid, 'selected_role': 'AI/ML Engineer'}
res = requests.post(f"{BASE}/api/interviews", json=payload)
print('create interview', res.status_code)
print(res.text)
if res.status_code != 200:
    raise SystemExit('create interview failed')

sid = res.json().get('session_id') or res.json().get('id')
print('session id', sid)

# loop through up to 5 questions
for i in range(5):
    res = requests.get(f"{BASE}/api/interviews/{sid}/current-question")
    print('current question', res.status_code)
    print(res.text)
    if res.status_code != 200:
        break
    q = res.json()
    qid = q.get('question_id') or q.get('id')
    ans = 'This is a short test answer demonstrating ML and evaluation experience.'
    res = requests.post(f"{BASE}/api/interviews/{sid}/answer", json={'question_id': qid, 'answer_text': ans})
    print('submit answer', res.status_code)
    print(res.text)
    res = requests.post(f"{BASE}/api/interviews/{sid}/next")
    print('next', res.status_code)
    print(res.text)

# complete
res = requests.post(f"{BASE}/api/interviews/{sid}/complete")
print('complete', res.status_code)
print(res.text)
res = requests.get(f"{BASE}/api/interviews/{sid}/report")
print('report', res.status_code)
try:
    print(json.dumps(res.json(), indent=2, default=str))
except Exception:
    print(res.text)

os.remove(fn)
