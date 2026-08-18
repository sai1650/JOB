import re
# uuid not currently used
from typing import List, Dict, Optional

try:
    import fitz  # PyMuPDF
except Exception:
    fitz = None

try:
    from pypdf import PdfReader
except Exception:
    PdfReader = None


class ResumeParser:
    def __init__(self, file_bytes: bytes, filename: str):
        self.file_bytes = file_bytes
        self.filename = filename.lower()
        self._text: Optional[str] = None

    def extract_text(self) -> str:
        if self._text is not None:
            return self._text

        if self.filename.endswith(".pdf"):
            text = self._extract_pdf_text()
        else:
            # treat as text
            try:
                text = self.file_bytes.decode("utf-8")
            except Exception:
                text = self.file_bytes.decode("latin-1", errors="ignore")

        self._text = text
        return text

    def _extract_pdf_text(self) -> str:
        if fitz:
            try:
                doc = fitz.open(stream=self.file_bytes, filetype="pdf")
                parts: List[str] = []
                for page in doc:
                    parts.append(page.get_text())
                text = "\n".join(parts)
                if text and text.strip():
                    return text
            except Exception:
                # fallback to pypdf before failing
                pass

        if PdfReader:
            try:
                reader = PdfReader(self.file_bytes)
                parts = []
                for page in reader.pages:
                    parts.append(page.extract_text() or "")
                text = "\n".join(parts)
                if text and text.strip():
                    return text
            except Exception:
                pass

        if not fitz and not PdfReader:
            raise RuntimeError(
                "No PDF parser available. "
                "Install PyMuPDF or pypdf, or upload TXT."
            )

        raise RuntimeError(
            "Unable to extract text from PDF. "
            "The file may be image-only or corrupted."
        )

    def clean_text(self, text: Optional[str] = None) -> str:
        if text is None:
            text = self.extract_text()
        # remove form feeds, normalize newlines and whitespace
        t = text.replace("\x0c", "\n")
        t = re.sub(r"[\r\t]+", " ", t)
        t = re.sub(r"\n{2,}", "\n\n", t)
        t = re.sub(r"[ ]{2,}", " ", t)
        # remove common extraction artifacts
        t = re.sub(r"\.{3,}", ".", t)
        t = t.strip()
        return t

    def extract_sections(self, text: Optional[str] = None) -> Dict[str, str]:
        if text is None:
            text = self.clean_text()
        lines = text.splitlines()
        sections: Dict[str, List[str]] = {}
        current = "overview"
        sections[current] = []
        for ln in lines:
            # detect headings (all caps or ends with ':' or common keywords)
            if re.match(r"^[A-Z \-]{3,}$", ln.strip()):
                current = ln.strip().lower()
                sections.setdefault(current, [])
                continue
            if ln.strip().endswith(":") and len(ln.strip()) < 40:
                current = ln.strip().rstrip(":").lower()
                sections.setdefault(current, [])
                continue
            sections.setdefault(current, []).append(ln)

        return {k: "\n".join(v).strip() for k, v in sections.items() if v}

    def extract_skills(self, text: Optional[str] = None) -> List[str]:
        if text is None:
            text = self.clean_text()
        # naive keyword+pattern matching with small seed list
        seed = [
            "python",
            "java",
            "sql",
            "javascript",
            "react",
            "docker",
            "kubernetes",
            "aws",
            "git",
        ]
        found = set()
        tl = text.lower()
        for s in seed:
            if re.search(r"\b" + re.escape(s) + r"\b", tl):
                found.add(s)

        # also capture capitalized token lists after 'Skills' heading
        sections = self.extract_sections(text)
        skills_block = ''
        for k in sections:
            if 'skill' in k:
                skills_block = sections[k]
                break
        if skills_block:
            tokens = re.split(r"[\n,;•\t]+", skills_block)
            for tok in tokens:
                tok = tok.strip()
                if len(tok) > 1 and len(tok) < 40:
                    found.add(tok.lower())

        return sorted(found)

    def extract_technologies(self, text: Optional[str] = None) -> List[str]:
        # overlap with skills but prefer tech nouns
        skills = self.extract_skills(text)
        techs = [s for s in skills if s not in ('git',)]
        return techs

    def extract_domains(self, text: Optional[str] = None) -> List[str]:
        if text is None:
            text = self.clean_text()
        domain_seeds = [
            'finance',
            'health',
            'education',
            'e-commerce',
            'retail',
        ]
        found = [d for d in domain_seeds if d in text.lower()]
        return found
