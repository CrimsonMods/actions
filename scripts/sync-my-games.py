import argparse
import re
from pathlib import Path


START = b"<!-- games:start -->"
END = b"<!-- games:end -->"
MARKED_SECTION = re.compile(rb"^" + START + rb"\r?\n.*?^" + END + rb"(?=\r?$)", re.M | re.S)

# Recognize the two existing forms so the first sync can insert markers.
LEGACY_HEADING = re.compile(rb"^(?:\*\*)?(?:or )?buy[ \t]*/[ \t]*play my games!(?:\*\*)?[ \t]*(?=\r?$)", re.I | re.M)
LEGACY_CARDS = re.compile(
    rb'\r?\n(?:[ \t]*\r?\n)*<p align="center">[ \t]*\r?\n'
    rb'(?:[ \t]*(?:<a href="https://store\.steampowered\.com/app/[^"\r\n]+">'
    rb'|<img src="https://[^"\r\n]+/steam/apps/[^"\r\n]+"[^>\r\n]*>|</a>)[ \t]*\r?\n)+'
    rb'</p>[ \t]*(?=\r?$)',
    re.M,
)
LEGACY_LINKS = re.compile(
    rb"(?:\r?\n(?:[ \t]*\r?\n)*\[[^\]\r\n]+\]\(https://store\.steampowered\.com/app/[^)\r\n]+\)[^\r\n]*)+"
)


def section_bounds(readme: bytes) -> tuple[int, int]:
    if START in readme or END in readme:
        match = MARKED_SECTION.search(readme)
        if match is None or readme.count(START) != 1 or readme.count(END) != 1:
            raise ValueError("expected exactly one ordered pair of games markers on their own lines")
        return match.span()

    headings = list(LEGACY_HEADING.finditer(readme))
    if len(headings) != 1:
        raise ValueError("expected exactly one existing Buy / Play My Games section")
    heading = headings[0]
    games = LEGACY_CARDS.match(readme, heading.end()) or LEGACY_LINKS.match(readme, heading.end())
    if games is None:
        raise ValueError("could not identify the games section; place markers around it manually")
    return heading.start(), games.end()


def render(readme: bytes, snippet: bytes) -> bytes:
    if not snippet.strip() or START in snippet or END in snippet:
        raise ValueError("the shared snippet must be nonempty and exclude the games markers")
    start, end = section_bounds(readme)
    first_line = readme[start:readme.index(b"\n", start) + 1]
    newline = b"\r\n" if first_line.endswith(b"\r\n") else b"\n"
    block = newline.join([START, *snippet.rstrip(b"\r\n").splitlines(), END])
    return readme[:start] + block + readme[end:]


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync the shared games section in a mod README.")
    parser.add_argument("readme", type=Path)
    args = parser.parse_args()
    snippet_path = Path(__file__).resolve().parents[1] / "snippets" / "my-games.md"

    try:
        if args.readme.is_symlink():
            raise ValueError("expected a regular README file")
        original = args.readme.read_bytes()
        updated = render(original, snippet_path.read_bytes())
        if updated != original:
            args.readme.write_bytes(updated)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"{args.readme}: {exc}\n")


if __name__ == "__main__":
    main()
