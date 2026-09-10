import subprocess
import sys
from pathlib import Path


def run_project_python(project, code, *, expect=None, check=True):
    proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    combined = proc.stdout + proc.stderr
    assert (proc.returncode == 0) == check, combined
    for token in expect or []:
        assert token in combined, combined
    return proc


def assert_pdf_created(path: Path):
    from pypdf import PdfReader

    assert path.stat().st_size > 1000
    assert len(PdfReader(path).pages) >= 1
