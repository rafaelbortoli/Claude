import argparse
import sys

from cli.commands import claude_start, setup_claude, build_resource, install_resource, publish_resource


def main():
    parser = argparse.ArgumentParser(prog="cli", description="Claude Hub CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    claude_start.register(sub)
    setup_claude.register(sub)
    build_resource.register(sub)
    install_resource.register(sub)
    publish_resource.register(sub)

    args = parser.parse_args()
    try:
        args.func(args)
    except Exception as e:
        print(f"[erro] {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
