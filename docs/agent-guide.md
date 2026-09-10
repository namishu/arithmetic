# Agent operation guide

This guide is for agents helping users generate worksheet PDFs. For installation,
read [README.md](../README.md). For available exercises, use the [level catalog](levels.md).

## 1. Prepare

You need shell execution, Python 3.10+, dependency installation, and access to
output files. Inspect the existing environment first. From the repository root,
use `uv sync` and prefix commands with `uv run`, or follow the README's virtual
environment instructions. Run `arithmetic --help` to verify installation.
Never claim completion if execution or file delivery is unavailable.

The command examples below assume the environment is active. When using uv,
prefix them with `uv run`.

## 2. Understand and select

Use `arithmetic list --json`, then `arithmetic describe --series CODE --level N --json`.
The JSON includes bilingual goals and source ranges, numeric types, allowed
operations, possible negative operands, blanks, grouping, actual examples, and
page capacity. Use these facts, not level numbers alone.

| Request | Candidate | Constraint |
|---|---|---|
| Basic addition | `addsub 1` | Operands 0–10; sums up to 20 |
| Nonnegative subtraction | `addsub 2` | Minuend may reach 20 |
| Nonnegative basic multiplication | `muldiv 1` | Factors 0–9, including zero |
| Nonnegative exact division | `muldiv 5` | Normal mode excludes zero divisors |
| Fraction addition/subtraction | `fraction 1` | Operands nonnegative; answers may be negative |
| Decimal addition/subtraction | `fraction 10` | Signed one-place decimals |
| Decimal multiplication | `fraction 13` | Signed one-place decimals |

Clarify only material ambiguities. “Addition within 10” could mean operands or sums.
“Without negatives” could constrain operands, answers, or both. “20 questions” is
not “20 pages”; calculate capacity, using a config override if appropriate. Four
fraction levels have fixed 12-question capacity. Do not silently substitute a
nearby preset for an unsupported strict constraint. Explain the mismatch and ask
whether a supported alternative is acceptable. School grade alone is insufficient
to promise curriculum alignment.

## 3. Generate

For example, a request for five pages of nonnegative basic multiplication:

```bash
arithmetic describe --series muldiv --level 1 --json
arithmetic generate --series muldiv --level 1 --pages 5 --output worksheets/multiplication.pdf --json
```

The success manifest contains absolute output paths, actual page capacity, seed,
and mode. Keep the seed for reproducing problem content. If a filename exists,
choose a new one unless replacement was requested. `--all` creates 68 files and
should only be used when a complete collection is requested.

Omit `--allow-undefined` for ordinary practice. Enable it only when the user
requests undefined-expression recognition exercises. It does not guarantee such
an expression on every page and never permits blanks without a unique solution.

## 4. Verify and deliver

At minimum verify a nonempty PDF exists. If a PDF reader is available, check that
it opens and has the requested page count; inspect or render a page when possible.
If `pypdf` is available, for example:

```python
from pypdf import PdfReader

reader = PdfReader("worksheets/multiplication.pdf")
assert len(reader.pages) == 5
assert "Multiplication" in reader.pages[0].extract_text()
```

Return the file/link, series and level, page count, questions/page, seed, and any
material mismatch or unverified check. Do not imply answer sheets exist. Use the
installed program for normal generation requests; change source only if requested.

## 5. Recover

- Missing command: verify the virtual environment or use `python -m namishu_arithmetic`.
- Missing dependency: install this project in that same environment.
- Invalid level: query `list` and `describe`; do not guess a new number.
- Existing file: choose another output name, or use `--force` when replacement is intended.
- Custom font failure: inspect the config-relative path, or remove the override to use standard Helvetica.
- Unsupported request: explain the specific constraint and propose a documented preset.

See [usage](usage.md) for configuration and [the catalog](levels.md) for all 68 presets.
Markdown and CLI metadata are enough; no agent-specific plugin is required.
