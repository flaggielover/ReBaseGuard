"""Independent certificate audit entry point (expanded in the certification tasks)."""

from __future__ import annotations

import argparse
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("certificate")
    args = parser.parse_args(argv)
    if not Path(args.certificate).is_file():
        return 2
    return 1


def main_entry() -> None:
    raise SystemExit(main())


if __name__ == "__main__":
    main_entry()

