<h1 align="center">Namishu Arithmetic</h1>

<p align="center">Printable arithmetic worksheets for integers, fractions, and decimals.</p>

<p align="center">
  <a href="pyproject.toml"><img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&amp;logo=python&amp;logoColor=white" alt="Python 3.10+"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-22A06B?style=flat" alt="License: MIT"></a>
  <a href="examples/addition.pdf"><img src="https://img.shields.io/badge/PDF-A4-E05D44?style=flat" alt="PDF: A4"></a>
</p>

<p align="center"><strong>English</strong> · <a href="README.zh-CN.md">简体中文</a></p>

<p align="center">
  <a href="#quick-start">Quick start</a> · <a href="docs/levels.md">Level catalog</a> ·
  <a href="#other-commands">Commands</a> · <a href="docs/agent-guide.md">Agent guide</a>
</p>

---

Namishu Arithmetic creates printable arithmetic worksheets for parents preparing daily practice,
teachers assigning classwork, and learners practicing specific operations. Choose an exercise type
and page count to get an A4 PDF ready to print, saving the time spent writing questions and arranging
them on a page. Run it again whenever you need a fresh set of questions.

With **68 levels across 3 series**, the project covers addition, subtraction, multiplication, and division
with integers, fractions, and decimals, including negative numbers, parentheses, mixed operations,
and missing-number exercises. Choose a preset for your practice goal, adjust the layout and number of
problems per page, or fix the random seed to generate the same set of questions again.

<p align="center">
  Sample PDFs: <a href="examples/addition.pdf">Addition</a> · <a href="examples/multiplication.pdf">Multiplication</a> ·
  <a href="examples/fractions.pdf">Fractions</a> · <a href="examples/decimals.pdf">Decimals</a>
</p>

## Installation

Requirements: **Python 3.10+ and uv**.

```bash
git clone https://github.com/namishu/arithmetic.git
cd arithmetic
uv sync
```

Run the commands below from the project directory.

## Quick start

Choose a series and level to generate a worksheet:

| Series (`--series`) | Levels (`--level`) | Content |
|---|---|---|
| `addsub` | 1–24 | Integer addition, subtraction, negative numbers, missing numbers |
| `muldiv` | 1–26 | Integer multiplication/division, parentheses, mixed operations, missing numbers |
| `fraction` | 1–18 | Fractions, decimals, and mixed numeric types |

Each level identifies an exercise preset, described in the [level catalog](docs/levels.md).
For example, `addsub` level 1 adds two integers from 0 to 10; sums may reach 20.

### Generate a PDF

Generate **five pages of addition practice**, saved to `worksheets/addition.pdf`:

```bash
uv run arithmetic generate --series addsub --level 1 --pages 5 --output worksheets/addition.pdf
```

`generate` creates a PDF. The four arguments above specify:

| Argument | Meaning | Required? |
|---|---|---|
| `--series addsub` | Select the addition/subtraction series | Required |
| `--level 1` | Select level 1 within that series | Required |
| `--pages 5` | Generate five pages | Optional; default: 10 pages |
| `--output worksheets/addition.pdf` | Set the PDF file location | Optional; default: `worksheets/{series}/level-{level}.pdf` |

The command prints the file location when complete. Open the PDF and print at actual size on A4 paper.

You can also add these options:

| Option | Purpose |
|---|---|
| `--seed 42` | Reproduce problem content with the same program and dependency versions; omitted seeds are randomly chosen and printed |
| `--disallow-zero-denominator` | Exclude expressions with a zero denominator or divisor; allowed by default |
| `--config examples/override.yaml` | Load layout and problems-per-page settings from a YAML file |
| `--force` | Replace an existing file; existing files cause an error by default |
| `--json` | Return file locations, page counts, exercises, seeds, and other generation details as JSON for programs or agents |

For example, generate **two pages of division practice with no division by zero and a fixed seed**:

```bash
uv run arithmetic generate --series muldiv --level 5 --pages 2 --seed 42 --disallow-zero-denominator --output worksheets/division.pdf
```

You can also give the repository URL or local folder to an agent that can run commands, with a request:

> Use this project to generate five pages of basic multiplication practice without negative operands,
> saved in worksheets/. Verify the PDF and provide a file link and the generation settings.

## Other commands

### List exercises: `list`

Show every series, level, and exercise name. Use `--series` to filter by series, or `--json` for JSON output.

```bash
uv run arithmetic list
uv run arithmetic list --series muldiv
```

### Inspect a level: `describe`

Show operand ranges, operation rules, examples, and problems per page for one level.
Both `--series` and `--level` are required; `--json` returns JSON output.

```bash
uv run arithmetic describe --series muldiv --level 5
```

### Generate a complete collection: `generate --all`

Create a separate PDF for each of the 68 levels. This command generates one page per level:

```bash
uv run arithmetic generate --all --pages 1 --output-dir worksheets/collection
```

`--all` selects every exercise; `--output-dir` sets the root directory, defaulting to `worksheets`.
Files are stored as `{series}/level-{level}.pdf`.
Batch generation accepts `--pages`, `--seed`, `--disallow-zero-denominator`, `--config`, `--force`, and `--json`.
It cannot be combined with `--series`, `--level`, or `--output`. `--output-dir` is only available with `--all`.

### Help and version

```bash
uv run arithmetic --help
uv run arithmetic generate --help
uv run arithmetic --version
```

`list` and `describe` also accept `--help`.

## Default configuration

| Setting | Default |
|---|---|
| Pages | 10 per PDF |
| Problems per page | Integer series: 10; fraction series: 14, with 12 fixed for levels 8, 9, 17, and 18 |
| Paper | A4 |
| Output path | `worksheets/{series}/level-{level}.pdf` |
| Zero denominators/divisors | Allowed |
| Output language | English |

Series and level must be selected explicitly. Each blank always requires a unique valid rational solution.
Save an override as `worksheet.yaml` to adjust problems per page, margins (in millimeters), and line spacing.
Only supplied settings change; other settings keep their defaults.

```yaml
problems_per_page:
  default: 12
layout:
  margin:
    left_mm: 20
    right_mm: 20
  typography:
    line_spacing_ratio: 1.0
```

```bash
uv run arithmetic generate --series addsub --level 1 --config worksheet.yaml
```

`default` sets the integer series capacity; use `fraction` alongside it to set the fraction series capacity.
The four levels with a fixed 12-question capacity retain that value.
See [examples/override.yaml](examples/override.yaml) for a ready-to-use file.

## License

Code and original documentation use the [MIT License](LICENSE).
Generated worksheets may be printed, shared, modified, and sold. Third-party assets follow their own license terms.
