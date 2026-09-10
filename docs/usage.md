# Usage and configuration

[简体中文](usage.zh-CN.md)

For installation and a first worksheet, start with [README.md](../README.md).
Use the [level catalog](levels.md) to choose an exercise, or the
[agent guide](agent-guide.md) to delegate generation to an agent.

## Commands

`arithmetic --help` and each subcommand's `--help` list the available options.
`python -m namishu_arithmetic` is an equivalent entry point.

| Command | Options |
|---|---|
| `list` | `--series`, `--lang en/zh-CN`, `--json` |
| `describe` | required `--series`, required `--level`, `--lang`, `--json` |
| `generate` | `--series`, `--level`, `--pages`, `--seed`, `--output`, `--config`, `--allow-undefined`, `--force`, `--json` |
| `generate --all` | `--output-dir`, `--pages`, `--seed`, `--config`, `--allow-undefined`, `--force`, `--json` |

Single-file defaults: series `addsub`, level 1, 10 pages, output
`worksheets/{series}/level-{level}.pdf`. Batch mode generates all 68 levels and
cannot be combined with `--series`, `--level`, or `--output`.

```bash
arithmetic generate --all --pages 1 --seed 42 --output-dir worksheets/collection
```

A random seed is chosen when omitted and is reported in the output. Same seed and
settings reproduce problem content within the same program/dependency versions.
PDF generation dates and metadata can differ.

Normal mode excludes undefined expressions and blanks without a unique rational
solution. `--allow-undefined` permits undefined complete expressions and marks
the footer, without guaranteeing their frequency. Blanks must still have one valid
rational solution.

## Paths and output

CLI output and config paths are relative to the current working directory.
Custom font paths inside YAML are relative to that YAML file. Standard Helvetica
needs no font file, and default settings are included with the program. You can
run the installed program from any directory.

Existing outputs require `--force` to replace. Error messages go to stderr with
exit code 2; successful `--json` output is a single JSON object on stdout.
The generation manifest reports absolute file paths, page count, problems/page,
seed, series, level, and whether undefined expressions are allowed.

## Configuration

Save the following as `worksheet.yaml`. Only specified settings are changed;
other settings retain their defaults.

```yaml
problems_per_page:
  default: 12
  fraction: 14
layout:
  page:
    width_mm: 210
    height_mm: 297
  margin:
    left_mm: 20
    right_mm: 20
    top_mm: 25
    bottom_mm: 25
  typography:
    line_spacing_ratio: 1.0
```

```bash
arithmetic generate --series addsub --level 1 --pages 2 --config worksheet.yaml --output worksheets/addition.pdf
```

The `default` capacity applies to integer series. `fraction` has its own default
of 14; fraction levels 8, 9, 17, and 18 override this with 12. Dimensions use
millimeters, except fields named `*_pt`, which use points. Long lines shrink to
fit the content width. Layout settings do not change operand ranges.

Diversity settings (`candidate_multiplier`, `max_same_leading_operand_per_page`,
`max_special_operand_per_page`) influence question selection, not mathematical
difficulty. They are soft preferences, not guarantees of unique questions.

## Fonts

The default Helvetica font covers the current English headings, digits, and
arithmetic symbols. It does not provide Chinese glyphs. PDF readers may use
slightly different substitute fonts. No font installation or system font search
is needed. See [ReportLab font documentation](https://docs.reportlab.com/reportlab/userguide/ch3_fonts/).

To use another PDF standard font, add this to your YAML override:

```yaml
layout:
  typography:
    font_name: Times-Roman
    font_path: null
```

`Courier` is another option. To supply your own local TrueType font, set a custom
`font_name` distinct from PDF standard font names, and set `font_path` relative
to the YAML file. The font remains subject to its applicable license.

## Python API

```python
from namishu_arithmetic import ArithmeticApp

app = ArithmeticApp()
path = app.generate("fraction", 10, "worksheets/decimals.pdf", pages=2, seed=42)
problems = app.generate_pages("fraction", 10, pages=2, seed=42)
```

The Python API writes to the supplied path, replacing an existing file. CLI
replacement protection is a CLI feature. `generate_pages` returns `list[list[str]]`:
one list of question strings per page, without writing a PDF.
Use `ArithmeticApp(config_path="worksheet.yaml")` to apply an override.
`allow_undefined=True` enables teaching mode for either generation method.
Concurrent generation in multiple threads is not supported.

## Switching from the old command

If you previously used the generator inside printables-python, install this
independent project and replace `uv run pt arithmetic ...` with
`uv run arithmetic generate ...`. For a complete collection, use
`uv run arithmetic generate --all`.

The three series IDs and 68 level IDs are retained. Default output now goes to
`worksheets/{series}/level-{level}.pdf`; use `--output` to choose another location.
Old seeds may produce different questions because normal mode now excludes
undefined expressions and invalid blanks.

## Limitations and troubleshooting

- No arbitrary range selection, answer-sheet export, curriculum/grade mapping, or GUI.
- Fractions are inline, may be unreduced, and are treated as single operands.
- Missing-number solutions can be negative or fractional even with integer source values.
- Duplicate or similar questions can remain with limited candidate pools.
- If `arithmetic` is missing, activate the environment or use `python -m namishu_arithmetic`.
- If a custom font cannot load, correct the path or remove the font override.
- Windows users unable to activate PowerShell scripts can run `.venv\Scripts\python.exe -m pip install .`
  and `.venv\Scripts\python.exe -m namishu_arithmetic generate` directly.
- The CLI checks file creation. Open the PDF in a reader to check page count and layout.
