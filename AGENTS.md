# Working with Namishu Arithmetic

This repository generates arithmetic worksheet PDFs. Users may want worksheets,
not code changes. Read [README.md](README.md) (or [Simplified Chinese](README.zh-CN.md)) and
[docs/agent-guide.md](docs/agent-guide.md) before operating it.

- Set up the project with `uv sync`, or a Python 3.10+ virtual environment and `python -m pip install .`.
- Discover supported presets with `arithmetic list --json`; inspect the chosen
  one with `arithmetic describe --series CODE --level N --json`.
- Map the request to actual documented ranges and numeric types. Never invent
  flags, levels, answer keys, or custom-range support.
- Use `arithmetic generate ... --output PATH --json` for a file manifest.
- Zero denominators and divisors are allowed by default. Use `--disallow-zero-denominator`
  when the user requires defined expressions. Do not use `--force` without intent to replace the file.
- Verify the PDF exists, opens, and has the requested page count when PDF tools are
  available. Report the actual verification performed, output path, series/level,
  page count, and seed. Return a clickable file link when your environment supports it.
- Use the existing program for generation; change source only when requested.

`docs/` contains usage documentation for people and agents. Human-facing guides
have English and Simplified Chinese versions; the agent operation guide is in
English. Keep architecture, implementation explanations, and maintenance workflows
out of `docs/`. For requested code changes, inspect the source and run the relevant checks.

Generate only the English level catalog with `scripts/build_catalog_docs.py`.
Translate and update `docs/levels.zh-CN.md` directly with AI when the English catalog changes;
do not generate translations with scripts or maintain a separate translation data file.
Preserve level IDs, numeric ranges, examples, and CLI commands when translating.

Run functional tests with `uv run pytest`. Build release distributions separately
with `uv build`, then verify the exact wheel using
`uv run python scripts/check_wheel.py dist/namishu_arithmetic-VERSION-py3-none-any.whl`.
The checker installs only the wheel and its runtime dependencies into a temporary
environment, tests the installed CLI, and reads the generated PDF. It requires uv
and the project's development dependencies. CI publishes the same verified artifacts.
