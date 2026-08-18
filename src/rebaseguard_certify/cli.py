"""Command-line entry point."""

from __future__ import annotations

import argparse

from rebaseguard_certify import audit


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    audit_parser = subparsers.add_parser("audit")
    audit_parser.add_argument("certificate")
    prove_parser = subparsers.add_parser("prove")
    prove_parser.add_argument("--certificate", required=True)
    args = parser.parse_args(argv)
    if args.command == "audit":
        return audit.main([args.certificate])
    return 1


def main_entry() -> None:
    raise SystemExit(main())


if __name__ == "__main__":
    main_entry()

