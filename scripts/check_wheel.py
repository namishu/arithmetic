"""Verify an explicit wheel in an isolated installation outside the checkout."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import zipfile
from email.parser import Parser
from pathlib import Path

from pypdf import PdfReader


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def check_wheel(wheel: Path) -> None:
    require(wheel.is_file() and wheel.suffix == ".whl", f"Wheel does not exist: {wheel}")
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        for asset in ["default.yaml", "catalog.json"]:
            require(f"namishu_arithmetic/data/{asset}" in names, f"Missing packaged resource: {asset}")
        require(
            not any(name.lower().endswith((".ttf", ".otf", ".ttc", ".pfb", "/ofl.txt")) for name in names),
            "Unexpected bundled font or font license",
        )
        require(any(name.endswith("/licenses/LICENSE") for name in names), "Missing package license")
        metadata_paths = [name for name in names if name.endswith(".dist-info/METADATA")]
        require(len(metadata_paths) == 1, "Expected one distribution metadata file")
        metadata = Parser().parsestr(archive.read(metadata_paths[0]).decode("utf-8"))
        require(metadata["Name"] == "namishu-arithmetic", "Unexpected distribution name")
        require(bool(metadata["Version"]), "Missing distribution version")

    with tempfile.TemporaryDirectory(prefix="arithmetic-wheel-") as directory:
        folder = Path(directory).resolve()
        env_dir = folder / "env"
        subprocess.run(["uv", "venv", "--python", sys.executable, str(env_dir)], check=True, timeout=120)
        bin_dir = env_dir / ("Scripts" if os.name == "nt" else "bin")
        python = bin_dir / ("python.exe" if os.name == "nt" else "python")
        command = bin_dir / ("arithmetic.exe" if os.name == "nt" else "arithmetic")
        subprocess.run(["uv", "pip", "install", "--python", str(python), str(wheel)], check=True, timeout=300)
        env = os.environ.copy()
        for key in ["PYTHONPATH", "PYTHONHOME"]:
            env.pop(key, None)
        env["PYTHONNOUSERSITE"] = "1"

        def run_cli(*args: str) -> str:
            result = subprocess.run(
                [str(command), *args], cwd=folder, env=env, capture_output=True, text=True, timeout=60
            )
            require(result.returncode == 0, f"arithmetic {' '.join(args)} failed:\n{result.stdout}\n{result.stderr}")
            return result.stdout

        require(
            run_cli("--version").strip() == f"namishu-arithmetic {metadata['Version']}",
            "CLI version does not match wheel metadata",
        )
        catalog = json.loads(run_cli("list", "--json"))
        require(len(catalog["levels"]) == 68, "Expected 68 levels in installed catalog")
        description = json.loads(run_cli("describe", "--series", "fraction", "--level", "10", "--json"))
        require(description["operand_types"] == ["decimal"], "Unexpected decimal level description")
        require(bool(description["examples"]), "Installed catalog returned no examples")
        manifest = json.loads(
            run_cli(
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
            )
        )
        require(len(manifest["files"]) == 1, "Expected one generated PDF")
        record = manifest["files"][0]
        output = folder / "installed.pdf"
        require(Path(record["output"]).resolve() == output, "Unexpected PDF output path")
        require(record["pages"] == 2 and record["seed"] == 42, "Unexpected generation settings")
        require(output.is_file() and output.stat().st_size > 0, "Missing or empty PDF")
        reader = PdfReader(output)
        require(len(reader.pages) == 2, "Expected a two-page PDF")
        for page in reader.pages:
            content = page.extract_text()
            require("Level 10" in content and "=" in content, "Missing level label or exercises in PDF")
        print(f"Verified {wheel.name}: resources, license, CLI version, catalog, and two-page PDF (seed 42).")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wheel", type=Path, help="Exact path to the wheel to verify")
    args = parser.parse_args()
    try:
        check_wheel(args.wheel.resolve())
    except (ValueError, OSError, subprocess.SubprocessError, zipfile.BadZipFile) as exc:
        parser.exit(1, f"Wheel verification failed: {exc}\n")


if __name__ == "__main__":
    main()
