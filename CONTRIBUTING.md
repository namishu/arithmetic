# Contributing

Install with `uv sync`. Keep changes focused and describe the user-visible behavior.
Contributions to project-owned code and documentation are made under the MIT license.
Retain notices and licenses for third-party assets.

Before submitting:

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run python scripts/build_catalog_docs.py --check
uv build
```

For a level change, update its generator and `data/catalog.json`, then run
`uv run python scripts/build_catalog_docs.py`. Level IDs are public identifiers;
do not silently renumber them. Include mathematical correctness tests, not only
PDF file-existence checks. Keep both READMEs accurate. Document changes in
`CHANGELOG.md` and do not commit generated personal worksheets.

Keep `docs/` focused on using the program, for both people and agents. Provide
English and Simplified Chinese human-facing guides, and an English agent guide.
Keep contribution workflows here; inspect the source for implementation details.

Report a problem with the program version, command, seed, override configuration,
and expected versus observed behavior. Avoid including personal information in
shared worksheet files.
