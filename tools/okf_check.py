#!/usr/bin/env python3 -I
"""Validate (and optionally re-index) an OKF v0.2 bundle.

Usage:
    python3 -I tools/okf_check.py <bundle-dir> [--write-indexes] [--allow-broken-links]

Checks, in the order the OKF v0.2 spec lists its conformance rules (SPEC.md section 11):

1. every non-reserved .md file has a parseable YAML frontmatter block,
2. every frontmatter block has a non-empty `type`,
3. reserved files follow their structure: `index.md` carries no frontmatter (the bundle root
   may carry `okf_version`), and `log.md` groups entries under ISO `## YYYY-MM-DD` headings.

On top of that, house rules for this bundle (stricter than the spec, which tolerates all of
them): every markdown link to a `.md` path inside the bundle resolves, every `generated.at`,
`verified[].at` and `stale_after` is an ISO 8601 instant with an explicit offset, every `Decision`
carries `decision_id` and `decision_status`, every `Requirement` carries `requirement_id` and
`priority`, and every concept directory has an `index.md` listing exactly its concepts and
subdirectories.

Only the standard library plus PyYAML are used. The YAML loader mirrors the OKF reference
parser: the timestamp resolver is removed so dates stay the strings the author wrote.
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import yaml

RESERVED = {"index.md", "log.md"}
DELIM = "---"
LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
INDEX_ENTRY_RE = re.compile(r"^\* \[(?P<title>[^\]]+)\]\((?P<link>[^)]+)\)(?: - (?P<desc>.*))?$")
LOG_DATE_RE = re.compile(r"^## \d{4}-\d{2}-\d{2}$")
DECISION_STATUSES = {"proposed", "accepted", "superseded", "rejected"}
PRIORITIES = {"must", "should", "could"}


class Loader(yaml.SafeLoader):
    pass


Loader.yaml_implicit_resolvers = {
    ch: [(tag, rx) for tag, rx in resolvers if tag != "tag:yaml.org,2002:timestamp"]
    for ch, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def parse(text: str) -> tuple[dict | None, str]:
    """Return (frontmatter or None, body). None means the file has no frontmatter block."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != DELIM:
        return None, text
    for i in range(1, len(lines)):
        if lines[i].strip() == DELIM:
            fm = yaml.load("\n".join(lines[1:i]), Loader=Loader) or {}
            if not isinstance(fm, dict):
                raise ValueError("frontmatter must be a YAML mapping")
            return fm, "\n".join(lines[i + 1:])
    raise ValueError("unterminated frontmatter block")


def is_instant(raw: object) -> bool:
    s = str(raw or "")
    if "T" not in s:
        return False
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).tzinfo is not None
    except ValueError:
        return False


class Checker:
    def __init__(self, root: Path, allow_broken_links: bool) -> None:
        self.root = root
        self.allow_broken_links = allow_broken_links
        self.errors: list[str] = []
        self.concepts: dict[Path, dict] = {}

    def err(self, path: Path, msg: str) -> None:
        self.errors.append(f"{path.relative_to(self.root)}: {msg}")

    def resolve_link(self, src: Path, target: str) -> Path | None:
        target = target.split("#", 1)[0]
        if not target or "://" in target or target.startswith("mailto:"):
            return None
        if target.startswith("/"):
            return (self.root / target.lstrip("/")).resolve()
        return (src.parent / target).resolve()

    def check_concept(self, path: Path) -> None:
        try:
            fm, body = parse(path.read_text(encoding="utf-8"))
        except (ValueError, yaml.YAMLError) as e:
            self.err(path, f"frontmatter: {e}")
            return
        if fm is None:
            self.err(path, "missing frontmatter block")
            return
        if not str(fm.get("type") or "").strip():
            self.err(path, "frontmatter has no non-empty `type`")
        self.concepts[path] = fm
        typ = str(fm.get("type") or "")
        if typ == "Decision":
            if not fm.get("decision_id"):
                self.err(path, "Decision without decision_id")
            if fm.get("decision_status") not in DECISION_STATUSES:
                self.err(path, f"Decision with decision_status {fm.get('decision_status')!r}")
        if typ == "Requirement":
            if not fm.get("requirement_id"):
                self.err(path, "Requirement without requirement_id")
            if fm.get("priority") not in PRIORITIES:
                self.err(path, f"Requirement with priority {fm.get('priority')!r}")
        gen = fm.get("generated")
        if gen is not None:
            if not isinstance(gen, dict) or not gen.get("by"):
                self.err(path, "generated must be a mapping with `by`")
            elif "at" in gen and not is_instant(gen["at"]):
                self.err(path, f"generated.at is not an ISO instant with offset: {gen['at']!r}")
        ver = fm.get("verified")
        if ver is not None:
            events = [ver] if isinstance(ver, dict) else ver if isinstance(ver, list) else []
            for ev in events:
                if not isinstance(ev, dict) or not ev.get("by") or not is_instant(ev.get("at")):
                    self.err(path, f"verified entry malformed: {ev!r}")
        if "stale_after" in fm and not is_instant(fm["stale_after"]):
            self.err(path, "stale_after is not an ISO instant with offset")
        if "status" in fm and fm["status"] not in {"draft", "stable", "deprecated"}:
            self.err(path, f"status {fm['status']!r} is not draft|stable|deprecated")
        self.check_links(path, body)

    def check_links(self, path: Path, body: str) -> None:
        for m in LINK_RE.finditer(body):
            target = self.resolve_link(path, m.group(1))
            if target is None:
                continue
            if target.suffix == ".md" and not target.exists():
                msg = f"broken link {m.group(1)}"
                if self.allow_broken_links:
                    print(f"warning: {path.relative_to(self.root)}: {msg}")
                else:
                    self.err(path, msg)

    def check_index(self, path: Path) -> None:
        text = path.read_text(encoding="utf-8")
        try:
            fm, body = parse(text)
        except (ValueError, yaml.YAMLError) as e:
            self.err(path, f"frontmatter: {e}")
            return
        if fm is not None:
            if path.parent != self.root:
                self.err(path, "index.md outside the bundle root must not carry frontmatter")
            elif set(fm) - {"okf_version"}:
                self.err(path, "root index.md frontmatter may only carry okf_version")
        listed: set[Path] = set()
        for line in body.splitlines():
            if not line.strip() or line.startswith("# "):
                continue
            m = INDEX_ENTRY_RE.match(line)
            if not m:
                self.err(path, f"index line is not `* [Title](link) - description`: {line!r}")
                continue
            target = (path.parent / m.group("link")).resolve()
            if not target.exists():
                self.err(path, f"index links to missing {m.group('link')}")
            listed.add(target)
        expected = set()
        for child in sorted(path.parent.iterdir()):
            if child.name in RESERVED or child.name.startswith("."):
                continue
            if child.is_file() and child.suffix == ".md":
                expected.add(child.resolve())
            elif child.is_dir() and any(child.rglob("*.md")):
                expected.add((child / "index.md").resolve())
        for missing in sorted(expected - listed):
            self.err(path, f"index does not list {missing.relative_to(self.root)}")
        for extra in sorted(listed - expected):
            self.err(path, f"index lists {extra.relative_to(self.root)} which is not a sibling concept")

    def check_log(self, path: Path) -> None:
        fm, body = parse(path.read_text(encoding="utf-8"))
        if fm is not None:
            self.err(path, "log.md must not carry frontmatter")
        if not any(LOG_DATE_RE.match(line) for line in body.splitlines()):
            self.err(path, "log.md has no `## YYYY-MM-DD` heading")
        for line in body.splitlines():
            if line.startswith("## ") and not LOG_DATE_RE.match(line):
                self.err(path, f"log heading is not ISO YYYY-MM-DD: {line!r}")
        self.check_links(path, body)

    def run(self) -> int:
        dirs_with_md = set()
        for md in sorted(self.root.rglob("*.md")):
            dirs_with_md.add(md.parent)
            if md.name == "index.md":
                self.check_index(md)
            elif md.name == "log.md":
                self.check_log(md)
            else:
                self.check_concept(md)
        for d in sorted(dirs_with_md):
            if not (d / "index.md").exists():
                self.err(d / "index.md", "directory with concepts has no index.md")
        ids: dict[str, list[Path]] = defaultdict(list)
        for p, fm in self.concepts.items():
            for key in ("decision_id", "requirement_id"):
                if fm.get(key):
                    ids[str(fm[key])].append(p)
        for ident, paths in ids.items():
            if len(paths) > 1:
                self.err(paths[0], f"id {ident} is reused by {[str(x.relative_to(self.root)) for x in paths]}")
        return len(self.errors)


def write_indexes(root: Path) -> list[Path]:
    """Regenerate every index.md from frontmatter, deepest directories first (SPEC section 8)."""
    written = []
    dirs = sorted({md.parent for md in root.rglob("*.md")}, key=lambda p: (-len(p.parts), str(p)))
    dir_desc: dict[Path, str] = {}
    for d in dirs:
        groups: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
        for child in sorted(d.iterdir()):
            if child.name in RESERVED or child.name.startswith("."):
                continue
            if child.is_file() and child.suffix == ".md":
                fm, _ = parse(child.read_text(encoding="utf-8"))
                fm = fm or {}
                groups[str(fm.get("type") or "Other")].append(
                    (str(fm.get("title") or child.stem), child.name, str(fm.get("description") or ""))
                )
            elif child.is_dir() and any(child.rglob("*.md")):
                groups["Subdirectories"].append((child.name, f"{child.name}/index.md", dir_desc.get(child, "")))
        if not groups:
            continue
        sections = []
        for typ in sorted(groups, key=lambda t: (t == "Subdirectories", t)):
            lines = [f"# {typ}", ""]
            order = groups[typ] if typ == "Subdirectories" else sorted(groups[typ], key=lambda e: e[1])
            for title, link, desc in order:
                lines.append(f"* [{title}]({link})" + (f" - {desc}" if desc else ""))
            sections.append("\n".join(lines))
        head = ""
        if d == root:
            head = "---\nokf_version: \"0.2\"\n---\n\n"
        (d / "index.md").write_text(head + "\n\n".join(sections) + "\n", encoding="utf-8")
        written.append(d / "index.md")
        if d != root:
            readme = d / "_about.md"
            if readme.exists():
                fm, _ = parse(readme.read_text(encoding="utf-8"))
                dir_desc[d] = str((fm or {}).get("description") or "")
            else:
                dir_desc[d] = f"{len(sum(groups.values(), []))} entries"
    return written


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if not a.startswith("--")]
    flags = {a for a in argv[1:] if a.startswith("--")}
    if len(args) != 1:
        print(__doc__)
        return 2
    root = Path(args[0]).resolve()
    if "--write-indexes" in flags:
        for p in write_indexes(root):
            print(f"wrote {p.relative_to(root)}")
    checker = Checker(root, allow_broken_links="--allow-broken-links" in flags)
    n = checker.run()
    for e in checker.errors:
        print(f"error: {e}")
    print(f"{len(checker.concepts)} concepts checked, {n} error(s)")
    return 1 if n else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
