from __future__ import annotations

import argparse
import json
import secrets
from pathlib import Path

from .app import ArithmeticApp
from .catalog import describe_level, list_levels
from .series import SERIES_SPECS, get_series_spec, series_choices


def _positive(value: str) -> int:
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Namishu Arithmetic: printable arithmetic worksheets")
    parser.add_argument("--version", action="version", version="namishu-arithmetic 1.0.0")
    commands = parser.add_subparsers(dest="command", required=True)
    listing = commands.add_parser("list", help="List supported series and levels")
    listing.add_argument("--series", choices=series_choices())
    listing.add_argument("--json", action="store_true")
    describe = commands.add_parser("describe", help="Describe one level with actual examples")
    describe.add_argument("--series", choices=series_choices(), required=True)
    describe.add_argument("--level", type=_positive, required=True)
    describe.add_argument("--json", action="store_true")
    generate = commands.add_parser("generate", help="Generate one PDF or all 68 levels")
    generate.add_argument("--series", choices=series_choices(), help="Required unless --all is used")
    generate.add_argument("--level", type=_positive, help="Required unless --all is used")
    generate.add_argument("--pages", type=_positive, default=10)
    generate.add_argument("--seed", type=int)
    generate.add_argument("--output", type=Path)
    generate.add_argument("--output-dir", type=Path)
    generate.add_argument("--all", action="store_true")
    generate.add_argument("--config", type=Path)
    generate.add_argument(
        "--disallow-zero-denominator",
        action="store_true",
        help="Exclude expressions with a zero denominator or divisor",
    )
    generate.add_argument("--force", action="store_true", help="Replace existing output files")
    generate.add_argument("--json", action="store_true", help="Return a machine-readable output manifest")
    args = parser.parse_args(argv)
    try:
        if args.command == "list":
            records = list_levels(args.series)
            if args.json:
                _json({"schema_version": 2, "levels": records})
            else:
                for item in records:
                    print(f"{item['series']:8} {item['level']:2}  {item['title']}")
        elif args.command == "describe":
            item = describe_level(args.series, args.level)
            if args.json:
                _json({"schema_version": 2, **item})
            else:
                print(f"{item['series']} / {item['level']}: {item['title']}")
                print(item["rules"])
                print(item["notes"])
                print(f"Problems/page: {item['default_problems_per_page']}")
                for example in item["examples"]:
                    print(f"  {example}")
                print(item["command"])
        else:
            _generate(args, parser)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))


def _json(value: dict) -> None:
    print(json.dumps(value, ensure_ascii=True, indent=2))


def _generate(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    if args.all:
        if args.output or args.series or args.level:
            parser.error("--all cannot be combined with --output, --series, or --level")
        tasks = [(spec.code, level) for spec in SERIES_SPECS for level in spec.levels]
    else:
        if args.output_dir:
            parser.error("--output-dir requires --all")
        if args.series is None or args.level is None:
            parser.error(
                "generate requires both --series and --level, or --all; "
                "use 'arithmetic list' to browse levels or 'arithmetic describe --series CODE --level N' for details"
            )
        code, level = args.series, args.level
        get_series_spec(code).validate_level(level)
        tasks = [(code, level)]
    output_dir = args.output_dir or Path("worksheets")
    outputs = [
        (series, level, (args.output or output_dir / series / f"level-{level}.pdf").resolve())
        for series, level in tasks
    ]
    for _, _, output in outputs:
        if output.exists() and not args.force:
            raise ValueError(f"output already exists: {output}; choose another path or use --force")
    seed = args.seed if args.seed is not None else secrets.randbits(32)
    app = ArithmeticApp(config_path=args.config)
    manifest = []
    for series, level, output in outputs:
        app.generate(
            series,
            level,
            output,
            pages=args.pages,
            seed=seed,
            allow_zero_denominator=not args.disallow_zero_denominator,
        )
        if not output.is_file() or output.stat().st_size == 0:
            raise ValueError(f"PDF was not created: {output}")
        count = get_series_spec(series).generator_cls(app._series_cfg(series, seed)).page_capacity(level)
        manifest.append(
            {
                "series": series,
                "level": level,
                "pages": args.pages,
                "problems_per_page": count,
                "output": str(output),
                "seed": seed,
                "allow_zero_denominator": not args.disallow_zero_denominator,
            }
        )
        if not args.json:
            print(f"Generated: {output} ({args.pages} pages; seed {seed})")
    if args.json:
        _json({"schema_version": 2, "files": manifest})


if __name__ == "__main__":
    main()
