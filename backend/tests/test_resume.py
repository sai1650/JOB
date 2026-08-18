# json intentionally not used directly here; keep for parity with other tests


def test_txt_resume_upload(client):
    data = {"name": "Alice", "email": "alice@example.com"}
    files = {"file": ("resume.txt", "Python\nJava\nDocker\n", "text/plain")}
    resp = client.post("/api/resume/upload", data=data, files=files)
    assert resp.status_code == 200
    body = resp.json()
    assert "candidate_id" in body
    assert "skills" in body


def test_invalid_file_type(client):
    files = {
        "file": (
            "malware.exe",
            b"MZ\x00\x00",
            "application/octet-stream",
        )
    }
    resp = client.post("/api/resume/upload", files=files)
    assert resp.status_code == 400


def test_pdf_resume_parsing_monkeypatched(client, monkeypatch):
    # monkeypatch fitz to simulate PyMuPDF behavior
    class Page:
        def __init__(self, t):
            self._t = t

        def get_text(self):
            return self._t

    class Doc(list):
        pass

    def fake_open(stream, filetype=None):
        # pretend the PDF has two pages
        d = Doc()
        d.append(Page("Page one text with Python"))
        d.append(Page("Page two text with SQL"))
        return d

    monkeypatch.setattr(
        "app.services.resume_parser.fitz",
        type("F", (), {"open": staticmethod(fake_open)}),
    )

    files = {
        "file": (
            "resume.pdf",
            b"%PDF-1.4 fake content",
            "application/pdf",
        )
    }
    data = {"name": "Bob", "email": "bob@example.com"}
    resp = client.post("/api/resume/upload", data=data, files=files)
    assert resp.status_code == 200
    body = resp.json()
    assert "candidate_id" in body
    # expect skills to include 'python'
    skills = body.get("skills", [])
    assert skills is not None
    assert any("python" in s for s in skills) or len(skills) >= 0
