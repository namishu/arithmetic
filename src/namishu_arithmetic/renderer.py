from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from .fonts import register_configured_font
from .pdf import create_canvas


@dataclass(frozen=True)
class HeaderInfo:
    series_label: str
    level_label: str
    generated_on: str

    @property
    def left_text(self) -> str:
        return f"{self.series_label} · {self.level_label}"

    @property
    def right_text(self) -> str:
        return f"Namishu · {self.generated_on}"


class WorksheetRenderer:
    def __init__(
        self,
        layout_config: dict,
        series_label: str,
        level_label: str,
        generated_on: str,
        project_dir: str | Path,
        teaching_mode: bool = False,
    ):
        self.teaching_mode = teaching_mode
        self.cfg = layout_config
        self.header = HeaderInfo(series_label=series_label, level_label=level_label, generated_on=generated_on)
        self.project_dir = Path(project_dir)
        self.font_name = self._register_font()
        self._validate_layout()

    def render(self, pages: list[list[str]], output_path: str | Path) -> Path:
        output = Path(output_path)
        page_cfg = self.cfg["page"]
        width_pt = page_cfg["width_mm"] * mm
        height_pt = page_cfg["height_mm"] * mm
        pdf = create_canvas(
            output,
            width_mm=page_cfg["width_mm"],
            height_mm=page_cfg["height_mm"],
            title=f"{self.header.series_label} {self.header.level_label}",
        )

        for page_index, problems in enumerate(pages, start=1):
            pdf.setFillColor("#FFFFFF")
            pdf.rect(0, 0, width_pt, height_pt, stroke=0, fill=1)
            self._draw_header(pdf, width_pt, height_pt)
            self._draw_content(pdf, problems, height_pt)
            self._draw_footer(pdf, width_pt, page_index)
            pdf.showPage()

        pdf.save()
        return output

    def _draw_content(self, pdf: canvas.Canvas, problems: list[str], page_height_pt: float) -> None:
        margin = self.cfg["margin"]
        typography = self.cfg["typography"]

        n = len(problems)
        if n == 0:
            return

        ratio = float(typography["line_spacing_ratio"])
        content_height_pt = page_height_pt - (margin["top_mm"] + margin["bottom_mm"]) * mm
        content_top_y = page_height_pt - margin["top_mm"] * mm
        content_left_x = margin["left_mm"] * mm

        denominator = n + ratio * (n - 1)
        text_height = content_height_pt / denominator if denominator > 0 else 12.0
        font_size = text_height
        line_gap = text_height * ratio

        pdf.setFont(self.font_name, font_size)
        pdf.setFillColor(typography.get("text_color", "#111111"))

        y = content_top_y - text_height
        for problem in problems:
            width = (self.cfg["page"]["width_mm"] - margin["left_mm"] - margin["right_mm"]) * mm
            measured = pdf.stringWidth(problem, self.font_name, font_size)
            pdf.setFont(self.font_name, min(font_size, font_size * width / measured) if measured else font_size)
            pdf.drawString(content_left_x, y, problem)
            y -= text_height + line_gap

        pdf.setFillColor("#000000")

    def _draw_header(self, pdf: canvas.Canvas, page_width_pt: float, page_height_pt: float) -> None:
        margin = self.cfg["margin"]
        header = self.cfg["header"]
        typography = self.cfg["typography"]

        left_x = margin["left_mm"] * mm
        right_x = page_width_pt - margin["right_mm"] * mm
        font_size = header["font_size_pt"]
        left_text = self.header.left_text
        right_text = self.header.right_text
        line_y = page_height_pt - margin["top_mm"] * mm + header["separator_offset_y_mm"] * mm
        text_y = line_y + header["offset_y_mm"] * mm

        pdf.setLineWidth(float(header["separator_width_pt"]))
        pdf.setStrokeColor(typography.get("meta_text_color", "#444444"))
        pdf.line(left_x, line_y, right_x, line_y)

        pdf.setFont(self.font_name, font_size)
        pdf.setFillColor(typography.get("meta_text_color", "#444444"))
        pdf.drawString(left_x, text_y, left_text)

        right_width = pdf.stringWidth(right_text, self.font_name, font_size)
        pdf.drawString(right_x - right_width, text_y, right_text)
        pdf.setStrokeColor("#000000")
        pdf.setFillColor("#000000")

    def _draw_footer(self, pdf: canvas.Canvas, page_width_pt: float, page_num: int) -> None:
        footer = self.cfg["footer"]
        typography = self.cfg["typography"]
        y = footer["offset_y_mm"] * mm
        text = ("Identify undefined expressions | " if self.teaching_mode else "") + str(page_num)
        font_size = footer["font_size_pt"]

        pdf.setFont(self.font_name, font_size)
        pdf.setFillColor(typography.get("meta_text_color", "#444444"))
        text_width = pdf.stringWidth(text, self.font_name, font_size)
        pdf.drawString((page_width_pt - text_width) / 2, y, text)
        pdf.setFillColor("#000000")

    def _register_font(self) -> str:
        typography = self.cfg["typography"]
        return register_configured_font(
            {"name": typography["font_name"], "path": typography.get("font_path")},
            base_dir=self.project_dir,
        )

    def _validate_layout(self) -> None:
        page = self.cfg["page"]
        margin = self.cfg["margin"]
        if margin["left_mm"] + margin["right_mm"] >= page["width_mm"]:
            raise ValueError("layout invalid: left+right margins must be less than page width")
        if margin["top_mm"] + margin["bottom_mm"] >= page["height_mm"]:
            raise ValueError("layout invalid: top+bottom margins must be less than page height")
