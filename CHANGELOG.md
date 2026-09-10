# Changelog

## 1.0.0

- Add GitHub Release publishing to PyPI with trusted publishing and a manual validation-only run.

- Consolidate user instructions in the READMEs; remove usage and contribution guides.

- Document generation arguments and every CLI command directly in both READMEs.

- Simplify preset mixing to equal shares and remove unused variant weights.
- Allow zero denominators/divisors by default; replace `--allow-undefined` with `--disallow-zero-denominator`.
- Replace Python `allow_undefined` with `allow_zero_denominator` (default true); remove teaching footer labels.
- Generation manifests use schema 2 with `allow_zero_denominator`.
- Use fixed Helvetica and remove font configuration and external font loading.

- Require explicit series and level for single-file generation; retain `--all` for complete collections.
- Organize README usage around installation, exercise selection, commands, and an agent example.

- Simplify both READMEs around uv-based usage, default settings, and agent generation.

- Use English throughout CLI output, public catalog metadata, and PDF labels; remove `--lang`.
- Catalog JSON schema 2 uses English strings for title, rules, and notes. Generation manifests also use schema 2.
- Keep Chinese catalog translations in documentation tooling and escape JSON for legacy Windows output encodings.

- Refresh both README headers with language navigation, Python/MIT/PDF badges, and sample PDF links.

## 0.1.0

- Keep `docs/` focused on usage, with bilingual human guides and an English agent guide.

- Extract the arithmetic generator into an independently installable Python project.
- Add `list`, `describe`, and `generate` commands with JSON output.
- Document all 68 levels in English and Chinese from shared metadata and real examples.
- Add agent operation instructions, packaged configuration, examples, and the MIT license.
- Use PDF standard Helvetica without distributing third-party font files.
- Validate normal worksheets using exact rational arithmetic and unique blank solutions.
- Make undefined-expression exercises opt-in; correct the level 18 missing-factor product.
