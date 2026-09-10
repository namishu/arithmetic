"""Build verification: install a wheel in an isolated environment, outside the source tree."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    wheel = max((ROOT / "dist").glob("*.whl"), key=lambda p: p.stat().st_mtime)
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        for asset in ["main.yaml", "catalog.json"]:
            assert f"namishu_arithmetic/data/{asset}" in names, asset
        assert not any(name.lower().endswith((".ttf", ".otf", ".ttc", ".pfb", "/ofl.txt")) for name in names)
        assert any(name.endswith("/licenses/LICENSE") for name in names)
    with tempfile.TemporaryDirectory(prefix="arithmetic-wheel-") as directory:
        folder = Path(directory)
        env_dir = folder / "env"
        subprocess.run(["uv", "venv", "--python", sys.executable, str(env_dir)], check=True)
        python = env_dir / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        subprocess.run(["uv", "pip", "install", "--python", str(python), str(wheel)], check=True)
        env = os.environ.copy()
        env.pop("PYTHONPATH", None)
        result = subprocess.run(
            [
                str(python),
                "-m",
                "namishu_arithmetic",
                "generate",
                "--series",
                "fraction",
                "--level",
                "10",
                "--pages",
                "2",
                "--seed",
                "42",
                "--output",
                "installed.pdf",
                "--json",
            ],
            cwd=folder,
            env=env,
            capture_output=True,
            text=True,
            check=True,
        )
        manifest = json.loads(result.stdout)
        from pypdf import PdfReader

        assert len(PdfReader(manifest["files"][0]["output"]).pages) == 2
        print(
            "Wheel installed independently; packaged config, catalog, and two-page PDF verified without bundled fonts."
        )


if __name__ == "__main__":
    main()
