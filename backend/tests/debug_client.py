from fastapi.testclient import TestClient
from app.main import app


def run():
    client = TestClient(app)
    files = {
        "file": (
            "resume.txt",
            b"Python\nGenerators\n",
            "text/plain",
        )
    }
    resp = client.post(
        "/api/resume/upload",
        data={"name": "X", "email": "x@example.com"},
        files=files,
    )
    print("upload status", resp.status_code, resp.text)
    if resp.status_code != 200:
        return
    cid = resp.json().get("candidate_id")
    print("candidate", cid)
    resp = client.post(
        "/api/interviews",
        json={"candidate_id": cid, "selected_role": "default"},
    )
    print("create interview", resp.status_code)
    print(resp.text)


if __name__ == "__main__":
    run()
