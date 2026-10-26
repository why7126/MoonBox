"""Read-only shared governance environment check; standard library only."""
import sys


def main():
    if sys.version_info < (3, 12):
        print('Python >=3.12 required; select a supported project environment.', file=sys.stderr)
        return 2
    try:
        import yaml
    except ImportError:
        print('PyYAML unavailable; install project dependencies in the selected environment. No files changed.', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
