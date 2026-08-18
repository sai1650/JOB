import re
import os
import uuid
from typing import Tuple


ALLOWED_EXT = (".pdf", ".txt")
MAX_UPLOAD_BYTES = 5 * 1024 * 1024


def secure_filename(filename: str) -> str:
    """Filesystem-safe filename with a uuid prefix."""
    name = os.path.basename(filename or "resume")
    # remove unsafe chars
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    # limit length
    if len(name) > 128:
        name = name[-128:]
    return f"{uuid.uuid4().hex[:8]}_{name}"


def allowed_file(filename: str) -> bool:
    if not filename:
        return False
    fn = filename.lower()
    return any(fn.endswith(e) for e in ALLOWED_EXT)


def validate_name_email(name: str, email: str) -> Tuple[str, str]:
    # basic name cleanup
    if not name:
        name = "Unknown"
    name = re.sub(r'[^A-Za-z0-9 \-\.\'\"]', '', name)[:100]

    # basic email validation
    if not email or not re.match(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        email = None

    return name, email
