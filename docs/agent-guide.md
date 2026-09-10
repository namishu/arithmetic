# Agent operation guide

This guide is for agents helping users generate worksheet PDFs. For installation,
read [README.md](../README.md). For available exercises, use the [level catalog](levels.md).

## 1. Prepare

You need shell execution, uv, and access to output files. Use the published PyPI package:

```bash
uvx --from namishu-arithmetic==1.0.0 arithmetic --help
```

In the examples below, replace `arithmetic` with `uvx --from namishu-arithmetic==1.0.0 arithmetic`.
For an existing source checkout, use `uv sync` and prefix commands with `uv run` instead.
Never claim completion if execution or file delivery is unavailable.

## 2. Understand and select

Use `arithmetic list --json`, then `arithmetic describe --series CODE --level N --json`.
The JSON includes English goals and source ranges, numeric types, allowed
operations, possible negative operands, blanks, grouping, actual examples, and
page capacity. Use these facts, not level numbers alone.

| Request | Candidate | Constraint |
|---|---|---|
| Basic addition | `addsub 1` | Operands 0–10; sums up to 20 |
| Nonnegative subtraction | `addsub 2` | Minuend may reach 20 |
| Nonnegative basic multiplication | `muldiv 1` | Factors 0–9, including zero |
| Nonnegative exact division | `muldiv 5` | Use `--disallow-zero-denominator` to exclude zero divisors |
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

Single-file generation requires explicit `--series` and `--level`; neither has a default.

For example, a request for five pages of nonnegative basic multiplication:

```bash
arithmetic describe --series muldiv --level 1 --json
arithmetic generate --series muldiv --level 1 --pages 5 --output worksheets/multiplication.pdf --json
```

The success manifest contains absolute output paths, actual page capacity, seed,
and mode. Keep the seed for reproducing problem content. If a filename exists,
choose a new one unless replacement was requested. `--all` creates 68 files and
should only be used when a complete collection is requested.

Zero denominators and divisors are allowed by default. Add `--disallow-zero-denominator`
when the user requires defined expressions. Allowing division by zero does not guarantee
it appears on every page. Blanks always require a unique valid solution.

Relative output and configuration paths resolve from the current working directory.
Successful `--json` output is one JSON object on stdout; errors go to stderr with exit code 2.
Catalog and generation JSON use schema 2. Catalog `title`, `rules`, and `notes` are English strings;
generation records include `allow_zero_denominator`.

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
- Unsupported request: explain the specific constraint and propose a documented preset.

See [README configuration](../README.md#default-configuration) for configuration and [the catalog](levels.md) for all 68 presets.
Markdown and CLI metadata are enough; no agent-specific plugin is required.
