import io
import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def make_pdf_bytes(text: str) -> bytes:
    try:
        import fitz
    except Exception:
        pytest.skip("PyMuPDF not available")
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    return doc.write()


def test_upload_txt_resume():
    data = {
        "name": "Alice",
        "email": "alice@example.com",
    }
    files = {
        "file": (
            "resume.txt",
            io.BytesIO(b"Alice\nSkills: Python, SQL"),
            "text/plain",
        )
    }
    resp = client.post("/api/resume/upload", files=files, data=data)
    assert resp.status_code == 200
    body = resp.json()
    assert "candidate_id" in body
    rt = body.get("resume_text") or ""
    assert "python" in rt.lower()


def test_upload_pdf_resume():
    pdf = make_pdf_bytes("Bob\nSkills: Java, Docker")
    files = {"file": ("resume.pdf", io.BytesIO(pdf), "application/pdf")}
    resp = client.post("/api/resume/upload", files=files)
    assert resp.status_code == 200
    body = resp.json()
    assert body["skills"] or body["technologies"]


def test_empty_pdf():
    # create an empty PDF
    try:
        import fitz
    except Exception:
        pytest.skip("PyMuPDF not available")
    d = fitz.open()
    files = {"file": ("empty.pdf", io.BytesIO(d.write()), "application/pdf")}
    resp = client.post("/api/resume/upload", files=files)
    assert resp.status_code == 400


def test_invalid_file_type():
    files = {
        "file": (
            "script.exe",
            io.BytesIO(b"MZ..."),
            "application/octet-stream",
        )
    }
    resp = client.post("/api/resume/upload", files=files)
    assert resp.status_code == 400
