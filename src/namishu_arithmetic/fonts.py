from __future__ import annotations

from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def register_configured_font(font_config: dict, *, base_dir: str | Path) -> str:
    """Use a PDF standard font, or an explicitly supplied local TrueType file."""
    name = str(font_config.get("name") or "Helvetica")
    raw_path = font_config.get("path")
    if not raw_path:
        if name not in pdfmetrics.standardFonts:
            raise ValueError(f"Unknown standard font: {name}; use Helvetica, Times-Roman, Courier, or set font_path")
        return name
    if name in pdfmetrics.standardFonts:
        raise ValueError("Custom font_name must differ from PDF standard font names")
    path = Path(base_dir) / raw_path
    try:
        pdfmetrics.registerFont(TTFont(name, str(path)))
    except Exception as exc:
        raise ValueError(f"Font load failed ({name}): {exc}") from exc
    return name
