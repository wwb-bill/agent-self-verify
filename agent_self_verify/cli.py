import sys, json, argparse
from agent_self_verify.verifier import verify, verify_spec, load_spec
from agent_self_verify.types import Assertion


def main(argv: list[str] | None = None) -> None:
    if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(prog="agent-self-verify", description="Self-verification harness for AI agent outputs")
    sub = parser.add_subparsers(dest="command")
    p = sub.add_parser("check"); p.add_argument("spec"); p.add_argument("output"); p.add_argument("--json", action="store_true")
    p2 = sub.add_parser("quick"); p2.add_argument("output"); p2.add_argument("--contains"); p2.add_argument("--not-contains"); p2.add_argument("--min-length"); p2.add_argument("--is-json", action="store_true"); p2.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "check":
            spec = load_spec(args.spec)
            output = _read(args.output)
            report = verify_spec(output, spec)
        elif args.command == "quick":
            assertions = []
            if args.contains: assertions.append(Assertion(type="contains", value=args.contains))
            if args.not_contains: assertions.append(Assertion(type="not-contains", value=args.not_contains))
            if args.min_length: assertions.append(Assertion(type="min-length", value=args.min_length))
            if args.is_json: assertions.append(Assertion(type="is-json"))
            report = verify(_read(args.output), assertions, "quick")
        else: parser.print_help(); return
        if args.json: print(json.dumps(report.to_dict(), indent=2))
        else: print(report.summary())
        sys.exit(0 if report.passed else 1)
    except Exception as e: print(f"Error: {e}", file=sys.stderr); sys.exit(2)


def _read(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as f: return f.read()
    except FileNotFoundError: return path


if __name__ == "__main__": main()
